import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get(
        "v1/monitoring/health/",
    )
    assert response.status_code == 200
