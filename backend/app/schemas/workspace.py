import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    """Schema for creating a new workspace."""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="The display name of the workspace."
    )
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-safe slug for the workspace: lowercase letters, numbers, and hyphens only.",
    )
    description: Optional[str] = Field(
        None, 
        max_length=2000, 
        description="Optional detailed description of the workspace and its purpose."
    )
    logo_url: Optional[str] = Field(
        None, 
        max_length=2048, 
        description="Optional URL pointing to the workspace's logo image."
    )
    timezone: str = Field(
        "UTC", 
        max_length=100, 
        description="The primary timezone for the workspace."
    )


class WorkspaceUpdate(BaseModel):
    """Schema for updating an existing workspace. All fields are optional."""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255, 
        description="New display name for the workspace."
    )
    description: Optional[str] = Field(
        None, 
        max_length=2000, 
        description="New detailed description for the workspace."
    )
    logo_url: Optional[str] = Field(
        None, 
        max_length=2048, 
        description="New URL pointing to the workspace's logo image."
    )
    timezone: Optional[str] = Field(
        None, 
        max_length=100, 
        description="New primary timezone for the workspace."
    )
    is_active: Optional[bool] = Field(
        None, 
        description="Toggle to activate or deactivate the workspace."
    )


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class WorkspaceResponse(BaseModel):
    """Full workspace response returned from API endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(description="Unique UUID identifier for the workspace.")
    name: str = Field(description="The display name of the workspace.")
    slug: str = Field(description="URL-safe slug for the workspace.")
    description: Optional[str] = Field(description="Detailed description of the workspace and its purpose.")
    owner_id: uuid.UUID = Field(description="UUID of the user who owns this workspace.")
    logo_url: Optional[str] = Field(description="URL pointing to the workspace's logo image.")
    timezone: str = Field(description="The primary timezone for the workspace.")
    is_active: bool = Field(description="Indicates whether the workspace is currently active.")
    created_at: datetime = Field(description="Timestamp indicating when the workspace was created.")
    updated_at: datetime = Field(description="Timestamp indicating when the workspace was last modified.")
