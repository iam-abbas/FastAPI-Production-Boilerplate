from enum import Enum
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base
from core.database.mixins import TimestampMixin
from core.security.access_control import (
    Allow,
    Authenticated,
    RolePrincipal,
    UserPrincipal,
)


class TaskPermission(Enum):
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    DELETE = "delete"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    task_author_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author = relationship("User", back_populates="tasks", uselist=False, lazy="raise")

    __mapper_args__ = {"eager_defaults": True}

    def __acl__(self):
        basic_permissions = [TaskPermission.CREATE]
        self_permissions = [
            TaskPermission.READ,
            TaskPermission.EDIT,
            TaskPermission.DELETE,
        ]
        all_permissions = list(TaskPermission)

        return [
            (Allow, Authenticated, basic_permissions),
            (Allow, UserPrincipal(self.task_author_id), self_permissions),
            (Allow, RolePrincipal("admin"), all_permissions),
        ]
