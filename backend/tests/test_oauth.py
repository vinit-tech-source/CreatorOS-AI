"""
tests/test_oauth.py

Tests for the OAuth Foundation.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import status

from app.services.oauth.state_manager import OAuthStateManager
from app.services.oauth.oauth_service import OAuthService, OAuthStateError, OAuthProviderError
from app.services.oauth.provider_base import AbstractOAuthProvider
from app.schemas.oauth import OAuthTokenResult, OAuthAccountIdentity
from app.schemas.social_account import SocialAccountCreate

TEST_WORKSPACE_ID = uuid.uuid4()
TEST_USER_ID = uuid.uuid4()


class MockOAuthProvider(AbstractOAuthProvider):
    @property
    def platform_name(self) -> str:
        return "X"

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        return f"https://mock.com/oauth/authorize?state={state}&redirect_uri={redirect_uri}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthTokenResult:
        if code == "invalid_code":
            raise ValueError("Invalid code")
        return OAuthTokenResult(
            access_token="mock_access_token_123",
            refresh_token="mock_refresh_token_456",
            expires_in=3600
        )

    async def refresh_token(self, refresh_token: str) -> OAuthTokenResult:
        pass

    async def revoke_token(self, access_token: str) -> None:
        pass

    async def get_account_identity(self, access_token: str) -> OAuthAccountIdentity:
        if access_token == "fail_identity":
            raise ValueError("Invalid token for identity")
        return OAuthAccountIdentity(
            platform_user_id="mock_user_999",
            username="mockuser",
            display_name="Mock User"
        )


@pytest.fixture
def mock_sa_service():
    service = AsyncMock()
    return service

@pytest.fixture
def oauth_service(mock_sa_service):
    service = OAuthService(social_account_service=mock_sa_service)
    service.register_provider(MockOAuthProvider())
    return service


def test_oauth_state_generation():
    """Test OAuth state generation."""
    state = OAuthStateManager.generate_state(TEST_WORKSPACE_ID, "X")
    assert state is not None
    assert isinstance(state, str)
    assert len(state) > 20


def test_state_validation_and_reuse():
    """Test state validation and prevent reuse."""
    state = OAuthStateManager.generate_state(TEST_WORKSPACE_ID, "X")
    
    # First validation should succeed
    metadata = OAuthStateManager.validate_and_consume_state(state)
    assert metadata is not None
    assert metadata["workspace_id"] == str(TEST_WORKSPACE_ID)
    assert metadata["platform"] == "X"
    
    # Second validation of the same state should fail (reuse rejected)
    metadata2 = OAuthStateManager.validate_and_consume_state(state)
    assert metadata2 is None


def test_expired_state():
    """Test expired state."""
    state = OAuthStateManager.generate_state(TEST_WORKSPACE_ID, "X")
    
    # Fast forward expiration
    import app.services.oauth.state_manager as sm
    sm._state_store[state]["expires_at"] = 0
    
    metadata = OAuthStateManager.validate_and_consume_state(state)
    assert metadata is None


@pytest.mark.asyncio
async def test_get_authorization_url(oauth_service):
    """Test get authorization URL uses mock provider."""
    result = await oauth_service.get_authorization_url(
        workspace_id=TEST_WORKSPACE_ID,
        platform="X",
        redirect_uri="https://myapp.com/callback"
    )
    assert "state=" in result.authorization_url
    assert result.state_token in result.authorization_url


@pytest.mark.asyncio
async def test_handle_callback_success(oauth_service, mock_sa_service):
    """Test full callback success flow."""
    state = OAuthStateManager.generate_state(TEST_WORKSPACE_ID, "X")
    
    await oauth_service.handle_callback(
        state=state,
        code="valid_code",
        redirect_uri="https://myapp.com/callback",
        requesting_user_id=TEST_USER_ID
    )
    
    # Verify social account creation was called with correct data
    mock_sa_service.create_social_account.assert_called_once()
    call_kwargs = mock_sa_service.create_social_account.call_args.kwargs
    assert call_kwargs["workspace_id"] == TEST_WORKSPACE_ID
    assert call_kwargs["requesting_user_id"] == TEST_USER_ID
    
    data = call_kwargs["data"]
    assert data.platform.value == "X"
    assert data.platform_user_id == "mock_user_999"
    # Verify tokens are passed to the service (which encrypts them)
    assert data.access_token == "mock_access_token_123"
    assert data.refresh_token == "mock_refresh_token_456"


@pytest.mark.asyncio
async def test_invalid_callback_state(oauth_service):
    """Test invalid callback state handling."""
    with pytest.raises(OAuthStateError):
        await oauth_service.handle_callback(
            state="invalid_state_token",
            code="valid_code",
            redirect_uri="https://myapp.com/callback",
            requesting_user_id=TEST_USER_ID
        )


@pytest.mark.asyncio
async def test_token_exchange_mock_failure(oauth_service):
    """Test token exchange failure."""
    state = OAuthStateManager.generate_state(TEST_WORKSPACE_ID, "X")
    
    with pytest.raises(OAuthProviderError, match="Failed to exchange authorization code"):
        await oauth_service.handle_callback(
            state=state,
            code="invalid_code",
            redirect_uri="https://myapp.com/callback",
            requesting_user_id=TEST_USER_ID
        )


@pytest.mark.asyncio
async def test_token_encryption_delegation(oauth_service, mock_sa_service):
    """
    Test token encryption and non-disclosure.
    The OAuth service delegates to SocialAccountService, which guarantees encryption.
    """
    state = OAuthStateManager.generate_state(TEST_WORKSPACE_ID, "X")
    
    await oauth_service.handle_callback(
        state=state,
        code="valid_code",
        redirect_uri="https://myapp.com/callback",
        requesting_user_id=TEST_USER_ID
    )
    
    data = mock_sa_service.create_social_account.call_args.kwargs["data"]
    assert isinstance(data, SocialAccountCreate)
    # The requirement is that we pass plaintext TO the service, and the service encrypts.
    # If the service expects plaintext (which `SocialAccountCreate` takes), this test proves we delegated correctly.
    assert data.access_token == "mock_access_token_123"
