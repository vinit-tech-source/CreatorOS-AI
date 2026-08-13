"""
app/schemas/social_account.py

Pydantic v2 schemas for SocialAccount request/response payloads.

SECURITY: access_token_encrypted and refresh_token_encrypted are NEVER
included in any response schema. The response surfaces only safe metadata.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.social_account import SocialPlatform


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class SocialAccountCreate(BaseModel):
    """
    Schema for creating (connecting) a new social media account.

    The access_token and refresh_token fields accept plaintext values from
    the caller (e.g. from an OAuth callback handler). The service layer will
    encrypt these before persistence. They must never appear in any response.
    """
    platform: SocialPlatform = Field(description="The social media platform.")
    account_name: str = Field(
        ..., min_length=1, max_length=255, description="Display name for the account."
    )
    platform_user_id: str = Field(
        ..., min_length=1, max_length=255, description="The unique user ID on the platform."
    )
    access_token: str = Field(
        ..., min_length=1, description="OAuth access token (will be encrypted before storage)."
    )
    refresh_token: Optional[str] = Field(
        None, description="OAuth refresh token (will be encrypted before storage)."
    )
    token_expires_at: Optional[datetime] = Field(
        None, description="UTC timestamp when the access token expires."
    )
    scopes: Optional[str] = Field(
        None, max_length=2000, description="Granted OAuth scopes as a space-separated string."
    )


class SocialAccountUpdate(BaseModel):
    """
    Schema for updating social account metadata.

    All fields are optional.

    IMPORTANT: Updating tokens should go through a dedicated token-refresh
    flow, not a general PATCH. This schema intentionally excludes token fields
    to prevent accidental token exposure through the update path.

    Null handling:
      - Omitted field  -> left unchanged (exclude_unset in repository)
      - Explicit null  -> clears the nullable field
    """
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    token_expires_at: Optional[datetime] = Field(None)
    scopes: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = Field(None)


# ─────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────

class SocialAccountResponse(BaseModel):
    """
    Safe social account metadata returned from API endpoints.

    SECURITY: access_token_encrypted and refresh_token_encrypted are
    deliberately excluded. No token data of any kind is surfaced here.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(description="Unique UUID identifier.")
    workspace_id: uuid.UUID = Field(description="Workspace this account belongs to.")
    platform: SocialPlatform = Field(description="Social media platform.")
    account_name: str = Field(description="Display name of the connected account.")
    platform_user_id: str = Field(description="Platform-assigned user identifier.")
    token_expires_at: Optional[datetime] = Field(description="When the access token expires.")
    scopes: Optional[str] = Field(description="Granted OAuth scopes.")
    is_active: bool = Field(description="Whether the account connection is active.")
    connected_at: datetime = Field(description="When this account was first connected.")
    updated_at: datetime = Field(description="When this record was last updated.")
