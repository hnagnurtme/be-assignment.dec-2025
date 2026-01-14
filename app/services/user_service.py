"""User service - business logic for user operations."""

from app.models.user import User, UserRole
from app.repositories.interfaces import IUserRepository
from app.services.interfaces import IHashService


class UserService:
    """Service class for user-related operations.
    
    Dependencies are injected following SOLID principles:
    - Depends on IUserRepository and IHashService interfaces
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        hash_service: IHashService,
    ) -> None:
        self._user_repo = user_repository
        self._hash_service = hash_service

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        return await self._user_repo.get_by_email(email)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get a user by ID."""
        return await self._user_repo.get_by_id(user_id)

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        organization_id: int,
        role: UserRole = UserRole.MEMBER,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=self._hash_service.hash(password),
            full_name=full_name,
            organization_id=organization_id,
            role=role,
            is_active=True,
        )
        return await self._user_repo.create(user)

    async def update_user(
        self,
        user: User,
        full_name: str | None = None,
    ) -> User:
        """Update user profile."""
        if full_name is not None:
            user.full_name = full_name
        return await self._user_repo.update(user)

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return await self._user_repo.email_exists(email)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against hash."""
        return self._hash_service.verify(password, hashed)
