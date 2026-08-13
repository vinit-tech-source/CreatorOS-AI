"""
app/mcp/servers/research_server.py

Research MCP Server for CreatorOS AI.
"""
from app.mcp.servers.base import AbstractMCPServer
from app.mcp.tools.youtube_search import YouTubeSearchTool
from app.mcp.tools.bluesky_search import BlueskySearchTool
from app.mcp.tools.reddit_search import RedditSearchTool


class ResearchServer(AbstractMCPServer):
    """
    Server hosting all research and trend retrieval tools.
    """
    
    def __init__(self, name: str = "research_server"):
        super().__init__(name=name)
        
        # Register the tools
        self.register_tool(YouTubeSearchTool())
        self.register_tool(BlueskySearchTool())
        self.register_tool(RedditSearchTool())
