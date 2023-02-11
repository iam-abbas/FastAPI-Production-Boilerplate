from fastapi import APIRouter, Depends

from app.controllers import UserController
from app.models.user import UserPermission
from app.schemas.extras.token import Token
from app.schemas.requests.users import LoginUserRequest, RegisterUserRequest
from app.schemas.responses.users import UserResponse
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationRequired
from core.security import AccessControl, Everyone

user_router = APIRouter()


def get_user_principals():
    return [Everyone]


Permissions = AccessControl(user_principals_getter=get_user_principals)


@user_router.get("/", dependencies=[Depends(AuthenticationRequired())])
async def get_users(
    user_controller: UserController = Depends(Factory().get_user_controller),
    enforce: AccessControl = Depends(Permissions.enforce(UserPermission.READ)),
) -> list[UserResponse]:
    users = await user_controller.get_multi()
    enforce(users)
    return users


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


@user_router.post("/login")
async def login_user(
    login_user_request: LoginUserRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> Token:
    return await user_controller.login(
        email=login_user_request.email, password=login_user_request.password
    )
