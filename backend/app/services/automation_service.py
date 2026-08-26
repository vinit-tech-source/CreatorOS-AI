import uuid
from typing import List

from app.models.automation_rule import AutomationRule
from app.repositories.automation_repository_interface import AutomationRepositoryInterface
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.automation import AutomationRuleCreate
import logging

logger = logging.getLogger(__name__)

class AutomationService:
    def __init__(
        self,
        automation_repo: AutomationRepositoryInterface,
        workspace_repo: AbstractWorkspaceRepository,
    ):
        self.automation_repo = automation_repo
        self.workspace_repo = workspace_repo

    async def _verify_access(self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID) -> None:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace or workspace.owner_id != requesting_user_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or unauthorized.",
            )

    async def create_rule(
        self, workspace_id: uuid.UUID, data: AutomationRuleCreate, requesting_user_id: uuid.UUID
    ) -> AutomationRule:
        await self._verify_access(workspace_id, requesting_user_id)

        rule = AutomationRule(
            workspace_id=workspace_id,
            name=data.name,
            trigger_type=data.trigger_type,
            condition=data.condition,
            action_type=data.action_type,
            is_active=data.is_active,
        )
        return await self.automation_repo.create(rule)

    async def list_rules(
        self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> List[AutomationRule]:
        await self._verify_access(workspace_id, requesting_user_id)
        return await self.automation_repo.get_by_workspace_id(workspace_id)

    async def toggle_rule(
        self, workspace_id: uuid.UUID, rule_id: uuid.UUID, is_active: bool, requesting_user_id: uuid.UUID
    ) -> AutomationRule:
        await self._verify_access(workspace_id, requesting_user_id)
        
        rule = await self.automation_repo.get_by_id(rule_id)
        if not rule or rule.workspace_id != workspace_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found.",
            )
            
        rule.is_active = is_active
        return await self.automation_repo.update(rule)

    async def delete_rule(
        self, workspace_id: uuid.UUID, rule_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        await self._verify_access(workspace_id, requesting_user_id)
        
        rule = await self.automation_repo.get_by_id(rule_id)
        if not rule or rule.workspace_id != workspace_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found.",
            )
            
        await self.automation_repo.delete(rule_id)
