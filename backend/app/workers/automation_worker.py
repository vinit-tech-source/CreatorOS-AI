import asyncio
import logging
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.repositories.automation_repository import AutomationRepository
from app.repositories.workspace_repository import WorkspaceRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def process_automations():
    """Fetches active automation rules and executes them."""
    async with AsyncSessionLocal() as session:
        automation_repo = AutomationRepository(session)
        workspace_repo = WorkspaceRepository(session)
        
        try:
            rules = await automation_repo.get_all_active()
        except Exception as e:
            logger.error(f"Error fetching automation rules: {e}")
            return

        for rule in rules:
            logger.info(f"Evaluating automation rule {rule.id}: {rule.name}")
            # Placeholder for actual rule evaluation logic
            # e.g., checking if trigger condition is met
            
            if rule.trigger_type == "RSS_FEED_UPDATE":
                # Logic to fetch RSS, detect new items
                logger.info(f"Checking RSS feed for rule {rule.id}")
            elif rule.trigger_type == "MENTION":
                # Logic to query social platforms for new mentions
                logger.info(f"Checking mentions for rule {rule.id}")
                
            # Logic to execute action if triggered
            if rule.action_type == "GENERATE_DRAFT":
                # Call ContentGenerationService or enqueue job
                pass


shutdown_event = asyncio.Event()

def handle_shutdown(sig, frame):
    logger.info(f"Received signal {sig}. Shutting down gracefully...")
    shutdown_event.set()

async def worker_loop(interval_seconds: int = 60):
    """Main loop for the automation worker."""
    logger.info("Automation worker started.")
    
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
            await process_automations()
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
        
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
            
    logger.info("Automation worker stopped cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Automation worker stopped.")
