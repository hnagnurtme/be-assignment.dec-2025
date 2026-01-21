import pytest
from unittest.mock import AsyncMock, Mock

from fastapi import HTTPException

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User, UserRole
from app.repositories.interfaces.project_repository import IProjectRepository
from app.repositories.interfaces.user_repository import IUserRepository
from app.services.project_service import ProjectService


class TestProjectService:

    @pytest.fixture
    def mock_project_repository(self):
        return Mock(spec=IProjectRepository)

    @pytest.fixture
    def mock_user_repository(self):
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def project_service(self, mock_project_repository, mock_user_repository):
        return ProjectService(
            project_repo=mock_project_repository,
            user_repo=mock_user_repository,
        )

    @pytest.fixture
    def admin_user(self):
        return User(
            id=1,
            email="admin@example.com",
            password_hash="hashed",
            full_name="Admin User",
            organization_id=1,
            role=UserRole.ADMIN,
            is_active=True,
        )

    @pytest.fixture
    def manager_user(self):
        return User(
            id=2,
            email="manager@example.com",
            password_hash="hashed",
            full_name="Manager User",
            organization_id=1,
            role=UserRole.MANAGER,
            is_active=True,
        )

    @pytest.fixture
    def member_user(self):
        return User(
            id=3,
            email="member@example.com",
            password_hash="hashed",
            full_name="Member User",
            organization_id=1,
            role=UserRole.MEMBER,
            is_active=True,
        )

    @pytest.fixture
    def sample_project(self):
        return Project(
            id=1,
            name="Test Project",
            description="Test Description",
            organization_id=1,
            created_by_id=1,
        )

    @pytest.mark.asyncio
    async def test_create_project_success(
        self, project_service, mock_project_repository, sample_project
    ):
        """Test successful project creation."""
        # Arrange
        mock_project_repository.create = AsyncMock(return_value=sample_project)

        # Act
        result = await project_service.create_project(
            name="Test Project",
            description="Test Description",
            organization_id=1,
            created_by_id=1,
        )

        # Assert
        assert result == sample_project
        mock_project_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_project_by_id_admin_success(
        self, project_service, mock_project_repository, sample_project, admin_user
    ):
        """Test admin can get any project in their organization."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)

        # Act
        result = await project_service.get_project_by_id(1, admin_user)

        # Assert
        assert result == sample_project
        mock_project_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_project_by_id_member_not_member(
        self, project_service, mock_project_repository, sample_project, member_user
    ):
        """Test member cannot access project they're not part of."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_project_repository.is_member = AsyncMock(return_value=False)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_service.get_project_by_id(1, member_user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self, project_service, mock_project_repository, admin_user
    ):
        """Test getting non-existent project."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_service.get_project_by_id(999, admin_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_projects_admin(
        self, project_service, mock_project_repository, admin_user, sample_project
    ):
        """Test admin can list all projects in organization."""
        # Arrange
        projects = [sample_project]
        mock_project_repository.get_by_organization = AsyncMock(return_value=projects)

        # Act
        result = await project_service.list_projects(1, admin_user, 0, 10)

        # Assert
        assert result == projects
        mock_project_repository.get_by_organization.assert_called_once_with(1, 0, 10)

    @pytest.mark.asyncio
    async def test_list_projects_member(
        self, project_service, mock_project_repository, member_user, sample_project
    ):
        """Test member can only list projects they're part of."""
        # Arrange
        projects = [sample_project]
        mock_project_repository.get_user_projects = AsyncMock(return_value=projects)

        # Act
        result = await project_service.list_projects(1, member_user, 0, 10)

        # Assert
        assert result == projects
        mock_project_repository.get_user_projects.assert_called_once_with(3, 0, 10)

    @pytest.mark.asyncio
    async def test_update_project_success(
        self, project_service, mock_project_repository, sample_project, admin_user
    ):
        """Test successful project update by admin."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_project_repository.update = AsyncMock(return_value=sample_project)

        # Act
        result = await project_service.update_project(
            1, admin_user, name="Updated Name", description="Updated Description"
        )

        # Assert
        assert result.name == "Updated Name"
        assert result.description == "Updated Description"
        mock_project_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_project_member_forbidden(
        self, project_service, mock_project_repository, sample_project, member_user
    ):
        """Test member cannot update project."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_service.update_project(1, member_user, name="New Name")

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_project_success(
        self, project_service, mock_project_repository, sample_project, admin_user
    ):
        """Test successful project deletion by admin."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_project_repository.delete = AsyncMock()

        # Act
        await project_service.delete_project(1, admin_user)

        # Assert
        mock_project_repository.delete.assert_called_once_with(sample_project)

    @pytest.mark.asyncio
    async def test_delete_project_manager_forbidden(
        self, project_service, mock_project_repository, sample_project, manager_user
    ):
        """Test manager cannot delete project."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_service.delete_project(1, manager_user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_add_member_success(
        self,
        project_service,
        mock_project_repository,
        mock_user_repository,
        sample_project,
        admin_user,
        member_user,
    ):
        """Test successfully adding member to project."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_user_repository.get_by_id = AsyncMock(return_value=member_user)
        mock_project_repository.is_member = AsyncMock(return_value=False)
        project_member = ProjectMember(project_id=1, user_id=3)
        mock_project_repository.add_member = AsyncMock(return_value=project_member)

        # Act
        result = await project_service.add_member(1, 3, admin_user)

        # Assert
        assert result.project_id == 1
        assert result.user_id == 3
        mock_project_repository.add_member.assert_called_once_with(1, 3)

    @pytest.mark.asyncio
    async def test_add_member_already_exists(
        self,
        project_service,
        mock_project_repository,
        mock_user_repository,
        sample_project,
        admin_user,
        member_user,
    ):
        """Test adding member that already exists."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_user_repository.get_by_id = AsyncMock(return_value=member_user)
        mock_project_repository.is_member = AsyncMock(return_value=True)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_service.add_member(1, 3, admin_user)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self,
        project_service,
        mock_project_repository,
        sample_project,
        admin_user,
    ):
        """Test successfully removing member from project."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_project_repository.is_member = AsyncMock(return_value=True)
        mock_project_repository.remove_member = AsyncMock()

        # Act
        await project_service.remove_member(1, 3, admin_user)

        # Assert
        mock_project_repository.remove_member.assert_called_once_with(1, 3)

    @pytest.mark.asyncio
    async def test_remove_member_not_found(
        self,
        project_service,
        mock_project_repository,
        sample_project,
        admin_user,
    ):
        """Test removing member that doesn't exist."""
        # Arrange
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_project_repository.is_member = AsyncMock(return_value=False)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_service.remove_member(1, 3, admin_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_members_success(
        self,
        project_service,
        mock_project_repository,
        sample_project,
        admin_user,
        member_user,
    ):
        """Test getting project members."""
        # Arrange
        members = [admin_user, member_user]
        mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
        mock_project_repository.get_members = AsyncMock(return_value=members)

        # Act
        result = await project_service.get_members(1, admin_user)

        # Assert
        assert result == members
        mock_project_repository.get_members.assert_called_once_with(1)
