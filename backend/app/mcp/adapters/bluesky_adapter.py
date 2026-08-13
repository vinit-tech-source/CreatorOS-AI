"""
app/mcp/adapters/bluesky_adapter.py

Bluesky (AT Protocol) Adapter.
"""
from typing import Dict, Any
import logging

from app.mcp.adapters.base import AbstractResearchAdapter

logger = logging.getLogger(__name__)


class BlueskyAdapter(AbstractResearchAdapter):
    """
    Adapter for the Bluesky / AT Protocol API.
    """
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        
    async def search(self, query: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Search Bluesky (Skeleton implementation).
        """
        from app.mcp.exceptions.exceptions import MCPProviderError
        if not self.enabled:
            raise MCPProviderError("Bluesky provider is disabled.")
            
        return {
            "posts": [
                {
                    "uri": "at://mock_uri",
                    "cid": "mock_cid",
                    "author": {"handle": "mock.bsky.social"},
                    "record": {
                        "text": f"Mock Bluesky post about {query}",
                        "createdAt": "2026-01-01T12:00:00Z"
                    },
                    "replyCount": 5,
                    "repostCount": 10,
                    "likeCount": 50
                }
            ]
        }
