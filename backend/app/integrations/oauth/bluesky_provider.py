"""
app/integrations/oauth/bluesky_provider.py

Bluesky concrete implementation of the OAuth provider abstraction.
"""
import logging
from typing import Optional
import httpx

from app.core.config import settings
from app.services.oauth.provider_base import AbstractOAuthProvider
from app.schemas.oauth import OAuthTokenResult, OAuthAccountIdentity

logger = logging.getLogger(__name__)

class BlueskyOAuthProvider(AbstractOAuthProvider):
    """
    Bluesky integration for OAuth.
    Uses AT Protocol OAuth or standard OAuth mappings to connect a Bluesky account.
    """

    def __init__(self):
        self.client_id = settings.BLUESKY_CLIENT_ID
        self.client_secret = settings.BLUESKY_CLIENT_SECRET
        # AT Protocol / Bluesky generally uses bsky.social for standard PDS, 
        # though standard OAuth for AT protocol requires discovering the PDS.
        # For this integration, we map to the standard bsky.social endpoints.
        self.auth_url = "https://bsky.social/oauth/authorize"
        self.token_url = "https://bsky.social/oauth/token"
        self.profile_url = "https://bsky.social/xrpc/app.bsky.actor.getProfile"

    @property
    def platform_name(self) -> str:
        return "BLUESKY"

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """
        Generate the Bluesky authorization URL.
        """
        # Note: AT Protocol OAuth requires PKCE and client metadata, 
        # but we use standard OAuth2 query params for the base flow abstraction.
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "atproto transition:generic"
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query_string}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthTokenResult:
        """
        Exchange the OAuth authorization code for tokens.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Bluesky token exchange failed: {response.text}")
                raise ValueError("Failed to exchange Bluesky authorization code")
                
            json_resp = response.json()
            return OAuthTokenResult(
                access_token=json_resp.get("access_token"),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=json_resp.get("expires_in"),
                scopes=json_resp.get("scope", "").split() if json_resp.get("scope") else []
            )

    async def refresh_token(self, refresh_token: str) -> OAuthTokenResult:
        """
        Exchange a refresh token for a new access token.
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Bluesky token refresh failed: {response.text}")
                raise ValueError("Failed to refresh Bluesky token")
                
            json_resp = response.json()
            return OAuthTokenResult(
                access_token=json_resp.get("access_token"),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=json_resp.get("expires_in")
            )

    async def revoke_token(self, access_token: str) -> None:
        """
        Revoke the access token. 
        Bluesky currently relies on token expiration or server-side session invalidation.
        We make a best-effort call if a revoke endpoint exists.
        """
        revoke_url = "https://bsky.social/oauth/revoke"
        data = {
            "token": access_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        async with httpx.AsyncClient() as client:
            # We ignore errors on revoke for best-effort
            await client.post(revoke_url, data=data)

    async def get_account_identity(self, access_token: str) -> OAuthAccountIdentity:
        """
        Retrieve the authenticated user's profile identity.
        In AT protocol, the token often contains the DID, or we can fetch the user's session.
        Since we need a DID to call getProfile, we first get the session.
        """
        session_url = "https://bsky.social/xrpc/com.atproto.server.getSession"
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            session_resp = await client.get(session_url, headers=headers)
            
            if session_resp.status_code != 200:
                logger.error(f"Bluesky get session failed: {session_resp.text}")
                raise ValueError("Failed to fetch Bluesky session")
                
            session_data = session_resp.json()
            did = session_data.get("did")
            handle = session_data.get("handle")
            
            # Fetch full profile
            profile_resp = await client.get(
                self.profile_url, 
                params={"actor": did}, 
                headers=headers
            )
            
            display_name = handle
            if profile_resp.status_code == 200:
                profile_data = profile_resp.json()
                display_name = profile_data.get("displayName") or handle
                
            return OAuthAccountIdentity(
                platform_user_id=did,
                username=handle,
                display_name=display_name,
                profile_url=f"https://bsky.app/profile/{handle}",
                metadata={"did": did}
            )
