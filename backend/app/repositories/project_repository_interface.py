import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class AbstractProjectRepository(ABC):
    """Abstract interface for the Project repository."""

    @abstractmethod
    async def create(self, data: ProjectCreate, workspace_id: uuid.UUID) -> Project:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_slug(self, workspace_id: uuid.UUID, slug: str) -> Optional[Project]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID) -> list[Project]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, project: Project, data: ProjectUpdate) -> Project:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, project: Project) -> None:
        raise NotImplementedError
