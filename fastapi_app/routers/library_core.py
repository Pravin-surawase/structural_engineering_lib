"""Thin FastAPI consumers for the supported footing and slab library routes."""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.library_core import (
    BuiltinContinuousOneWaySlabDesignRequest,
    BuiltinTwoWaySlabPanelDesignRequest,
    CompleteOneWaySlabDesignRequest,
    CompleteOneWaySlabDesignResponse,
    ContinuousOneWaySlabDesignRequest,
    ContinuousOneWaySlabDesignResponse,
    FootingLoadTransferRequest,
    FootingLoadTransferResponse,
    OneWaySlabDesignRequest,
    OneWaySlabDesignResponse,
    TwoWaySlabPanelDesignRequest,
    TwoWaySlabPanelDesignResponse,
)
from fastapi_app.models.response import APIResponse, error_response, success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/design", tags=["footing", "slab"])


@router.post(
    "/footing/load-transfer",
    response_model=APIResponse[FootingLoadTransferResponse],
    summary="Check isolated-footing load transfer",
)
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


@router.post(
    "/slab/one-way",
    response_model=APIResponse[OneWaySlabDesignResponse],
    summary="Design a simply supported one-way slab strip",
)
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


@router.post(
    "/slab/one-way/complete",
    response_model=APIResponse[CompleteOneWaySlabDesignResponse],
    summary="Design a complete bounded simply supported one-way slab strip",
)
async def design_complete_one_way_slab(request: CompleteOneWaySlabDesignRequest):
    """Add ordinary shear and strict reviewed-limit serviceability."""
    try:
        from structural_lib.services.api import design_complete_one_way_slab_is456

        result = design_complete_one_way_slab_is456(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "complete one-way slab design")),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Complete one-way slab service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "complete one-way slab design")),
        )


@router.post(
    "/slab/one-way/continuous",
    response_model=APIResponse[ContinuousOneWaySlabDesignResponse],
    summary="Design a coefficient-method continuous one-way slab strip",
)
async def design_continuous_one_way_slab(
    request: ContinuousOneWaySlabDesignRequest,
):
    """Validate coefficient provenance/domain and call the public service."""
    try:
        from structural_lib.services.api import design_continuous_one_way_slab_is456

        result = design_continuous_one_way_slab_is456(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                sanitize_error(exc, "continuous one-way slab design")
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Continuous one-way slab service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                sanitize_error(exc, "continuous one-way slab design")
            ),
        )


@router.post(
    "/slab/one-way/continuous/builtin",
    response_model=APIResponse[ContinuousOneWaySlabDesignResponse],
    summary="Design a continuous one-way slab using built-in IS 456 coefficients",
)
async def design_continuous_one_way_slab_builtin(
    request: BuiltinContinuousOneWaySlabDesignRequest,
):
    """Resolve Tables 12/13 and call the bounded public workflow."""
    try:
        from structural_lib.services.api import (
            design_continuous_one_way_slab_builtin_is456,
        )

        result = design_continuous_one_way_slab_builtin_is456(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                sanitize_error(exc, "built-in continuous one-way slab design")
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Built-in continuous one-way slab service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                sanitize_error(exc, "built-in continuous one-way slab design")
            ),
        )


@router.post(
    "/slab/two-way/panel",
    response_model=APIResponse[TwoWaySlabPanelDesignResponse],
    summary="Design a common oriented two-way solid slab panel",
)
async def design_two_way_slab_panel(request: TwoWaySlabPanelDesignRequest):
    """Run topology, external coefficients, strips, torsion, shear and bars."""
    try:
        from structural_lib.services.api import design_two_way_slab_panel_is456

        result = design_two_way_slab_panel_is456(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "two-way slab panel design")),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Two-way slab panel service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "two-way slab panel design")),
        )


@router.post(
    "/slab/two-way/panel/builtin",
    response_model=APIResponse[TwoWaySlabPanelDesignResponse],
    summary="Design a two-way slab panel using built-in IS 456 coefficients",
)
async def design_two_way_slab_panel_builtin(
    request: BuiltinTwoWaySlabPanelDesignRequest,
):
    """Resolve Table 26/27 with bounded interpolation and run the panel workflow."""
    try:
        from structural_lib.services.api import (
            design_two_way_slab_panel_builtin_is456,
        )

        result = design_two_way_slab_panel_builtin_is456(**request.model_dump())
        return success_response(jsonable_encoder(asdict(result)))
    except (ValueError, TypeError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                sanitize_error(exc, "built-in two-way slab panel design")
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Built-in two-way slab panel service failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                sanitize_error(exc, "built-in two-way slab panel design")
            ),
        )
