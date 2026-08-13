"""
app/services/project_service.py

Project business logic for CreatorOS AI.

Responsibilities:
  - Create, read, update, delete Content Projects.
  - Enforce workspace ownership boundaries (info hiding with 404).
  - Enforce workspace-scoped slug uniqueness.
"""
import uuid
import logging
from typing import Optional

from app.core.exceptions import (
    ProjectNotFoundError,
    ProjectSlugAlreadyExistsError,
)
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Handles Project business logic.
    """

    def __init__(
        self,
        project_repository: AbstractProjectRepository,
        workspace_repository: AbstractWorkspaceRepository,
    ) -> None:
        self._project_repo = project_repository
        self._ws_repo = workspace_repository

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    async def _assert_workspace_owner(
        self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        """
        Verify that the workspace exists and is owned by the requesting user.
        Raises ProjectNotFoundError to avoid confirming existence.
        """
        workspace = await self._ws_repo.get_by_id(workspace_id)
        if workspace is None or workspace.owner_id != requesting_user_id:
            if workspace is None:
                logger.warning(
                    f"Project operation denied: workspace={workspace_id} does not exist"
                )
            else:
                logger.warning(
                    f"Project operation denied: user={requesting_user_id} does not own "
                    f"workspace={workspace_id}"
                )
            raise ProjectNotFoundError()

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_project(
        self,
        workspace_id: uuid.UUID,
        data: ProjectCreate,
        requesting_user_id: uuid.UUID,
    ) -> ProjectResponse:
        """
        Create a new Content Project in the workspace.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        # Check slug uniqueness within workspace
        existing = await self._project_repo.get_by_slug(workspace_id, data.slug)
        if existing is not None:
            raise ProjectSlugAlreadyExistsError()

        project = await self._project_repo.create(data, workspace_id)
        return ProjectResponse.model_validate(project)

    # ─────────────────────────────────────────────
    # Read (Single)
    # ─────────────────────────────────────────────

    async def get_project(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> ProjectResponse:
        """
        Retrieve details of a specific project.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        project = await self._project_repo.get_by_id(project_id)
        if project is None or project.workspace_id != workspace_id:
            raise ProjectNotFoundError()

        return ProjectResponse.model_validate(project)

    # ─────────────────────────────────────────────
    # Read (List)
    # ─────────────────────────────────────────────

    async def list_projects(
        self,
        workspace_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> list[ProjectResponse]:
        """
        List all projects for the workspace.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        projects = await self._project_repo.list_by_workspace(workspace_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_project(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        requesting_user_id: uuid.UUID,
    ) -> ProjectResponse:
        """
        Apply partial updates to a project.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        project = await self._project_repo.get_by_id(project_id)
        if project is None or project.workspace_id != workspace_id:
            raise ProjectNotFoundError()

        if data.slug is not None and data.slug != project.slug:
            existing = await self._project_repo.get_by_slug(workspace_id, data.slug)
            if existing is not None:
                raise ProjectSlugAlreadyExistsError()

        updated = await self._project_repo.update(project, data)
        return ProjectResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_project(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        """
        Delete a project permanently.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        project = await self._project_repo.get_by_id(project_id)
        if project is None or project.workspace_id != workspace_id:
            raise ProjectNotFoundError()

        await self._project_repo.delete(project)
