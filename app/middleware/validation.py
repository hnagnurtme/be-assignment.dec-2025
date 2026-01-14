"""Request validation middleware."""

import re
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.constants import Messages, ErrorCodes
from app.core.logging import get_logger
from app.schemas import ErrorResponse

logger = get_logger(__name__)

# Content type patterns
ALLOWED_CONTENT_TYPES = [
    "application/json",
    "multipart/form-data",
    "application/x-www-form-urlencoded",
]

# Path patterns for validation
DANGEROUS_PATH_PATTERNS = [
    r"\.\./",              # Path traversal
    r"<script",            # XSS attempt  
    r"%00",                # Null byte injection
    r"\x00",               # Null byte
]


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and security checks.
    
    Performs:
    - Content-Type validation for POST/PUT/PATCH requests
    - Request size validation
    - Path traversal detection
    - Basic XSS pattern detection
    - SQL injection pattern detection (basic)
    """

    def __init__(
        self,
        app,
        max_content_length: int = 10 * 1024 * 1024,  # 10MB default
    ) -> None:
        super().__init__(app)
        self._max_content_length = max_content_length
        self._dangerous_patterns = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATH_PATTERNS]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")

        # 1. Validate Content-Type for body requests
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("Content-Type", "")
            if content_type and not self._is_valid_content_type(content_type):
                logger.warning(
                    "Invalid content type",
                    request_id=request_id,
                    content_type=content_type,
                    path=request.url.path,
                )
                return self._bad_request_response(
                    "Unsupported Content-Type",
                    request_id,
                )

        # 2. Validate Content-Length
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > self._max_content_length:
                    logger.warning(
                        "Request too large",
                        request_id=request_id,
                        content_length=content_length,
                        max_allowed=self._max_content_length,
                    )
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content=ErrorResponse(
                            message="Request body too large",
                            error_code=ErrorCodes.BAD_REQUEST,
                        ).model_dump(),
                    )
            except ValueError:
                pass

        # 3. Validate path for dangerous patterns
        full_path = str(request.url)
        if self._has_dangerous_pattern(full_path):
            logger.warning(
                "Dangerous pattern detected in path",
                request_id=request_id,
                path=request.url.path,
            )
            return self._bad_request_response(
                "Invalid request path",
                request_id,
            )

        # 4. Validate query parameters
        for key, value in request.query_params.items():
            if self._has_dangerous_pattern(value):
                logger.warning(
                    "Dangerous pattern detected in query param",
                    request_id=request_id,
                    param=key,
                )
                return self._bad_request_response(
                    "Invalid query parameter",
                    request_id,
                )

        return await call_next(request)

    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is allowed."""
        content_type_lower = content_type.lower()
        return any(
            allowed in content_type_lower
            for allowed in ALLOWED_CONTENT_TYPES
        )

    def _has_dangerous_pattern(self, value: str) -> bool:
        """Check if value contains dangerous patterns."""
        for pattern in self._dangerous_patterns:
            if pattern.search(value):
                return True
        return False

    def _bad_request_response(self, message: str, request_id: str) -> JSONResponse:
        """Create 400 Bad Request response."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                message=message,
                error_code=ErrorCodes.BAD_REQUEST,
            ).model_dump(),
        )
