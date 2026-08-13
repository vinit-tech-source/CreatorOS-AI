"""
tests/test_hashtag_agent.py

Tests for the AI Hashtag Agent.
"""
from unittest.mock import AsyncMock
import pytest

from app.agents import hashtag_agent
from app.core.exceptions import AIProviderError
from app.schemas.ai.hashtag import HashtagOutput, HashtagItem


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the hashtag_agent module."""
    service = AsyncMock()
    hashtag_agent._ai_service_instance = service
    yield service
    hashtag_agent._ai_service_instance = None


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
            "restricted_terms": ["badterm"]
        },
        "seo": {},
        "research": [],
        "strategy": {},
        "trends": [],
        "workspace": {}
    }


@pytest.mark.asyncio
async def test_hashtag_agent_success(mock_ai_service, valid_state):
    """Test that valid content produces normalized hashtags."""
    expected_output = HashtagOutput(
        hashtags=[
            HashtagItem(hashtag="#AI", relevance_score=0.9, category="broad"),
            HashtagItem(hashtag="#TechTrends2026", relevance_score=0.8, category="niche")
        ],
        primary_hashtags=["AI", "TechTrends2026", " #Spaces "],
        niche_hashtags=["AI", "badterm", "invalid tag"],
        recommendations=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await hashtag_agent.hashtag_agent(valid_state)
    
    assert "hashtags" in result
    hashtags_out = result["hashtags"][0]
    
    # 1. AI is added with # (since output had "AI")
    # 2. TechTrends2026 added with #
    # 3. #Spaces is stripped to #Spaces
    # 4. Duplicate "AI" is removed
    # 5. "badterm" is filtered
    # 6. "invalid tag" is filtered
    # Limit for X is 3
    assert len(hashtags_out["primary_hashtags"]) <= 3
    assert "#AI" in hashtags_out["primary_hashtags"]
    assert "#TechTrends2026" in hashtags_out["primary_hashtags"]
    assert "#Spaces" in hashtags_out["primary_hashtags"]
    assert "#badterm" not in hashtags_out["primary_hashtags"]


@pytest.mark.asyncio
async def test_hashtag_agent_platform_limits(mock_ai_service, valid_state):
    """Test that platform hashtag recommendations are enforced."""
    valid_state["platform"] = "X"
    
    expected_output = HashtagOutput(
        hashtags=[],
        primary_hashtags=["tag1", "tag2", "tag3", "tag4", "tag5"],
        niche_hashtags=[],
        recommendations=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await hashtag_agent.hashtag_agent(valid_state)
    
    # X limit is 3
    hashtags_out = result["hashtags"][0]
    assert len(hashtags_out["primary_hashtags"]) == 3


@pytest.mark.asyncio
async def test_hashtag_agent_rejects_failed_fact_check(valid_state):
    """Fact check FAILED should raise an error to stop execution."""
    valid_state["fact_check"]["overall_status"] = "FAILED"

    with pytest.raises(ValueError, match="Fact check status 'FAILED' is not PASSED"):
        await hashtag_agent.hashtag_agent(valid_state)


@pytest.mark.asyncio
async def test_hashtag_agent_rejects_needs_review_fact_check(valid_state):
    """Fact check NEEDS_REVIEW should raise an error to stop execution."""
    valid_state["fact_check"]["overall_status"] = "NEEDS_REVIEW"

    with pytest.raises(ValueError, match="Fact check status 'NEEDS_REVIEW' is not PASSED"):
        await hashtag_agent.hashtag_agent(valid_state)


@pytest.mark.asyncio
async def test_hashtag_agent_missing_content(valid_state):
    valid_state["optimized_content"] = None
    valid_state["draft"] = None
    with pytest.raises(ValueError, match="Missing 'draft' or 'optimized_content'"):
        await hashtag_agent.hashtag_agent(valid_state)


@pytest.mark.asyncio
async def test_hashtag_agent_missing_platform(valid_state):
    valid_state["platform"] = ""
    with pytest.raises(ValueError, match="Missing 'platform'"):
        await hashtag_agent.hashtag_agent(valid_state)


@pytest.mark.asyncio
async def test_hashtag_agent_missing_fact_check(valid_state):
    valid_state["fact_check"] = None
    with pytest.raises(ValueError, match="Missing 'fact_check'"):
        await hashtag_agent.hashtag_agent(valid_state)


@pytest.mark.asyncio
async def test_hashtag_agent_provider_failure(mock_ai_service, valid_state):
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    
    with pytest.raises(AIProviderError):
        await hashtag_agent.hashtag_agent(valid_state)
