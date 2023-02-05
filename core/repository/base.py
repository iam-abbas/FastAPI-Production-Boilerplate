from functools import reduce
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import Select, func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql.expression import select as sqla_select

from core.database import Base

# pylint: disable-next=invalid-name
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model_class: Type[ModelType] = model

    def create(self, attributes: dict[str, Any] = None) -> ModelType:
        """Creates the model instance."""
        if not attributes:
            attributes = {}

        model = self.model_class(**attributes)
        self.db.add(model)

        return model

    def get(self, id_: int, join_: set[str] | None = None) -> ModelType | None:
        """Returns the model instance matching the id."""
        select = self._callable(join_)
        select = self._by_id(select, id_)

        return self._one_or_none(select)

    def get_by_uuid(
        self, uuid: UUID, join_: set[str] | None = None
    ) -> ModelType | None:
        """Returns the model instance matching the uuid."""
        select = self._callable(join_)
        select = self._by_uuid(select, uuid)

        return self._one_or_none(select)

    def get_multi(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """Returns a list of models based on pagination params."""
        select = self._callable(join_)
        select = select.offset(skip).limit(limit)

        return self._all(select)

    def update(self, model: ModelType, attributes: dict[str, Any]) -> ModelType:
        """Updates the model from attributes."""

        for field in attributes:
            setattr(model, field, attributes[field])

        return model

    def delete(self, model: ModelType) -> None:
        """Deletes the model."""
        self.db.delete(model)

    def _callable(
        self,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Select:
        """Returns a callable that can be used to query the model."""
        select = sqla_select(self.model_class)
        select = self._maybe_join(select, join_)
        select = self._maybe_ordered(select, order_)

        return select

    def _all(self, select: Select) -> list[ModelType]:
        """Returns all results from the query."""
        if results := self._maybe_join_collection(select):
            return results

        return self.db.scalars(select).all()

    def _first(self, select: Select) -> ModelType | None:
        """Returns the first result from the query."""
        if results := self._maybe_join_collection(select):
            return next(iter(results), None)

        return self.db.scalars(select).first()

    def _one_or_none(self, select: Select) -> ModelType | None:
        """Returns the first result from the query or None."""
        if results := self._maybe_join_collection(select, limit_one=True):
            return next(iter(results), None)

        return self.db.scalars(select).one_or_none()

    def _one(self, select: Select) -> ModelType:
        """
        Returns the first result from the query or raises NoResultFound.
        """
        if results := self._maybe_join_collection(select, limit_one=True):
            if result := next(iter(results), None):
                return result

            raise NoResultFound

        return self.db.scalars(select).one()

    def _count(self, select: Select) -> int:
        """Returns the count of the query."""
        select = select.subquery()
        return self.db.scalars(sqla_select(func.count()).select_from(select)).one()

    def _sort_by(
        self,
        select: Select,
        sort_by: str,
        order: str | None = "asc",
        model: Type[ModelType] | None = None,
        case_insensitive: bool = False,
    ) -> Select:
        """Returns the query sorted by the given column."""
        model = model or self.model_class

        order_column = None

        if case_insensitive:
            order_column = func.lower(getattr(model, sort_by))
        else:
            order_column = getattr(model, sort_by)

        if order == "desc":
            return select.order_by(order_column.desc())

        return select.order_by(order_column.asc())

    def _by_id(self, select: Select, id_: int) -> Select:
        """Returns the query filtered by the given id."""
        return select.filter(self.model_class.id == id_)

    def _by_uuid(self, select: Select, uuid: str) -> Select:
        """Returns the query filtered by the given uuid."""
        return select.filter(self.model_class.uuid == uuid)

    def _maybe_join(self, select: Select, join_: set[str] | None = None) -> Select:
        """Returns the query with the given joins."""
        if not join_:
            return select

        if not isinstance(join_, set):
            raise TypeError("join_ must be a set")

        return reduce(self._add_join_to_select, join_, select)

    def _maybe_ordered(self, select: Select, order_: dict | None = None) -> Select:
        """Returns the query ordered by the given column."""
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    select = select.order_by(getattr(self.model_class, order).asc())
            else:
                for order in order_["desc"]:
                    select = select.order_by(getattr(self.model_class, order).desc())

        return select

    def _maybe_join_collection(
        self, select: Select, limit_one: bool = False
    ) -> list[ModelType] | None:
        """Returns the results from the query if it contains a joined collection."""
        execution_options = select.get_execution_options()

        if execution_options.get("contains_joined_collection", False):
            results = self.db.scalars(select).unique().all()

            if limit_one and len(results) > 1:
                raise MultipleResultsFound

            return results
        return None

    def _add_join_to_select(self, select: Select, join_: set[str]) -> Select:
        return getattr(self, "_join_" + join_)(select)
