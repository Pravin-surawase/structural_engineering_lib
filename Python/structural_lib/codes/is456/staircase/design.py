# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Structural design checks for the bounded straight-flight waist slab."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.slab.shear import (
    SlabShearInput,
    SlabShearResult,
    check_solid_slab_one_way_shear,
)
from structural_lib.codes.is456.staircase.actions import (
    StraightFlightActionResult,
    analyze_straight_flight_actions,
)
from structural_lib.codes.is456.staircase.models import (
    StaircaseContractError,
    positive_finite,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "StaircaseDesignCheck",
    "StaircaseDesignStatus",
    "StaircaseServiceabilityStatus",
    "StraightFlightDesignInput",
    "StraightFlightDesignResult",
    "design_straight_flight_staircase",
]


_SUPPORTED_FY_N_PER_MM2 = (250.0, 415.0, 500.0)
_SOURCE_REFS = (
    "IS 456:2000 Cl. 23.2.1, 26.3.3, 26.5.2.1, 38.1, 40.1 and 40.2",
    "IS 456:2000 Table 19 and Table 20",
    "NPTEL-M9L20-EX9.1",
)
_LIMITATIONS = (
    "HOLD: modification factors and direct deflection are not calculated.",
    "HOLD: crack width, development-length layout, landing torsion, and automatic bar selection are not implemented.",
    "HOLD: load generation, combinations, patterns, continuity, moment redistribution, and seismic behavior are not inferred.",
    "REVIEW LIMITATION: software verification is not professional design approval.",
)


class StaircaseDesignStatus(StrEnum):
    """Aggregate bounded design disposition."""

    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAIL = "FAIL"


class StaircaseServiceabilityStatus(StrEnum):
    """Basic simply-supported L/d disposition without invented modifiers."""

    BASIC_RATIO_SATISFIED = "basic_ratio_satisfied"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class StaircaseDesignCheck:
    """One explicit comparison with retained units."""

    check_id: str
    actual: float
    limit: float
    unit: str
    comparison: str
    passed: bool


@dataclass(frozen=True)
class StraightFlightDesignInput:
    """Accepted actions, material properties, depth, and supplied bars."""

    actions: StraightFlightActionResult
    effective_depth_mm: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float
    main_bar_diameter_mm: float
    main_bar_spacing_mm: float
    distribution_bar_diameter_mm: float
    distribution_bar_spacing_mm: float

    def __post_init__(self) -> None:
        if not isinstance(self.actions, StraightFlightActionResult):
            raise StaircaseContractError("actions must be a StraightFlightActionResult")
        for name, unit in (
            ("effective_depth_mm", "mm"),
            ("fck_n_per_mm2", "N/mm2"),
            ("fy_n_per_mm2", "N/mm2"),
            ("main_bar_diameter_mm", "mm"),
            ("main_bar_spacing_mm", "mm"),
            ("distribution_bar_diameter_mm", "mm"),
            ("distribution_bar_spacing_mm", "mm"),
        ):
            object.__setattr__(
                self,
                name,
                positive_finite(getattr(self, name), name, unit),
            )
        waist_thickness = self.actions.input.geometry.waist_thickness_mm
        if self.effective_depth_mm >= waist_thickness:
            raise StaircaseContractError(
                "effective_depth_mm must be less than waist_thickness_mm"
            )
        if not 20.0 <= self.fck_n_per_mm2 <= 40.0:
            raise StaircaseContractError(
                "fck_n_per_mm2 must be within the combined flexure/shear domain of 20 to 40 N/mm2"
            )
        if not any(
            abs(self.fy_n_per_mm2 - grade) < 0.5 for grade in _SUPPORTED_FY_N_PER_MM2
        ):
            raise StaircaseContractError(
                "fy_n_per_mm2 must be one of 250, 415, or 500 N/mm2"
            )


