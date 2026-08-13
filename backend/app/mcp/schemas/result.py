"""
app/mcp/schemas/result.py

MCP tool result schemas.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field


class ToolResultMetadata(BaseModel):
    """
    Metadata associated with a tool result.
    """
    provider: str = Field(..., description="The provider that executed the request (e.g., youtube, test).")
    observed_at: str = Field(..., description="Timestamp of when the result was observed in ISO format.")
    request_id: str = Field(..., description="Unique request ID for tracing.")


class ToolResult(BaseModel):
    """
    Standardized MCP result structure.
    """
    success: bool = Field(..., description="Whether the tool execution was successful.")
    tool_name: str = Field(..., description="The name of the tool that was executed.")
    data: Dict[str, Any] = Field(default_factory=dict, description="The returned data payload.")
    metadata: ToolResultMetadata = Field(..., description="Metadata about the execution.")
