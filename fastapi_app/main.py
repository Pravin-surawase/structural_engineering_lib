"""
FastAPI Application Entry Point.

This module creates and configures the FastAPI application with:
- CORS middleware for React frontend
- OpenAPI documentation metadata
- Router mounting for all API endpoints
- Health check and version endpoints

Usage:
    uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000

API Docs:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json
"""

import logging
import traceback
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse as StarletteJSONResponse

from fastapi_app import __version__
from fastapi_app.config import get_settings
from fastapi_app.routers import (
    analysis,
    column,
    design,
    detailing,
    export,
    geometry,
    health,
    imports,
    insights,
    optimization,
    rebar,
    streaming,
    websocket,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Application Metadata for OpenAPI
# =============================================================================

API_TITLE = "Structural Engineering API"
API_DESCRIPTION = """
## IS 456:2000 Compliant Structural Engineering Library

This API provides comprehensive structural engineering calculations following
the Indian Standard IS 456:2000 for reinforced concrete design.

### Features

- **Beam Design**: Flexure, shear, and combined design calculations
- **Detailing**: Reinforcement layout, spacing, and development lengths
- **Optimization**: Cost-optimized beam cross-section selection
- **Smart Analysis**: AI-assisted design suggestions and insights
- **3D Geometry**: Visualization-ready mesh generation

### Design Codes

- IS 456:2000 - Plain and Reinforced Concrete
- IS 13920 - Ductile Detailing for Seismic Resistance

### Units

All inputs and outputs use consistent units:
- **Length**: millimeters (mm)
- **Force**: kilonewtons (kN)
- **Moment**: kilonewton-meters (kN·m)
- **Stress**: N/mm² (MPa)
- **Area**: mm²
"""

API_TAGS_METADATA = [
    {
        "name": "health",
        "description": "Health check and system status endpoints.",
    },
    {
        "name": "design",
        "description": "Beam design calculations for flexure, shear, and combined loading.",
    },
    {
        "name": "column",
        "description": "Column design: classification, eccentricity, and axial capacity per IS 456.",
    },
    {
        "name": "detailing",
        "description": "Reinforcement detailing including bar layout, spacing, and anchorage.",
    },
    {
        "name": "optimization",
        "description": "Cost optimization and efficient section selection.",
    },
    {
        "name": "analysis",
        "description": "Smart analysis with design suggestions and insights.",
    },
    {
        "name": "geometry",
        "description": "3D geometry generation for visualization.",
    },
    {
        "name": "websocket",
        "description": "WebSocket endpoints for live design updates.",
    },
    {
        "name": "streaming",
        "description": "Server-Sent Events (SSE) for batch processing and progress.",
    },
    {
        "name": "import",
        "description": "CSV import using structural_lib adapters (ETABS, SAFE, STAAD, Generic).",
    },
]

# =============================================================================
# FastAPI Application Instance
# =============================================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=__version__,
    openapi_tags=API_TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    contact={
        "name": "Structural Engineering Library",
        "url": "https://github.com/yourusername/structural_engineering_lib",
    },
)

# =============================================================================
# Auth Middleware (opt-in via AUTH_ENABLED=True)
# =============================================================================


class AuthMiddleware(BaseHTTPMiddleware):
    """Enforce Bearer-token auth on all endpoints when AUTH_ENABLED=True."""

    PUBLIC_PATHS = frozenset({"/", "/health", "/docs", "/openapi.json", "/redoc"})

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if not settings.auth_enabled:
            return await call_next(request)

        path = request.url.path
        if path in self.PUBLIC_PATHS or path.startswith("/ws/"):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return StarletteJSONResponse(
                status_code=401, content={"detail": "Not authenticated"}
            )

        token = auth_header.removeprefix("Bearer ")
        try:
            from fastapi_app.auth import decode_token

            decode_token(token)
        except Exception:
            return StarletteJSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        return await call_next(request)


app.add_middleware(AuthMiddleware)

# =============================================================================
# CORS Middleware Configuration
# =============================================================================