@dataclass(frozen=True)
class StraightFlightDesignResult:
    """Strength, supplied-bar, shear, and basic serviceability evidence."""

    input: StraightFlightDesignInput
    design_strip_width_mm: float
    factored_moment_knm_per_m: float
    factored_shear_kn_per_m: float
    limiting_moment_knm_per_m: float
    ast_required_mm2_per_m: float | None
    neutral_axis_depth_mm: float | None
    minimum_reinforcement_mm2_per_m: float
    main_reinforcement_required_mm2_per_m: float | None
    main_reinforcement_provided_mm2_per_m: float
    distribution_reinforcement_required_mm2_per_m: float
    distribution_reinforcement_provided_mm2_per_m: float
    maximum_bar_diameter_mm: float
    maximum_main_bar_spacing_mm: float
    maximum_distribution_bar_spacing_mm: float
    shear: SlabShearResult
    actual_span_to_depth_ratio: float
    basic_span_to_depth_limit: float
    serviceability_status: StaircaseServiceabilityStatus
    governing_checks: tuple[StaircaseDesignCheck, ...]
    status: StaircaseDesignStatus
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    complete_engineering_design_approved: bool = False

    @property
    def is_strength_and_detailing_satisfied(self) -> bool:
        """Return whether every non-serviceability comparison passed."""
        return all(
            check.passed
            for check in self.governing_checks
            if check.check_id != "INDIA-2C-LD-01"
        )


def _bar_area_mm2(diameter_mm: float) -> float:
    return math.pi * diameter_mm * diameter_mm / 4.0


def _minimum_reinforcement_ratio(fy_n_per_mm2: float) -> float:
    if abs(fy_n_per_mm2 - 250.0) < 0.5:
        return 0.0015
    return 0.0012


def _validate_action_integrity(actions: StraightFlightActionResult) -> None:
    """Reject a forged or internally inconsistent action carrier."""
    recomputed = analyze_straight_flight_actions(actions.input)
    for field_name in (
        "total_factored_load_kn",
        "lower_support_reaction_kn",
        "upper_support_reaction_kn",
        "maximum_factored_shear_kn_per_m",
        "maximum_factored_moment_knm_per_m",
    ):
        actual = getattr(actions, field_name)
        expected = getattr(recomputed, field_name)
        if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
            raise StaircaseContractError(
                f"actions.{field_name} is inconsistent with retained inputs"
            )


