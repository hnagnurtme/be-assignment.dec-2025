"""Abstract base repository with generic CRUD operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Abstract base repository providing common CRUD operations.
    
    This implements the Repository Pattern to separate data access
    from business logic, following SOLID principles:
    - Single Responsibility: Only handles data access
    - Dependency Inversion: Services depend on abstractions
    """

    def __init__(self, db: AsyncSession, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get entity by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get all entities with pagination."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total entities."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0

    async def create(self, entity: ModelType) -> ModelType:
        """Create a new entity."""
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """Update an existing entity."""
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Delete an entity."""
        await self.db.delete(entity)
        await self.db.flush()

    async def exists(self, id: int) -> bool:
        """Check if entity exists by ID."""
        result = await self.db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None
