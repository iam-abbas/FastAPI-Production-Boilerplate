from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base
from core.database.mixins import TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    task_author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="tasks", uselist=False, lazy="raise")

    __mapper_args__ = {"eager_defaults": True}
