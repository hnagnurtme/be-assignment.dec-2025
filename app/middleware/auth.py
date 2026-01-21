from typing import Callable

import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.constants import Messages, ErrorCodes
from app.core.logging import get_logger
from app.services.jwt_service import PyJwtService
from app.schemas import ErrorResponse

logger = get_logger(__name__)

PUBLIC_PATHS = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
    "/api/v1/health/db",
    "/api/v1/health/redis",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
]


class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self._jwt_service = PyJwtService()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        path = request.url.path


        if self._is_public_path(path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._unauthorized_response(Messages.UNAUTHORIZED, request_id)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return self._unauthorized_response(Messages.UNAUTHORIZED, request_id)

        token = parts[1]
        try:
            payload = self._jwt_service.decode_token(token)
            user_id = payload.get("sub")
            token_type = payload.get("type")

            if user_id is None:
                return self._unauthorized_response(Messages.UNAUTHORIZED, request_id)

            if token_type != "access":
                return self._unauthorized_response(Messages.UNAUTHORIZED, request_id)

            request.state.user_id = int(user_id)

        except jwt.ExpiredSignatureError:
            return self._unauthorized_response(Messages.UNAUTHORIZED, request_id)

        except jwt.InvalidTokenError as e:
            logger.warning(
                "Invalid token",
                request_id=request_id,
                error=str(e),
                path=path,
            )
            return self._unauthorized_response(Messages.UNAUTHORIZED, request_id)

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        if path in PUBLIC_PATHS:
            return True
        if path.startswith("/docs") or path.startswith("/redoc"):
            return True
        return False

    def _unauthorized_response(self, message: str, request_id: str) -> JSONResponse:
        logger.warning(
            "Authentication failed",
            request_id=request_id,
            message=message,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(
                message=message,
                error_code=ErrorCodes.UNAUTHORIZED,
            ).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
