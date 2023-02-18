from httpx import AsyncClient

from tests.factory.users import create_fake_user


async def _create_user_and_login(
    client: AsyncClient, fake_user=create_fake_user()
) -> None:
    await client.post("/v1/users/", json=fake_user)

    response = await client.post("/v1/users/login", json=fake_user)
    access_token = response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    return None


__all__ = ["_create_user_and_login"]