# Allow all origins in development; restrict in production
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8080",  # Alternative dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# =============================================================================
# Request ID Middleware
# =============================================================================


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique X-Request-ID header to every request/response."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(RequestIDMiddleware)

# =============================================================================
# Global Exception Handlers for structural_lib errors
# =============================================================================

try:
    from structural_lib.core.errors import (
        CalculationError,
        ComplianceError,
        ConfigurationError,
        DesignConstraintError,
        StructuralLibError,
        ValidationError,
    )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle input validation errors from structural_lib."""
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": exc.message,
                "suggestion": exc.suggestion,
                "clause_ref": exc.clause_ref,
                "details": exc.details,
            },
        )

    @app.exception_handler(DesignConstraintError)
    async def design_constraint_handler(request: Request, exc: DesignConstraintError):
        """Handle infeasible design errors from structural_lib."""
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "DESIGN_CONSTRAINT_ERROR",
                "message": exc.message,
                "suggestion": exc.suggestion,
                "clause_ref": exc.clause_ref,
                "details": exc.details,
            },
        )

    @app.exception_handler(ComplianceError)
    async def compliance_error_handler(request: Request, exc: ComplianceError):
        """Handle IS 456 compliance violations from structural_lib."""
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "COMPLIANCE_ERROR",
                "message": exc.message,
                "suggestion": exc.suggestion,
                "clause_ref": exc.clause_ref,
                "details": exc.details,
            },
        )

    @app.exception_handler(ConfigurationError)
    async def config_error_handler(request: Request, exc: ConfigurationError):
        """Handle library misconfiguration errors."""
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "CONFIGURATION_ERROR",
                "message": exc.message,
                "suggestion": exc.suggestion,
                "details": exc.details,
            },
        )

    @app.exception_handler(CalculationError)
    async def calculation_error_handler(request: Request, exc: CalculationError):
        """Handle numerical/calculation errors from structural_lib."""
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "CALCULATION_ERROR",
                "message": exc.message,
                "suggestion": exc.suggestion,
                "details": exc.details,
            },
        )

    @app.exception_handler(StructuralLibError)
    async def structural_lib_error_handler(request: Request, exc: StructuralLibError):
        """Catch-all for any StructuralLibError not handled above."""
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "STRUCTURAL_LIB_ERROR",
                "message": exc.message,
                "suggestion": exc.suggestion,
                "clause_ref": exc.clause_ref,
                "details": exc.details,
            },
        )

except ImportError:
    # structural_lib not installed — handlers will not be registered
    pass


# =============================================================================
# Generic Exception Handler — OWASP A05 Stack Trace Sanitization
# =============================================================================


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions. Logs full traceback server-side,
    returns a generic 500 response to the client (no internal details leaked)."""
    logger.error(
        "Unhandled exception: %s\n%s",
        str(exc),
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )


# =============================================================================
# Router Registration
# =============================================================================

# Health check first (priority routing)
app.include_router(health.router)

# API routers under /api/v1 prefix
API_V1_PREFIX = "/api/v1"

app.include_router(
    design.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    column.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    detailing.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    optimization.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    analysis.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    geometry.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    imports.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    rebar.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    insights.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    export.router,
    prefix=API_V1_PREFIX,
)

# WebSocket router (no prefix - ws://host/ws/...)
app.include_router(websocket.router)

# Streaming router (SSE for batch processing)
app.include_router(streaming.router)

# =============================================================================
# Root Endpoint
# =============================================================================


@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint providing API information.

    Returns basic API information and links to documentation.
    """
    return {
        "name": API_TITLE,
        "version": __version__,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "api_prefix": API_V1_PREFIX,
        "status": "operational",
    }


# =============================================================================
# Application Lifecycle Events
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Initializes any required resources or connections.
    """
    settings = get_settings()
    if not settings.auth_enabled:
        logger.warning(
            "AUTH_ENABLED=False — all endpoints are PUBLIC. "
            "Set AUTH_ENABLED=True for production."
        )


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.

    Cleans up resources and connections.
    """
    # Future: Close database connections, flush caches, etc.
    pass
