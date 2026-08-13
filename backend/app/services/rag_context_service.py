"""
app/services/rag_context_service.py

High-level RAG Context Service for LangGraph Agents.
"""
import logging
from typing import List, Dict, Any

from app.services.rag_service import RAGService
from app.core.config import settings
from app.rag.embeddings.base import FakeEmbeddingProvider
from app.rag.vectorstore.base import InMemoryVectorStore
from app.rag.exceptions.exceptions import RAGProviderError

logger = logging.getLogger(__name__)

# Global instances for the MVP foundation since we lack full DI for RAG
_global_embedding_provider = FakeEmbeddingProvider()
_global_vector_store = InMemoryVectorStore()

def get_rag_service() -> RAGService:
    return RAGService(
        embedding_provider=_global_embedding_provider,
        vector_store=_global_vector_store
    )

class RAGContextService:
    """
    Service responsible for retrieving safe, normalized workspace context
    for consumption by LangGraph AI agents.
    """
    
    def __init__(self, rag_service: RAGService = None):
        self.rag_service = rag_service or get_rag_service()
        
    async def retrieve_agent_context(
        self,
        query: str,
        workspace_id: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves workspace-scoped context, applies score thresholding,
        and enforces maximum context token limits deterministically.
        
        Args:
            query: Focused search query (not necessarily the full prompt).
            workspace_id: Strict tenant isolation parameter.
            top_k: Max chunks to fetch from vector DB.
            
        Returns:
            List of safely serialized dictionaries containing chunk text and safe metadata.
        """
        if not settings.RAG_ENABLED:
            logger.info("RAG is disabled in configuration. Skipping retrieval.")
            return []
            
        actual_top_k = top_k or settings.RAG_TOP_K
        
        try:
            raw_chunks = await self.rag_service.retrieve_context(
                query=query,
                workspace_id=workspace_id,
                top_k=actual_top_k
            )
        except RAGProviderError as e:
            logger.error(f"RAG Provider failed during context retrieval: {str(e)}")
            return [] # Fail open, do not corrupt workflow if RAG is down
            
        valid_chunks = []
        total_tokens = 0
        
        for chunk in raw_chunks:
            if chunk.score < settings.RAG_MIN_SCORE:
                continue
                
            # Naive token estimation: ~4 chars per token
            chunk_tokens = len(chunk.content) // 4
            
            if total_tokens + chunk_tokens > settings.RAG_MAX_CONTEXT_TOKENS:
                # Deterministic truncation: stop adding chunks if we exceed budget
                logger.info("RAG context max tokens reached. Truncating further chunks.")
                break
                
            valid_chunks.append({
                "content": chunk.content,
                "score": chunk.score,
                "metadata": chunk.metadata
            })
            total_tokens += chunk_tokens
            
        return valid_chunks
