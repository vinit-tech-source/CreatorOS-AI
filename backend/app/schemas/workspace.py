import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    """Schema for creating a new workspace."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-safe slug: lowercase letters, numbers, and hyphens only.",
    )
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = Field(None, max_length=2048)
    timezone: str = Field("UTC", max_length=100)


class WorkspaceUpdate(BaseModel):
    """Schema for updating an existing workspace. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = Field(None, max_length=2048)
    timezone: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class WorkspaceResponse(BaseModel):
    """Full workspace response returned from API endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    owner_id: uuid.UUID
    logo_url: Optional[str]
    timezone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
