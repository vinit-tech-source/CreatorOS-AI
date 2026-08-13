"""
app/schemas/project.py

Pydantic v2 schemas for Content Project request/response payloads.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.project import ProjectStatus


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """Schema for creating a new Content Project."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Project name."
    )
    slug: str = Field(
        ...,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="Workspace-unique URL-friendly identifier (lowercase letters, numbers, hyphens).",
    )
    description: Optional[str] = Field(None, description="Optional project description.")
    status: ProjectStatus = Field(
        default=ProjectStatus.DRAFT, description="Initial project status."
    )
    objective: Optional[str] = Field(None, description="High-level objective.")
    target_audience: Optional[str] = Field(None, description="Intended audience.")
    start_date: Optional[datetime] = Field(None, description="Optional start date.")
    end_date: Optional[datetime] = Field(None, description="Optional end date.")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: Optional[datetime], info) -> Optional[datetime]:
        """Ensure end_date is not earlier than start_date."""
        start_date = info.data.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return end_date


class ProjectUpdate(BaseModel):
    """Schema for partially updating a Content Project.

    All fields are optional.

    Null handling:
      - Omitted field  -> left unchanged (exclude_unset semantics in repository)
      - Explicit null  -> clears the nullable field
    """

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(
        None, min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$"
    )
    description: Optional[str] = Field(None)
    status: Optional[ProjectStatus] = Field(None)
    objective: Optional[str] = Field(None)
    target_audience: Optional[str] = Field(None)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    is_active: Optional[bool] = Field(None)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: Optional[datetime], info) -> Optional[datetime]:
        """Ensure end_date is not earlier than start_date if both are provided in the update."""
        start_date = info.data.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return end_date


# ─────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────

class ProjectResponse(BaseModel):
    """Full Project response returned from API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    status: ProjectStatus
    objective: Optional[str]
    target_audience: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
