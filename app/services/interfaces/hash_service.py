"""Abstract interface for password hashing operations."""

from abc import ABC, abstractmethod


class IHashService(ABC):
    """Interface for password hashing service.
    
    Follows Interface Segregation Principle - only hashing operations.
    Implementations can use bcrypt, argon2, or any other algorithm.
    """

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plain text password.
        
        Args:
            password: Plain text password to hash.
            
        Returns:
            Hashed password string.
        """
        pass

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash.
        
        Args:
            password: Plain text password to verify.
            hashed: Hashed password to compare against.
            
        Returns:
            True if password matches, False otherwise.
        """
        pass
