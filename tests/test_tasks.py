import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User, UserRole
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.repositories.interfaces import (
    ITaskRepository,
    IProjectRepository,
    ICommentRepository,
    IAttachmentRepository,
)
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate


class TestTaskService:

    @pytest.fixture
    def mock_task_repo(self):
        return Mock(spec=ITaskRepository)

    @pytest.fixture
    def mock_project_repo(self):
        return Mock(spec=IProjectRepository)

    @pytest.fixture
    def mock_comment_repo(self):
        return Mock(spec=ICommentRepository)

    @pytest.fixture
    def mock_attachment_repo(self):
        return Mock(spec=IAttachmentRepository)

    @pytest.fixture
    def task_service(
        self, mock_task_repo, mock_project_repo, mock_comment_repo, mock_attachment_repo
    ):
        return TaskService(
            task_repository=mock_task_repo,
            project_repository=mock_project_repo,
            comment_repository=mock_comment_repo,
            attachment_repository=mock_attachment_repo,
        )

    @pytest.fixture
    def member_user(self):
        return User(
            id=1,
            email="member@example.com",
            role=UserRole.MEMBER,
            organization_id=1,
            is_active=True,
        )

    @pytest.fixture
    def admin_user(self):
        return User(
            id=2,
            email="admin@example.com",
            role=UserRole.ADMIN,
            organization_id=1,
            is_active=True,
        )

    @pytest.fixture
    def sample_task(self):
        return Task(
            id=1,
            title="Sample Task",
            project_id=1,
            assignee_id=1,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
        )

    # 1. Create Task Tests

    @pytest.mark.asyncio
    async def test_create_task_success(self, task_service, mock_project_repo, mock_task_repo, member_user):
        # Arrange
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])
        data = TaskCreate(title="New Task", due_date=datetime.now() + timedelta(days=1))
        mock_task_repo.create = AsyncMock(return_value=Task(id=1, title="New Task"))

        # Act
        result = await task_service.create_task(1, member_user, data)

        # Assert
        assert result.title == "New Task"
        mock_task_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_not_member_forbidden(self, task_service, mock_project_repo, member_user):
        # Arrange
        mock_project_repo.get_members = AsyncMock(return_value=[])
        data = TaskCreate(title="New Task")

        # Act & Assert
        with pytest.raises(ForbiddenException) as exc:
            await task_service.create_task(1, member_user, data)
        assert "Only project members" in str(exc.value)

    @pytest.mark.asyncio
    async def test_create_task_past_due_date_bad_request(self, task_service, mock_project_repo, member_user):
        # Arrange
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])
        data = TaskCreate(title="New Task", due_date=datetime.now() - timedelta(days=1))

        # Act & Assert
        with pytest.raises(BadRequestException) as exc:
            await task_service.create_task(1, member_user, data)
        assert "Due date must be today or in the future" in str(exc.value)

    @pytest.mark.asyncio
    async def test_create_task_assign_to_other_forbidden_for_member(self, task_service, mock_project_repo, member_user):
        # Arrange
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])
        data = TaskCreate(title="New Task", assignee_id=99)

        # Act & Assert
        with pytest.raises(ForbiddenException) as exc:
            await task_service.create_task(1, member_user, data)
        assert "Only Admin or Manager can gán task" in str(exc.value)

    # 2. Update Status Tests

    @pytest.mark.asyncio
    async def test_update_status_forward_success(self, task_service, mock_task_repo, mock_project_repo, member_user, sample_task):
        # Arrange
        mock_task_repo.get_by_id = AsyncMock(return_value=sample_task)
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])
        mock_task_repo.update = AsyncMock(return_value=sample_task)

        # Act
        result = await task_service.update_status(1, member_user, TaskStatus.IN_PROGRESS)

        # Assert
        assert result.status == TaskStatus.IN_PROGRESS
        mock_task_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_backward_forbidden(self, task_service, mock_task_repo, mock_project_repo, member_user):
        # Arrange
        task = Task(id=1, project_id=1, status=TaskStatus.DONE)
        mock_task_repo.get_by_id = AsyncMock(return_value=task)
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])

        # Act & Assert
        with pytest.raises(BadRequestException) as exc:
            await task_service.update_status(1, member_user, TaskStatus.IN_PROGRESS)
        assert "Cannot move status backwards" in str(exc.value)

    # 3. Comment Tests

    @pytest.mark.asyncio
    async def test_add_comment_success(self, task_service, mock_task_repo, mock_project_repo, mock_comment_repo, member_user, sample_task):
        # Arrange
        mock_task_repo.get_by_id = AsyncMock(return_value=sample_task)
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])
        mock_comment_repo.create = AsyncMock(return_value=Comment(id=1, content="Nice"))

        # Act
        result = await task_service.add_comment(1, member_user, "Nice")

        # Assert
        assert result.content == "Nice"
        mock_comment_repo.create.assert_called_once()

    # 4. Attachment Tests

    @pytest.mark.asyncio
    async def test_add_attachment_limit_exceeded(self, task_service, mock_task_repo, mock_project_repo, mock_attachment_repo, member_user, sample_task):
        # Arrange
        mock_task_repo.get_by_id = AsyncMock(return_value=sample_task)
        mock_project_repo.get_members = AsyncMock(return_value=[member_user])
        mock_attachment_repo.count_by_task = AsyncMock(return_value=3)

        # Act & Assert
        with pytest.raises(BadRequestException) as exc:
            await task_service.add_attachment(1, member_user, "path", "file.txt", "text/plain", 100)
        assert "Maximum 3 attachments" in str(exc.value)

    # 5. Delete Task Tests

    @pytest.mark.asyncio
    async def test_delete_task_member_forbidden(self, task_service, mock_task_repo, member_user, sample_task):
        # Arrange
        mock_task_repo.get_by_id = AsyncMock(return_value=sample_task)

        # Act & Assert
        with pytest.raises(ForbiddenException) as exc:
            await task_service.delete_task(1, member_user)
        assert "Only Admin or Manager" in str(exc.value)

    @pytest.mark.asyncio
    async def test_delete_task_admin_success(self, task_service, mock_task_repo, mock_project_repo, admin_user, sample_task):
        # Arrange
        mock_task_repo.get_by_id = AsyncMock(return_value=sample_task)
        mock_project_repo.get_members = AsyncMock(return_value=[admin_user])
        mock_task_repo.delete = AsyncMock()

        # Act
        await task_service.delete_task(1, admin_user)

        # Assert
        mock_task_repo.delete.assert_called_once_with(1)
