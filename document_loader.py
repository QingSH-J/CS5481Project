"""
文档加载器模块
符合RAG系统统一API接口规范
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from CS5481Project.common_types import Document, DocumentMetadata, create_document
import fitz  # PyMuPDF


class DocumentLoader:
    """文档加载器 - 标准接口实现"""

    def __init__(self, supported_formats: List[str] = None):
        """
        初始化加载器

        Args:
            supported_formats: 支持的文件格式列表，默认['pdf', 'txt', 'md']
        """
        if supported_formats is None:
            supported_formats = ['pdf', 'txt', 'md', 'markdown']

        self.supported_formats = supported_formats

        # 文件格式与加载方法的映射
        self._loader_map = {
            'pdf': self._load_pdf,
            'txt': self._load_txt,
            'md': self._load_markdown,
            'markdown': self._load_markdown
        }

    def load_documents(self, data_path: str) -> List[Document]:
        """
        加载指定路径的文档

        Args:
            data_path: 文档路径（文件或文件夹）

        Returns:
            List[Document]: 文档对象列表

        Raises:
            ValueError: 不支持的文件格式
            FileNotFoundError: 文件不存在
        """
        path = Path(data_path)

        if not path.exists():
            raise FileNotFoundError(f"路径不存在: {data_path}")

        # 如果是文件，直接加载
        if path.is_file():
            return [self.load_single_document(str(path))]

        # 如果是目录，加载所有支持的文件
        if path.is_dir():
            return self._load_directory(path, recursive=True)

        raise ValueError(f"无效的路径: {data_path}")

    def load_single_document(self, file_path: str) -> Document:
        """
        加载单个文档

        Args:
            file_path: 文档文件路径

        Returns:
            Document: 文档对象

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not self.validate_format(file_path):
            file_ext = path.suffix.lstrip('.')
            raise ValueError(
                f"不支持的文件格式: {file_ext}. "
                f"支持的格式: {self.supported_formats}"
            )

        # 获取文件扩展名
        file_ext = path.suffix.lstrip('.').lower()

        # 调用对应的加载方法
        loader_func = self._loader_map.get(file_ext)
        if not loader_func:
            raise ValueError(f"未找到格式 '{file_ext}' 的加载器")

        return loader_func(path)

    def validate_format(self, file_path: str) -> bool:
        """
        验证文件格式是否支持

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否支持该格式
        """
        file_ext = Path(file_path).suffix.lstrip('.').lower()
        return file_ext in self.supported_formats

    def _load_directory(
        self,
        directory_path: Path,
        recursive: bool = True
    ) -> List[Document]:
        """
        批量加载目录下的文档

        Args:
            directory_path: 目录路径
            recursive: 是否递归加载子目录

        Returns:
            List[Document]: 文档对象列表
        """
        all_documents = []

        # 遍历目录
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and self.validate_format(str(file_path)):
                try:
                    doc = self.load_single_document(str(file_path))
                    all_documents.append(doc)
                    print(f"✓ 成功加载: {file_path.name}")
                except Exception as e:
                    print(f"✗ 加载失败 {file_path.name}: {str(e)}")

        return all_documents

    def _load_pdf(self, file_path: Path) -> Document:
        """加载PDF文件（合并所有页面为一个文档）"""
        try:
            pdf_document = fitz.open(str(file_path))
            all_text = []

            # 提取所有页面的文本
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text()
                all_text.append(text)

            pdf_document.close()

            # 合并所有页面文本
            content = "\n\n".join(all_text)

            # 创建元数据
            metadata = self._extract_file_metadata(
                file_path,
                total_pages=len(all_text)
            )

            # 创建文档对象
            return Document(content=content, metadata=metadata)

        except Exception as e:
            raise Exception(f"无法加载PDF文件 {file_path}: {str(e)}")

    def _load_txt(self, file_path: Path) -> Document:
        """加载TXT文件"""
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()

                # 创建元数据
                metadata = self._extract_file_metadata(file_path)

                # 创建文档对象
                return Document(content=content, metadata=metadata)

            except UnicodeDecodeError:
                continue

        raise ValueError(f"无法解码文件 {file_path}，尝试的编码: {encodings}")

    def _load_markdown(self, file_path: Path) -> Document:
        """加载Markdown文件"""
        # Markdown 文件本质上是文本文件
        return self._load_txt(file_path)

    def _extract_file_metadata(
        self,
        file_path: Path,
        **extra_fields
    ) -> DocumentMetadata:
        """
        提取文件的基础元数据

        Args:
            file_path: 文件路径
            **extra_fields: 额外的元数据字段

        Returns:
            DocumentMetadata: 元数据对象
        """
        stat = file_path.stat()

        # 计算文件hash
        file_hash = self._calculate_file_hash(file_path)

        # 获取文件类型
        file_type = file_path.suffix.lstrip('.').lower()

        # 创建元数据
        return DocumentMetadata(
            source=str(file_path),
            file_type=file_type,
            title=file_path.stem,  # 使用文件名作为标题
            file_size=stat.st_size,
            file_hash=file_hash,
            created_date=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            processed_time=datetime.now(),
            **extra_fields
        )

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def clean_text(self, text: str) -> str:
        """
        清洗和标准化文本

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)

        # 移除特殊控制字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 移除多余的换行
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 移除行首行尾空白
        text = '\n'.join(line.strip() for line in text.split('\n'))

        # 移除多余的空格
        text = re.sub(r' {2,}', ' ', text)

        return text.strip()

    def process_documents(
        self,
        documents: List[Document],
        clean: bool = True,
        add_custom_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        处理文档：清洗文本、添加元数据

        Args:
            documents: Document对象列表
            clean: 是否清洗文本
            add_custom_metadata: 要添加的自定义元数据

        Returns:
            处理后的Document对象列表
        """
        processed_docs = []

        for doc in documents:
            # 清洗文本
            if clean:
                doc.content = self.clean_text(doc.content)

            # 添加自定义元数据
            if add_custom_metadata:
                doc.metadata.custom_metadata.update(add_custom_metadata)

            processed_docs.append(doc)

        return processed_docs

    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """
        获取文档统计信息

        Args:
            documents: Document对象列表

        Returns:
            统计信息字典
        """
        total_docs = len(documents)
        total_chars = sum(len(doc.content) for doc in documents)

        # 按文件类型统计
        file_types = {}
        for doc in documents:
            file_type = doc.metadata.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1

        # 按来源文件统计
        sources = {}
        for doc in documents:
            source = Path(doc.metadata.source).name
            sources[source] = sources.get(source, 0) + 1

        return {
            'total_documents': total_docs,
            'total_characters': total_chars,
            'average_doc_length': total_chars / total_docs if total_docs > 0 else 0,
            'file_types': file_types,
            'sources': sources
        }


