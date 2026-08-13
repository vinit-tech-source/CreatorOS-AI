"""
tests/test_trend_agent.py

Tests for the AI Trend Agent.
"""
from unittest.mock import AsyncMock
import uuid

import pytest

from app.agents import trend_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.trend import TrendOutput, TrendItem
from app.services.context_service import ContextService
from app.models.workspace import Workspace
from app.models.project import Project


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the trend_agent module."""
    service = AsyncMock()
    trend_agent._ai_service_instance = service
    yield service
    trend_agent._ai_service_instance = None


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
    # The trend agent requires strategy to be present
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
    return state


@pytest.mark.asyncio
async def test_trend_agent_success(mock_ai_service, valid_state):
    """Test that a valid input produces a valid TrendOutput state update."""
    expected_output = TrendOutput(
        trends=[
            TrendItem(
                topic="AI in 2026",
                relevance_score=0.9,
                platform_relevance=0.8,
                reason="High engagement on X"
            )
        ],
        recommended_hashtags=["#AI", "#TechTrends"],
        trend_summary="AI remains a strong topic."
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await trend_agent.trend_agent(valid_state)
    
    assert "trends" in result
    assert len(result["trends"]) == 1
    
    trend_data = result["trends"][0]
    assert len(trend_data["trends"]) == 1
    assert trend_data["trends"][0]["topic"] == "AI in 2026"
    assert trend_data["recommended_hashtags"] == ["#AI", "#TechTrends"]
    
    # Verify the AI service was called with the correct schema
    mock_ai_service.generate_structured.assert_called_once()
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert call_kwargs["response_schema"] == TrendOutput
    assert "System:" in call_kwargs["prompt"]
    assert "User:" in call_kwargs["prompt"]
    # Ensure strategy is included in the prompt
    assert "Educate" in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_trend_agent_missing_user_request(valid_state):
    """Test that missing user_request raises ValueError."""
    valid_state["user_request"] = ""
    with pytest.raises(ValueError, match="Missing 'user_request'"):
        await trend_agent.trend_agent(valid_state)


@pytest.mark.asyncio
async def test_trend_agent_missing_platform(valid_state):
    """Test that missing platform raises ValueError."""
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await trend_agent.trend_agent(valid_state)


@pytest.mark.asyncio
async def test_trend_agent_missing_strategy(valid_state):
    """Test that missing strategy raises ValueError."""
    valid_state["strategy"] = None
    with pytest.raises(ValueError, match="Missing 'strategy'"):
        await trend_agent.trend_agent(valid_state)


@pytest.mark.asyncio
async def test_trend_agent_provider_failure(mock_ai_service, valid_state):
    """Test that provider failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await trend_agent.trend_agent(valid_state)


@pytest.mark.asyncio
async def test_trend_agent_validation_failure(mock_ai_service, valid_state):
    """Test that structured validation failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIValidationError("Bad schema")
    
    with pytest.raises(AIValidationError):
        await trend_agent.trend_agent(valid_state)
