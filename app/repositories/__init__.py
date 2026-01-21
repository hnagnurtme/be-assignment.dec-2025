"""Repositories package - exports all repository classes and interfaces."""

from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.base import BaseRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.repositories.interfaces import (
    IRepository,
    IAttachmentRepository,
    ICommentRepository,
    IOrganizationRepository,
    IProjectRepository,
    ITaskRepository,
    IUserRepository,
)

__all__ = [
    # Base
    "BaseRepository",
    # Implementations
    "AttachmentRepository",
    "CommentRepository",
    "OrganizationRepository",
    "ProjectRepository",
    "TaskRepository",
    "UserRepository",
    # Interfaces
    "IRepository",
    "IAttachmentRepository",
    "ICommentRepository",
    "IOrganizationRepository",
    "IProjectRepository",
    "ITaskRepository",
    "IUserRepository",
]
