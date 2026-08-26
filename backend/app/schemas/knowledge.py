import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class KnowledgeSourceBase(BaseModel):
    name: str = Field(..., max_length=255)
    source_type: str = Field(..., max_length=50) # TEXT, URL
    content: str

class KnowledgeSourceCreate(KnowledgeSourceBase):
    pass

class KnowledgeSourceResponse(KnowledgeSourceBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
