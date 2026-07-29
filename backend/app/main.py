from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.redis import redis_manager
from app.api.health import router as health_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup
    await redis_manager.connect()
    yield
    # Application shutdown
    await redis_manager.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(health_router, prefix=settings.API_V1_STR, tags=["System"])
