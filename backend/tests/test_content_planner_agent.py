"""
tests/test_content_planner_agent.py

Tests for the AI Content Planner Agent.
"""
from unittest.mock import AsyncMock
import uuid

import pytest

from app.agents import content_planner_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.content_plan import ContentPlanOutput, ContentSection
from app.services.context_service import ContextService
from app.models.workspace import Workspace
from app.models.project import Project


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the content_planner_agent module."""
    service = AsyncMock()
    content_planner_agent._ai_service_instance = service
    yield service
    content_planner_agent._ai_service_instance = None


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
    # The planner agent requires strategy, trends, and research to be present
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
    state["research"] = [
        {
            "summary": "AI continues to grow in 2026.",
            "key_facts": ["AI adoption is up 50%."],
            "sources": [],
            "uncertainties": [],
            "research_confidence": 0.9
        }
    ]
    return state


@pytest.mark.asyncio
async def test_content_planner_agent_success(mock_ai_service, valid_state):
    """Test that a valid input produces a valid ContentPlanOutput state update."""
    expected_output = ContentPlanOutput(
        title="The State of AI",
        content_goal="Educate",
        hook="AI is everywhere.",
        sections=[
            ContentSection(
                heading="Introduction",
                objective="Hook the reader",
                key_points=["AI is big"],
                estimated_length=100
            ),
            ContentSection(
                heading="Conclusion",
                objective="Wrap up",
                key_points=["Read more"],
                estimated_length=50
            )
        ],
        key_message="AI is growing.",
        call_to_action="Follow me",
        content_type="Thread",
        tone="Educational",
        platform="X",
        language="English",
        constraints=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await content_planner_agent.content_planner_agent(valid_state)
    
    assert "outline" in result
    
    outline_data = result["outline"]
    assert outline_data["title"] == "The State of AI"
    assert len(outline_data["sections"]) == 2
    assert outline_data["sections"][0]["heading"] == "Introduction"
    assert outline_data["hook"] == "AI is everywhere."
    
    # Verify the AI service was called with the correct schema
    mock_ai_service.generate_structured.assert_called_once()
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert call_kwargs["response_schema"] == ContentPlanOutput
    assert "System:" in call_kwargs["prompt"]
    assert "User:" in call_kwargs["prompt"]
    # Ensure all previous context is passed
    assert "Educate" in call_kwargs["prompt"]
    assert "AI is trending." in call_kwargs["prompt"]
    assert "AI adoption is up 50%." in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_content_planner_agent_missing_user_request(valid_state):
    """Test that missing user_request raises ValueError."""
    valid_state["user_request"] = ""
    with pytest.raises(ValueError, match="Missing 'user_request'"):
        await content_planner_agent.content_planner_agent(valid_state)


@pytest.mark.asyncio
async def test_content_planner_agent_missing_platform(valid_state):
    """Test that missing platform raises ValueError."""
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await content_planner_agent.content_planner_agent(valid_state)


@pytest.mark.asyncio
async def test_content_planner_agent_missing_strategy(valid_state):
    """Test that missing strategy raises ValueError."""
    valid_state["strategy"] = None
    with pytest.raises(ValueError, match="Missing 'strategy'"):
        await content_planner_agent.content_planner_agent(valid_state)


@pytest.mark.asyncio
async def test_content_planner_agent_missing_trends(valid_state):
    """Test that missing trends raises ValueError."""
    valid_state["trends"] = []
    with pytest.raises(ValueError, match="Missing 'trends'"):
        await content_planner_agent.content_planner_agent(valid_state)


@pytest.mark.asyncio
async def test_content_planner_agent_missing_research(valid_state):
    """Test that missing research raises ValueError."""
    valid_state["research"] = []
    with pytest.raises(ValueError, match="Missing 'research'"):
        await content_planner_agent.content_planner_agent(valid_state)


@pytest.mark.asyncio
async def test_content_planner_agent_provider_failure(mock_ai_service, valid_state):
    """Test that provider failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await content_planner_agent.content_planner_agent(valid_state)


@pytest.mark.asyncio
async def test_content_planner_agent_validation_failure(mock_ai_service, valid_state):
    """Test that structured validation failures are re-raised."""
    mock_ai_service.generate_structured.side_effect = AIValidationError("Bad schema")
    
    with pytest.raises(AIValidationError):
        await content_planner_agent.content_planner_agent(valid_state)
