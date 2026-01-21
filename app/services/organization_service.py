from app.models.organization import Organization
from app.repositories.interfaces import IOrganizationRepository
from app.services.interfaces import IHashService

class OrganizationService:
    def __init__(
        self,
        organization_repository: IOrganizationRepository,
        hash_service: IHashService,
        ):
        self._organization_repo = organization_repository
        self._hash_service = hash_service

    async def get_organization_by_name(self, name: str) -> Organization | None:
        return await self._organization_repo.get_by_name(name)

    async def add_user_to_organization(self , organization_id: int, user_id: int) -> Organization | None :
        return await self._organization_repo.add_user_to_organization(organization_id, user_id)

