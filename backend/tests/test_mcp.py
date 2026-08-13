"""
tests/test_mcp.py

Tests for the Model Context Protocol (MCP) foundation architecture.
"""
import pytest
import asyncio
from typing import Dict, Any

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.servers.base import AbstractMCPServer
from app.mcp.client.registry import MCPServerRegistry
from app.mcp.client.client import MCPClient
from app.mcp.exceptions.exceptions import (
    MCPToolNotFoundError,
    MCPToolValidationError,
    MCPToolPermissionError,
    MCPToolTimeoutError,
    MCPToolExecutionError
)


# Mock Tool for Testing
class MockTool(AbstractMCPTool):
    def __init__(self, should_fail: bool = False, delay: int = 0):
        self.should_fail = should_fail
        self.delay = delay

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="mock_tool",
            description="A mock tool for testing.",
            server_name="test_server",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            required_permissions=[],
            timeout=2,
            enabled=True
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        if self.delay > 0:
            await asyncio.sleep(self.delay)
            
        if self.should_fail:
            raise ValueError("Intentional failure")
            
        from app.mcp.schemas.result import ToolResultMetadata
        from datetime import datetime, timezone
        
        return ToolResult(
            success=True,
            tool_name=self.definition.name,
            data={"echo": input_data},
            metadata=ToolResultMetadata(
                provider="test",
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id="1234"
            )
        )


class MockServer(AbstractMCPServer):
    pass


@pytest.fixture
def mcp_registry():
    return MCPServerRegistry()


@pytest.fixture
def test_server():
    server = MockServer(name="test_server")
    tool = MockTool()
    server.register_tool(tool)
    return server


@pytest.fixture
def mcp_client(mcp_registry, test_server):
    mcp_registry.register_server(test_server)
    return MCPClient(registry=mcp_registry)


def test_registry_server_registration(mcp_registry):
    server = MockServer(name="mock_server")
    mcp_registry.register_server(server)
    assert mcp_registry.get_server("mock_server") == server
    assert len(mcp_registry.list_servers()) == 1


def test_server_tool_registration(test_server):
    tools = test_server.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "mock_tool"
    assert test_server.get_tool("mock_tool") is not None


def test_server_invalid_tool_registration():
    server = MockServer(name="wrong_server")
    tool = MockTool()
    # Tool defines its server as "test_server", so this should fail
    with pytest.raises(ValueError, match="belongs to server test_server"):
        server.register_tool(tool)


def test_client_list_tools(mcp_client):
    tools = mcp_client.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "mock_tool"


def test_client_get_tool(mcp_client):
    tool_def = mcp_client.get_tool("test_server", "mock_tool")
    assert tool_def.name == "mock_tool"


def test_client_get_tool_not_found(mcp_client):
    with pytest.raises(MCPToolNotFoundError):
        mcp_client.get_tool("missing_server", "mock_tool")
        
    with pytest.raises(MCPToolNotFoundError):
        mcp_client.get_tool("test_server", "missing_tool")


@pytest.mark.asyncio
async def test_client_call_tool_success(mcp_client):
    result = await mcp_client.call_tool(
        server_name="test_server",
        tool_name="mock_tool",
        input_data={"hello": "world"},
        granted_permissions=[]
    )
    
    assert result.success is True
    assert result.data == {"echo": {"hello": "world"}}


@pytest.mark.asyncio
async def test_client_call_tool_not_found(mcp_client):
    with pytest.raises(MCPToolNotFoundError):
        await mcp_client.call_tool("missing_server", "mock_tool", {}, [])


@pytest.mark.asyncio
async def test_client_call_tool_validation_error(mcp_client):
    with pytest.raises(MCPToolValidationError):
        # input_data must be a dict
        await mcp_client.call_tool("test_server", "mock_tool", "not a dict", [])


@pytest.mark.asyncio
async def test_client_call_tool_permission_error(mcp_registry):
    server = MockServer(name="test_server")
    
    class PermTool(MockTool):
        @property
        def definition(self) -> ToolDefinition:
            from app.mcp.permissions.permissions import MCPPermission
            def_copy = super().definition.model_dump()
            def_copy["required_permissions"] = [MCPPermission.RESEARCH_READ]
            return ToolDefinition(**def_copy)
            
    server.register_tool(PermTool())
    mcp_registry.register_server(server)
    client = MCPClient(registry=mcp_registry)
    
    with pytest.raises(MCPToolPermissionError):
        # No permissions granted
        await client.call_tool("test_server", "mock_tool", {}, [])


@pytest.mark.asyncio
async def test_client_call_tool_execution_error(mcp_registry):
    server = MockServer(name="test_server")
    server.register_tool(MockTool(should_fail=True))
    mcp_registry.register_server(server)
    client = MCPClient(registry=mcp_registry)
    
    with pytest.raises(MCPToolExecutionError):
        await client.call_tool("test_server", "mock_tool", {}, [])


@pytest.mark.asyncio
async def test_client_call_tool_timeout(mcp_registry):
    server = MockServer(name="test_server")
    server.register_tool(MockTool(delay=2))
    mcp_registry.register_server(server)
    # Set default timeout to 1
    client = MCPClient(registry=mcp_registry, default_timeout=1)
    
    with pytest.raises(MCPToolTimeoutError):
        # Will time out because delay is 2 and timeout is 1
        await client.call_tool("test_server", "mock_tool", {}, [], timeout=1)
