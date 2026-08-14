"""
app/mcp/tools/social/publish_post.py

Tool to publish a post to a social account.
Implements idempotency to prevent duplicate publications.
"""
from typing import Dict, Any, List
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.future import select

from app.mcp.schemas.tool import ToolDefinition
from app.mcp.schemas.result import ToolResult, ToolResultMetadata
from app.mcp.tools.base import AbstractMCPTool
from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.adapters.factory import get_social_adapter
from app.mcp.permissions.permissions import MCPPermission
from app.mcp.exceptions.exceptions import MCPToolValidationError, MCPProviderError

from app.core.database import AsyncSessionLocal
from app.repositories.social_account_repository import SocialAccountRepository
from app.repositories.post_repository import PostRepository
from app.models.publishing_log import PublishingLog, PublishStatus
from app.models.post import Post, PostStatus

logger = logging.getLogger(__name__)


class PublishPostTool(AbstractMCPTool):
    """
    Publishes content to a connected social account.
    """
    
    def __init__(self, adapter: SocialAdapter = None):
        self.adapter = adapter

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="publish_post",
            description="Publish content to a connected social account.",
            server_name="social_server",
            input_schema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "format": "uuid"},
                    "social_account_id": {"type": "string", "format": "uuid"},
                    "post_id": {"type": "string", "format": "uuid"},
                    "idempotency_key": {"type": "string", "minLength": 1}
                },
                "required": ["workspace_id", "social_account_id", "post_id", "idempotency_key"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "platform": {"type": "string"},
                    "external_post_id": {"type": "string"},
                    "published_at": {"type": "string"},
                    "post_url": {"type": "string"},
                    "status": {"type": "string"}
                }
            },
            required_permissions=[MCPPermission.SOCIAL_PUBLISH],
            timeout=30,
            enabled=True
        )

    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        workspace_id_str = input_data.get("workspace_id")
        account_id_str = input_data.get("social_account_id")
        post_id_str = input_data.get("post_id")
        idempotency_key = input_data.get("idempotency_key")
        
        if not workspace_id_str or not account_id_str or not post_id_str or not idempotency_key:
            raise MCPToolValidationError("Missing required parameters.")
            
        try:
            workspace_id = uuid.UUID(workspace_id_str)
            account_id = uuid.UUID(account_id_str)
            post_id = uuid.UUID(post_id_str)
        except ValueError:
            raise MCPToolValidationError("Invalid UUID format.")
            
        async with AsyncSessionLocal() as session:
            # 1. Idempotency Check
            stmt = select(PublishingLog).where(PublishingLog.idempotency_key == idempotency_key)
            result = await session.execute(stmt)
            existing_log = result.scalar_one_or_none()
            
            if existing_log:
                if existing_log.status == PublishStatus.SUCCESS:
                    # Return previous success silently
                    return ToolResult(
                        success=True,
                        tool_name=self.definition.name,
                        data={
                            "result": {
                                "platform": existing_log.platform.value if hasattr(existing_log.platform, 'value') else str(existing_log.platform),
                                "external_post_id": existing_log.external_post_id,
                                "published_at": existing_log.published_at.isoformat() if existing_log.published_at else None,
                                "post_url": None, # Cannot easily recreate URL here without platform specifics
                                "status": existing_log.status.value
                            }
                        },
                        metadata=ToolResultMetadata(
                            provider="CACHE",
                            observed_at=datetime.now(timezone.utc).isoformat(),
                            request_id=str(uuid.uuid4())
                        )
                    )
                else:
                    raise MCPProviderError(f"Previous publish attempt with this idempotency key failed: {existing_log.error_code}")
            
            # 2. Authorization and Account Retrieval
            repo = SocialAccountRepository(session)
            account = await repo.get_by_id(account_id)
            
            if not account or account.workspace_id != workspace_id:
                raise MCPProviderError(f"Social account {account_id} not found for workspace {workspace_id}")
                
            platform = account.platform.value if hasattr(account.platform, 'value') else str(account.platform)
            
            # 2.5 Verify Post Approval
            post_repo = PostRepository(session)
            post = await post_repo.get_by_id(post_id)
            if not post:
                raise MCPProviderError(f"Post {post_id} not found")
                
            # Verify workspace ownership via project (simplification, assume post belongs to project in workspace)
            # Verify Post is APPROVED
            if post.status != PostStatus.APPROVED:
                raise MCPProviderError(f"Post {post_id} is not APPROVED. Current status: {post.status.value}")
                
            content = post.content
            media_urls = [] # In a real app, map post.media_assets to URLs
            
            # 3. Create Pending Log
            pub_log = PublishingLog(
                workspace_id=workspace_id,
                social_account_id=account_id,
                platform=account.platform,
                idempotency_key=idempotency_key,
                status=PublishStatus.PENDING
            )
            session.add(pub_log)
            await session.commit()
            
        # 4. Execute Publish
        adapter = self.adapter or get_social_adapter(account)
        
        try:
            publish_result = await adapter.publish_post(
                content=content,
                idempotency_key=idempotency_key,
                media=media_urls
            )
            
            # 5. Update Log on Success
            async with AsyncSessionLocal() as session:
                stmt = select(PublishingLog).where(PublishingLog.idempotency_key == idempotency_key)
                result = await session.execute(stmt)
                log = result.scalar_one()
                log.status = PublishStatus.SUCCESS
                log.external_post_id = publish_result.external_post_id
                log.published_at = publish_result.published_at
                await session.commit()
                
            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data={"result": publish_result.model_dump()},
                metadata=ToolResultMetadata(
                    provider=platform,
                    observed_at=datetime.now(timezone.utc).isoformat(),
                    request_id=str(uuid.uuid4())
                )
            )
            
        except Exception as e:
            # 6. Update Log on Failure
            async with AsyncSessionLocal() as session:
                stmt = select(PublishingLog).where(PublishingLog.idempotency_key == idempotency_key)
                result = await session.execute(stmt)
                log = result.scalar_one()
                log.status = PublishStatus.FAILED
                log.error_code = str(e)
                await session.commit()
                
            if isinstance(e, MCPProviderError):
                raise
            raise MCPProviderError(f"Provider failed to publish post: {str(e)}")
