"""
tests/test_content_generator_agent.py

Tests for the AI Content Generator Agent.
"""
from unittest.mock import AsyncMock
import uuid

import pytest

from app.agents import content_generator_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.generated_content import GeneratedContentOutput
from app.services.context_service import ContextService
from app.models.workspace import Workspace
from app.models.project import Project


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the content_generator_agent module."""
    service = AsyncMock()
    content_generator_agent._ai_service_instance = service
    yield service
    content_generator_agent._ai_service_instance = None


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
    # The generator agent requires strategy, trends, research, and outline to be present
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
    state["outline"] = {
        "title": "The State of AI",
        "content_goal": "Educate",
        "hook": "AI is everywhere.",
        "sections": [
            {
                "heading": "Introduction",
                "objective": "Hook the reader",
                "key_points": ["AI is big"],
                "estimated_length": 100
            }
        ],
        "key_message": "AI is growing.",
        "call_to_action": "Follow me",
        "content_type": "Thread",
        "tone": "Educational",
        "platform": "X",
        "language": "English",
        "constraints": []
    }
    return state


@pytest.mark.asyncio
async def test_content_generator_agent_success(mock_ai_service, valid_state):
    """Test that a valid input produces a valid GeneratedContentOutput state update."""
    expected_output = GeneratedContentOutput(
        title="The State of AI",
        content="AI is everywhere. Adoption is up 50% in 2026. Follow me for more.",
        content_type="Thread",
        platform="X",
        language="English",
        hashtags=["#AI", "#Tech"],
        call_to_action="Follow me for more.",
        character_count=999,  # Intentionally wrong to test Python recalculation
        word_count=999
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await content_generator_agent.content_generator_agent(valid_state)
    
    assert "draft" in result
    
    draft_data = result["draft"]
    assert draft_data["title"] == "The State of AI"
    assert "Adoption is up 50% in 2026." in draft_data["content"]
    
    # Assert counts were recalculated deterministically in Python
    expected_content = "AI is everywhere. Adoption is up 50% in 2026. Follow me for more."
    assert draft_data["character_count"] == len(expected_content)
    assert draft_data["word_count"] == len(expected_content.split())
    
    # Verify the AI service was called with the correct schema
    mock_ai_service.generate_structured.assert_called_once()
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert call_kwargs["response_schema"] == GeneratedContentOutput
    assert "System:" in call_kwargs["prompt"]
    assert "User:" in call_kwargs["prompt"]
    # Ensure all previous context is passed
    assert "Educate" in call_kwargs["prompt"]
    assert "AI is trending." in call_kwargs["prompt"]
    assert "AI adoption is up 50%." in call_kwargs["prompt"]
    assert "Hook the reader" in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_content_generator_agent_x_character_limit_success(mock_ai_service, valid_state):
    """Test that an X post within limits succeeds."""
    valid_state["platform"] = "X"
    expected_output = GeneratedContentOutput(
        title=None,
        content="Short tweet.",
        content_type="Post",
        platform="X",
        language="English",
        hashtags=[],
        call_to_action=None,
        character_count=0,
        word_count=0
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await content_generator_agent.content_generator_agent(valid_state)
    assert result["draft"]["character_count"] == 12


@pytest.mark.asyncio
async def test_content_generator_agent_x_character_limit_exceeded(mock_ai_service, valid_state):
    """Test that an X post exceeding 280 characters raises an error."""
    valid_state["platform"] = "X"
    expected_output = GeneratedContentOutput(
        title=None,
        content="A" * 281,
        content_type="Post",
        platform="X",
        language="English",
        hashtags=[],
        call_to_action=None,
        character_count=0,
        word_count=0
    )
    mock_ai_service.generate_structured.return_value = expected_output

    with pytest.raises(AIValidationError, match="exceeds 280 characters"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_x_thread_ignores_limit(mock_ai_service, valid_state):
    """Test that an X Thread exceeding 280 characters succeeds (it is multiple posts)."""
    valid_state["platform"] = "X"
    expected_output = GeneratedContentOutput(
        title=None,
        content="A" * 500,
        content_type="Thread",
        platform="X",
        language="English",
        hashtags=[],
        call_to_action=None,
        character_count=0,
        word_count=0
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await content_generator_agent.content_generator_agent(valid_state)
    assert result["draft"]["character_count"] == 500


@pytest.mark.asyncio
async def test_content_generator_agent_missing_user_request(valid_state):
    valid_state["user_request"] = ""
    with pytest.raises(ValueError, match="Missing 'user_request'"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_missing_platform(valid_state):
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_missing_strategy(valid_state):
    valid_state["strategy"] = None
    with pytest.raises(ValueError, match="Missing 'strategy'"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_missing_trends(valid_state):
    valid_state["trends"] = []
    with pytest.raises(ValueError, match="Missing 'trends'"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_missing_research(valid_state):
    valid_state["research"] = []
    with pytest.raises(ValueError, match="Missing 'research'"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_missing_outline(valid_state):
    valid_state["outline"] = None
    with pytest.raises(ValueError, match="Missing 'outline'"):
        await content_generator_agent.content_generator_agent(valid_state)


@pytest.mark.asyncio
async def test_content_generator_agent_provider_failure(mock_ai_service, valid_state):
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await content_generator_agent.content_generator_agent(valid_state)
