"""
RAG系统统一数据结构定义
所有模块共享的数据结构
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
 
@dataclass
class DocumentMetadata:
    """文档元数据标准格式"""
    source: str  # 文件路径
    file_type: str  # pdf/txt/md
    title: Optional[str] = None
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    page_number: Optional[int] = None
    total_pages: Optional[int] = None
    file_size: Optional[int] = None  # 文件大小（字节）
    file_hash: Optional[str] = None  # 文件哈希值
    modified_time: Optional[datetime] = None  # 文件修改时间
    processed_time: Optional[datetime] = None  # 处理时间
    custom_metadata: Dict[str, Any] = field(default_factory=dict)  # 自定义元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'source': self.source,
            'file_type': self.file_type,
            'title': self.title,
            'author': self.author,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'page_number': self.page_number,
            'total_pages': self.total_pages,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'modified_time': self.modified_time.isoformat() if self.modified_time else None,
            'processed_time': self.processed_time.isoformat() if self.processed_time else None,
            **self.custom_metadata
        }


@dataclass
class Document:
    """文档对象标准格式"""
    content: str  # 文档内容
    metadata: DocumentMetadata  # 元数据
    doc_id: Optional[str] = None  # 文档唯一标识

    def __post_init__(self):
        """初始化后自动生成文档ID"""
        if self.doc_id is None:
            self.doc_id = str(uuid.uuid4())

#
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'content': self.content,
            'metadata': self.metadata.to_dict(),
            'doc_id': self.doc_id
        }

    def get_content_length(self) -> int:
        """获取内容长度"""
        return len(self.content)


@dataclass
class Chunk:
    """文档块标准格式"""
    text: str  # 块文本内容
    chunk_id: str  # 块唯一标识
    metadata: DocumentMetadata  # 继承原文档元数据
    embedding: Optional[List[float]] = None  # 向量嵌入
    chunk_index: int = 0  # 在原文档中的位置
    total_chunks: int = 1  # 原文档总块数

    def __post_init__(self):
        """初始化后自动生成块ID"""
        if not self.chunk_id:
            self.chunk_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'text': self.text,
            'chunk_id': self.chunk_id,
            'metadata': self.metadata.to_dict(),
            'embedding': self.embedding,
            'chunk_index': self.chunk_index,
            'total_chunks': self.total_chunks
        }

    def get_text_length(self) -> int:
        """获取文本长度"""
        return len(self.text)


@dataclass
class RetrievalResult:
    """检索结果标准格式"""
    chunk: Chunk  # 检索到的文档块
    score: float  # 相似度分数
    rank: int  # 排序位置

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'chunk': self.chunk.to_dict(),
            'score': self.score,
            'rank': self.rank
        }


@dataclass
class QAResponse:
    """问答响应标准格式"""
    question: str  # 原始问题
    answer: str  # 生成的答案
    sources: List[RetrievalResult]  # 来源文档
    confidence: Optional[float] = None  # 置信度
    timestamp: Optional[datetime] = None  # 生成时间

    def __post_init__(self):
        """初始化后自动设置时间戳"""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'question': self.question,
            'answer': self.answer,
            'sources': [source.to_dict() for source in self.sources],
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    def get_source_count(self) -> int:
        """获取来源数量"""
        return len(self.sources)


# 工具函数
def create_document_metadata(
    source: str,
    file_type: str,
    **kwargs
) -> DocumentMetadata:
    """
    便捷创建文档元数据

    Args:
        source: 文件路径
        file_type: 文件类型
        **kwargs: 其他元数据字段

    Returns:
        DocumentMetadata: 元数据对象
    """
    return DocumentMetadata(
        source=source,
        file_type=file_type,
        **kwargs
    )


def create_document(
    content: str,
    source: str,
    file_type: str,
    **metadata_kwargs
) -> Document:
    """
    便捷创建文档对象

    Args:
        content: 文档内容
        source: 文件路径
        file_type: 文件类型
        **metadata_kwargs: 其他元数据字段

    Returns:
        Document: 文档对象
    """
    metadata = create_document_metadata(source, file_type, **metadata_kwargs)
    return Document(content=content, metadata=metadata)
