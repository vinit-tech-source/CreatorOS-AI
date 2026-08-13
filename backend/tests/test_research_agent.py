"""
tests/test_research_agent.py

Tests for the AI Research Agent.
"""
from unittest.mock import AsyncMock
import uuid

import pytest

from app.agents import research_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.research import ResearchOutput, ResearchSource
from app.services.context_service import ContextService
from app.models.workspace import Workspace
from app.models.project import Project


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the research_agent module."""
    service = AsyncMock()
    research_agent._ai_service_instance = service
    yield service
    research_agent._ai_service_instance = None


@pytest.fixture
def valid_state():
    workspace = Workspace()
    workspace.id = uuid.uuid4()
    workspace.name = "Test Workspace"
    
    project = Project()
    project.id = uuid.uuid4()
    project.name = "Test Project"
    
    state = ContextService.assemble_initial_state(
        workspace=workspace,
        project=project,
        brand_kit=None,
        user_request="Write a thread about AI",
        platform="X"
    )
    # The research agent requires strategy and trends to be present
    state["strategy"] = {
        "content_goal": "Educate",
        "target_audience": "Developers",
        "platform_strategy": "Threads",
        "content_type": "Thread",
        "tone": "Educational",
        "language": "English",
        "call_to_action": "Read more",
        "constraints": []
    }
    state["trends"] = [
        {
            "trends": [{"topic": "AI", "relevance_score": 0.9, "platform_relevance": 0.9, "reason": "Hot topic"}],
            "recommended_hashtags": ["#AI"],
            "trend_summary": "AI is trending."
        }
    ]
    state["research_sources"] = [
        {
            "title": "State of AI 2026",
            "url": "https://example.com/ai-2026",
            "source_name": "Tech Insights",
            "published_at": "2026-01-01"
        }
    ]
    return state


@pytest.mark.asyncio
async def test_research_agent_success(mock_ai_service, valid_state):
    """Test that a valid input produces a valid ResearchOutput state update."""
    expected_output = ResearchOutput(
        summary="AI continues to grow in 2026.",
        key_facts=["AI adoption is up 50%."],
        sources=[
            ResearchSource(
                title="State of AI 2026",
                url="https://example.com/ai-2026",
                source_name="Tech Insights",
                published_at="2026-01-01",
                relevance_score=0.9,
                credibility_score=0.8,
                key_points=["Adoption up"]
            )
        ],
        uncertainties=["Future regulations are unclear."],
        research_confidence=0.85
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await research_agent.research_agent(valid_state)
    
    assert "research" in result
    assert len(result["research"]) == 1
    
    research_data = result["research"][0]
    assert research_data["summary"] == "AI continues to grow in 2026."
    assert len(research_data["sources"]) == 1
    assert str(research_data["sources"][0]["url"]) == "https://example.com/ai-2026"
    assert research_data["research_confidence"] == 0.85
    
    # Verify the AI service was called with the correct schema
    mock_ai_service.generate_structured.assert_called_once()
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert call_kwargs["response_schema"] == ResearchOutput
    assert "System:" in call_kwargs["prompt"]
    assert "User:" in call_kwargs["prompt"]
    # Ensure strategy, trends, and research_sources are included in the prompt
    assert "Educate" in call_kwargs["prompt"]
    assert "AI is trending." in call_kwargs["prompt"]
    assert "State of AI 2026" in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_research_agent_missing_user_request(valid_state):
    """Test that missing user_request raises ValueError."""
    valid_state["user_request"] = ""
    with pytest.raises(ValueError, match="Missing 'user_request'"):
        await research_agent.research_agent(valid_state)


@pytest.mark.asyncio
async def test_research_agent_missing_platform(valid_state):
    """Test that missing platform raises ValueError."""
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await research_agent.research_agent(valid_state)


@pytest.mark.asyncio
async def test_research_agent_missing_strategy(valid_state):
    """Test that missing strategy raises ValueError."""
    valid_state["strategy"] = None
    with pytest.raises(ValueError, match="Missing 'strategy'"):
        await research_agent.research_agent(valid_state)


@pytest.mark.asyncio
async def test_research_agent_missing_trends(valid_state):
    """Test that missing trends raises ValueError."""
    valid_state["trends"] = []
    with pytest.raises(ValueError, match="Missing 'trends'"):
        await research_agent.research_agent(valid_state)


@pytest.mark.asyncio
async def test_research_agent_no_sources(mock_ai_service, valid_state):
    """Test that the agent succeeds even if research_sources are missing."""
    valid_state["research_sources"] = []
    
    expected_output = ResearchOutput(
        summary="Knowledge-based summary without external sources.",
        key_facts=["AI is popular."],
        sources=[],
        uncertainties=["Missing live data"],
        research_confidence=0.5
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await research_agent.research_agent(valid_state)
    assert "research" in result
    assert result["research"][0]["sources"] == []


@pytest.mark.asyncio
async def test_research_agent_provider_failure(mock_ai_service, valid_state):
    """Test that provider failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await research_agent.research_agent(valid_state)


@pytest.mark.asyncio
async def test_research_agent_validation_failure(mock_ai_service, valid_state):
    """Test that structured validation failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIValidationError("Bad schema")
    
    with pytest.raises(AIValidationError):
        await research_agent.research_agent(valid_state)
