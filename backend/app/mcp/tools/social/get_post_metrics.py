"""
app/mcp/tools/social/get_post_metrics.py

Tool to retrieve analytics metrics for a specific post.
"""
from typing import Dict, Any
import uuid
from datetime import datetime, timezone

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.adapters.factory import get_social_adapter
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError

from app.core.database import AsyncSessionLocal
from app.repositories.social_account_repository import SocialAccountRepository


class GetPostMetricsTool(AbstractMCPTool):
    """
    Retrieves normalized social metrics for a specific published post.
    """
    
    def __init__(self, adapter: SocialAdapter = None):
        self.adapter = adapter

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_post_metrics",
            description="Retrieve normalized analytics metrics for a published post.",
            server_name="social_server",
            input_schema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "format": "uuid"},
                    "social_account_id": {"type": "string", "format": "uuid"},
                    "external_post_id": {"type": "string"}
                },
                "required": ["workspace_id", "social_account_id", "external_post_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "metrics": {"type": "object"}
                }
            },
            required_permissions=[MCPPermission.ANALYTICS_READ],
            timeout=10,
            enabled=True
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        workspace_id_str = input_data.get("workspace_id")
        account_id_str = input_data.get("social_account_id")
        external_post_id = input_data.get("external_post_id")
        
        if not workspace_id_str or not account_id_str or not external_post_id:
            raise MCPToolValidationError("Missing required parameters: 'workspace_id', 'social_account_id', 'external_post_id'")
            
        try:
            workspace_id = uuid.UUID(workspace_id_str)
            account_id = uuid.UUID(account_id_str)
        except ValueError:
            raise MCPToolValidationError("Invalid UUID format for workspace_id or social_account_id")

        async with AsyncSessionLocal() as session:
            repo = SocialAccountRepository(session)
            account = await repo.get_by_id(account_id)
            
            if not account or account.workspace_id != workspace_id:
                raise MCPProviderError(f"Social account {account_id} not found for workspace {workspace_id}")
                
            platform = account.platform.value if hasattr(account.platform, 'value') else str(account.platform)
            
        # Select adapter
        adapter = self.adapter or get_social_adapter(account)
        
        try:
            metrics = await adapter.get_post_metrics(external_post_id=external_post_id)
        except Exception as e:
            if isinstance(e, MCPProviderError):
                raise
            raise MCPProviderError(f"Provider failed to retrieve post metrics: {str(e)}")
            
        return ToolResult(
            success=True,
            tool_name=self.definition.name,
            data={"metrics": metrics.model_dump()},
            metadata=ToolResultMetadata(
                provider=platform,
                observed_at=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4())
            )
        )
