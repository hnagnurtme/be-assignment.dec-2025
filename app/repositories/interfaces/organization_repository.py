from abc import abstractmethod

from app.models.organization import Organization
from app.repositories.interfaces.base import IRepository


class IOrganizationRepository(IRepository[Organization]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Organization | None:
        pass    
    @abstractmethod
    async def name_exists(self, name: str) -> bool:
        pass
    @abstractmethod
    async def add_user_to_organization(self, organization_id: int, user_id: int) -> Organization | None:
        pass