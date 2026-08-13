"""
tests/test_brand_voice_agent.py

Tests for the AI Brand Voice Agent.
"""
from unittest.mock import AsyncMock
import uuid

import pytest

from app.agents import brand_voice_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.brand_voice import BrandVoiceOutput, BrandVoiceIssue, IssueSeverity
from app.services.context_service import ContextService
from app.models.workspace import Workspace
from app.models.project import Project


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the brand_voice_agent module."""
    service = AsyncMock()
    brand_voice_agent._ai_service_instance = service
    yield service
    brand_voice_agent._ai_service_instance = None


@pytest.fixture
def valid_state():
    workspace = Workspace()
    workspace.id = uuid.uuid4()
    workspace.name = "Test Workspace"
    
    project = Project()
    project.id = uuid.uuid4()
    project.name = "Test Project"
    
    from app.models.brand_kit import BrandKit
    brand_kit = BrandKit()
    brand_kit.id = uuid.uuid4()
    brand_kit.brand_name = "Acme Corp"
    brand_kit.default_tone = "Professional"
    brand_kit.target_audience = "B2B"
    brand_kit.brand_values = ["Integrity", "Innovation"]
    brand_kit.preferred_language = "English"
    brand_kit.primary_color = "#000000"
    brand_kit.secondary_color = "#FFFFFF"
    brand_kit.accent_color = "#FF0000"
    brand_kit.website_url = "https://acme.com"
    brand_kit.description = "A great company"
    
    state = ContextService.assemble_initial_state(
        workspace=workspace,
        project=project,
        brand_kit=brand_kit,
        user_request="Write a thread about AI",
        platform="X"
    )
    
    state["strategy"] = {
        "content_goal": "Educate",
        "target_audience": "Developers"
    }
    
    state["draft"] = {
        "title": "The State of AI",
        "content": "AI is dope.",
        "content_type": "Post",
        "platform": "X",
        "language": "English",
        "hashtags": ["#AI"],
        "character_count": 11,
        "word_count": 3
    }
    return state


@pytest.mark.asyncio
async def test_brand_voice_agent_success_compliant(mock_ai_service, valid_state):
    """Test that compliant content is unchanged."""
    expected_output = BrandVoiceOutput(
        compliant=True,
        brand_score=1.0,
        revised_content="AI is dope.",
        issues=[],
        changes=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await brand_voice_agent.brand_voice_agent(valid_state)
    
    assert "brand_voice" in result
    assert "optimized_content" in result
    
    assert result["optimized_content"] == "AI is dope."
    assert result["brand_voice"]["compliant"] is True
    assert result["brand_voice"]["brand_score"] == 1.0


@pytest.mark.asyncio
async def test_brand_voice_agent_success_revised(mock_ai_service, valid_state):
    """Test that violating content is revised."""
    expected_output = BrandVoiceOutput(
        compliant=False,
        brand_score=0.5,
        revised_content="AI is excellent.",
        issues=[
            BrandVoiceIssue(
                category="Tone",
                description="Word 'dope' is too informal for Professional tone.",
                severity=IssueSeverity.MEDIUM
            )
        ],
        changes=["Replaced 'dope' with 'excellent'."]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await brand_voice_agent.brand_voice_agent(valid_state)
    
    assert result["optimized_content"] == "AI is excellent."
    assert result["brand_voice"]["compliant"] is False
    assert result["brand_voice"]["brand_score"] == 0.5
    assert len(result["brand_voice"]["issues"]) == 1
    assert result["brand_voice"]["issues"][0]["severity"] == "MEDIUM"


@pytest.mark.asyncio
async def test_brand_voice_agent_x_character_limit_exceeded(mock_ai_service, valid_state):
    """Test that a revised X post exceeding 280 characters raises an error."""
    valid_state["platform"] = "X"
    valid_state["draft"]["content_type"] = "Post"
    
    expected_output = BrandVoiceOutput(
        compliant=False,
        brand_score=0.8,
        revised_content="A" * 281,
        issues=[],
        changes=["Made it way too long."]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    with pytest.raises(AIValidationError, match="exceeds 280 characters"):
        await brand_voice_agent.brand_voice_agent(valid_state)


@pytest.mark.asyncio
async def test_brand_voice_agent_missing_draft(valid_state):
    valid_state["draft"] = None
    with pytest.raises(ValueError, match="Missing 'draft'"):
        await brand_voice_agent.brand_voice_agent(valid_state)


@pytest.mark.asyncio
async def test_brand_voice_agent_missing_platform(valid_state):
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await brand_voice_agent.brand_voice_agent(valid_state)


@pytest.mark.asyncio
async def test_brand_voice_agent_missing_brand_kit(valid_state):
    valid_state["brand_kit"] = None
    with pytest.raises(ValueError, match="Missing 'brand_kit'"):
        await brand_voice_agent.brand_voice_agent(valid_state)


@pytest.mark.asyncio
async def test_brand_voice_agent_provider_failure(mock_ai_service, valid_state):
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await brand_voice_agent.brand_voice_agent(valid_state)
