"""
app/services/research_retrieval_service.py

Service for orchestrating multi-platform research retrieval via MCP.
"""
import logging
from typing import List, Dict, Any, Tuple

from app.mcp.client.client import MCPClient
from app.mcp.schemas.research import ResearchItem
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPProviderError

logger = logging.getLogger(__name__)


class ResearchRetrievalService:
    """
    Orchestrates research retrieval across multiple providers using the MCP client.
    Handles deduplication, fallback, and bounding.
    """
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        
    async def search_research_sources(
        self,
        query: str,
        platforms: List[str],
        max_results: int = 10
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Search across multiple platforms using MCP tools.
        
        Args:
            query: The search query.
            platforms: List of platforms to search (e.g., ["youtube", "bluesky", "reddit"]).
            max_results: Maximum total results to return across all platforms.
            
        Returns:
            Tuple containing:
            - List of normalized ResearchItem dictionaries.
            - Metadata dictionary containing failure information.
        """
        all_results: List[Dict[str, Any]] = []
        failures: Dict[str, str] = {}
        
        # Tools map exactly to platform names based on our architecture:
        # e.g., 'youtube' -> 'youtube_search'
        for platform in platforms:
            tool_name = f"{platform.lower()}_search"
            try:
                # We distribute the max_results roughly evenly among requested platforms
                # just to bound the individual queries, but cap the global total later.
                platform_max = max(5, max_results // len(platforms))
                
                result = await self.mcp_client.call_tool(
                    server_name="research_server",
                    tool_name=tool_name,
                    input_data={"query": query, "max_results": platform_max},
                    granted_permissions=[MCPPermission.RESEARCH_READ.value]
                )
                
                if result.success and result.data and "results" in result.data:
                    all_results.extend(result.data["results"])
                    
            except Exception as e:
                logger.warning(f"Failed to retrieve research from {platform}: {str(e)}")
                failures[platform] = str(e)
                
        if not all_results and len(failures) == len(platforms):
            # All requested platforms failed
            raise MCPProviderError(f"All requested research providers failed: {failures}")
            
        # Deduplicate results based on URL and ID
        deduplicated = self._deduplicate_results(all_results)
        
        # Sort or prioritize (e.g., by engagement, or just evenly distributed)
        # For MVP, we just truncate to the requested bound
        bounded_results = deduplicated[:max_results]
        
        metadata = {
            "query": query,
            "platforms_requested": platforms,
            "failures": failures,
            "total_retrieved": len(all_results),
            "total_returned": len(bounded_results)
        }
        
        return bounded_results, metadata
        
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate research items based on ID or URL.
        """
        seen_identifiers = set()
        deduplicated = []
        
        for item in results:
            item_id = item.get("id")
            item_url = item.get("url")
            item_title = item.get("title")
            
            # Create a composite key if both exist, otherwise use whichever exists
            if item_id and item_url:
                identifier = f"{item_id}_{item_url}"
            elif item_id:
                identifier = item_id
            elif item_url:
                identifier = item_url
            else:
                identifier = str(item)  # Fallback
                
            # Basic title deduplication
            title_key = item_title.strip().lower() if item_title else None
                
            if identifier not in seen_identifiers and (not title_key or title_key not in seen_identifiers):
                seen_identifiers.add(identifier)
                if title_key:
                    seen_identifiers.add(title_key)
                deduplicated.append(item)
                
        return deduplicated
