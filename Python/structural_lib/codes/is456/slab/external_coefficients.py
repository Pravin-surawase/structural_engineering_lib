# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Record caller-supplied two-way slab coefficients without a table lookup.

This narrow P9 contract validates provenance and input shape only.  It does
not distribute, look up, interpolate, infer, or verify protected coefficient
data.  The submitted coefficients remain subject to qualified review before a
later design step may rely on them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456.slab.classification import (
    classify_solid_rectangular_slab,
)
from structural_lib.codes.is456.slab.models import (
    SlabClassification,
    SlabContractError,
    SolidRectangularSlabGeometry,
)

__all__ = [
    "AMENDMENT_6_SOURCE_ID",
    "ExternalCoefficientPolicyStatus",
    "ExternalCoefficientReviewStatus",
    "ExternalTwoWaySlabCoefficientRecord",
    "IS456_CONSOLIDATED_SOURCE_ID",
    "record_external_two_way_slab_coefficients",
]


IS456_CONSOLIDATED_SOURCE_ID = (
    "is456_2000_amd5_reff2021.pdf:"
    "sha256:964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264"
)
AMENDMENT_6_SOURCE_ID = (
    "is456_amd_06_2024.pdf:"
    "sha256:4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881"
)


class ExternalCoefficientPolicyStatus(StrEnum):
    """Policy state for coefficients that must originate outside the package."""

    EXTERNAL_SOURCE_REQUIRED = "external_source_required"


class ExternalCoefficientReviewStatus(StrEnum):
    """Review state; this recorder cannot validate coefficient correctness."""

    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class ExternalTwoWaySlabCoefficientRecord:
    """Immutable provenance record for caller-supplied two-way coefficients.

    ``alpha_x`` and ``alpha_y`` are retained exactly as submitted after basic
    dimensionless-domain validation.  This record asserts neither the support
    case nor the correctness or applicability of either coefficient.
    """

    geometry: SolidRectangularSlabGeometry
    support_case_id: str
    alpha_x: float
    alpha_y: float
    span_ratio_ly_lx: float
    coefficient_source_reference: str
    coefficient_source_is_approved: bool
    source_ids: tuple[str, str]
    policy_status: ExternalCoefficientPolicyStatus
    coefficient_review_status: ExternalCoefficientReviewStatus
    qualified_acceptance_recorded: bool
    coefficient_correctness_verified_by_library: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        """Keep the public immutable record fail-closed when built directly."""
        classification_result = classify_solid_rectangular_slab(self.geometry)
        if classification_result.classification is not SlabClassification.TWO_WAY:
            raise SlabContractError(
                "external two-way slab coefficients require geometry classified as two_way"
            )
        if self.coefficient_source_is_approved is not True:
            raise SlabContractError(
                "coefficient_source_is_approved must be True for external coefficients"
            )
        if self.span_ratio_ly_lx != classification_result.span_ratio_ly_lx:
            raise SlabContractError(
                "span_ratio_ly_lx must exactly echo the P6 geometry classification"
            )
        if self.source_ids != (IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID):
            raise SlabContractError(
                "source_ids must retain the approved source identities"
            )
        if (
            self.policy_status
            is not ExternalCoefficientPolicyStatus.EXTERNAL_SOURCE_REQUIRED
        ):
            raise SlabContractError("policy_status must be external_source_required")
        if (
            self.coefficient_review_status
            is not ExternalCoefficientReviewStatus.REVIEW_REQUIRED
        ):
            raise SlabContractError("coefficient_review_status must be review_required")
        if self.qualified_acceptance_recorded is not False:
            raise SlabContractError(
                "P9 coefficient records cannot record qualified acceptance"
            )
        if self.coefficient_correctness_verified_by_library is not False:
            raise SlabContractError(
                "coefficient correctness cannot be verified by this library"
            )

        object.__setattr__(
            self,
            "support_case_id",
            _nonblank_string(self.support_case_id, "support_case_id"),
        )
        object.__setattr__(
            self, "alpha_x", _positive_finite_coefficient(self.alpha_x, "alpha_x")
        )
        object.__setattr__(
            self, "alpha_y", _positive_finite_coefficient(self.alpha_y, "alpha_y")
        )
        object.__setattr__(
            self,
            "coefficient_source_reference",
            _nonblank_string(
                self.coefficient_source_reference, "coefficient_source_reference"
            ),
        )
        _nonempty_text_tuple(self.assumptions, "assumptions")
        _nonempty_text_tuple(self.limitations, "limitations")

    @property
    def review_status(self) -> ExternalCoefficientReviewStatus:
        """Compatibility alias; use ``coefficient_review_status`` in records."""
        return self.coefficient_review_status

    @property
    def coefficient_correctness_is_verified(self) -> bool:
        """Compatibility alias; use the library-specific canonical field."""
        return self.coefficient_correctness_verified_by_library


