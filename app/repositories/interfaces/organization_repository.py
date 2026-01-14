"""Abstract interface for Organization repository operations."""

from abc import abstractmethod

from app.models.organization import Organization
from app.repositories.interfaces.base import IRepository


class IOrganizationRepository(IRepository[Organization]):
    """Interface for Organization repository operations.
    
    Extends generic IRepository with Organization-specific methods.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Organization | None:
        """Get organization by name."""
        pass

    @abstractmethod
    async def name_exists(self, name: str) -> bool:
        """Check if organization name already exists."""
        pass
