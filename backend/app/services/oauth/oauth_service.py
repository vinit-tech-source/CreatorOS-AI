"""
app/services/oauth/oauth_service.py

Service for orchestrating the OAuth flow.
"""
import uuid
import logging
from typing import Dict

from app.core.exceptions import AppException
from fastapi import status

from app.services.oauth.provider_base import AbstractOAuthProvider
from app.services.oauth.state_manager import OAuthStateManager
from app.services.social_account_service import SocialAccountService
from app.schemas.social_account import SocialAccountCreate
from app.models.social_account import SocialPlatform
from app.schemas.oauth import OAuthAuthorization

logger = logging.getLogger(__name__)

class OAuthError(AppException):
    """Base class for OAuth errors."""
    pass

class OAuthStateError(OAuthError):
    def __init__(self, message: str = "Invalid or expired OAuth state"):
        super().__init__(message)

class OAuthProviderError(OAuthError):
    def __init__(self, message: str = "OAuth provider error"):
        super().__init__(message)


class OAuthService:
    """
    Orchestrates OAuth flows in a provider-agnostic way.
    """
    
    def __init__(self, social_account_service: SocialAccountService):
        self._sa_service = social_account_service
        self._providers: Dict[str, AbstractOAuthProvider] = {}
        
    def register_provider(self, provider: AbstractOAuthProvider) -> None:
        """Register a provider by its platform name."""
        self._providers[provider.platform_name.upper()] = provider
        
    def get_provider(self, platform: str) -> AbstractOAuthProvider:
        """Retrieve a registered provider."""
        provider = self._providers.get(platform.upper())
        if not provider:
            raise OAuthProviderError(f"OAuth provider for platform '{platform}' not configured.")
        return provider

    async def get_authorization_url(self, workspace_id: uuid.UUID, platform: str, redirect_uri: str) -> OAuthAuthorization:
        """
        Start the OAuth flow by generating a secure state and authorization URL.
        """
        provider = self.get_provider(platform)
        state = OAuthStateManager.generate_state(workspace_id=workspace_id, platform=platform)
        
        try:
            url = await provider.get_authorization_url(state=state, redirect_uri=redirect_uri)
        except Exception as e:
            logger.error(f"Failed to generate authorization URL for {platform}: {e}")
            raise OAuthProviderError("Failed to initiate OAuth flow.")
            
        return OAuthAuthorization(authorization_url=url, state_token=state)

    async def handle_callback(
        self, 
        state: str, 
        code: str, 
        redirect_uri: str, 
        requesting_user_id: uuid.UUID
    ) -> None:
        """
        Handle the OAuth callback:
        1. Validate State
        2. Exchange Code
        3. Get Identity
        4. Create Social Account
        """
        # 1. Validate State
        metadata = OAuthStateManager.validate_and_consume_state(state)
        if not metadata:
            raise OAuthStateError("Invalid, expired, or reused OAuth state.")
            
        platform = metadata["platform"]
        workspace_id_str = metadata["workspace_id"]
        workspace_id = uuid.UUID(workspace_id_str)
        
        provider = self.get_provider(platform)
        
        # 2. Exchange Code
        try:
            token_result = await provider.exchange_code(code=code, redirect_uri=redirect_uri)
        except Exception as e:
            logger.error(f"OAuth token exchange failed for {platform}: {e}")
            raise OAuthProviderError("Failed to exchange authorization code.")
            
        # 3. Get Account Identity
        try:
            identity = await provider.get_account_identity(access_token=token_result.access_token)
        except Exception as e:
            logger.error(f"OAuth identity fetch failed for {platform}: {e}")
            # Attempt to revoke token if identity fails to prevent dangling tokens
            try:
                await provider.revoke_token(token_result.access_token)
            except Exception:
                pass
            raise OAuthProviderError("Failed to fetch social account profile.")
            
        # 4. Create Social Account
        try:
            enum_platform = SocialPlatform(platform.upper())
        except ValueError:
            raise OAuthProviderError(f"Unsupported platform enum mapping for '{platform}'")
            
        create_data = SocialAccountCreate(
            platform=enum_platform,
            platform_user_id=identity.platform_user_id,
            account_name=identity.display_name or identity.username,
            access_token=token_result.access_token,
            refresh_token=token_result.refresh_token
        )
        
        # The service handles encrypting the tokens and validating workspace ownership
        await self._sa_service.create_social_account(
            workspace_id=workspace_id,
            data=create_data,
            requesting_user_id=requesting_user_id
        )
        logger.info(f"Successfully connected {platform} account for workspace {workspace_id}")
