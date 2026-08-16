"""FastAPI transport for the bounded property-line strap-footing service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.strap_footing_api as strap_footing_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.response import APIResponse, error_response, success_response
from fastapi_app.models.strap_footing import (
    PropertyLineStrapFootingRequest,
    PropertyLineStrapFootingResponse,
)

router = APIRouter(prefix="/design/strap-footing", tags=["strap-footing"])


def _service_input(
    request: PropertyLineStrapFootingRequest,
) -> strap_footing_api.PropertyLineStrapFootingDesignInput:
    return strap_footing_api.build_property_line_strap_footing_design_input(
        request.model_dump()
    )


@router.post(
    "/property-line",
    response_model=APIResponse[PropertyLineStrapFootingResponse],
    summary="Design a bounded property-line strap footing",
)
async def design_property_line_strap_footing(
    request: PropertyLineStrapFootingRequest,
) -> dict[str, object] | JSONResponse:
    """Validate transport input and delegate every calculation to the service."""
    try:
        result = strap_footing_api.design_property_line_strap_footing_is456(
            _service_input(request)
        )
        return success_response(jsonable_encoder(asdict(result)))
    except strap_footing_api.StrapFootingContractError as exc:
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
                            "msg": sanitize_error_string(str(exc), "strap footing"),
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
                    "message": sanitize_error(exc, "strap footing"),
                    "details": [],
                }
            ),
        )