# 测试代码
if __name__ == "__main__":
    """测试文档加载器"""

    # 初始化加载器
    loader = DocumentLoader()

    # 测试加载单个文件
    print("=== 测试加载单个PDF文件 ===")
    try:
        doc = loader.load_single_document("CS4280.pdf")
        print(f"✓ 成功加载文档")
        print(f"  - 文档ID: {doc.doc_id}")
        print(f"  - 标题: {doc.metadata.title}")
        print(f"  - 文件类型: {doc.metadata.file_type}")
        print(f"  - 文件大小: {doc.metadata.file_size} bytes")
        print(f"  - 内容长度: {doc.get_content_length()} 字符")
        print(f"  - 内容预览: {doc.content[:100]}...")
    except Exception as e:
        print(f"✗ 加载失败: {e}")

    # 测试加载目录
    print("\n=== 测试加载当前目录的PDF文件 ===")
    try:
        # 创建临时目录测试
        docs = loader._load_directory(Path("."), recursive=False)
        print(f"\n✓ 成功加载 {len(docs)} 个文档")

        # 统计信息
        stats = loader.get_document_stats(docs)
        print(f"\n统计信息:")
        print(f"  - 总文档数: {stats['total_documents']}")
        print(f"  - 总字符数: {stats['total_characters']:,}")
        print(f"  - 平均文档长度: {stats['average_doc_length']:.0f}")
        print(f"  - 文件类型分布: {stats['file_types']}")
    except Exception as e:
        print(f"✗ 加载失败: {e}")
