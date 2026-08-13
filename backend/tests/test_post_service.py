"""
tests/test_post_service.py

Unit tests for PostService.
All tests use mocked repositories.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    InvalidStatusTransitionError,
    PostNotFoundError,
    ProjectNotFoundError,
)
from app.models.post import ContentType, Post, PostStatus
from app.models.project import Project
from app.models.social_account import SocialPlatform
from app.models.workspace import Workspace
from app.schemas.post import PostCreate, PostUpdate
from app.services.post_service import PostService


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_workspace(owner_id: uuid.UUID | None = None) -> Workspace:
    ws = Workspace()
    ws.id = uuid.uuid4()
    ws.name = "Test Workspace"
    ws.owner_id = owner_id or uuid.uuid4()
    return ws


def make_project(workspace_id: uuid.UUID | None = None) -> Project:
    proj = Project()
    proj.id = uuid.uuid4()
    proj.workspace_id = workspace_id or uuid.uuid4()
    return proj


def make_post(project_id: uuid.UUID | None = None) -> Post:
    post = Post()
    post.id = uuid.uuid4()
    post.project_id = project_id or uuid.uuid4()
    post.title = "Test Post"
    post.content = "Test Content"
    post.content_type = ContentType.TEXT
    post.status = PostStatus.DRAFT
    post.platform = SocialPlatform.X
    post.scheduled_at = None
    post.published_at = None
    post.external_post_id = None
    post.created_at = datetime.now(timezone.utc)
    post.updated_at = datetime.now(timezone.utc)
    return post


def make_post_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list_by_project = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=None)
    return repo


def make_proj_repo(project: Project | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=project)
    return repo


def make_ws_repo(workspace: Workspace | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=workspace)
    return repo


def make_service(
    post_repo: AsyncMock, proj_repo: AsyncMock, ws_repo: AsyncMock
) -> PostService:
    return PostService(
        post_repository=post_repo,
        project_repository=proj_repo,
        workspace_repository=ws_repo,
    )


# ─────────────────────────────────────────────
# 1. Create Post
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_post_success():
    """Owner can create a post successfully."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)

    post_repo = make_post_repo()
    post_repo.create.return_value = post
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    data = PostCreate(
        content="Test Content",
        content_type=ContentType.TEXT,
        status=PostStatus.DRAFT,
        platform=SocialPlatform.X,
    )
    result = await service.create_post(
        project_id=project.id,
        data=data,
        requesting_user_id=owner_id,
    )

    post_repo.create.assert_awaited_once()
    assert result.id == post.id


@pytest.mark.asyncio
async def test_create_post_non_owner_raises():
    """Non-owner receives 404."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    post_repo = make_post_repo()
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    data = PostCreate(
        content="Test", content_type=ContentType.TEXT, platform=SocialPlatform.X
    )
    with pytest.raises(ProjectNotFoundError):
        await service.create_post(
            project_id=project.id,
            data=data,
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# Schema Validation
# ─────────────────────────────────────────────

def test_post_create_invalid_content_raises():
    """Empty content raises validation error."""
    with pytest.raises(ValueError):
        PostCreate(
            content="",
            content_type=ContentType.TEXT,
            status=PostStatus.DRAFT,
            platform=SocialPlatform.X,
        )


def test_post_create_invalid_enum_raises():
    """Invalid enum value raises validation error."""
    with pytest.raises(ValueError):
        PostCreate(
            content="test",
            content_type="INVALID_TYPE",
            status=PostStatus.DRAFT,
            platform=SocialPlatform.X,
        )


# ─────────────────────────────────────────────
# Read
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_post_owner_succeeds():
    """Owner can retrieve a post."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)

    post_repo = make_post_repo()
    post_repo.get_by_id.return_value = post
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    result = await service.get_post(
        project_id=project.id,
        post_id=post.id,
        requesting_user_id=owner_id,
    )
    assert result.id == post.id


