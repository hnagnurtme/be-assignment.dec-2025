from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.task import Task, TaskStatus, TaskPriority
from app.repositories.base import BaseRepository
from app.repositories.interfaces.task_repository import ITaskRepository


class TaskRepository(BaseRepository[Task], ITaskRepository):
    """SQLAlchemy implementation of the task repository."""

    def __init__(self, session: Session) -> None:
        super().__init__(Task, session)

    async def get_by_project(
        self,
        project_id: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        query = select(Task).where(Task.project_id == project_id)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)

        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_by_project(
        self,
        project_id: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
    ) -> int:
        query = select(func.count(Task.id)).where(Task.project_id == project_id)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)

        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_overdue_tasks(self, project_id: int) -> list[Task]:
        now = datetime.now()
        query = select(Task).where(
            Task.project_id == project_id,
            Task.due_date < now,
            Task.status != TaskStatus.DONE,
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_by_status(self, project_id: int) -> dict[str, int]:
        query = (
            select(Task.status, func.count(Task.id))
            .where(Task.project_id == project_id)
            .group_by(Task.status)
        )
        result = await self._session.execute(query)
        counts = {status.value: count for status, count in result.all()}
        
        # Ensure all statuses are present
        for status in TaskStatus:
            if status.value not in counts:
                counts[status.value] = 0
                
        return counts
