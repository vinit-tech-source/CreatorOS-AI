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
async def test_langgraph_workflow_execution():
    """Test that the placeholder node executes and modifies state."""
    graph = build_content_workflow()
    
    workspace = Workspace()
    workspace.id = uuid.uuid4()
    workspace.name = "W"
    
    project = Project()
    project.id = uuid.uuid4()
    project.name = "P"
    
    initial_state = ContextService.assemble_initial_state(
        workspace=workspace,
        project=project,
        brand_kit=None,
        user_request="Test",
        platform="X"
    )
    
    final_state = await graph.ainvoke(initial_state)
    
    assert final_state["metadata"]["processed_by"] == "placeholder_node"
    assert final_state["user_request"] == "Test"
