import uuid
from abc import ABC, abstractmethod

from app.models.automation_rule import AutomationRule

class AutomationRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, rule: AutomationRule) -> AutomationRule:
        pass

    @abstractmethod
    async def get_by_id(self, rule_id: uuid.UUID) -> AutomationRule | None:
        pass

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> list[AutomationRule]:
        pass

    @abstractmethod
    async def get_all_active(self) -> list[AutomationRule]:
        pass

    @abstractmethod
    async def update(self, rule: AutomationRule) -> AutomationRule:
        pass

    @abstractmethod
    async def delete(self, rule_id: uuid.UUID) -> None:
        pass
