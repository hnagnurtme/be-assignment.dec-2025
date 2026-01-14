"""Abstract interface for generic repository operations."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")


class IRepository(ABC, Generic[ModelType]):
    """Interface for generic repository operations.
    
    Defines common CRUD operations that all repositories must implement.
    Follows Interface Segregation Principle.
    """

    @abstractmethod
    async def get_by_id(self, id: int) -> ModelType | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total entities."""
        pass

    @abstractmethod
    async def create(self, entity: ModelType) -> ModelType:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, entity: ModelType) -> ModelType:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity: ModelType) -> None:
        """Delete an entity."""
        pass

    @abstractmethod
    async def exists(self, id: int) -> bool:
        """Check if entity exists by ID."""
        pass
