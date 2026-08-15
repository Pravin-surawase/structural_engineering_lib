"""FastAPI transport for the bounded simply supported deep-beam service."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.deep_beam_api as deep_beam_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.deep_beam import (
    SimplySupportedDeepBeamRequest,
    SimplySupportedDeepBeamResponse,
)
from fastapi_app.models.response import APIResponse, error_response, success_response

router = APIRouter(prefix="/design/deep-beam", tags=["deep-beam"])


def _side_face_payload(result: Any) -> dict[str, object]:
    return {
        "minimum_ratio": result.minimum_ratio,
        "required_area_mm2_per_m": result.required_area_mm2_per_m,
        "provided_area_mm2_per_m": result.provided_area_mm2_per_m,
        "provided_ratio": result.provided_ratio,
        "required_face_grid_count": result.required_face_grid_count,
        "provided_face_grid_count": result.provided_face_grid_count,
        "maximum_spacing_mm": result.maximum_spacing_mm,
        "provided_spacing_mm": result.provided_spacing_mm,
        "area_status": result.area_status,
        "spacing_status": result.spacing_status,
        "status": result.status,
    }


def _result_payload(
    result: deep_beam_api.SimplySupportedDeepBeamDesignResult,
) -> dict[str, object]:
    reinforcement = result.reinforcement
    return {
        "case_id": result.case_id,
        "status": result.status,
        "reinforcement": {
            "geometry": {
                "effective_span_mm": reinforcement.geometry.effective_span_mm,
                "effective_span_to_depth_ratio": (
                    reinforcement.geometry.effective_span_to_depth_ratio
                ),
                "lever_arm_case": reinforcement.geometry.lever_arm_case,
                "lever_arm_mm": reinforcement.geometry.lever_arm_mm,
                "positive_reinforcement_zone_depth_mm": (
                    reinforcement.geometry.positive_reinforcement_zone_depth_mm
                ),
                "source_refs": reinforcement.geometry.source_refs,
            },
            "positive_tie": reinforcement.positive_tie,
            "placement": reinforcement.placement,
            "continuity_status": reinforcement.continuity_status,
            "anchorage": {
                **vars(reinforcement.anchorage),
                "status": reinforcement.anchorage.status,
            },
            "vertical_side_face": _side_face_payload(reinforcement.vertical_side_face),
            "horizontal_side_face": _side_face_payload(
                reinforcement.horizontal_side_face
            ),
            "external_bearing_nodal_prerequisite_satisfied": (
                reinforcement.external_bearing_nodal_prerequisite_satisfied
            ),
            "status": reinforcement.status,
            "shear_deemed_satisfied_within_clause_29_scope": (
                reinforcement.shear_deemed_satisfied_within_clause_29_scope
            ),
            "source_refs": reinforcement.source_refs,
        },
        "supported_case": result.supported_case,
        "held_cases": result.held_cases,
        "provenance": result.provenance,
        "qualified_review_required": result.qualified_review_required,
        "complete_engineering_design_approved": (
            result.complete_engineering_design_approved
        ),
        "shear_deemed_satisfied_within_clause_29_scope": (
            result.shear_deemed_satisfied_within_clause_29_scope
        ),
    }


@router.post(
    "/simply-supported",
    response_model=APIResponse[SimplySupportedDeepBeamResponse],
    summary="Check a bounded Clause 29 simply supported deep beam",
)
async def design_simply_supported_deep_beam(
    request: SimplySupportedDeepBeamRequest,
):
    """Validate transport input and delegate all calculation to the service."""
    try:
        result = deep_beam_api.design_simply_supported_deep_beam_is456(
            deep_beam_api.SimplySupportedDeepBeamDesignInput(**request.model_dump())
        )
        return success_response(jsonable_encoder(_result_payload(result)))
    except deep_beam_api.DeepBeamContractError as exc:
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
                            "msg": sanitize_error_string(str(exc), "deep beam"),
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
                    "message": sanitize_error(exc, "deep beam"),
                    "details": [],
                }
            ),
        )
