"""
app/mcp/adapters/base.py

Abstract interfaces for MCP provider adapters.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AbstractResearchAdapter(ABC):
    """
    Abstract interface for research providers (e.g., YouTube, Reddit, Bluesky).
    """
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """Search the provider for research data."""
        pass


class AbstractSocialAdapter(ABC):
    """
    Abstract interface for social providers (e.g., X, LinkedIn).
    """
    
    @abstractmethod
    async def get_trends(self, **kwargs) -> Dict[str, Any]:
        """Get trending topics from the provider."""
        pass
