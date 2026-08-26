import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation_rule import AutomationRule
from app.repositories.automation_repository_interface import AutomationRepositoryInterface

class AutomationRepository(AutomationRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, rule: AutomationRule) -> AutomationRule:
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: uuid.UUID) -> AutomationRule | None:
        stmt = select(AutomationRule).where(AutomationRule.id == rule_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> list[AutomationRule]:
        stmt = select(AutomationRule).where(AutomationRule.workspace_id == workspace_id).order_by(AutomationRule.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_all_active(self) -> list[AutomationRule]:
        stmt = select(AutomationRule).where(AutomationRule.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, rule: AutomationRule) -> AutomationRule:
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete(self, rule_id: uuid.UUID) -> None:
        rule = await self.get_by_id(rule_id)
        if rule:
            await self.session.delete(rule)
            await self.session.commit()
