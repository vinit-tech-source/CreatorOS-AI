"""
tests/test_media_asset_service.py

Unit tests for MediaAssetService.
All tests use mocked repositories.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from app.core.exceptions import (
    MediaAssetNotFoundError,
    PostNotFoundError,
    WorkspaceNotFoundError,
)
from app.models.media_asset import MediaAsset, MediaType
from app.models.post import Post
from app.models.project import Project
from app.models.workspace import Workspace
from app.schemas.media_asset import MediaAssetCreate, MediaAssetUpdate
from app.services.media_asset_service import MediaAssetService


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
    return post


def make_media_asset(workspace_id: uuid.UUID | None = None) -> MediaAsset:
    media = MediaAsset()
    media.id = uuid.uuid4()
    media.workspace_id = workspace_id or uuid.uuid4()
    media.post_id = None
    media.file_name = "test.png"
    media.storage_key = "some/key/test.png"
    media.storage_url = "https://example.com/test.png"
    media.mime_type = "image/png"
    media.media_type = MediaType.IMAGE
    media.file_size = 1024
    media.width = 800
    media.height = 600
    media.duration_seconds = None
    media.checksum = "abc123checksum"
    media.alt_text = "A test image"
    media.is_active = True
    media.created_at = datetime.now(timezone.utc)
    media.updated_at = datetime.now(timezone.utc)
    return media


def make_media_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list_by_workspace = AsyncMock(return_value=[])
    repo.list_by_post = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=None)
    return repo


def make_post_repo(post: Post | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=post)
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
    media_repo: AsyncMock,
    post_repo: AsyncMock,
    proj_repo: AsyncMock,
    ws_repo: AsyncMock,
) -> MediaAssetService:
    return MediaAssetService(
        media_repo=media_repo,
        post_repo=post_repo,
        project_repo=proj_repo,
        ws_repo=ws_repo,
    )


# ─────────────────────────────────────────────
# 1. Create Media Asset
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_media_asset_success():
    """Owner can create a media asset without a post link successfully."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    media = make_media_asset(workspace_id=workspace.id)

    media_repo = make_media_repo()
    media_repo.create.return_value = media
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    data = MediaAssetCreate(
        file_name="test.png",
        storage_key="key",
        mime_type="image/png",
        media_type=MediaType.IMAGE,
        file_size=100,
    )
    result = await service.create_media_asset(
        workspace_id=workspace.id,
        data=data,
        requesting_user_id=owner_id,
    )

    media_repo.create.assert_awaited_once()
    assert result.id == media.id


@pytest.mark.asyncio
async def test_create_media_asset_with_post_success():
    """Owner can create a media asset linked to their own post."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    project = make_project(workspace_id=workspace.id)
    post = make_post(project_id=project.id)
    media = make_media_asset(workspace_id=workspace.id)
    media.post_id = post.id

    media_repo = make_media_repo()
    media_repo.create.return_value = media
    post_repo = make_post_repo(post=post)
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, post_repo, proj_repo, ws_repo)

    data = MediaAssetCreate(
        post_id=post.id,
        file_name="test.png",
        storage_key="key",
        mime_type="image/png",
        media_type=MediaType.IMAGE,
        file_size=100,
    )
    result = await service.create_media_asset(
        workspace_id=workspace.id,
        data=data,
        requesting_user_id=owner_id,
    )

    media_repo.create.assert_awaited_once()
    assert result.post_id == post.id


@pytest.mark.asyncio
async def test_create_media_asset_wrong_workspace_post_raises():
    """Trying to link a media asset to a post in a different workspace raises 404."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    
    # Another user's project and post
    other_workspace = make_workspace(owner_id=uuid.uuid4())
    project = make_project(workspace_id=other_workspace.id)
    post = make_post(project_id=project.id)

    media_repo = make_media_repo()
    post_repo = make_post_repo(post=post)
    proj_repo = make_proj_repo(project=project)
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, post_repo, proj_repo, ws_repo)

    data = MediaAssetCreate(
        post_id=post.id,
        file_name="test.png",
        storage_key="key",
        mime_type="image/png",
        media_type=MediaType.IMAGE,
        file_size=100,
    )
    with pytest.raises(PostNotFoundError):
        await service.create_media_asset(
            workspace_id=workspace.id,
            data=data,
            requesting_user_id=owner_id,
        )


