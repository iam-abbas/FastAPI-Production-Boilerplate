from fastapi import APIRouter

from .health import health_router

monitoring_router = APIRouter()
monitoring_router.include_router(health_router, prefix="/health", tags=["health"])

__all__ = ["monitoring_router"]
