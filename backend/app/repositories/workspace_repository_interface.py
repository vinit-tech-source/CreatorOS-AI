import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class AbstractWorkspaceRepository(ABC):
    """Abstract interface for the Workspace repository."""

    @abstractmethod
    async def create(self, data: WorkspaceCreate, owner_id: uuid.UUID) -> Workspace:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, workspace_id: uuid.UUID) -> Optional[Workspace]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(self, owner_id: uuid.UUID) -> list[Workspace]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, workspace: Workspace, data: WorkspaceUpdate) -> Workspace:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, workspace: Workspace) -> None:
        raise NotImplementedError
