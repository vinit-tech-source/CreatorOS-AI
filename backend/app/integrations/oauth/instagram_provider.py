"""
app/integrations/oauth/instagram_provider.py

Instagram OAuth 2.0 provider via Meta's Graph API.

Uses the Facebook Login / Instagram Graph API OAuth 2.0 flow.
Docs: https://developers.facebook.com/docs/instagram-api/getting-started

Required env vars:
    INSTAGRAM_CLIENT_ID      — Meta App ID
    INSTAGRAM_CLIENT_SECRET  — Meta App Secret
    INSTAGRAM_ENABLED=true   — feature flag

Note: Instagram requires a Facebook Page linked to a Business/Creator Instagram account.
Personal Instagram accounts cannot use the Graph API.
"""
import logging

import httpx

from app.core.config import settings
from app.services.oauth.provider_base import AbstractOAuthProvider
from app.schemas.oauth import OAuthTokenResult, OAuthAccountIdentity

logger = logging.getLogger(__name__)


class InstagramOAuthProvider(AbstractOAuthProvider):
    """
    Instagram OAuth 2.0 via Meta Graph API (Facebook Login flow).

    Scopes requested:
        instagram_basic            — read profile and media
        instagram_content_publish  — publish photos/videos
        pages_read_engagement      — read page metrics
        pages_show_list            — list linked Facebook pages
    """

    AUTH_URL = "https://www.facebook.com/v19.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
    LONG_LIVED_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
    ME_URL = "https://graph.facebook.com/v19.0/me"

    SCOPES = (
        "instagram_basic,instagram_content_publish,"
        "pages_read_engagement,pages_show_list"
    )

    def __init__(self):
        self.client_id = settings.INSTAGRAM_CLIENT_ID
        self.client_secret = settings.INSTAGRAM_CLIENT_SECRET

    @property
    def platform_name(self) -> str:
        return "INSTAGRAM"

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Build the Facebook Login OAuth2 authorization URL for Instagram access."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.SCOPES,
            "response_type": "code",
            "state": state,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthTokenResult:
        """
        Exchange the authorization code for a short-lived token,
        then upgrade to a long-lived token (60-day expiry).
        """
        # Step 1: Short-lived token
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.TOKEN_URL, params=params)
            if response.status_code != 200:
                logger.error(f"Instagram token exchange failed ({response.status_code}): {response.text}")
                raise ValueError(f"Instagram token exchange failed: {response.text}")

            short_token = response.json().get("access_token")

            # Step 2: Upgrade to long-lived token
            ll_response = await client.get(
                self.LONG_LIVED_URL,
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "fb_exchange_token": short_token,
                },
            )
            if ll_response.status_code != 200:
                logger.warning(f"Instagram long-lived token upgrade failed: {ll_response.text}. Using short-lived token.")
                return OAuthTokenResult(
                    access_token=short_token,
                    refresh_token=None,
                    expires_in=3600,
                    scopes=self.SCOPES.split(","),
                )

            ll_data = ll_response.json()
            return OAuthTokenResult(
                access_token=ll_data.get("access_token", short_token),
                refresh_token=None,  # Meta long-lived tokens don't use refresh tokens
                expires_in=ll_data.get("expires_in", 5183944),  # ~60 days
                scopes=self.SCOPES.split(","),
            )

    async def refresh_token(self, refresh_token: str) -> OAuthTokenResult:
        """
        Meta Graph API long-lived tokens can be refreshed by requesting a new
        long-lived token using the existing one (before it expires).
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.LONG_LIVED_URL,
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "fb_exchange_token": refresh_token,  # use old access token as exchange token
                },
            )
            if response.status_code != 200:
                logger.error(f"Instagram token refresh failed: {response.text}")
                raise ValueError("Failed to refresh Instagram token")

            data = response.json()
            return OAuthTokenResult(
                access_token=data.get("access_token"),
                refresh_token=None,
                expires_in=data.get("expires_in", 5183944),
            )

    async def revoke_token(self, access_token: str) -> None:
        """Revoke a Meta access token (best-effort)."""
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"https://graph.facebook.com/v19.0/me/permissions",
                params={"access_token": access_token},
            )

    async def get_account_identity(self, access_token: str) -> OAuthAccountIdentity:
        """
        Retrieve Instagram Business account identity.
        First gets the Facebook user, then finds the linked Instagram Business account.
        """
        async with httpx.AsyncClient() as client:
            # Get Facebook user info
            fb_response = await client.get(
                self.ME_URL,
                params={
                    "fields": "id,name,accounts{instagram_business_account{id,name,username}}",
                    "access_token": access_token,
                },
            )
            if fb_response.status_code != 200:
                logger.error(f"Instagram get identity failed: {fb_response.text}")
                raise ValueError("Failed to fetch Instagram user identity")

            fb_data = fb_response.json()
            fb_name = fb_data.get("name", "")

            # Try to get the linked Instagram Business account
            ig_account = None
            accounts = fb_data.get("accounts", {}).get("data", [])
            for page in accounts:
                ig = page.get("instagram_business_account")
                if ig:
                    ig_account = ig
                    break

            if ig_account:
                ig_id = ig_account.get("id")
                ig_username = ig_account.get("username", "")
                ig_name = ig_account.get("name", fb_name)
                return OAuthAccountIdentity(
                    platform_user_id=ig_id,
                    username=ig_username,
                    display_name=ig_name,
                    profile_url=f"https://www.instagram.com/{ig_username}",
                    metadata={"facebook_user_id": fb_data.get("id")},
                )
            else:
                # Fallback to Facebook user identity
                fb_id = fb_data.get("id")
                return OAuthAccountIdentity(
                    platform_user_id=fb_id,
                    username=fb_id,
                    display_name=fb_name,
                    profile_url="https://www.instagram.com",
                    metadata={"facebook_user_id": fb_id, "warning": "No Instagram Business account linked"},
                )
