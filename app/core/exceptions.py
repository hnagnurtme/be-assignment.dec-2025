"""Custom application exceptions."""

from typing import Any


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details
        super().__init__(self.message)


class BadRequestException(AppException):
    """400 Bad Request."""

    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 400, "BAD_REQUEST", details)


class UnauthorizedException(AppException):
    """401 Unauthorized."""

    def __init__(
        self,
        message: str = "Unauthorized",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 401, "UNAUTHORIZED", details)


class ForbiddenException(AppException):
    """403 Forbidden."""

    def __init__(
        self,
        message: str = "Access denied",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 403, "FORBIDDEN", details)


class NotFoundException(AppException):
    """404 Not Found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 404, "NOT_FOUND", details)


class ConflictException(AppException):
    """409 Conflict."""

    def __init__(
        self,
        message: str = "Resource already exists",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 409, "CONFLICT", details)


class ValidationException(AppException):
    """422 Validation Error."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 422, "VALIDATION_ERROR", details)
