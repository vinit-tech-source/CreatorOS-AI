"""
tests/test_research_retrieval_service.py

Tests for the Research Retrieval Service.
"""
import pytest
from unittest.mock import AsyncMock

from app.services.research_retrieval_service import ResearchRetrievalService
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.exceptions.exceptions import MCPProviderError


@pytest.fixture
def mock_mcp_client():
    client = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_search_all_providers_success(mock_mcp_client):
    # Setup mock to return a different result based on the tool called
    async def mock_call_tool(server_name, tool_name, input_data, granted_permissions):
        if tool_name == "youtube_search":
            return ToolResult(
                success=True,
                tool_name=tool_name,
                data={"results": [{"id": "yt1", "url": "https://youtube.com/1", "title": "YT Title"}]},
                metadata=ToolResultMetadata(provider="youtube", observed_at="2026", request_id="1")
            )
        elif tool_name == "bluesky_search":
            return ToolResult(
                success=True,
                tool_name=tool_name,
                data={"results": [{"id": "bs1", "url": "https://bsky.app/1", "title": "BS Title"}]},
                metadata=ToolResultMetadata(provider="bluesky", observed_at="2026", request_id="1")
            )
        elif tool_name == "reddit_search":
            return ToolResult(
                success=True,
                tool_name=tool_name,
                data={"results": [{"id": "rd1", "url": "https://reddit.com/1", "title": "RD Title"}]},
                metadata=ToolResultMetadata(provider="reddit", observed_at="2026", request_id="1")
            )
    
    mock_mcp_client.call_tool.side_effect = mock_call_tool
    
    service = ResearchRetrievalService(mcp_client=mock_mcp_client)
    
    results, metadata = await service.search_research_sources(
        query="test",
        platforms=["youtube", "bluesky", "reddit"],
        max_results=10
    )
    
    assert len(results) == 3
    assert len(metadata["failures"]) == 0
    assert metadata["total_returned"] == 3


@pytest.mark.asyncio
async def test_search_partial_failure(mock_mcp_client):
    async def mock_call_tool(server_name, tool_name, input_data, granted_permissions):
        if tool_name == "youtube_search":
            raise MCPProviderError("YouTube Rate Limit")
        elif tool_name == "bluesky_search":
            return ToolResult(
                success=True,
                tool_name=tool_name,
                data={"results": [{"id": "bs1", "url": "https://bsky.app/1", "title": "BS Title"}]},
                metadata=ToolResultMetadata(provider="bluesky", observed_at="2026", request_id="1")
            )
    
    mock_mcp_client.call_tool.side_effect = mock_call_tool
    
    service = ResearchRetrievalService(mcp_client=mock_mcp_client)
    
    results, metadata = await service.search_research_sources(
        query="test",
        platforms=["youtube", "bluesky"],
        max_results=10
    )
    
    assert len(results) == 1
    assert "youtube" in metadata["failures"]
    assert "YouTube Rate Limit" in metadata["failures"]["youtube"]
    assert metadata["total_returned"] == 1


@pytest.mark.asyncio
async def test_search_all_failure(mock_mcp_client):
    mock_mcp_client.call_tool.side_effect = MCPProviderError("Global Failure")
    
    service = ResearchRetrievalService(mcp_client=mock_mcp_client)
    
    with pytest.raises(MCPProviderError, match="All requested research providers failed"):
        await service.search_research_sources(
            query="test",
            platforms=["youtube", "bluesky"],
            max_results=10
        )


@pytest.mark.asyncio
async def test_deduplication(mock_mcp_client):
    async def mock_call_tool(server_name, tool_name, input_data, granted_permissions):
        return ToolResult(
            success=True,
            tool_name=tool_name,
            data={"results": [
                {"id": "duplicate_id", "url": "https://example.com/1", "title": "Title A"},
                {"id": "duplicate_id", "url": "https://example.com/1", "title": "Title B"},
                {"id": "unique_id", "url": "https://example.com/2", "title": "Same Title"},
                {"id": "unique_id_3", "url": "https://example.com/3", "title": "Same Title"}
            ]},
            metadata=ToolResultMetadata(provider="test", observed_at="2026", request_id="1")
        )
    
    mock_mcp_client.call_tool.side_effect = mock_call_tool
    
    service = ResearchRetrievalService(mcp_client=mock_mcp_client)
    
    results, metadata = await service.search_research_sources(
        query="test",
        platforms=["youtube"],
        max_results=10
    )
    
    # 1. duplicate_id & Title A -> added
    # 2. duplicate_id & Title B -> skipped because duplicate_id already seen
    # 3. unique_id & Same Title -> added
    # 4. unique_id_3 & Same Title -> skipped because title "Same Title" already seen
    assert len(results) == 2


@pytest.mark.asyncio
async def test_bound_max_results(mock_mcp_client):
    async def mock_call_tool(server_name, tool_name, input_data, granted_permissions):
        return ToolResult(
            success=True,
            tool_name=tool_name,
            data={"results": [
                {"id": f"{tool_name}_{i}", "url": f"https://example.com/{tool_name}/{i}", "title": f"Title {tool_name} {i}"} for i in range(10)
            ]},
            metadata=ToolResultMetadata(provider="test", observed_at="2026", request_id="1")
        )
        
    mock_mcp_client.call_tool.side_effect = mock_call_tool
    
    service = ResearchRetrievalService(mcp_client=mock_mcp_client)
    
    # Request 3 platforms, each returns 10 results = 30 total
    results, metadata = await service.search_research_sources(
        query="test",
        platforms=["youtube", "bluesky", "reddit"],
        max_results=15
    )
    
    assert len(results) == 15
    assert metadata["total_retrieved"] == 30
