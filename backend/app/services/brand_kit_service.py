"""
app/services/brand_kit_service.py

BrandKit business logic for CreatorOS AI.

Responsibilities:
  - Create a Brand Kit for a workspace (one per workspace, owner-only)
  - Retrieve a workspace's Brand Kit (owner-only)
  - Update a workspace's Brand Kit (owner-only)
  - Delete a workspace's Brand Kit (owner-only)

Does NOT handle:
  - FastAPI request/response
  - Database session management (injected via repository)
  - AI content generation

Authorization:
  - The requesting user must own the workspace.
  - For read operations, non-existence and non-ownership both surface as
    BrandKitNotFoundError to avoid revealing whether a workspace or its
    Brand Kit exists (same pattern as WorkspaceService.get_workspace).
"""
import uuid
import logging

from app.core.exceptions import (
    BrandKitAlreadyExistsError,
    BrandKitNotFoundError,
    WorkspaceNotFoundError,
)
from app.repositories.brand_kit_repository_interface import AbstractBrandKitRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.brand_kit import BrandKitCreate, BrandKitResponse, BrandKitUpdate

logger = logging.getLogger(__name__)


class BrandKitService:
    """
    Handles all Brand Kit business logic.

    Depends on BrandKitRepository for BrandKit data access and
    WorkspaceRepository to verify workspace ownership before any operation.
    Raises application-level exceptions; the API layer maps these to HTTP responses.
    """

    def __init__(
        self,
        brand_kit_repository: AbstractBrandKitRepository,
        workspace_repository: AbstractWorkspaceRepository,
    ) -> None:
        self._bk_repo = brand_kit_repository
        self._ws_repo = workspace_repository

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    async def _assert_workspace_owner(
        self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        """
        Verify that the workspace exists and is owned by the requesting user.

        Raises BrandKitNotFoundError in both cases (non-existence and non-ownership)
        to avoid revealing whether a workspace or its Brand Kit exists.
        """
        workspace = await self._ws_repo.get_by_id(workspace_id)
        if workspace is None or workspace.owner_id != requesting_user_id:
            if workspace is None:
                logger.warning(
                    f"Brand Kit operation denied: workspace={workspace_id} does not exist"
                )
            else:
                logger.warning(
                    f"Brand Kit operation denied: user={requesting_user_id} does not own "
                    f"workspace={workspace_id}"
                )
            raise BrandKitNotFoundError()

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_brand_kit(
        self,
        workspace_id: uuid.UUID,
        data: BrandKitCreate,
        requesting_user_id: uuid.UUID,
    ) -> BrandKitResponse:
        """
        Create a Brand Kit for the given workspace.

        Steps:
          1. Verify the workspace exists and is owned by the requester.
          2. Ensure the workspace does not already have a Brand Kit.
          3. Persist the Brand Kit via the repository.
          4. Return the BrandKitResponse.

        Args:
            workspace_id:       UUID of the workspace.
            data:               Validated BrandKitCreate schema.
            requesting_user_id: UUID of the authenticated user.

        Returns:
            BrandKitResponse for the newly created Brand Kit.

        Raises:
            BrandKitNotFoundError:      If the workspace does not exist or is not owned by the user.
            BrandKitAlreadyExistsError: If the workspace already has a Brand Kit.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        existing = await self._bk_repo.get_by_workspace_id(workspace_id)
        if existing is not None:
            logger.warning(
                f"Brand Kit already exists for workspace={workspace_id}"
            )
            raise BrandKitAlreadyExistsError()

        brand_kit = await self._bk_repo.create(data, workspace_id)
        logger.info(
            f"Brand Kit created: id={brand_kit.id} workspace={workspace_id} "
            f"owner={requesting_user_id}"
        )
        return BrandKitResponse.model_validate(brand_kit)

    # ─────────────────────────────────────────────
    # Read
    # ─────────────────────────────────────────────

    async def get_brand_kit(
        self,
        workspace_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> BrandKitResponse:
        """
        Retrieve the Brand Kit for the given workspace.

        Only the workspace owner is allowed to read the Brand Kit.
        Non-existence and non-ownership both raise BrandKitNotFoundError
        to avoid revealing whether a workspace or its Brand Kit exists.

        Args:
            workspace_id:       UUID of the workspace.
            requesting_user_id: UUID of the authenticated user.

        Returns:
            BrandKitResponse for the workspace's Brand Kit.

        Raises:
            BrandKitNotFoundError: If the workspace does not exist, is not owned by the user,
                                   or does not have a Brand Kit.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        brand_kit = await self._bk_repo.get_by_workspace_id(workspace_id)
        if brand_kit is None:
            raise BrandKitNotFoundError()

        return BrandKitResponse.model_validate(brand_kit)

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_brand_kit(
        self,
        workspace_id: uuid.UUID,
        data: BrandKitUpdate,
        requesting_user_id: uuid.UUID,
    ) -> BrandKitResponse:
        """
        Apply partial updates to the workspace's Brand Kit.

        Only the workspace owner is allowed to update.

        Args:
            workspace_id:       UUID of the workspace.
            data:               Validated BrandKitUpdate schema (partial).
            requesting_user_id: UUID of the authenticated user.

        Returns:
            Updated BrandKitResponse.

        Raises:
            BrandKitNotFoundError: If the workspace does not exist, is not owned by the user,
                                   or does not have a Brand Kit.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        brand_kit = await self._bk_repo.get_by_workspace_id(workspace_id)
        if brand_kit is None:
            raise BrandKitNotFoundError()

        updated = await self._bk_repo.update(brand_kit, data)
        logger.info(
            f"Brand Kit updated: id={brand_kit.id} workspace={workspace_id} "
            f"by user={requesting_user_id}"
        )
        return BrandKitResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_brand_kit(
        self,
        workspace_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        """
        Permanently delete the workspace's Brand Kit.

        Only the workspace owner is allowed to delete.

        Args:
            workspace_id:       UUID of the workspace.
            requesting_user_id: UUID of the authenticated user.

        Raises:
            BrandKitNotFoundError: If the workspace does not exist, is not owned by the user,
                                   or does not have a Brand Kit.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        brand_kit = await self._bk_repo.get_by_workspace_id(workspace_id)
        if brand_kit is None:
            raise BrandKitNotFoundError()

        await self._bk_repo.delete(brand_kit)
        logger.info(
            f"Brand Kit deleted: id={brand_kit.id} workspace={workspace_id} "
            f"by user={requesting_user_id}"
        )
