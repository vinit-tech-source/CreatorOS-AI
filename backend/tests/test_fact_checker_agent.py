"""
tests/test_fact_checker_agent.py

Tests for the AI Fact Checker Agent.
"""
from unittest.mock import AsyncMock
import pytest

from app.agents import fact_checker_agent
from app.core.exceptions import AIProviderError
from app.schemas.ai.fact_check import FactCheckOutput, FactCheckIssue, IssueStatus, OverallStatus


@pytest.fixture
def mock_ai_service():
    """Mock the global AI service instance in the fact_checker_agent module."""
    service = AsyncMock()
    fact_checker_agent._ai_service_instance = service
    yield service
    fact_checker_agent._ai_service_instance = None


@pytest.fixture
def valid_state():
    return {
        "optimized_content": "AI adoption grew 50% in 2026.",
        "draft": {
            "content": "AI adoption grew 50% in 2026."
        },
        "research": [
            {
                "summary": "AI is growing.",
                "key_facts": ["AI adoption grew 50% in 2026."]
            }
        ],
        "strategy": {},
        "trends": [],
        "brand_voice": {}
    }


@pytest.mark.asyncio
async def test_fact_checker_agent_success_passed(mock_ai_service, valid_state):
    """Test that a compliant draft passes fact check."""
    expected_output = FactCheckOutput(
        overall_status=OverallStatus.PASSED,
        confidence=0.9,
        issues=[],
        verified_claims=["AI adoption grew 50% in 2026."],
        unsupported_claims=[],
        recommendations=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await fact_checker_agent.fact_checker_agent(valid_state)
    
    assert "fact_check" in result
    assert result["fact_check"]["overall_status"] == "PASSED"
    assert result["fact_check"]["confidence"] == 0.9


@pytest.mark.asyncio
async def test_fact_checker_agent_success_failed(mock_ai_service, valid_state):
    """Test that an unsupported draft fails fact check."""
    expected_output = FactCheckOutput(
        overall_status=OverallStatus.FAILED,
        confidence=0.9,
        issues=[
            FactCheckIssue(
                claim="AI adoption grew 99% in 2026.",
                status=IssueStatus.CONTRADICTED,
                explanation="Research says 50%, not 99%.",
                evidence="Research summary: AI adoption grew 50%",
                confidence=0.9
            )
        ],
        verified_claims=[],
        unsupported_claims=["AI adoption grew 99% in 2026."],
        recommendations=["Correct the adoption percentage."]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await fact_checker_agent.fact_checker_agent(valid_state)
    
    assert result["fact_check"]["overall_status"] == "FAILED"
    assert len(result["fact_check"]["issues"]) == 1


@pytest.mark.asyncio
async def test_fact_checker_agent_fallback_to_draft(mock_ai_service, valid_state):
    """Test that it falls back to draft if optimized_content is None."""
    valid_state["optimized_content"] = None
    expected_output = FactCheckOutput(
        overall_status=OverallStatus.PASSED,
        confidence=0.9,
        issues=[],
        verified_claims=[],
        unsupported_claims=[],
        recommendations=[]
    )
    mock_ai_service.generate_structured.return_value = expected_output

    result = await fact_checker_agent.fact_checker_agent(valid_state)
    assert result["fact_check"]["overall_status"] == "PASSED"
    
    # Verify the prompt used the draft content
    call_kwargs = mock_ai_service.generate_structured.call_args.kwargs
    assert "AI adoption grew 50%" in call_kwargs["prompt"]


@pytest.mark.asyncio
async def test_fact_checker_agent_missing_content(valid_state):
    valid_state["optimized_content"] = None
    valid_state["draft"] = None
    with pytest.raises(ValueError, match="Missing 'draft' or 'optimized_content'"):
        await fact_checker_agent.fact_checker_agent(valid_state)


@pytest.mark.asyncio
async def test_fact_checker_agent_missing_research(valid_state):
    valid_state["research"] = []
    with pytest.raises(ValueError, match="Missing 'research'"):
        await fact_checker_agent.fact_checker_agent(valid_state)


@pytest.mark.asyncio
async def test_fact_checker_agent_provider_failure(mock_ai_service, valid_state):
    mock_ai_service.generate_structured.side_effect = AIProviderError("API down")
    with pytest.raises(AIProviderError):
        await fact_checker_agent.fact_checker_agent(valid_state)
