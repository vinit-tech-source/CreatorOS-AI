"""
app/mcp/tools/bluesky_search.py

Bluesky Search Tool.
"""
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.schemas.research import ResearchItem, EngagementMetrics
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.adapters.bluesky_adapter import BlueskyAdapter
from app.core.config import settings
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError


class BlueskySearchTool(AbstractMCPTool):
    """
    MCP Tool for searching Bluesky.
    """
    
    def __init__(self, adapter: BlueskyAdapter = None):
        self.adapter = adapter or BlueskyAdapter(enabled=settings.BLUESKY_ENABLED)

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="bluesky_search",
            description="Search Bluesky (AT Protocol) for relevant content.",
            server_name="research_server",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 20},
                    "since": {"type": "string", "format": "date-time"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "array",
                "items": {"$ref": "#/components/schemas/ResearchItem"}
            },
            required_permissions=[MCPPermission.RESEARCH_READ],
            timeout=20,
            enabled=settings.BLUESKY_ENABLED
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        query = input_data.get("query")
        if not query:
            raise MCPToolValidationError("Missing required parameter 'query'")
            
        max_results = input_data.get("max_results", 20)
        if max_results > 100:
            max_results = 100
            
        try:
            raw_data = await self.adapter.search(
                query=query, 
                limit=max_results,
                since=input_data.get("since")
            )
        except Exception as e:
            if isinstance(e, MCPProviderError):
                raise
            raise MCPProviderError(f"Bluesky search failed: {str(e)}")
            
        normalized_results = []
        posts = raw_data.get("posts", [])
        
        for post in posts:
            uri = post.get("uri", "")
            record = post.get("record", {})
            author = post.get("author", {})
            
            # Simple conversion of AT URI to an HTTP url for the web client if possible, 
            # though standard bsky.app URLs are often used.
            author_handle = author.get("handle", "")
            post_id = uri.split("/")[-1] if "/" in uri else ""
            http_url = f"https://bsky.app/profile/{author_handle}/post/{post_id}" if author_handle and post_id else uri
            
            research_item = ResearchItem(
                id=uri,
                title=None,
                content=record.get("text", ""),
                url=http_url,
                source_name="Bluesky",
                platform="Bluesky",
                author=author_handle,
                published_at=record.get("createdAt"),
                engagement=EngagementMetrics(
                    likes=post.get("likeCount", 0),
                    reposts=post.get("repostCount", 0),
                    comments=post.get("replyCount", 0)
                ),
                metadata={"cid": post.get("cid")}
            )
            normalized_results.append(research_item.model_dump())
            
        return ToolResult(
            success=True,
            tool_name=self.definition.name,
            data={"results": normalized_results},
            metadata=ToolResultMetadata(
                provider="bluesky",
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4())
            )
        )
