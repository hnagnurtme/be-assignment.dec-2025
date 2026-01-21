"""Project repository interface."""

from abc import abstractmethod

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.repositories.interfaces.base import IRepository


class IProjectRepository(IRepository[Project]):
    """Interface for project repository operations."""

    @abstractmethod
    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Get all projects in an organization."""
        pass

    @abstractmethod
    async def count_by_organization(self, organization_id: int) -> int:
        """Count total projects in an organization."""
        pass

    @abstractmethod
    async def add_member(self, project_id: int, user_id: int) -> ProjectMember:
        """Add a member to a project."""
        pass

    @abstractmethod
    async def remove_member(self, project_id: int, user_id: int) -> None:
        """Remove a member from a project."""
        pass

    @abstractmethod
    async def get_members(self, project_id: int) -> list[User]:
        """Get all members of a project."""
        pass

    @abstractmethod
    async def is_member(self, project_id: int, user_id: int) -> bool:
        """Check if a user is a member of a project."""
        pass

    @abstractmethod
    async def get_user_projects(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """Get all projects a user is a member of."""
        pass

    @abstractmethod
    async def count_user_projects(self, user_id: int) -> int:
        """Count total projects a user is a member of."""
        pass
