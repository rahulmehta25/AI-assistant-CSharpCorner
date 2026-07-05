"""
Health check endpoints.
"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends

from core.config import settings
from core.cache import cache, CacheNamespace
from models.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns service status and version.
    """
    checks: Dict[str, bool] = {}

    # Check cache
    try:
        await cache.set(CacheNamespace.CAREER_DATA, "_health_check", "ok", ttl=10)
        cached = await cache.get(CacheNamespace.CAREER_DATA, "_health_check")
        checks["cache"] = cached == "ok"
    except Exception:
        checks["cache"] = False

    # Check AI service availability
    try:
        from services.ai_service import ai_service, LANGCHAIN_AVAILABLE
        checks["ai_service"] = LANGCHAIN_AVAILABLE and bool(settings.openai_api_key)
    except Exception:
        checks["ai_service"] = False

    # Check data modules
    try:
        from modules.data_loader import data_loader
        careers = data_loader.get_all_careers()
        checks["career_data"] = len(careers) > 0
    except Exception:
        checks["career_data"] = False

    # Overall status
    status = "healthy" if all(checks.values()) else "degraded"
    if not any(checks.values()):
        status = "unhealthy"

    return HealthResponse(
        status=status,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        checks=checks,
        environment=settings.environment,
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.
    """
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    """
    return {"alive": True}
