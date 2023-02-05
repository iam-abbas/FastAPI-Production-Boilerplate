from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_health(
    app: FastAPI,
    client: TestClient,
):
    response = client.get(
        "v1/monitoring/health",
    )
    assert response.status_code == 200
