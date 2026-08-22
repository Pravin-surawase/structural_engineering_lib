# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed, explicit-unit contracts for the supported IS 456 slab scope.

P6 deliberately models only solid rectangular slab geometry supplied with
effective spans.  It does not derive spans, infer supports, or select a design
method.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    StructuralIssueV1,
    StructuralResultEnvelopeV1,
)

__all__ = [
    "SlabClassification",
    "SlabClassificationResult",
    "SlabCapacityFailureResult",
    "SlabContractError",
    "SlabScopeStatus",
    "SolidRectangularSlabGeometry",
    "slab_capacity_failure",
]


class SlabContractError(ValueError):
    """Raised when input is outside the P6 solid rectangular slab contract."""


@dataclass(frozen=True)
class SlabCapacityFailureResult:
    """Structured engineering failure for supported slab flexural demand."""

    component: str
    governing_region: str
    factored_moment_knm: float
    limiting_moment_knm: float
    utilization_ratio: float
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    status: EngineeringStatus
    qualified_review_required: bool
    result_envelope: StructuralResultEnvelopeV1

    @property
    def is_safe(self) -> bool:
        """Capacity exceedance is always an engineering failure."""

        return False


def slab_capacity_failure(
    *,
    component: str,
    governing_region: str,
    factored_moment_knm: float,
    limiting_moment_knm: float,
    clause_refs: tuple[str, ...],
    source_refs: tuple[str, ...],
) -> SlabCapacityFailureResult:
    """Build the canonical VALID/COMPLETED/FAIL slab-capacity result."""

    utilization_ratio = factored_moment_knm / limiting_moment_knm
    issue = StructuralIssueV1(
        code="SLAB_FLEXURE_CAPACITY_EXCEEDED",
        path="$.factored_area_load_kn_per_m2",
        message=(
            f"{governing_region} factored moment {factored_moment_knm:.6g} kN m "
            f"exceeds limiting singly reinforced capacity "
            f"{limiting_moment_knm:.6g} kN m."
        ),
    )
    result_envelope = StructuralResultEnvelopeV1(
        intake_status=IntakeStatus.VALID,
        calculation_status=CalculationStatus.COMPLETED,
        engineering_status=EngineeringStatus.FAIL,
        issues=(issue,),
    )
    return SlabCapacityFailureResult(
        component=component,
        governing_region=governing_region,
        factored_moment_knm=factored_moment_knm,
        limiting_moment_knm=limiting_moment_knm,
        utilization_ratio=utilization_ratio,
        clause_refs=clause_refs,
        source_refs=source_refs,
        status=EngineeringStatus.FAIL,
        qualified_review_required=True,
        result_envelope=result_envelope,
    )


class SlabClassification(StrEnum):
    """Load-action classification based only on normalized effective spans."""

    ONE_WAY = "one_way"
    TWO_WAY = "two_way"


class SlabScopeStatus(StrEnum):
    """Whether a result is within the intentionally narrow P6 scope."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"


def _positive_finite_mm(value: float, field_name: str) -> float:
    """Return a finite positive millimetre quantity or raise a contract error."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{field_name} must be a real value in mm")

    normalized = float(value)
    if not math.isfinite(normalized):
        raise SlabContractError(f"{field_name} must be finite in mm")
    if normalized <= 0.0:
        raise SlabContractError(f"{field_name} must be positive in mm")
    return normalized


@dataclass(frozen=True)
class SolidRectangularSlabGeometry:
    """Solid rectangular slab geometry with caller-supplied effective spans.

    ``span_a_effective_mm`` and ``span_b_effective_mm`` are intentionally
    axis-neutral.  This contract normalizes them into short ``Lx`` and long
    ``Ly`` spans, so callers do not need to supply their spans in a particular
    order.  The effective-span derivation, support condition, and any design
    route remain outside this type.
    """

    span_a_effective_mm: float
    span_b_effective_mm: float
    thickness_mm: float
    strip_width_mm: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "span_a_effective_mm",
            _positive_finite_mm(self.span_a_effective_mm, "span_a_effective_mm"),
        )
        object.__setattr__(
            self,
            "span_b_effective_mm",
            _positive_finite_mm(self.span_b_effective_mm, "span_b_effective_mm"),
        )
        object.__setattr__(
            self,
            "thickness_mm",
            _positive_finite_mm(self.thickness_mm, "thickness_mm"),
        )
        if self.strip_width_mm is not None:
            object.__setattr__(
                self,
                "strip_width_mm",
                _positive_finite_mm(self.strip_width_mm, "strip_width_mm"),
            )

    @property
    def short_effective_span_mm(self) -> float:
        """Normalized short effective span, Lx (mm)."""
        return min(self.span_a_effective_mm, self.span_b_effective_mm)

    @property
    def long_effective_span_mm(self) -> float:
        """Normalized long effective span, Ly (mm)."""
        return max(self.span_a_effective_mm, self.span_b_effective_mm)

    @property
    def span_order_was_normalized(self) -> bool:
        """Whether the caller supplied the long span before the short span."""
        return self.span_a_effective_mm > self.span_b_effective_mm


@dataclass(frozen=True)
class SlabClassificationResult:
    """Classification-only result; it is not a slab design result."""

    geometry: SolidRectangularSlabGeometry
    classification: SlabClassification
    span_ratio_ly_lx: float
    scope_status: SlabScopeStatus
    assumptions: tuple[str, ...]
    source_refs: tuple[str, ...]

    @property
    def is_supported(self) -> bool:
        """Return whether this result is within the current P6 scope."""
        return self.scope_status is SlabScopeStatus.SUPPORTED
