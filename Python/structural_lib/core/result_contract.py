# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Canonical, fail-closed structural result and issue contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

__all__ = [
    "RESULT_ENVELOPE_SCHEMA_VERSION",
    "CalculationStatus",
    "EngineeringStatus",
    "FreshnessStatus",
    "IntakeStatus",
    "OverallStatus",
    "ResultIdentityV1",
    "ReviewStatus",
    "StructuralIssueV1",
    "StructuralResultEnvelopeV1",
    "StructuralResultEnvelopeV2",
    "adapt_legacy_result_status",
    "derive_overall_status",
]


RESULT_ENVELOPE_SCHEMA_VERSION = "structural-result-envelope/v2"


class IntakeStatus(StrEnum):
    """Whether all calculation-bearing input was accounted and accepted."""

    VALID = "VALID"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"

    # More descriptive spelling for new callers; transport remains compatible.
    ACCEPTED = "VALID"


class CalculationStatus(StrEnum):
    """Whether the declared calculation was evaluated successfully."""

    NOT_EVALUATED = "NOT_EVALUATED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

    # Descriptive aliases for callers that use calculation-centric wording.
    NOT_CALCULATED = "NOT_EVALUATED"
    CALCULATED = "COMPLETED"
    FAILED = "ERROR"


class EngineeringStatus(StrEnum):
    """Bounded engineering disposition; never a professional approval."""

    NOT_EVALUATED = "NOT_EVALUATED"
    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"
    HOLD = "HOLD"

    UNEVALUATED = "NOT_EVALUATED"


class ReviewStatus(StrEnum):
    """Qualified-review state kept separate from software calculation status."""

    QUALIFIED_REVIEW_REQUIRED = "QUALIFIED_REVIEW_REQUIRED"
    REVIEWED_ACCEPTED = "REVIEWED_ACCEPTED"
    REVIEWED_REJECTED = "REVIEWED_REJECTED"

    REVIEW_REQUIRED = "QUALIFIED_REVIEW_REQUIRED"


class FreshnessStatus(StrEnum):
    """Whether the result still matches the inputs and calculation identity."""

    CURRENT = "CURRENT"
    STALE = "STALE"


class OverallStatus(StrEnum):
    """Deterministic fail-closed aggregate of the calculation-bearing axes."""

    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    NOT_EVALUATED = "NOT_EVALUATED"
    STALE = "STALE"
    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class StructuralIssueV1:
    """Stable machine issue with an exact path and human explanation."""

    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class ResultIdentityV1:
    """Minimum replay identity carried by a canonical structural result."""

    contract_version: str
    library_version: str
    input_hash: str | None = None
    calculation_identity: str | None = None
    artifact_sha256: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "contract_version": self.contract_version,
            "library_version": self.library_version,
            "input_hash": self.input_hash,
            "calculation_identity": self.calculation_identity,
            "artifact_sha256": self.artifact_sha256,
        }


def derive_overall_status(
    intake_status: IntakeStatus,
    calculation_status: CalculationStatus,
    engineering_status: EngineeringStatus,
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT,
) -> OverallStatus:
    """Derive the only permitted aggregate from explicit orthogonal state."""

    if intake_status is IntakeStatus.BLOCKED:
        return OverallStatus.BLOCKED
    if calculation_status is CalculationStatus.ERROR:
        return OverallStatus.ERROR
    if freshness_status is FreshnessStatus.STALE:
        return OverallStatus.STALE
    if intake_status is IntakeStatus.PARTIAL:
        return OverallStatus.HOLD
    if calculation_status is CalculationStatus.NOT_EVALUATED:
        return OverallStatus.NOT_EVALUATED
    if engineering_status is EngineeringStatus.PASS:
        return OverallStatus.PASS
    if engineering_status is EngineeringStatus.FAIL:
        return OverallStatus.FAIL
    return OverallStatus.HOLD


@dataclass(frozen=True)
class StructuralResultEnvelopeV2:
    """Versioned status, issue, review, and replay-identity envelope."""

    intake_status: IntakeStatus
    calculation_status: CalculationStatus
    engineering_status: EngineeringStatus
    issues: tuple[StructuralIssueV1, ...] = ()
    result_identity: ResultIdentityV1 | None = None
    serviceability_escalation: str | None = None
    review_status: ReviewStatus = ReviewStatus.QUALIFIED_REVIEW_REQUIRED
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT

    @property
    def overall_status(self) -> OverallStatus:
        """Return the fail-closed aggregate for the supplied axes."""

        return derive_overall_status(
            self.intake_status,
            self.calculation_status,
            self.engineering_status,
            self.freshness_status,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the one stable transport representation."""

        return {
            "schema_version": RESULT_ENVELOPE_SCHEMA_VERSION,
            "intake_status": self.intake_status.value,
            "calculation_status": self.calculation_status.value,
            "engineering_status": self.engineering_status.value,
            "review_status": self.review_status.value,
            "qualified_review_required": self.review_status
            is ReviewStatus.QUALIFIED_REVIEW_REQUIRED,
            "freshness_status": self.freshness_status.value,
            "serviceability_escalation": self.serviceability_escalation,
            "overall_status": self.overall_status.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "result_identity": (
                self.result_identity.to_dict()
                if self.result_identity is not None
                else None
            ),
        }


# The v1 public name is a compatibility alias to the single canonical carrier,
# not a second competing result implementation.
StructuralResultEnvelopeV1 = StructuralResultEnvelopeV2


_INTAKE_ALIASES = {"ACCEPTED": "VALID"}
_CALCULATION_ALIASES = {
    "NOT_CALCULATED": "NOT_EVALUATED",
    "CALCULATED": "COMPLETED",
    "FAILED": "ERROR",
}
_ENGINEERING_ALIASES = {"UNEVALUATED": "NOT_EVALUATED"}


def adapt_legacy_result_status(
    payload: Mapping[str, Any],
) -> StructuralResultEnvelopeV2:
    """Translate explicit legacy axes while mapping missing truth to HOLD.

    Boolean ``success`` or ``is_safe`` fields are deliberately ignored. They
    cannot prove that intake and calculation completed under this contract.
    """

    intake_raw = payload.get("intake_status")
    calculation_raw = payload.get("calculation_status")
    engineering_raw = payload.get("engineering_status")
    axes_complete = all(
        value is not None for value in (intake_raw, calculation_raw, engineering_raw)
    )
    try:
        intake = IntakeStatus(_INTAKE_ALIASES.get(str(intake_raw), str(intake_raw)))
    except ValueError:
        intake = IntakeStatus.VALID
        axes_complete = False
    try:
        calculation = CalculationStatus(
            _CALCULATION_ALIASES.get(str(calculation_raw), str(calculation_raw))
        )
    except ValueError:
        calculation = CalculationStatus.NOT_EVALUATED
        axes_complete = False
    try:
        engineering = EngineeringStatus(
            _ENGINEERING_ALIASES.get(str(engineering_raw), str(engineering_raw))
        )
    except ValueError:
        engineering = EngineeringStatus.HOLD
        axes_complete = False

    issues: tuple[StructuralIssueV1, ...] = ()
    if not axes_complete and intake is not IntakeStatus.BLOCKED:
        intake = IntakeStatus.PARTIAL
        engineering = EngineeringStatus.HOLD
        issues = (
            StructuralIssueV1(
                code="CANONICAL_STATUS_INCOMPLETE",
                path="$",
                message="Legacy result omitted one or more canonical status axes.",
            ),
        )
    return StructuralResultEnvelopeV2(
        intake_status=intake,
        calculation_status=calculation,
        engineering_status=engineering,
        issues=issues,
    )
