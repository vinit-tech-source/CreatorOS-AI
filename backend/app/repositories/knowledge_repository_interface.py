import uuid
from abc import ABC, abstractmethod

from app.models.knowledge_source import KnowledgeSource

class KnowledgeRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        pass

    @abstractmethod
    async def get_by_id(self, knowledge_id: uuid.UUID) -> KnowledgeSource | None:
        pass

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> list[KnowledgeSource]:
        pass

    @abstractmethod
    async def update(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        pass

    @abstractmethod
    async def delete(self, knowledge_id: uuid.UUID) -> None:
        pass
