import os
from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from core.server import create_app

SQLALCHEMY_DATABASE_URL = os.getenv("TEST_POSTGRES_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("TEST_POSTGRES_URL is not set")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)
    _app = create_app()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    with TestClient(app) as client:
        yield client
