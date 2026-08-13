"""
app/mcp/tools/base.py

Abstract base classes for MCP tools.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult


class AbstractMCPTool(ABC):
    """
    Abstract base class for all MCP tools.
    """
    
    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Return the strict Pydantic definition of this tool."""
        pass
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with the given input data.
        Must return a validated ToolResult.
        """
        pass
