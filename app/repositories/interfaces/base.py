from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")


class IRepository(ABC, Generic[ModelType]):
    @abstractmethod
    async def get_by_id(self, id: int) -> ModelType | None:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def create(self, entity: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def update(self, entity: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, entity: ModelType) -> None:
        pass

    @abstractmethod
    async def exists(self, id: int) -> bool:
        pass