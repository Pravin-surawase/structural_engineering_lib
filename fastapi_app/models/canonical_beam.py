"""FastAPI response projection of the canonical beam service result."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from fastapi_app.models.response import StructuralResultEnvelopeResponse
from structural_lib.services.contracts.beam import BeamDesignInputV1, MemberIdentityV1


class CanonicalBeamDesignResponseV1(BaseModel):
    """Typed REST v2 projection of ``BeamDesignResultV1``."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["beam-design-result/v1"]
    identity: MemberIdentityV1
    request: BeamDesignInputV1
    envelope: StructuralResultEnvelopeResponse
    calculation: dict[str, Any]
    limitations: list[str]
    assumptions: list[str]
    provenance: list[str]
