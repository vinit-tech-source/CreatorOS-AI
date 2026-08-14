"""
app/workers/scheduler_worker.py

Background worker that periodically checks for due posts and publishes them
by invoking the existing publish_post MCP tool.
"""
import asyncio
import logging
import uuid
import sys
import os
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.services.scheduler_service import SchedulerService
from app.repositories.post_repository import PostRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.models.post import PostStatus, SchedulingStatus
from app.mcp.tools.social.publish_post import PublishPostTool
from app.mcp.exceptions.exceptions import MCPProviderError, MCPAuthenticationError, MCPToolValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def process_due_posts():
    """Fetches due posts and processes them."""
    async with AsyncSessionLocal() as session:
        post_repo = PostRepository(session)
        proj_repo = ProjectRepository(session)
        ws_repo = WorkspaceRepository(session)
        
        service = SchedulerService(
            post_repo=post_repo,
            project_repo=proj_repo,
            workspace_repo=ws_repo
        )
        
        try:
            due_posts = await service.get_due_posts(limit=10)
        except Exception as e:
            logger.error(f"Error fetching due posts: {e}")
            return

        for post in due_posts:
            # Try to claim
            claimed = await service.claim_due_post(post.id)
            if not claimed:
                logger.info(f"Post {post.id} already claimed or no longer due. Skipping.")
                continue
                
            logger.info(f"Processing post {post.id}...")
            
            # Fetch workspace to get workspace_id and social_account_id
            # Wait, the post object doesn't have social_account_id directly.
            # We need to find the social account for the post's platform and workspace.
            # We will use the workspace_id from the project.
            
            project = await proj_repo.get_by_id(post.project_id)
            workspace_id = project.workspace_id
            
            # The prompt says: "Verify social account is active". We can query it here.
            social_repo = SocialAccountRepository(session)
            accounts = await social_repo.get_by_workspace_id(workspace_id)
            
            target_account = None
            for acc in accounts:
                if acc.platform == post.platform and acc.is_active:
                    target_account = acc
                    break
                    
            if not target_account:
                await service.mark_failed(
                    post.id, 
                    reason=f"No active social account found for platform {post.platform}",
                    retry=False
                )
                continue
                
            # Verify post is still approved (already handled by claim query which locks it, but checking just in case)
            if post.status not in (PostStatus.APPROVED, PostStatus.SCHEDULED):
                await service.mark_failed(post.id, reason="Post is no longer in an approved/scheduled state.", retry=False)
                continue

            # Generate unique idempotency key for this attempt
            # The attempt count is retrieved from the DB during claim, we can just use uuid
            idempotency_key = f"sched-{post.id}-{post.scheduled_attempts}-{uuid.uuid4().hex[:8]}"
            
            # Call publish_post MCP tool
            tool = PublishPostTool()
            
            try:
                result = await tool.execute({
                    "workspace_id": str(workspace_id),
                    "social_account_id": str(target_account.id),
                    "post_id": str(post.id),
                    "idempotency_key": idempotency_key
                })
                
                if result.success:
                    logger.info(f"Successfully published post {post.id}")
                    await service.mark_completed(post.id)
                else:
                    logger.error(f"Failed to publish post {post.id}: {result.data}")
                    await service.mark_failed(post.id, reason=str(result.data), retry=True)
                    
            except (MCPAuthenticationError, MCPToolValidationError) as e:
                logger.error(f"Non-retriable error publishing post {post.id}: {e}")
                await service.mark_failed(post.id, reason=str(e), retry=False)
            except MCPProviderError as e:
                logger.error(f"Provider error publishing post {post.id}: {e}")
                # We consider generic provider errors temporary
                await service.mark_failed(post.id, reason=str(e), retry=True)
            except Exception as e:
                logger.error(f"Unexpected error publishing post {post.id}: {e}")
                await service.mark_failed(post.id, reason=str(e), retry=True)


shutdown_event = asyncio.Event()

def handle_shutdown(sig, frame):
    logger.info(f"Received signal {sig}. Shutting down gracefully...")
    shutdown_event.set()

async def worker_loop(interval_seconds: int = 10):
    """Main loop for the scheduler worker."""
    logger.info("Scheduler worker started.")
    
    import signal
    try:
        loop = asyncio.get_running_loop()
        # In Docker, the main process gets SIGTERM. We might also get SIGINT.
        # Note: signal.signal is safer for cross-platform, but asyncio handles it better.
        # But we must register signal handlers via asyncio if supported.
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: shutdown_event.set())
    except NotImplementedError:
        # Windows doesn't support add_signal_handler fully, fallback to signal module
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    while not shutdown_event.is_set():
        try:
            await process_due_posts()
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
        
        # Sleep with a timeout so it can be interrupted by shutdown event
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
            
    logger.info("Scheduler worker stopped cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler worker stopped.")
