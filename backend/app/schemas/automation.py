import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AutomationRuleBase(BaseModel):
    name: str = Field(..., max_length=255)
    trigger_type: str = Field(..., max_length=100) # RSS_FEED_UPDATE, MENTION, etc
    condition: Optional[str] = None
    action_type: str = Field(..., max_length=100) # GENERATE_DRAFT
    is_active: bool = True

class AutomationRuleCreate(AutomationRuleBase):
    pass

class AutomationRuleResponse(AutomationRuleBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
