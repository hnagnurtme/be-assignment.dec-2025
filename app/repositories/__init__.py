"""Repositories package - exports all repository classes and interfaces."""

from app.repositories.base import BaseRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.repositories.interfaces import (
    IRepository,
    IOrganizationRepository,
    IProjectRepository,
    IUserRepository,
)

__all__ = [
    # Base
    "BaseRepository",
    # Implementations
    "OrganizationRepository",
    "ProjectRepository",
    "UserRepository",
    # Interfaces
    "IRepository",
    "IOrganizationRepository",
    "IProjectRepository",
    "IUserRepository",
]
