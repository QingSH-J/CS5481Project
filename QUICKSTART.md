# Quick Start Guide

Get up and running with the Agentic RAG system in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- **Google Gemini API key** (get one at https://makersuite.google.com/app/apikey - **FREE tier available!**)
  - OR OpenAI API key (https://platform.openai.com/api-keys - paid only)

## Setup Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Key

**Option A: Using Google Gemini (Recommended - FREE!)**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google Gemini API key
# GOOGLE_API_KEY=AIza...your-key-here
```

On macOS/Linux:
```bash
echo "GOOGLE_API_KEY=AIza...your-key-here" > .env
```

**Option B: Using OpenAI**

If you prefer OpenAI, update `config.yaml`:
```yaml
embeddings:
  provider: "openai"
  model: "text-embedding-3-small"

llm:
  provider: "openai"
  model: "gpt-4o-mini"

agent:
  agent_type: "openai-tools"
```

Then add your OpenAI key:
```bash
echo "OPENAI_API_KEY=sk-...your-key-here" > .env
```

### 3. Add Documents

The project includes a sample document to get you started:
- `documents/sample_knowledge.md` - Information about RAG systems

Add your own documents:
```bash
cp /path/to/your/documents/*.pdf documents/
cp /path/to/your/documents/*.txt documents/
```

Supported formats: PDF, TXT, MD, DOCX

### 4. Ingest Documents

Process documents and create the vector database:

```bash
python ingest_documents.py
```

You should see output like:
```
Processing documents...
Loaded 1 documents matching *.md
Split 1 documents into 15 chunks
Creating vector embeddings...
Ingestion Complete!
```

### 5. Run the System

Start the interactive chat:

```bash
python main.py
```

## Example Questions

Try asking these questions:

- "What is retrieval-augmented generation?"
- "How does chunking work in RAG systems?"
- "What are the benefits of using RAG?"
- "Tell me about vector embeddings"
- "What is ChromaDB?"
- "What are best practices for RAG systems?"

## Commands

While chatting:
- `/help` - Show available commands
- `/stats` - View knowledge base statistics
- `/clear` - Clear conversation history
- `/quit` - Exit

## Single Question Mode

Ask a question without entering interactive mode:

```bash
python main.py --question "What is RAG?"
```

## Customization

Edit `config.yaml` to customize:

- **Chunk size**: How documents are split
  ```yaml
  chunking:
    chunk_size: 1000
    chunk_overlap: 200
  ```

- **Number of results**: How many chunks to retrieve
  ```yaml
  retrieval:
    top_k: 4
  ```

- **LLM model**: Which model to use
  ```yaml
  llm:
    model: "gemini-2.0-flash"  # or "gemini-1.5-pro" for better quality
  ```

## Troubleshooting

### "GOOGLE_API_KEY not found" or "OPENAI_API_KEY not found"
Make sure you created the `.env` file with the appropriate API key:
```bash
cat .env
# Should show: GOOGLE_API_KEY=AIza... (for Gemini)
# OR: OPENAI_API_KEY=sk-... (for OpenAI)
```

### "Vector database not found"
Run the ingestion script first:
```bash
python ingest_documents.py
```

### "No documents found"
Add documents to the `documents/` directory and run ingestion again

### Want to start fresh?
Reset the database:
```bash
python ingest_documents.py --reset
```

## Next Steps

1. **Add your own documents**: Replace or add to the sample documents
2. **Experiment with settings**: Try different chunk sizes and retrieval parameters
3. **Explore the code**: Check out the modules in `src/`
4. **Read the full README**: See `README.md` for detailed documentation

## Getting Help

- Check `README.md` for detailed documentation
- Review `config.yaml` for all configuration options
- See the example in `documents/sample_knowledge.md`

Enjoy your Agentic RAG system!
