from datetime import datetime
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.user import User, UserRole
from app.repositories.interfaces import (
    ITaskRepository,
    IProjectRepository,
    ICommentRepository,
    IAttachmentRepository,
)
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service for managing tasks and enforcing business rules."""

    def __init__(
        self,
        task_repository: ITaskRepository,
        project_repository: IProjectRepository,
        comment_repository: ICommentRepository,
        attachment_repository: IAttachmentRepository,
    ) -> None:
        self._task_repo = task_repository
        self._project_repo = project_repository
        self._comment_repo = comment_repository
        self._attachment_repo = attachment_repository

    async def _is_project_member(self, project_id: int, user_id: int) -> bool:
        """Check if a user is a member of a project."""
        members = await self._project_repo.get_members(project_id)
        return any(m.id == user_id for m in members)

    async def create_task(
        self,
        project_id: int,
        user: User,
        data: TaskCreate,
    ) -> Task:
        """Create a new task in a project."""
        # BR1: Project Membership
        if not await self._is_project_member(project_id, user.id):
            raise ForbiddenException("Only project members can create tasks in this project")

        # BR3: Due Date Validation
        if data.due_date and data.due_date.date() < datetime.now().date():
            raise BadRequestException("Due date must be today or in the future")

        # BR2: Task Assignment
        assignee_id = data.assignee_id or user.id
        if assignee_id != user.id and user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise ForbiddenException("Only Admin or Manager can gán task cho người khác")

        task = Task(
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
            project_id=project_id,
            assignee_id=assignee_id,
            created_by_id=user.id,
            status=TaskStatus.TODO,
        )
        return await self._task_repo.create(task)

    async def list_tasks(
        self,
        project_id: int,
        user: User,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        """List tasks in a project with filters and pagination."""
        # BR1: Project Membership
        if not await self._is_project_member(project_id, user.id):
            raise ForbiddenException("You don't have access to this project's tasks")

        tasks = await self._task_repo.get_by_project(
            project_id=project_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            skip=skip,
            limit=limit,
        )
        total = await self._task_repo.count_by_project(
            project_id=project_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )
        return tasks, total

    async def get_task_by_id(self, task_id: int, user: User) -> Task:
        """Get task details by ID."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("You don't have access to this task")

        return task

    async def update_task(self, task_id: int, user: User, data: TaskUpdate) -> Task:
        """Update task details."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("Only project members can update tasks")

        # BR3: Due Date Validation
        if data.due_date and data.due_date.date() < datetime.now().date():
            raise BadRequestException("Due date must be today or in the future")

        # Update fields if provided
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.due_date is not None:
            task.due_date = data.due_date
        
        if data.assignee_id is not None:
            # BR2: Task Assignment
            if data.assignee_id != user.id and user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenException("Only Admin or Manager can gán task cho người khác")
            task.assignee_id = data.assignee_id

        return await self._task_repo.update(task)

    async def update_status(self, task_id: int, user: User, new_status: TaskStatus) -> Task:
        """Update task status with flow validation."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("Only project members can update task status")

        # BR4: Status Flow (Forward only: todo -> in-progress -> done)
        status_order = {
            TaskStatus.TODO: 0,
            TaskStatus.IN_PROGRESS: 1,
            TaskStatus.DONE: 2,
        }
        
        if status_order[new_status] < status_order[task.status]:
            raise BadRequestException(
                f"Cannot move status backwards from {task.status.value} to {new_status.value}"
            )

        task.status = new_status
        return await self._task_repo.update(task)

    async def delete_task(self, task_id: int, user: User) -> None:
        """Delete a task."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # UC3.5: Delete Task - Admin/Manager only
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise ForbiddenException("Only Admin or Manager can delete tasks")

        # Must be in the same organization (implied by Admin/Manager role and project context)
        # But let's check membership anyway
        if not await self._is_project_member(task.project_id, user.id):
             raise ForbiddenException("You don't have access to this project")

        await self._task_repo.delete(task_id)

    async def get_task_counts(self, project_id: int, user: User) -> dict[str, int]:
        """Get task counts by status for a project."""
        if not await self._is_project_member(project_id, user.id):
            raise ForbiddenException("You don't have access to this project")
        
        return await self._task_repo.count_by_status(project_id)

    async def get_overdue_tasks(self, project_id: int, user: User) -> list[Task]:
        """Get list of overdue tasks in a project."""
        if not await self._is_project_member(project_id, user.id):
            raise ForbiddenException("You don't have access to this project")
            
        return await self._task_repo.get_overdue_tasks(project_id)

    # Comment operations

    async def add_comment(self, task_id: int, user: User, content: str) -> Comment:
        """Add a comment to a task."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("Only project members can comment on tasks")

        comment = Comment(
            content=content,
            task_id=task_id,
            user_id=user.id,
        )
        return await self._comment_repo.create(comment)

    async def list_comments(self, task_id: int, user: User) -> list[Comment]:
        """List all comments on a task."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("You don't have access to this task's comments")

        return await self._comment_repo.get_by_task(task_id)

    async def delete_comment(self, comment_id: int, user: User) -> None:
        """Delete a comment."""
        comment = await self._comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException("Comment not found")

        # UC4.1: Delete Comment - Owner or Admin only
        if comment.user_id != user.id and user.role != UserRole.ADMIN:
            raise ForbiddenException("You can only delete your own comments")

        await self._comment_repo.delete(comment_id)

    # Attachment operations

    async def add_attachment(
        self,
        task_id: int,
        user: User,
        file_path: str,
        file_name: str,
        file_type: str | None,
        file_size: int | None,
    ) -> Attachment:
        """Add an attachment to a task."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("Only project members can upload attachments")

        # BR5: Attachment Limits (max 3 per task)
        count = await self._attachment_repo.count_by_task(task_id)
        if count >= 3:
            raise BadRequestException("Maximum 3 attachments per task allowed")

        attachment = Attachment(
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            task_id=task_id,
            user_id=user.id,
        )
        return await self._attachment_repo.create(attachment)

    async def list_attachments(self, task_id: int, user: User) -> list[Attachment]:
        """List all attachments for a task."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # BR1: Project Membership
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("You don't have access to this task's attachments")

        return await self._attachment_repo.get_by_task(task_id)

    async def get_attachment_by_id(self, attachment_id: int, user: User) -> Attachment:
        """Get attachment by ID."""
        attachment = await self._attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise NotFoundException("Attachment not found")

        # Must be project member to access
        task = await self._task_repo.get_by_id(attachment.task_id)
        if not await self._is_project_member(task.project_id, user.id):
            raise ForbiddenException("You don't have access to this attachment")

        return attachment

    async def delete_attachment(self, attachment_id: int, user: User) -> None:
        """Delete an attachment."""
        attachment = await self._attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise NotFoundException("Attachment not found")

        # UC4.2: Delete Attachment - Uploader or Admin only
        if attachment.user_id != user.id and user.role != UserRole.ADMIN:
            raise ForbiddenException("You can only delete your own attachments")

        await self._attachment_repo.delete(attachment_id)
