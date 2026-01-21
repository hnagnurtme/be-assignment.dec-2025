from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.organization import Organization
from app.repositories.base import BaseRepository
from app.repositories.interfaces import IOrganizationRepository


class OrganizationRepository(BaseRepository[Organization], IOrganizationRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Organization)

    async def get_by_name(self, name: str) -> Organization | None:
        result = await self.db.execute(
            select(Organization).where(Organization.name == name)
        )
        return result.scalar_one_or_none()

    async def name_exists(self, name: str) -> bool:
        result = await self.db.execute(
            select(Organization.id).where(Organization.name == name)
        )
        return result.scalar_one_or_none() is not None

    async def add_user_to_organization(self, organization_id: int, user_id: int):
        organization = await self.db.get(Organization, organization_id)
        if not organization:
            return None
        user = await  self.db.get(User, user_id)
        if not user:
            return None
        organization.users.append(user)
        await self.db.commit()
        await self.db.refresh(organization)

        return organization