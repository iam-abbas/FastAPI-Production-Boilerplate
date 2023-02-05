from fastapi import APIRouter, Depends

from api.v1.users.request import RegisterUserRequest
from api.v1.users.response import UserResponse
from app.controllers import UserController
from core.factory import Factory

user_router = APIRouter()


@user_router.get("/")
async def get_users(
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> list[UserResponse]:
    return await user_controller.get_multi()


@user_router.post("/")
async def register_user(
    register_user_request: RegisterUserRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserResponse:
    return await user_controller.register(
        email=register_user_request.email,
        password=register_user_request.password,
        username=register_user_request.username,
    )
