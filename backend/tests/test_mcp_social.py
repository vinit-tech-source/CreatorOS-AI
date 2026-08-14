"""
tests/test_mcp_social.py

Tests for the Social MCP Server foundation.
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock

from app.mcp.servers.social_server import SocialServer
from app.mcp.schemas.social import SocialAccountData, SocialPostData, SocialMetrics
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import (
    MCPToolValidationError,
    MCPProviderError,
    MCPToolPermissionError,
    MCPToolNotFoundError
)
from app.mcp.client.client import MCPClient
from app.mcp.client.registry import MCPServerRegistry

# Fake workspace and account for tests
TEST_WORKSPACE_ID = str(uuid.uuid4())
TEST_ACCOUNT_ID = str(uuid.uuid4())

# Setup a fixture for the social server client
@pytest.fixture
def social_mcp_client():
    registry = MCPServerRegistry()
    registry.register_server(SocialServer())
    return MCPClient(registry=registry)


# We need to patch the SocialAccountRepository for the tools so it doesn't try to use the DB
@pytest.fixture
def mock_repo():
    with patch("app.mcp.tools.social.get_account_info.SocialAccountRepository") as info_repo_mock, \
         patch("app.mcp.tools.social.get_profile_metrics.SocialAccountRepository") as metrics_repo_mock, \
         patch("app.mcp.tools.social.get_recent_posts.SocialAccountRepository") as posts_repo_mock:
             
        # Create a mock account
        mock_account = MagicMock()
        mock_account.workspace_id = uuid.UUID(TEST_WORKSPACE_ID)
        mock_account.platform = "FAKE"
        mock_account.platform_user_id = "user123"
        
        info_instance = MagicMock()
        info_instance.get_by_id = AsyncMock(return_value=mock_account)
        info_repo_mock.return_value = info_instance
        
        metrics_instance = MagicMock()
        metrics_instance.get_by_id = AsyncMock(return_value=mock_account)
        metrics_repo_mock.return_value = metrics_instance
        
        posts_instance = MagicMock()
        posts_instance.get_by_id = AsyncMock(return_value=mock_account)
        posts_repo_mock.return_value = posts_instance
        
        yield mock_account


@pytest.mark.asyncio
async def test_social_server_registers_tools(social_mcp_client):
    """1. Social server registers tools."""
    tools = social_mcp_client.list_tools()
    tool_names = [t.name for t in tools]
    
    assert "get_account_info" in tool_names
    assert "get_profile_metrics" in tool_names
    assert "get_recent_posts" in tool_names
    assert "publish_post" in tool_names
    
    for tool in tools:
        if tool.name == "publish_post":
            assert MCPPermission.SOCIAL_PUBLISH in tool.required_permissions
            assert MCPPermission.SOCIAL_READ not in tool.required_permissions
        else:
            assert MCPPermission.SOCIAL_READ in tool.required_permissions
            assert MCPPermission.SOCIAL_PUBLISH not in tool.required_permissions


@pytest.mark.asyncio
async def test_get_account_info_works(social_mcp_client, mock_repo):
    """2. get_account_info works."""
    result = await social_mcp_client.call_tool(
        server_name="social_server",
        tool_name="get_account_info",
        input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID},
        granted_permissions=[MCPPermission.SOCIAL_READ.value]
    )
    
    assert result.success is True
    assert "account" in result.data
    # 11. Normalized schemas are valid
    account = result.data["account"]
    assert account["platform"] == "FAKE"
    assert account["username"] == "fake_user123"
    # 12. Tokens never appear in tool results
    assert "access_token" not in account
    assert "refresh_token" not in account


@pytest.mark.asyncio
async def test_get_profile_metrics_works(social_mcp_client, mock_repo):
    """3. get_profile_metrics works."""
    result = await social_mcp_client.call_tool(
        server_name="social_server",
        tool_name="get_profile_metrics",
        input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID},
        granted_permissions=[MCPPermission.SOCIAL_READ.value]
    )
    
    assert result.success is True
    assert "metrics" in result.data
    metrics = result.data["metrics"]
    assert metrics["followers"] == 1000
    assert metrics["impressions"] == 5000


@pytest.mark.asyncio
async def test_get_recent_posts_works(social_mcp_client, mock_repo):
    """4. get_recent_posts works."""
    result = await social_mcp_client.call_tool(
        server_name="social_server",
        tool_name="get_recent_posts",
        input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID, "limit": 5},
        granted_permissions=[MCPPermission.SOCIAL_READ.value]
    )
    
    assert result.success is True
    assert "posts" in result.data
    posts = result.data["posts"]
    assert len(posts) == 5
    assert posts[0]["platform"] == "FAKE"
    

@pytest.mark.asyncio
async def test_workspace_isolation_works(social_mcp_client, mock_repo):
    """5. Workspace isolation works."""
    # Alter mock repo to simulate a workspace mismatch
    mock_repo.workspace_id = uuid.uuid4() # Different UUID
    
    with pytest.raises(MCPProviderError, match="not found for workspace"):
        await social_mcp_client.call_tool(
            server_name="social_server",
            tool_name="get_account_info",
            input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID},
            granted_permissions=[MCPPermission.SOCIAL_READ.value]
        )


@pytest.mark.asyncio
async def test_permission_failure_works(social_mcp_client):
    """6. Permission failure works."""
    # Provide wrong permission
    with pytest.raises(MCPToolPermissionError):
        await social_mcp_client.call_tool(
            server_name="social_server",
            tool_name="get_account_info",
            input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID},
            granted_permissions=[MCPPermission.SOCIAL_PUBLISH.value] # Not READ
        )


@pytest.mark.asyncio
async def test_invalid_account_id_handled(social_mcp_client):
    """7. Invalid account ID is handled."""
    with pytest.raises(MCPToolValidationError, match="Invalid UUID format"):
        await social_mcp_client.call_tool(
            server_name="social_server",
            tool_name="get_account_info",
            input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": "not-a-uuid"},
            granted_permissions=[MCPPermission.SOCIAL_READ.value]
        )


@pytest.mark.asyncio
async def test_provider_failure_mapped(social_mcp_client, mock_repo):
    """9. Provider failure is mapped."""
    # Set the platform_user_id to 'error_user' which our FakeSocialAdapter specifically fails on
    mock_repo.platform_user_id = "error_user"
    
    with pytest.raises(MCPProviderError, match="Simulated provider error"):
        await social_mcp_client.call_tool(
            server_name="social_server",
            tool_name="get_account_info",
            input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID},
            granted_permissions=[MCPPermission.SOCIAL_READ.value]
        )


@pytest.mark.asyncio
async def test_pagination_limit_bounded(social_mcp_client, mock_repo):
    """10. Pagination/limit is bounded."""
    result = await social_mcp_client.call_tool(
        server_name="social_server",
        tool_name="get_recent_posts",
        input_data={"workspace_id": TEST_WORKSPACE_ID, "social_account_id": TEST_ACCOUNT_ID, "limit": 1000}, # Exceeds max
        granted_permissions=[MCPPermission.SOCIAL_READ.value]
    )
    
    assert result.success is True
    assert "posts" in result.data
    posts = result.data["posts"]
    assert len(posts) == 50 # Bounded to 50
