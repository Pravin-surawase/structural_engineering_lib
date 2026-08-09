"""Public discovery route for the canonical supported IS 456 contract."""

from __future__ import annotations

from fastapi import APIRouter

from fastapi_app.models.capabilities import IS456CapabilityDocumentModel
from fastapi_app.models.response import APIResponse, success_response

router = APIRouter(prefix="/library", tags=["library"])


@router.get(
    "/capabilities",
    response_model=APIResponse[IS456CapabilityDocumentModel],
    summary="Discover supported and held IS 456 capabilities",
)
async def get_library_capabilities():
    """Return the same canonical document exposed by Python and the CLI."""
    from structural_lib.services.api import get_supported_is456_capability_document

    return success_response(get_supported_is456_capability_document())
