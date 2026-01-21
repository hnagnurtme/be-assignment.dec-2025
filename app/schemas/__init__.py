"""Pydantic schemas for request/response validation."""

from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import (
    ApiResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    create_pagination_meta,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.task import (
    AttachmentResponse,
    CommentCreate,
    CommentResponse,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import OrganizationInfo, UserCreate, UserResponse, UserUpdate

__all__ = [
    # Auth
    "LoginRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenResponse",
    # Common
    "ApiResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "create_pagination_meta",
    # Project
    "ProjectCreate",
    "ProjectListResponse",
    "ProjectMemberAdd",
    "ProjectMemberResponse",
    "ProjectResponse",
    "ProjectUpdate",
    # Task
    "AttachmentResponse",
    "CommentCreate",
    "CommentResponse",
    "TaskCreate",
    "TaskResponse",
    "TaskStatusUpdate",
    "TaskUpdate",
    # User
    "OrganizationInfo",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
]
