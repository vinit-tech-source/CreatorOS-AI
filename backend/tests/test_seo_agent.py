"""
tests/test_seo_agent.py

Tests for the AI SEO Agent.
"""
from unittest.mock import AsyncMock
import pytest

from app.agents import seo_agent
from app.core.exceptions import AIProviderError, AIValidationError
from app.schemas.ai.seo import SEOOutput


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the seo_agent module."""
    service = AsyncMock()
    seo_agent._ai_service_instance = service
    yield service
    seo_agent._ai_service_instance = None


@pytest.fixture
def valid_state():
    return {
        "optimized_content": "AI adoption grew 50% in 2026.",
        "draft": {
            "content": "AI adoption grew 50% in 2026.",
            "content_type": "Post"
        },
        "fact_check": {
            "overall_status": "PASSED"
        },
        "platform": "X",
        "research": [],
        "strategy": {},
        "trends": []
    }


@pytest.mark.asyncio
async def test_seo_agent_success(mock_ai_service, valid_state):
    """Test that a compliant draft is optimized successfully."""
    expected_output = SEOOutput(
        optimized_content="AI adoption skyrocketed 50% in 2026! 🚀 #AI",
        seo_score=0.9,
        primary_keywords=["AI adoption"],
        secondary_keywords=["2026 tech trends"],
        recommendations=["Add an image."],
        changes=["Added hashtag."]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await seo_agent.seo_agent(valid_state)
    
    assert "seo" in result
    assert result["optimized_content"] == expected_output.optimized_content
    assert result["seo"]["seo_score"] == 0.9


@pytest.mark.asyncio
async def test_seo_agent_bypasses_on_failed_fact_check(mock_ai_service, valid_state):
    """Test that it does not optimize if fact check FAILED."""
    valid_state["fact_check"]["overall_status"] = "FAILED"

    result = await seo_agent.seo_agent(valid_state)
    
    assert "seo" in result
    assert result["seo"]["seo_score"] == 0.0
    assert result["seo"]["optimized_content"] == "AI adoption grew 50% in 2026."
    assert "Skipped optimization" in result["seo"]["changes"][0]
    
    # Verify AI provider was NOT called
    mock_ai_service.generate_structured.assert_not_called()


@pytest.mark.asyncio
async def test_seo_agent_x_character_limit_exceeded(mock_ai_service, valid_state):
    """Test that a revised X post exceeding 280 characters raises an error."""
    expected_output = SEOOutput(
        optimized_content="A" * 281,
        seo_score=0.9,
        primary_keywords=[],
        secondary_keywords=[],
        recommendations=[],
        changes=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    with pytest.raises(AIValidationError, match="exceeds 280 characters"):
        await seo_agent.seo_agent(valid_state)


@pytest.mark.asyncio
async def test_seo_agent_missing_content(valid_state):
    valid_state["optimized_content"] = None
    valid_state["draft"] = None
    with pytest.raises(ValueError, match="Missing 'draft' or 'optimized_content'"):
        await seo_agent.seo_agent(valid_state)


@pytest.mark.asyncio
async def test_seo_agent_missing_platform(valid_state):
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await seo_agent.seo_agent(valid_state)


@pytest.mark.asyncio
async def test_seo_agent_missing_fact_check(valid_state):
    valid_state["fact_check"] = None
    with pytest.raises(ValueError, match="Missing 'fact_check'"):
        await seo_agent.seo_agent(valid_state)


@pytest.mark.asyncio
async def test_seo_agent_provider_failure(mock_ai_service, valid_state):
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await seo_agent.seo_agent(valid_state)
