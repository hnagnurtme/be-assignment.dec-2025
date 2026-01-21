from abc import abstractmethod
from app.models.attachment import Attachment
from app.repositories.interfaces.base import IRepository


class IAttachmentRepository(IRepository[Attachment]):
    """Interface for attachment repository."""

    @abstractmethod
    async def get_by_task(self, task_id: int) -> list[Attachment]:
        """Get all attachments for a task."""
        pass

    @abstractmethod
    async def count_by_task(self, task_id: int) -> int:
        """Count attachments for a task."""
        pass
