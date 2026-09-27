"""
app/core/cache.py

Response caching layer using fastapi-cache2 and Redis.
"""
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.core.redis import redis_manager
from redis import asyncio as aioredis
from app.core.config import settings

def init_cache():
    """
    Initialize the FastAPI Cache with our Redis instance.
    Called in the lifespan of the application.
    """
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
