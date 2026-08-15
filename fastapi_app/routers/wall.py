"""FastAPI transport for the bounded braced-wall service."""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.wall_api as wall_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.response import APIResponse, error_response, success_response
from fastapi_app.models.wall import BracedWallRequest, BracedWallResponse

router = APIRouter(prefix="/design/wall", tags=["wall"])


def _direction_payload(
    result: wall_api.WallDirectionalReinforcementResult,
) -> dict[str, object]:
    return {
        "minimum_ratio": result.minimum_ratio,
        "required_area_mm2_per_m": result.required_area_mm2_per_m,
        "provided_area_mm2_per_m": result.provided_area_mm2_per_m,
        "provided_ratio": result.provided_ratio,
        "maximum_spacing_mm": result.maximum_spacing_mm,
        "provided_spacing_mm": result.provided_spacing_mm,
        "area_status": result.area_status,
        "spacing_status": result.spacing_status,
        "status": result.status,
    }


def _result_payload(result: wall_api.BracedWallDesignResult) -> dict[str, object]:
    return {
        "case_id": result.case_id,
        "status": result.status,
        "axial": {
            "effective_height_mm": result.axial.geometry.effective_height_mm,
            "effective_height_to_thickness_ratio": (
                result.axial.geometry.effective_height_to_thickness_ratio
            ),
            "minimum_eccentricity_mm": result.axial.minimum_eccentricity_mm,
            "design_eccentricity_mm": result.axial.design_eccentricity_mm,
            "additional_eccentricity_mm": result.axial.additional_eccentricity_mm,
            "effective_compression_thickness_mm": (
                result.axial.effective_compression_thickness_mm
            ),
            "axial_capacity_n_per_mm": result.axial.axial_capacity_n_per_mm,
            "axial_capacity_kn_per_m": result.axial.axial_capacity_kn_per_m,
            "total_axial_capacity_kn": result.axial.total_axial_capacity_kn,
            "axial_demand_n_per_mm": result.axial.axial_demand_n_per_mm,
            "axial_demand_kn_per_m": result.axial.axial_demand_kn_per_m,
            "utilization_ratio": result.axial.utilization_ratio,
            "status": result.axial.status,
            "source_refs": result.axial.source_refs,
            "load_generation_status": result.axial.load_generation_status,
        },
        "reinforcement": {
            "vertical": _direction_payload(result.reinforcement.vertical),
            "horizontal": _direction_payload(result.reinforcement.horizontal),
            "transverse_enclosure_required": (
                result.reinforcement.transverse_enclosure_required
            ),
            "status": result.reinforcement.status,
            "source_refs": result.reinforcement.source_refs,
        },
        "supported_case": result.supported_case,
        "held_cases": result.held_cases,
        "provenance": result.provenance,
        "qualified_review_required": result.qualified_review_required,
        "complete_engineering_design_approved": (
            result.complete_engineering_design_approved
        ),
    }


@router.post(
    "/braced-axial",
    response_model=APIResponse[BracedWallResponse],
    summary="Check a bounded Clause 32 braced wall",
)
async def design_braced_wall(request: BracedWallRequest):
    """Validate transport inputs and delegate all calculation to the service."""
    try:
        result = wall_api.design_braced_wall_is456(
            wall_api.BracedWallDesignInput(**request.model_dump())
        )
        return success_response(jsonable_encoder(_result_payload(result)))
    except wall_api.WallContractError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=error_response(
                {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": [
                        {
                            "type": "value_error",
                            "loc": ["body"],
                            "msg": sanitize_error_string(str(exc), "braced wall"),
                        }
                    ],
                }
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                {
                    "code": "INTERNAL_ERROR",
                    "message": sanitize_error(exc, "braced wall"),
                    "details": [],
                }
            ),
        )
