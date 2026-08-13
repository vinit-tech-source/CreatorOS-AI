"""
tests/test_workflow.py

Tests for the AI workflow foundation.
"""
import uuid
import pytest

from app.models.brand_kit import BrandKit
from app.models.project import Project
from app.models.workspace import Workspace
from app.prompts.base import PromptDefinition
from app.services.context_service import ContextService
from app.workflows.content_workflow import build_content_workflow


def test_prompt_definition_creation():
    """Test that a prompt definition can be created and formatted."""
    prompt = PromptDefinition(
        prompt_id="test_prompt",
        version="1.0.0",
        model="gemini",
        status="draft",
        system_instructions="You are a helpful assistant.",
        user_instructions="Write a story about {topic}.",
    )
    
    formatted = prompt.build_user_prompt(topic="space")
    assert formatted == "Write a story about space."


def test_context_builder_excludes_sensitive_data():
    """Test that the context builder produces safe dictionaries."""
    workspace = Workspace()
    workspace.id = uuid.uuid4()
    workspace.name = "Test Workspace"
    workspace.description = "A workspace"
    workspace.timezone = "UTC"
    workspace.owner_id = uuid.uuid4() # Should not be in output
    
    project = Project()
    project.id = uuid.uuid4()
    project.name = "Test Project"
    project.description = "A project"
    project.objective = "Objective"
    project.target_audience = "Audience"
    project.workspace_id = workspace.id # Should not be in output
    
    brand_kit = BrandKit()
    brand_kit.brand_name = "Test Brand"
    brand_kit.description = "A brand"
    brand_kit.target_audience = "Everyone"
    brand_kit.brand_values = "Honesty"
    brand_kit.default_tone = "Professional"
    brand_kit.preferred_language = "English"
    brand_kit.id = uuid.uuid4() # Should not be in output

    initial_state = ContextService.assemble_initial_state(
        workspace=workspace,
        project=project,
        brand_kit=brand_kit,
        user_request="Do something",
        platform="Twitter",
    )
    
    assert "owner_id" not in initial_state["workspace"]
    assert initial_state["workspace"]["name"] == "Test Workspace"
    
    assert "workspace_id" not in initial_state["project"]
    assert initial_state["project"]["name"] == "Test Project"
    
    assert "id" not in initial_state["brand_kit"]
    assert initial_state["brand_kit"]["brand_name"] == "Test Brand"
    
    assert initial_state["user_request"] == "Do something"
    assert initial_state["platform"] == "Twitter"


def test_langgraph_workflow_compiles():
    """Test that the placeholder LangGraph workflow compiles."""
    graph = build_content_workflow()
    assert graph is not None


