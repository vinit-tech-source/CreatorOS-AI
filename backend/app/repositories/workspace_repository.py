import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate

logger = logging.getLogger(__name__)


class WorkspaceRepository(AbstractWorkspaceRepository):
    """
    Concrete SQLAlchemy 2.0 async implementation of the Workspace repository.
    All database access for the Workspace model is handled here.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: WorkspaceCreate, owner_id: uuid.UUID) -> Workspace:
        """Create and persist a new Workspace record."""
        workspace = Workspace(
            name=data.name,
            slug=data.slug,
            description=data.description,
            owner_id=owner_id,
            logo_url=data.logo_url,
            timezone=data.timezone,
        )
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        logger.info(f"Workspace created: id={workspace.id} slug={workspace.slug}")
        return workspace

    async def get_by_id(self, workspace_id: uuid.UUID) -> Optional[Workspace]:
        """Return a Workspace by primary key, or None if not found."""
        result = await self.session.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        """Return a Workspace by slug, or None if not found."""
        result = await self.session.execute(
            select(Workspace).where(Workspace.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: uuid.UUID) -> list[Workspace]:
        """Return all Workspaces owned by the given user, ordered by name."""
        result = await self.session.execute(
            select(Workspace)
            .where(Workspace.owner_id == owner_id)
            .order_by(Workspace.name)
        )
        return list(result.scalars().all())

    async def update(self, workspace: Workspace, data: WorkspaceUpdate) -> Workspace:
        """Apply partial updates from WorkspaceUpdate schema to an existing Workspace.

        Uses exclude_unset=True so that:
          - Omitted fields are left unchanged.
          - Explicitly provided null values (e.g. {"logo_url": null}) correctly
            clear nullable fields on the model.
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        logger.info(f"Workspace updated: id={workspace.id}")
        return workspace

    async def delete(self, workspace: Workspace) -> None:
        """Permanently remove a Workspace record from the database."""
        await self.session.delete(workspace)
        await self.session.commit()
        logger.info(f"Workspace deleted: id={workspace.id} slug={workspace.slug}")
