# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Shared result and error boundary for curated family facades.

This module contains transport construction only.  Engineering arithmetic stays
in the existing family service and code owners.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, NoReturn

from pydantic import Field

from structural_lib.core.errors import (
    CalculationError,
    InputContractError,
    InputIssueV1,
)
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    ResultIdentityV1,
    ReviewStatus,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.core.version import get_runtime_version
from structural_lib.services.contracts.common import StrictPublicModel

__all__ = [
    "CanonicalFamilyResultV1",
    "FamilyIdentityV1",
    "canonical_family_result",
    "require_request_type",
    "translate_owner_input_error",
]


class FamilyIdentityV1(StrictPublicModel):
    """Caller-owned replay identity for one bounded family calculation."""

    family_id: str = Field(min_length=1, max_length=80)
    case_id: str = Field(min_length=1, max_length=80)
    member_id: str | None = Field(default=None, min_length=1, max_length=80)
    story: str | None = Field(default=None, min_length=1, max_length=80)
    source_reference: str | None = Field(default=None, min_length=1, max_length=240)


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CalculationError(
                "Canonical family result contains a non-finite numeric value.",
                details={"value": str(value)},
            )
        return value
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="python"))
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if hasattr(value, "to_dict"):
        return _jsonable(value.to_dict())
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    raise CalculationError(
        "Canonical family result contains an unsupported serialization value.",
        details={"type": type(value).__name__},
    )


def _input_hash(request: StrictPublicModel) -> str:
    payload = json.dumps(
        request.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CanonicalFamilyResultV1:
    """Typed family payload carried by the common B0 result semantics."""

    request: StrictPublicModel
    calculation: Any
    envelope: StructuralResultEnvelopeV2
    limitations: tuple[str, ...]
    assumptions: tuple[str, ...]
    provenance: tuple[str, ...]
    workflow_id: str
    schema_version: str = "family-design-result/v1"

    @property
    def identity(self) -> FamilyIdentityV1:
        identity = getattr(self.request, "identity", None)
        if not isinstance(identity, FamilyIdentityV1):
            raise CalculationError(
                "Canonical family request omitted FamilyIdentityV1.",
                details={"request_type": type(self.request).__name__},
            )
        return identity

    @property
    def intake_status(self) -> IntakeStatus:
        return self.envelope.intake_status

    @property
    def calculation_status(self) -> CalculationStatus:
        return self.envelope.calculation_status

    @property
    def engineering_status(self) -> EngineeringStatus:
        return self.envelope.engineering_status

    @property
    def qualified_review_required(self) -> bool:
        return self.envelope.review_status is ReviewStatus.QUALIFIED_REVIEW_REQUIRED

    @property
    def issues(self) -> tuple[StructuralIssueV1, ...]:
        return self.envelope.issues

    @property
    def is_ok(self) -> bool:
        return self.engineering_status is EngineeringStatus.PASS

    @property
    def is_safe(self) -> bool:
        return self.is_ok

    def to_dict(self) -> dict[str, Any]:
        value = _jsonable(
            {
                "schema_version": self.schema_version,
                "workflow_id": self.workflow_id,
                "identity": self.identity,
                "request": self.request,
                "envelope": self.envelope.to_dict(),
                "calculation": self.calculation,
                "limitations": self.limitations,
                "assumptions": self.assumptions,
                "provenance": self.provenance,
            }
        )
        assert isinstance(value, dict)
        return value


def canonical_family_result(
    request: StrictPublicModel,
    calculation: Any,
    *,
    workflow_id: str,
    engineering_status: EngineeringStatus,
    limitations: tuple[str, ...] = (),
    assumptions: tuple[str, ...] = (),
    provenance: tuple[str, ...] = (),
) -> CanonicalFamilyResultV1:
    """Bind one completed owner calculation to the common result envelope."""

    return CanonicalFamilyResultV1(
        request=request,
        calculation=calculation,
        envelope=StructuralResultEnvelopeV2(
            intake_status=IntakeStatus.VALID,
            calculation_status=CalculationStatus.COMPLETED,
            engineering_status=engineering_status,
            review_status=ReviewStatus.QUALIFIED_REVIEW_REQUIRED,
            result_identity=ResultIdentityV1(
                contract_version=str(
                    getattr(request, "schema_version", "family-input/v1")
                ),
                library_version=get_runtime_version(),
                input_hash=_input_hash(request),
                calculation_identity=workflow_id,
            ),
        ),
        limitations=limitations,
        assumptions=assumptions,
        provenance=provenance,
        workflow_id=workflow_id,
    )


def require_request_type(request: object, expected: type[StrictPublicModel]) -> None:
    """Fail closed before any owner calculation is invoked."""

    if not isinstance(request, expected):
        raise InputContractError(
            (
                InputIssueV1(
                    code="INPUT_TYPE_INVALID",
                    path="request",
                    message=f"request must be {expected.__name__}",
                    received=f"<{type(request).__name__}>",
                ),
            )
        )


def translate_owner_input_error(error: Exception, *, path: str = "request") -> NoReturn:
    """Translate a known owner contract exception without hiding internals."""

    raise InputContractError(
        (
            InputIssueV1(
                code="FAMILY_INPUT_INVALID",
                path=path,
                message=str(error),
            ),
        )
    ) from error
