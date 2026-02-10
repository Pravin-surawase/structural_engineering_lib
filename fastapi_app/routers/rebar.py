# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Rebar Validation and Application Router.

Endpoints for rebar configuration validation and preview.
Uses structural_lib.rebar for IS 456 compliant checks.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/rebar",
    tags=["rebar"],
)


# =============================================================================
# Request/Response Models
# =============================================================================


class BeamParams(BaseModel):
    """Beam parameters for rebar validation."""

    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Beam depth D (mm)")
    cover: float = Field(default=40.0, ge=20.0, le=75.0, description="Clear cover (mm)")
    span: float = Field(default=5000.0, gt=0, description="Beam span (mm)")


class RebarConfig(BaseModel):
    """Rebar configuration to validate or apply."""

    bar_count: int = Field(ge=2, le=12, description="Number of bars")
    bar_dia: float = Field(ge=8.0, le=40.0, description="Bar diameter (mm)")
    stirrup_dia: float = Field(
        default=8.0, ge=6.0, le=16.0, description="Stirrup diameter (mm)"
    )
    layers: int = Field(default=1, ge=1, le=3, description="Number of bar layers")
    is_top: bool = Field(default=False, description="Whether bars are in top zone")
    stirrup_spacing_start: float = Field(
        default=150.0, gt=0, le=300.0, description="Stirrup spacing at start (mm)"
    )
    stirrup_spacing_mid: float = Field(
        default=200.0, gt=0, le=300.0, description="Stirrup spacing at mid (mm)"
    )
    stirrup_spacing_end: float = Field(
        default=150.0, gt=0, le=300.0, description="Stirrup spacing at end (mm)"
    )
    agg_size: float = Field(
        default=20.0, ge=10.0, le=40.0, description="Aggregate size (mm)"
    )


class RebarValidateRequest(BaseModel):
    """Request model for rebar validation."""

    beam: BeamParams = Field(description="Beam parameters")
    config: RebarConfig = Field(description="Rebar configuration to validate")


class ValidationResult(BaseModel):
    """Validation result details."""

    ok: bool = Field(description="Whether configuration is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    details: dict = Field(default_factory=dict, description="Computed details")


class RebarValidateResponse(BaseModel):
    """Response model for rebar validation."""

    success: bool = Field(description="Whether validation completed")
    message: str = Field(description="Summary message")
    validation: ValidationResult = Field(description="Validation results")


class RebarApplyRequest(BaseModel):
    """Request model for rebar apply."""

    beam: BeamParams = Field(description="Beam parameters")
    config: RebarConfig = Field(description="Rebar configuration to apply")


class RebarApplyResponse(BaseModel):
    """Response model for rebar apply."""

    success: bool = Field(description="Whether apply succeeded")
    message: str = Field(description="Summary message")
    ast_provided_mm2: float | None = Field(
        default=None, description="Steel area provided (mm²)"
    )
    validation: ValidationResult = Field(description="Validation results")
    geometry: dict | None = Field(
        default=None, description="Rebar geometry for visualization"
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/validate",
    response_model=RebarValidateResponse,
    summary="Validate Rebar Configuration",
    description="""
Validate a rebar configuration against IS 456 requirements.

Returns validation results with errors, warnings, and computed spacing.
Use this before applying configuration to check for issues.
""",
)
async def validate_rebar(request: RebarValidateRequest) -> RebarValidateResponse:
    """
    Validate rebar configuration against geometry and code requirements.

    Checks:
    - Bar spacing vs IS 456 minimum
    - Cover adequacy
    - Fit within section

    Returns validation report suitable for UI display.
    """
    try:
        from structural_lib.services.rebar import validate_rebar_config

        # Convert Pydantic models to dicts for library
        beam_dict = {
            "b_mm": request.beam.width,
            "D_mm": request.beam.depth,
            "cover_mm": request.beam.cover,
            "span_mm": request.beam.span,
        }
        config_dict = {
            "bar_count": request.config.bar_count,
            "bar_dia_mm": request.config.bar_dia,
            "stirrup_dia_mm": request.config.stirrup_dia,
            "layers": request.config.layers,
            "is_top": request.config.is_top,
            "agg_size_mm": request.config.agg_size,
        }

        report = validate_rebar_config(beam_dict, config_dict)

        return RebarValidateResponse(
            success=True,
            message="Valid configuration" if report.ok else "Configuration has issues",
            validation=ValidationResult(
                ok=report.ok,
                errors=report.errors,
                warnings=report.warnings,
                details=report.details,
            ),
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"structural_lib not available: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {e}",
        )


@router.post(
    "/apply",
    response_model=RebarApplyResponse,
    summary="Apply Rebar Configuration",
    description="""
Apply a rebar configuration and get geometry for visualization.

Validates first, then computes:
- Rebar positions and paths
- Stirrup positions and loops
- Steel area provided

Returns geometry suitable for React Three Fiber rendering.
""",
)
async def apply_rebar(request: RebarApplyRequest) -> RebarApplyResponse:
    """
    Apply rebar configuration and generate 3D geometry.

    Computes:
    - Bar positions based on cover, spacing, layers
    - Stirrup positions based on zonal spacing
    - Total steel area provided

    Returns geometry for visualization preview.
    """
    try:
        from structural_lib.services.rebar import apply_rebar_config

        # Convert Pydantic models to dicts for library
        beam_dict = {
            "b_mm": request.beam.width,
            "D_mm": request.beam.depth,
            "cover_mm": request.beam.cover,
            "span_mm": request.beam.span,
        }
        config_dict = {
            "bar_count": request.config.bar_count,
            "bar_dia_mm": request.config.bar_dia,
            "stirrup_dia_mm": request.config.stirrup_dia,
            "layers": request.config.layers,
            "is_top": request.config.is_top,
            "stirrup_spacing_start": request.config.stirrup_spacing_start,
            "stirrup_spacing_mid": request.config.stirrup_spacing_mid,
            "stirrup_spacing_end": request.config.stirrup_spacing_end,
        }

        result = apply_rebar_config(beam_dict, config_dict)

        validation_data = result.get("validation", {})

        return RebarApplyResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            ast_provided_mm2=result.get("ast_provided_mm2"),
            validation=ValidationResult(
                ok=validation_data.get("ok", False),
                errors=validation_data.get("errors", []),
                warnings=validation_data.get("warnings", []),
                details=validation_data.get("details", {}),
            ),
            geometry=result.get("geometry"),
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"structural_lib not available: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Apply failed: {e}",
        )
