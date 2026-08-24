from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import httpx
from app.database import get_db
from app.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/health", tags=["health"])

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check of all services"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=2.0
            )
            if response.status_code == 200:
                health_status["services"]["ollama"] = "ok"
            else:
                health_status["services"]["ollama"] = f"error: {response.status_code}"
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["ollama"] = f"error: {str(e)}"
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    return health_status

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe"""
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"ready": False, "error": str(e)}

@router.get("/live")
async def liveness_check():
    """Liveness probe"""
    return {"alive": True, "timestamp": datetime.utcnow().isoformat()}