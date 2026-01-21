from abc import abstractmethod
from app.models.comment import Comment
from app.repositories.interfaces.base import IRepository


class ICommentRepository(IRepository[Comment]):
    """Interface for comment repository."""

    @abstractmethod
    async def get_by_task(self, task_id: int) -> list[Comment]:
        """Get all comments for a task."""
        pass
