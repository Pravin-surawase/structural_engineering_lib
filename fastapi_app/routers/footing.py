"""FastAPI transport for the bounded concentric isolated-footing service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import structural_lib.services.footing_api as footing_api
from fastapi_app.error_utils import sanitize_error, sanitize_error_string
from fastapi_app.models.footing import (
    ConcentricIsolatedFootingRequest,
    ConcentricIsolatedFootingResponse,
)
from fastapi_app.models.response import APIResponse, error_response, success_response

router = APIRouter(prefix="/design/footing", tags=["footing"])


@router.post(
    "/isolated/concentric",
    response_model=APIResponse[ConcentricIsolatedFootingResponse],
    summary="Design a bounded concentric isolated footing",
)
async def design_concentric_isolated_footing(
    request: ConcentricIsolatedFootingRequest,
):
    """Validate transport inputs and delegate all calculation to the service."""
    try:
        values = request.model_dump()
        values["footing_type"] = footing_api.FootingType[request.footing_type.value]
        result = footing_api.design_concentric_isolated_footing_is456(
            footing_api.ConcentricIsolatedFootingInput(**values)
        )
        return success_response(jsonable_encoder(asdict(result)))
    except footing_api.ValidationError as exc:
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
                                exc.message, "concentric isolated footing"
                            ),
                            "ctx": jsonable_encoder(exc.details),
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
                    "message": sanitize_error(exc, "concentric isolated footing"),
                    "details": [],
                }
            ),
        )
