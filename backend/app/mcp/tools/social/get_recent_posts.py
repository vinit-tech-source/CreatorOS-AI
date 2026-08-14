"""
app/mcp/tools/social/get_recent_posts.py

Tool to retrieve recent posts from a social account.
"""
from typing import Dict, Any
import uuid
from datetime import datetime, timezone

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.adapters.fake_social_adapter import FakeSocialAdapter
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError

from app.core.database import AsyncSessionLocal
from app.repositories.social_account_repository import SocialAccountRepository


class GetRecentPostsTool(AbstractMCPTool):
    """
    Retrieves normalized recent posts for a connected social account.
    """
    
    def __init__(self, adapter: SocialAdapter = None):
        self.adapter = adapter

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_recent_posts",
            description="Retrieve normalized recent posts for a connected social account.",
            server_name="social_server",
            input_schema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "format": "uuid"},
                    "social_account_id": {"type": "string", "format": "uuid"},
                    "limit": {"type": "integer", "default": 10, "maximum": 50}
                },
                "required": ["workspace_id", "social_account_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "posts": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                }
            },
            required_permissions=[MCPPermission.SOCIAL_READ],
            timeout=15,
            enabled=True
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        workspace_id_str = input_data.get("workspace_id")
        account_id_str = input_data.get("social_account_id")
        limit = input_data.get("limit", 10)
        
        if not workspace_id_str or not account_id_str:
            raise MCPToolValidationError("Missing required parameters: 'workspace_id' and 'social_account_id'")
            
        try:
            workspace_id = uuid.UUID(workspace_id_str)
            account_id = uuid.UUID(account_id_str)
        except ValueError:
            raise MCPToolValidationError("Invalid UUID format for workspace_id or social_account_id")
            
        if not isinstance(limit, int) or limit < 1:
            limit = 10
        if limit > 50:
            limit = 50

        async with AsyncSessionLocal() as session:
            repo = SocialAccountRepository(session)
            account = await repo.get_by_id(account_id)
            
            if not account or account.workspace_id != workspace_id:
                raise MCPProviderError(f"Social account {account_id} not found for workspace {workspace_id}")
                
            platform = account.platform.value if hasattr(account.platform, 'value') else str(account.platform)
            platform_user_id = account.platform_user_id
            
        adapter = self.adapter or FakeSocialAdapter(platform=platform)
        
        try:
            posts = await adapter.get_recent_posts(platform_user_id=platform_user_id, limit=limit)
        except Exception as e:
            if isinstance(e, MCPProviderError):
                raise
            raise MCPProviderError(f"Provider failed to retrieve recent posts: {str(e)}")
            
        return ToolResult(
            success=True,
            tool_name=self.definition.name,
            data={"posts": [post.model_dump() for post in posts]},
            metadata=ToolResultMetadata(
                provider=platform,
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4())
            )
        )
