"""
tests/test_project_service.py

Unit tests for ProjectService.
All tests use mocked repositories.
"""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    ProjectNotFoundError,
    ProjectSlugAlreadyExistsError,
)
from app.models.project import Project, ProjectStatus
from app.models.workspace import Workspace
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_workspace(owner_id: uuid.UUID | None = None) -> Workspace:
    ws = Workspace()
    ws.id = uuid.uuid4()
    ws.name = "Test Workspace"
    ws.slug = "test-ws"
    ws.owner_id = owner_id or uuid.uuid4()
    return ws


def make_project(workspace_id: uuid.UUID | None = None) -> Project:
    proj = Project()
    proj.id = uuid.uuid4()
    proj.workspace_id = workspace_id or uuid.uuid4()
    proj.name = "Test Project"
    proj.slug = "test-project"
    proj.description = None
    proj.status = ProjectStatus.DRAFT
    proj.objective = None
    proj.target_audience = None
    proj.start_date = None
    proj.end_date = None
    proj.is_active = True
    proj.created_at = datetime.now(timezone.utc)
    proj.updated_at = datetime.now(timezone.utc)
    return proj


def make_proj_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_slug = AsyncMock(return_value=None)
    repo.list_by_workspace = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=None)
    return repo


def make_ws_repo(workspace: Workspace | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=workspace)
    return repo


def make_service(proj_repo: AsyncMock, ws_repo: AsyncMock) -> ProjectService:
    return ProjectService(project_repository=proj_repo, workspace_repository=ws_repo)


# ─────────────────────────────────────────────
# 1. Create Project
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_project_success():
    """Owner can create a project successfully."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    proj_repo = make_proj_repo()
    proj_repo.get_by_slug.return_value = None
    proj_repo.create.return_value = project

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    data = ProjectCreate(name="My Proj", slug="my-proj", status=ProjectStatus.DRAFT)
    result = await service.create_project(
        workspace_id=workspace.id,
        data=data,
        requesting_user_id=owner_id,
    )

    proj_repo.create.assert_awaited_once()
    assert result.id == project.id


@pytest.mark.asyncio
async def test_create_project_duplicate_slug_raises():
    """Creating a project with an existing slug in the same workspace raises 409."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    existing_project = make_project(workspace_id=workspace.id)

    proj_repo = make_proj_repo()
    proj_repo.get_by_slug.return_value = existing_project

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    data = ProjectCreate(name="My Proj", slug=existing_project.slug, status=ProjectStatus.DRAFT)
    with pytest.raises(ProjectSlugAlreadyExistsError):
        await service.create_project(
            workspace_id=workspace.id,
            data=data,
            requesting_user_id=owner_id,
        )


# ─────────────────────────────────────────────
# 2. Schema Validation (Enum, Dates)
# ─────────────────────────────────────────────

def test_project_create_invalid_status_raises():
    """Providing an invalid enum value raises validation error."""
    with pytest.raises(ValueError):
        ProjectCreate(name="Test", slug="test", status="INVALID_STATUS")


def test_project_create_invalid_date_range_raises():
    """end_date < start_date raises validation error."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="end_date cannot be earlier than start_date"):
        ProjectCreate(
            name="Test",
            slug="test",
            status=ProjectStatus.DRAFT,
            start_date=now,
            end_date=now - timedelta(days=1),
        )


def test_project_update_invalid_date_range_raises():
    """end_date < start_date in update schema raises validation error."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="end_date cannot be earlier than start_date"):
        ProjectUpdate(start_date=now, end_date=now - timedelta(days=1))


# ─────────────────────────────────────────────
# 3. Get Project
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_project_owner_succeeds():
    """Owner can retrieve a project."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    proj_repo = make_proj_repo()
    proj_repo.get_by_id.return_value = project

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    result = await service.get_project(
        workspace_id=workspace.id,
        project_id=project.id,
        requesting_user_id=owner_id,
    )
    assert result.id == project.id


@pytest.mark.asyncio
async def test_get_project_non_owner_raises_not_found():
    """Non-owner receives 404."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    proj_repo = make_proj_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    with pytest.raises(ProjectNotFoundError):
        await service.get_project(
            workspace_id=workspace.id,
            project_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# 4. List Projects
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_projects_owner_succeeds():
    """Owner can list workspace projects."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    projects = [make_project(workspace_id=workspace.id) for _ in range(3)]

    proj_repo = make_proj_repo()
    proj_repo.list_by_workspace.return_value = projects

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    result = await service.list_projects(
        workspace_id=workspace.id,
        requesting_user_id=owner_id,
    )
    assert len(result) == 3


# ─────────────────────────────────────────────
# 5. Update Project
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_project_owner_succeeds():
    """Owner can update project."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    updated_project = make_project(workspace_id=workspace.id)
    updated_project.name = "Updated Name"

    proj_repo = make_proj_repo()
    proj_repo.get_by_id.return_value = project
    proj_repo.update.return_value = updated_project

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    data = ProjectUpdate(name="Updated Name")
    result = await service.update_project(
        workspace_id=workspace.id,
        project_id=project.id,
        data=data,
        requesting_user_id=owner_id,
    )

    proj_repo.update.assert_awaited_once()
    assert result.name == "Updated Name"


@pytest.mark.asyncio
async def test_update_project_duplicate_slug_raises():
    """Owner cannot update slug to one that already exists."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    existing_other_project = make_project(workspace_id=workspace.id)
    existing_other_project.slug = "existing-slug"

    proj_repo = make_proj_repo()
    proj_repo.get_by_id.return_value = project
    proj_repo.get_by_slug.return_value = existing_other_project

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    data = ProjectUpdate(slug="existing-slug")
    with pytest.raises(ProjectSlugAlreadyExistsError):
        await service.update_project(
            workspace_id=workspace.id,
            project_id=project.id,
            data=data,
            requesting_user_id=owner_id,
        )


@pytest.mark.asyncio
async def test_update_project_non_owner_raises():
    """Non-owner cannot update project."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    proj_repo = make_proj_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    with pytest.raises(ProjectNotFoundError):
        await service.update_project(
            workspace_id=workspace.id,
            project_id=uuid.uuid4(),
            data=ProjectUpdate(name="Hacked"),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# 6. Delete Project
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_project_owner_succeeds():
    """Owner can delete project."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    proj_repo = make_proj_repo()
    proj_repo.get_by_id.return_value = project

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    await service.delete_project(
        workspace_id=workspace.id,
        project_id=project.id,
        requesting_user_id=owner_id,
    )

    proj_repo.delete.assert_awaited_once_with(project)


@pytest.mark.asyncio
async def test_delete_project_non_owner_raises():
    """Non-owner cannot delete project."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    proj_repo = make_proj_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(proj_repo, ws_repo)

    with pytest.raises(ProjectNotFoundError):
        await service.delete_project(
            workspace_id=workspace.id,
            project_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )
