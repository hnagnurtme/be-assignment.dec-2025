from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import HealthDocs, Messages
from app.db.session import get_db
from app.schemas import ApiResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=ApiResponse[dict],
    summary=HealthDocs.Check.SUMMARY,
    description=HealthDocs.Check.DESCRIPTION,
)
async def health_check() -> ApiResponse[dict]:
    """Basic health check endpoint."""
    return ApiResponse(
        message=Messages.API_HEALTHY,
        data={"status": "ok"},
    )


@router.get(
    "/db",
    response_model=ApiResponse[dict],
    summary=HealthDocs.Database.SUMMARY,
    description=HealthDocs.Database.DESCRIPTION,
)
async def database_health_check(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[dict]:
    """Check database connectivity."""
    await db.execute(text("SELECT 1"))
    return ApiResponse(
        message=Messages.DATABASE_HEALTHY,
        data={"status": "ok", "database": "postgresql"},
    )
