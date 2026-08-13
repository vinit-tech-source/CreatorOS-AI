"""
app/rag/ingestion/pipeline.py

Pipeline for extracting, cleaning, chunking, embedding, and storing documents.
"""
import uuid
from typing import List

from app.rag.schemas.document import RAGDocument, RAGChunk
from app.rag.embeddings.base import EmbeddingProvider
from app.rag.vectorstore.base import VectorStore
from app.core.config import settings
from app.rag.exceptions.exceptions import RAGValidationError


class TextChunker:
    """A deterministic text chunker using sliding window."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
        self.overlap = chunk_overlap or settings.RAG_CHUNK_OVERLAP
        
        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be greater than 0.")
        if self.overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be strictly less than chunk size.")
            
    def chunk_document(self, document: RAGDocument) -> List[RAGChunk]:
        """Split a document's content into RAGChunks."""
        content = document.content.strip()
        if not content:
            raise RAGValidationError("Cannot chunk an empty document.")
            
        chunks = []
        start = 0
        chunk_idx = 0
        
        while start < len(content):
            end = start + self.chunk_size
            chunk_content = content[start:end]
            
            # Optionally, we could adjust 'end' to the nearest word boundary here.
            # For foundational MVP, exact slice is sufficient.
            
            chunk = RAGChunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                chunk_index=chunk_idx,
                content=chunk_content,
                # Inject workspace_id into metadata to guarantee it's passed to vector store
                metadata={**document.metadata, "workspace_id": document.workspace_id}
            )
            chunks.append(chunk)
            
            chunk_idx += 1
            start += (self.chunk_size - self.overlap)
            
        return chunks


class IngestionPipeline:
    """Coordinates the ingestion of documents into the RAG system."""
    
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunker = TextChunker()
        
    async def ingest_document(self, document: RAGDocument) -> List[RAGChunk]:
        """
        Extract -> Clean -> Chunk -> Embed -> Store.
        """
        # For foundation, we assume Document content is already extracted text.
        # Clean
        if not document.content or not document.content.strip():
            raise RAGValidationError("Document content cannot be empty.")
            
        # Chunk
        chunks = self.chunker.chunk_document(document)
        
        # Embed
        texts_to_embed = [c.content for c in chunks]
        embeddings = await self.embedding_provider.embed_documents(texts_to_embed)
        
        # Store
        await self.vector_store.add_documents(chunks, embeddings)
        
        return chunks
