"""Repositories package - exports all repository classes and interfaces."""

from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.interfaces import (
    IRepository,
    IUserRepository,
    IOrganizationRepository,
)

__all__ = [
    # Base
    "BaseRepository",
    # Implementations
    "UserRepository",
    "OrganizationRepository",
    # Interfaces
    "IRepository",
    "IUserRepository",
    "IOrganizationRepository",
]
