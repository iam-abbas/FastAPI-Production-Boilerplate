from fastapi import APIRouter, Depends

from core.fastapi.dependencies.authentication import AuthenticationRequired

from .tasks import task_router

tasks_router = APIRouter()
tasks_router.include_router(
    task_router,
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(AuthenticationRequired)],
)

__all__ = ["tasks_router"]
