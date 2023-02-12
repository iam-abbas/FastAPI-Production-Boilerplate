from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from app.models import Task
from core.repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """
    Task repository provides all the database operations for the Task model.
    """

    def get_by_author_id(
        self, author_id: int, join_: set[str] | None = None
    ) -> list[Task]:
        """
        Get all tasks by author id.
        """
        query = self._query(join_)
        query = self._get_by(query, "author_id", author_id)

        return self._all(query)

    def _join_author(self, query: Select) -> Select:
        """
        Join the author relationship.
        """
        return query.options(joinedload(Task.author))
