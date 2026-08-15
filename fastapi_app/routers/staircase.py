"""FastAPI transport for the bounded straight-flight staircase service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.staircase_api as staircase_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.response import APIResponse, error_response, success_response
from fastapi_app.models.staircase import (
    StraightFlightStaircaseRequest,
    StraightFlightStaircaseResponse,
)

router = APIRouter(prefix="/design/staircase", tags=["staircase"])


@router.post(
    "/straight-flight",
    response_model=APIResponse[StraightFlightStaircaseResponse],
    summary="Design a bounded straight-flight waist-slab staircase",
)
async def design_straight_flight_staircase(
    request: StraightFlightStaircaseRequest,
):
    """Validate transport inputs and delegate all calculation to the service."""
    try:
        result = staircase_api.design_straight_flight_staircase_is456(
            staircase_api.StraightFlightStaircaseInput(**request.model_dump())
        )
        return success_response(jsonable_encoder(asdict(result)))
    except staircase_api.StaircaseContractError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": [
                        {
                            "type": "value_error",
                            "loc": ["body"],
                            "msg": sanitize_error_string(
                                str(exc), "straight-flight staircase"
                            ),
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
                    "message": sanitize_error(exc, "straight-flight staircase"),
                    "details": [],
                }
            ),
        )
