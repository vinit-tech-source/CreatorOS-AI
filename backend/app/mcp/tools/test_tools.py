"""
app/mcp/tools/test_tools.py

Mock tools for testing the MCP architecture.
"""
from datetime import datetime, timezone
import uuid
from typing import Dict, Any

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.tools.base import AbstractMCPTool


class TestEchoTool(AbstractMCPTool):
    """
    A simple echo tool for testing the MCP pipeline.
    """
    
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="test_echo",
            description="A test tool that echoes the input text.",
            server_name="test_server",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            },
            required_permissions=[],
            timeout=10,
            enabled=True
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        # Simple validation
        if "text" not in input_data:
            from app.mcp.exceptions.exceptions import MCPToolValidationError
            raise MCPToolValidationError("Missing required field 'text'")
            
        text = input_data["text"]
        
        return ToolResult(
            success=True,
            tool_name="test_echo",
            data={"text": text},
            metadata=ToolResultMetadata(
                provider="test",
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4())
            )
        )
