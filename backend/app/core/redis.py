import logging
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Manages the lifecycle of the Redis connection pool.
    """
    def __init__(self):
        self.client: Optional[Redis] = None

    async def connect(self) -> None:
        """
        Initialize the Redis connection using the configuration URL.
        """
        try:
            self.client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Verify connection immediately
            await self.client.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {settings.REDIS_URL}: {e}")
            raise

    async def close(self) -> None:
        """
        Close the Redis connection pool cleanly.
        """
        if self.client:
            await self.client.aclose()
            logger.info("Redis connection closed.")
            self.client = None

    async def check_health(self) -> bool:
        """
        Utility to verify if the Redis connection is healthy.
        Returns True if responsive, False otherwise.
        """
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception:
            return False


# Global instance to be imported and used across the application
redis_manager = RedisManager()
