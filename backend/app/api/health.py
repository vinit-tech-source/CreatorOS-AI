from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.redis import redis_manager

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check(session: AsyncSession = Depends(get_db)):
    # Check Redis
    redis_healthy = await redis_manager.check_health()
    
    # Check Database
    db_healthy = False
    try:
        await session.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        pass

    # Overall Status
    is_healthy = redis_healthy and db_healthy
    
    return {
        "status": "healthy" if is_healthy else "degraded", 
        "service": "CreatorOS AI API",
        "redis_connected": redis_healthy,
        "database_connected": db_healthy
    }
