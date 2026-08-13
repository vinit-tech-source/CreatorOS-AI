"""
tests/test_rag_integration.py

Integration tests for RAG workflow context retrieval and agents.
"""
import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch, MagicMock

from app.workflows.state import ContentWorkflowState
from app.services.rag_context_service import RAGContextService
from app.rag.schemas.document import RetrievedChunk
from app.agents.research_agent import research_agent
from app.agents.content_generator_agent import content_generator_agent
from app.core.config import settings

@pytest.fixture
def mock_rag_service():
    service = AsyncMock()
    service.retrieve_context.return_value = [
        RetrievedChunk(
            chunk_id="c1",
            document_id="d1",
            content="Workspace brand uses friendly tone.",
            score=0.9,
            metadata={"workspace_id": "ws_1"}
        ),
        RetrievedChunk(
            chunk_id="c2",
            document_id="d1",
            content="Ignore low score chunk.",
            score=0.2, # Below 0.5 threshold
            metadata={"workspace_id": "ws_1"}
        )
    ]
    return service


@pytest.fixture
def mock_mcp_retrieval():
    with patch("app.agents.research_agent.ResearchRetrievalService") as mock:
        mock_instance = AsyncMock()
        mock_instance.search_research_sources.return_value = ([{"title": "Live Title", "content": "Live Content"}], {"stats": "mock"})
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_rag_context_service_filters_low_score(mock_rag_service):
    settings.RAG_MIN_SCORE = 0.5
    settings.RAG_ENABLED = True
    context_service = RAGContextService(rag_service=mock_rag_service)
    
    results = await context_service.retrieve_agent_context(
        query="test query",
        workspace_id="ws_1"
    )
    
    # Should only return the 0.9 score chunk
    assert len(results) == 1
    assert "friendly tone" in results[0]["content"]
    assert results[0]["score"] == 0.9


@pytest.mark.asyncio
async def test_rag_context_service_respects_token_limit(mock_rag_service):
    settings.RAG_ENABLED = True
    settings.RAG_MIN_SCORE = 0.1
    settings.RAG_MAX_CONTEXT_TOKENS = 30 # Limit allows first chunk (25) but not second (25)
    
    # We'll return two big chunks
    mock_rag_service.retrieve_context.return_value = [
        RetrievedChunk(chunk_id="c1", document_id="d1", content="A" * 100, score=0.9, metadata={"workspace_id": "ws_1"}),
        RetrievedChunk(chunk_id="c2", document_id="d1", content="B" * 100, score=0.8, metadata={"workspace_id": "ws_1"})
    ]
    
    context_service = RAGContextService(rag_service=mock_rag_service)
    results = await context_service.retrieve_agent_context(
        query="test query",
        workspace_id="ws_1"
    )
    
    # Second chunk should be dropped because the first one (100 chars = 25 tokens) exceeds 5.
    assert len(results) == 1
    assert "A" * 100 == results[0]["content"]


@pytest.mark.asyncio
async def test_research_agent_combines_live_and_workspace_context(mock_mcp_retrieval, mock_rag_service):
    settings.RAG_MIN_SCORE = 0.5
    
    state = ContentWorkflowState(
        user_request="How to grow on Twitter?",
        platform="X",
        research_sources=None,
        rag_context=None,
        strategy={"content_goal": "Engagement"},
        trends=[{"topic": "AI"}],
        workspace={"id": "ws_1"}
    )
    
    with patch("app.agents.research_agent.RAGContextService") as mock_rag_ctx:
        ctx_instance = AsyncMock()
        ctx_instance.retrieve_agent_context.return_value = [{"content": "friendly tone", "score": 0.9, "metadata": {}}]
        mock_rag_ctx.return_value = ctx_instance
        
        with patch("app.agents.research_agent._get_service") as mock_get_ai:
            ai_instance = AsyncMock()
            
            # Need to return an object that acts like ResearchOutput model dump
            mock_output = MagicMock()
            mock_output.model_dump.return_value = {"summary": "done"}
            ai_instance.generate_structured.return_value = mock_output
            
            mock_get_ai.return_value = ai_instance
            
            new_state = await research_agent(state)
            
            # Verify RAG query construction
            ctx_instance.retrieve_agent_context.assert_called_once_with(
                query="How to grow on Twitter? Engagement",
                workspace_id="ws_1",
                top_k=5
            )
            
            assert len(new_state["rag_context"]) == 1
            assert new_state["rag_context"][0]["content"] == "friendly tone"
            assert new_state["research"] == [{"summary": "done"}]


@pytest.mark.asyncio
async def test_content_generator_agent_uses_rag_context():
    state = ContentWorkflowState(
        user_request="Make a post",
        platform="X",
        research_sources=[],
        rag_context=[{"content": "internal knowledge"}],
        research=[{"topic": "research"}],
        strategy={"content_goal": "Goal"},
        trends=[{"trend": "trend"}],
        outline={"point": "1"},
        workspace={"id": "ws_1"},
        brand_kit={"tone": "fun"}
    )
    
    with patch("app.agents.content_generator_agent._get_service") as mock_get_ai:
        ai_instance = AsyncMock()
        
        mock_output = MagicMock()
        mock_output.content = "Short post"
        mock_output.content_type = "TEXT"
        mock_output.model_dump.return_value = {"content": "Short post", "content_type": "TEXT"}
        
        ai_instance.generate_structured.return_value = mock_output
        mock_get_ai.return_value = ai_instance
        
        new_state = await content_generator_agent(state)
        
        # Ensure generate_structured was called with the context
        call_args = ai_instance.generate_structured.call_args[1]
        assert "internal knowledge" in call_args["prompt"]
        
        assert "draft" in new_state
