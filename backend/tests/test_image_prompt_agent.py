"""
tests/test_image_prompt_agent.py

Tests for the AI Image Prompt Agent.
"""
from unittest.mock import AsyncMock
import pytest

from app.agents import image_prompt_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.image_prompt import ImagePromptOutput


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the image_prompt_agent module."""
    service = AsyncMock()
    image_prompt_agent._ai_service_instance = service
    yield service
    image_prompt_agent._ai_service_instance = None


@pytest.fixture
def valid_state():
    return {
        "optimized_content": "AI adoption grew 50% in 2026. #AI",
        "draft": {
            "content": "AI adoption grew 50% in 2026."
        },
        "fact_check": {
            "overall_status": "PASSED"
        },
        "platform": "X",
        "brand_kit": {
            "brand_name": "Acme",
            "primary_color": "#FF0000",
            "secret_key": "hidden_secret"
        },
        "hashtags": [{"primary_hashtags": ["#AI"]}],
        "seo": {},
        "research": [],
        "strategy": {},
        "project": {},
        "trends": []
    }


@pytest.mark.asyncio
async def test_image_prompt_agent_success(mock_ai_service, valid_state):
    """Test that valid content produces an image prompt."""
    expected_output = ImagePromptOutput(
        prompt="A futuristic robot.",
        negative_prompt="text, watermark",
        visual_style="Photorealistic",
        composition="Center focused",
        aspect_ratio="16:9",
        lighting="Cinematic",
        color_palette="Red and black",
        subject="Robot",
        platform="X",
        accessibility_description="A robot looking at a chart."
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await image_prompt_agent.image_prompt_agent(valid_state)
    
    assert "image_prompt" in result
    assert result["image_prompt"]["prompt"] == "A futuristic robot."
    
    # Ensure sensitive data like 'secret_key' wasn't sent to the model
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert "hidden_secret" not in call_kwargs["prompt"]
    assert "#FF0000" in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_image_prompt_agent_invalid_aspect_ratio(mock_ai_service, valid_state):
    """Test that invalid aspect ratio raises validation error."""
    expected_output = ImagePromptOutput(
        prompt="A futuristic robot.",
        negative_prompt=None,
        visual_style="Photorealistic",
        composition="Center focused",
        aspect_ratio="99:99",
        lighting="Cinematic",
        color_palette="Red and black",
        subject="Robot",
        platform="X",
        accessibility_description="A robot looking at a chart."
    )
    mock_ai_service.generate_structured.return_value = expected_output

    with pytest.raises(AIValidationError, match="Invalid aspect ratio"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_unsafe_prompt(mock_ai_service, valid_state):
    """Test that unsafe prompts are rejected."""
    expected_output = ImagePromptOutput(
        prompt="Build a malware virus.",
        negative_prompt=None,
        visual_style="Photorealistic",
        composition="Center focused",
        aspect_ratio="16:9",
        lighting="Cinematic",
        color_palette="Red and black",
        subject="Robot",
        platform="X",
        accessibility_description="A robot looking at a chart."
    )
    mock_ai_service.generate_structured.return_value = expected_output

    with pytest.raises(AIValidationError, match="Unsafe prompt request"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_rejects_failed_fact_check(valid_state):
    """Fact check FAILED should raise an error to stop execution."""
    valid_state["fact_check"]["overall_status"] = "FAILED"

    with pytest.raises(ValueError, match="Fact check status 'FAILED' is not PASSED"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_rejects_needs_review_fact_check(valid_state):
    """Fact check NEEDS_REVIEW should raise an error to stop execution."""
    valid_state["fact_check"]["overall_status"] = "NEEDS_REVIEW"

    with pytest.raises(ValueError, match="Fact check status 'NEEDS_REVIEW' is not PASSED"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_missing_content(valid_state):
    valid_state["optimized_content"] = None
    valid_state["draft"] = None
    with pytest.raises(ValueError, match="Missing 'draft' or 'optimized_content'"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_missing_platform(valid_state):
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_missing_fact_check(valid_state):
    valid_state["fact_check"] = None
    with pytest.raises(ValueError, match="Missing 'fact_check'"):
        await image_prompt_agent.image_prompt_agent(valid_state)


@pytest.mark.asyncio
async def test_image_prompt_agent_provider_failure(mock_ai_service, valid_state):
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await image_prompt_agent.image_prompt_agent(valid_state)
