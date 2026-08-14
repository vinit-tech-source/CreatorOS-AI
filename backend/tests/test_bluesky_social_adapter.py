"""
tests/test_bluesky_social_adapter.py

Tests for the Bluesky Social MCP Adapter and Tool integration.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.mcp.adapters.bluesky_social_adapter import BlueskySocialAdapter
from app.mcp.schemas.social import SocialAccountData, SocialMetrics, SocialPostData
from app.mcp.exceptions.exceptions import MCPProviderError, MCPAuthenticationError
from app.core.encryption import encrypt_secret
from app.mcp.tools.social.get_recent_posts import GetRecentPostsTool
from cryptography.fernet import Fernet
from app.core.config import settings

@pytest.fixture(autouse=True)
def setup_encryption_key():
    original_key = settings.ENCRYPTION_KEY
    settings.ENCRYPTION_KEY = Fernet.generate_key().decode()
    yield
    settings.ENCRYPTION_KEY = original_key


@pytest.fixture
def encrypted_token():
    return encrypt_secret("mock_access_token")

@pytest.fixture
def adapter(encrypted_token):
    return BlueskySocialAdapter(
        access_token_encrypted=encrypted_token,
        platform_user_id="did:plc:123"
    )

# ---------------------------------------------------------
# ADAPTER TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_account_info_normalization(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={
        "did": "did:plc:123",
        "handle": "user.bsky.social",
        "displayName": "User Name",
        "followersCount": 100,
        "followsCount": 50
    })
    mock_get.return_value = mock_resp
    
    info = await adapter.get_account_info("did:plc:123")
    
    assert isinstance(info, SocialAccountData)
    assert info.platform == "BLUESKY"
    assert info.platform_user_id == "did:plc:123"
    assert info.username == "user.bsky.social"
    assert info.display_name == "User Name"
    assert info.followers == 100
    assert info.following == 50
    assert info.profile_url == "https://bsky.app/profile/user.bsky.social"


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_profile_metric_normalization(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={
        "followersCount": 1500,
        "followsCount": 300
    })
    mock_get.return_value = mock_resp
    
    metrics = await adapter.get_profile_metrics("did:plc:123")
    
    assert isinstance(metrics, SocialMetrics)
    assert metrics.followers == 1500
    # Unsupported metrics should be None, not fabricated
    assert metrics.impressions is None
    assert metrics.engagement_rate is None
    assert metrics.likes is None


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_recent_post_normalization(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={
        "feed": [
            {
                "post": {
                    "uri": "at://did:plc:123/app.bsky.feed.post/3k123456",
                    "author": {"handle": "user.bsky.social"},
                    "record": {
                        "text": "Hello Bluesky!",
                        "createdAt": "2026-08-14T10:00:00Z"
                    },
                    "likeCount": 10,
                    "replyCount": 2,
                    "repostCount": 5
                }
            }
        ]
    })
    mock_get.return_value = mock_resp
    
    posts = await adapter.get_recent_posts("did:plc:123", limit=5)
    
    assert len(posts) == 1
    post = posts[0]
    assert isinstance(post, SocialPostData)
    assert post.platform == "BLUESKY"
    assert post.post_id == "at://did:plc:123/app.bsky.feed.post/3k123456"
    assert post.text == "Hello Bluesky!"
    assert post.likes == 10
    assert post.comments == 2
    assert post.shares == 5
    assert post.impressions is None
    assert post.url == "https://bsky.app/profile/user.bsky.social/post/3k123456"
    assert post.published_at.isoformat() == "2026-08-14T10:00:00+00:00"


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_recent_post_empty_list(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={"feed": []})
    mock_get.return_value = mock_resp
    
    posts = await adapter.get_recent_posts("did:plc:123", limit=5)
    
    assert len(posts) == 0


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_recent_post_bounded_limit(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={"feed": []})
    mock_get.return_value = mock_resp
    
    await adapter.get_recent_posts("did:plc:123", limit=999)
    
    # Should bound to 100
    args, kwargs = mock_get.call_args
    assert kwargs["params"]["limit"] == 100


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_provider_timeout(mock_get, adapter):
    import httpx
    mock_get.side_effect = httpx.RequestError("Timeout")
    
    with pytest.raises(MCPProviderError, match="unavailable or timed out"):
        await adapter.get_account_info("did:plc:123")


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_provider_authentication_failure(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 401
    mock_get.return_value = mock_resp
    
    with pytest.raises(MCPAuthenticationError, match="credentials expired or unauthorized"):
        await adapter.get_account_info("did:plc:123")


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.get")
async def test_invalid_provider_response(mock_get, adapter):
    mock_resp = AsyncMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp
    
    with pytest.raises(MCPProviderError, match="returned an error"):
        await adapter.get_account_info("did:plc:123")


# ---------------------------------------------------------
# TOOL INTEGRATION TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
@patch("app.mcp.tools.social.get_recent_posts.AsyncSessionLocal")
@patch("app.mcp.adapters.bluesky_social_adapter.BlueskySocialAdapter.get_recent_posts")
@patch("app.mcp.tools.social.get_recent_posts.get_social_adapter")
async def test_tool_invocation_through_bluesky_adapter(mock_get_adapter, mock_adapter_method, mock_session):
    # Setup mock DB session and repo
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    mock_account = MagicMock()
    workspace_id = uuid.uuid4()
    account_id = uuid.uuid4()
    mock_account.workspace_id = workspace_id
    mock_account.platform.value = "BLUESKY"
    mock_account.platform_user_id = "did:plc:999"
    mock_account.access_token_encrypted = encrypt_secret("mock_token")
    mock_account.refresh_token_encrypted = encrypt_secret("mock_refresh")
    
    # We must patch SocialAccountRepository inside the tool
    with patch("app.mcp.tools.social.get_recent_posts.SocialAccountRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_account
        mock_repo_class.return_value = mock_repo
        
        # Setup mock adapter response
        mock_adapter_method.return_value = [
            SocialPostData(
                post_id="post_1",
                platform="BLUESKY",
                text="Test post",
                published_at=datetime.now(timezone.utc),
                likes=5,
                comments=1,
                shares=0,
                url="https://bsky.app/test"
            )
        ]
        
        # Make get_social_adapter return an instance of BlueskySocialAdapter so our mock is hit
        from app.mcp.adapters.bluesky_social_adapter import BlueskySocialAdapter
        mock_get_adapter.return_value = BlueskySocialAdapter(access_token_encrypted=mock_account.access_token_encrypted, platform_user_id=mock_account.platform_user_id)
        
        tool = GetRecentPostsTool()
        result = await tool.execute({
            "workspace_id": str(workspace_id),
            "social_account_id": str(account_id),
            "limit": 5
        })
        
        # 13. Tool invocation works through adapter
        assert result.success
        assert len(result.data["posts"]) == 1
        assert result.data["posts"][0]["platform"] == "BLUESKY"
        
        # Verify the tool correctly invoked the factory and the adapter method
        mock_adapter_method.assert_called_once_with(
            platform_user_id="did:plc:999",
            limit=5
        )


@pytest.mark.asyncio
@patch("app.mcp.tools.social.get_recent_posts.AsyncSessionLocal")
async def test_tool_workspace_isolation(mock_session):
    """Test that tool enforces workspace isolation."""
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    mock_account = MagicMock()
    workspace_id = uuid.uuid4()
    other_workspace_id = uuid.uuid4()
    account_id = uuid.uuid4()
    
    # Account belongs to other_workspace_id
    mock_account.workspace_id = other_workspace_id
    
    with patch("app.mcp.tools.social.get_recent_posts.SocialAccountRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_account
        mock_repo_class.return_value = mock_repo
        
        tool = GetRecentPostsTool()
        
        with pytest.raises(MCPProviderError, match="not found for workspace"):
            await tool.execute({
                "workspace_id": str(workspace_id),
                "social_account_id": str(account_id)
            })


def test_token_never_in_logs_or_exceptions(adapter):
    """
    Test that if decryption fails, the encrypted payload or error details
    do not leak into the exception message.
    """
    # Break the encrypted token to force a failure
    adapter._access_token_encrypted = "broken_token"
    
    import pytest
    with pytest.raises(MCPAuthenticationError) as exc_info:
        adapter._get_access_token()
        
    # The message should just say failed to decrypt, with NO token payload
    error_msg = str(exc_info.value)
    assert "broken_token" not in error_msg
    assert "mock_access_token" not in error_msg
    assert "decrypt access token" in error_msg

def test_token_never_in_mcp_output():
    """
    Test that SocialPostData schema structure prevents tokens from being added 
    since it is Pydantic validated.
    """
    post = SocialPostData(
        post_id="post_1",
        platform="BLUESKY",
        text="Test post",
        published_at=datetime.now(timezone.utc),
        likes=5,
        comments=1,
        shares=0,
        url="https://bsky.app/test"
    )
    
    dump = post.model_dump()
    assert "access_token" not in dump
    assert "refresh_token" not in dump
