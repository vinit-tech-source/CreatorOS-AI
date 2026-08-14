"""
app/mcp/client/client.py

MCP Client for interacting with tools.
"""
import asyncio
import logging
from typing import Dict, Any, List

from app.mcp.client.registry import MCPServerRegistry
from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult
from app.mcp.exceptions.exceptions import (
    MCPToolNotFoundError,
    MCPToolTimeoutError,
    MCPToolExecutionError,
    MCPProviderError
)

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for interacting with MCP servers and tools.
    """
    
    def __init__(self, registry: MCPServerRegistry, default_timeout: int = 30):
        self._registry = registry
        self._default_timeout = default_timeout
        
    def list_tools(self) -> List[ToolDefinition]:
        """List all available tools across all servers."""
        tools = []
        for server in self._registry.list_servers():
            tools.extend(server.list_tools())
        return tools
        
    def get_tool(self, server_name: str, tool_name: str) -> ToolDefinition:
        """Get a specific tool definition."""
        server = self._registry.get_server(server_name)
        if not server:
            raise MCPToolNotFoundError(f"Server {server_name} not found")
            
        tool = server.get_tool(tool_name)
        if not tool or not tool.definition.enabled:
            raise MCPToolNotFoundError(f"Tool {tool_name} not found on server {server_name}")
            
        return tool.definition
        
    async def call_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        input_data: Dict[str, Any], 
        granted_permissions: List[str],
        timeout: int = None
    ) -> ToolResult:
        """
        Call a tool on a specific server with the given inputs.
        """
        server = self._registry.get_server(server_name)
        if not server:
            raise MCPToolNotFoundError(f"Server {server_name} not found")
            
        tool = server.get_tool(tool_name)
        if not tool:
            raise MCPToolNotFoundError(f"Tool {tool_name} not found on server {server_name}")
            
        exec_timeout = timeout or tool.definition.timeout or self._default_timeout
        
        try:
            # Wrap execution in asyncio.wait_for for timeout control
            result = await asyncio.wait_for(
                server.call_tool(tool_name, input_data, granted_permissions),
                timeout=exec_timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Execution of {tool_name} timed out after {exec_timeout}s")
            raise MCPToolTimeoutError(f"Tool {tool_name} timed out")
        except MCPProviderError:
            raise
        except Exception as e:
            # Reraise known MCP exceptions, otherwise wrap in MCPToolExecutionError
            from app.mcp.exceptions.exceptions import MCPToolPermissionError, MCPToolValidationError, MCPConnectionError
            if isinstance(e, (MCPToolPermissionError, MCPToolValidationError, MCPConnectionError)):
                raise
            raise MCPToolExecutionError(f"Error calling tool {tool_name}: {str(e)}")


def get_default_mcp_client() -> MCPClient:
    """
    Helper to instantiate a fully configured MCPClient with the Research Server and Social Server.
    """
    from app.mcp.client.registry import MCPServerRegistry
    from app.mcp.servers.research_server import ResearchServer
    from app.mcp.servers.social_server import SocialServer
    
    registry = MCPServerRegistry()
    registry.register_server(ResearchServer())
    registry.register_server(SocialServer())
    
    from app.core.config import settings
    return MCPClient(registry=registry, default_timeout=settings.MCP_DEFAULT_TIMEOUT)
