"""
tests/test_mcp_research.py

Tests for the Research MCP Server and associated tools/adapters.
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.mcp.servers.research_server import ResearchServer
from app.mcp.client.registry import MCPServerRegistry
from app.mcp.client.client import MCPClient
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError, MCPToolPermissionError
from app.mcp.permissions.permissions import MCPPermission
from app.core.config import settings


@pytest.fixture
def mcp_client():
    # Force enable settings for testing
    settings.YOUTUBE_ENABLED = True
    settings.BLUESKY_ENABLED = True
    settings.REDDIT_ENABLED = True
    
    registry = MCPServerRegistry()
    server = ResearchServer()
    registry.register_server(server)
    return MCPClient(registry=registry)


# ---------------------------------------------------------
# YouTube Tool Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_youtube_search_success(mcp_client):
    with patch("app.mcp.tools.youtube_search.YouTubeAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {
            "items": [
                {
                    "id": {"videoId": "123"},
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test Desc",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2026-01-01T00:00:00Z"
                    }
                }
            ]
        }
        
        result = await mcp_client.call_tool(
            server_name="research_server",
            tool_name="youtube_search",
            input_data={"query": "AI content"},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )
        
        assert result.success is True
        results = result.data["results"]
        assert len(results) == 1
        
        item = results[0]
        assert item["id"] == "123"
        assert item["title"] == "Test Video"
        assert item["url"] == "https://www.youtube.com/watch?v=123"
        assert item["platform"] == "YouTube"


@pytest.mark.asyncio
async def test_youtube_search_empty(mcp_client):
    with patch("app.mcp.tools.youtube_search.YouTubeAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"items": []}
        
        result = await mcp_client.call_tool(
            server_name="research_server",
            tool_name="youtube_search",
            input_data={"query": "AI content"},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )
        
        assert result.success is True
        assert len(result.data["results"]) == 0


@pytest.mark.asyncio
async def test_youtube_search_missing_query(mcp_client):
    with pytest.raises(MCPToolValidationError, match="Missing required parameter 'query'"):
        await mcp_client.call_tool(
            server_name="research_server",
            tool_name="youtube_search",
            input_data={},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )


@pytest.mark.asyncio
async def test_youtube_search_provider_failure(mcp_client):
    with patch("app.mcp.tools.youtube_search.YouTubeAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = MCPProviderError("Rate limit exceeded")
        
        with pytest.raises(MCPProviderError, match="Rate limit exceeded"):
            await mcp_client.call_tool(
                server_name="research_server",
                tool_name="youtube_search",
                input_data={"query": "test"},
                granted_permissions=[MCPPermission.RESEARCH_READ.value]
            )


# ---------------------------------------------------------
# Bluesky Tool Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_bluesky_search_success(mcp_client):
    with patch("app.mcp.tools.bluesky_search.BlueskyAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {
            "posts": [
                {
                    "uri": "at://did:plc:123/app.bsky.feed.post/456",
                    "cid": "cid_xyz",
                    "author": {"handle": "user.bsky.social"},
                    "record": {"text": "Hello world", "createdAt": "2026-01-01T00:00:00Z"},
                    "likeCount": 10
                }
            ]
        }
        
        result = await mcp_client.call_tool(
            server_name="research_server",
            tool_name="bluesky_search",
            input_data={"query": "test"},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )
        
        assert result.success is True
        results = result.data["results"]
        assert len(results) == 1
        
        item = results[0]
        assert item["id"] == "at://did:plc:123/app.bsky.feed.post/456"
        assert item["content"] == "Hello world"
        assert item["platform"] == "Bluesky"
        assert item["url"] == "https://bsky.app/profile/user.bsky.social/post/456"
        assert item["engagement"]["likes"] == 10


@pytest.mark.asyncio
async def test_bluesky_search_empty(mcp_client):
    with patch("app.mcp.tools.bluesky_search.BlueskyAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"posts": []}
        
        result = await mcp_client.call_tool(
            server_name="research_server",
            tool_name="bluesky_search",
            input_data={"query": "test"},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )
        
        assert len(result.data["results"]) == 0


@pytest.mark.asyncio
async def test_bluesky_search_provider_failure(mcp_client):
    with patch("app.mcp.tools.bluesky_search.BlueskyAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("Network Error")
        
        with pytest.raises(MCPProviderError, match="Bluesky search failed: Network Error"):
            await mcp_client.call_tool(
                server_name="research_server",
                tool_name="bluesky_search",
                input_data={"query": "test"},
                granted_permissions=[MCPPermission.RESEARCH_READ.value]
            )


# ---------------------------------------------------------
# Reddit Tool Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_reddit_search_success(mcp_client):
    with patch("app.mcp.tools.reddit_search.RedditAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "abc",
                            "title": "Reddit Post",
                            "selftext": "Content",
                            "url": "https://reddit.com/r/test",
                            "subreddit": "test",
                            "author": "tester",
                            "created_utc": 1704067200,
                            "score": 50,
                            "num_comments": 5
                        }
                    }
                ]
            }
        }
        
        result = await mcp_client.call_tool(
            server_name="research_server",
            tool_name="reddit_search",
            input_data={"query": "test"},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )
        
        assert result.success is True
        results = result.data["results"]
        assert len(results) == 1
        
        item = results[0]
        assert item["id"] == "abc"
        assert item["title"] == "Reddit Post"
        assert item["platform"] == "Reddit"
        assert item["published_at"] == "2024-01-01T00:00:00+00:00"
        assert item["engagement"]["likes"] == 50
        assert item["metadata"]["subreddit"] == "test"


@pytest.mark.asyncio
async def test_reddit_search_empty(mcp_client):
    with patch("app.mcp.tools.reddit_search.RedditAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"data": {"children": []}}
        
        result = await mcp_client.call_tool(
            server_name="research_server",
            tool_name="reddit_search",
            input_data={"query": "test"},
            granted_permissions=[MCPPermission.RESEARCH_READ.value]
        )
        
        assert len(result.data["results"]) == 0


@pytest.mark.asyncio
async def test_reddit_search_provider_failure(mcp_client):
    with patch("app.mcp.tools.reddit_search.RedditAdapter.search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = MCPProviderError("Auth Failed")
        
        with pytest.raises(MCPProviderError, match="Auth Failed"):
            await mcp_client.call_tool(
                server_name="research_server",
                tool_name="reddit_search",
                input_data={"query": "test"},
                granted_permissions=[MCPPermission.RESEARCH_READ.value]
            )


# ---------------------------------------------------------
# MCP Client & Server General Tests
# ---------------------------------------------------------
def test_tools_discoverable(mcp_client):
    tools = mcp_client.list_tools()
    tool_names = [t.name for t in tools]
    
    assert "youtube_search" in tool_names
    assert "bluesky_search" in tool_names
    assert "reddit_search" in tool_names


@pytest.mark.asyncio
async def test_research_read_permission_enforced(mcp_client):
    with pytest.raises(MCPToolPermissionError, match="Missing required permission 'research:read'"):
        # Not providing any granted permissions
        await mcp_client.call_tool(
            server_name="research_server",
            tool_name="youtube_search",
            input_data={"query": "test"},
            granted_permissions=[]
        )
