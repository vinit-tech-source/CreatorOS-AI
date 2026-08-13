"""
tests/test_strategy_agent.py

Tests for the AI Strategy Agent.
"""
from unittest.mock import AsyncMock
import uuid

import pytest

from app.agents import strategy_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.strategy import StrategyOutput
from app.services.context_service import ContextService
from app.models.workspace import Workspace
from app.models.project import Project


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the strategy_agent module."""
    service = AsyncMock()
    strategy_agent._ai_service_instance = service
    yield service
    strategy_agent._ai_service_instance = None


@pytest.fixture
def valid_state():
    workspace = Workspace()
    workspace.id = uuid.uuid4()
    workspace.name = "Test Workspace"
    
    project = Project()
    project.id = uuid.uuid4()
    project.name = "Test Project"
    
    return ContextService.assemble_initial_state(
        workspace=workspace,
        project=project,
        brand_kit=None,
        user_request="Write a thread about AI",
        platform="X"
    )


@pytest.mark.asyncio
async def test_strategy_agent_success(mock_ai_service, valid_state):
    """Test that a valid input produces a valid StrategyOutput state update."""
    expected_output = StrategyOutput(
        content_goal="Educate",
        target_audience="Developers",
        platform_strategy="Threads",
        content_type="Thread",
        tone="Educational",
        language="English",
        call_to_action="Read more",
        constraints=["Max 280 chars per tweet"]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await strategy_agent.strategy_agent(valid_state)
    
    assert "strategy" in result
    assert result["strategy"]["content_goal"] == "Educate"
    
    # Verify the AI service was called with the correct schema
    mock_ai_service.generate_structured.assert_called_once()
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert call_kwargs["response_schema"] == StrategyOutput
    assert "System:" in call_kwargs["prompt"]
    assert "User:" in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_strategy_agent_missing_user_request(valid_state):
    """Test that missing user_request raises ValueError."""
    valid_state["user_request"] = ""
    with pytest.raises(ValueError, match="Missing 'user_request'"):
        await strategy_agent.strategy_agent(valid_state)


@pytest.mark.asyncio
async def test_strategy_agent_missing_platform(valid_state):
    """Test that missing platform raises ValueError."""
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await strategy_agent.strategy_agent(valid_state)


@pytest.mark.asyncio
async def test_strategy_agent_provider_failure(mock_ai_service, valid_state):
    """Test that provider failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await strategy_agent.strategy_agent(valid_state)


@pytest.mark.asyncio
async def test_strategy_agent_validation_failure(mock_ai_service, valid_state):
    """Test that structured validation failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIValidationError("Bad schema")
    
    with pytest.raises(AIValidationError):
        await strategy_agent.strategy_agent(valid_state)
