from app.controllers import AuthController, TaskController, UserController
from app.models import Task, User
from app.repositories import TaskRepository, UserRepository


class ControllerOverrides:
    def __init__(self, db_session):
        self.db_session = db_session

    def user_controller(self):
        print("\n\n\n OVERRIDE \n\n\n")
        return UserController(UserRepository(model=User, session=self.db_session))

    def task_controller(self):
        return TaskController(TaskRepository(model=Task, session=self.db_session))

    def auth_controller(self):
        return AuthController(UserRepository(model=User, session=self.db_session))
