"""Project repository implementation."""

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.interfaces.project_repository import IProjectRepository


class ProjectRepository(BaseRepository[Project], IProjectRepository):
    """Repository for project database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Project)

    async def get_by_id(self, id: int) -> Project | None:
        """Get project by ID with relationships loaded."""
        result = await self.db.execute(
            select(Project)
            .where(Project.id == id)
            .options(
                selectinload(Project.organization),
                selectinload(Project.created_by),
                selectinload(Project.members),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Get all projects in an organization."""
        result = await self.db.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .options(selectinload(Project.created_by))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_organization(self, organization_id: int) -> int:
        """Count total projects in an organization."""
        result = await self.db.execute(
            select(func.count(Project.id))
            .where(Project.organization_id == organization_id)
        )
        return result.scalar_one()

    async def add_member(self, project_id: int, user_id: int) -> ProjectMember:
        """Add a member to a project."""
        member = ProjectMember(project_id=project_id, user_id=user_id)
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(self, project_id: int, user_id: int) -> None:
        """Remove a member from a project."""
        await self.db.execute(
            delete(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        await self.db.flush()

    async def get_members(self, project_id: int) -> list[User]:
        """Get all members of a project."""
        result = await self.db.execute(
            select(User)
            .join(ProjectMember, ProjectMember.user_id == User.id)
            .where(ProjectMember.project_id == project_id)
            .options(selectinload(User.organization))
        )
        return list(result.scalars().all())

    async def is_member(self, project_id: int, user_id: int) -> bool:
        """Check if a user is a member of a project."""
        result = await self.db.execute(
            select(ProjectMember.project_id).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_projects(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Get all projects a user is a member of."""
        result = await self.db.execute(
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
            .options(selectinload(Project.created_by))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_user_projects(self, user_id: int) -> int:
        """Count total projects a user is a member of."""
        result = await self.db.execute(
            select(func.count(Project.id))
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
        )
        return result.scalar_one()

    async def get_by_name_for_user(self, name: str, user_id: int) -> Project | None:
        """Get project by name (case-insensitive) that user is a member of."""
        result = await self.db.execute(
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                ProjectMember.user_id == user_id,
                func.lower(Project.name) == name.lower()
            )
            .options(selectinload(Project.created_by))
        )
        return result.scalar_one_or_none()

