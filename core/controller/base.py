from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

from core.database import Base, Propagation, Transactional
from core.exceptions import NotFoundException
from core.repository import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class BaseController(Generic[ModelType]):
    """Base class for data controllers."""

    def __init__(self, model: Type[ModelType], repository: BaseRepository):
        self.model_class = model
        self.repository = repository

    async def get_by_id(self, id_: int, join_: set[str] | None = None) -> ModelType:
        """Returns the model instance matching the id."""

        db_obj = await self.repository.get_by(field="id", value=id_, join_=join_)
        if not db_obj:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {id} does not exist"
            )

        return db_obj

    async def get_by_uuid(self, uuid: UUID, join_: set[str] | None = None) -> ModelType:
        """Returns the model instance matching the id."""

        db_obj = await self.repository.get_by(field="uuid", value=uuid, join_=join_)
        if not db_obj:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {uuid} does not exist"
            )
        return db_obj

    async def get_all(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """Returns a list of models based on pagination params."""
        response = await self.repository.get_all(skip, limit, join_)
        return response

    @Transactional(propagation=Propagation.REQUIRED)
    async def create(self, attributes: dict[str, Any]) -> ModelType:
        """Creates a new Sqlalchemy Object"""
        create = await self.repository.create(attributes)
        return create

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete(self, model: ModelType) -> bool:
        """Deletes a Sqlalchemy Object"""
        delete = await self.repository.delete(model)
        return delete

    @staticmethod
    async def extract_attributes_from_schema(
        schema: BaseModel, excludes: set = None
    ) -> dict[str, Any]:
        """Returns a dictionary from a Pydantic schema."""

        return await schema.dict(exclude=excludes, exclude_unset=True)
