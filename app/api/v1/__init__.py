"""API v1 router - includes all v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.projects import router as projects_router
from app.api.v1.users import router as users_router

# Create v1 router
router = APIRouter(prefix="/api/v1")

# Include endpoint routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(projects_router)
router.include_router(health_router)

