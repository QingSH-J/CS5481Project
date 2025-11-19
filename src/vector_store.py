"""
Vector Store Module
Handles vector database operations using ChromaDB.
"""

import yaml
from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


class VectorStoreManager:
    """Manages the vector database for document storage and retrieval."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the vector store manager.

        Args:
            config_path: Path to the configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.persist_directory = self.config['vector_db']['persist_directory']
        self.collection_name = self.config['vector_db']['collection_name']

        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()

        # Vector store (will be initialized on first use)
        self.vector_store = None

    def _initialize_embeddings(self):
        """Initialize the embedding model based on configuration."""
        provider = self.config['embeddings']['provider']

        if provider == 'gemini':
            model = self.config['embeddings']['model']
            print(f"Using Google Gemini embeddings: {model}")
            return GoogleGenerativeAIEmbeddings(model=model)

        elif provider == 'openai':
            model = self.config['embeddings'].get('openai_model', self.config['embeddings'].get('model'))
            print(f"Using OpenAI embeddings: {model}")
            return OpenAIEmbeddings(model=model)

        elif provider == 'huggingface':
            model = self.config['embeddings'].get(
                'huggingface_model',
                'sentence-transformers/all-MiniLM-L6-v2'
            )
            print(f"Using HuggingFace embeddings: {model}")
            return HuggingFaceEmbeddings(model_name=model)

        else:
            raise ValueError(f"Unsupported embeddings provider: {provider}")

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Create a new vector store from documents.

        Args:
            documents: List of documents to add to the vector store

        Returns:
            Chroma vector store instance
        """
        print(f"Creating vector store with {len(documents)} documents...")

        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )

        print(f"Vector store created and persisted to {self.persist_directory}")
        return self.vector_store

    def load_vector_store(self) -> Chroma:
        """
        Load an existing vector store from disk.

        Returns:
            Chroma vector store instance
        """
        print(f"Loading vector store from {self.persist_directory}")

        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )

        return self.vector_store

    def add_documents(self, documents: List[Document]):
        """
        Add documents to an existing vector store.

        Args:
            documents: List of documents to add
        """
        if self.vector_store is None:
            self.load_vector_store()

        self.vector_store.add_documents(documents)
        print(f"Added {len(documents)} documents to vector store")

    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Perform similarity search on the vector store.

        Args:
            query: Search query
            k: Number of results to return (uses config default if None)
            filter: Optional metadata filter

        Returns:
            List of most similar documents
        """
        if self.vector_store is None:
            self.load_vector_store()

        if k is None:
            k = self.config['retrieval']['top_k']

        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter=filter
        )

        return results

    def similarity_search_with_score(
        self,
        query: str,
        k: int = None,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of (document, score) tuples
        """
        if self.vector_store is None:
            self.load_vector_store()

        if k is None:
            k = self.config['retrieval']['top_k']

        results = self.vector_store.similarity_search_with_score(
            query,
            k=k,
            filter=filter
        )

        return results

    def as_retriever(self, **kwargs):
        """
        Get the vector store as a retriever for LangChain.

        Args:
            **kwargs: Additional arguments for the retriever

        Returns:
            Retriever instance
        """
        if self.vector_store is None:
            self.load_vector_store()

        search_kwargs = {
            'k': self.config['retrieval']['top_k'],
        }
        search_kwargs.update(kwargs)

        return self.vector_store.as_retriever(
            search_type=self.config['retrieval']['search_type'],
            search_kwargs=search_kwargs
        )


if __name__ == "__main__":
    # Test the vector store
    manager = VectorStoreManager()
    print("Vector store manager initialized successfully")
