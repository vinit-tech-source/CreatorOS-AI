"""
app/services/workspace_service.py

Workspace business logic for CreatorOS AI.

Responsibilities:
  - Create workspace (with slug uniqueness validation)
  - Retrieve a single workspace
  - List workspaces owned by a user
  - Update workspace (owner-only)
  - Delete workspace (owner-only)

Does NOT handle:
  - FastAPI request/response
  - Database session management (injected via repository)
  - Brand Kit or social media integrations
"""
import uuid
import logging

from app.core.exceptions import (
    PermissionDeniedError,
    SlugAlreadyExistsError,
    WorkspaceNotFoundError,
)
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate

logger = logging.getLogger(__name__)


class WorkspaceService:
    """
    Handles all workspace-related business logic.

    Depends on WorkspaceRepository for data access.
    Raises application-level exceptions; the API layer maps these to HTTP responses.
    """

    def __init__(self, workspace_repository: WorkspaceRepository) -> None:
        self._repo = workspace_repository

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_workspace(
        self, data: WorkspaceCreate, owner_id: uuid.UUID
    ) -> WorkspaceResponse:
        """
        Create a new workspace for the given owner.

        Steps:
          1. Verify the slug is not already taken.
          2. Persist the workspace via the repository.
          3. Return the workspace response.

        Args:
            data:     Validated WorkspaceCreate schema.
            owner_id: UUID of the authenticated user creating the workspace.

        Returns:
            WorkspaceResponse for the newly created workspace.

        Raises:
            SlugAlreadyExistsError: If the slug is already in use.
        """
        existing = await self._repo.get_by_slug(data.slug)
        if existing is not None:
            logger.warning(f"Workspace creation failed — slug taken: {data.slug}")
            raise SlugAlreadyExistsError()

        workspace = await self._repo.create(data, owner_id)
        logger.info(
            f"Workspace created: id={workspace.id} slug={workspace.slug} "
            f"owner={owner_id}"
        )
        return WorkspaceResponse.model_validate(workspace)

    # ─────────────────────────────────────────────
    # Read (single)
    # ─────────────────────────────────────────────

    async def get_workspace(self, workspace_id: uuid.UUID) -> WorkspaceResponse:
        """
        Retrieve a workspace by its UUID.

        Args:
            workspace_id: UUID of the workspace to retrieve.

        Returns:
            WorkspaceResponse for the workspace.

        Raises:
            WorkspaceNotFoundError: If no workspace exists with the given ID.
        """
        workspace = await self._repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError()
        return WorkspaceResponse.model_validate(workspace)

    # ─────────────────────────────────────────────
    # Read (list)
    # ─────────────────────────────────────────────

    async def list_workspaces(
        self, owner_id: uuid.UUID
    ) -> list[WorkspaceResponse]:
        """
        List all workspaces owned by the given user.

        Args:
            owner_id: UUID of the user whose workspaces to list.

        Returns:
            List of WorkspaceResponse objects, ordered by name.
        """
        workspaces = await self._repo.list_by_owner(owner_id)
        return [WorkspaceResponse.model_validate(w) for w in workspaces]

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_workspace(
        self,
        workspace_id: uuid.UUID,
        data: WorkspaceUpdate,
        requesting_user_id: uuid.UUID,
    ) -> WorkspaceResponse:
        """
        Apply partial updates to an existing workspace.

        Only the workspace owner is allowed to update.

        Args:
            workspace_id:       UUID of the workspace to update.
            data:               Validated WorkspaceUpdate schema (partial).
            requesting_user_id: UUID of the authenticated user making the request.

        Returns:
            Updated WorkspaceResponse.

        Raises:
            WorkspaceNotFoundError: If the workspace does not exist.
            PermissionDeniedError:  If the requester is not the workspace owner.
        """
        workspace = await self._repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError()

        if workspace.owner_id != requesting_user_id:
            logger.warning(
                f"Permission denied: user={requesting_user_id} attempted to update "
                f"workspace={workspace_id} owned by {workspace.owner_id}"
            )
            raise PermissionDeniedError()

        updated = await self._repo.update(workspace, data)
        logger.info(f"Workspace updated: id={workspace_id} by user={requesting_user_id}")
        return WorkspaceResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_workspace(
        self,
        workspace_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        """
        Permanently delete a workspace.

        Only the workspace owner is allowed to delete.

        Args:
            workspace_id:       UUID of the workspace to delete.
            requesting_user_id: UUID of the authenticated user making the request.

        Raises:
            WorkspaceNotFoundError: If the workspace does not exist.
            PermissionDeniedError:  If the requester is not the workspace owner.
        """
        workspace = await self._repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError()

        if workspace.owner_id != requesting_user_id:
            logger.warning(
                f"Permission denied: user={requesting_user_id} attempted to delete "
                f"workspace={workspace_id} owned by {workspace.owner_id}"
            )
            raise PermissionDeniedError()

        await self._repo.delete(workspace)
        logger.info(f"Workspace deleted: id={workspace_id} by user={requesting_user_id}")
