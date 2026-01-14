"""Schemas package - exports all Pydantic schemas."""

from app.schemas.common import (
    ApiResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    create_pagination_meta,
)
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
)
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserCreate,
    OrganizationInfo,
)

__all__ = [
    # Common
    "ApiResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "create_pagination_meta",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    # User
    "UserResponse",
    "UserUpdate",
    "UserCreate",
    "OrganizationInfo",
]
