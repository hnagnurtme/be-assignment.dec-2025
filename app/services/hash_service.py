"""Bcrypt implementation of IHashService."""

from passlib.context import CryptContext

from app.services.interfaces import IHashService


class BcryptHashService(IHashService):
    """Password hashing service using bcrypt algorithm.
    
    This implementation uses passlib with bcrypt for secure password hashing.
    """

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Hash a plain text password using bcrypt."""
        return self._context.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a bcrypt hash."""
        return self._context.verify(password, hashed)
