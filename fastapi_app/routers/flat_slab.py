"""FastAPI transport for the bounded regular interior flat-slab service."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.flat_slab_api as flat_slab_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.flat_slab import (
    RegularInteriorFlatSlabRequest,
    RegularInteriorFlatSlabResponse,
)
from fastapi_app.models.response import APIResponse, error_response, success_response

router = APIRouter(prefix="/design/flat-slab", tags=["flat-slab"])


def _service_input(
    request: RegularInteriorFlatSlabRequest,
) -> flat_slab_api.RegularInteriorFlatSlabDesignInput:
    return flat_slab_api.build_regular_interior_flat_slab_design_input(
        request.model_dump()
    )


def _provided_check_payload(result: Any) -> dict[str, object]:
    return {**vars(result), "is_adequate": result.is_adequate}


def _region_payload(result: Any) -> dict[str, object]:
    return {
        **{
            key: value for key, value in vars(result).items() if key != "provided_check"
        },
        "provided_check": _provided_check_payload(result.provided_check),
        "is_adequate": result.is_adequate,
    }


def _direction_payload(result: Any) -> dict[str, object]:
    region_names = {
        "column_strip_negative",
        "column_strip_positive",
        "middle_strip_negative",
        "middle_strip_positive",
    }
    return {
        **{
            key: value for key, value in vars(result).items() if key not in region_names
        },
        **{name: _region_payload(getattr(result, name)) for name in region_names},
        "is_adequate": result.is_adequate,
    }


def _serviceability_payload(result: Any) -> dict[str, object]:
    return {**vars(result), "is_satisfied": result.is_satisfied}


def _reinforcement_payload(result: Any) -> dict[str, object]:
    return {
        "geometry_x": vars(result.moments.geometry.x),
        "geometry_y": vars(result.moments.geometry.y),
        "moments_x": vars(result.moments.x),
        "moments_y": vars(result.moments.y),
        "x": _direction_payload(result.x),
        "y": _direction_payload(result.y),
        "x_serviceability": _serviceability_payload(result.x_serviceability),
        "y_serviceability": _serviceability_payload(result.y_serviceability),
        "direct_deflection_status": result.direct_deflection_status,
        "crack_width_status": result.crack_width_status,
        "source_refs": result.source_refs,
        "limitations": result.limitations,
        "is_reinforcement_and_detailing_adequate": (
            result.is_reinforcement_and_detailing_adequate
        ),
        "is_span_depth_satisfied": result.is_span_depth_satisfied,
    }


def _punching_payload(result: Any) -> dict[str, object]:
    return {
        **{key: value for key, value in vars(result).items() if key != "input"},
        "is_adequate_without_punching_reinforcement": (
            result.is_adequate_without_punching_reinforcement
        ),
    }


def _result_payload(
    result: flat_slab_api.RegularInteriorFlatSlabDesignResult,
) -> dict[str, object]:
    return {
        "case_id": result.case_id,
        "status": result.status,
        "reinforcement": _reinforcement_payload(result.reinforcement),
        "punching": _punching_payload(result.punching),
        "supported_case": result.supported_case,
        "held_cases": result.held_cases,
        "provenance": vars(result.provenance),
        "qualified_review_required": result.qualified_review_required,
        "complete_engineering_design_approved": (
            result.complete_engineering_design_approved
        ),
    }


@router.post(
    "/regular-interior",
    response_model=APIResponse[RegularInteriorFlatSlabResponse],
    summary="Design a bounded regular interior flat-slab panel",
)
async def design_regular_interior_flat_slab(
    request: RegularInteriorFlatSlabRequest,
):
    """Validate transport input and delegate every calculation to the service."""
    try:
        result = flat_slab_api.design_regular_interior_flat_slab_is456(
            _service_input(request)
        )
        return success_response(jsonable_encoder(_result_payload(result)))
    except flat_slab_api.FlatSlabContractError as exc:
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
                            "msg": sanitize_error_string(str(exc), "flat slab"),
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
                    "message": sanitize_error(exc, "flat slab"),
                    "details": [],
                }
            ),
        )
