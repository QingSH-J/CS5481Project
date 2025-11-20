# DocumentLoad API 文档
change
## 概述

DocumentLoad 是一个基于 LangChain 的文档加载模块，专注于加载多种格式的文档文件，提供文档清洗、标准化处理和元数据管理功能。

### 主要特性

- 支持多种文档格式（PDF、TXT、Markdown）
- 自动文档清洗和标准化
- 丰富的元数据提取和管理
- 批量目录加载
- Markdown 格式导出
- 完全兼容 LangChain 标准
- 轻量级设计，专注于文档加载
- 
## 安装依赖

```bash
pip install langchain langchain-community langchain-core PyMuPDF
```

## 核心类：DocumentProcessor

### 初始化

```python
from DocumentLoad import DocumentProcessor

processor = DocumentProcessor()
```

DocumentProcessor 无需任何参数即可初始化，开箱即用。

---

## 方法详解

### 1. load_document

加载单个文档文件。

#### 方法签名

```python
def load_document(self, file_path: str) -> List[Document]
```

#### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_path` | `str` | 文档文件路径 |

#### 返回值

`List[Document]` - LangChain Document 对象列表

#### 支持的文件格式

- `.pdf` - PDF 文档（使用 PyMuPDF）
- `.txt` - 文本文件（自动检测编码：UTF-8、GBK、Latin-1）
- `.md` - Markdown 文件
- `.markdown` - Markdown 文件

#### 异常

- `FileNotFoundError` - 文件不存在
- `ValueError` - 不支持的文件格式

#### 示例

```python
processor = DocumentProcessor()

# 加载 PDF 文档
docs = processor.load_document("example.pdf")
print(f"加载了 {len(docs)} 页")

# 加载 TXT 文档
docs = processor.load_document("example.txt")

# 加载 Markdown 文档
docs = processor.load_document("example.md")
```

#### 返回的 Document 结构

每个 Document 对象包含：

**page_content** (str): 文档内容

**metadata** (dict): 元数据，包括：
- `source` - 文件完整路径
- `filename` - 文件名
- `file_type` - 文件扩展名
- `file_size` - 文件大小（字节）
- `created_time` - 创建时间（ISO 格式）
- `modified_time` - 修改时间（ISO 格式）
- `file_hash` - 文件 MD5 哈希值
- `processed_time` - 处理时间（ISO 格式）
- `page` - 页码（仅 PDF）

---

### 2. load_directory

批量加载目录下的文档文件。

#### 方法签名

```python
def load_directory(
    self,
    directory_path: str,
    file_types: Optional[List[str]] = None,
    recursive: bool = True
) -> List[Document]
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `directory_path` | `str` | - | 目录路径 |
| `file_types` | `Optional[List[str]]` | `None` | 要加载的文件类型列表，None 表示加载所有支持的格式 |
| `recursive` | `bool` | `True` | 是否递归加载子目录 |

#### 返回值

`List[Document]` - 所有文档的 Document 对象列表

#### 异常

- `FileNotFoundError` - 目录不存在

#### 示例

```python
processor = DocumentProcessor()

# 加载目录下所有支持的文档
all_docs = processor.load_directory("./documents")

# 只加载 PDF 文件
pdf_docs = processor.load_directory(
    "./documents",
    file_types=['.pdf']
)

# 只加载当前目录，不递归子目录
docs = processor.load_directory(
    "./documents",
    recursive=False
)

# 加载多种格式
docs = processor.load_directory(
    "./documents",
    file_types=['.pdf', '.txt', '.md']
)
```

#### 输出示例

```
✓ 成功加载: document1.pdf
✓ 成功加载: document2.txt
✗ 加载失败 corrupted.pdf: 无法加载PDF文件
```

---

### 3. process_documents

处理文档：清洗文本、添加元数据。

#### 方法签名

```python
def process_documents(
    self,
    documents: List[Document],
    clean: bool = True,
    add_custom_metadata: Optional[Dict[str, Any]] = None
) -> List[Document]
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `documents` | `List[Document]` | - | Document 对象列表 |
| `clean` | `bool` | `True` | 是否清洗文本 |
| `add_custom_metadata` | `Optional[Dict[str, Any]]` | `None` | 要添加的自定义元数据 |

#### 返回值

`List[Document]` - 处理后的 Document 对象列表

#### 文本清洗功能

当 `clean=True` 时，会执行以下清洗操作：
- 移除多余的空白字符
- 移除特殊控制字符
- 统一换行符为 `\n`
- 移除多余的换行（3个以上）
- 移除行首行尾空白
- 移除多余的空格（2个以上）

#### 示例

```python
processor = DocumentProcessor()

# 加载文档
docs = processor.load_document("example.pdf")

# 处理文档（清洗文本）
processed = processor.process_documents(docs, clean=True)

# 不清洗，保持原始文本
unprocessed = processor.process_documents(docs, clean=False)

# 添加自定义元数据
custom_meta = {
    'category': 'technical',
    'department': 'engineering',
    'version': '1.0'
}
processed = processor.process_documents(
    docs,
    clean=True,
    add_custom_metadata=custom_meta
)
```