@pytest.mark.asyncio
async def test_create_media_asset_non_owner_raises():
    """Non-owner receives 404."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    media_repo = make_media_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    data = MediaAssetCreate(
        file_name="test.png",
        storage_key="key",
        mime_type="image/png",
        media_type=MediaType.IMAGE,
        file_size=100,
    )
    with pytest.raises(WorkspaceNotFoundError):
        await service.create_media_asset(
            workspace_id=workspace.id,
            data=data,
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# Schema Validation
# ─────────────────────────────────────────────

def test_media_asset_invalid_enum_raises():
    with pytest.raises(ValidationError):
        MediaAssetCreate(
            file_name="test.png",
            storage_key="key",
            mime_type="image/png",
            media_type="INVALID_TYPE", # type: ignore
            file_size=100,
        )

def test_media_asset_negative_file_size_raises():
    with pytest.raises(ValidationError):
        MediaAssetCreate(
            file_name="test.png",
            storage_key="key",
            mime_type="image/png",
            media_type=MediaType.IMAGE,
            file_size=-100,
        )

def test_media_asset_invalid_dimensions_raises():
    with pytest.raises(ValidationError):
        MediaAssetCreate(
            file_name="test.png",
            storage_key="key",
            mime_type="image/png",
            media_type=MediaType.IMAGE,
            file_size=100,
            width=-10,
        )


# ─────────────────────────────────────────────
# Read
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_media_asset_owner_succeeds():
    """Owner can retrieve a media asset."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    media = make_media_asset(workspace_id=workspace.id)

    media_repo = make_media_repo()
    media_repo.get_by_id.return_value = media
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    result = await service.get_media_asset(
        workspace_id=workspace.id,
        media_id=media.id,
        requesting_user_id=owner_id,
    )
    assert result.id == media.id


@pytest.mark.asyncio
async def test_get_media_asset_non_owner_raises():
    """Non-owner receives 404."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    media_repo = make_media_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    with pytest.raises(WorkspaceNotFoundError):
        await service.get_media_asset(
            workspace_id=workspace.id,
            media_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )


@pytest.mark.asyncio
async def test_list_media_assets_owner_succeeds():
    """Owner can list workspace media."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    medias = [make_media_asset(workspace_id=workspace.id) for _ in range(3)]

    media_repo = make_media_repo()
    media_repo.list_by_workspace.return_value = medias
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    result = await service.list_media_assets(
        workspace_id=workspace.id,
        requesting_user_id=owner_id,
    )
    assert len(result) == 3


# ─────────────────────────────────────────────
# Update
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_media_asset_owner_succeeds():
    """Owner can update media asset."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    media = make_media_asset(workspace_id=workspace.id)
    updated_media = make_media_asset(workspace_id=workspace.id)
    updated_media.alt_text = "New Alt Text"

    media_repo = make_media_repo()
    media_repo.get_by_id.return_value = media
    media_repo.update.return_value = updated_media
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    data = MediaAssetUpdate(alt_text="New Alt Text")
    result = await service.update_media_asset(
        workspace_id=workspace.id,
        media_id=media.id,
        data=data,
        requesting_user_id=owner_id,
    )
    assert result.alt_text == "New Alt Text"


@pytest.mark.asyncio
async def test_update_media_asset_non_owner_raises():
    """Non-owner receives 404 when trying to update."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    media_repo = make_media_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    with pytest.raises(WorkspaceNotFoundError):
        await service.update_media_asset(
            workspace_id=workspace.id,
            media_id=uuid.uuid4(),
            data=MediaAssetUpdate(alt_text="Hacked"),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_media_asset_owner_succeeds():
    """Owner can delete media asset."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    media = make_media_asset(workspace_id=workspace.id)

    media_repo = make_media_repo()
    media_repo.get_by_id.return_value = media
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    await service.delete_media_asset(
        workspace_id=workspace.id,
        media_id=media.id,
        requesting_user_id=owner_id,
    )
    media_repo.delete.assert_awaited_once_with(media)


@pytest.mark.asyncio
async def test_delete_media_asset_non_owner_raises():
    """Non-owner receives 404 when trying to delete."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    media_repo = make_media_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(media_repo, AsyncMock(), AsyncMock(), ws_repo)

    with pytest.raises(WorkspaceNotFoundError):
        await service.delete_media_asset(
            workspace_id=workspace.id,
            media_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )
