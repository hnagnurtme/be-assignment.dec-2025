"""Organization model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
    """Organization model - represents a company/team."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
        lazy="selectin",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="organization",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}')>"


# Import at the end to avoid circular imports
from app.models.user import User  # noqa: E402, F401
from app.models.project import Project  # noqa: E402, F401
