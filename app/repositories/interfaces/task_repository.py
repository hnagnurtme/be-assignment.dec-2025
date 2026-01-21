from abc import abstractmethod
from app.models.task import Task, TaskStatus, TaskPriority
from app.repositories.interfaces.base import IRepository


class ITaskRepository(IRepository[Task]):
    """Interface for task repository."""

    @abstractmethod
    async def get_by_project(
        self,
        project_id: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        """Get tasks in a project with filters and pagination."""
        pass

    @abstractmethod
    async def count_by_project(
        self,
        project_id: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
    ) -> int:
        """Count tasks in a project with filters."""
        pass

    @abstractmethod
    async def get_overdue_tasks(self, project_id: int) -> list[Task]:
        """Get overdue tasks in a project."""
        pass

    @abstractmethod
    async def count_by_status(self, project_id: int) -> dict[str, int]:
        """Count tasks by status for a project."""
        pass
