import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.post import Post, PostStatus
from app.models.publishing_log import PublishingLog, PublishStatus
from app.services.analytics_service import AnalyticsService
from app.mcp.client.client import MCPClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def process_analytics_for_published_posts():
    """Fetches published posts that need metrics refresh and processes them."""
    async with AsyncSessionLocal() as session:
        # We need to find published posts that haven't been updated in a while.
        # For simplicity in this implementation, we grab recent published posts.
        # In a production system, you'd use a robust collection window strategy.
        
        # Find published posts from the last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        stmt = (
            select(Post)
            .options(selectinload(Post.project))
            .where(
                Post.status == PostStatus.PUBLISHED,
                Post.published_at >= thirty_days_ago,
                Post.external_post_id.is_not(None)
            )
            .limit(50)
            .with_for_update(skip_locked=True)
        )
        
        result = await session.execute(stmt)
        published_posts = result.scalars().all()
        
        if not published_posts:
            return
            
        from app.mcp.client.client import get_default_mcp_client
        mcp_client = get_default_mcp_client()
        # Ensure MCP servers are initialized (in a real worker this would happen once at startup)
        # We will assume mcp_client works or we'll just initialize it here for safety
        
        service = AnalyticsService(session=session, mcp_client=mcp_client)
        
        for post in published_posts:
            try:
                # We could add an idempotency check here: 
                # Did we collect analytics for this post in the last 1 hour?
                # If so, skip. (Leaving for simple demo).
                
                logger.info(f"Collecting analytics for post {post.id}...")
                await service.record_snapshot(post_id=post.id, workspace_id=post.project.workspace_id)
                logger.info(f"Successfully recorded analytics for post {post.id}")
            except Exception as e:
                logger.error(f"Failed to collect analytics for post {post.id}: {e}")

shutdown_event = asyncio.Event()

def handle_shutdown(sig, frame):
    logger.info(f"Received signal {sig}. Shutting down gracefully...")
    shutdown_event.set()

async def analytics_worker_loop(interval_seconds: int = 3600):
    """Main loop for the analytics worker."""
    logger.info("Analytics worker started.")
    
    import signal
    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: shutdown_event.set())
    except NotImplementedError:
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    while not shutdown_event.is_set():
        try:
            await process_analytics_for_published_posts()
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
        
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
            
    logger.info("Analytics worker stopped cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(analytics_worker_loop())
    except KeyboardInterrupt:
        logger.info("Analytics worker stopped.")
