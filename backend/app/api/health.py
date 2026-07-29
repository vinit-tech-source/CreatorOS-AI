from fastapi import APIRouter
from app.core.redis import redis_manager

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    redis_healthy = await redis_manager.check_health()
    return {
        "status": "healthy" if redis_healthy else "degraded", 
        "service": "CreatorOS AI API",
        "redis_connected": redis_healthy
    }
