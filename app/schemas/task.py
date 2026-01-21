"""Task schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status."""
    status: TaskStatus


class TaskResponse(BaseModel):
    """Response schema for task data."""
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    project_id: int
    assignee_id: int | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    """Response schema for comment data."""
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttachmentResponse(BaseModel):
    """Response schema for attachment data."""
    id: int
    file_name: str
    file_path: str
    file_type: str | None
    file_size: int | None
    task_id: int
    user_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
