"""
app/mcp/tools/youtube_search.py

YouTube Search Tool.
"""
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.schemas.research import ResearchItem, EngagementMetrics
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.adapters.youtube_adapter import YouTubeAdapter
from app.core.config import settings
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError


class YouTubeSearchTool(AbstractMCPTool):
    """
    MCP Tool for searching YouTube.
    """
    
    def __init__(self, adapter: YouTubeAdapter = None):
        self.adapter = adapter or YouTubeAdapter(api_key=settings.YOUTUBE_API_KEY)

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="youtube_search",
            description="Search YouTube for relevant recent content.",
            server_name="research_server",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": settings.YOUTUBE_MAX_RESULTS},
                    "published_after": {"type": "string", "format": "date-time"},
                    "published_before": {"type": "string", "format": "date-time"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "array",
                "items": {"$ref": "#/components/schemas/ResearchItem"}
            },
            required_permissions=[MCPPermission.RESEARCH_READ],
            timeout=30,
            enabled=settings.YOUTUBE_ENABLED
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        query = input_data.get("query")
        if not query:
            raise MCPToolValidationError("Missing required parameter 'query'")
            
        max_results = input_data.get("max_results", settings.YOUTUBE_MAX_RESULTS)
        
        # Max results guardrail
        if max_results > 50:
            max_results = 50
            
        try:
            raw_data = await self.adapter.search(
                query=query, 
                limit=max_results,
                published_after=input_data.get("published_after"),
                published_before=input_data.get("published_before")
            )
        except Exception as e:
            if isinstance(e, MCPProviderError):
                raise
            raise MCPProviderError(f"YouTube search failed: {str(e)}")
            
        normalized_results = []
        items = raw_data.get("items", [])
        
        for item in items:
            vid_id = item.get("id", {}).get("videoId", "")
            snippet = item.get("snippet", {})
            
            research_item = ResearchItem(
                id=vid_id,
                title=snippet.get("title"),
                content=snippet.get("description", ""),
                url=f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "",
                source_name="YouTube",
                platform="YouTube",
                author=snippet.get("channelTitle"),
                published_at=snippet.get("publishedAt"),
                engagement=None,  # Search API doesn't return detailed stats without an extra call
                metadata={}
            )
            normalized_results.append(research_item.model_dump())
            
        return ToolResult(
            success=True,
            tool_name=self.definition.name,
            data={"results": normalized_results},
            metadata=ToolResultMetadata(
                provider="youtube",
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4())
            )
        )
