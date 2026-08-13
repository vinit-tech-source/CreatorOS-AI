"""
app/rag/retriever/retriever.py

Retriever abstraction enforcing workspace isolation and metadata filtering.
"""
from typing import List, Dict, Any, Optional

from app.rag.schemas.document import RetrievedChunk
from app.rag.embeddings.base import EmbeddingProvider
from app.rag.vectorstore.base import VectorStore
from app.core.config import settings
from app.rag.exceptions.exceptions import RAGProviderError


class RAGRetriever:
    """Retrieves relevant context from the vector store with enforced workspace isolation."""
    
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        
    async def retrieve(
        self,
        query: str,
        workspace_id: str,
        top_k: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve chunks relevant to the query.
        
        Args:
            query: The natural language search query.
            workspace_id: The mandatory workspace ID to enforce tenant isolation.
            top_k: Maximum chunks to return. Defaults to RAG_TOP_K.
            filter_metadata: Additional strict metadata filters.
            
        Returns:
            List of RetrievedChunk sorted by relevance.
        """
        if not query or not query.strip():
            return []
            
        if not workspace_id:
            raise ValueError("workspace_id must be provided for RAG retrieval to guarantee isolation.")
            
        actual_top_k = top_k or settings.RAG_TOP_K
        
        try:
            # Generate the query embedding
            query_embedding = await self.embedding_provider.embed_text(query)
            
            # Perform similarity search with STRICT workspace isolation
            results = await self.vector_store.similarity_search(
                query_embedding=query_embedding,
                workspace_id=str(workspace_id),
                top_k=actual_top_k,
                filter_metadata=filter_metadata
            )
            
            return results
        except Exception as e:
            raise RAGProviderError(f"RAG retrieval failed: {str(e)}")