def _positive_finite_coefficient(value: float, field_name: str) -> float:
    """Validate a dimensionless input without encoding coefficient data."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{field_name} must be a real dimensionless value")

    normalized = float(value)
    if not math.isfinite(normalized):
        raise SlabContractError(f"{field_name} must be finite")
    if not 0.0 < normalized <= 1.0:
        raise SlabContractError(f"{field_name} must be within the interval (0, 1]")
    return normalized


def _nonblank_string(value: str, field_name: str) -> str:
    """Require an explicit caller-defined identifier or reference."""
    if not isinstance(value, str) or not value.strip():
        raise SlabContractError(f"{field_name} must be a non-blank string")
    return value


def _nonempty_text_tuple(value: tuple[str, ...], field_name: str) -> None:
    """Require recorded assumptions and limitations rather than omitting them."""
    if not isinstance(value, tuple) or not value:
        raise SlabContractError(f"{field_name} must be a non-empty tuple of strings")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise SlabContractError(f"{field_name} must contain only non-blank strings")


def record_external_two_way_slab_coefficients(
    *,
    geometry: SolidRectangularSlabGeometry,
    support_case_id: str,
    alpha_x: float,
    alpha_y: float,
    coefficient_source_reference: str,
    coefficient_source_is_approved: bool,
) -> ExternalTwoWaySlabCoefficientRecord:
    """Validate and record externally sourced coefficients for a two-way slab.

    The caller defines ``support_case_id`` and provides both coefficient values
    plus an exact source reference.  ``coefficient_source_is_approved`` is an
    affirmative provenance acknowledgement; false is rejected.  This function
    never chooses a support case, reads coefficient data, or assesses whether
    the submitted values are correct.

    Raises:
        SlabContractError: If geometry is not two-way, provenance is incomplete,
            or either submitted coefficient is outside the validation domain.
    """
    classification_result = classify_solid_rectangular_slab(geometry)
    if classification_result.classification is not SlabClassification.TWO_WAY:
        raise SlabContractError(
            "external two-way slab coefficients require geometry classified as two_way"
        )
    return ExternalTwoWaySlabCoefficientRecord(
        geometry=geometry,
        support_case_id=support_case_id,
        alpha_x=alpha_x,
        alpha_y=alpha_y,
        span_ratio_ly_lx=classification_result.span_ratio_ly_lx,
        coefficient_source_reference=coefficient_source_reference,
        coefficient_source_is_approved=coefficient_source_is_approved,
        source_ids=(IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID),
        policy_status=ExternalCoefficientPolicyStatus.EXTERNAL_SOURCE_REQUIRED,
        coefficient_review_status=ExternalCoefficientReviewStatus.REVIEW_REQUIRED,
        qualified_acceptance_recorded=False,
        coefficient_correctness_verified_by_library=False,
        assumptions=(
            "Effective spans are caller-supplied in mm and classified by the P6 contract.",
            "support_case_id is caller-defined and is not interpreted by this contract.",
            "alpha_x and alpha_y are caller-supplied external inputs; no table is bundled or queried.",
        ),
        limitations=(
            "Coefficient correctness, support applicability, and source interpretation are not verified by this library.",
            "This P9 record does not record qualified acceptance; that provenance belongs to the P10 result.",
            "A qualified review must accept the specific submitted coefficients before later design use.",
            "P10 moment and design calculations depend on an accepted external-coefficient record.",
        ),
    )
