"""Project API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.constants import Messages, ProjectDocs
from app.core.auth import CurrentUser, require_admin, require_manager
from app.dependencies import ProjectSvc
from app.schemas import (
    ApiResponse,
    PaginatedResponse,
    ProjectCreate,
    ProjectMemberAdd,
    ProjectResponse,
    ProjectUpdate,
    UserResponse,
    create_pagination_meta,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ApiResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary=ProjectDocs.Create.SUMMARY,
    description=ProjectDocs.Create.DESCRIPTION,
)
async def create_project(
    data: ProjectCreate,
    current_user: Annotated[CurrentUser, Depends(require_manager)],
    project_service: ProjectSvc,
) -> ApiResponse[ProjectResponse]:
    """Create a new project (Admin/Manager only)."""
    project = await project_service.create_project(
        name=data.name,
        description=data.description,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
    )
    return ApiResponse(
        message=Messages.PROJECT_CREATED,
        data=ProjectResponse.model_validate(project),
    )


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    summary=ProjectDocs.List.SUMMARY,
    description=ProjectDocs.List.DESCRIPTION,
)
async def list_projects(
    current_user: CurrentUser,
    project_service: ProjectSvc,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[ProjectResponse]:
    """List projects based on user role with pagination."""
    # Calculate skip from page number
    skip = (page - 1) * per_page
    
    projects, total = await project_service.list_projects(
        organization_id=current_user.organization_id,
        user=current_user,
        skip=skip,
        limit=per_page,
    )
    
    return PaginatedResponse(
        message=Messages.PROJECT_LIST_RETRIEVED,
        data=[ProjectResponse.model_validate(p) for p in projects],
        meta=create_pagination_meta(
            page=page,
            per_page=per_page,
            total_items=total,
        ),
    )


@router.get(
    "/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    summary=ProjectDocs.Get.SUMMARY,
    description=ProjectDocs.Get.DESCRIPTION,
)
async def get_project(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectSvc,
) -> ApiResponse[ProjectResponse]:
    """Get project details."""
    project = await project_service.get_project_by_id(project_id, current_user)
    return ApiResponse(
        message=Messages.PROJECT_RETRIEVED,
        data=ProjectResponse.model_validate(project),
    )


@router.put(
    "/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    summary=ProjectDocs.Update.SUMMARY,
    description=ProjectDocs.Update.DESCRIPTION,
)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: Annotated[CurrentUser, Depends(require_manager)],
    project_service: ProjectSvc,
) -> ApiResponse[ProjectResponse]:
    """Update project (Admin/Manager only)."""
    project = await project_service.update_project(
        project_id=project_id,
        user=current_user,
        name=data.name,
        description=data.description,
    )
    return ApiResponse(
        message=Messages.PROJECT_UPDATED,
        data=ProjectResponse.model_validate(project),
    )


@router.delete(
    "/{project_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary=ProjectDocs.Delete.SUMMARY,
    description=ProjectDocs.Delete.DESCRIPTION,
)
async def delete_project(
    project_id: int,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    project_service: ProjectSvc,
) -> ApiResponse[None]:
    """Delete project (Admin only)."""
    await project_service.delete_project(project_id, current_user)
    return ApiResponse(
        message=Messages.PROJECT_DELETED,
        data=None,
    )


@router.post(
    "/{project_id}/members",
    response_model=ApiResponse[None],
    status_code=status.HTTP_201_CREATED,
    summary=ProjectDocs.AddMember.SUMMARY,
    description=ProjectDocs.AddMember.DESCRIPTION,
)
async def add_project_member(
    project_id: int,
    data: ProjectMemberAdd,
    current_user: Annotated[CurrentUser, Depends(require_manager)],
    project_service: ProjectSvc,
) -> ApiResponse[None]:
    """Add member to project (Admin/Manager only)."""
    await project_service.add_member(
        project_id=project_id,
        user_id=data.user_id,
        current_user=current_user,
    )
    return ApiResponse(
        message=Messages.PROJECT_MEMBER_ADDED,
        data=None,
    )


@router.delete(
    "/{project_id}/members/{user_id}",
    response_model=ApiResponse[None],
    summary=ProjectDocs.RemoveMember.SUMMARY,
    description=ProjectDocs.RemoveMember.DESCRIPTION,
)
async def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: Annotated[CurrentUser, Depends(require_manager)],
    project_service: ProjectSvc,
) -> ApiResponse[None]:
    """Remove member from project (Admin/Manager only)."""
    await project_service.remove_member(
        project_id=project_id,
        user_id=user_id,
        current_user=current_user,
    )
    return ApiResponse(
        message=Messages.PROJECT_MEMBER_REMOVED,
        data=None,
    )


@router.get(
    "/{project_id}/members",
    response_model=ApiResponse[list[UserResponse]],
    summary="List project members",
    description="Get a list of all members in the project.",
)
async def list_project_members(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectSvc,
) -> ApiResponse[list[UserResponse]]:
    """List project members."""
    members = await project_service.get_members(project_id, current_user)
    return ApiResponse(
        message=Messages.PROJECT_MEMBERS_RETRIEVED,
        data=[UserResponse.model_validate(m) for m in members],
    )
