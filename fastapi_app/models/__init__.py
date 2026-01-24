"""
Pydantic Models Package.

Exports all request/response models for API endpoints.
"""

from fastapi_app.models.beam import (
    BeamDesignRequest,
    BeamDesignResponse,
    BeamCheckRequest,
    BeamCheckResponse,
    BeamDetailingRequest,
    BeamDetailingResponse,
)
from fastapi_app.models.optimization import (
    CostOptimizationRequest,
    CostOptimizationResponse,
)
from fastapi_app.models.analysis import (
    SmartAnalysisRequest,
    SmartAnalysisResponse,
)
from fastapi_app.models.geometry import (
    Geometry3DRequest,
    Geometry3DResponse,
)
from fastapi_app.models.common import (
    MaterialProperties,
    BeamSection,
    LoadCase,
    DesignBasis,
    APIResponse,
    ErrorResponse,
)

__all__ = [
    # Beam models
    "BeamDesignRequest",
    "BeamDesignResponse",
    "BeamCheckRequest",
    "BeamCheckResponse",
    "BeamDetailingRequest",
    "BeamDetailingResponse",
    # Optimization models
    "CostOptimizationRequest",
    "CostOptimizationResponse",
    # Analysis models
    "SmartAnalysisRequest",
    "SmartAnalysisResponse",
    # Geometry models
    "Geometry3DRequest",
    "Geometry3DResponse",
    # Common models
    "MaterialProperties",
    "BeamSection",
    "LoadCase",
    "DesignBasis",
    "APIResponse",
    "ErrorResponse",
]
