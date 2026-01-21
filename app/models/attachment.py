from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


class Attachment(Base):
    __tablename__ = "attachments"

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Foreign Keys
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="attachments")
    user: Mapped["User"] = relationship("User", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, name='{self.file_name}')>"


