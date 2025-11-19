#!/bin/bash
# Quick setup script for the Agentic RAG System

echo "=================================="
echo "Agentic RAG System - Quick Setup"
echo "=================================="

# Check Python version
echo -e "\nChecking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version detected"
else
    echo "✗ Python 3.9+ required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo -e "\nCreating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\nActivating virtual environment..."
source venv/bin/activate

# Install dependencies
echo -e "\nInstalling dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
echo -e "\nChecking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found. Creating from template..."
    cp .env.example .env
    echo "✗ Please edit .env and add your OPENAI_API_KEY"
    echo "  Run: nano .env"
else
    echo "✓ .env file exists"
fi

# Check if API key is set
if [ -f ".env" ]; then
    if grep -q "your_openai_api_key_here" .env; then
        echo "⚠ Warning: Please update your OPENAI_API_KEY in .env"
    else
        echo "✓ API key appears to be configured"
    fi
fi

# Create documents directory
if [ ! -d "documents" ]; then
    mkdir -p documents
    echo "✓ Documents directory created"
fi

echo -e "\n=================================="
echo "Setup Complete!"
echo "=================================="
echo -e "\nNext steps:"
echo "1. Add your OpenAI API key to .env file"
echo "2. Add documents to the documents/ directory"
echo "3. Run: python ingest_documents.py"
echo "4. Run: python main.py"
echo -e "\nFor detailed instructions, see QUICKSTART.md"
