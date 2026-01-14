"""User repository - data access for User entities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.interfaces import IUserRepository


class UserRepository(BaseRepository[User], IUserRepository):
    """Repository for User entity data access.
    
    Implements IUserRepository interface.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, User)

    async def get_by_id(self, id: int) -> User | None:
        """Get user by ID with organization loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.organization))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address with organization loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.organization))
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all users in an organization."""
        result = await self.db.execute(
            select(User)
            .where(User.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
