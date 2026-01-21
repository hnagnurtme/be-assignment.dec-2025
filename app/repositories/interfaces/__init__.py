from app.repositories.interfaces.attachment_repository import IAttachmentRepository
from app.repositories.interfaces.base import IRepository
from app.repositories.interfaces.comment_repository import ICommentRepository
from app.repositories.interfaces.organization_repository import IOrganizationRepository
from app.repositories.interfaces.project_repository import IProjectRepository
from app.repositories.interfaces.task_repository import ITaskRepository
from app.repositories.interfaces.user_repository import IUserRepository

__all__ = [
    "IAttachmentRepository",
    "ICommentRepository",
    "IRepository",
    "IOrganizationRepository",
    "IProjectRepository",
    "ITaskRepository",
    "IUserRepository",
]
