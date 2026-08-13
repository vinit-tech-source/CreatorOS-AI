"""
app/mcp/schemas/tool.py

MCP tool definitions schema.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.mcp.permissions.permissions import MCPPermission


class ToolDefinition(BaseModel):
    """
    Strict definition of an MCP Tool.
    """
    name: str = Field(..., min_length=1, description="Unique name of the tool within the server.")
    description: str = Field(..., min_length=1, description="Clear description of the tool's purpose.")
    server_name: str = Field(..., min_length=1, description="Name of the MCP server hosting this tool.")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for the tool's input.")
    output_schema: Dict[str, Any] = Field(..., description="JSON Schema for the tool's output.")
    required_permissions: List[MCPPermission] = Field(default_factory=list, description="Permissions required to execute this tool.")
    timeout: int = Field(default=30, ge=1, description="Execution timeout in seconds.")
    enabled: bool = Field(default=True, description="Whether the tool is currently enabled.")
