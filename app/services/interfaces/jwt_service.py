"""Abstract interface for JWT token operations."""

from abc import ABC, abstractmethod
from typing import Any


class IJwtService(ABC):
    """Interface for JWT token service.
    
    Follows Interface Segregation Principle - only JWT operations.
    Implementations can use PyJWT, python-jose, or other libraries.
    """

    @abstractmethod
    def create_access_token(self, data: dict[str, Any]) -> str:
        """Create a new access token.
        
        Args:
            data: Payload data to encode in the token.
            
        Returns:
            Encoded JWT access token string.
        """
        pass

    @abstractmethod
    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Create a new refresh token.
        
        Args:
            data: Payload data to encode in the token.
            
        Returns:
            Encoded JWT refresh token string.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token.
        
        Args:
            token: JWT token string to decode.
            
        Returns:
            Decoded payload dictionary.
            
        Raises:
            Exception: If token is invalid or expired.
        """
        pass

    @abstractmethod
    def get_subject(self, token: str) -> str | None:
        """Extract subject (user ID) from token.
        
        Args:
            token: JWT token string.
            
        Returns:
            Subject string or None if not found.
        """
        pass
