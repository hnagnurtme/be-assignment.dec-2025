"""Repository interfaces package - exports all repository interfaces."""

from app.repositories.interfaces.base import IRepository
from app.repositories.interfaces.user_repository import IUserRepository
from app.repositories.interfaces.organization_repository import IOrganizationRepository

__all__ = [
    "IRepository",
    "IUserRepository",
    "IOrganizationRepository",
]
