"""Unit tests for AuthService."""

import pytest
import jwt
from unittest.mock import Mock, AsyncMock

from app.core import ConflictException
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.repositories.interfaces import IUserRepository, IOrganizationRepository
from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.auth_service import AuthService
from app.services.interfaces import IHashService, IJwtService


class TestAuthService:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def mock_organization_repository(self):
        return Mock(spec=IOrganizationRepository)

    @pytest.fixture
    def mock_hash_service(self):
        return Mock(spec=IHashService)

    @pytest.fixture
    def mock_jwt_service(self):
        return Mock(spec=IJwtService)

    @pytest.fixture
    def auth_service(
        self,
        mock_user_repository,
        mock_organization_repository,
        mock_hash_service,
        mock_jwt_service,
    ):
        return AuthService(
            user_repository=mock_user_repository,
            organization_repository=mock_organization_repository,
            hash_service=mock_hash_service,
            jwt_service=mock_jwt_service,
        )

    @pytest.mark.asyncio
    async def test_register_success(
        self,
        auth_service,
        mock_user_repository,
        mock_organization_repository,
        mock_hash_service,
    ):
        # Arrange
        data = RegisterRequest(
            email="new@example.com",
            password="password123",
            full_name="New User",
            organization_name="New Org"
        )
        mock_user_repository.email_exists = AsyncMock(return_value=False)
        
        org = Organization(id=1, name="New Org")
        mock_organization_repository.create = AsyncMock(return_value=org)
        
        user = User(
            id=1,
            email=data.email,
            full_name=data.full_name,
            organization_id=1,
            role=UserRole.ADMIN,
            is_active=True
        )
        mock_user_repository.create = AsyncMock(return_value=user)
        mock_user_repository.get_by_id = AsyncMock(return_value=user)
        mock_hash_service.hash.return_value = "hashed_password"

        # Act
        result = await auth_service.register(data)

        # Assert
        assert result == user
        mock_user_repository.email_exists.assert_called_once_with(data.email)
        mock_organization_repository.create.assert_called_once()
        mock_user_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_conflict(self, auth_service, mock_user_repository):
        # Arrange
        data = RegisterRequest(
            email="existing@example.com",
            password="password123",
            full_name="User",
            organization_name="Org"
        )
        mock_user_repository.email_exists = AsyncMock(return_value=True)

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await auth_service.register(data)
        assert exc_info.value.message == "Email already registered"

    @pytest.mark.asyncio
    async def test_register_missing_org_name(self, auth_service, mock_user_repository):
        # Arrange
        data = RegisterRequest(
            email="new@example.com",
            password="password123",
            full_name="New User",
            organization_name=None
        )
        mock_user_repository.email_exists = AsyncMock(return_value=False)

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            await auth_service.register(data)
        assert "Organization name is required" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        auth_service,
        mock_user_repository,
        mock_hash_service,
        mock_jwt_service,
    ):
        # Arrange
        email = "test@example.com"
        password = "password123"
        user = User(
            id=1,
            email=email,
            password_hash="hashed_password",
            is_active=True
        )
        mock_user_repository.get_by_email = AsyncMock(return_value=user)
        mock_hash_service.verify.return_value = True
        mock_jwt_service.create_access_token.return_value = "access_token"
        mock_jwt_service.create_refresh_token.return_value = "refresh_token"

        # Act
        result = await auth_service.login(email, password)

        # Assert
        assert isinstance(result, TokenResponse)
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        assert result.user_id == user.id

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service, mock_user_repository):
        # Arrange
        mock_user_repository.get_by_email = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login("none@example.com", "pass")
        assert exc_info.value.message == "Invalid email or password"

    @pytest.mark.asyncio
    async def test_login_incorrect_password(
        self,
        auth_service,
        mock_user_repository,
        mock_hash_service,
    ):
        # Arrange
        user = User(id=1, email="test@example.com", password_hash="hash", is_active=True)
        mock_user_repository.get_by_email = AsyncMock(return_value=user)
        mock_hash_service.verify.return_value = False

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login("test@example.com", "wrong")
        assert exc_info.value.message == "Invalid email or password"

    @pytest.mark.asyncio
    async def test_login_user_inactive(
        self,
        auth_service,
        mock_user_repository,
        mock_hash_service,
    ):
        # Arrange
        user = User(id=1, email="test@example.com", password_hash="hash", is_active=False)
        mock_user_repository.get_by_email = AsyncMock(return_value=user)
        mock_hash_service.verify.return_value = True

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login("test@example.com", "pass")
        assert exc_info.value.message == "User account is deactivated"

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        auth_service,
        mock_user_repository,
        mock_jwt_service,
    ):
        # Arrange
        refresh_token = "valid_refresh_token"
        payload = {"userId": "1", "type": "refresh"}
        mock_jwt_service.decode_token.return_value = payload
        
        user = User(id=1, email="test@example.com", is_active=True)
        mock_user_repository.get_by_id = AsyncMock(return_value=user)
        
        mock_jwt_service.create_access_token.return_value = "new_access_token"
        mock_jwt_service.create_refresh_token.return_value = "new_refresh_token"

        # Act
        result = await auth_service.refresh_token(refresh_token)

        # Assert
        assert result.access_token == "new_access_token"
        assert result.refresh_token == "new_refresh_token"
        mock_jwt_service.decode_token.assert_called_once_with(refresh_token)
        mock_user_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_refresh_token_expired(self, auth_service, mock_jwt_service):
        # Arrange
        mock_jwt_service.decode_token.side_effect = jwt.ExpiredSignatureError()

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.refresh_token("expired_token")
        assert exc_info.value.message == "Refresh token has expired"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_service, mock_jwt_service):
        # Arrange
        mock_jwt_service.decode_token.side_effect = jwt.InvalidTokenError()

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.refresh_token("invalid_token")
        assert exc_info.value.message == "Invalid refresh token"

    @pytest.mark.asyncio
    async def test_refresh_token_wrong_type(self, auth_service, mock_jwt_service):
        # Arrange
        mock_jwt_service.decode_token.return_value = {"userId": "1", "type": "access"}

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.refresh_token("access_token_passed_as_refresh")
        assert exc_info.value.message == "Invalid refresh token"

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(
        self,
        auth_service,
        mock_user_repository,
        mock_jwt_service,
    ):
        # Arrange
        mock_jwt_service.decode_token.return_value = {"userId": "1", "type": "refresh"}
        mock_user_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.refresh_token("token")
        assert exc_info.value.message == "User not found or deactivated"
