"""Comment model."""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    """Comment model for tasks."""

    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Foreign Keys
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    user: Mapped["User"] = relationship("User", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, task_id={self.task_id}, user_id={self.user_id})>"


# Import at the end to avoid circular imports
from app.models.task import Task  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
