"""
app/services/oauth/provider_base.py

Abstract base class for OAuth providers.
"""
from abc import ABC, abstractmethod
from app.schemas.oauth import OAuthAuthorization, OAuthTokenResult, OAuthAccountIdentity

class AbstractOAuthProvider(ABC):
    """
    Abstract interface for platform-specific OAuth providers.
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name of the social platform (e.g., 'X', 'LINKEDIN')."""
        pass

    @abstractmethod
    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """
        Generate the OAuth authorization URL for the provider.
        
        Args:
            state: The cryptographically secure state token to include in the query.
            redirect_uri: The callback URI where the provider should redirect the user.
        """
        pass

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthTokenResult:
        """
        Exchange the OAuth authorization code for access and refresh tokens.
        """
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> OAuthTokenResult:
        """
        Exchange a refresh token for a new access token.
        """
        pass

    @abstractmethod
    async def revoke_token(self, access_token: str) -> None:
        """
        Revoke the access token.
        """
        pass

    @abstractmethod
    async def get_account_identity(self, access_token: str) -> OAuthAccountIdentity:
        """
        Use the access token to retrieve the authenticated user's profile identity.
        """
        pass
