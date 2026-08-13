"""
app/repositories/project_repository.py

Concrete SQLAlchemy 2.0 async implementation of the Project repository.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectRepository(AbstractProjectRepository):
    """Concrete repository for Project database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: ProjectCreate, workspace_id: uuid.UUID) -> Project:
        """Persist a new Project to the database."""
        project = Project(
            workspace_id=workspace_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            status=data.status,
            objective=data.objective,
            target_audience=data.target_audience,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=True,
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        logger.info(
            f"Project created: id={project.id} slug={project.slug} workspace={workspace_id}"
        )
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        """Return a Project by its UUID primary key."""
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, workspace_id: uuid.UUID, slug: str) -> Optional[Project]:
        """Return a Project by its workspace_id and slug combination."""
        result = await self.session.execute(
            select(Project).where(
                Project.workspace_id == workspace_id,
                Project.slug == slug,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: uuid.UUID) -> list[Project]:
        """Return all Projects for a specific workspace, ordered newest first."""
        result = await self.session.execute(
            select(Project)
            .where(Project.workspace_id == workspace_id)
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, project: Project, data: ProjectUpdate) -> Project:
        """Apply partial updates from ProjectUpdate schema.

        Uses exclude_unset=True so that:
          - Omitted fields are left unchanged.
          - Explicitly provided null values clear nullable fields.
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        logger.info(f"Project updated: id={project.id} slug={project.slug}")
        return project

    async def delete(self, project: Project) -> None:
        """Permanently remove a Project record."""
        await self.session.delete(project)
        await self.session.commit()
        logger.info(
            f"Project deleted: id={project.id} slug={project.slug} workspace={project.workspace_id}"
        )
