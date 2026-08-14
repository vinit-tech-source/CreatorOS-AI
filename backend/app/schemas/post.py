"""
app/schemas/post.py

Pydantic v2 schemas for Content Post request/response payloads.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.post import ContentType, PostStatus
from app.models.social_account import SocialPlatform


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class PostCreate(BaseModel):
    """Schema for creating a new Content Post."""

    title: Optional[str] = Field(None, max_length=255, description="Optional title.")
    content: str = Field(..., min_length=1, description="The actual post content.")
    content_type: ContentType = Field(description="Type of content.")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Initial post status.")
    platform: SocialPlatform = Field(description="Target social platform.")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time.")


class PostUpdate(BaseModel):
    """Schema for partially updating a Content Post.

    All fields are optional.
    Null handling:
      - Omitted field  -> left unchanged (exclude_unset semantics in repository)
      - Explicit null  -> clears the nullable field
    """

    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[ContentType] = Field(None)
    status: Optional[PostStatus] = Field(None)
    platform: Optional[SocialPlatform] = Field(None)
    scheduled_at: Optional[datetime] = Field(None)
    # Note: published_at and external_post_id should typically be updated
    # by the publishing worker, but we allow it here for administrative overrides.
    published_at: Optional[datetime] = Field(None)
    external_post_id: Optional[str] = Field(None)
    
    # Approval fields
    approval_status: Optional[str] = Field(None)
    approved_by: Optional[uuid.UUID] = Field(None)
    approved_at: Optional[datetime] = Field(None)
    rejection_reason: Optional[str] = Field(None)

class PostReject(BaseModel):
    """Schema for rejecting a post."""
    rejection_reason: str = Field(..., min_length=1, description="Reason for rejection.")


# ─────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────

class PostResponse(BaseModel):
    """Full Post response returned from API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: Optional[str]
    content: str
    content_type: ContentType
    status: PostStatus
    platform: SocialPlatform
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    external_post_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Approval fields
    approval_status: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
