"""
tests/api/test_content.py

Unit tests for ContentGenerationService.
"""
import uuid
import pytest
from unittest.mock import AsyncMock

from app.models.project import Project, ProjectStatus
from app.models.workspace import Workspace
from app.schemas.content import ContentGenerateRequest
from app.services.content_generation_service import ContentGenerationService
from app.core.exceptions import ProjectNotFoundError, PermissionDeniedError


def make_workspace(owner_id: uuid.UUID) -> Workspace:
    ws = Workspace()
    ws.id = uuid.uuid4()
    ws.name = "Test Workspace"
    ws.slug = "test-ws"
    ws.owner_id = owner_id
    return ws


def make_project(workspace_id: uuid.UUID) -> Project:
    proj = Project()
    proj.id = uuid.uuid4()
    proj.workspace_id = workspace_id
    proj.name = "Test Project"
    proj.slug = "test-project"
    proj.description = None
    proj.status = ProjectStatus.DRAFT
    proj.objective = None
    proj.target_audience = None
    return proj


def make_repos(workspace, project):
    ws_repo = AsyncMock()
    ws_repo.get_by_id = AsyncMock(return_value=workspace)

    proj_repo = AsyncMock()
    proj_repo.get_by_id = AsyncMock(return_value=project)

    bk_repo = AsyncMock()
    bk_repo.get_by_workspace = AsyncMock(return_value=None)
    
    workflow = AsyncMock()
    workflow.ainvoke = AsyncMock(return_value={
        "draft": {"title": "Draft for X", "content": "Hello AI"},
        "optimized_content": "Hello AI Optimized",
        "hashtags": ["AI", "Tech"],
    })

    return ws_repo, proj_repo, bk_repo, workflow


@pytest.mark.asyncio
async def test_generate_content_success():
    """Test successful AI content generation."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    ws_repo, proj_repo, bk_repo, workflow = make_repos(workspace, project)
    service = ContentGenerationService(ws_repo, proj_repo, bk_repo, workflow)

    request = ContentGenerateRequest(
        workspace_id=workspace.id,
        project_id=project.id,
        platform="X",
        content_type="Standard Post",
        user_request="Tell me about AI",
    )

    response = await service.generate_content(request, owner_id)

    assert response.platform == "X"
    assert response.content == "Hello AI Optimized"
    assert response.title == "Draft for X"
    assert len(response.hashtags) == 2


@pytest.mark.asyncio
async def test_generate_content_unauthorized_workspace():
    """Test 403 when user does not own workspace."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    ws_repo, proj_repo, bk_repo, workflow = make_repos(workspace, project)
    service = ContentGenerationService(ws_repo, proj_repo, bk_repo, workflow)

    request = ContentGenerateRequest(
        workspace_id=workspace.id,
        project_id=project.id,
        platform="X",
        content_type="Standard Post",
        user_request="Tell me about AI",
    )

    with pytest.raises(PermissionDeniedError):
        await service.generate_content(request, attacker_id)


@pytest.mark.asyncio
async def test_generate_content_unauthorized_project():
    """Test 404 when project does not belong to workspace."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    
    other_workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=other_workspace.id)

    ws_repo, proj_repo, bk_repo, workflow = make_repos(workspace, project)
    service = ContentGenerationService(ws_repo, proj_repo, bk_repo, workflow)

    request = ContentGenerateRequest(
        workspace_id=workspace.id,
        project_id=project.id,
        platform="X",
        content_type="Standard Post",
        user_request="Tell me about AI",
    )

    with pytest.raises(ProjectNotFoundError):
        await service.generate_content(request, owner_id)
