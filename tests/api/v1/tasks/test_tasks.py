import pytest
from httpx import AsyncClient

from tests.factory.tasks import create_fake_task
from tests.utils.login import _create_user_and_login


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, db_session) -> None:
    """Test task creation."""
    await _create_user_and_login(client)

    fake_task = create_fake_task()
    response = await client.post("/v1/tasks/", json=fake_task)
    assert response.status_code == 201
    assert response.json()["title"] == fake_task["title"]
    assert response.json()["description"] == fake_task["description"]
    assert response.json()["uuid"] is not None


@pytest.mark.asyncio
async def test_create_task_with_invalid_title(client: AsyncClient, db_session) -> None:
    """Test task creation with invalid title."""
    await _create_user_and_login(client)

    fake_task = create_fake_task()
    fake_task["title"] = ""

    response = await client.post("/v1/tasks/", json=fake_task)
    assert response.status_code == 422
    assert response.json()["detail"] is not None


@pytest.mark.asyncio
async def test_create_task_with_invalid_description(
    client: AsyncClient, db_session
) -> None:
    """Test task creation with invalid description."""
    await _create_user_and_login(client)

    fake_task = create_fake_task()
    fake_task["description"] = ""

    response = await client.post("/v1/tasks/", json=fake_task)
    assert response.status_code == 422
    assert response.json()["detail"] is not None


@pytest.mark.asyncio
async def get_all_tasks(client: AsyncClient, db_session) -> None:
    """Test get all tasks."""
    await _create_user_and_login(client)

    await client.post("/v1/tasks/", json=create_fake_task())
    await client.post("/v1/tasks/", json=create_fake_task())
    await client.post("/v1/tasks/", json=create_fake_task())

    response = await client.get("/v1/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 3
