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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_app import __version__
from fastapi_app.routers import (
    analysis,
    design,
    detailing,
    geometry,
    health,
    imports,
    insights,
    optimization,
    rebar,
    streaming,
    websocket,
)

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
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,  # Cache preflight requests for 10 minutes
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
    # Future: Initialize database connections, cache, etc.
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.

    Cleans up resources and connections.
    """
    # Future: Close database connections, flush caches, etc.
    pass
