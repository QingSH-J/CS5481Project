# Google Gemini Setup Guide

This guide explains how to configure the Agentic RAG system to use Google Gemini instead of OpenAI.

## Why Use Gemini?

- **Free Tier**: Google offers generous free tier for Gemini API
- **Fast**: Gemini 1.5 Flash is very fast and cost-effective
- **Privacy**: Keep your data within Google's ecosystem
- **Latest Features**: Access to Google's latest AI models

## Prerequisites

1. Google account
2. Google AI Studio API key

## Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key (starts with `AIza...`)

## Step 2: Configure Environment

Edit your `.env` file and add:

```bash
GOOGLE_API_KEY=AIzaSy...your_key_here
```

Or create the file:

```bash
echo "GOOGLE_API_KEY=AIzaSy...your_key_here" > .env
```

## Step 3: Configuration is Already Set

The system is already configured to use Gemini! Check `config.yaml`:

```yaml
# Embedding Configuration
embeddings:
  provider: "gemini"
  model: "models/embedding-001"

# LLM Configuration
llm:
  provider: "gemini"
  model: "gemini-1.5-flash"
  temperature: 0
  max_tokens: 1000

# Agent Configuration
agent:
  agent_type: "react"  # Gemini uses ReAct agent
```

## Step 4: Install Dependencies

Install the Gemini-specific packages:

```bash
pip install -r requirements.txt
```

This will install:
- `google-generativeai` - Google's Gemini API client
- `langchain-google-genai` - LangChain integration for Gemini

## Step 5: Run the System

Now you can use the system with Gemini:

```bash
# Ingest documents
python ingest_documents.py

# Run the RAG system
python main.py
```

## Available Gemini Models

### For Embeddings

- `models/embedding-001` (recommended) - 768 dimensions

### For LLM

- `gemini-2.0-flash` (default, recommended) - Fast and cost-effective
- `gemini-1.5-pro` - More capable, slower
- `gemini-pro` - Legacy model

Update in `config.yaml`:

```yaml
llm:
  model: "gemini-1.5-pro"  # Change model here
```

## Switching Between OpenAI and Gemini

You can easily switch between providers by editing `config.yaml`:

### Use Gemini:

```yaml
embeddings:
  provider: "gemini"
  model: "models/embedding-001"

llm:
  provider: "gemini"
  model: "gemini-1.5-flash"

agent:
  agent_type: "react"
```

### Use OpenAI:

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

**Note**: If you switch providers, you need to re-ingest your documents with `--reset`:

```bash
python ingest_documents.py --reset
```

This is because different embedding models create incompatible vector representations.

## Troubleshooting

### "GOOGLE_API_KEY not found"

Make sure:
1. You created a `.env` file in the project root
2. The file contains `GOOGLE_API_KEY=your_key`
3. No quotes around the key
4. No spaces around the `=`

### "Invalid API key"

1. Check your key at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Make sure it starts with `AIza`
3. Try generating a new key

### "Quota exceeded"

Gemini has rate limits:
- Free tier: 60 requests per minute
- If you hit limits, wait a minute or upgrade to paid tier

### Agent not using tools properly

Make sure `agent_type` is set to `"react"` in config.yaml for Gemini models.

## Cost Comparison

### Gemini (Free Tier)
- Embeddings: 1,500 requests/day free
- Text generation: 60 requests/minute free
- **Monthly cost: $0**

### OpenAI
- Embeddings: $0.00002 per 1K tokens
- GPT-4o-mini: $0.150 per 1M input tokens
- **Monthly cost: ~$5-20** (typical usage)

## Performance Comparison

| Feature | Gemini 1.5 Flash | GPT-4o-mini |
|---------|------------------|-------------|
| Speed | Very Fast | Fast |
| Quality | Excellent | Excellent |
| Context | 1M tokens | 128K tokens |
| Cost | Free tier available | Paid only |
| Tools/Functions | Supported | Native support |

## Next Steps

Once configured, use the system normally:

```bash
python main.py
```

Try asking:
- "What is RAG?"
- "How does chunking work?"
- "Show me knowledge base stats"

Enjoy using Gemini with your RAG system!
