"""
app/services/rag_service.py

High-level RAG Service orchestrating ingestion and retrieval.
"""
from typing import List, Dict, Any, Optional

from app.rag.schemas.document import RAGDocument, RAGChunk, RetrievedChunk
from app.rag.embeddings.base import EmbeddingProvider
from app.rag.vectorstore.base import VectorStore
from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.retriever.retriever import RAGRetriever


class RAGService:
    """Service to interact with the RAG foundation."""
    
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore):
        self.pipeline = IngestionPipeline(embedding_provider, vector_store)
        self.retriever = RAGRetriever(embedding_provider, vector_store)
        self.vector_store = vector_store
        
    async def ingest_document(self, document: RAGDocument) -> List[RAGChunk]:
        """Ingest a new document into the RAG system."""
        # Sanitize metadata before ingestion to ensure no sensitive fields enter vector DB
        document.metadata = self._sanitize_metadata(document.metadata)
        return await self.pipeline.ingest_document(document)
        
    async def retrieve_context(
        self,
        query: str,
        workspace_id: str,
        top_k: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """Retrieve relevant context for a given query and workspace."""
        return await self.retriever.retrieve(
            query=query,
            workspace_id=workspace_id,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
    async def delete_document(self, document_id: str):
        """Delete a document from the RAG system."""
        await self.vector_store.delete_documents([document_id])
        
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove any potentially sensitive information from metadata before vector storage."""
        sensitive_keys = {"password", "token", "secret", "key", "authorization", "credential", "auth_"}
        sanitized = {}
        for k, v in metadata.items():
            k_lower = k.lower()
            if any(sec in k_lower for sec in sensitive_keys):
                continue
            sanitized[k] = v
        return sanitized
