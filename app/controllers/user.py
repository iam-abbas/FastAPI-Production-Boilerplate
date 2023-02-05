from pydantic import EmailStr

from app.models import User
from app.repositories import TaskRepository, UserRepository
from core.controller import BaseController
from core.database import Propagation, Transactional
from core.exceptions import UnprocessableEntity


class UserController(BaseController[User]):
    def __init__(
        self, user_repository: UserRepository, task_repository: TaskRepository
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.task_repository = task_repository

    @Transactional(propagation=Propagation.REQUIRED)
    async def register(self, email: EmailStr, password: str, username: str) -> User:
        # Check if user exists with email
        user = await self.user_repository.get_by_email(email)

        if user:
            raise UnprocessableEntity("User already exists with this email")

        # Check if user exists with username
        user = await self.user_repository.get_by_username(username)

        if user:
            raise UnprocessableEntity("User already exists with this username")

        return await self.user_repository.create(
            {
                "email": email,
                "password": password,
                "username": username,
            }
        )

    async def get_by_username(self, username: str) -> User:
        return await self.user_repository.get_by_username(username)

    async def get_by_email(self, email: str) -> User:
        return await self.user_repository.get_by_email(email)
