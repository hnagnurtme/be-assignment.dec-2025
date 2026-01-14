"""Unit of Work pattern for transaction management."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository


class UnitOfWork:
    """Unit of Work pattern for managing database transactions.
    
    Provides:
    - Single point of access to all repositories
    - Transaction management (commit/rollback)
    - Ensures all operations use the same session
    
    Usage:
        async with UnitOfWork(db) as uow:
            user = await uow.users.get_by_id(1)
            await uow.commit()
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users: UserRepository | None = None
        self._organizations: OrganizationRepository | None = None

    @property
    def users(self) -> UserRepository:
        """Get User repository (lazy initialization)."""
        if self._users is None:
            self._users = UserRepository(self._db)
        return self._users

    @property
    def organizations(self) -> OrganizationRepository:
        """Get Organization repository (lazy initialization)."""
        if self._organizations is None:
            self._organizations = OrganizationRepository(self._db)
        return self._organizations

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self._db.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self._db.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
