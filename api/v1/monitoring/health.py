from fastapi import APIRouter

from api.v1.monitoring.response import Health
from core.config import config

health_router = APIRouter()


@health_router.get("/")
async def health() -> Health:
    return Health(version=config.RELEASE_VERSION, status="Healthy")
