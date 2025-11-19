# System Architecture

## Overview

This document describes the architecture of the Agentic RAG (Retrieval-Augmented Generation) system, detailing how each component works together to enable intelligent question-answering over custom document collections.

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                         USER INPUT                             │
│                    (Questions / Commands)                      │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                    MAIN APPLICATION                            │
│                      (main.py)                                 │
│  • CLI Interface                                               │
│  • Input validation                                            │
│  • Command routing (/help, /stats, /quit)                      │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                     AGENTIC LAYER                              │
│                     (src/agent.py)                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LangChain Agent (OpenAI Tools)                         │  │
│  │  • Receives user query                                  │  │
│  │  • Plans approach to answer                             │  │
│  │  • Selects and executes tools                           │  │
│  │  • Synthesizes final response                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Conversation Memory                                    │  │
│  │  • Maintains chat history                               │  │
│  │  • Enables context-aware responses                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LLM (GPT-4o-mini / GPT-4)                              │  │
│  │  • Reasoning and generation                             │  │
│  │  • Natural language understanding                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────┬────────────────────────────┘
                    │              │
        ┌───────────┘              └──────────┐
        ▼                                     ▼
┌──────────────────────┐           ┌──────────────────────┐
│  AGENT TOOLS         │           │  AGENT TOOLS         │
│  (src/agent_tools.py)│           │  (src/agent_tools.py)│
│                      │           │                      │
│  Knowledge Base      │           │  Document Stats      │
│  Search Tool         │           │  Tool                │
│  • Semantic search   │           │  • Collection info   │
│  • Score ranking     │           │  • Source listing    │
│  • Result formatting │           │  • Metadata query    │
└──────────┬───────────┘           └──────────┬───────────┘
           │                                  │
           └────────────┬─────────────────────┘
                        ▼
           ┌────────────────────────┐
           │   VECTOR STORE MANAGER │
           │   (src/vector_store.py)│
           │                        │
           │  • Query embedding     │
           │  • Similarity search   │
           │  • Result retrieval    │
           └────────┬───────────────┘
                    │
                    ▼
           ┌────────────────────────┐
           │      CHROMADB          │
           │   (Vector Database)    │
           │                        │
           │  • Vector storage      │
           │  • Cosine similarity   │
           │  • Metadata filtering  │
           │  • Persistent storage  │
           └────────────────────────┘
```

## Data Ingestion Pipeline

```
┌───────────────────────────────────────────────────────────────┐
│                   INGESTION PROCESS                            │
│                  (ingest_documents.py)                         │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│              DOCUMENT PROCESSOR                                │
│          (src/document_processor.py)                           │
│                                                                │
│  Step 1: LOAD DOCUMENTS                                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ DirectoryLoader                                          │ │
│  │ • TextLoader (.txt)                                      │ │
│  │ • PyPDFLoader (.pdf)                                     │ │
│  │ • UnstructuredMarkdownLoader (.md)                       │ │
│  │ • Docx2txtLoader (.docx)                                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  Step 2: CHUNK DOCUMENTS                                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ RecursiveCharacterTextSplitter                           │ │
│  │ • Split by separators: \n\n, \n, space                   │ │
│  │ • Chunk size: 1000 characters (configurable)             │ │
│  │ • Overlap: 200 characters (prevents context loss)        │ │
│  │ • Preserve metadata (source, page, etc.)                 │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│              VECTOR STORE MANAGER                              │
│          (src/vector_store.py)                                 │
│                                                                │
│  Step 3: CREATE EMBEDDINGS                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Embedding Model                                          │ │
│  │ • OpenAI: text-embedding-3-small (1536 dimensions)       │ │
│  │ • HuggingFace: all-MiniLM-L6-v2 (384 dimensions)         │ │
│  │ • Converts text → vector representation                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  Step 4: STORE IN DATABASE                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ChromaDB                                                 │ │
│  │ • Persist to disk (./chroma_db)                          │ │
│  │ • Index for fast retrieval                               │ │
│  │ • Store metadata with vectors                            │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## Query Processing Flow

