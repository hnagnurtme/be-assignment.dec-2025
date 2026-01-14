"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class OrganizationInfo(BaseModel):
    """Embedded organization info in user response."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    organization: OrganizationInfo
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Request schema for updating user profile."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)


class UserCreate(BaseModel):
    """Request schema for admin creating a user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.MEMBER
