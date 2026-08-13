"""
tests/test_rag.py

Tests for the RAG foundation components.
"""
import uuid
import pytest
from datetime import datetime

from app.rag.schemas.document import RAGDocument, RAGChunk
from app.rag.embeddings.base import FakeEmbeddingProvider
from app.rag.vectorstore.base import InMemoryVectorStore
from app.rag.ingestion.pipeline import TextChunker, IngestionPipeline
from app.rag.retriever.retriever import RAGRetriever
from app.services.rag_service import RAGService
from app.rag.exceptions.exceptions import RAGValidationError, RAGProviderError
from app.core.config import settings


@pytest.fixture
def fake_embedding_provider():
    return FakeEmbeddingProvider(dimension=10)


@pytest.fixture
def in_memory_vector_store():
    return InMemoryVectorStore()


@pytest.fixture
def rag_service(fake_embedding_provider, in_memory_vector_store):
    return RAGService(fake_embedding_provider, in_memory_vector_store)


@pytest.fixture
def sample_document():
    return RAGDocument(
        id=str(uuid.uuid4()),
        workspace_id="workspace_1",
        source_type="text",
        title="Test Document",
        content="This is a test document. " * 50, # Sufficiently long to trigger chunking
        metadata={"author": "Test Author", "secret_key": "12345"}
    )


def test_text_chunker():
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    
    doc = RAGDocument(
        id="doc_1",
        workspace_id="ws_1",
        source_type="text",
        title="Title",
        content="A" * 100, # 100 characters
        metadata={}
    )
    
    chunks = chunker.chunk_document(doc)
    # Expected chunks:
    # 0-50 (len 50)
    # 40-90 (len 50)
    # 80-100 (len 20)
    assert len(chunks) == 3
    assert len(chunks[0].content) == 50
    assert chunks[0].chunk_index == 0
    assert chunks[0].metadata["workspace_id"] == "ws_1"
    
    
def test_text_chunker_empty_rejection():
    chunker = TextChunker()
    doc = RAGDocument(
        id="doc_1",
        workspace_id="ws_1",
        source_type="text",
        title="Title",
        content="   ", # empty
        metadata={}
    )
    with pytest.raises(RAGValidationError):
        chunker.chunk_document(doc)


@pytest.mark.asyncio
async def test_ingestion_and_retrieval(rag_service, sample_document):
    # Ingest
    chunks = await rag_service.ingest_document(sample_document)
    assert len(chunks) > 0
    
    # Retrieve
    results = await rag_service.retrieve_context(
        query="test",
        workspace_id="workspace_1",
        top_k=2
    )
    
    assert len(results) > 0
    assert results[0].document_id == sample_document.id
    assert "workspace_id" in results[0].metadata
    

@pytest.mark.asyncio
async def test_workspace_isolation(rag_service, sample_document):
    # Ingest document into workspace_1
    await rag_service.ingest_document(sample_document)
    
    # Attempt to retrieve from workspace_2
    results = await rag_service.retrieve_context(
        query="test",
        workspace_id="workspace_2"
    )
    
    # Must be totally empty due to strict isolation
    assert len(results) == 0


@pytest.mark.asyncio
async def test_sensitive_metadata_sanitization(rag_service, sample_document):
    # Contains "secret_key"
    assert "secret_key" in sample_document.metadata
    
    chunks = await rag_service.ingest_document(sample_document)
    
    # Should be stripped
    for chunk in chunks:
        assert "secret_key" not in chunk.metadata
        assert "author" in chunk.metadata


@pytest.mark.asyncio
async def test_metadata_filtering(rag_service):
    doc1 = RAGDocument(id="1", workspace_id="ws_1", source_type="text", title="1", content="content 1", metadata={"tag": "A"})
    doc2 = RAGDocument(id="2", workspace_id="ws_1", source_type="text", title="2", content="content 2", metadata={"tag": "B"})
    
    await rag_service.ingest_document(doc1)
    await rag_service.ingest_document(doc2)
    
    results = await rag_service.retrieve_context(
        query="query",
        workspace_id="ws_1",
        filter_metadata={"tag": "B"}
    )
    
    assert len(results) == 1
    assert results[0].document_id == "2"


@pytest.mark.asyncio
async def test_delete_document(rag_service, sample_document):
    await rag_service.ingest_document(sample_document)
    
    results_before = await rag_service.retrieve_context("test", "workspace_1")
    assert len(results_before) > 0
    
    await rag_service.delete_document(sample_document.id)
    
    results_after = await rag_service.retrieve_context("test", "workspace_1")
    assert len(results_after) == 0


@pytest.mark.asyncio
async def test_retriever_missing_workspace(rag_service):
    with pytest.raises(ValueError, match="workspace_id must be provided"):
        await rag_service.retrieve_context(
            query="test",
            workspace_id=""
        )
