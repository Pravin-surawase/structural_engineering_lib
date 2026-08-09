"""Thin FastAPI consumers for the supported footing and slab library routes."""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.library_core import (
    FootingLoadTransferRequest,
    OneWaySlabDesignRequest,
)
from fastapi_app.models.response import error_response, success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/design", tags=["footing", "slab"])


@router.post("/footing/load-transfer", summary="Check isolated-footing load transfer")
async def check_footing_load_transfer(request: FootingLoadTransferRequest):
    """Validate a request, call the public library service, and map its result."""
    try:
        from structural_lib.services.api import check_isolated_footing_load_transfer

        result = check_isolated_footing_load_transfer(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "footing load transfer")),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Footing load-transfer service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "footing load transfer")),
        )


@router.post("/slab/one-way", summary="Design a simply supported one-way slab strip")
async def design_one_way_slab(request: OneWaySlabDesignRequest):
    """Validate a request, call the public slab service, and map its result."""
    try:
        from structural_lib.services.api import design_one_way_slab_is456

        result = design_one_way_slab_is456(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "one-way slab design")),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("One-way slab service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "one-way slab design")),
        )
