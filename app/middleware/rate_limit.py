"""Rate limiting middleware using in-memory or Redis backend."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.constants import Messages, ErrorCodes
from app.core.logging import get_logger
from app.schemas import ErrorResponse

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests.
    
    Implements sliding window rate limiting per IP address.
    Can be configured per endpoint or globally.
    
    Default: 100 requests per minute per IP.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        burst_limit: int = 20,
    ) -> None:
        super().__init__(app)
        self._requests_per_minute = requests_per_minute
        self._burst_limit = burst_limit
        self._window_size = 60  # 1 minute in seconds
        
        # In-memory storage: {ip: [(timestamp, count), ...]}
        self._request_counts: dict[str, list[float]] = defaultdict(list)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> JSONResponse:
        # Get client IP
        client_ip = self._get_client_ip(request)
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Check rate limit
        if not self._is_allowed(client_ip):
            logger.warning(
                "Rate limit exceeded",
                request_id=request_id,
                client_ip=client_ip,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=ErrorResponse(
                    message="Too many requests. Please try again later.",
                    error_code=ErrorCodes.SERVICE_UNAVAILABLE,
                ).model_dump(),
                headers={
                    "Retry-After": str(self._window_size),
                    "X-RateLimit-Limit": str(self._requests_per_minute),
                },
            )

        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self._requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request, considering proxies."""
        # Check X-Forwarded-For header (from reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

    def _is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit."""
        current_time = time.time()
        window_start = current_time - self._window_size
        
        # Clean old entries
        self._request_counts[client_ip] = [
            ts for ts in self._request_counts[client_ip]
            if ts > window_start
        ]
        
        # Check if under limit
        if len(self._request_counts[client_ip]) >= self._requests_per_minute:
            return False
        
        # Record this request
        self._request_counts[client_ip].append(current_time)
        return True

    def _get_remaining(self, client_ip: str) -> int:
        """Get remaining requests in current window."""
        count = len(self._request_counts.get(client_ip, []))
        return max(0, self._requests_per_minute - count)
