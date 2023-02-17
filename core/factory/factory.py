from app.controllers import AuthController, TaskController, UserController
from app.models import Task, User
from app.repositories import TaskRepository, UserRepository


class Factory:
    """
    This is the factory container that will instantiate all the controllers and
    repositories which can be accessed by the rest of the application.
    """

    # Repositories
    task_repository = TaskRepository(Task)
    user_repository = UserRepository(User)

    def get_user_controller(self):
        return UserController(user_repository=self.user_repository)

    def get_task_controller(self):
        return TaskController(task_repository=self.task_repository)

    def get_auth_controller(self):
        return AuthController(user_repository=self.user_repository)
