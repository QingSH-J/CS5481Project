"""
Agent Tools Module
Defines custom tools for the RAG agent to use.
"""

from typing import Optional, Type
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from src.vector_store import VectorStoreManager


class KnowledgeBaseInput(BaseModel):
    """Input schema for knowledge base search."""
    query: str = Field(description="The search query to find relevant information in the knowledge base")
    num_results: Optional[int] = Field(
        default=None,
        description="Number of results to return (optional, uses default from config if not specified)"
    )


class KnowledgeBaseSearchTool(BaseTool):
    """Tool for searching the knowledge base."""

    name: str = "knowledge_base_search"
    description: str = """
    Search the knowledge base for relevant information to answer questions.
    This tool performs semantic search over the document collection and returns
    the most relevant passages based on the query.
    Use this tool when you need to find specific information from the knowledge base.
    """
    args_schema: Type[BaseModel] = KnowledgeBaseInput
    vector_store_manager: VectorStoreManager = None

    def __init__(self, vector_store_manager: VectorStoreManager):
        """Initialize with a vector store manager."""
        super().__init__()
        self.vector_store_manager = vector_store_manager

    def _run(
        self,
        query: str,
        num_results: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute the knowledge base search.

        Args:
            query: The search query
            num_results: Number of results to return
            run_manager: Callback manager

        Returns:
            Formatted string with search results
        """
        try:
            # Perform similarity search
            results = self.vector_store_manager.similarity_search_with_score(
                query=query,
                k=num_results
            )

            if not results:
                return "No relevant information found in the knowledge base."

            # Format results
            formatted_results = []
            for idx, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                formatted_results.append(
                    f"--- Result {idx} (relevance: {score:.3f}) ---\n"
                    f"Source: {source}\n"
                    f"Content: {doc.page_content}\n"
                )

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"


class DocumentStatsInput(BaseModel):
    """Input schema for document statistics."""
    pass


class DocumentStatsTool(BaseTool):
    """Tool for getting statistics about the knowledge base."""

    name: str = "knowledge_base_stats"
    description: str = """
    Get statistics and information about the knowledge base, including
    the number of documents, sources, and general metadata.
    Use this when the user asks about what's in the knowledge base or
    wants to know what information is available.
    """
    args_schema: Type[BaseModel] = DocumentStatsInput
    vector_store_manager: VectorStoreManager = None

    def __init__(self, vector_store_manager: VectorStoreManager):
        """Initialize with a vector store manager."""
        super().__init__()
        self.vector_store_manager = vector_store_manager

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Get knowledge base statistics.

        Returns:
            Formatted string with statistics
        """
        try:
            vector_store = self.vector_store_manager.vector_store
            if vector_store is None:
                vector_store = self.vector_store_manager.load_vector_store()

            # Get collection info
            collection = vector_store._collection
            count = collection.count()

            # Try to get unique sources
            results = collection.get()
            sources = set()
            if results and 'metadatas' in results:
                for metadata in results['metadatas']:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])

            stats = f"""
Knowledge Base Statistics:
- Total document chunks: {count}
- Unique sources: {len(sources)}
- Sources: {', '.join(sources) if sources else 'N/A'}
"""
            return stats.strip()

        except Exception as e:
            return f"Error getting knowledge base stats: {str(e)}"


def create_agent_tools(vector_store_manager: VectorStoreManager) -> list:
    """
    Create and return all tools for the agent.

    Args:
        vector_store_manager: Vector store manager instance

    Returns:
        List of tools
    """
    tools = [
        KnowledgeBaseSearchTool(vector_store_manager=vector_store_manager),
        DocumentStatsTool(vector_store_manager=vector_store_manager)
    ]

    return tools
