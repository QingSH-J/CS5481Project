"""
Test Script
Quick test to verify the system is working correctly.
"""

import os
import sys
from dotenv import load_dotenv


def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    try:
        import langchain
        import chromadb
        import openai
        import yaml
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_community.vectorstores import Chroma
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def test_env():
    """Test if environment variables are configured."""
    print("\nTesting environment configuration...")
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY not found in environment")
        print("Create a .env file with your API key")
        return False

    if api_key.startswith("sk-"):
        print("✓ OPENAI_API_KEY is configured")
        return True
    else:
        print("⚠ OPENAI_API_KEY format looks incorrect")
        return False


def test_config():
    """Test if configuration file exists and is valid."""
    print("\nTesting configuration...")
    try:
        import yaml
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)

        required_keys = ['embeddings', 'vector_db', 'chunking', 'retrieval', 'llm', 'agent']
        for key in required_keys:
            if key not in config:
                print(f"✗ Missing config key: {key}")
                return False

        print("✓ Configuration file is valid")
        return True
    except FileNotFoundError:
        print("✗ config.yaml not found")
        return False
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False


def test_documents():
    """Test if documents directory exists and has files."""
    print("\nTesting documents...")

    if not os.path.exists("documents"):
        print("✗ Documents directory not found")
        return False

    files = [f for f in os.listdir("documents")
             if f.endswith(('.txt', '.pdf', '.md', '.docx')) and not f.startswith('.')]

    if not files:
        print("⚠ No documents found in documents/ directory")
        print("Add some documents before running ingestion")
        return False

    print(f"✓ Found {len(files)} document(s): {', '.join(files[:3])}")
    return True


def test_vector_db():
    """Test if vector database exists."""
    print("\nTesting vector database...")

    import yaml
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    persist_dir = config['vector_db']['persist_directory']

    if not os.path.exists(persist_dir):
        print(f"⚠ Vector database not found at {persist_dir}")
        print("Run: python ingest_documents.py")
        return False

    print(f"✓ Vector database exists at {persist_dir}")
    return True


def test_modules():
    """Test if custom modules can be imported."""
    print("\nTesting custom modules...")
    try:
        from src.document_processor import DocumentProcessor
        from src.vector_store import VectorStoreManager
        from src.agent_tools import create_agent_tools
        from src.agent import AgenticRAG
        print("✓ All custom modules can be imported")
        return True
    except ImportError as e:
        print(f"✗ Error importing custom module: {e}")
        return False


def main():
    """Run all tests."""
    print("="*50)
    print("Agentic RAG System - Test Suite")
    print("="*50)

    results = {
        "Imports": test_imports(),
        "Environment": test_env(),
        "Configuration": test_config(),
        "Custom Modules": test_modules(),
        "Documents": test_documents(),
        "Vector Database": test_vector_db(),
    }

    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<30} {status}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("Run: python main.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("See QUICKSTART.md for setup instructions.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
