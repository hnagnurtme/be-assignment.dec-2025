from abc import abstractmethod

from app.models.user import User
from app.repositories.interfaces.base import IRepository


class IUserRepository(IRepository[User]):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        pass
    @abstractmethod
    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        pass