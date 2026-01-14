"""Organization repository - data access for Organization entities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.repositories.base import BaseRepository
from app.repositories.interfaces import IOrganizationRepository


class OrganizationRepository(BaseRepository[Organization], IOrganizationRepository):
    """Repository for Organization entity data access.
    
    Implements IOrganizationRepository interface.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Organization)

    async def get_by_name(self, name: str) -> Organization | None:
        """Get organization by name."""
        result = await self.db.execute(
            select(Organization).where(Organization.name == name)
        )
        return result.scalar_one_or_none()

    async def name_exists(self, name: str) -> bool:
        """Check if organization name already exists."""
        result = await self.db.execute(
            select(Organization.id).where(Organization.name == name)
        )
        return result.scalar_one_or_none() is not None
