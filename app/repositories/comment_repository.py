from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.repositories.base import BaseRepository
from app.repositories.interfaces.comment_repository import ICommentRepository


class CommentRepository(BaseRepository[Comment], ICommentRepository):
    """SQLAlchemy implementation of the comment repository."""

    def __init__(self, session: Session) -> None:
        super().__init__(Comment, session)

    async def get_by_task(self, task_id: int) -> list[Comment]:
        query = select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at.asc())
        result = await self._session.execute(query)
        return list(result.scalars().all())
