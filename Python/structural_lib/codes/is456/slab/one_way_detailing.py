# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""P8 provided-reinforcement checks for the bounded one-way slab strip.

This module consumes the accepted P7 flexural result.  It checks only the
caller-provided main and distribution reinforcement; it never selects bars or
uses deflection modification factors.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456.slab.models import (
    SlabContractError,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.slab.one_way import (
    OneWaySlabFlexureInput,
    OneWaySlabFlexureResult,
    OneWaySlabFlexureStatus,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "DetailingAdequacyStatus",
    "OneWaySlabDetailingCheck",
    "OneWaySlabDetailingInput",
    "OneWaySlabDetailingResult",
    "OneWaySlabReviewRequirement",
    "OneWaySlabServiceabilityStatus",
    "check_simply_supported_one_way_slab_detailing",
]


_SUPPORTED_FY_N_PER_MM2 = (250.0, 415.0, 500.0)
_DEFAULT_STRIP_WIDTH_MM = 1000.0
_P8_SOURCE_REFS: tuple[str, ...] = (
    "P8-MIN-REINF-01",
    "P8-BAR-DIA-01",
    "P8-MAIN-SPACING-01",
    "P8-DIST-SPACING-01",
    "P8-BASIC-LD-01",
)
_P8_LIMITATIONS: tuple[str, ...] = (
    "P8 HOLD: deflection modification factors are not implemented.",
    "P8 HOLD: direct deflection calculation is not implemented.",
    "P8 HOLD: cracking, shear, load combinations, continuity, cantilevers, and load patterns are not checked.",
    "REVIEW LIMITATION: qualified structural-engineering review remains required where the basic Lx/d boundary is exceeded.",
)


class DetailingAdequacyStatus(StrEnum):
    """Whether all provided-reinforcement detailing checks pass."""

    ADEQUATE = "adequate"
    INADEQUATE = "inadequate"


class OneWaySlabServiceabilityStatus(StrEnum):
    """Bounded serviceability disposition for the simply supported strip."""

    BASIC_RATIO_SATISFIED = "basic_ratio_satisfied"
    QUALIFIED_REVIEW_REQUIRED = "qualified_review_required"


class OneWaySlabReviewRequirement(StrEnum):
    """Whether the bounded result requires qualified engineering review."""

    NO_QUALIFIED_REVIEW_REQUIRED = "no_qualified_review_required"
    QUALIFIED_REVIEW_REQUIRED = "qualified_review_required"


@dataclass(frozen=True)
class OneWaySlabDetailingCheck:
    """One explicit P8 comparison, retaining derived values and units."""

    check_id: str
    actual: float
    limit: float
    unit: str
    comparison: str
    passed: bool


def _positive_finite(value: float, field_name: str, unit: str) -> float:
    """Normalize a positive finite engineering input or fail closed."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise SlabContractError(f"{field_name} must be finite in {unit}")
    if normalized <= 0.0:
        raise SlabContractError(f"{field_name} must be positive in {unit}")
    return normalized


def _supported_fy(value: float) -> bool:
    """Return whether the P7 steel grade has a supported P8 minimum ratio."""
    return any(abs(value - grade) < 0.5 for grade in _SUPPORTED_FY_N_PER_MM2)


def _minimum_reinforcement_ratio(fy_n_per_mm2: float) -> float:
    """Return the P8 minimum reinforcement fraction for the supported grade."""
    if abs(fy_n_per_mm2 - 250.0) < 0.5:
        return 0.0015
    if abs(fy_n_per_mm2 - 415.0) < 0.5 or abs(fy_n_per_mm2 - 500.0) < 0.5:
        return 0.0012
    raise SlabContractError(
        "fy_n_per_mm2 must be one of the P8 supported grades: 250, 415, or 500 N/mm2"
    )


def _bar_area_mm2(diameter_mm: float) -> float:
    """Return the circular nominal bar area in square millimetres."""
    return math.pi * diameter_mm * diameter_mm / 4.0


@dataclass(frozen=True)
class OneWaySlabDetailingInput:
    """Accepted P7 result plus caller-provided main and distribution bars."""

    flexure_result: OneWaySlabFlexureResult
    main_bar_diameter_mm: float
    main_bar_spacing_mm: float
    distribution_bar_diameter_mm: float
    distribution_bar_spacing_mm: float

    def __post_init__(self) -> None:
        if not isinstance(self.flexure_result, OneWaySlabFlexureResult):
            raise SlabContractError(
                "flexure_result must be an accepted OneWaySlabFlexureResult"
            )
        if self.flexure_result.status not in (
            OneWaySlabFlexureStatus.FLEXURE_ONLY_PENDING_P8,
            OneWaySlabFlexureStatus.COMPLETE_WORKFLOW_CHECKS_COMPOSED,
        ):
            raise SlabContractError(
                "flexure_result must retain a recognized one-way workflow status"
            )
        object.__setattr__(
            self,
            "main_bar_diameter_mm",
            _positive_finite(self.main_bar_diameter_mm, "main_bar_diameter_mm", "mm"),
        )
        object.__setattr__(
            self,
            "main_bar_spacing_mm",
            _positive_finite(self.main_bar_spacing_mm, "main_bar_spacing_mm", "mm"),
        )
        object.__setattr__(
            self,
            "distribution_bar_diameter_mm",
            _positive_finite(
                self.distribution_bar_diameter_mm,
                "distribution_bar_diameter_mm",
                "mm",
            ),
        )
        object.__setattr__(
            self,
            "distribution_bar_spacing_mm",
            _positive_finite(
                self.distribution_bar_spacing_mm,
                "distribution_bar_spacing_mm",
                "mm",
            ),
        )


def _validate_accepted_flexure_result(result: OneWaySlabFlexureResult) -> None:
    """Fail closed unless the retained P7 state is internally consistent."""
    if result.status is not OneWaySlabFlexureStatus.FLEXURE_ONLY_PENDING_P8:
        raise SlabContractError(
            "flexure_result must have P7 FLEXURE_ONLY_PENDING_P8 status"
        )
    if not isinstance(result.input, OneWaySlabFlexureInput):
        raise SlabContractError("flexure_result must retain a OneWaySlabFlexureInput")
    geometry = result.input.geometry
    if not isinstance(geometry, SolidRectangularSlabGeometry):
        raise SlabContractError(
            "flexure_result must retain solid rectangular slab geometry"
        )
    expected_strip_width_mm = geometry.strip_width_mm or _DEFAULT_STRIP_WIDTH_MM
    if result.effective_short_span_mm != geometry.short_effective_span_mm:
        raise SlabContractError(
            "flexure_result has inconsistent effective short-span geometry"
        )
    if result.design_strip_width_mm != expected_strip_width_mm:
        raise SlabContractError("flexure_result has inconsistent design-strip geometry")
    if geometry.long_effective_span_mm / geometry.short_effective_span_mm <= 2.0:
        raise SlabContractError(
            "flexure_result geometry is outside the P8 one-way scope"
        )
    for value, field_name, unit in (
        (result.input.d_mm, "flexure_result.input.d_mm", "mm"),
        (geometry.thickness_mm, "flexure_result.geometry.thickness_mm", "mm"),
        (
            result.input.factored_area_load_kn_per_m2,
            "flexure_result.input.factored_area_load_kn_per_m2",
            "kN/m2",
        ),
        (result.input.fck_n_per_mm2, "flexure_result.input.fck_n_per_mm2", "N/mm2"),
        (result.input.fy_n_per_mm2, "flexure_result.input.fy_n_per_mm2", "N/mm2"),
        (result.line_load_kn_per_m, "flexure_result.line_load_kn_per_m", "kN/m"),
        (result.factored_moment_knm, "flexure_result.factored_moment_knm", "kN m"),
        (result.ast_required_mm2, "flexure_result.ast_required_mm2", "mm2"),
        (result.neutral_axis_depth_mm, "flexure_result.neutral_axis_depth_mm", "mm"),
        (result.limiting_moment_knm, "flexure_result.limiting_moment_knm", "kN m"),
        (
            result.effective_short_span_mm,
            "flexure_result.effective_short_span_mm",
            "mm",
        ),
        (result.design_strip_width_mm, "flexure_result.design_strip_width_mm", "mm"),
    ):
        _positive_finite(value, field_name, unit)
    if result.input.d_mm >= geometry.thickness_mm:
        raise SlabContractError("flexure_result has d_mm not less than slab thickness")
    if not _supported_fy(result.input.fy_n_per_mm2):
        raise SlabContractError(
            "fy_n_per_mm2 must be one of the P8 supported grades: 250, 415, or 500 N/mm2"
        )


@dataclass(frozen=True)
class OneWaySlabDetailingResult:
    """P8 provided-bar checks and the explicit basic Lx/d review boundary."""

    input: OneWaySlabDetailingInput
    minimum_reinforcement_ratio: float
    minimum_reinforcement_mm2: float
    main_reinforcement_required_mm2: float
    distribution_reinforcement_required_mm2: float
    main_reinforcement_provided_mm2: float
    distribution_reinforcement_provided_mm2: float
    maximum_bar_diameter_mm: float
    maximum_main_spacing_mm: float
    maximum_distribution_spacing_mm: float
    basic_span_to_depth_ratio: float
    basic_span_to_depth_limit: float
    governing_checks: tuple[OneWaySlabDetailingCheck, ...]
    detailing_adequacy: DetailingAdequacyStatus
    serviceability_status: OneWaySlabServiceabilityStatus
    review_requirement: OneWaySlabReviewRequirement
    limitations: tuple[str, ...]
    source_refs: tuple[str, ...]

    @property
    def is_detailing_adequate(self) -> bool:
        """Return whether every provided-bar detailing comparison passes."""
        return self.detailing_adequacy is DetailingAdequacyStatus.ADEQUATE


@clause("24.1", "26.3.3", "26.5.2.1")
def check_simply_supported_one_way_slab_detailing(
    detailing_input: OneWaySlabDetailingInput,
) -> OneWaySlabDetailingResult:
    """Check provided reinforcement for the bounded P7 simply supported strip.

    The serviceability outcome is deliberately a review boundary: a basic
    Lx/d ratio at or below 20 is recorded as satisfied, while a higher ratio
    requests qualified review because modification factors and direct
    deflection are outside P8.
    """
    if not isinstance(detailing_input, OneWaySlabDetailingInput):
        raise SlabContractError("detailing_input must be a OneWaySlabDetailingInput")

    _validate_accepted_flexure_result(detailing_input.flexure_result)
    flexure = detailing_input.flexure_result
    geometry = flexure.input.geometry
    strip_width_mm = flexure.design_strip_width_mm
    minimum_ratio = _minimum_reinforcement_ratio(flexure.input.fy_n_per_mm2)
    minimum_reinforcement_mm2 = minimum_ratio * strip_width_mm * geometry.thickness_mm
    main_required_mm2 = max(flexure.ast_required_mm2, minimum_reinforcement_mm2)
    distribution_required_mm2 = minimum_reinforcement_mm2
    main_provided_mm2 = (
        _bar_area_mm2(detailing_input.main_bar_diameter_mm)
        * strip_width_mm
        / detailing_input.main_bar_spacing_mm
    )
    distribution_provided_mm2 = (
        _bar_area_mm2(detailing_input.distribution_bar_diameter_mm)
        * strip_width_mm
        / detailing_input.distribution_bar_spacing_mm
    )
    maximum_bar_diameter_mm = geometry.thickness_mm / 8.0
    maximum_main_spacing_mm = min(3.0 * flexure.input.d_mm, 300.0)
    maximum_distribution_spacing_mm = min(5.0 * flexure.input.d_mm, 450.0)
    basic_span_to_depth_ratio = flexure.effective_short_span_mm / flexure.input.d_mm
    basic_span_to_depth_limit = 20.0

    checks = (
        OneWaySlabDetailingCheck(
            "P8-MAIN-STEEL-01",
            main_provided_mm2,
            main_required_mm2,
            "mm2/strip",
            ">=",
            main_provided_mm2 >= main_required_mm2,
        ),
        OneWaySlabDetailingCheck(
            "P8-DIST-STEEL-01",
            distribution_provided_mm2,
            distribution_required_mm2,
            "mm2/strip",
            ">=",
            distribution_provided_mm2 >= distribution_required_mm2,
        ),
        OneWaySlabDetailingCheck(
            "P8-MAIN-DIA-01",
            detailing_input.main_bar_diameter_mm,
            maximum_bar_diameter_mm,
            "mm",
            "<=",
            detailing_input.main_bar_diameter_mm <= maximum_bar_diameter_mm,
        ),
        OneWaySlabDetailingCheck(
            "P8-DIST-DIA-01",
            detailing_input.distribution_bar_diameter_mm,
            maximum_bar_diameter_mm,
            "mm",
            "<=",
            detailing_input.distribution_bar_diameter_mm <= maximum_bar_diameter_mm,
        ),
        OneWaySlabDetailingCheck(
            "P8-MAIN-SPACING-01",
            detailing_input.main_bar_spacing_mm,
            maximum_main_spacing_mm,
            "mm",
            "<=",
            detailing_input.main_bar_spacing_mm <= maximum_main_spacing_mm,
        ),
        OneWaySlabDetailingCheck(
            "P8-DIST-SPACING-01",
            detailing_input.distribution_bar_spacing_mm,
            maximum_distribution_spacing_mm,
            "mm",
            "<=",
            detailing_input.distribution_bar_spacing_mm
            <= maximum_distribution_spacing_mm,
        ),
    )
    detailing_adequacy = (
        DetailingAdequacyStatus.ADEQUATE
        if all(check.passed for check in checks)
        else DetailingAdequacyStatus.INADEQUATE
    )
    serviceability_status = (
        OneWaySlabServiceabilityStatus.BASIC_RATIO_SATISFIED
        if basic_span_to_depth_ratio <= basic_span_to_depth_limit
        else OneWaySlabServiceabilityStatus.QUALIFIED_REVIEW_REQUIRED
    )
    review_requirement = (
        OneWaySlabReviewRequirement.QUALIFIED_REVIEW_REQUIRED
        if serviceability_status
        is OneWaySlabServiceabilityStatus.QUALIFIED_REVIEW_REQUIRED
        else OneWaySlabReviewRequirement.NO_QUALIFIED_REVIEW_REQUIRED
    )
    return OneWaySlabDetailingResult(
        input=detailing_input,
        minimum_reinforcement_ratio=minimum_ratio,
        minimum_reinforcement_mm2=minimum_reinforcement_mm2,
        main_reinforcement_required_mm2=main_required_mm2,
        distribution_reinforcement_required_mm2=distribution_required_mm2,
        main_reinforcement_provided_mm2=main_provided_mm2,
        distribution_reinforcement_provided_mm2=distribution_provided_mm2,
        maximum_bar_diameter_mm=maximum_bar_diameter_mm,
        maximum_main_spacing_mm=maximum_main_spacing_mm,
        maximum_distribution_spacing_mm=maximum_distribution_spacing_mm,
        basic_span_to_depth_ratio=basic_span_to_depth_ratio,
        basic_span_to_depth_limit=basic_span_to_depth_limit,
        governing_checks=checks,
        detailing_adequacy=detailing_adequacy,
        serviceability_status=serviceability_status,
        review_requirement=review_requirement,
        limitations=_P8_LIMITATIONS,
        source_refs=flexure.source_refs + _P8_SOURCE_REFS,
    )
