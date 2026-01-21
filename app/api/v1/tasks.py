"""Task API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.constants import Messages, TaskDocs, CommentDocs, ReportDocs
from app.core.auth import CurrentUser
from app.dependencies import TaskSvc
from app.models.task import TaskStatus, TaskPriority
from app.schemas import (
    ApiResponse,
    AttachmentResponse,
    CommentCreate,
    CommentResponse,
    PaginatedResponse,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
    create_pagination_meta,
)

from fastapi import File, UploadFile
import os
import uuid
from app.config import settings

router = APIRouter(tags=["Tasks"])


@router.post(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[TaskResponse],
    summary=TaskDocs.Create.SUMMARY,
    description=TaskDocs.Create.DESCRIPTION,
)
async def create_task(
    project_id: int,
    data: TaskCreate,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[TaskResponse]:
    """Create a new task in a project."""
    task = await task_service.create_task(project_id, current_user, data)
    return ApiResponse(
        message=Messages.TASK_CREATED,
        data=TaskResponse.model_validate(task),
    )


@router.get(
    "/projects/{project_id}/tasks",
    response_model=PaginatedResponse[TaskResponse],
    summary=TaskDocs.List.SUMMARY,
    description=TaskDocs.List.DESCRIPTION,
)
async def list_tasks(
    project_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
    status: TaskStatus | None = Query(None, description="Filter by status"),
    priority: TaskPriority | None = Query(None, description="Filter by priority"),
    assignee_id: int | None = Query(None, description="Filter by assignee"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[TaskResponse]:
    """List tasks in a project with filtering and pagination."""
    skip = (page - 1) * per_page
    tasks, total = await task_service.list_tasks(
        project_id=project_id,
        user=current_user,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        skip=skip,
        limit=per_page,
    )
    return PaginatedResponse(
        message=Messages.TASK_LIST_RETRIEVED,
        data=[TaskResponse.model_validate(t) for t in tasks],
        meta=create_pagination_meta(page, per_page, total),
    )


@router.get(
    "/tasks/{task_id}",
    response_model=ApiResponse[TaskResponse],
    summary=TaskDocs.Get.SUMMARY,
    description=TaskDocs.Get.DESCRIPTION,
)
async def get_task(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[TaskResponse]:
    """Get task details."""
    task = await task_service.get_task_by_id(task_id, current_user)
    return ApiResponse(
        message=Messages.TASK_RETRIEVED,
        data=TaskResponse.model_validate(task),
    )


@router.put(
    "/tasks/{task_id}",
    response_model=ApiResponse[TaskResponse],
    summary=TaskDocs.Update.SUMMARY,
    description=TaskDocs.Update.DESCRIPTION,
)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[TaskResponse]:
    """Update task details."""
    task = await task_service.update_task(task_id, current_user, data)
    return ApiResponse(
        message=Messages.TASK_UPDATED,
        data=TaskResponse.model_validate(task),
    )


@router.patch(
    "/tasks/{task_id}/status",
    response_model=ApiResponse[TaskResponse],
    summary=TaskDocs.UpdateStatus.SUMMARY,
    description=TaskDocs.UpdateStatus.DESCRIPTION,
)
async def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[TaskResponse]:
    """Update task status (forward only)."""
    task = await task_service.update_status(task_id, current_user, data.status)
    return ApiResponse(
        message=Messages.TASK_STATUS_UPDATED,
        data=TaskResponse.model_validate(task),
    )


@router.delete(
    "/tasks/{task_id}",
    response_model=ApiResponse[None],
    summary=TaskDocs.Delete.SUMMARY,
    description=TaskDocs.Delete.DESCRIPTION,
)
async def delete_task(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[None]:
    """Delete a task (Admin/Manager only)."""
    await task_service.delete_task(task_id, current_user)
    return ApiResponse(
        message=Messages.TASK_DELETED,
        data=None,
    )


# Report Endpoints

@router.get(
    "/projects/{project_id}/reports/task-count",
    response_model=ApiResponse[dict[str, int]],
    summary=ReportDocs.TaskCount.SUMMARY,
    description=ReportDocs.TaskCount.DESCRIPTION,
)
async def get_task_count_report(
    project_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[dict[str, int]]:
    """Get counts of tasks by status."""
    counts = await task_service.get_task_counts(project_id, current_user)
    return ApiResponse(
        message=Messages.REPORT_RETRIEVED,
        data=counts,
    )


@router.get(
    "/projects/{project_id}/reports/overdue-tasks",
    response_model=ApiResponse[list[TaskResponse]],
    summary=ReportDocs.OverdueTasks.SUMMARY,
    description=ReportDocs.OverdueTasks.DESCRIPTION,
)
async def get_overdue_tasks(
    project_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[list[TaskResponse]]:
    """Get overdue tasks in project."""
    tasks = await task_service.get_overdue_tasks(project_id, current_user)
    return ApiResponse(
        message=Messages.REPORT_RETRIEVED,
        data=[TaskResponse.model_validate(t) for t in tasks],
    )


# Comment Endpoints

@router.post(
    "/tasks/{task_id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[CommentResponse],
    summary=CommentDocs.Create.SUMMARY,
    description=CommentDocs.Create.DESCRIPTION,
)
async def add_comment(
    task_id: int,
    data: CommentCreate,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[CommentResponse]:
    """Add a comment to a task."""
    comment = await task_service.add_comment(task_id, current_user, data.content)
    return ApiResponse(
        message=Messages.COMMENT_ADDED,
        data=CommentResponse.model_validate(comment),
    )


@router.get(
    "/tasks/{task_id}/comments",
    response_model=ApiResponse[list[CommentResponse]],
    summary=CommentDocs.List.SUMMARY,
    description=CommentDocs.List.DESCRIPTION,
)
async def list_comments(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[list[CommentResponse]]:
    """List all comments on a task."""
    comments = await task_service.list_comments(task_id, current_user)
    return ApiResponse(
        message=Messages.COMMENTS_RETRIEVED,
        data=[CommentResponse.model_validate(c) for c in comments],
    )


@router.delete(
    "/comments/{comment_id}",
    response_model=ApiResponse[None],
    summary="Delete comment",
    description="Delete a comment by ID (Owner/Admin only).",
)
async def delete_comment(
    comment_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[None]:
    """Delete a comment."""
    await task_service.delete_comment(comment_id, current_user)
    return ApiResponse(
        message=Messages.DELETED,
        data=None,
    )


# Attachment Endpoints

@router.post(
    "/tasks/{task_id}/attachments",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[AttachmentResponse],
    summary="Upload attachment",
    description="Upload a file đính kèm (max 5MB, tối đa 3 files/task).",
)
async def upload_attachment(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
    file: UploadFile = File(...),
) -> ApiResponse[AttachmentResponse]:
    """Upload a file attachment."""
    # BR5: File Size Limit (5MB)
    MAX_SIZE = 5 * 1024 * 1024
    # Read file to check size
    content = await file.read()
    if len(content) > MAX_SIZE:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("File size exceeds 5MB limit")
    
    # Ensure upload directory exists
    upload_dir = os.path.join("storage", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
        
    attachment = await task_service.add_attachment(
        task_id=task_id,
        user=current_user,
        file_path=file_path,
        file_name=file.filename,
        file_type=file.content_type,
        file_size=len(content),
    )
    
    return ApiResponse(
        message=Messages.CREATED,
        data=AttachmentResponse.model_validate(attachment),
    )


@router.get(
    "/tasks/{task_id}/attachments",
    response_model=ApiResponse[list[AttachmentResponse]],
    summary="List attachments",
    description="Get all attachments for a task.",
)
async def list_attachments(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[list[AttachmentResponse]]:
    """List task attachments."""
    attachments = await task_service.list_attachments(task_id, current_user)
    return ApiResponse(
        message=Messages.SUCCESS,
        data=[AttachmentResponse.model_validate(a) for a in attachments],
    )


@router.delete(
    "/attachments/{attachment_id}",
    response_model=ApiResponse[None],
    summary="Delete attachment",
    description="Delete an attachment and its local file.",
)
async def delete_attachment(
    attachment_id: int,
    current_user: CurrentUser,
    task_service: TaskSvc,
) -> ApiResponse[None]:
    """Delete an attachment."""
    attachment = await task_service.get_attachment_by_id(attachment_id, current_user)
    
    # Delete local file
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
        
    await task_service.delete_attachment(attachment_id, current_user)
    
    return ApiResponse(
        message=Messages.DELETED,
        data=None,
    )
