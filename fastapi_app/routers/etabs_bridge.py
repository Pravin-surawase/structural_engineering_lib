"""Versioned localhost transport for the bounded live ETABS beam pilot."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from fastapi_app.auth import (
    require_etabs_live_mutation,
    require_etabs_live_read,
    require_loopback_request,
)
from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.response import APIResponse, error_response, success_response
from structural_lib.services.contracts.etabs_w3 import (
    BeamDemandBuildResultV1,
    BeamDemandDerivationRequestV1,
    derive_beam_demand_snapshot_v1,
)
from structural_lib.services.etabs_beam_bridge import (
    ETABSBeamBaselineCapacityError,
    ETABSBeamBaselinePreflightV1,
    ETABSBeamBaselineRunRequestV1,
    ETABSBeamBaselineTransportV1,
    inspect_etabs_beam_baseline_v1,
    run_etabs_beam_baseline_v1,
)
from structural_lib.services.etabs_catalogue_bridge import (
    ETABSLiveCatalogueRunRequestV1,
    ETABSLiveCatalogueTransportV1,
    run_etabs_live_catalogue_v1,
)
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

offline_router = APIRouter(prefix="/etabs-bridge/v1", tags=["etabs-bridge"])
live_read_router = APIRouter(
    prefix="/etabs-bridge/v1",
    tags=["etabs-bridge"],
    dependencies=[
        Depends(require_loopback_request),
        Depends(require_etabs_live_read),
    ],
)
live_mutation_router = APIRouter(
    prefix="/etabs-bridge/v1",
    tags=["etabs-bridge"],
    dependencies=[
        Depends(require_loopback_request),
        Depends(require_etabs_live_mutation),
    ],
)

# Compatibility alias for callers that intentionally mount offline-only routes.
router = offline_router


@offline_router.get(
    "/status",
    response_model=APIResponse[ETABSBridgeStatusV1],
    summary="Check local Python and ETABS COM bridge readiness",
)
async def get_etabs_bridge_status():
    return success_response(get_etabs_bridge_status_v1())


@live_read_router.post(
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


@live_read_router.post(
    "/beam-baseline/preflight",
    response_model=APIResponse[ETABSBeamBaselinePreflightV1],
    summary="Inspect the open ETABS model and runtime before a W2 baseline read",
)
async def inspect_etabs_beam_baseline():
    try:
        result = await run_in_threadpool(inspect_etabs_beam_baseline_v1)
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
    except ETABSDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(exc.to_problem()),
        )
    except Exception as exc:  # pragma: no cover - defensive COM boundary
        logger.exception("ETABS baseline preflight failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "ETABS baseline preflight")),
        )


@live_read_router.post(
    "/beam-baseline",
    response_model=APIResponse[ETABSBeamBaselineTransportV1],
    summary="Read one complete preflight-bound W2 beam baseline",
)
async def run_etabs_beam_baseline(request: ETABSBeamBaselineRunRequestV1):
    try:
        result = await run_in_threadpool(run_etabs_beam_baseline_v1, request)
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
    except ETABSBeamBaselineCapacityError as exc:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
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
            content=error_response(sanitize_error(exc, "ETABS beam baseline")),
        )
    except Exception as exc:  # pragma: no cover - defensive COM boundary
        logger.exception("ETABS beam baseline failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "ETABS beam baseline")),
        )


@live_read_router.post(
    "/result-catalogue",
    response_model=APIResponse[ETABSLiveCatalogueTransportV1],
    summary="Read one complete preflight-bound W3 result catalogue",
)
async def run_etabs_result_catalogue(request: ETABSLiveCatalogueRunRequestV1):
    try:
        result = await run_in_threadpool(run_etabs_live_catalogue_v1, request)
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
    except ETABSDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(exc.to_problem()),
        )
    except (TypeError, ValueError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "ETABS result catalogue")),
        )
    except Exception as exc:  # pragma: no cover - defensive COM boundary
        logger.exception("ETABS result catalogue failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "ETABS result catalogue")),
        )


@offline_router.post(
    "/beam-demand",
    response_model=APIResponse[BeamDemandBuildResultV1],
    summary="Derive a canonical W3 beam-demand snapshot from retained evidence",
)
async def derive_etabs_beam_demand(payload: dict[str, Any]):
    try:
        request = BeamDemandDerivationRequestV1.model_validate(payload, strict=False)
        result = await run_in_threadpool(derive_beam_demand_snapshot_v1, request)
        return success_response(result)
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "ETABS beam demand")),
        )
    except (TypeError, ValueError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "ETABS beam demand")),
        )
    except Exception as exc:  # pragma: no cover - defensive calculation boundary
        logger.exception("ETABS beam demand derivation failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "ETABS beam demand")),
        )


@live_mutation_router.post(
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
