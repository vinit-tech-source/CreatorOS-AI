"""
app/mcp/servers/base.py

Abstract base class for MCP Servers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.exceptions.exceptions import MCPToolNotFoundError, MCPToolPermissionError, MCPToolValidationError

logger = logging.getLogger(__name__)


class AbstractMCPServer(ABC):
    """
    Abstract base class for MCP Servers.
    A server groups related tools and manages their execution.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._tools: Dict[str, AbstractMCPTool] = {}
        
    def register_tool(self, tool: AbstractMCPTool) -> None:
        """Register a tool with this server."""
        definition = tool.definition
        if definition.server_name != self.name:
            raise ValueError(f"Tool {definition.name} belongs to server {definition.server_name}, not {self.name}")
        self._tools[definition.name] = tool
        logger.info(f"Registered tool {definition.name} on server {self.name}")
        
    def list_tools(self) -> List[ToolDefinition]:
        """List all tools available on this server."""
        return [tool.definition for tool in self._tools.values() if tool.definition.enabled]
        
    def get_tool(self, tool_name: str) -> Optional[AbstractMCPTool]:
        """Get a specific tool by name."""
        return self._tools.get(tool_name)
        
    async def call_tool(self, tool_name: str, input_data: Dict[str, Any], granted_permissions: List[str]) -> ToolResult:
        """
        Execute a tool on this server, validating permissions and inputs.
        """
        tool = self.get_tool(tool_name)
        if not tool or not tool.definition.enabled:
            raise MCPToolNotFoundError(f"Tool {tool_name} not found or disabled on server {self.name}")
            
        definition = tool.definition
        
        # Permission validation
        for req_perm in definition.required_permissions:
            if req_perm.value not in granted_permissions:
                raise MCPToolPermissionError(f"Missing required permission '{req_perm.value}' for tool {tool_name}")
                
        # Basic input validation (schema validation would ideally use jsonschema library)
        # For this MVP foundation, we rely on the tool's internal validation or future schema validators
        if not isinstance(input_data, dict):
            raise MCPToolValidationError(f"Input data for tool {tool_name} must be a dictionary")
            
        try:
            logger.info(f"Executing tool {tool_name} on server {self.name}")
            # Ensure sensitive data is not logged
            result = await tool.execute(input_data)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
