"""
app/mcp/tools/reddit_search.py

Reddit Search Tool.
"""
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.schemas.research import ResearchItem, EngagementMetrics
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.adapters.reddit_adapter import RedditAdapter
from app.core.config import settings
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError


class RedditSearchTool(AbstractMCPTool):
    """
    MCP Tool for searching Reddit.
    """
    
    def __init__(self, adapter: RedditAdapter = None):
        self.adapter = adapter or RedditAdapter(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET
        )

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="reddit_search",
            description="Search Reddit for relevant discussions.",
            server_name="research_server",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "subreddit": {"type": "string"},
                    "max_results": {"type": "integer", "default": 15},
                    "sort": {"type": "string", "enum": ["relevance", "hot", "top", "new"], "default": "relevance"},
                    "time_filter": {"type": "string", "enum": ["all", "day", "hour", "month", "week", "year"], "default": "all"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "array",
                "items": {"$ref": "#/components/schemas/ResearchItem"}
            },
            required_permissions=[MCPPermission.RESEARCH_READ],
            timeout=25,
            enabled=settings.REDDIT_ENABLED
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        query = input_data.get("query")
        if not query:
            raise MCPToolValidationError("Missing required parameter 'query'")
            
        max_results = input_data.get("max_results", 15)
        if max_results > 100:
            max_results = 100
            
        try:
            raw_data = await self.adapter.search(
                query=query,
                limit=max_results,
                subreddit=input_data.get("subreddit"),
                sort=input_data.get("sort", "relevance"),
                time_filter=input_data.get("time_filter", "all")
            )
        except Exception as e:
            if isinstance(e, MCPProviderError):
                raise
            raise MCPProviderError(f"Reddit search failed: {str(e)}")
            
        normalized_results = []
        children = raw_data.get("data", {}).get("children", [])
        
        for child in children:
            post_data = child.get("data", {})
            post_id = post_data.get("id", "")
            
            # Reddit created timestamp is usually epoch seconds
            created_utc = post_data.get("created_utc")
            published_at = None
            if created_utc:
                try:
                    published_at = datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat()
                except (ValueError, TypeError):
                    pass
            
            research_item = ResearchItem(
                id=post_id,
                title=post_data.get("title", ""),
                content=post_data.get("selftext", ""),
                url=post_data.get("url", ""),
                source_name="Reddit",
                platform="Reddit",
                author=post_data.get("author", ""),
                published_at=published_at,
                engagement=EngagementMetrics(
                    likes=post_data.get("score", 0),  # Reddit uses score (upvotes - downvotes)
                    comments=post_data.get("num_comments", 0)
                ),
                metadata={
                    "subreddit": post_data.get("subreddit", "")
                }
            )
            normalized_results.append(research_item.model_dump())
            
        return ToolResult(
            success=True,
            tool_name=self.definition.name,
            data={"results": normalized_results},
            metadata=ToolResultMetadata(
                provider="reddit",
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4())
            )
        )
