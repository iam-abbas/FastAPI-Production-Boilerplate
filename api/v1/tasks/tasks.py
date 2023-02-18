from typing import Callable

from fastapi import APIRouter, Depends, Request

from app.controllers import TaskController
from app.models.task import TaskPermission
from app.schemas.requests.tasks import TaskCreate
from app.schemas.responses.tasks import TaskResponse
from core.factory import Factory
from core.fastapi.dependencies.permissions import Permissions

task_router = APIRouter()


@task_router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    request: Request,
    task_controller: TaskController = Depends(Factory().get_task_controller),
    assert_access: Callable = Depends(Permissions(TaskPermission.READ)),
) -> list[TaskResponse]:
    tasks = await task_controller.get_by_author_id(request.user.id)

    assert_access(tasks)
    return tasks


@task_router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    request: Request,
    task_create: TaskCreate,
    task_controller: TaskController = Depends(Factory().get_task_controller),
) -> TaskResponse:
    task = await task_controller.add(
        title=task_create.title,
        description=task_create.description,
        author_id=request.user.id,
    )
    return task


@task_router.get("/{task_uuid}", response_model=TaskResponse)
async def get_task(
    task_uuid: str,
    task_controller: TaskController = Depends(Factory().get_task_controller),
    assert_access: Callable = Depends(Permissions(TaskPermission.READ)),
) -> TaskResponse:
    task = await task_controller.get_by_uuid(task_uuid)

    assert_access(task)
    return task
