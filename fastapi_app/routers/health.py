"""
Health Check Router.

Provides system health and readiness endpoints for:
- Kubernetes liveness/readiness probes
- Load balancer health checks
- Monitoring and observability
"""

import platform
import sys
import time
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from fastapi_app import __version__

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


# =============================================================================
# Response Models
# =============================================================================


class HealthStatus(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy", "degraded"] = Field(
        description="Overall system health status"
    )
    version: str = Field(description="API version")
    timestamp: str = Field(description="ISO 8601 timestamp")
    uptime_seconds: float = Field(description="Time since startup in seconds", ge=0)


class ReadinessStatus(BaseModel):
    """Readiness check response model."""

    ready: bool = Field(description="Whether the service is ready to accept requests")
    checks: dict[str, bool] = Field(description="Individual component readiness")


class SystemInfo(BaseModel):
    """System information response model."""

    python_version: str = Field(description="Python interpreter version")
    platform: str = Field(description="Operating system platform")
    api_version: str = Field(description="API version")
    structural_lib_available: bool = Field(
        description="Whether structural_lib is importable"
    )


# =============================================================================
# Module State
# =============================================================================

# Track startup time for uptime calculation
_startup_time: datetime | None = None


def _get_startup_time() -> datetime:
    """Get or initialize startup time."""
    global _startup_time
    if _startup_time is None:
        _startup_time = datetime.now(timezone.utc)
    return _startup_time


def _check_structural_lib() -> bool:
    """Check if structural_lib is available and importable."""
    try:
        from structural_lib import api  # noqa: F401

        return True
    except ImportError:
        return False


# =============================================================================
# Smoke Test (cached computation check)
# =============================================================================

_smoke_cache: dict = {"timestamp": 0.0, "passed": False}
_SMOKE_TTL = 30.0  # seconds


def _run_smoke_test() -> bool:
    """Run a minimal beam design to verify compute engine works."""
    now = time.monotonic()
    if now - _smoke_cache["timestamp"] < _SMOKE_TTL:
        return _smoke_cache["passed"]
    try:
        from structural_lib.services.api import design_beam_is456

        result = design_beam_is456(
            units="IS456",
            b_mm=230.0,
            D_mm=450.0,
            d_mm=400.0,
            fck_nmm2=25.0,
            fy_nmm2=415.0,
            mu_knm=50.0,
            vu_kn=30.0,
        )
        passed = result is not None and hasattr(result, "flexure")
    except Exception:
        passed = False
    _smoke_cache["timestamp"] = now
    _smoke_cache["passed"] = passed
    return passed


# =============================================================================
# Health Endpoints
# =============================================================================


@router.get(
    "",
    response_model=HealthStatus,
    summary="Health Check",
    description="Returns the current health status of the API.",
)
async def health_check() -> HealthStatus:
    """
    Perform a basic health check.

    This endpoint is designed for:
    - Kubernetes liveness probes
    - Load balancer health checks
    - Basic uptime monitoring

    Returns HTTP 200 if the service is running.
    """
    startup = _get_startup_time()
    now = datetime.now(timezone.utc)
    uptime = (now - startup).total_seconds()

    return HealthStatus(
        status="healthy",
        version=__version__,
        timestamp=now.isoformat(),
        uptime_seconds=uptime,
    )


@router.get(
    "/ready",
    response_model=ReadinessStatus,
    summary="Readiness Check",
    description="Returns whether the service is ready to accept requests.",
)
async def readiness_check() -> ReadinessStatus:
    """
    Check if the service is ready to handle requests.

    Verifies that all required dependencies are available:
    - structural_lib module is importable
    - Any future dependencies (database, cache, etc.)

    This endpoint is designed for:
    - Kubernetes readiness probes
    - Deployment zero-downtime verification
    """
    lib_available = _check_structural_lib()
    compute_ok = _run_smoke_test()

    checks = {
        "structural_lib": lib_available,
        "compute_engine": compute_ok,
        # Future: Add database, cache, external service checks
    }

    all_ready = all(checks.values())

    return ReadinessStatus(
        ready=all_ready,
        checks=checks,
    )


@router.get(
    "/info",
    response_model=SystemInfo,
    summary="System Information",
    description="Returns detailed system and version information.",
)
async def system_info() -> SystemInfo:
    """
    Get detailed system information.

    Returns version information for debugging and compatibility checks.
    """
    return SystemInfo(
        python_version=sys.version,
        platform=platform.platform(),
        api_version=__version__,
        structural_lib_available=_check_structural_lib(),
    )
