"""
app/workers/token_refresh_worker.py

Background worker that automatically refreshes expiring social account OAuth tokens.

Runs every TOKEN_REFRESH_INTERVAL_SECONDS (default: 3600 = 1 hour).
On each cycle it calls TokenRefreshService.refresh_all_expiring() which:
  1. Finds accounts whose tokens expire within TOKEN_REFRESH_BEFORE_EXPIRY_MINUTES
  2. Calls the appropriate OAuth provider refresh endpoint
  3. Re-encrypts and saves the new tokens

Usage (standalone):
    python -m app.workers.token_refresh_worker

Or integrate into FastAPI lifespan via asyncio.create_task().
"""
import asyncio
import logging
import signal

from app.core.database import AsyncSessionLocal
from app.services.token_refresh_service import TokenRefreshService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# How often the worker runs (seconds). 1 hour default.
TOKEN_REFRESH_INTERVAL_SECONDS = 3600

shutdown_event = asyncio.Event()


def handle_shutdown(sig, frame):
    logger.info(f"Token refresh worker received signal {sig}. Shutting down...")
    shutdown_event.set()


async def run_refresh_cycle():
    """Run a single refresh cycle within a fresh DB session."""
    async with AsyncSessionLocal() as session:
        service = TokenRefreshService(session=session)
        try:
            summary = await service.refresh_all_expiring()
            logger.info(f"Token refresh cycle complete: {summary}")
        except Exception as exc:
            logger.error(f"Token refresh cycle error: {exc}", exc_info=True)


async def token_refresh_worker_loop(interval_seconds: int = TOKEN_REFRESH_INTERVAL_SECONDS):
    """
    Main background loop for token refresh.

    Runs immediately on start, then waits `interval_seconds` before running again.
    Stops cleanly when shutdown_event is set.
    """
    logger.info("Token refresh worker started.")

    # Install signal handlers for graceful shutdown
    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown_event.set)
    except (NotImplementedError, AttributeError):
        # Windows does not support add_signal_handler on the event loop
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    while not shutdown_event.is_set():
        await run_refresh_cycle()

        # Wait for next interval (or early exit on shutdown signal)
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass  # Normal — time to run another cycle

    logger.info("Token refresh worker stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(token_refresh_worker_loop())
    except KeyboardInterrupt:
        logger.info("Token refresh worker stopped by keyboard interrupt.")
