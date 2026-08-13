"""
app/rag/vectorstore/base.py

Abstract base class for Vector Stores and an In-Memory mock for foundational testing.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.rag.schemas.document import RAGChunk, RetrievedChunk


class VectorStore(ABC):
    """Abstract base class for vector databases."""
    
    @abstractmethod
    async def add_documents(self, chunks: List[RAGChunk], embeddings: List[List[float]]):
        """Add chunks and their embeddings to the vector store."""
        pass
        
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]):
        """Delete all chunks associated with specific document IDs."""
        pass
        
    @abstractmethod
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        workspace_id: str, 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Search for similar chunks. MUST strictly isolate by workspace_id.
        """
        pass
        
    @abstractmethod
    async def similarity_search_with_score(
        self,
        query_embedding: List[float],
        workspace_id: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Search and return chunks with explicit scores.
        """
        pass


class InMemoryVectorStore(VectorStore):
    """An in-memory vector store for foundational testing without external dependencies."""
    
    def __init__(self):
        # Store tuples of (RAGChunk, embedding)
        self._store: List[tuple[RAGChunk, List[float]]] = []
        
    async def add_documents(self, chunks: List[RAGChunk], embeddings: List[List[float]]):
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must equal number of embeddings.")
        for chunk, emb in zip(chunks, embeddings):
            self._store.append((chunk, emb))
            
    async def delete_documents(self, document_ids: List[str]):
        doc_id_set = set(document_ids)
        self._store = [(c, e) for c, e in self._store if c.document_id not in doc_id_set]
        
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        workspace_id: str, 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        return await self.similarity_search_with_score(query_embedding, workspace_id, top_k, filter_metadata)
        
    async def similarity_search_with_score(
        self,
        query_embedding: List[float],
        workspace_id: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        # Filter by workspace FIRST (Strict Isolation)
        valid_pairs = [
            (c, e) for c, e in self._store 
            if c.metadata.get("workspace_id") == workspace_id
        ]
        
        # Apply additional metadata filters
        if filter_metadata:
            valid_pairs = [
                (c, e) for c, e in valid_pairs
                if all(c.metadata.get(k) == v for k, v in filter_metadata.items())
            ]
            
        results = []
        for chunk, emb in valid_pairs:
            # Fake dot product similarity
            score = sum(q * doc for q, doc in zip(query_embedding, emb))
            results.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=score,
                    metadata=chunk.metadata
                )
            )
            
        # Sort descending by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
