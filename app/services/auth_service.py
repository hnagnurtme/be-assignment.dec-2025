"""Auth service - business logic for authentication."""

import jwt

from app.core.exceptions import BadRequestException, UnauthorizedException
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.repositories.interfaces import IUserRepository, IOrganizationRepository
from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.interfaces import IHashService, IJwtService


class AuthService:
    """Service class for authentication operations.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles authentication logic
    - Dependency Inversion: Depends on interfaces, not implementations
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        organization_repository: IOrganizationRepository,
        hash_service: IHashService,
        jwt_service: IJwtService,
    ) -> None:
        self._user_repo = user_repository
        self._org_repo = organization_repository
        self._hash_service = hash_service
        self._jwt_service = jwt_service

    async def register(self, data: RegisterRequest) -> User:
        """Register a new user with optional organization creation."""
        # Check if email already exists
        if await self._user_repo.email_exists(data.email):
            raise BadRequestException("Email already registered")

        # Create or require organization
        if data.organization_name:
            # Create new organization and user as admin
            organization = Organization(name=data.organization_name)
            organization = await self._org_repo.create(organization)

            user = User(
                email=data.email,
                password_hash=self._hash_service.hash(data.password),
                full_name=data.full_name,
                organization_id=organization.id,
                role=UserRole.ADMIN,
                is_active=True,
            )
            user = await self._user_repo.create(user)
        else:
            raise BadRequestException(
                "Organization name is required for registration. "
                "To join an existing organization, please ask an admin to add you."
            )

        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self._user_repo.get_by_email(email)

        if user is None:
            raise UnauthorizedException("Invalid email or password")

        if not self._hash_service.verify(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is deactivated")

        # Generate tokens
        token_data = {"sub": user.id}
        access_token = self._jwt_service.create_access_token(token_data)
        refresh_token = self._jwt_service.create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            payload = self._jwt_service.decode_token(refresh_token)
            user_id = payload.get("sub")
            token_type = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise UnauthorizedException("Invalid refresh token")

        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid refresh token")

        # Verify user still exists and is active
        user = await self._user_repo.get_by_id(int(user_id))
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or deactivated")

        # Generate new tokens
        token_data = {"sub": user.id}
        new_access_token = self._jwt_service.create_access_token(token_data)
        new_refresh_token = self._jwt_service.create_refresh_token(token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
