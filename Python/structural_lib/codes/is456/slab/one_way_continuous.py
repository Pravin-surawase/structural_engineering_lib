# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Coefficient-method actions and flexure for continuous one-way slab strips."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.slab.classification import (
    classify_solid_rectangular_slab,
)
from structural_lib.codes.is456.slab.coefficients import (
    OneWayContinuousCoefficientSet,
)
from structural_lib.codes.is456.slab.models import (
    SlabClassification,
    SlabContractError,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "ContinuousOneWaySlabActionResult",
    "ContinuousOneWaySlabInput",
    "ContinuousOneWaySlabResult",
    "design_continuous_one_way_slab_flexure",
]


def _positive(value: float, name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise SlabContractError(f"{name} must be finite and positive in {unit}")
    return normalized


@dataclass(frozen=True)
class ContinuousOneWaySlabInput:
    geometry: SolidRectangularSlabGeometry
    d_mm: float
    factored_area_load_kn_per_m2: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float
    coefficients: OneWayContinuousCoefficientSet
    number_of_spans: int
    maximum_span_variation_percent: float
    uniform_cross_section_acknowledged: bool
    substantially_uniform_load_acknowledged: bool
    redistribution_applied: bool

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, SolidRectangularSlabGeometry):
            raise SlabContractError("geometry must be SolidRectangularSlabGeometry")
        if not isinstance(self.coefficients, OneWayContinuousCoefficientSet):
            raise SlabContractError(
                "coefficients must be OneWayContinuousCoefficientSet"
            )
        for name, unit in (
            ("d_mm", "mm"),
            ("factored_area_load_kn_per_m2", "kN/m2"),
            ("fck_n_per_mm2", "N/mm2"),
            ("fy_n_per_mm2", "N/mm2"),
        ):
            object.__setattr__(self, name, _positive(getattr(self, name), name, unit))
        if self.d_mm >= self.geometry.thickness_mm:
            raise SlabContractError("d_mm must be less than slab thickness")
        if not isinstance(self.number_of_spans, int) or isinstance(
            self.number_of_spans, bool
        ):
            raise SlabContractError("number_of_spans must be an integer")
        if self.number_of_spans < 3:
            raise SlabContractError("coefficient method requires at least three spans")
        variation = float(self.maximum_span_variation_percent)
        if not math.isfinite(variation) or variation < 0.0 or variation > 15.0:
            raise SlabContractError(
                "maximum_span_variation_percent must be between 0 and 15"
            )
        object.__setattr__(self, "maximum_span_variation_percent", variation)
        if self.uniform_cross_section_acknowledged is not True:
            raise SlabContractError(
                "uniform_cross_section_acknowledged must be explicitly True"
            )
        if self.substantially_uniform_load_acknowledged is not True:
            raise SlabContractError(
                "substantially_uniform_load_acknowledged must be explicitly True"
            )
        if self.redistribution_applied is not False:
            raise SlabContractError(
                "redistribution_applied must be explicitly False for coefficient actions"
            )
        if not 20.0 <= self.fck_n_per_mm2 <= 80.0:
            raise SlabContractError("fck_n_per_mm2 must be between 20 and 80")
        try:
            materials.get_xu_max_d(self.fy_n_per_mm2)
        except Exception as exc:
            raise SlabContractError("fy_n_per_mm2 must be 250, 415, or 500") from exc


@dataclass(frozen=True)
class ContinuousOneWaySlabActionResult:
    action_id: str
    location: str
    coefficient: float
    factored_moment_knm_per_m: float
    ast_required_mm2_per_m: float
    neutral_axis_depth_mm: float
    limiting_moment_knm_per_m: float


@dataclass(frozen=True)
class ContinuousOneWaySlabResult:
    input: ContinuousOneWaySlabInput
    line_load_kn_per_m: float
    positive_midspan: ContinuousOneWaySlabActionResult
    negative_support: ContinuousOneWaySlabActionResult
    factored_shear_kn_per_m: float
    coefficient_correctness_verified_by_library: bool
    complete_engineering_design_approved: bool
    source_refs: tuple[str, ...]


def _moment_action(
    *,
    action_id: str,
    location: str,
    coefficient: float,
    line_load_kn_per_m: float,
    span_m: float,
    strip_width_mm: float,
    d_mm: float,
    fck: float,
    fy: float,
) -> ContinuousOneWaySlabActionResult:
    moment = coefficient * line_load_kn_per_m * span_m**2
    xu_max_over_d = materials.get_xu_max_d(fy)
    limiting = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * fck
        * strip_width_mm
        * d_mm**2
        / 1_000_000.0
    )
    if moment > limiting:
        raise SlabContractError(
            f"{action_id} exceeds singly reinforced rectangular capacity"
        )
    ast, xu = calculate_ast_from_rectangular_stress_block(
        b_mm=strip_width_mm,
        d_mm=d_mm,
        factored_moment_knm=moment,
        fck_n_per_mm2=fck,
        fy_n_per_mm2=fy,
    )
    return ContinuousOneWaySlabActionResult(
        action_id=action_id,
        location=location,
        coefficient=coefficient,
        factored_moment_knm_per_m=moment,
        ast_required_mm2_per_m=ast,
        neutral_axis_depth_mm=xu,
        limiting_moment_knm_per_m=limiting,
    )


@clause("24.1", "38.1")
def design_continuous_one_way_slab_flexure(
    design_input: ContinuousOneWaySlabInput,
) -> ContinuousOneWaySlabResult:
    """Produce labeled coefficient actions without redistribution or inference."""
    if not isinstance(design_input, ContinuousOneWaySlabInput):
        raise SlabContractError("design_input must be ContinuousOneWaySlabInput")
    classification = classify_solid_rectangular_slab(design_input.geometry)
    if classification.classification is not SlabClassification.ONE_WAY:
        raise SlabContractError(
            "continuous one-way route requires Ly/Lx greater than 2"
        )
    strip_width = design_input.geometry.strip_width_mm or 1000.0
    line_load = design_input.factored_area_load_kn_per_m2 * strip_width / 1000.0
    span_m = design_input.geometry.short_effective_span_mm / 1000.0
    positive = _moment_action(
        action_id="continuous_positive_midspan",
        location="midspan_bottom",
        coefficient=design_input.coefficients.positive_midspan,
        line_load_kn_per_m=line_load,
        span_m=span_m,
        strip_width_mm=strip_width,
        d_mm=design_input.d_mm,
        fck=design_input.fck_n_per_mm2,
        fy=design_input.fy_n_per_mm2,
    )
    negative = _moment_action(
        action_id="continuous_negative_support",
        location="continuous_support_top",
        coefficient=design_input.coefficients.negative_support,
        line_load_kn_per_m=line_load,
        span_m=span_m,
        strip_width_mm=strip_width,
        d_mm=design_input.d_mm,
        fck=design_input.fck_n_per_mm2,
        fy=design_input.fy_n_per_mm2,
    )
    return ContinuousOneWaySlabResult(
        input=design_input,
        line_load_kn_per_m=line_load,
        positive_midspan=positive,
        negative_support=negative,
        factored_shear_kn_per_m=(
            design_input.coefficients.shear_support * line_load * span_m
        ),
        coefficient_correctness_verified_by_library=(
            design_input.coefficients.verified_by_library
        ),
        complete_engineering_design_approved=False,
        source_refs=(
            "IS 456:2000 Cl. 22.5",
            design_input.coefficients.source_reference,
            design_input.coefficients.qualified_acceptance_reference,
        ),
    )
