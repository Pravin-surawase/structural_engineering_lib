"""Versioned REST transport for Building Gravity Workflow V1."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.response import APIResponse, error_response, success_response
from structural_lib.services.gravity_calculation_book import (
    GravityWorkflowDefinitionV1,
    GravityWorkflowRunBundleV1,
    get_gravity_workflow_definition_v1,
    run_gravity_workflow_with_book_v1,
)
from structural_lib.services.gravity_workflow import GravityWorkflowRequestV1

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/building-gravity/v1", tags=["building-gravity"])


@router.get(
    "/definition",
    response_model=APIResponse[GravityWorkflowDefinitionV1],
    summary="Discover the bounded Building Gravity Workflow V1 contract",
)
async def get_building_gravity_definition_v1():
    return success_response(get_gravity_workflow_definition_v1())


@router.post(
    "/run",
    response_model=APIResponse[GravityWorkflowRunBundleV1],
    summary="Run the bounded one-storey dead/live gravity workflow",
)
async def run_building_gravity_v1(request: GravityWorkflowRequestV1):
    """Validate one accepted model/load identity and return its review dossier."""

    try:
        bundle = await run_in_threadpool(run_gravity_workflow_with_book_v1, request)
        return success_response(bundle)
    except (TypeError, ValueError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "building gravity workflow")),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Building Gravity Workflow V1 failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "building gravity workflow")),
        )
