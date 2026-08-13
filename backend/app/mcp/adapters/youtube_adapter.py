"""
app/mcp/adapters/youtube_adapter.py

YouTube Data API Adapter.
"""
from typing import Dict, Any
import logging

from app.mcp.adapters.base import AbstractResearchAdapter
from app.mcp.exceptions.exceptions import MCPProviderError

logger = logging.getLogger(__name__)


class YouTubeAdapter(AbstractResearchAdapter):
    """
    Adapter for the YouTube Data API.
    """
    
    def __init__(self, api_key: str):
        if not api_key:
            logger.warning("YouTubeAdapter initialized without an API key.")
        self.api_key = api_key
        
    async def search(self, query: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Search YouTube (Skeleton implementation).
        Real API integration will be done in a subsequent phase.
        """
        if not self.api_key:
            raise MCPProviderError("YouTube API key not configured.")
            
        # For this foundation phase, we return a mock payload 
        # to allow the tool to demonstrate normalization.
        return {
            "items": [
                {
                    "id": {"videoId": "mock_vid_1"},
                    "snippet": {
                        "title": f"Mock YouTube Video for {query}",
                        "description": "This is a mock description.",
                        "channelTitle": "MockChannel",
                        "publishedAt": "2026-01-01T12:00:00Z"
                    }
                }
            ]
        }
