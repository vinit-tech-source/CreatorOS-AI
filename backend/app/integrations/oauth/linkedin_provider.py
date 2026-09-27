"""
app/integrations/oauth/linkedin_provider.py

LinkedIn OAuth 2.0 provider.

Uses LinkedIn's standard OAuth 2.0 Authorization Code Flow.
Docs: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow

Required env vars:
    LINKEDIN_CLIENT_ID      — from LinkedIn Developer Portal
    LINKEDIN_CLIENT_SECRET  — from LinkedIn Developer Portal
    LINKEDIN_ENABLED=true   — feature flag
"""
import logging

import httpx

from app.core.config import settings
from app.services.oauth.provider_base import AbstractOAuthProvider
from app.schemas.oauth import OAuthTokenResult, OAuthAccountIdentity

logger = logging.getLogger(__name__)


class LinkedInOAuthProvider(AbstractOAuthProvider):
    """
    LinkedIn OAuth 2.0 Authorization Code Flow.
    Requires: openid, profile, email, w_member_social scopes.
    """

    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    REVOKE_URL = "https://www.linkedin.com/oauth/v2/revoke"
    PROFILE_URL = "https://api.linkedin.com/v2/userinfo"

    SCOPES = "openid profile email w_member_social"

    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET

    @property
    def platform_name(self) -> str:
        return "LINKEDIN"

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Build the LinkedIn OAuth2 authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.SCOPES,
            "state": state,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthTokenResult:
        """Exchange authorization code for LinkedIn access token."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code != 200:
                logger.error(f"LinkedIn token exchange failed ({response.status_code}): {response.text}")
                raise ValueError(f"LinkedIn token exchange failed: {response.text}")

            json_resp = response.json()
            return OAuthTokenResult(
                access_token=json_resp.get("access_token"),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=json_resp.get("expires_in"),
                scopes=self.SCOPES.split(),
            )

    async def refresh_token(self, refresh_token: str) -> OAuthTokenResult:
        """Refresh a LinkedIn access token."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code != 200:
                logger.error(f"LinkedIn token refresh failed: {response.text}")
                raise ValueError("Failed to refresh LinkedIn token")

            json_resp = response.json()
            return OAuthTokenResult(
                access_token=json_resp.get("access_token"),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=json_resp.get("expires_in"),
            )

    async def revoke_token(self, access_token: str) -> None:
        """Revoke a LinkedIn access token."""
        async with httpx.AsyncClient() as client:
            await client.post(
                self.REVOKE_URL,
                data={
                    "token": access_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    async def get_account_identity(self, access_token: str) -> OAuthAccountIdentity:
        """Retrieve the authenticated LinkedIn member's profile via OpenID Connect userinfo."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.PROFILE_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code != 200:
                logger.error(f"LinkedIn get profile failed: {response.text}")
                raise ValueError("Failed to fetch LinkedIn user identity")

            data = response.json()
            sub = data.get("sub")          # LinkedIn member URN / unique ID
            name = data.get("name", "")
            given_name = data.get("given_name", "")
            family_name = data.get("family_name", "")
            email = data.get("email", "")

            display_name = name or f"{given_name} {family_name}".strip() or email

            return OAuthAccountIdentity(
                platform_user_id=sub,
                username=email or sub,
                display_name=display_name,
                profile_url=f"https://www.linkedin.com/in/{sub}",
                metadata={"email": email},
            )
