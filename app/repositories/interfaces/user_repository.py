"""Abstract interface for User repository operations."""

from abc import abstractmethod

from app.models.user import User
from app.repositories.interfaces.base import IRepository


class IUserRepository(IRepository[User]):
    """Interface for User repository operations.
    
    Extends generic IRepository with User-specific methods.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        pass

    @abstractmethod
    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all users in an organization."""
        pass
