import pytest
import pytest_asyncio
from faker import Faker

from app.models import User
from core.repository import BaseRepository

fake = Faker()


class TestBaseRepository:
    @pytest_asyncio.fixture
    async def repository(self, db_session):
        return BaseRepository(model=User, db_session=db_session)

    @pytest.mark.asyncio
    async def test_create(self, repository):
        user = await repository.create(self._user_data_generator())
        await repository.session.commit()
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_get_all(self, repository):
        await repository.create(self._user_data_generator())
        await repository.create(self._user_data_generator())
        users = await repository.get_all()
        assert len(users) == 2

    def _user_data_generator(self):
        return {
            "email": fake.email(),
            "username": fake.user_name(),
            "password": fake.password(),
        }
