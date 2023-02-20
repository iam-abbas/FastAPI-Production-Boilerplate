## FastAPI Production Template

A scalable and production ready boilerplate for FastAPI

### Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation Guide](#installation-guide)
- [Usage Guide](#usage-guide)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

### Project Overview

This boilerplate follows a layered architecture that includes a model layer, a repository layer, a controller layer, and an API layer. Its directory structure is designed to isolate boilerplate code within the core directory, which requires minimal attention, thereby facilitating quick and easy feature development. The directory structure is also generally very predictable. The project's primary objective is to offer a production-ready boilerplate with a better developer experience and readily available features. It also has some widely used features like authentication, authorization, database migrations, type checking, etc which are discussed in detail in the [Features](#features) section.

### Features

- Python 3.11+ support
- SQLAlchemy 2.0+ support
- Asynchoronous capabilities
- Database migrations using Alembic
- Basic Authentication using JWT
- Row Level Access Control for permissions
- Redis for caching
- Celery for background tasks
- Testing suite
- Type checking using mypy
- Dockerized database and redis
- Readily available CRUD operations
- Linting using pylint
- Formatting using black

### Installation Guide

You need following to run this project:

- Python 3.11
- [Docker with Docker Compose](https://docs.docker.com/compose/install/)
- [Poetry](https://python-poetry.org/docs/#installation)

I use [asdf](https://asdf-vm.com/#/) to manage my python versions. You can use it too. However, it is only supported on Linux and macOS. For Windows, you can use something like pyenv.

Once you have installed the above and have cloned the repository, you can follow the following steps to get the project up and running:

1. Create a virtual environment using poetry:

```bash
poetry shell
```

2. Install the dependencies:

```bash
poetry install
```

3. Run the database and redis containers:

```bash
docker-compose up -d
```

4. Copy the `.env.example` file to `.env` and update the values as per your needs.

5. Run the migrations:

```bash
make migrate
```

6. Run the server:

```bash
make run
```

The server should now be running on `http://localhost:8000` and the API documentation should be available at `http://localhost:8000/docs`.

### Usage Guide

The project is designed to be modular and scalable. There are 3 main directories in the project:

1. `core`: This directory contains the central part of this project. It contains most of the boiler plate code like security dependencies, database connections, configuration, middlewares etc. It also contains the base classes for the models, repositories, and controllers. The `core` directory is designed to be as minimal as possible and usually requires minimal attention. Overall, the `core` directory is designed to be as generic as possible and can be used in any project. While building additional feature you may not need to modify this directory at all except for adding more controllers to the `Factory` class in `core/factory.py`.

2. `app`: This directory contains the actual application code. It contains the models, repositories, controllers, and schemas for the application. This is the directory you will be spending most of your time in while building features. The directory has following sub-directories:

   - `models` Here is where you add new tables
   - `repositories` For each model, you need to create a repository. This is where you add the CRUD operations for the model.
   - `controllers` For each logical unit of the application, you need to create a controller. This is where you add the business logic for the application.
   - `schemas` This is where you add the schemas for the application. The schemas are used for validation and serialization/deserialization of the data.

3. `api`: This directory contains the API layer of the application. It contains the API router, it is where you add the API endpoints.

### Advanced Usage

The boilerplate contains a lot of features some of which are used in the application and some of which are not. The following sections describe the features in detail.

#### Database Migrations

The migrations are handled by Alembic. The migrations are stored in the `migrations` directory. To create a new migration, you can run the following command:

```bash
make generate-migration
```

It will ask you for a message for the migration. Once you enter the message, it will create a new migration file in the `migrations` directory. You can then run the migrations using the following command:

```bash
make migrate
```

If you need to downgrade the database or reset it. You can use `make rollback` and `make reset-database` respectively.

#### Authentication

The authentication used is basic implementation of JWT with bearer token. When the `bearer` token is supplied in the `Authorization` header, the token is verified and the user is automatically authenticated by setting `request.user.id` using middleware. To use the user model in any endpoint you can use the `get_current_user` dependency. If for any endpoint you want to enforce authentication, you can use the `AuthenticationRequired` dependency. It will raise a `HTTPException` if the user is not authenticated.

#### Row Level Access Control

The boilerplate contains a custom row level permissions management module. It is inspired by [fastapi-permissions](https://github.com/holgi/fastapi-permissions). It is located in `core/security/access_control.py`. You can use this to enforce different permissions for different models. The module operates based on `Principals` and `permissions`. Every user has their own set of principals which need to be set using a function. Check `core/fastapi/dependencies/permissions.py` for an example. The principals are then used to check the permissions for the user. The permissions need to be defined at the model level. Check `app/models/user.py` for an example. Then you can use the dependency directly in the route to raise a `HTTPException` if the user does not have the required permissions. Below is an incomplete example:

```python
from fastapi import APIRouter, Depends
from core.security.access_control import AccessControl, UserPrincipal, RolePrincipal, Allow
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)

    def __acl__(self):
        return [
            (Allow, UserPrincipal(self.id), "view"),
            (Allow, RolePrincipal("admin"), "delete"),
        ]

def get_user_principals(user: User = Depends(get_current_user)):
    return [UserPrincipal(user.id)]

Permission = AccessControl(get_user_principals)

router = APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: int, user: User = get_user(user_id), assert_access = Permission("view")):
    assert_access(user)
    return user

```

#### Caching

You can directly use the `Cache.cached` decorator from `core.cache`. Example

```python
from core.cache import Cache

@Cache.cached(prefix="user", ttl=60)
def get_user(user_id: int):
    ...
```

#### Celery

The celery worker is already configured for the app. You can add your tasks in `worker/` to run the celery worker, you can run the following command:

```bash
make celery-worker
```

#### Session Management

The sessions are already handled by the middleware and `get_session` dependency which injected into the repositories through fastapi dependency injection inside the `Factory` class in `core/factory.py`. There is also `Transactional` decorator which can be used to wrap the functions which need to be executed in a transaction. Example:

```python
@Transactional()
async def some_mutating_function():
    ...
```

Note: The decorator already handles the commit and rollback of the transaction. You do not need to do it manually.

If for any case you need an isolated sessions you can use `standalone_session` decorator from `core.database`. Example:

```python
@standalone_session
async def do_something():
    ...
```

#### Repository Pattern

The boilerplate uses the repository pattern. Every model has a repository and all of them inherit `base` repository from `core/repository`. The repositories are located in `app/repositories`. The repositories are injected into the controllers inside the `Factory` class in `core/factory/factory.py.py`.

The base repository has the basic crud operations. All customer operations can be added to the specific repository. Example:

```python
from core.repository import BaseRepository
from app.models.user import User
from sqlalchemy.sql.expression import select

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str):
        return await select(User).filter(User.email == email).gino.first()

```

To facilitate easier access to queries with complex joins, the `BaseRepository` class has a `_query` function (along with other handy functions like `_all()` and `_one_or_none()`) which can be used to write compplex queries very easily. Example:

```python
async def get_user_by_email_join_tasks(email: str):
    query = await self._query(join_)
    query = query.filter(User.email == email)
    return await self._one_or_none(query)
```

Note: For every join you want to make you need to create a function in the same repository with pattern `_join_{name}`. Example: `_join_tasks` for `tasks`. Example:

```python
async def _join_tasks(self, query: Select) -> Select:
    return query.options(joinedload(User.tasks))
```

#### Controllers

Kind of to repositories, every logical unit of the application has a controller. The controller also has a primary repository which is injected into it. The controllers are located in `app/controllers`.

These controllers contain all the business logic of the application. Check `app/controllers/auth.py` for an example.

#### Schemas

The schemas are located in `app/schemas`. The schemas are used to validate the request body and response body. The schemas are also used to generate the OpenAPI documentation. The schemas are inherited from `BaseModel` from `pydantic`. The schemas are primarily isolated into `requests` and `responses` which are pretty self explainatory.

#### Formatting

You can use `make format` to format the code using `black` and `isort`.

#### Linting

You can use `make lint` to lint the code using `pylint`.

#### Testing

The project contains tests for all endpoints, some of the logical components like `JWTHander` and `AccessControl` and an example of testing complex inner components like `BaseRepository`. The tests are located in `tests/`. You can run the tests using `make test`.

## Contributing

Contributions are higly welcome. Please open an issue or a PR if you want to contribute.

## License

This project is licensed under the terms of the MIT license. See the LICENSE file.

## Acknowledgements

- This project uses several components from [teamhide/fastapi-boilerplate](https://github.com/teamhide/fastapi-boilerplate)
- The row level access control is inspired by [fastapi-permissions](https://github.com/holgi/fastapi-permissions)
- CRUD pattern is inspired by [full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql)