@clause("23.2.1", "26.3.3", "26.5.2.1", "38.1", "40.1", "40.2")
def design_straight_flight_staircase(
    design_input: StraightFlightDesignInput,
) -> StraightFlightDesignResult:
    """Check one metre of the accepted straight-flight waist-slab member."""
    if not isinstance(design_input, StraightFlightDesignInput):
        raise StaircaseContractError("design_input must be a StraightFlightDesignInput")
    _validate_action_integrity(design_input.actions)

    strip_width_mm = 1000.0
    actions = design_input.actions
    geometry = actions.input.geometry
    moment_knm_per_m = actions.maximum_factored_moment_knm_per_m
    shear_kn_per_m = actions.maximum_factored_shear_kn_per_m
    xu_max_over_d = materials.get_xu_max_d(design_input.fy_n_per_mm2)
    limiting_moment_knm = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * design_input.fck_n_per_mm2
        * strip_width_mm
        * design_input.effective_depth_mm
        * design_input.effective_depth_mm
        / 1_000_000.0
    )
    flexure_capacity_satisfied = moment_knm_per_m <= limiting_moment_knm
    ast_required: float | None = None
    neutral_axis_depth: float | None = None
    if flexure_capacity_satisfied:
        ast_required, neutral_axis_depth = calculate_ast_from_rectangular_stress_block(
            b_mm=strip_width_mm,
            d_mm=design_input.effective_depth_mm,
            factored_moment_knm=moment_knm_per_m,
            fck_n_per_mm2=design_input.fck_n_per_mm2,
            fy_n_per_mm2=design_input.fy_n_per_mm2,
        )

    minimum_reinforcement = (
        _minimum_reinforcement_ratio(design_input.fy_n_per_mm2)
        * strip_width_mm
        * geometry.waist_thickness_mm
    )
    main_required = (
        max(ast_required, minimum_reinforcement) if ast_required is not None else None
    )
    main_provided = (
        _bar_area_mm2(design_input.main_bar_diameter_mm)
        * strip_width_mm
        / design_input.main_bar_spacing_mm
    )
    distribution_provided = (
        _bar_area_mm2(design_input.distribution_bar_diameter_mm)
        * strip_width_mm
        / design_input.distribution_bar_spacing_mm
    )
    maximum_bar_diameter = geometry.waist_thickness_mm / 8.0
    maximum_main_spacing = min(3.0 * design_input.effective_depth_mm, 300.0)
    maximum_distribution_spacing = min(5.0 * design_input.effective_depth_mm, 450.0)
    shear_result = check_solid_slab_one_way_shear(
        SlabShearInput(
            factored_shear_kn=shear_kn_per_m,
            strip_width_mm=strip_width_mm,
            effective_depth_mm=design_input.effective_depth_mm,
            overall_depth_mm=geometry.waist_thickness_mm,
            fck_n_per_mm2=design_input.fck_n_per_mm2,
            tension_reinforcement_mm2=main_provided,
            uniformly_distributed_load_only=True,
            beam_or_wall_supported=True,
        )
    )
    actual_span_to_depth = (
        actions.geometry.effective_span_mm / design_input.effective_depth_mm
    )
    basic_span_to_depth_limit = 20.0
    serviceability_satisfied = actual_span_to_depth <= basic_span_to_depth_limit
    serviceability_status = (
        StaircaseServiceabilityStatus.BASIC_RATIO_SATISFIED
        if serviceability_satisfied
        else StaircaseServiceabilityStatus.REVIEW_REQUIRED
    )

    main_steel_satisfied = main_required is not None and main_provided >= main_required
    checks = (
        StaircaseDesignCheck(
            "INDIA-2C-MU-01",
            moment_knm_per_m,
            limiting_moment_knm,
            "kNm/m",
            "<=",
            flexure_capacity_satisfied,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-MAIN-STEEL-01",
            main_provided,
            main_required if main_required is not None else math.inf,
            "mm2/m",
            ">=",
            main_steel_satisfied,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-DIST-STEEL-01",
            distribution_provided,
            minimum_reinforcement,
            "mm2/m",
            ">=",
            distribution_provided >= minimum_reinforcement,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-MAIN-DIA-01",
            design_input.main_bar_diameter_mm,
            maximum_bar_diameter,
            "mm",
            "<=",
            design_input.main_bar_diameter_mm <= maximum_bar_diameter,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-DIST-DIA-01",
            design_input.distribution_bar_diameter_mm,
            maximum_bar_diameter,
            "mm",
            "<=",
            design_input.distribution_bar_diameter_mm <= maximum_bar_diameter,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-MAIN-SPACING-01",
            design_input.main_bar_spacing_mm,
            maximum_main_spacing,
            "mm",
            "<=",
            design_input.main_bar_spacing_mm <= maximum_main_spacing,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-DIST-SPACING-01",
            design_input.distribution_bar_spacing_mm,
            maximum_distribution_spacing,
            "mm",
            "<=",
            design_input.distribution_bar_spacing_mm <= maximum_distribution_spacing,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-SHEAR-01",
            shear_result.tau_v_n_per_mm2,
            shear_result.design_tau_c_n_per_mm2,
            "N/mm2",
            "<=",
            shear_result.is_safe_without_shear_reinforcement,
        ),
        StaircaseDesignCheck(
            "INDIA-2C-LD-01",
            actual_span_to_depth,
            basic_span_to_depth_limit,
            "ratio",
            "<=",
            serviceability_satisfied,
        ),
    )
    strength_and_detailing_satisfied = all(
        check.passed for check in checks if check.check_id != "INDIA-2C-LD-01"
    )
    if not strength_and_detailing_satisfied:
        status = StaircaseDesignStatus.FAIL
    elif not serviceability_satisfied:
        status = StaircaseDesignStatus.REVIEW_REQUIRED
    else:
        status = StaircaseDesignStatus.PASS

    return StraightFlightDesignResult(
        input=design_input,
        design_strip_width_mm=strip_width_mm,
        factored_moment_knm_per_m=moment_knm_per_m,
        factored_shear_kn_per_m=shear_kn_per_m,
        limiting_moment_knm_per_m=limiting_moment_knm,
        ast_required_mm2_per_m=ast_required,
        neutral_axis_depth_mm=neutral_axis_depth,
        minimum_reinforcement_mm2_per_m=minimum_reinforcement,
        main_reinforcement_required_mm2_per_m=main_required,
        main_reinforcement_provided_mm2_per_m=main_provided,
        distribution_reinforcement_required_mm2_per_m=minimum_reinforcement,
        distribution_reinforcement_provided_mm2_per_m=distribution_provided,
        maximum_bar_diameter_mm=maximum_bar_diameter,
        maximum_main_bar_spacing_mm=maximum_main_spacing,
        maximum_distribution_bar_spacing_mm=maximum_distribution_spacing,
        shear=shear_result,
        actual_span_to_depth_ratio=actual_span_to_depth,
        basic_span_to_depth_limit=basic_span_to_depth_limit,
        serviceability_status=serviceability_status,
        governing_checks=checks,
        status=status,
        source_refs=_SOURCE_REFS,
        limitations=_LIMITATIONS,
    )
