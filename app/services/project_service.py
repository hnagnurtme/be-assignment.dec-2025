from fastapi import HTTPException, status

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User, UserRole
from app.repositories.interfaces.project_repository import IProjectRepository
from app.repositories.interfaces.user_repository import IUserRepository


class ProjectService:

    def __init__(
        self,
        project_repo: IProjectRepository,
        user_repo: IUserRepository,
    ) -> None:
        self._project_repo = project_repo
        self._user_repo = user_repo

    async def create_project(
        self,
        name: str,
        description: str | None,
        organization_id: int,
        created_by_id: int,
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            description=description,
            organization_id=organization_id,
            created_by_id=created_by_id,
        )
        return await self._project_repo.create(project)

    async def get_project_by_id(self, project_id: int, user: User) -> Project:
        """Get project by ID with authorization check."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Check if user has access to this project
        if not await self._can_access_project(project, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        return project

    async def list_projects(
        self,
        organization_id: int,
        user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """List projects based on user role."""
        # Admin and Manager can see all projects in their organization
        if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return await self._project_repo.get_by_organization(
                organization_id, skip, limit
            )

        # Members can only see projects they are part of
        return await self._project_repo.get_user_projects(user.id, skip, limit)

    async def update_project(
        self,
        project_id: int,
        user: User,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        """Update project (Admin/Manager only)."""
        # Check authorization
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Manager can update projects",
            )

        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Check if project belongs to user's organization
        if project.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        # Update fields
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description

        return await self._project_repo.update(project)

    async def delete_project(self, project_id: int, user: User) -> None:
        """Delete project (Admin only)."""
        # Only Admin can delete projects
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin can delete projects",
            )

        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Check if project belongs to user's organization
        if project.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        await self._project_repo.delete(project)

    async def add_member(
        self,
        project_id: int,
        user_id: int,
        current_user: User,
    ) -> ProjectMember:
        """Add member to project (Admin/Manager only)."""
        # Check authorization
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Manager can add members",
            )

        # Check if project exists and user has access
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        # Check if user to be added exists and is in the same organization
        user_to_add = await self._user_repo.get_by_id(user_id)
        if not user_to_add:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user_to_add.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be in the same organization",
            )

        # Check if user is already a member
        if await self._project_repo.is_member(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this project",
            )

        return await self._project_repo.add_member(project_id, user_id)

    async def remove_member(
        self,
        project_id: int,
        user_id: int,
        current_user: User,
    ) -> None:
        """Remove member from project (Admin/Manager only)."""
        # Check authorization
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Manager can remove members",
            )

        # Check if project exists and user has access
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        # Check if user is a member
        if not await self._project_repo.is_member(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this project",
            )

        await self._project_repo.remove_member(project_id, user_id)

    async def get_members(self, project_id: int, user: User) -> list[User]:
        """Get project members."""
        # Check if project exists and user has access
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        if not await self._can_access_project(project, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        return await self._project_repo.get_members(project_id)

    async def _can_access_project(self, project: Project, user: User) -> bool:
        """Check if user can access a project."""
        # Check if project belongs to user's organization
        if project.organization_id != user.organization_id:
            return False

        # Admin and Manager can access all projects in their organization
        if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return True

        # Members can only access projects they are part of
        return await self._project_repo.is_member(project.id, user.id)
