"""
app/rag/schemas/document.py

Pydantic schemas for RAG documents, chunks, and retrieval.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RAGDocument(BaseModel):
    """Represents a complete document ingested into the RAG system."""
    id: str
    workspace_id: str
    source_type: str = Field(..., description="e.g., 'text', 'pdf', 'webpage'")
    source_id: Optional[str] = None
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RAGChunk(BaseModel):
    """Represents a single chunk of a RAGDocument prepared for embedding."""
    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """Represents a chunk retrieved from the vector store."""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
