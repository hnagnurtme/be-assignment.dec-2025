"""Project schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(min_length=1, max_length=255, description="Project name")
    description: str | None = Field(default=None, description="Project description")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None)


class ProjectResponse(BaseModel):
    """Response schema for project data."""

    id: int
    name: str
    description: str | None
    organization_id: int
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberAdd(BaseModel):
    """Schema for adding a member to a project."""

    user_id: int = Field(gt=0, description="User ID to add to the project")


class ProjectMemberResponse(BaseModel):
    """Response schema for project member data."""

    user_id: int
    project_id: int
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Response schema for paginated project list."""

    projects: list[ProjectResponse]
    total: int
    page: int
    per_page: int
