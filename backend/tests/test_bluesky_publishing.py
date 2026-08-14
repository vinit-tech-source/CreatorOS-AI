"""
tests/test_bluesky_publishing.py

Tests for Bluesky publishing through the Social MCP Tool.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from sqlalchemy.future import select
from cryptography.fernet import Fernet

from app.mcp.adapters.bluesky_social_adapter import BlueskySocialAdapter
from app.mcp.schemas.social import SocialPublishResult
from app.mcp.exceptions.exceptions import MCPProviderError, MCPAuthenticationError, MCPToolValidationError
from app.mcp.tools.social.publish_post import PublishPostTool
from app.core.encryption import encrypt_secret
from app.core.config import settings
from app.models.publishing_log import PublishingLog, PublishStatus


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
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.post")
async def test_successful_bluesky_publish(mock_post, adapter):
    """1. Successful Bluesky publish & 10. Normalized response."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value={
        "uri": "at://did:plc:123/app.bsky.feed.post/3k123456",
        "cid": "bafyreib2"
    })
    mock_post.return_value = mock_resp
    
    result = await adapter.publish_post("Hello World", "idemp-key-1")
    
    assert isinstance(result, SocialPublishResult)
    assert result.platform == "BLUESKY"
    assert result.external_post_id == "at://did:plc:123/app.bsky.feed.post/3k123456"
    assert result.status == "SUCCESS"
    assert "https://bsky.app/profile/did:plc:123/post/3k123456" == result.post_url
    assert result.published_at is not None
    
    # 11. Token never appears in result
    dump = result.model_dump()
    assert "access_token" not in dump


@pytest.mark.asyncio
async def test_content_validation(adapter):
    """9. Content validation."""
    with pytest.raises(MCPProviderError, match="Content cannot be empty"):
        await adapter.publish_post("", "idemp")
        
    with pytest.raises(MCPProviderError, match="Content cannot be empty"):
        await adapter.publish_post("   ", "idemp")


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.post")
async def test_expired_credentials(mock_post, adapter):
    """5. Expired credentials."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 401
    mock_post.return_value = mock_resp
    
    with pytest.raises(MCPAuthenticationError, match="credentials expired"):
        await adapter.publish_post("Hello", "idemp")


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.post")
async def test_provider_timeout(mock_post, adapter):
    """6. Provider timeout."""
    import httpx
    mock_post.side_effect = httpx.RequestError("Timeout")
    
    with pytest.raises(MCPProviderError, match="unavailable or timed out"):
        await adapter.publish_post("Hello", "idemp")


@pytest.mark.asyncio
@patch("app.mcp.adapters.bluesky_social_adapter.httpx.AsyncClient.post")
async def test_provider_failure(mock_post, adapter):
    """7. Provider failure."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp
    
    with pytest.raises(MCPProviderError, match="returned an error"):
        await adapter.publish_post("Hello", "idemp")


def test_token_never_in_logs_or_errors(adapter):
    """12. Token never appears in logs/errors."""
    adapter._access_token_encrypted = "broken_token"
    
    with pytest.raises(MCPAuthenticationError) as exc:
        adapter._get_access_token()
        
    assert "mock_access_token" not in str(exc.value)
    assert "broken_token" not in str(exc.value)


# ---------------------------------------------------------
# TOOL INTEGRATION & IDEMPOTENCY TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
@patch("app.mcp.tools.social.publish_post.AsyncSessionLocal")
async def test_tool_workspace_authorization(mock_session):
    """2. Workspace authorization failure."""
    mock_db = AsyncMock()
    # Let the queries return nothing
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    mock_session.return_value.__aenter__.return_value = mock_db
    
    mock_account = MagicMock()
    mock_account.workspace_id = uuid.uuid4() # Different workspace
    
    with patch("app.mcp.tools.social.publish_post.SocialAccountRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_account
        mock_repo_class.return_value = mock_repo
        
        tool = PublishPostTool()
        with pytest.raises(MCPProviderError, match="not found for workspace"):
            await tool.execute({
                "workspace_id": str(uuid.uuid4()),
                "social_account_id": str(uuid.uuid4()),
                "post_id": str(uuid.uuid4()),
                "idempotency_key": "idemp-1"
            })


@pytest.mark.asyncio
@patch("app.mcp.tools.social.publish_post.AsyncSessionLocal")
async def test_duplicate_idempotency_key(mock_session):
    """8. Duplicate idempotency key (success path returns cache)."""
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    existing_log = MagicMock()
    existing_log.status = PublishStatus.SUCCESS
    existing_log.platform.value = "BLUESKY"
    existing_log.external_post_id = "at://some-uri"
    existing_log.published_at = datetime.now(timezone.utc)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_log
    mock_db.execute.return_value = mock_result
    
    tool = PublishPostTool()
    result = await tool.execute({
        "workspace_id": str(uuid.uuid4()),
        "social_account_id": str(uuid.uuid4()),
        "post_id": str(uuid.uuid4()),
        "idempotency_key": "idemp-existing"
    })
    
    assert result.success
    assert result.metadata.provider == "CACHE"
    assert result.data["result"]["external_post_id"] == "at://some-uri"
