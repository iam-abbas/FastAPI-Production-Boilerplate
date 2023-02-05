from app.models import Task
from app.repositories import TaskRepository
from core.controller import BaseController


class TaskController(BaseController[Task]):
    """Task controller."""

    def __init__(self, task_repository: TaskRepository):
        super().__init__(model=Task, repository=task_repository)
        self.task_repository = task_repository

    async def get_by_author_id(self, author_id: int) -> list[Task]:
        """Returns a list of tasks based on author_id."""
        return await self.task_repository.get_by_author_id(author_id)
