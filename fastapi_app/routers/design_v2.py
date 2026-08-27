"""Versioned canonical beam-design transport."""

from fastapi import APIRouter

from fastapi_app.models.canonical_beam import CanonicalBeamDesignResponseV1
from structural_lib.design.is456 import beam
from structural_lib.services.contracts.beam import BeamDesignInputV1

router = APIRouter(prefix="/api/v2/design", tags=["design-v2"])


@router.post(
    "/beam",
    response_model=CanonicalBeamDesignResponseV1,
    summary="Run the canonical IS 456 rectangular-beam design journey",
)
async def design_beam_v2(request: BeamDesignInputV1) -> dict:
    """Return the same nested request, issues, and result contract as Python."""

    return beam.design(request).to_dict()
