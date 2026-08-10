"""Thin read-only transport for the canonical application workflow catalogue."""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from fastapi_app.models.catalog import WorkflowCatalogDocumentModel
from fastapi_app.models.response import APIResponse, error_response, success_response

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get(
    "/workflows",
    response_model=APIResponse[WorkflowCatalogDocumentModel],
    summary="Discover approved application workflows",
)
async def get_workflow_catalog(
    response: Response,
    version: str | None = Query(default=None),
):
    """Return the library-owned catalogue without serializing Python callables."""
    from structural_lib.services.workflow_catalog import (
        UnsupportedCatalogVersionError,
        get_workflow_catalog_document,
        serialize_workflow_catalog,
    )

    try:
        document = get_workflow_catalog_document(version)
        identity = hashlib.sha256(
            serialize_workflow_catalog(version).encode("utf-8")
        ).hexdigest()
    except UnsupportedCatalogVersionError as exc:
        return JSONResponse(
            status_code=409,
            content=error_response(
                {
                    "code": "UNSUPPORTED_CATALOG_VERSION",
                    "message": str(exc),
                }
            ),
        )

    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["ETag"] = f'"{identity}"'
    return success_response(document)
