"""
app/mcp/client/registry.py

MCP Server Registry.
"""
from typing import Dict, Optional, List

from app.mcp.servers.base import AbstractMCPServer


class MCPServerRegistry:
    """
    Registry for managing available MCP servers.
    """
    
    def __init__(self):
        self._servers: Dict[str, AbstractMCPServer] = {}
        
    def register_server(self, server: AbstractMCPServer) -> None:
        """Register a new MCP server."""
        self._servers[server.name] = server
        
    def get_server(self, name: str) -> Optional[AbstractMCPServer]:
        """Get a server by name."""
        return self._servers.get(name)
        
    def list_servers(self) -> List[AbstractMCPServer]:
        """List all registered servers."""
        return list(self._servers.values())
