"""Core package - exports auth utilities and exceptions."""

from app.core.auth import (
    get_current_user,
    CurrentUser,
    RoleChecker,
    require_admin,
    require_manager,
    require_member,
)
from app.core.exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
)
from app.core.logging import get_logger, setup_logging

__all__ = [
    # Auth
    "get_current_user",
    "CurrentUser",
    "RoleChecker",
    "require_admin",
    "require_manager",
    "require_member",
    # Exceptions
    "AppException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
    # Logging
    "get_logger",
    "setup_logging",
]