```
User Question: "What is RAG?"
         │
         ▼
┌────────────────────┐
│ 1. AGENT RECEIVES  │
│    INPUT           │
│                    │
│ • Parse question   │
│ • Load history     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 2. AGENT REASONING │
│                    │
│ Decision:          │
│ "I need to search  │
│  the knowledge     │
│  base for info     │
│  about RAG"        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────────────┐
│ 3. TOOL EXECUTION              │
│    knowledge_base_search       │
│                                │
│ Input: "What is RAG?"          │
│                                │
│ a) Embed query using           │
│    embedding model             │
│    → [0.12, -0.34, 0.56, ...]  │
│                                │
│ b) Similarity search in        │
│    ChromaDB                    │
│    → Find top 4 chunks         │
│                                │
│ c) Retrieve & format           │
│    → Return with scores        │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│ 4. TOOL RESULT                 │
│                                │
│ --- Result 1 (score: 0.89) --- │
│ Source: sample_knowledge.md    │
│ Content: "RAG is an AI         │
│ framework that combines..."    │
│                                │
│ --- Result 2 (score: 0.85) --- │
│ ...                            │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│ 5. AGENT SYNTHESIS             │
│                                │
│ Prompt to LLM:                 │
│ "Based on these documents,     │
│  answer the question about     │
│  RAG. Only use provided        │
│  context..."                   │
│                                │
│ Context: [Retrieved chunks]    │
│ Question: "What is RAG?"       │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│ 6. LLM GENERATION              │
│                                │
│ Generated answer:              │
│ "Retrieval-Augmented           │
│  Generation (RAG) is an AI     │
│  framework that combines..."   │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│ 7. RESPONSE TO USER            │
│                                │
│ • Formatted answer             │
│ • Stored in memory             │
│ • Displayed in CLI             │
└────────────────────────────────┘
```

## Component Details

### 1. Document Processor (`src/document_processor.py`)

**Responsibilities:**
- Load documents from multiple formats
- Split documents into chunks
- Add and manage metadata

**Key Classes:**
- `DocumentProcessor`: Main class for document handling

**Configuration:**
```yaml
chunking:
  chunk_size: 1000
  chunk_overlap: 200
  separators: ["\n\n", "\n", " ", ""]
```

### 2. Vector Store Manager (`src/vector_store.py`)

**Responsibilities:**
- Initialize embedding models
- Create and manage vector database
- Perform similarity searches
- Provide retriever interface

**Key Classes:**
- `VectorStoreManager`: Manages ChromaDB operations

**Supported Embeddings:**
- OpenAI (API-based, high quality)
- HuggingFace (local, free)

### 3. Agent Tools (`src/agent_tools.py`)

**Tools Provided:**
1. `KnowledgeBaseSearchTool`:
   - Performs semantic search
   - Returns ranked results with scores
   - Formats output for LLM consumption

2. `DocumentStatsTool`:
   - Provides collection statistics
   - Lists available sources
   - Shows chunk count

**Tool Interface:**
- Implements LangChain's `BaseTool`
- Pydantic schemas for input validation
- Error handling and graceful degradation

### 4. Agentic RAG (`src/agent.py`)

**Responsibilities:**
- Orchestrate all components
- Manage conversation flow
- Route queries to appropriate tools
- Generate final responses

**Key Components:**
- **Agent**: OpenAI Tools agent (function calling)
- **LLM**: GPT-4o-mini or GPT-4
- **Memory**: Conversation buffer for context
- **Executor**: Manages agent execution loop

**Agent Behavior:**
1. Receives user input
2. Analyzes what's needed
3. Decides which tools to use
4. Executes tool calls
5. Synthesizes information
6. Generates natural language response

## Data Flow Diagrams

### Embedding Space

```
Documents                    Embedding Model              Vector Space
─────────                    ───────────────              ────────────

"RAG is an AI         →     [0.12, -0.34, 0.56,    →     Point A
 framework..."                0.89, ...]

"Vector embeddings    →     [0.15, -0.29, 0.61,    →     Point B
 represent text..."           0.85, ...]                  (close to A)

"The weather today    →     [-0.67, 0.23, -0.12,   →     Point C
 is sunny..."                 0.34, ...]                  (far from A, B)


Query: "What is RAG?"  →    [0.13, -0.35, 0.57,    →     Query Point
                              0.88, ...]                  (closest to A)

Cosine Similarity:
Query ↔ A: 0.92 ✓ (retrieved)
Query ↔ B: 0.78 ✓ (retrieved)
Query ↔ C: 0.31 ✗ (not retrieved)
```

