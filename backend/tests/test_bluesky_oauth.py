"""
tests/test_bluesky_oauth.py

Tests for the Bluesky OAuth provider implementation.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.integrations.oauth.bluesky_provider import BlueskyOAuthProvider

@pytest.fixture
def bluesky_provider():
    return BlueskyOAuthProvider()

def test_platform_name(bluesky_provider):
    """Test platform name is BLUESKY."""
    assert bluesky_provider.platform_name == "BLUESKY"

@pytest.mark.asyncio
async def test_get_authorization_url(bluesky_provider):
    """Test authorization URL generation."""
    url = await bluesky_provider.get_authorization_url(
        state="mock_state_123",
        redirect_uri="https://myapp.com/callback"
    )
    
    assert "bsky.social/oauth/authorize" in url
    assert "state=mock_state_123" in url
    assert "redirect_uri=https://myapp.com/callback" in url
    assert "response_type=code" in url


@pytest.mark.asyncio
@patch("app.integrations.oauth.bluesky_provider.httpx.AsyncClient.post")
async def test_exchange_code(mock_post, bluesky_provider):
    """Test successful token exchange."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={
        "access_token": "acc_123",
        "refresh_token": "ref_456",
        "expires_in": 3600,
        "scope": "atproto"
    })
    mock_post.return_value = mock_resp
    
    result = await bluesky_provider.exchange_code(
        code="mock_code",
        redirect_uri="https://myapp.com/callback"
    )
    
    assert result.access_token == "acc_123"
    assert result.refresh_token == "ref_456"
    assert result.expires_in == 3600
    assert "atproto" in result.scopes
    
    # Verify post was called with correct args
    args, kwargs = mock_post.call_args
    data = kwargs["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "mock_code"


@pytest.mark.asyncio
@patch("app.integrations.oauth.bluesky_provider.httpx.AsyncClient.post")
async def test_exchange_code_failure(mock_post, bluesky_provider):
    """Test token exchange failure."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 400
    mock_resp.text = "Invalid code"
    mock_post.return_value = mock_resp
    
    with pytest.raises(ValueError, match="Failed to exchange"):
        await bluesky_provider.exchange_code(
            code="invalid_code",
            redirect_uri="https://myapp.com/callback"
        )


@pytest.mark.asyncio
@patch("app.integrations.oauth.bluesky_provider.httpx.AsyncClient.post")
async def test_refresh_token(mock_post, bluesky_provider):
    """Test refresh token."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={
        "access_token": "acc_123_new",
        "refresh_token": "ref_456_new",
        "expires_in": 3600
    })
    mock_post.return_value = mock_resp
    
    result = await bluesky_provider.refresh_token("old_refresh")
    
    assert result.access_token == "acc_123_new"
    
    args, kwargs = mock_post.call_args
    data = kwargs["data"]
    assert data["grant_type"] == "refresh_token"
    assert data["refresh_token"] == "old_refresh"


@pytest.mark.asyncio
@patch("app.integrations.oauth.bluesky_provider.httpx.AsyncClient.post")
async def test_revoke_token(mock_post, bluesky_provider):
    """Test revoke token is best effort."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp
    
    # Should not raise exception
    await bluesky_provider.revoke_token("acc_123")
    
    args, kwargs = mock_post.call_args
    data = kwargs["data"]
    assert data["token"] == "acc_123"


@pytest.mark.asyncio
@patch("app.integrations.oauth.bluesky_provider.httpx.AsyncClient.get")
async def test_get_account_identity(mock_get, bluesky_provider):
    """Test retrieving account identity using two consecutive calls."""
    
    # Setup multiple side effects for the two requests:
    # 1. getSession
    # 2. getProfile
    mock_session_resp = AsyncMock()
    mock_session_resp.status_code = 200
    mock_session_resp.json = MagicMock(return_value={
        "did": "did:plc:12345",
        "handle": "test.bsky.social"
    })
    
    mock_profile_resp = AsyncMock()
    mock_profile_resp.status_code = 200
    mock_profile_resp.json = MagicMock(return_value={
        "displayName": "Test User"
    })
    
    mock_get.side_effect = [mock_session_resp, mock_profile_resp]
    
    identity = await bluesky_provider.get_account_identity("acc_123")
    
    assert identity.platform_user_id == "did:plc:12345"
    assert identity.username == "test.bsky.social"
    assert identity.display_name == "Test User"
    assert "test.bsky.social" in identity.profile_url


@pytest.mark.asyncio
@patch("app.integrations.oauth.bluesky_provider.httpx.AsyncClient.get")
async def test_get_account_identity_failure(mock_get, bluesky_provider):
    """Test identity fetch failure on session call."""
    mock_session_resp = AsyncMock()
    mock_session_resp.status_code = 401
    mock_get.return_value = mock_session_resp
    
    with pytest.raises(ValueError, match="Failed to fetch"):
        await bluesky_provider.get_account_identity("invalid_token")