@pytest.mark.asyncio
async def test_get_post_non_owner_raises():
    """Non-owner receives 404."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    post_repo = make_post_repo()
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    with pytest.raises(ProjectNotFoundError):
        await service.get_post(
            project_id=project.id,
            post_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )


@pytest.mark.asyncio
async def test_list_posts_owner_succeeds():
    """Owner can list project posts."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    posts = [make_post(project_id=project.id) for _ in range(3)]

    post_repo = make_post_repo()
    post_repo.list_by_project.return_value = posts
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    result = await service.list_posts(
        project_id=project.id,
        requesting_user_id=owner_id,
    )
    assert len(result) == 3


# ─────────────────────────────────────────────
# Update & Transitions
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_post_owner_succeeds():
    """Owner can update post content."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)
    updated_post = make_post(project_id=project.id)
    updated_post.content = "Updated Content"

    post_repo = make_post_repo()
    post_repo.get_by_id.return_value = post
    post_repo.update.return_value = updated_post
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    data = PostUpdate(content="Updated Content")
    result = await service.update_post(
        project_id=project.id,
        post_id=post.id,
        data=data,
        requesting_user_id=owner_id,
    )
    assert result.content == "Updated Content"


@pytest.mark.asyncio
async def test_update_post_valid_transition_succeeds():
    """Transitioning from DRAFT to PENDING_REVIEW succeeds."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)
    post.status = PostStatus.DRAFT

    updated_post = make_post(project_id=project.id)
    updated_post.status = PostStatus.PENDING_REVIEW

    post_repo = make_post_repo()
    post_repo.get_by_id.return_value = post
    post_repo.update.return_value = updated_post
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    data = PostUpdate(status=PostStatus.PENDING_REVIEW)
    result = await service.update_post(
        project_id=project.id,
        post_id=post.id,
        data=data,
        requesting_user_id=owner_id,
    )
    assert result.status == PostStatus.PENDING_REVIEW


@pytest.mark.asyncio
async def test_update_post_invalid_transition_raises():
    """Transitioning from DRAFT to PUBLISHED fails."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)
    post.status = PostStatus.DRAFT

    post_repo = make_post_repo()
    post_repo.get_by_id.return_value = post
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    data = PostUpdate(status=PostStatus.PUBLISHED)
    with pytest.raises(InvalidStatusTransitionError):
        await service.update_post(
            project_id=project.id,
            post_id=post.id,
            data=data,
            requesting_user_id=owner_id,
        )


@pytest.mark.asyncio
async def test_update_post_non_owner_raises():
    """Non-owner receives 404 when trying to update."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    post_repo = make_post_repo()
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    with pytest.raises(ProjectNotFoundError):
        await service.update_post(
            project_id=project.id,
            post_id=uuid.uuid4(),
            data=PostUpdate(content="Hacked"),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_post_owner_succeeds():
    """Owner can delete post."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)

    post_repo = make_post_repo()
    post_repo.get_by_id.return_value = post
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    await service.delete_post(
        project_id=project.id,
        post_id=post.id,
        requesting_user_id=owner_id,
    )
    post_repo.delete.assert_awaited_once_with(post)


@pytest.mark.asyncio
async def test_delete_post_non_owner_raises():
    """Non-owner receives 404 when trying to delete."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)

    post_repo = make_post_repo()
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    with pytest.raises(ProjectNotFoundError):
        await service.delete_post(
            project_id=project.id,
            post_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# Edge Cases
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_access_post_from_wrong_project_raises():
    """Accessing a post through the wrong project ID raises 404."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project_a = make_project(workspace_id=workspace.id)
    project_b = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project_a.id)

    post_repo = make_post_repo()
    post_repo.get_by_id.return_value = post
    proj_repo = make_proj_repo(project=project_b)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(post_repo, proj_repo, ws_repo)

    # Trying to get post from project_a using project_b's ID
    with pytest.raises(PostNotFoundError):
        await service.get_post(
            project_id=project_b.id,
            post_id=post.id,
            requesting_user_id=owner_id,
        )
