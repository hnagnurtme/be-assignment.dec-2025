"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.config import settings
from app.core.logging import get_logger, setup_logging
from app.mcp.server import MCPServer
from mcp.server.sse import SseServerTransport
from app.middleware import (
    AuthMiddleware,
    ExceptionMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    RequestIdMiddleware,
    ValidationMiddleware,
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting application", app_name=settings.app_name)
    
    # Initialize MCP Server
    mcp_server = MCPServer(app)
    app.state.mcp_server = mcp_server
    
    yield
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-organization Task Management API with authentication and RBAC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ============================================================
# Middleware Stack (order matters - executed in reverse order)
# Bottom of stack = first to process request, last to process response
# ============================================================

# 1. CORS - outermost, handles preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Exception Handler - catches all exceptions from inner middleware
app.add_middleware(ExceptionMiddleware)

# 3. Request ID - generates unique ID for tracing
app.add_middleware(RequestIdMiddleware)

# 4. Logging - logs requests/responses with timing
app.add_middleware(LoggingMiddleware)

# 5. Rate Limiting - protects against abuse (100 req/min per IP)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 6. Validation - validates request content and security
app.add_middleware(ValidationMiddleware, max_content_length=10 * 1024 * 1024)  # 10MB

# 7. Auth - validates JWT tokens (innermost for protected routes)
app.add_middleware(AuthMiddleware)


# ============================================================
# Routers
# ============================================================

app.include_router(v1_router)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ============================================================
# MCP Server SSE Endpoint
# ============================================================

@app.get("/mcp/sse")
async def sse_endpoint(request: Request):
    """MCP Server SSE connection endpoint."""
    mcp_server: MCPServer = request.app.state.mcp_server
    sse = SseServerTransport("/mcp/messages")
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await mcp_server.server.run(read, write, mcp_server.server.create_initialization_options())
