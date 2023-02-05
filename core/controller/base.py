from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

from core.database import Base, Propagation, Transactional
from core.exceptions import NotFoundException
from core.repository import BaseRepository

# pylint: disable=invalid-name
ModelType = TypeVar("ModelType", bound=Base)
UpdateType = TypeVar("UpdateType", bound=BaseModel)


class BaseController(Generic[ModelType, UpdateType]):
    """Base class for data controllers."""

    def __init__(self, model: Type[ModelType], repository: BaseRepository):
        self.model_class = model
        self.repository = repository

    def get(self, id_: int, join_: set[str] | None = None) -> ModelType:
        """Returns the model instance matching the id."""

        db_obj = self.repository.get(id_, join_)
        if not db_obj:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {id_} does not exist"
            )

        return db_obj

    def get_by_uuid(self, uuid: UUID, join_: set[str] | None = None) -> ModelType:
        """Returns the model instance matching the id."""

        db_obj = self.repository.get_by_uuid(uuid, join_)
        if not db_obj:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {uuid} does not exist"
            )
        return db_obj

    def get_multi(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """Returns a list of models based on pagination params."""
        return self.repository.get_multi(skip, limit, join_)

    @Transactional(propagation=Propagation.REQUIRED)
    def create(self, attributes: dict[str, Any]) -> ModelType:
        """Creates a new Sqlalchemy Object"""
        return self.repository.create(attributes)

    @Transactional(propagation=Propagation.REQUIRED)
    def update(self, db_obj: ModelType, update_obj: UpdateType) -> ModelType:
        """Updates a Sqlalchemy from a update Pydantic schema."""

        attributes = BaseController.extract_attributes_from_schema(update_obj)
        return self.repository.update(db_obj, attributes)

    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, model: ModelType) -> bool:
        """Deletes a Sqlalchemy Object"""
        return self.repository.delete(model)

    @staticmethod
    def extract_attributes_from_schema(
        schema: BaseModel, excludes: set = None
    ) -> dict[str, Any]:
        """Returns a dictionary from a Pydantic schema."""

        return schema.dict(exclude=excludes, exclude_unset=True)
