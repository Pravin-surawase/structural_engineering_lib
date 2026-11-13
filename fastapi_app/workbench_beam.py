"""HTTP inputs and replay error mapping for checked workbench layouts."""

from __future__ import annotations

from typing import Literal, TypeVar

from fastapi import HTTPException
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)

from structural_lib.services.canonical_beam import BeamDesignAndDetailResultV1
from structural_lib.services.contracts.beam import BeamDesignInputV1
from structural_lib.services.workbench_beam import replay_workbench_layout


class WorkbenchBeamExportRequest(BaseModel):
    """Exact calculation request and checked-layout identity from the workbench."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    checked_request: BeamDesignInputV1
    checked_layout_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    format: Literal["html", "json"] = "html"

    @property
    def beam_id(self) -> str:
        return self.checked_request.identity.member_id


LegacyRequest = TypeVar("LegacyRequest", bound=BaseModel)


def checked_layout_or(legacy_model: type[LegacyRequest]) -> WrapValidator:
    """Select a wire shape without adding union labels to validation paths."""

    def validate(
        value: object, _handler: ValidatorFunctionWrapHandler
    ) -> WorkbenchBeamExportRequest | LegacyRequest:
        if isinstance(value, dict) and (
            "checked_request" in value or "checked_layout_id" in value
        ):
            return WorkbenchBeamExportRequest.model_validate(value)
        return legacy_model.model_validate(value)

    return WrapValidator(validate)


def replay_checked_workbench(
    request: WorkbenchBeamExportRequest,
) -> BeamDesignAndDetailResultV1:
    """Return the checked physical layout or a replay conflict."""
    try:
        return replay_workbench_layout(
            request.checked_request, request.checked_layout_id
        )
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
