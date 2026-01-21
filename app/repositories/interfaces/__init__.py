from app.repositories.interfaces.base import IRepository
from app.repositories.interfaces.organization_repository import IOrganizationRepository
from app.repositories.interfaces.project_repository import IProjectRepository
from app.repositories.interfaces.user_repository import IUserRepository

__all__ = [
    "IRepository",
    "IOrganizationRepository",
    "IProjectRepository",
    "IUserRepository",
]
