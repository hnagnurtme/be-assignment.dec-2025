"""Centralized dependency injection for FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.unit_of_work import UnitOfWork
from app.repositories import (
    IOrganizationRepository,
    IProjectRepository,
    ITaskRepository,
    ICommentRepository,
    IAttachmentRepository,
    IUserRepository,
    OrganizationRepository,
    ProjectRepository,
    TaskRepository,
    CommentRepository,
    AttachmentRepository,
    UserRepository,
)

from app.services.interfaces import IHashService, IJwtService
from app.services.auth_service import AuthService
from app.services.hash_service import BcryptHashService
from app.services.jwt_service import PyJwtService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService


# ============================================================
# Database Dependencies
# ============================================================

async def get_unit_of_work(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UnitOfWork:
    return UnitOfWork(db)


# ============================================================
# Repository Dependencies (return interfaces, not implementations)
# ============================================================

async def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IUserRepository:
    return UserRepository(db)


async def get_organization_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IOrganizationRepository:
    return OrganizationRepository(db)

async def get_project_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IProjectRepository:
    return ProjectRepository(db)


async def get_task_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ITaskRepository:
    return TaskRepository(db)


async def get_comment_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ICommentRepository:
    return CommentRepository(db)


async def get_attachment_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IAttachmentRepository:
    return AttachmentRepository(db)


# ============================================================
# Infrastructure Service Dependencies (Singletons)
# ============================================================



# Singleton instances
_hash_service: IHashService | None = None
_jwt_service: IJwtService | None = None


def get_hash_service() -> IHashService:
    """Get Hash service instance (singleton)."""
    global _hash_service
    if _hash_service is None:
        _hash_service = BcryptHashService()
    return _hash_service


def get_jwt_service() -> IJwtService:
    """Get JWT service instance (singleton)."""
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = PyJwtService()
    return _jwt_service


# ============================================================
# Business Service Dependencies
# ============================================================

async def get_user_service(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    hash_service: Annotated[IHashService, Depends(get_hash_service)],
) -> UserService:
    return UserService(user_repo, hash_service)


async def get_auth_service(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
    org_repo: Annotated[IOrganizationRepository, Depends(get_organization_repository)],
    hash_service: Annotated[IHashService, Depends(get_hash_service)],
    jwt_service: Annotated[IJwtService, Depends(get_jwt_service)],
) -> AuthService:
    return AuthService(user_repo, org_repo, hash_service, jwt_service)

async def get_project_service(
    project_repo: Annotated[IProjectRepository, Depends(get_project_repository)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> ProjectService:
    return ProjectService(project_repo, user_repo)


async def get_task_service(
    task_repo: Annotated[ITaskRepository, Depends(get_task_repository)],
    project_repo: Annotated[IProjectRepository, Depends(get_project_repository)],
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],
    attachment_repo: Annotated[IAttachmentRepository, Depends(get_attachment_repository)],
) -> TaskService:
    return TaskService(task_repo, project_repo, comment_repo, attachment_repo)


# ============================================================
# Type Aliases for Clean Dependency Injection
# ============================================================

# Database
UoW = Annotated[UnitOfWork, Depends(get_unit_of_work)]

# Repositories (interface types)
UserRepo = Annotated[IUserRepository, Depends(get_user_repository)]
OrgRepo = Annotated[IOrganizationRepository, Depends(get_organization_repository)]
ProjectRepo = Annotated[IProjectRepository, Depends(get_project_repository)]
TaskRepo = Annotated[ITaskRepository, Depends(get_task_repository)]
CommentRepo = Annotated[ICommentRepository, Depends(get_comment_repository)]
AttachmentRepo = Annotated[IAttachmentRepository, Depends(get_attachment_repository)]

# Infrastructure Services
HashSvc = Annotated[IHashService, Depends(get_hash_service)]
JwtSvc = Annotated[IJwtService, Depends(get_jwt_service)]

# Business Services
UserSvc = Annotated[UserService, Depends(get_user_service)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
ProjectSvc = Annotated[ProjectService, Depends(get_project_service)]
TaskSvc = Annotated[TaskService, Depends(get_task_service)]
