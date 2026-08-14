"""
app/mcp/servers/social_server.py

Social MCP Server implementation.
"""
from app.mcp.servers.base import AbstractMCPServer
from app.mcp.tools.social.get_account_info import GetAccountInfoTool
from app.mcp.tools.social.get_profile_metrics import GetProfileMetricsTool
from app.mcp.tools.social.get_recent_posts import GetRecentPostsTool


class SocialServer(AbstractMCPServer):
    """
    MCP Server for read-only Social Media interactions.
    """
    
    def __init__(self, name: str = "social_server"):
        super().__init__(name)
        
        # Register social tools
        self.register_tool(GetAccountInfoTool())
        self.register_tool(GetProfileMetricsTool())
        self.register_tool(GetRecentPostsTool())