---

### 4. clean_text

清洗和标准化文本。

#### 方法签名

```python
def clean_text(self, text: str) -> str
```

#### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 原始文本 |

#### 返回值

`str` - 清洗后的文本

#### 示例

```python
processor = DocumentProcessor()

raw_text = "这是一段    有很多\n\n\n\n空白    的文本"
cleaned = processor.clean_text(raw_text)
print(cleaned)  # "这是一段 有很多\n\n空白 的文本"
```

---

### 5. get_document_stats

获取文档统计信息。

#### 方法签名

```python
def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]
```

#### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `documents` | `List[Document]` | Document 对象列表 |

#### 返回值

`Dict[str, Any]` - 包含以下键的统计信息字典：

| 键 | 类型 | 说明 |
|----|------|------|
| `total_documents` | `int` | 文档总数 |
| `total_characters` | `int` | 总字符数 |
| `average_doc_length` | `float` | 平均文档长度 |
| `file_types` | `Dict[str, int]` | 各文件类型的数量 |
| `sources` | `Dict[str, int]` | 各来源文件的文档数量 |

#### 示例

```python
processor = DocumentProcessor()
docs = processor.load_directory("./documents")
processed = processor.process_documents(docs)

stats = processor.get_document_stats(processed)
print(f"总文档数: {stats['total_documents']}")
print(f"总字符数: {stats['total_characters']}")
print(f"平均长度: {stats['average_doc_length']:.0f}")
print(f"文件类型分布: {stats['file_types']}")
```

#### 输出示例

```python
{
    'total_documents': 150,
    'total_characters': 125000,
    'average_doc_length': 833.33,
    'file_types': {'.pdf': 100, '.txt': 30, '.md': 20},
    'sources': {'doc1.pdf': 50, 'doc2.pdf': 50, 'readme.txt': 30, 'guide.md': 20}
}
```

---

### 6. export_to_markdown

将文档导出为 Markdown 文件。

#### 方法签名

```python
def export_to_markdown(
    self,
    documents: List[Document],
    output_path: str,
    include_metadata: bool = True,
    add_toc: bool = True
) -> None
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `documents` | `List[Document]` | - | Document 对象列表 |
| `output_path` | `str` | - | 输出文件路径 |
| `include_metadata` | `bool` | `True` | 是否包含元数据信息 |
| `add_toc` | `bool` | `True` | 是否添加目录 |

#### 返回值

`None`

#### 导出的 Markdown 结构

1. **文档标题和生成时间**
2. **统计信息**
   - 总文档数
   - 总字符数
   - 平均文档长度
3. **目录**（如果 `add_toc=True`）
   - 每个文档的快速导航链接
4. **文档内容**
   - 每个文档的元数据（页码、文件名、文件类型、字符数）
   - 文档内容

#### 示例

```python
processor = DocumentProcessor()

# 加载文档
docs = processor.load_document("example.pdf")

# 处理文档
processed = processor.process_documents(docs, clean=True)

# 导出为 Markdown（包含元数据和目录）
processor.export_to_markdown(
    documents=processed,
    output_path="example_export.md",
    include_metadata=True,
    add_toc=True
)

# 简单导出（不含元数据和目录）
processor.export_to_markdown(
    documents=processed,
    output_path="example_simple.md",
    include_metadata=False,
    add_toc=False
)
```

#### 输出示例

```
✓ Markdown文件已保存至: example_export.md
  - 文件大小: 125.48 KB
```

---

## 完整使用示例

### 示例 1: 处理单个 PDF 文档

```python
from DocumentLoad import DocumentProcessor

# 初始化处理器
processor = DocumentProcessor(
    chunk_size=1000,
    chunk_overlap=200
)

# 加载文档
docs = processor.load_document("example.pdf")
print(f"加载了 {len(docs)} 页")

# 保存原始文档
original_docs = docs.copy()

# 处理文档（清洗 + 分割）
processed = processor.process_documents(docs)
print(f"生成了 {len(processed)} 个文档块")

# 查看统计信息
stats = processor.get_document_stats(processed)
print(f"总字符数: {stats['total_characters']:,}")
print(f"平均块长度: {stats['average_doc_length']:.0f} 字符")

# 导出为 Markdown
processor.export_to_markdown(
    documents=processed,
    output_path="example_processed.md",
    original_documents=original_docs
)
```

### 示例 2: 批量处理目录

```python
from DocumentLoad import DocumentProcessor

# 初始化处理器
processor = DocumentProcessor(
    chunk_size=500,
    chunk_overlap=100
)

# 批量加载目录
all_docs = processor.load_directory(
    "./documents",
    file_types=['.pdf', '.txt', '.md'],
    recursive=True
)
print(f"加载了 {len(all_docs)} 个文档")

