"""
Document Processing Module
Handles loading, chunking, and preprocessing of documents for the RAG system.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class DocumentProcessor:
    """Handles document loading and chunking for the knowledge base."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the document processor.

        Args:
            config_path: Path to the configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.chunk_size = self.config['chunking']['chunk_size']
        self.chunk_overlap = self.config['chunking']['chunk_overlap']
        self.separators = self.config['chunking']['separators']
        self.documents_dir = self.config['data_sources']['documents_directory']

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
        )

    def load_documents(self, directory: str = None) -> List[Document]:
        """
        Load all documents from the specified directory.

        Args:
            directory: Directory containing documents (uses config default if None)

        Returns:
            List of loaded documents
        """
        if directory is None:
            directory = self.documents_dir

        if not os.path.exists(directory):
            raise ValueError(f"Documents directory not found: {directory}")

        documents = []

        # Load different file types
        loaders = {
            '*.txt': TextLoader,
            '*.md': UnstructuredMarkdownLoader,
            '*.pdf': PyPDFLoader,
            '*.docx': Docx2txtLoader,
        }

        for pattern, loader_class in loaders.items():
            try:
                loader = DirectoryLoader(
                    directory,
                    glob=pattern,
                    loader_cls=loader_class,
                    show_progress=True
                )
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded {len(docs)} documents matching {pattern}")
            except Exception as e:
                print(f"Warning: Error loading {pattern} files: {e}")

        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: List of documents to chunk

        Returns:
            List of chunked documents
        """
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

    def process_documents(self, directory: str = None) -> List[Document]:
        """
        Complete pipeline: load and chunk documents.

        Args:
            directory: Directory containing documents

        Returns:
            List of chunked documents ready for embedding
        """
        print("Loading documents...")
        documents = self.load_documents(directory)

        if not documents:
            raise ValueError("No documents found to process")

        print(f"Successfully loaded {len(documents)} documents")

        print("Chunking documents...")
        chunks = self.chunk_documents(documents)

        return chunks

    def add_metadata(self, chunks: List[Document], metadata: Dict[str, Any]) -> List[Document]:
        """
        Add custom metadata to document chunks.

        Args:
            chunks: List of document chunks
            metadata: Dictionary of metadata to add

        Returns:
            Chunks with updated metadata
        """
        for chunk in chunks:
            chunk.metadata.update(metadata)
        return chunks


if __name__ == "__main__":
    # Test the document processor
    processor = DocumentProcessor()
    try:
        chunks = processor.process_documents()
        print(f"\nSuccessfully processed documents into {len(chunks)} chunks")
        print(f"Sample chunk:\n{chunks[0].page_content[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
