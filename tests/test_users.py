"""Unit tests for user service."""

import pytest
from unittest.mock import Mock, AsyncMock

from app.models.user import User, UserRole
from app.services.user_service import UserService
from app.repositories.interfaces import IUserRepository
from app.services.interfaces import IHashService


class TestUserService:
    """Test cases for UserService class."""

    @pytest.fixture
    def mock_user_repository(self):
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def mock_hash_service(self):
        return Mock(spec=IHashService)

    @pytest.fixture
    def user_service(self, mock_user_repository, mock_hash_service):
        return UserService(
            user_repository=mock_user_repository,
            hash_service=mock_hash_service
        )

    @pytest.fixture
    def sample_user(self):
        return User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            organization_id=1,
            role=UserRole.MEMBER,
            is_active=True
        )

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self,
        user_service,
        mock_user_repository,
        sample_user
    ):
        # Arrange
        email = "test@example.com"
        mock_user_repository.get_by_email = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.get_user_by_email(email)

        # Assert
        assert result == sample_user
        mock_user_repository.get_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test user retrieval by email when user not found."""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repository.get_by_email = AsyncMock(return_value=None)

        # Act
        result = await user_service.get_user_by_email(email)

        # Assert
        assert result is None
        mock_user_repository.get_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self,
        user_service,
        mock_user_repository,
        sample_user
    ):
        """Test successful user retrieval by ID."""
        # Arrange
        user_id = 1
        mock_user_repository.get_by_id = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.get_user_by_id(user_id)

        # Assert
        assert result == sample_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test user retrieval by ID when user not found."""
        # Arrange
        user_id = 999
        mock_user_repository.get_by_id = AsyncMock(return_value=None)

        # Act
        result = await user_service.get_user_by_id(user_id)

        # Assert
        assert result is None
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service,
        mock_user_repository,
        mock_hash_service,
        sample_user
    ):
        """Test successful user creation."""
        # Arrange
        email = "test@example.com"
        password = "password123"
        full_name = "Test User"
        organization_id = 1
        role = UserRole.MEMBER
        hashed_password = "hashed_password123"

        mock_hash_service.hash.return_value = hashed_password
        mock_user_repository.create = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.create_user(
            email=email,
            password=password,
            full_name=full_name,
            organization_id=organization_id,
            role=role
        )

        # Assert
        assert result == sample_user
        mock_hash_service.hash.assert_called_once_with(password)
        mock_user_repository.create.assert_called_once()

        # Verify the user object passed to create has correct attributes
        created_user_call = mock_user_repository.create.call_args[0][0]
        assert created_user_call.email == email
        assert created_user_call.password_hash == hashed_password
        assert created_user_call.full_name == full_name
        assert created_user_call.organization_id == organization_id
        assert created_user_call.role == role
        assert created_user_call.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_with_default_role(
        self,
        user_service,
        mock_user_repository,
        mock_hash_service,
        sample_user
    ):
        """Test user creation with default role."""
        # Arrange
        email = "test@example.com"
        password = "password123"
        full_name = "Test User"
        organization_id = 1
        hashed_password = "hashed_password123"

        mock_hash_service.hash.return_value = hashed_password
        mock_user_repository.create = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.create_user(
            email=email,
            password=password,
            full_name=full_name,
            organization_id=organization_id
        )

        # Assert
        assert result == sample_user
        mock_hash_service.hash.assert_called_once_with(password)
        mock_user_repository.create.assert_called_once()

        # Verify the user object has default role
        created_user_call = mock_user_repository.create.call_args[0][0]
        assert created_user_call.role == UserRole.MEMBER

    @pytest.mark.asyncio
    async def test_create_user_with_admin_role(
        self,
        user_service,
        mock_user_repository,
        mock_hash_service,
        sample_user
    ):
        """Test user creation with admin role."""
        # Arrange
        email = "admin@example.com"
        password = "password123"
        full_name = "Admin User"
        organization_id = 1
        role = UserRole.ADMIN
        hashed_password = "hashed_password123"

        mock_hash_service.hash.return_value = hashed_password
        mock_user_repository.create = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.create_user(
            email=email,
            password=password,
            full_name=full_name,
            organization_id=organization_id,
            role=role
        )

        # Assert
        assert result == sample_user
        created_user_call = mock_user_repository.create.call_args[0][0]
        assert created_user_call.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_update_user_with_full_name(
        self,
        user_service,
        mock_user_repository,
        sample_user
    ):
        """Test updating user with new full name."""
        # Arrange
        new_full_name = "Updated Name"
        original_name = sample_user.full_name

        # Create a new User object for the return value
        updated_user = User(
            id=sample_user.id,
            email=sample_user.email,
            password_hash=sample_user.password_hash,
            full_name=new_full_name,
            organization_id=sample_user.organization_id,
            role=sample_user.role,
            is_active=sample_user.is_active
        )

        mock_user_repository.update = AsyncMock(return_value=updated_user)

        # Act
        result = await user_service.update_user(
            user=sample_user,
            full_name=new_full_name
        )

        # Assert
        assert result.full_name == new_full_name
        assert sample_user.full_name == new_full_name  # Original user should be modified
        mock_user_repository.update.assert_called_once_with(sample_user)

    @pytest.mark.asyncio
    async def test_update_user_without_changes(
        self,
        user_service,
        mock_user_repository,
        sample_user
    ):
        """Test updating user without any changes."""
        # Arrange
        original_name = sample_user.full_name
        mock_user_repository.update = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.update_user(user=sample_user)

        # Assert
        assert result == sample_user
        assert sample_user.full_name == original_name  # Name should remain unchanged
        mock_user_repository.update.assert_called_once_with(sample_user)

    @pytest.mark.asyncio
    async def test_update_user_with_none_full_name(
        self,
        user_service,
        mock_user_repository,
        sample_user
    ):
        """Test updating user with None full name (should not change)."""
        # Arrange
        original_name = sample_user.full_name
        mock_user_repository.update = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.update_user(
            user=sample_user,
            full_name=None
        )

        # Assert
        assert result == sample_user
        assert sample_user.full_name == original_name  # Name should remain unchanged
        mock_user_repository.update.assert_called_once_with(sample_user)

    @pytest.mark.asyncio
    async def test_email_exists_true(
        self,
        user_service,
        mock_user_repository
    ):
        """Test email exists check when email exists."""
        # Arrange
        email = "existing@example.com"
        mock_user_repository.email_exists = AsyncMock(return_value=True)

        # Act
        result = await user_service.email_exists(email)

        # Assert
        assert result is True
        mock_user_repository.email_exists.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_email_exists_false(
        self,
        user_service,
        mock_user_repository
    ):
        """Test email exists check when email doesn't exist."""
        # Arrange
        email = "new@example.com"
        mock_user_repository.email_exists = AsyncMock(return_value=False)

        # Act
        result = await user_service.email_exists(email)

        # Assert
        assert result is False
        mock_user_repository.email_exists.assert_called_once_with(email)

    def test_verify_password_success(
        self,
        user_service,
        mock_hash_service
    ):
        """Test successful password verification."""
        # Arrange
        password = "password123"
        hashed_password = "hashed_password123"
        mock_hash_service.verify.return_value = True

        # Act
        result = user_service.verify_password(password, hashed_password)

        # Assert
        assert result is True
        mock_hash_service.verify.assert_called_once_with(password, hashed_password)

    def test_verify_password_failure(
        self,
        user_service,
        mock_hash_service
    ):
        """Test password verification failure."""
        # Arrange
        password = "wrong_password"
        hashed_password = "hashed_password123"
        mock_hash_service.verify.return_value = False

        # Act
        result = user_service.verify_password(password, hashed_password)

        # Assert
        assert result is False
        mock_hash_service.verify.assert_called_once_with(password, hashed_password)

    def test_verify_password_with_empty_strings(
        self,
        user_service,
        mock_hash_service
    ):
        """Test password verification with empty strings."""
        # Arrange
        password = ""
        hashed_password = ""
        mock_hash_service.verify.return_value = False

        # Act
        result = user_service.verify_password(password, hashed_password)

        # Assert
        assert result is False
        mock_hash_service.verify.assert_called_once_with(password, hashed_password)


