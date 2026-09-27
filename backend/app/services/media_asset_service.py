"""
app/services/media_asset_service.py

MediaAsset business logic for CreatorOS AI.

Responsibilities:
  - Create, read, update, delete Media Assets.
  - Enforce workspace ownership boundaries.
  - Optionally validate Post relationships against the workspace.
"""
import uuid
import logging
from typing import Optional

from app.core.exceptions import (
    MediaAssetNotFoundError,
    PostNotFoundError,
    WorkspaceNotFoundError,
)
from app.repositories.media_asset_repository_interface import AbstractMediaAssetRepository
from app.repositories.post_repository_interface import AbstractPostRepository
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.media_asset import (
    MediaAssetCreate,
    MediaAssetResponse,
    MediaAssetUpdate,
)

logger = logging.getLogger(__name__)


class MediaAssetService:
    """
    Handles MediaAsset business logic.
    """

    def __init__(
        self,
        media_repo: AbstractMediaAssetRepository,
        post_repo: AbstractPostRepository,
        project_repo: AbstractProjectRepository,
        ws_repo: AbstractWorkspaceRepository,
    ) -> None:
        self._media_repo = media_repo
        self._post_repo = post_repo
        self._project_repo = project_repo
        self._ws_repo = ws_repo

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    async def _assert_workspace_owner(
        self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        """
        Verify that the workspace exists and is owned by the requesting user.
        Raises WorkspaceNotFoundError to avoid info leakage.
        """
        workspace = await self._ws_repo.get_by_id(workspace_id)
        if workspace is None or workspace.owner_id != requesting_user_id:
            logger.warning(
                f"Media access denied: user={requesting_user_id} does not own "
                f"workspace={workspace_id}"
            )
            raise WorkspaceNotFoundError()

    async def _assert_post_belongs_to_workspace(
        self, post_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> None:
        """
        Verify that a given post belongs to a project within the given workspace.
        """
        post = await self._post_repo.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError()
            
        project = await self._project_repo.get_by_id(post.project_id)
        if project is None or project.workspace_id != workspace_id:
            logger.warning(
                f"Media linking denied: post={post_id} does not belong to workspace={workspace_id}"
            )
            raise PostNotFoundError()

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_media_asset(
        self,
        workspace_id: uuid.UUID,
        data: MediaAssetCreate,
        requesting_user_id: uuid.UUID,
    ) -> MediaAssetResponse:
        """
        Create a new MediaAsset in the workspace.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        if data.post_id:
            await self._assert_post_belongs_to_workspace(data.post_id, workspace_id)

        media = await self._media_repo.create(data, workspace_id)
        return MediaAssetResponse.model_validate(media)

    # ─────────────────────────────────────────────
    # Read (Single)
    # ─────────────────────────────────────────────

    async def get_media_asset(
        self,
        workspace_id: uuid.UUID,
        media_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> MediaAssetResponse:
        """
        Retrieve details of a specific media asset.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        media = await self._media_repo.get_by_id(media_id)
        if media is None or media.workspace_id != workspace_id:
            raise MediaAssetNotFoundError()

        return MediaAssetResponse.model_validate(media)

    # ─────────────────────────────────────────────
    # Read (List)
    # ─────────────────────────────────────────────

    async def list_media_assets(
        self,
        workspace_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MediaAssetResponse]:
        """
        List media assets for the workspace with pagination.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        medias = await self._media_repo.list_by_workspace(workspace_id, limit=limit, offset=offset)
        return [MediaAssetResponse.model_validate(m) for m in medias]

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_media_asset(
        self,
        workspace_id: uuid.UUID,
        media_id: uuid.UUID,
        data: MediaAssetUpdate,
        requesting_user_id: uuid.UUID,
    ) -> MediaAssetResponse:
        """
        Apply partial updates to a media asset.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        media = await self._media_repo.get_by_id(media_id)
        if media is None or media.workspace_id != workspace_id:
            raise MediaAssetNotFoundError()

        if data.post_id is not None:
            await self._assert_post_belongs_to_workspace(data.post_id, workspace_id)

        updated = await self._media_repo.update(media, data)
        return MediaAssetResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_media_asset(
        self,
        workspace_id: uuid.UUID,
        media_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        """
        Delete a media asset permanently.
        Note: The actual cloud storage deletion would happen via an event/worker.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        media = await self._media_repo.get_by_id(media_id)
        if media is None or media.workspace_id != workspace_id:
            raise MediaAssetNotFoundError()

        await self._media_repo.delete(media)
