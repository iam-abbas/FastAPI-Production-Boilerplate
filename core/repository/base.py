from functools import reduce
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import Select, func
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql.expression import select

from core.database import Base, session

# pylint: disable-next=invalid-name
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.session = session
        self.model_class: Type[ModelType] = model

    async def create(self, attributes: dict[str, Any] = None) -> ModelType:
        """Creates the model instance."""
        if attributes is None:
            attributes = {}
        model = self.model_class(**attributes)
        self.session.add(model)
        return model

    async def get(self, id_: int, join_: set[str] | None = None) -> ModelType | None:
        """Returns the model instance matching the id."""
        query = await self._callable(join_)
        query = await self._get_by(query, "id", id_)

        return await self._one_or_none(query)

    async def get_by_uuid(
        self, uuid: UUID, join_: set[str] | None = None
    ) -> ModelType | None:
        """Returns the model instance matching the uuid."""
        query = await self._callable(join_)
        query = await self._get_by(query, "uuid", uuid)

        return await self._one_or_none(query)

    async def get_multi(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """Returns a list of models based on pagination params."""
        query = await self._callable(join_)
        query = query.offset(skip).limit(limit)

        return await self._all(query)

    async def update(self, model: ModelType, attributes: dict[str, Any]) -> ModelType:
        """Updates the model from attributes."""

        for field in attributes:
            setattr(model, field, attributes[field])

        return model

    async def delete(self, model: ModelType) -> None:
        """Deletes the model."""
        self.session.delete(model)

    async def _callable(
        self,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Select:
        """Returns a callable that can be used to query the model."""
        query = select(self.model_class)
        query = await self._maybe_join(query, join_)
        query = await self._maybe_ordered(query, order_)

        return query

    async def _all(self, query: Select) -> list[ModelType]:
        """Returns all results from the query."""
        if results := await self._maybe_join_collection(query):
            return results

        query = await self.session.scalars(query)
        return query.all()

    async def _first(self, query: Select) -> ModelType | None:
        """Returns the first result from the query."""
        if results := await self._maybe_join_collection(query):
            return next(iter(results), None)

        query = await self.session.scalars(query)
        return query.first()

    async def _one_or_none(self, query: Select) -> ModelType | None:
        """Returns the first result from the query or None."""
        if results := await self._maybe_join_collection(query, limit_one=True):
            return next(iter(results), None)

        query = await self.session.scalars(query)
        return query.one_or_none()

    async def _one(self, query: Select) -> ModelType:
        """
        Returns the first result from the query or raises NoResultFound.
        """
        if results := await self._maybe_join_collection(query, limit_one=True):
            if result := next(iter(results), None):
                return result

            raise NoResultFound

        query = await self.session.scalars(query)
        return query.one()

    async def _count(self, query: Select) -> int:
        """Returns the count of the query."""
        query = query.subquery()
        query = await self.session.scalars(select(func.count()).select_from(query))
        return query.one()

    async def _sort_by(
        self,
        query: Select,
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
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    async def _get_by(self, query: Select, field: str, value: Any) -> Select:
        """Returns the query filtered by the given field and value."""
        return query.filter(getattr(self.model_class, field) == value)

    async def _maybe_join(self, query: Select, join_: set[str] | None = None) -> Select:
        """Returns the query with the given joins."""
        if not join_:
            return query

        if not isinstance(join_, set):
            raise TypeError("join_ must be a set")

        return reduce(self._add_join_to_query, join_, query)

    async def _maybe_ordered(self, query: Select, order_: dict | None = None) -> Select:
        """Returns the query ordered by the given column."""
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(getattr(self.model_class, order).asc())
            else:
                for order in order_["desc"]:
                    query = query.order_by(getattr(self.model_class, order).desc())

        return query

    async def _maybe_join_collection(
        self, query: Select, limit_one: bool = False
    ) -> list[ModelType] | None:
        """Returns the results from the query if it contains a joined collection."""
        execution_options = query.get_execution_options()

        if execution_options.get("contains_joined_collection", False):
            results = self.session.scalars(query).unique().all()

            if limit_one and len(results) > 1:
                raise MultipleResultsFound

            return results
        return None

    async def _add_join_to_query(self, query: Select, join_: set[str]) -> Select:
        return getattr(self, "_join_" + join_)(query)