# 添加自定义元数据
custom_metadata = {
    'project': 'RAG System',
    'version': '1.0'
}

# 处理文档
processed = processor.process_documents(
    all_docs,
    clean=True,
    split=True,
    add_custom_metadata=custom_metadata
)

# 统计信息
stats = processor.get_document_stats(processed)
print(f"总块数: {stats['total_documents']}")
print(f"文件类型: {stats['file_types']}")
```

### 示例 3: 自定义文本分割

```python
from DocumentLoad import DocumentProcessor

# 使用自定义分割符（只按段落分割）
processor = DocumentProcessor(
    chunk_size=2000,
    chunk_overlap=500,
    separators=["\n\n", "\n"]
)

# 加载和处理
docs = processor.load_document("example.txt")
processed = processor.process_documents(docs)

# 查看第一个块
first_chunk = processed[0]
print(f"内容: {first_chunk.page_content[:200]}...")
print(f"元数据: {first_chunk.metadata}")
```

### 示例 4: 与 LangChain 集成

```python
from DocumentLoad import DocumentProcessor
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 加载和处理文档
processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
docs = processor.load_document("knowledge_base.pdf")
processed = processor.process_documents(docs)

# 创建向量数据库
embeddings = HuggingFaceEmbeddings()
vectorstore = Chroma.from_documents(
    documents=processed,
    embedding=embeddings
)

# 执行检索
query = "什么是 RAG？"
results = vectorstore.similarity_search(query, k=3)
for doc in results:
    print(f"页码: {doc.metadata.get('page')}")
    print(f"内容: {doc.page_content[:100]}...\n")
```

---

## 元数据字段说明

### 基础元数据（所有文档）

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | `str` | 文件完整路径 |
| `filename` | `str` | 文件名 |
| `file_type` | `str` | 文件扩展名（如 `.pdf`） |
| `file_size` | `int` | 文件大小（字节） |
| `created_time` | `str` | 文件创建时间（ISO 格式） |
| `modified_time` | `str` | 文件修改时间（ISO 格式） |
| `file_hash` | `str` | 文件 MD5 哈希值 |
| `processed_time` | `str` | 处理时间（ISO 格式） |

### PDF 特有元数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `page` | `int` | 页码（从1开始） |

### 分块后的元数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `chunk_id` | `int` | 块编号（从0开始） |
| `total_chunks` | `int` | 该文档的总块数 |
| `chunk_size` | `int` | 该块的字符数 |

### 自定义元数据

通过 `add_custom_metadata` 参数添加的任意键值对。

---

## 性能建议

### 块大小选择

| 使用场景 | 建议 chunk_size | 建议 chunk_overlap |
|----------|----------------|-------------------|
| 精确检索 | 300-500 | 50-100 |
| 平衡模式 | 800-1200 | 150-250 |
| 上下文丰富 | 1500-2000 | 300-400 |

### 编码处理

- TXT 文件支持自动编码检测（UTF-8 → GBK → Latin-1）
- 如果遇到编码问题，建议先转换为 UTF-8

### 批量处理

```python
# 推荐：分批处理大量文档
import os

processor = DocumentProcessor()
batch_size = 10
files = os.listdir("./documents")

for i in range(0, len(files), batch_size):
    batch_files = files[i:i+batch_size]
    for file in batch_files:
        docs = processor.load_document(file)
        # 处理...
```

---

## 错误处理

### 常见错误

1. **FileNotFoundError**
   ```python
   try:
       docs = processor.load_document("nonexistent.pdf")
   except FileNotFoundError as e:
       print(f"文件不存在: {e}")
   ```

2. **ValueError - 不支持的格式**
   ```python
   try:
       docs = processor.load_document("image.jpg")
   except ValueError as e:
       print(f"格式错误: {e}")
   ```

3. **PDF 加载失败**
   ```python
   try:
       docs = processor.load_document("corrupted.pdf")
   except Exception as e:
       print(f"PDF 加载失败: {e}")
   ```

### 批量加载的错误处理

`load_directory` 方法会自动捕获单个文件的错误，并继续处理其他文件：

```python
docs = processor.load_directory("./documents")
# 输出：
# ✓ 成功加载: doc1.pdf
# ✗ 加载失败 corrupted.pdf: 无法加载PDF文件
# ✓ 成功加载: doc2.txt
```

---

## 依赖库版本

推荐的依赖库版本：

```
langchain>=0.1.0
langchain-community>=0.0.10
langchain-text-splitters>=0.0.1
langchain-core>=0.1.0
PyMuPDF>=1.23.0
```

---

## 许可证

请根据您的项目需求添加相应的许可证信息。

---

## 更新日志

### v1.0.0
- 初始版本
- 支持 PDF、TXT、Markdown 格式
- 基于 PyMuPDF 的 PDF 解析
- 中英文文本分割
- Markdown 导出功能
- 完整的元数据管理

---

## 联系方式

如有问题或建议，请联系项目维护者。
