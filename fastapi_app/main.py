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

import jwt
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse as StarletteJSONResponse

from fastapi_app import __version__
from fastapi_app.auth import RateLimiter
from fastapi_app.config import get_settings
from fastapi_app.models.metadata import APIInfoResponse
from fastapi_app.models.response import ProblemResponse, error_response
from fastapi_app.routers import (
    analysis,
    building_gravity,
    catalog,
    capabilities,
    column,
    combined_footing,
    deep_beam,
    design,
    design_v2,
    detailing,
    etabs_bridge,
    excel_workbench,
    export,
    flat_slab,
    footing,
    geometry,
    health,
    imports,
    insights,
    library_core,
    optimization,
    rebar,
    staircase,
    strap_footing,
    streaming,
    wall,
    websocket,
    workflows,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Application Metadata for OpenAPI
# =============================================================================

API_TITLE = "Structural Engineering API"
API_DESCRIPTION = """
## IS 456:2000 Compliant Structural Engineering Library

This API exposes the library's route-specific supported IS 456:2000 reinforced
concrete calculations. Each result remains inside its documented case
boundary. Engineer review is one final-stage activity after the integrated
library is complete, not an intermediate API-development gate.

### Features

- **Beam Design**: Flexure, shear, and combined design calculations
- **Column Design**: Bounded rectangular short/long-column workflows
- **Footing Design**: Isolated-footing checks and concentric load transfer
- **Slab Design**: Bounded simply supported one-way slab strip
- **Staircase Design**: Bounded longitudinal straight waist-slab flight
- **Wall Design**: Bounded Clause 32 braced-wall axial and reinforcement checks
- **Deep-Beam Design**: Bounded Clause 29 simply supported positive-reinforcement checks
- **Flat-Slab Design**: Bounded regular interior direct-design and punching checks
- **Combined-Footing Design**: Bounded symmetric two-column rigid-footing checks
- **Strap-Footing Design**: Bounded property-line no-soil-contact strap checks
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
        "name": "library",
        "description": "Canonical supported/held capability and semantic discovery.",
    },
    {
        "name": "catalog",
        "description": "Versioned application workflow discovery from library-owned truth.",
    },
    {
        "name": "column",
        "description": "Column design: classification, eccentricity, and axial capacity per IS 456.",
    },
    {
        "name": "footing",
        "description": "Bounded isolated-footing design and maintained evidence.",
    },
    {
        "name": "staircase",
        "description": "Bounded straight-flight staircase design and maintained evidence.",
    },
    {
        "name": "wall",
        "description": "Bounded Clause 32 braced-wall checks and maintained evidence.",
    },
    {
        "name": "deep-beam",
        "description": "Bounded Clause 29 deep-beam checks and maintained evidence.",
    },
    {
        "name": "flat-slab",
        "description": "Bounded regular interior flat-slab checks and maintained evidence.",
    },
    {
        "name": "combined-footing",
        "description": "Bounded symmetric two-column combined-footing checks and maintained evidence.",
    },
    {
        "name": "strap-footing",
        "description": "Bounded property-line strap-footing checks and maintained evidence.",
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
        "name": "building-gravity",
        "description": "Bounded one-storey dead/live gravity load path and component review.",
    },
    {
        "name": "excel-workbench",
        "description": "Selected-table Excel mapping, canonical beam review, and stale evidence.",
    },
    {
        "name": "etabs-bridge",
        "description": "Bounded Windows ETABS pilot plus preflight-bound read-only W2 beam baseline.",
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
        "name": "workflows",
        "description": "Explicitly activated bounded local/test workflow execution.",
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
    responses={
        400: {"model": ProblemResponse, "description": "Bad request"},
        401: {"model": ProblemResponse, "description": "Authentication required"},
        403: {"model": ProblemResponse, "description": "Forbidden"},
        404: {"model": ProblemResponse, "description": "Resource not found"},
        409: {"model": ProblemResponse, "description": "State conflict"},
        422: {
            "model": ProblemResponse,
            "description": "Request validation failed",
        },
        429: {"model": ProblemResponse, "description": "Concurrency or rate limit"},
        500: {"model": ProblemResponse, "description": "Internal application error"},
        503: {"model": ProblemResponse, "description": "Capability unavailable"},
    },
)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Map every Pydantic request failure to the maintained API envelope."""
    if request.url.path.startswith("/api/v2/"):
        from structural_lib.services.contracts.common import (
            input_issues_from_details,
        )

        issues = input_issues_from_details(exc.errors(), drop_location_prefix="body")
        error = {
            "code": "INPUT_CONTRACT_INVALID",
            "message": f"Input contract rejected {len(issues)} issue(s).",
            "details": {"issues": [issue.to_dict() for issue in issues]},
        }
    else:
        error = {
            "code": "REQUEST_VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": jsonable_encoder(exc.errors()),
        }
    return JSONResponse(
        status_code=422,
        content=error_response(
            error,
            request_id=getattr(request.state, "request_id", None),
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Normalize explicit HTTP rejections into the maintained problem contract."""

    detail = exc.detail
    if isinstance(detail, dict):
        problem = dict(detail)
        problem.setdefault("code", f"HTTP_{exc.status_code}")
        problem.setdefault(
            "message", str(problem.get("detail", "Request was rejected"))
        )
    else:
        problem = {
            "code": f"HTTP_{exc.status_code}",
            "message": str(detail),
        }
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=error_response(
            problem,
            request_id=getattr(request.state, "request_id", None),
        ),
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
                status_code=401,
                content=error_response(
                    {
                        "code": "AUTHENTICATION_REQUIRED",
                        "message": "Not authenticated",
                    },
                    request_id=getattr(request.state, "request_id", None),
                ),
            )

        token = auth_header.removeprefix("Bearer ")
        try:
            from fastapi_app.auth import decode_token

            decode_token(token)
        except (jwt.PyJWTError, KeyError, AttributeError):
            return StarletteJSONResponse(
                status_code=401,
                content=error_response(
                    {
                        "code": "AUTHENTICATION_TOKEN_INVALID",
                        "message": "Invalid or expired token",
                    },
                    request_id=getattr(request.state, "request_id", None),
                ),
            )

        return await call_next(request)


app.add_middleware(AuthMiddleware)

# =============================================================================
# Rate Limit Middleware — applies to all non-health endpoints (EA-17)
# =============================================================================


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global rate limiter — applies to all non-health endpoints."""

    SKIP_PREFIXES = ("/health", "/docs", "/openapi.json", "/redoc", "/ws/")

    def __init__(self, app, requests_per_minute: int = 120, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.limiter = RateLimiter(
            requests_per_window=requests_per_minute, window_seconds=60
        )

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        path = request.url.path
        if path.startswith(self.SKIP_PREFIXES):
            return await call_next(request)

        allowed, headers = self.limiter.is_allowed(request)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content=error_response(
                    {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                    },
                    request_id=getattr(request.state, "request_id", None),
                ),
                headers=headers,
            )

        response = await call_next(request)
        response.headers.update(headers)
        return response


_settings = get_settings()
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=_settings.rate_limit_per_minute,
    enabled=_settings.rate_limit_enabled,
)

# =============================================================================
# CORS Middleware Configuration
# =============================================================================

# Origins are configurable via CORS_ORIGINS env var; defaults defined in config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins,
    allow_credentials=_settings.cors_allow_credentials,
    allow_methods=_settings.cors_allow_methods,
    allow_headers=_settings.cors_allow_headers,
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
        InputContractError,
        StructuralLibError,
        ValidationError,
    )

    @app.exception_handler(InputContractError)
    async def input_contract_error_handler(
        request: Request, exc: InputContractError
    ) -> JSONResponse:
        """Preserve canonical issue codes and paths at transport boundaries."""

        return JSONResponse(
            status_code=422,
            content=error_response(
                exc.to_problem(),
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle input validation errors from structural_lib."""
        return JSONResponse(
            status_code=422,
            content=error_response(
                {
                    "code": "VALIDATION_ERROR",
                    "message": exc.message,
                    "details": {
                        "suggestion": exc.suggestion,
                        "clause_ref": exc.clause_ref,
                        "error_details": exc.details,
                    },
                },
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(DesignConstraintError)
    async def design_constraint_handler(request: Request, exc: DesignConstraintError):
        """Handle infeasible design errors from structural_lib."""
        return JSONResponse(
            status_code=422,
            content=error_response(
                {
                    "code": "DESIGN_CONSTRAINT_ERROR",
                    "message": exc.message,
                    "details": {
                        "suggestion": exc.suggestion,
                        "clause_ref": exc.clause_ref,
                        "error_details": exc.details,
                    },
                },
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(ComplianceError)
    async def compliance_error_handler(request: Request, exc: ComplianceError):
        """Handle IS 456 compliance violations from structural_lib."""
        return JSONResponse(
            status_code=422,
            content=error_response(
                {
                    "code": "COMPLIANCE_ERROR",
                    "message": exc.message,
                    "details": {
                        "suggestion": exc.suggestion,
                        "clause_ref": exc.clause_ref,
                        "error_details": exc.details,
                    },
                },
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(ConfigurationError)
    async def config_error_handler(request: Request, exc: ConfigurationError):
        """Handle library misconfiguration errors."""
        return JSONResponse(
            status_code=500,
            content=error_response(
                {
                    "code": "CONFIGURATION_ERROR",
                    "message": exc.message,
                    "details": {
                        "suggestion": exc.suggestion,
                        "error_details": exc.details,
                    },
                },
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(CalculationError)
    async def calculation_error_handler(request: Request, exc: CalculationError):
        """Handle numerical/calculation errors from structural_lib."""
        return JSONResponse(
            status_code=500,
            content=error_response(
                {
                    "code": "CALCULATION_ERROR",
                    "message": exc.message,
                    "details": {
                        "suggestion": exc.suggestion,
                        "error_details": exc.details,
                    },
                },
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(StructuralLibError)
    async def structural_lib_error_handler(request: Request, exc: StructuralLibError):
        """Catch-all for any StructuralLibError not handled above."""
        return JSONResponse(
            status_code=500,
            content=error_response(
                {
                    "code": "STRUCTURAL_LIB_ERROR",
                    "message": exc.message,
                    "details": {
                        "suggestion": exc.suggestion,
                        "clause_ref": exc.clause_ref,
                        "error_details": exc.details,
                    },
                },
                request_id=getattr(request.state, "request_id", None),
            ),
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
        content=error_response(
            {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
            },
            request_id=getattr(request.state, "request_id", None),
        ),
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
app.include_router(design_v2.router)
app.include_router(
    capabilities.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    catalog.router,
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
    building_gravity.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    excel_workbench.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    etabs_bridge.router,
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
    library_core.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    footing.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    staircase.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    wall.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    deep_beam.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    flat_slab.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    combined_footing.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    strap_footing.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    export.router,
    prefix=API_V1_PREFIX,
)
app.include_router(
    workflows.router,
    prefix=API_V1_PREFIX,
)

# WebSocket router (no prefix - ws://host/ws/...)
app.include_router(websocket.router)

# Streaming router (SSE for batch processing)
app.include_router(streaming.router)

# =============================================================================
# Root Endpoint
# =============================================================================


@app.get("/", tags=["health"], response_model=APIInfoResponse)
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
