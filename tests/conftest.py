u"""Pytest configuration and fixtures."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock
import os

# Set test environment
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.repositories.interfaces import IUserRepository, IOrganizationRepository
from app.services.interfaces import IHashService, IJwtService
from app.services.user_service import UserService
from app.services.auth_service import AuthService


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_user_repository() -> Mock:
    """Mock user repository."""
    return Mock(spec=IUserRepository)


@pytest.fixture
def mock_organization_repository() -> Mock:
    """Mock organization repository."""
    return Mock(spec=IOrganizationRepository)


@pytest.fixture
def mock_hash_service() -> Mock:
    """Mock hash service."""
    mock = Mock(spec=IHashService)
    mock.hash.return_value = "hashed_password"
    mock.verify.return_value = True
    return mock


@pytest.fixture
def mock_jwt_service() -> Mock:
    """Mock JWT service."""
    mock = Mock(spec=IJwtService)
    mock.create_access_token.return_value = "test_jwt_token"
    mock.verify_token.return_value = {"sub": "1", "email": "test@example.com"}
    return mock


@pytest.fixture
def user_service(mock_user_repository, mock_hash_service) -> UserService:
    """Create UserService instance with mocked dependencies."""
    return UserService(
        user_repository=mock_user_repository,
        hash_service=mock_hash_service
    )


@pytest.fixture
def auth_service(
    mock_user_repository,
    mock_hash_service,
    mock_jwt_service
) -> AuthService:
    """Create AuthService instance with mocked dependencies."""
    return AuthService(
        user_repository=mock_user_repository,
        hash_service=mock_hash_service,
        jwt_service=mock_jwt_service
    )


@pytest.fixture
def sample_organization() -> Organization:
    """Create a sample organization for testing."""
    return Organization(
        id=1,
        name="Test Organization",
        description="A test organization",
        is_active=True
    )


@pytest.fixture
def sample_user(sample_organization) -> User:
    """Create a sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        organization_id=sample_organization.id,
        role=UserRole.MEMBER,
        is_active=True
    )


@pytest.fixture
def admin_user(sample_organization) -> User:
    """Create a sample admin user for testing."""
    return User(
        id=2,
        email="admin@example.com",
        password_hash="hashed_admin_password",
        full_name="Admin User",
        organization_id=sample_organization.id,
        role=UserRole.ADMIN,
        is_active=True
    )


@pytest.fixture
def manager_user(sample_organization) -> User:
    """Create a sample manager user for testing."""
    return User(
        id=3,
        email="manager@example.com",
        password_hash="hashed_manager_password",
        full_name="Manager User",
        organization_id=sample_organization.id,
        role=UserRole.MANAGER,
        is_active=True
    )


@pytest.fixture
def valid_user_data() -> dict:
    """Valid user data for testing."""
    return {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User",
        "organization_id": 1
    }


@pytest.fixture
def invalid_user_data() -> dict:
    """Invalid user data for testing."""
    return {
        "email": "invalid-email",
        "password": "123",  # Too short
        "full_name": "",  # Empty
        "organization_id": -1  # Invalid
    }


@pytest.fixture
def auth_headers() -> dict:
    """Authentication headers for testing."""
    return {
        "Authorization": "Bearer test_jwt_token",
        "Content-Type": "application/json"
    }


# Async fixtures for database testing
@pytest_asyncio.fixture
async def mock_async_user_repository() -> AsyncMock:
    """Mock async user repository."""
    mock = AsyncMock(spec=IUserRepository)
    return mock


@pytest_asyncio.fixture
async def mock_async_organization_repository() -> AsyncMock:
    """Mock async organization repository."""
    mock = AsyncMock(spec=IOrganizationRepository)
    return mock


# Test data generators
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def create_user(
        id: int = 1,
        email: str = "test@example.com",
        full_name: str = "Test User",
        role: UserRole = UserRole.MEMBER,
        organization_id: int = 1,
        is_active: bool = True
    ) -> User:
        return User(
            id=id,
            email=email,
            password_hash="hashed_password",
            full_name=full_name,
            role=role,
            organization_id=organization_id,
            is_active=is_active
        )
    return create_user


@pytest.fixture
def organization_factory():
    """Factory for creating test organizations."""
    def create_organization(
        id: int = 1,
        name: str = "Test Organization",
        description: str = "Test Description",
        is_active: bool = True
    ) -> Organization:
        return Organization(
            id=id,
            name=name,
            description=description,
            is_active=is_active
        )
    return create_organization


# Test markers and configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as an authentication test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "db: mark test as requiring database"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ["integration", "api", "slow", "db"]
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)

        # Add async marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here
    pass