@pytest.mark.asyncio
async def test_langgraph_workflow_execution(monkeypatch):
    """Test that the strategy node executes and modifies state."""
    from unittest.mock import AsyncMock
    from app.agents import strategy_agent, trend_agent, research_agent, content_planner_agent, content_generator_agent, brand_voice_agent, fact_checker_agent, seo_agent
    from app.schemas.ai.strategy import StrategyOutput
    from app.schemas.ai.trend import TrendOutput, TrendItem
    from app.schemas.ai.research import ResearchOutput, ResearchSource
    from app.schemas.ai.content_plan import ContentPlanOutput, ContentSection
    from app.schemas.ai.generated_content import GeneratedContentOutput
    from app.schemas.ai.brand_voice import BrandVoiceOutput, BrandVoiceIssue, IssueSeverity
    from app.schemas.ai.fact_check import FactCheckOutput, OverallStatus
    from app.schemas.ai.seo import SEOOutput

    mock_strategy_service = AsyncMock()
    mock_strategy_service.generate_structured.return_value = StrategyOutput(
        content_goal="Educate",
        target_audience="Developers",
        platform_strategy="Threads",
        content_type="Thread",
        tone="Educational",
        language="English",
        call_to_action="Read more",
        constraints=[]
    )
    monkeypatch.setattr(strategy_agent, "_ai_service_instance", mock_strategy_service)

    mock_trend_service = AsyncMock()
    mock_trend_service.generate_structured.return_value = TrendOutput(
        trends=[
            TrendItem(topic="AI", relevance_score=0.9, platform_relevance=0.9, reason="Trending")
        ],
        recommended_hashtags=["#AI"],
        trend_summary="Summary"
    )
    monkeypatch.setattr(trend_agent, "_ai_service_instance", mock_trend_service)
    
    mock_research_service = AsyncMock()
    mock_research_service.generate_structured.return_value = ResearchOutput(
        summary="AI is growing.",
        key_facts=["Fact 1"],
        sources=[],
        uncertainties=[],
        research_confidence=0.9
    )
    monkeypatch.setattr(research_agent, "_ai_service_instance", mock_research_service)

    mock_planner_service = AsyncMock()
    mock_planner_service.generate_structured.return_value = ContentPlanOutput(
        title="Test Title",
        content_goal="Educate",
        hook="Hook",
        sections=[
            ContentSection(heading="A", objective="A", key_points=["A"], estimated_length=10),
            ContentSection(heading="B", objective="B", key_points=["B"], estimated_length=10)
        ],
        key_message="Message",
        call_to_action="CTA",
        content_type="Thread",
        tone="Tone",
        platform="X",
        language="En",
        constraints=[]
    )
    monkeypatch.setattr(content_planner_agent, "_ai_service_instance", mock_planner_service)
    
    mock_generator_service = AsyncMock()
    mock_generator_service.generate_structured.return_value = GeneratedContentOutput(
        title="Test Title",
        content="Generated post content.",
        content_type="Post",
        platform="X",
        language="En",
        hashtags=["#Test"],
        call_to_action=None,
        character_count=0,
        word_count=0
    )
    monkeypatch.setattr(content_generator_agent, "_ai_service_instance", mock_generator_service)

    mock_brand_voice_service = AsyncMock()
    mock_brand_voice_service.generate_structured.return_value = BrandVoiceOutput(
        compliant=False,
        brand_score=0.9,
        revised_content="Optimized post content.",
        issues=[],
        changes=["Optimized it."]
    )
    monkeypatch.setattr(brand_voice_agent, "_ai_service_instance", mock_brand_voice_service)
    
    mock_fact_checker_service = AsyncMock()
    mock_fact_checker_service.generate_structured.return_value = FactCheckOutput(
        overall_status=OverallStatus.PASSED,
        confidence=0.9,
        issues=[],
        verified_claims=["Fact 1"],
        unsupported_claims=[],
        recommendations=[]
    )
    monkeypatch.setattr(fact_checker_agent, "_ai_service_instance", mock_fact_checker_service)
    
    mock_seo_service = AsyncMock()
    mock_seo_service.generate_structured.return_value = SEOOutput(
        optimized_content="Fully optimized post content.",
        seo_score=0.95,
        primary_keywords=["AI"],
        secondary_keywords=[],
        recommendations=[],
        changes=[]
    )
    monkeypatch.setattr(seo_agent, "_ai_service_instance", mock_seo_service)

    graph = build_content_workflow()
    
    workspace = Workspace()
    workspace.id = uuid.uuid4()
    workspace.name = "W"
    
    project = Project()
    project.id = uuid.uuid4()
    project.name = "P"
    
    from app.models.brand_kit import BrandKit
    brand_kit = BrandKit()
    brand_kit.id = uuid.uuid4()
    brand_kit.brand_name = "Acme Corp"
    brand_kit.default_tone = "Professional"
    brand_kit.target_audience = "B2B"
    brand_kit.brand_values = ["Integrity"]
    brand_kit.preferred_language = "English"

    initial_state = ContextService.assemble_initial_state(
        workspace=workspace,
        project=project,
        brand_kit=brand_kit,
        user_request="Test",
        platform="X"
    )
    
    final_state = await graph.ainvoke(initial_state)
    
    assert "strategy" in final_state
    assert final_state["strategy"]["content_goal"] == "Educate"
    
    assert "trends" in final_state
    assert len(final_state["trends"]) == 1
    assert final_state["trends"][0]["trend_summary"] == "Summary"
    
    assert "research" in final_state
    assert len(final_state["research"]) == 1
    assert final_state["research"][0]["summary"] == "AI is growing."
    
    assert "outline" in final_state
    assert final_state["outline"]["title"] == "Test Title"
    
    assert "draft" in final_state
    assert final_state["draft"]["content"] == "Generated post content."
    assert final_state["draft"]["character_count"] == 23
    assert final_state["draft"]["word_count"] == 3
    
    assert "optimized_content" in final_state
    assert final_state["optimized_content"] == "Fully optimized post content."
    assert "brand_voice" in final_state
    assert final_state["brand_voice"]["brand_score"] == 0.9
    
    assert "fact_check" in final_state
    assert final_state["fact_check"]["overall_status"] == "PASSED"
    assert final_state["fact_check"]["confidence"] == 0.9
    
    assert "seo" in final_state
    assert final_state["seo"]["seo_score"] == 0.95
    
    assert final_state["user_request"] == "Test"
