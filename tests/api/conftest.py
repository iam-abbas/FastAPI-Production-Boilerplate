import asyncio
import os
from typing import Any, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.models import Base
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


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    async_session_factory = sessionmaker(
        class_=AsyncSession,
        sync_session_class=async_scoped_session,
        expire_on_commit=False,
        bind=engine,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.MetaData().create_all)

    async_session = async_session_factory()
    async with async_session.begin():
        try:
            yield async_session
        finally:
            await async_session.close()
            Base.metadata.drop_all(engine)


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    """
    Create a new FastAPI AsyncClient
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
