"""Versioned REST transport for Excel Routine Workbench V1."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.response import APIResponse, error_response, success_response
from structural_lib.services.excel_workbench import (
    ExcelFreshnessCheckV1,
    ExcelFreshnessRequestV1,
    ExcelMappingPreviewV1,
    ExcelWorkbookPreviewRequestV1,
    ExcelWorkbookRunRequestV1,
    ExcelWorkbookRunResultV1,
    ExcelWorkbenchDefinitionV1,
    build_excel_mapping_preview_v1,
    check_excel_workbook_freshness_v1,
    get_excel_workbench_definition_v1,
    run_excel_workbook_v1,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/excel-workbench/v1", tags=["excel-workbench"])


@router.get(
    "/definition",
    response_model=APIResponse[ExcelWorkbenchDefinitionV1],
    summary="Discover the bounded Excel Routine Workbench V1 contract",
)
async def get_excel_workbench_definition():
    return success_response(get_excel_workbench_definition_v1())


@router.post(
    "/mapping-preview",
    response_model=APIResponse[ExcelMappingPreviewV1],
    summary="Preview and hash the selected Excel table mapping",
)
async def preview_excel_workbook_mapping(request: ExcelWorkbookPreviewRequestV1):
    return success_response(build_excel_mapping_preview_v1(request))


@router.post(
    "/run",
    response_model=APIResponse[ExcelWorkbookRunResultV1],
    summary="Run a reviewed selected-table rectangular-beam batch",
)
async def run_excel_workbook(request: ExcelWorkbookRunRequestV1):
    try:
        result = await run_in_threadpool(run_excel_workbook_v1, request)
        return success_response(result)
    except (TypeError, ValueError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(sanitize_error(exc, "Excel Workbench V1")),
        )
    except Exception as exc:  # pragma: no cover - defensive transport boundary
        logger.exception("Excel Workbench V1 failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(sanitize_error(exc, "Excel Workbench V1")),
        )


@router.post(
    "/freshness",
    response_model=APIResponse[ExcelFreshnessCheckV1],
    summary="Compare retained Excel evidence with the current selected table",
)
async def check_excel_workbook_freshness(request: ExcelFreshnessRequestV1):
    return success_response(check_excel_workbook_freshness_v1(request))
