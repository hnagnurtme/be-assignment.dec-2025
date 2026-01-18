from fastapi import APIRouter, status

from app.constants import AuthDocs, Messages
from app.dependencies import AuthSvc
from app.schemas import (
    ApiResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary=AuthDocs.Register.SUMMARY,
    description=AuthDocs.Register.DESCRIPTION,
)
async def register(
    data: RegisterRequest,
    auth_service: AuthSvc,
) -> ApiResponse[UserResponse]:
    user = await auth_service.register(data)
    return ApiResponse(
        message=Messages.USER_REGISTERED,
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary=AuthDocs.Login.SUMMARY,
    description=AuthDocs.Login.DESCRIPTION,
)
async def login(
    data: LoginRequest,
    auth_service: AuthSvc,
) -> ApiResponse[TokenResponse]:
    tokens = await auth_service.login(data.email, data.password)
    return ApiResponse(
        message=Messages.LOGIN_SUCCESS,
        data=tokens,
    )


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    summary=AuthDocs.Refresh.SUMMARY,
    description=AuthDocs.Refresh.DESCRIPTION,
)
async def refresh_token(
    data: RefreshRequest,
    auth_service: AuthSvc,
) -> ApiResponse[TokenResponse]:
    tokens = await auth_service.refresh_token(data.refresh_token)
    return ApiResponse(
        message=Messages.TOKEN_REFRESHED,
        data=tokens,
    )
