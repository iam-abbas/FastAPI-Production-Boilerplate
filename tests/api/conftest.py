import asyncio
import os
from typing import Any, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient

from core.server import create_app

SQLALCHEMY_DATABASE_URL = os.getenv("TEST_POSTGRES_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("TEST_POSTGRES_URL is not set")


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a new FastAPI app
    """
    app = create_app()
    yield app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    """
    Create a new FastAPI AsyncClient
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