### Memory and Context

```
Conversation Flow:

Turn 1:
User: "What is RAG?"
Agent: "RAG is a framework that..."
         │
         ├─> Stored in Memory
         │
Turn 2:
User: "How does it work?"  ← Needs context!
         │
         ├─> Memory loaded
         │   Context: Previous Q&A about RAG
         │
Agent: "RAG works by first retrieving..." ← Context-aware answer
```

## Configuration System

All system behavior is controlled via `config.yaml`:

```yaml
embeddings:
  provider: "openai"      # or "huggingface"
  model: "..."            # Model selection

vector_db:
  provider: "chroma"
  persist_directory: "./chroma_db"
  collection_name: "knowledge_base"

chunking:
  chunk_size: 1000        # Characters per chunk
  chunk_overlap: 200      # Overlap for context

retrieval:
  top_k: 4               # Number of chunks to retrieve
  search_type: "similarity"

llm:
  provider: "openai"      # or "ollama" for local
  model: "gpt-4o-mini"
  temperature: 0          # Deterministic responses
  max_tokens: 1000

agent:
  max_iterations: 5       # Prevent infinite loops
  verbose: true           # Debug output
  agent_type: "openai-tools"
```

## Scalability Considerations

### Current Implementation
- **Local storage**: ChromaDB with disk persistence
- **Single-user**: CLI interface
- **Synchronous**: Sequential processing

### Future Enhancements
- **Remote vector DB**: Pinecone, Weaviate, or Qdrant for production
- **Web interface**: FastAPI + React frontend
- **Async processing**: Handle multiple queries concurrently
- **Caching**: Redis for frequent queries
- **Monitoring**: LangSmith or custom telemetry

## Security & Privacy

- **API Keys**: Stored in `.env`, never committed
- **Local Processing**: Documents stay on your machine
- **No Data Sharing**: Vector DB is private
- **Configurable**: Can use fully local models (Ollama)

## Performance Optimization

1. **Chunk Size**: Balance between context and precision
2. **Top-K**: More results = better context, slower responses
3. **Embeddings**: OpenAI (quality) vs HuggingFace (speed/local)
4. **LLM Choice**: GPT-4 (quality) vs GPT-4o-mini (speed/cost)

## Error Handling

The system includes robust error handling:
- **Missing documents**: Clear error messages
- **API failures**: Graceful degradation
- **Invalid queries**: User-friendly feedback
- **Database issues**: Automatic recovery when possible

## Testing

Use `test_system.py` to verify:
- ✓ All dependencies installed
- ✓ Environment configured
- ✓ Config file valid
- ✓ Documents present
- ✓ Vector DB created
- ✓ Modules importable

## Extending the System

### Adding New Tools

```python
# In src/agent_tools.py

class MyCustomTool(BaseTool):
    name: str = "my_tool"
    description: str = "What my tool does..."

    def _run(self, input: str) -> str:
        # Tool logic here
        return result

# Register in create_agent_tools()
```

### Supporting New Document Types

```python
# In src/document_processor.py

loaders = {
    '*.txt': TextLoader,
    '*.pdf': PyPDFLoader,
    '*.csv': CSVLoader,  # Add new loader
}
```

### Using Different LLMs

```yaml
# In config.yaml

llm:
  provider: "ollama"
  ollama_model: "llama2"
  ollama_base_url: "http://localhost:11434"
```

## Summary

This agentic RAG system provides:
- ✓ Complete RAG pipeline (ingest → store → retrieve → generate)
- ✓ Intelligent agent with tool use
- ✓ Conversation memory
- ✓ Flexible configuration
- ✓ Production-ready architecture
- ✓ Extensible design

Perfect for building knowledge-based Q&A systems over custom documents!
