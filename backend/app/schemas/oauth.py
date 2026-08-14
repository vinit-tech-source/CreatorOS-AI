"""
app/schemas/oauth.py

Typed schemas for OAuth provider interactions.
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class OAuthAuthorization(BaseModel):
    """Result of generating an authorization URL."""
    authorization_url: str = Field(..., description="The URL to redirect the user to")
    state_token: str = Field(..., description="The CSRF protection state string")


class OAuthTokenResult(BaseModel):
    """Normalized response from an OAuth token exchange."""
    access_token: str = Field(..., description="The access token string")
    refresh_token: Optional[str] = Field(None, description="The refresh token string, if provided")
    expires_in: Optional[int] = Field(None, description="Seconds until the access token expires")
    scopes: Optional[List[str]] = Field(None, description="Scopes granted by the user")


class OAuthAccountIdentity(BaseModel):
    """Normalized identity of the social account retrieved from the provider after OAuth."""
    platform_user_id: str = Field(..., description="The unique ID of the user on the provider platform")
    username: str = Field(..., description="The handle or username")
    display_name: str = Field(..., description="The display name of the account")
    profile_url: Optional[str] = Field(None, description="URL to the user's profile")
    metadata: Optional[dict] = Field(None, description="Additional provider-specific metadata")