class TestUserServiceIntegration:
    """Integration-style tests for UserService with more realistic scenarios."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository for integration tests."""
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def mock_hash_service(self):
        """Mock hash service for integration tests."""
        return Mock(spec=IHashService)

    @pytest.fixture
    def user_service(self, mock_user_repository, mock_hash_service):
        """Create UserService instance."""
        return UserService(
            user_repository=mock_user_repository,
            hash_service=mock_hash_service
        )

    @pytest.mark.asyncio
    async def test_create_user_and_verify_password_flow(
        self,
        user_service,
        mock_user_repository,
        mock_hash_service
    ):
        """Test the complete flow of creating a user and verifying password."""
        # Arrange
        email = "test@example.com"
        password = "password123"
        full_name = "Test User"
        organization_id = 1
        hashed_password = "hashed_password123"

        # Mock hash service
        mock_hash_service.hash.return_value = hashed_password
        mock_hash_service.verify.return_value = True

        # Mock repository
        created_user = User(
            id=1,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            organization_id=organization_id,
            role=UserRole.MEMBER,
            is_active=True
        )
        mock_user_repository.create = AsyncMock(return_value=created_user)

        # Act - Create user
        user = await user_service.create_user(
            email=email,
            password=password,
            full_name=full_name,
            organization_id=organization_id
        )

        # Act - Verify password
        is_valid = user_service.verify_password(password, user.password_hash)

        # Assert
        assert user.email == email
        assert user.password_hash == hashed_password
        assert is_valid is True
        mock_hash_service.hash.assert_called_once_with(password)
        mock_hash_service.verify.assert_called_once_with(password, hashed_password)

    @pytest.mark.asyncio
    async def test_user_registration_workflow(
        self,
        user_service,
        mock_user_repository,
        mock_hash_service
    ):
        """Test complete user registration workflow."""
        # Arrange
        email = "newuser@example.com"
        password = "securepassword"
        full_name = "New User"
        organization_id = 1

        # Mock email doesn't exist initially
        mock_user_repository.email_exists = AsyncMock(return_value=False)

        # Mock user creation
        hashed_password = "hashed_securepassword"
        mock_hash_service.hash.return_value = hashed_password

        created_user = User(
            id=2,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            organization_id=organization_id,
            role=UserRole.MEMBER,
            is_active=True
        )
        mock_user_repository.create = AsyncMock(return_value=created_user)

        # Act
        # Step 1: Check if email exists
        email_exists = await user_service.email_exists(email)
        assert email_exists is False

        # Step 2: Create user
        user = await user_service.create_user(
            email=email,
            password=password,
            full_name=full_name,
            organization_id=organization_id
        )

        # Assert
        assert user.email == email
        assert user.full_name == full_name
        assert user.organization_id == organization_id
        assert user.role == UserRole.MEMBER
        assert user.is_active is True
        mock_user_repository.email_exists.assert_called_once_with(email)
        mock_user_repository.create.assert_called_once()
