"""User API endpoints."""

from fastapi import APIRouter

from app.constants import UserDocs, Messages
from app.core.auth import CurrentUser
from app.dependencies import UserSvc
from app.schemas import ApiResponse, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary=UserDocs.GetMe.SUMMARY,
    description=UserDocs.GetMe.DESCRIPTION,
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> ApiResponse[UserResponse]:
    """Get current user profile."""
    return ApiResponse(
        message=Messages.USER_PROFILE_RETRIEVED,
        data=UserResponse.model_validate(current_user),
    )


@router.put(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary=UserDocs.UpdateMe.SUMMARY,
    description=UserDocs.UpdateMe.DESCRIPTION,
)
async def update_current_user_profile(
    data: UserUpdate,
    current_user: CurrentUser,
    user_service: UserSvc,
) -> ApiResponse[UserResponse]:
    """Update current user profile."""
    updated_user = await user_service.update_user(
        user=current_user,
        full_name=data.full_name,
    )
    return ApiResponse(
        message=Messages.USER_PROFILE_UPDATED,
        data=UserResponse.model_validate(updated_user),
    )
