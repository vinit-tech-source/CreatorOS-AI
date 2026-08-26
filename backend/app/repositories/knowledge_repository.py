import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_source import KnowledgeSource
from app.repositories.knowledge_repository_interface import KnowledgeRepositoryInterface

class KnowledgeRepository(KnowledgeRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        self.session.add(knowledge_source)
        await self.session.commit()
        await self.session.refresh(knowledge_source)
        return knowledge_source

    async def get_by_id(self, knowledge_id: uuid.UUID) -> KnowledgeSource | None:
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> list[KnowledgeSource]:
        stmt = select(KnowledgeSource).where(KnowledgeSource.workspace_id == workspace_id).order_by(KnowledgeSource.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        self.session.add(knowledge_source)
        await self.session.commit()
        await self.session.refresh(knowledge_source)
        return knowledge_source

    async def delete(self, knowledge_id: uuid.UUID) -> None:
        source = await self.get_by_id(knowledge_id)
        if source:
            await self.session.delete(source)
            await self.session.commit()
