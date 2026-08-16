# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Shared, fail-closed structural result status contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

__all__ = [
    "RESULT_ENVELOPE_SCHEMA_VERSION",
    "CalculationStatus",
    "EngineeringStatus",
    "IntakeStatus",
    "OverallStatus",
    "ReviewStatus",
    "StructuralResultEnvelopeV1",
    "adapt_legacy_result_status",
    "derive_overall_status",
]


RESULT_ENVELOPE_SCHEMA_VERSION = "structural-result-envelope/v1"


class IntakeStatus(StrEnum):
    """Whether the complete calculation-bearing input was accepted."""

    VALID = "VALID"
    BLOCKED = "BLOCKED"


class CalculationStatus(StrEnum):
    """Whether a calculation was evaluated successfully."""

    NOT_EVALUATED = "NOT_EVALUATED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class EngineeringStatus(StrEnum):
    """Bounded engineering disposition; never a professional approval."""

    NOT_EVALUATED = "NOT_EVALUATED"
    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"
    HOLD = "HOLD"


class ReviewStatus(StrEnum):
    """Professional review boundary shared by every structural result."""

    QUALIFIED_REVIEW_REQUIRED = "QUALIFIED_REVIEW_REQUIRED"


class OverallStatus(StrEnum):
    """Deterministic aggregate of the orthogonal status axes."""

    BLOCKED = "BLOCKED"
    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"
    HOLD = "HOLD"


def derive_overall_status(
    intake_status: IntakeStatus,
    calculation_status: CalculationStatus,
    engineering_status: EngineeringStatus,
) -> OverallStatus:
    """Derive a fail-closed overall status from explicit orthogonal state."""

    if intake_status is IntakeStatus.BLOCKED:
        return OverallStatus.BLOCKED
    if calculation_status is not CalculationStatus.COMPLETED:
        return OverallStatus.HOLD
    if engineering_status is EngineeringStatus.PASS:
        return OverallStatus.PASS
    if engineering_status is EngineeringStatus.FAIL:
        return OverallStatus.FAIL
    return OverallStatus.HOLD


@dataclass(frozen=True)
class StructuralResultEnvelopeV1:
    """Versioned status envelope reusable across structural element results."""

    intake_status: IntakeStatus
    calculation_status: CalculationStatus
    engineering_status: EngineeringStatus
    serviceability_escalation: str | None = None
    review_status: ReviewStatus = ReviewStatus.QUALIFIED_REVIEW_REQUIRED

    @property
    def overall_status(self) -> OverallStatus:
        """Return the only permitted aggregate for the supplied axes."""

        return derive_overall_status(
            self.intake_status,
            self.calculation_status,
            self.engineering_status,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a stable transport representation."""

        return {
            "schema_version": RESULT_ENVELOPE_SCHEMA_VERSION,
            "intake_status": self.intake_status.value,
            "calculation_status": self.calculation_status.value,
            "engineering_status": self.engineering_status.value,
            "review_status": self.review_status.value,
            "qualified_review_required": True,
            "serviceability_escalation": self.serviceability_escalation,
            "overall_status": self.overall_status.value,
        }


def adapt_legacy_result_status(
    payload: Mapping[str, Any],
) -> StructuralResultEnvelopeV1:
    """Translate explicit legacy axes while mapping every missing axis to HOLD.

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
        intake = IntakeStatus(str(intake_raw))
    except ValueError:
        intake = IntakeStatus.VALID
        axes_complete = False
    try:
        calculation = CalculationStatus(str(calculation_raw))
    except ValueError:
        calculation = CalculationStatus.COMPLETED
        axes_complete = False
    try:
        engineering = EngineeringStatus(str(engineering_raw))
    except ValueError:
        engineering = EngineeringStatus.HOLD
        axes_complete = False

    if not axes_complete and intake is not IntakeStatus.BLOCKED:
        engineering = EngineeringStatus.HOLD
    return StructuralResultEnvelopeV1(
        intake_status=intake,
        calculation_status=calculation,
        engineering_status=engineering,
    )
