from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.repositories.base import BaseRepository
from app.repositories.interfaces.attachment_repository import IAttachmentRepository


class AttachmentRepository(BaseRepository[Attachment], IAttachmentRepository):
    """SQLAlchemy implementation of the attachment repository."""

    def __init__(self, session: Session) -> None:
        super().__init__(Attachment, session)

    async def get_by_task(self, task_id: int) -> list[Attachment]:
        query = select(Attachment).where(Attachment.task_id == task_id)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_by_task(self, task_id: int) -> int:
        query = select(func.count(Attachment.id)).where(Attachment.task_id == task_id)
        result = await self._session.execute(query)
        return result.scalar() or 0
