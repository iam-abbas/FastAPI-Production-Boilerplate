from fastapi import APIRouter

from .monitoring import monitoring_router

v1_router = APIRouter()
v1_router.include_router(monitoring_router, prefix="/monitoring")
