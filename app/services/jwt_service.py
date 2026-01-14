"""PyJWT implementation of IJwtService."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import settings
from app.services.interfaces import IJwtService


class PyJwtService(IJwtService):
    """JWT service implementation using PyJWT library.
    
    Handles access token and refresh token creation/validation.
    """

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
        refresh_token_expire_days: int | None = None,
    ) -> None:
        self._secret_key = secret_key or settings.jwt_secret_key
        self._algorithm = algorithm or settings.jwt_algorithm
        self._access_expire = access_token_expire_minutes or settings.jwt_access_token_expire_minutes
        self._refresh_expire = refresh_token_expire_days or settings.jwt_refresh_token_expire_days

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        # Ensure subject is a string (JWT standard)
        if "sub" in to_encode:
            to_encode["sub"] = str(to_encode["sub"])
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._access_expire)
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        })
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        
        # Ensure subject is a string (JWT standard)
        if "sub" in to_encode:
            to_encode["sub"] = str(to_encode["sub"])
        
        expire = datetime.now(timezone.utc) + timedelta(days=self._refresh_expire)
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        })
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token."""
        return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

    def get_subject(self, token: str) -> str | None:
        """Extract subject (user ID) from token."""
        try:
            payload = self.decode_token(token)
            return payload.get("sub")
        except jwt.InvalidTokenError:
            return None
