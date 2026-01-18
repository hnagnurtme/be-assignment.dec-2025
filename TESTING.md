# Testing Guide

This document provides comprehensive information about testing in the TaskMind backend application.

## 🧪 Test Overview

The project uses **pytest** as the primary testing framework with comprehensive test coverage and multiple testing strategies.

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_users.py           # User service unit tests
├── test_auth.py            # Authentication tests
├── test_organizations.py   # Organization tests
├── test_projects.py        # Project management tests
├── test_tasks.py           # Task management tests
└── test_*.py               # Other test modules
```

## 🚀 Quick Start

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::TestUserService::test_create_user_success
```

### Using Makefile (Recommended)

```bash
# Install dependencies
make install

# Run all tests
make test

# Run tests with coverage
make test-cov

# Run user service tests
make test-users

# Run authentication tests
make test-auth

# Run tests in parallel
make test-parallel

# See all available commands
make help
```

## 📊 Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Marker**: `@pytest.mark.unit`
- **Command**: `make test-unit` or `pytest -m unit`

### Integration Tests
- **Purpose**: Test component interactions
- **Marker**: `@pytest.mark.integration`
- **Command**: `make test-integration` or `pytest -m integration`

### API Tests
- **Purpose**: Test REST API endpoints
- **Marker**: `@pytest.mark.api`
- **Command**: `make test-api` or `pytest -k "api or endpoint"`

## 🔧 Configuration

### Environment Variables

```bash
export APP_ENV=testing
export DATABASE_URL=sqlite+aiosqlite:///./test.db
export REDIS_URL=redis://localhost:6379/1
export JWT_SECRET_KEY=test-secret-key
```

### pytest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = [
    "--strict-markers",
    "--verbose",
    "--asyncio-mode=auto",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-fail-under=70",
]
testpaths = ["tests"]
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "api: marks tests as API tests",
    "slow: marks tests as slow running",
]
```

## 📈 Coverage Reports

### Terminal Coverage
```bash
# Basic coverage
make test-cov

# HTML coverage report
make test-html
# Then open htmlcov/index.html
```

### Coverage Targets
- **Target**: 70% minimum coverage
- **Current**: Check with `make test-cov`
- **HTML Report**: Generated in `htmlcov/`

## 🧩 Test Fixtures

### Available Fixtures (from conftest.py)

```python
# Service fixtures
user_service            # UserService with mocked dependencies
auth_service           # AuthService with mocked dependencies

# Mock fixtures
mock_user_repository   # Mock user repository
mock_hash_service     # Mock hash service
mock_jwt_service      # Mock JWT service

# Data fixtures
sample_user           # Sample User instance
admin_user           # Sample admin User instance
sample_organization  # Sample Organization instance

# Factory fixtures
user_factory         # User factory function
organization_factory # Organization factory function

# HTTP client fixtures
test_client          # Synchronous FastAPI test client
async_client         # Asynchronous HTTP client
```

### Example Usage

```python
def test_create_user(user_service, mock_user_repository):
    # Test implementation
    pass

async def test_api_endpoint(async_client):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
```

## 🏗️ Writing Tests

### Test Structure Template

```python
"""Test module docstring."""

import pytest
from unittest.mock import AsyncMock

class TestServiceName:
    """Test class for ServiceName."""
    
    @pytest.mark.asyncio
    async def test_method_success(self, fixture_name):
        """Test successful method execution."""
        # Arrange
        
        # Act
        
        # Assert
    
    @pytest.mark.asyncio 
    async def test_method_failure(self, fixture_name):
        """Test method failure scenario."""
        # Arrange
        
        # Act & Assert
        with pytest.raises(ExceptionType):
            await service.method()
```

### Best Practices

1. **Test Naming**: Use descriptive names (`test_create_user_with_valid_data`)
2. **AAA Pattern**: Arrange, Act, Assert
3. **One Assertion**: Test one thing per test function
4. **Mocking**: Mock external dependencies
5. **Async Tests**: Use `@pytest.mark.asyncio` for async functions
6. **Markers**: Use appropriate markers (`@pytest.mark.unit`, etc.)

## 🔍 Test Examples

### Unit Test Example

```python
@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_repository, mock_hash_service):
    """Test successful user creation."""
    # Arrange
    email = "test@example.com"
    password = "password123"
    mock_hash_service.hash.return_value = "hashed_password"
    mock_user_repository.create = AsyncMock(return_value=sample_user)
    
    # Act
    result = await user_service.create_user(email, password, "Test User", 1)
    
    # Assert
    assert result.email == email
    mock_hash_service.hash.assert_called_once_with(password)
    mock_user_repository.create.assert_called_once()
```

### API Test Example

```python
@pytest.mark.asyncio
@pytest.mark.api
async def test_health_endpoint(async_client):
    """Test health check endpoint."""
    # Act
    response = await async_client.get("/health")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

## ⚡ Performance Testing

### Parallel Execution
```bash
# Run tests in parallel
make test-parallel
pytest -n auto
```

### Fast Test Execution
```bash
# Quick tests (no coverage)
make test-fast
pytest -x --tb=short
```

## 🐛 Debugging Tests

### Debug Mode
```bash
# Run with debugging
make test-debug
pytest -s --pdb

# Verbose output
pytest -vvv --tb=long

# Run last failed tests only
pytest --lf
```

### Common Issues

1. **Import Errors**: Check PYTHONPATH and module imports
2. **Async Issues**: Ensure `@pytest.mark.asyncio` is used
3. **Database Issues**: Check DATABASE_URL for testing
4. **Mock Issues**: Verify mock specifications and return values

## 📦 CI/CD Integration

### GitHub Actions

The CI pipeline runs:
1. Linting with ruff
2. Comprehensive test suite
3. Coverage reporting
4. Security scanning
5. Performance tests (on main branch)

### Local CI Simulation
```bash
# Run comprehensive test suite
./test_runner.sh

# Or use CI-like command
make ci-test
```

## 📋 Test Checklist

Before submitting code:

- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained above 70%
- [ ] Tests follow naming conventions
- [ ] Mock dependencies appropriately
- [ ] Async tests use proper markers
- [ ] Integration tests cover happy/sad paths
- [ ] API tests validate response formats

## 🔧 Advanced Testing

### Custom Markers
```python
# Mark slow tests
@pytest.mark.slow
def test_performance_heavy():
    pass

# Mark database tests
@pytest.mark.db
async def test_database_operation():
    pass
```

### Parameterized Tests
```python
@pytest.mark.parametrize("email,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
])
def test_email_validation(email, expected):
    assert validate_email(email) == expected
```

### Test Data Factories
```python
def test_with_factory(user_factory):
    user = user_factory(
        email="custom@example.com",
        role=UserRole.ADMIN
    )
    assert user.role == UserRole.ADMIN
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 🤝 Contributing

When adding new tests:

1. Follow the established patterns
2. Add appropriate markers
3. Update this documentation if needed
4. Ensure tests are deterministic
5. Mock external dependencies
6. Add integration tests for new endpoints
