"""Versioned localhost transport for the bounded live ETABS beam pilot."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.response import APIResponse, error_response, success_response
from structural_lib.services.etabs_live_bridge import (
    ETABSBridgeStatusV1,
    ETABSConnectionError,
    ETABSConnectionV1,
    ETABSDataError,
    ETABSPilotRequestV1,
    ETABSPilotResultV1,
    ETABSUnavailableError,
    InputContractError,
    connect_etabs_v1,
    get_etabs_bridge_status_v1,
    run_etabs_beam_pilot_v1,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/etabs-bridge/v1", tags=["etabs-bridge"])


@router.get(
    "/status",
    response_model=APIResponse[ETABSBridgeStatusV1],
    summary="Check local Python and ETABS COM bridge readiness",
)
async def get_etabs_bridge_status():
    return success_response(get_etabs_bridge_status_v1())


@router.post(
    "/connect",
    response_model=APIResponse[ETABSConnectionV1],
    summary="Attach to the already-open ETABS model and return its identity",
)
async def connect_etabs():
    try:
        result = await run_in_threadpool(connect_etabs_v1)
        return success_response(result)
    except ETABSUnavailableError as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(exc.to_problem()),
        )
    except ETABSConnectionError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(exc.to_problem()),
        )
    except Exception as exc:  # pragma: no cover - defensive COM boundary
        logger.exception("ETABS connection failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "ETABS connection")),
        )


@router.post(
    "/beam-pilot",
    response_model=APIResponse[ETABSPilotResultV1],
    summary="Extract and canonically design up to five rectangular ETABS beams",
)
async def run_etabs_beam_pilot(request: ETABSPilotRequestV1):
    try:
        result = await run_in_threadpool(run_etabs_beam_pilot_v1, request)
        return success_response(result)
    except InputContractError:
        raise
    except ETABSUnavailableError as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(exc.to_problem()),
        )
    except ETABSConnectionError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(exc.to_problem()),
        )
    except ETABSDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(exc.to_problem()),
        )
    except (TypeError, ValueError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "ETABS beam pilot")),
        )
    except Exception as exc:  # pragma: no cover - defensive COM boundary
        logger.exception("ETABS beam pilot failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "ETABS beam pilot")),
        )
