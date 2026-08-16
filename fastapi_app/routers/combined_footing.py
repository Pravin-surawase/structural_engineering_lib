"""FastAPI transport for the bounded symmetric combined-footing service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.combined_footing_api as combined_footing_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.combined_footing import (
    SymmetricCombinedFootingRequest,
    SymmetricCombinedFootingResponse,
)
from fastapi_app.models.response import APIResponse, error_response, success_response

router = APIRouter(prefix="/design/combined-footing", tags=["combined-footing"])


def _service_input(
    request: SymmetricCombinedFootingRequest,
) -> combined_footing_api.SymmetricCombinedFootingDesignInput:
    return combined_footing_api.build_symmetric_combined_footing_design_input(
        request.model_dump()
    )


@router.post(
    "/symmetric",
    response_model=APIResponse[SymmetricCombinedFootingResponse],
    summary="Design a bounded symmetric two-column combined footing",
)
async def design_symmetric_combined_footing(
    request: SymmetricCombinedFootingRequest,
):
    """Validate transport input and delegate every calculation to the service."""
    try:
        result = combined_footing_api.design_symmetric_combined_footing_is456(
            _service_input(request)
        )
        return success_response(jsonable_encoder(asdict(result)))
    except combined_footing_api.CombinedFootingContractError as exc:
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
                            "msg": sanitize_error_string(str(exc), "combined footing"),
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
                    "message": sanitize_error(exc, "combined footing"),
                    "details": [],
                }
            ),
        )
