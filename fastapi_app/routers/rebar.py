"""
Rebar Router.

Endpoints for rebar validation and application helpers.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.rebar import (
    RebarApplyRequest,
    RebarApplyResponse,
    RebarValidationRequest,
    RebarValidationResponse,
)

router = APIRouter(
    prefix="/rebar",
    tags=["rebar"],
)


@router.post(
    "/validate",
    response_model=RebarValidationResponse,
    summary="Validate rebar configuration",
    description="Validate bar count/diameter/spacing against geometry constraints.",
)
async def validate_rebar(
    request: RebarValidationRequest,
) -> RebarValidationResponse:
    try:
        from structural_lib.rebar import validate_rebar_config

        beam = {
            "b_mm": request.beam.width_mm,
            "D_mm": request.beam.depth_mm,
            "cover_mm": request.beam.cover_mm,
            "span_mm": request.beam.span_mm,
        }
        config = {
            "bar_count": request.config.bar_count,
            "bar_dia_mm": request.config.bar_dia_mm,
            "stirrup_dia_mm": request.config.stirrup_dia_mm,
            "layers": request.config.layers,
            "is_top": request.config.is_top,
            "agg_size_mm": request.config.agg_size_mm,
        }

        report = validate_rebar_config(beam, config)
        return RebarValidationResponse(
            success=report.ok,
            message="Rebar configuration is valid" if report.ok else "Invalid rebar configuration",
            validation=report.to_dict(),
            warnings=report.warnings,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rebar validation failed: {e}",
        )


@router.post(
    "/apply",
    response_model=RebarApplyResponse,
    summary="Apply rebar configuration",
    description="Apply rebar config and return preview geometry.",
)
async def apply_rebar(
    request: RebarApplyRequest,
) -> RebarApplyResponse:
    try:
        from structural_lib.rebar import apply_rebar_config

        beam = {
            "b_mm": request.beam.width_mm,
            "D_mm": request.beam.depth_mm,
            "cover_mm": request.beam.cover_mm,
            "span_mm": request.beam.span_mm,
        }
        config = {
            "bar_count": request.config.bar_count,
            "bar_dia_mm": request.config.bar_dia_mm,
            "stirrup_dia_mm": request.config.stirrup_dia_mm,
            "layers": request.config.layers,
            "is_top": request.config.is_top,
            "stirrup_spacing_start": request.config.stirrup_spacing_start,
            "stirrup_spacing_mid": request.config.stirrup_spacing_mid,
            "stirrup_spacing_end": request.config.stirrup_spacing_end,
            "agg_size_mm": request.config.agg_size_mm,
        }

        result = apply_rebar_config(beam, config)
        return RebarApplyResponse(
            success=bool(result.get("success")),
            message=result.get("message", ""),
            validation=result.get("validation"),
            geometry=result.get("geometry"),
            warnings=result.get("warnings", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rebar apply failed: {e}",
        )
