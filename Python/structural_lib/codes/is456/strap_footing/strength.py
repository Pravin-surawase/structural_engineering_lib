# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strength and detailing checks for the bounded property-line strap."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.beam.detailing import get_bond_stress
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.strap_footing.analysis import (
    StrapFootingAnalysisResult,
    StrapFootingTensionFace,
    analyze_property_line_strap_footing,
)
from structural_lib.codes.is456.strap_footing.models import (
    StrapFootingContractError,
    StrapFootingDesignInput,
)
from structural_lib.codes.is456.tables import get_tc_max_value, get_tc_value
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "StrapFootingDesignDisposition",
    "StrapFootingFlexureResult",
    "StrapFootingShearResult",
    "StrapFootingSideFaceResult",
    "StrapFootingStrengthResult",
    "check_property_line_strap_footing_strength",
]


_SOURCE_REFS = (
    "IS456-2000-A5:sha256:964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
    "IS456-AMD6-2024:sha256:4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881",
    "NPTEL-AFE-C3-STRAP Section 3.6.1 and Fig. 3.2",
    "INDIA-2-STRAP-HAND-01",
)
_CLAUSE_REFS = (
    "IS 456:2000 Cl. 26.2.1, 26.2.1.1, 26.3.2 and 26.4",
    "IS 456:2000 Cl. 26.5.1.1, 26.5.1.3, 26.5.1.5 and 26.5.1.6",
    "IS 456:2000 Cl. 38.1 and Annex G-1.1",
    "IS 456:2000 Cl. 40.1, 40.2 and 40.4; Tables 19 and 20",
)
_LIMITATIONS = (
    "Only the G0-frozen property-line two-footing equal-pressure system is represented.",
    "Footing slabs, transfer regions, soil capacity, settlement and connections remain externally verified.",
    "No coated, bundled, spliced, curtailed or automatically selected reinforcement.",
    "Vertical closed stirrups and straight anchorage into both footings only.",
    "Qualified engineering review is required; software output is not professional approval.",
)
_SIDE_FACE_RATIO_TOTAL = 0.001
_SIDE_FACE_DEPTH_THRESHOLD_MM = 750.0
_MAX_SIDE_FACE_SPACING_MM = 300.0


class StrapFootingDesignDisposition(StrEnum):
    """Aggregate outcomes admitted by the bounded strength workflow."""

    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"


@dataclass(frozen=True)
class StrapFootingFlexureResult:
    """Exact stress-block, minimum steel, spacing, cover and anchorage checks."""

    governing_tension_face: StrapFootingTensionFace
    factored_moment_demand_kn_m: float
    limiting_singly_reinforced_moment_kn_m: float
    exact_flexural_steel_required_mm2: float | None
    exact_neutral_axis_depth_mm: float | None
    beam_minimum_steel_required_mm2: float
    top_steel_required_mm2: float | None
    bottom_steel_required_mm2: float | None
    top_steel_provided_mm2: float
    bottom_steel_provided_mm2: float
    top_neutral_axis_depth_mm: float
    bottom_neutral_axis_depth_mm: float
    top_moment_capacity_kn_m: float
    bottom_moment_capacity_kn_m: float
    top_clear_spacing_mm: float
    bottom_clear_spacing_mm: float
    minimum_top_clear_spacing_mm: float
    minimum_bottom_clear_spacing_mm: float
    nominal_cover_mm: float
    required_nominal_cover_mm: float
    tension_design_bond_stress_nmm2: float
    top_development_length_required_mm: float
    bottom_development_length_required_mm: float
    top_anchorage_exterior_available_mm: float
    top_anchorage_interior_available_mm: float
    bottom_anchorage_exterior_available_mm: float
    bottom_anchorage_interior_available_mm: float
    singly_reinforced_capacity_is_sufficient: bool
    top_area_is_safe: bool
    bottom_area_is_safe: bool
    top_section_is_under_reinforced: bool
    bottom_section_is_under_reinforced: bool
    top_clear_spacing_is_safe: bool
    bottom_clear_spacing_is_safe: bool
    nominal_cover_is_safe: bool
    top_anchorage_is_safe: bool
    bottom_anchorage_is_safe: bool
    is_safe: bool


@dataclass(frozen=True)
class StrapFootingSideFaceResult:
    """Side-face steel and vertical spacing check for the deep strap web."""

    required: bool
    required_total_area_mm2: float
    required_area_each_face_mm2: float
    provided_area_each_face_mm2: float
    provided_total_area_mm2: float
    provided_vertical_spacing_mm: float
    maximum_vertical_spacing_mm: float
    area_is_safe: bool
    spacing_is_safe: bool
    is_safe: bool


@dataclass(frozen=True)
class StrapFootingShearResult:
    """Table 19/20 shear and supplied vertical-stirrup check."""

    factored_shear_demand_kn: float
    tension_reinforcement_area_mm2: float
    tension_reinforcement_percent: float
    table_19_lookup_reinforcement_percent: float
    nominal_shear_stress_nmm2: float
    concrete_design_shear_strength_nmm2: float
    maximum_design_shear_stress_nmm2: float
    concrete_shear_capacity_kn: float
    stirrup_carried_shear_required_kn: float
    stirrup_area_provided_mm2: float
    minimum_stirrup_area_at_provided_spacing_mm2: float
    stirrup_shear_capacity_provided_kn: float
    provided_stirrup_spacing_mm: float
    maximum_stirrup_spacing_mm: float
    maximum_stress_is_safe: bool
    minimum_stirrup_area_is_safe: bool
    stirrup_strength_is_safe: bool
    stirrup_spacing_is_safe: bool
    is_safe: bool


@dataclass(frozen=True)
class StrapFootingStrengthResult:
    """Composed service, strength and detailing disposition."""

    input: StrapFootingDesignInput
    actions: StrapFootingAnalysisResult
    flexure: StrapFootingFlexureResult
    side_face: StrapFootingSideFaceResult
    shear: StrapFootingShearResult
    disposition: StrapFootingDesignDisposition
    reasons: tuple[str, ...]
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    qualified_review_required: bool = True
    complete_engineering_approval: bool = False

    @property
    def is_safe_within_supported_scope(self) -> bool:
        """Return whether every represented comparison passes."""

        return self.disposition is StrapFootingDesignDisposition.PASS


def _bar_area_mm2(diameter_mm: float) -> float:
    return math.pi * diameter_mm**2 / 4.0


def _section_capacity(
    *,
    steel_area_mm2: float,
    width_mm: float,
    effective_depth_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
) -> tuple[float, float]:
    neutral_axis = 0.87 * fy_nmm2 * steel_area_mm2 / (0.36 * fck_nmm2 * width_mm)
    capacity = (
        0.36
        * fck_nmm2
        * width_mm
        * neutral_axis
        * (effective_depth_mm - 0.42 * neutral_axis)
        / 1_000_000.0
    )
    return neutral_axis, capacity


def _clear_spacing(
    *,
    width_mm: float,
    count: int,
    diameter_mm: float,
    cover_mm: float,
    stirrup_diameter_mm: float,
) -> float:
    return (width_mm - 2.0 * (cover_mm + stirrup_diameter_mm) - count * diameter_mm) / (
        count - 1
    )


def _development_length(
    *, diameter_mm: float, fck_nmm2: float, fy_nmm2: float
) -> tuple[float, float]:
    bond_stress = get_bond_stress(fck_nmm2, "deformed")
    return bond_stress, diameter_mm * 0.87 * fy_nmm2 / (4.0 * bond_stress)


def _check_flexure(
    footing_input: StrapFootingDesignInput, actions: StrapFootingAnalysisResult
) -> StrapFootingFlexureResult:
    geometry = footing_input.analysis.geometry
    material = footing_input.material
    reinforcement = footing_input.reinforcement
    width = geometry.strap_width_mm
    depth = geometry.strap_effective_depth_mm
    fck = material.strap_concrete_grade_nmm2
    fy = material.steel_grade_nmm2
    demand = actions.factored_clear_strap.governing_moment_demand_kn_m
    tension_face = actions.factored_clear_strap.governing_tension_face
    xu_max = materials.get_xu_max_d(fy) * depth
    limiting_moment = (
        0.36 * fck * width * xu_max * (depth - 0.42 * xu_max) / 1_000_000.0
    )
    capacity_is_sufficient = demand <= limiting_moment
    required_flexural: float | None = None
    required_xu: float | None = None
    if capacity_is_sufficient and demand > 0.0:
        required_flexural, required_xu = calculate_ast_from_rectangular_stress_block(
            b_mm=width,
            d_mm=depth,
            factored_moment_knm=demand,
            fck_n_per_mm2=fck,
            fy_n_per_mm2=fy,
        )
    minimum_area = 0.85 * width * depth / fy
    top_required = minimum_area
    bottom_required = minimum_area
    if required_flexural is not None:
        if tension_face is StrapFootingTensionFace.TOP:
            top_required = max(top_required, required_flexural)
        elif tension_face is StrapFootingTensionFace.BOTTOM:
            bottom_required = max(bottom_required, required_flexural)
    if not capacity_is_sufficient:
        top_required_result: float | None = None
        bottom_required_result: float | None = None
    else:
        top_required_result = top_required
        bottom_required_result = bottom_required

    top_area = reinforcement.top_bar_count * _bar_area_mm2(
        reinforcement.top_bar_diameter_mm
    )
    bottom_area = reinforcement.bottom_bar_count * _bar_area_mm2(
        reinforcement.bottom_bar_diameter_mm
    )
    top_xu, top_capacity = _section_capacity(
        steel_area_mm2=top_area,
        width_mm=width,
        effective_depth_mm=depth,
        fck_nmm2=fck,
        fy_nmm2=fy,
    )
    bottom_xu, bottom_capacity = _section_capacity(
        steel_area_mm2=bottom_area,
        width_mm=width,
        effective_depth_mm=depth,
        fck_nmm2=fck,
        fy_nmm2=fy,
    )
    top_clear = _clear_spacing(
        width_mm=width,
        count=reinforcement.top_bar_count,
        diameter_mm=reinforcement.top_bar_diameter_mm,
        cover_mm=reinforcement.nominal_cover_mm,
        stirrup_diameter_mm=reinforcement.stirrup_diameter_mm,
    )
    bottom_clear = _clear_spacing(
        width_mm=width,
        count=reinforcement.bottom_bar_count,
        diameter_mm=reinforcement.bottom_bar_diameter_mm,
        cover_mm=reinforcement.nominal_cover_mm,
        stirrup_diameter_mm=reinforcement.stirrup_diameter_mm,
    )
    top_min_clear = max(
        reinforcement.top_bar_diameter_mm,
        reinforcement.maximum_aggregate_size_mm + 5.0,
        25.0,
    )
    bottom_min_clear = max(
        reinforcement.bottom_bar_diameter_mm,
        reinforcement.maximum_aggregate_size_mm + 5.0,
        25.0,
    )
    bond_stress, top_ld = _development_length(
        diameter_mm=reinforcement.top_bar_diameter_mm,
        fck_nmm2=fck,
        fy_nmm2=fy,
    )
    _, bottom_ld = _development_length(
        diameter_mm=reinforcement.bottom_bar_diameter_mm,
        fck_nmm2=fck,
        fy_nmm2=fy,
    )
    top_area_safe = top_required_result is not None and top_area >= top_required_result
    bottom_area_safe = (
        bottom_required_result is not None and bottom_area >= bottom_required_result
    )
    top_under_reinforced = top_xu <= xu_max
    bottom_under_reinforced = bottom_xu <= xu_max
    top_anchor_safe = (
        min(
            reinforcement.available_top_anchorage_exterior_mm,
            reinforcement.available_top_anchorage_interior_mm,
        )
        >= top_ld
    )
    bottom_anchor_safe = (
        min(
            reinforcement.available_bottom_anchorage_exterior_mm,
            reinforcement.available_bottom_anchorage_interior_mm,
        )
        >= bottom_ld
    )
    cover_safe = (
        reinforcement.nominal_cover_mm >= reinforcement.required_nominal_cover_mm
    )
    top_spacing_safe = top_clear >= top_min_clear
    bottom_spacing_safe = bottom_clear >= bottom_min_clear
    is_safe = all(
        (
            capacity_is_sufficient,
            top_area_safe,
            bottom_area_safe,
            top_under_reinforced,
            bottom_under_reinforced,
            top_spacing_safe,
            bottom_spacing_safe,
            cover_safe,
            top_anchor_safe,
            bottom_anchor_safe,
        )
    )
    return StrapFootingFlexureResult(
        governing_tension_face=tension_face,
        factored_moment_demand_kn_m=demand,
        limiting_singly_reinforced_moment_kn_m=limiting_moment,
        exact_flexural_steel_required_mm2=required_flexural,
        exact_neutral_axis_depth_mm=required_xu,
        beam_minimum_steel_required_mm2=minimum_area,
        top_steel_required_mm2=top_required_result,
        bottom_steel_required_mm2=bottom_required_result,
        top_steel_provided_mm2=top_area,
        bottom_steel_provided_mm2=bottom_area,
        top_neutral_axis_depth_mm=top_xu,
        bottom_neutral_axis_depth_mm=bottom_xu,
        top_moment_capacity_kn_m=top_capacity,
        bottom_moment_capacity_kn_m=bottom_capacity,
        top_clear_spacing_mm=top_clear,
        bottom_clear_spacing_mm=bottom_clear,
        minimum_top_clear_spacing_mm=top_min_clear,
        minimum_bottom_clear_spacing_mm=bottom_min_clear,
        nominal_cover_mm=reinforcement.nominal_cover_mm,
        required_nominal_cover_mm=reinforcement.required_nominal_cover_mm,
        tension_design_bond_stress_nmm2=bond_stress,
        top_development_length_required_mm=top_ld,
        bottom_development_length_required_mm=bottom_ld,
        top_anchorage_exterior_available_mm=(
            reinforcement.available_top_anchorage_exterior_mm
        ),
        top_anchorage_interior_available_mm=(
            reinforcement.available_top_anchorage_interior_mm
        ),
        bottom_anchorage_exterior_available_mm=(
            reinforcement.available_bottom_anchorage_exterior_mm
        ),
        bottom_anchorage_interior_available_mm=(
            reinforcement.available_bottom_anchorage_interior_mm
        ),
        singly_reinforced_capacity_is_sufficient=capacity_is_sufficient,
        top_area_is_safe=top_area_safe,
        bottom_area_is_safe=bottom_area_safe,
        top_section_is_under_reinforced=top_under_reinforced,
        bottom_section_is_under_reinforced=bottom_under_reinforced,
        top_clear_spacing_is_safe=top_spacing_safe,
        bottom_clear_spacing_is_safe=bottom_spacing_safe,
        nominal_cover_is_safe=cover_safe,
        top_anchorage_is_safe=top_anchor_safe,
        bottom_anchorage_is_safe=bottom_anchor_safe,
        is_safe=is_safe,
    )


def _check_side_face(
    footing_input: StrapFootingDesignInput,
) -> StrapFootingSideFaceResult:
    geometry = footing_input.analysis.geometry
    reinforcement = footing_input.reinforcement
    required = geometry.strap_overall_depth_mm > _SIDE_FACE_DEPTH_THRESHOLD_MM
    required_total = (
        _SIDE_FACE_RATIO_TOTAL
        * geometry.strap_width_mm
        * geometry.strap_overall_depth_mm
        if required
        else 0.0
    )
    required_each = required_total / 2.0
    provided_each = reinforcement.side_face_bar_count_each_face * _bar_area_mm2(
        reinforcement.side_face_bar_diameter_mm
    )
    area_safe = provided_each >= required_each
    spacing_safe = (
        not required
        or reinforcement.side_face_vertical_spacing_mm <= _MAX_SIDE_FACE_SPACING_MM
    )
    return StrapFootingSideFaceResult(
        required=required,
        required_total_area_mm2=required_total,
        required_area_each_face_mm2=required_each,
        provided_area_each_face_mm2=provided_each,
        provided_total_area_mm2=2.0 * provided_each,
        provided_vertical_spacing_mm=reinforcement.side_face_vertical_spacing_mm,
        maximum_vertical_spacing_mm=(_MAX_SIDE_FACE_SPACING_MM if required else 0.0),
        area_is_safe=area_safe,
        spacing_is_safe=spacing_safe,
        is_safe=area_safe and spacing_safe,
    )


def _check_shear(
    footing_input: StrapFootingDesignInput,
    actions: StrapFootingAnalysisResult,
    flexure: StrapFootingFlexureResult,
) -> StrapFootingShearResult:
    geometry = footing_input.analysis.geometry
    material = footing_input.material
    reinforcement = footing_input.reinforcement
    width = geometry.strap_width_mm
    depth = geometry.strap_effective_depth_mm
    fy = material.steel_grade_nmm2
    fck = material.strap_concrete_grade_nmm2
    demand = actions.factored_clear_strap.governing_shear_demand_kn
    tension_area = (
        flexure.top_steel_provided_mm2
        if actions.factored_clear_strap.governing_tension_face
        is StrapFootingTensionFace.TOP
        else flexure.bottom_steel_provided_mm2
    )
    steel_percent = 100.0 * tension_area / (width * depth)
    lookup_percent = min(max(steel_percent, 0.15), 3.0)
    tau_v = demand * 1000.0 / (width * depth)
    tau_c = get_tc_value(fck, lookup_percent)
    tau_c_max = get_tc_max_value(fck)
    concrete_capacity = tau_c * width * depth / 1000.0
    required_stirrup_shear = max(demand - concrete_capacity, 0.0)
    stirrup_area = reinforcement.stirrup_leg_count * _bar_area_mm2(
        reinforcement.stirrup_diameter_mm
    )
    minimum_area = 0.4 * width * reinforcement.stirrup_spacing_mm / (0.87 * fy)
    provided_capacity = (
        0.87 * fy * stirrup_area * depth / reinforcement.stirrup_spacing_mm / 1000.0
    )
    maximum_spacing = min(0.75 * depth, 300.0)
    maximum_safe = tau_v <= tau_c_max
    minimum_safe = stirrup_area >= minimum_area
    strength_safe = provided_capacity >= required_stirrup_shear
    spacing_safe = reinforcement.stirrup_spacing_mm <= maximum_spacing
    return StrapFootingShearResult(
        factored_shear_demand_kn=demand,
        tension_reinforcement_area_mm2=tension_area,
        tension_reinforcement_percent=steel_percent,
        table_19_lookup_reinforcement_percent=lookup_percent,
        nominal_shear_stress_nmm2=tau_v,
        concrete_design_shear_strength_nmm2=tau_c,
        maximum_design_shear_stress_nmm2=tau_c_max,
        concrete_shear_capacity_kn=concrete_capacity,
        stirrup_carried_shear_required_kn=required_stirrup_shear,
        stirrup_area_provided_mm2=stirrup_area,
        minimum_stirrup_area_at_provided_spacing_mm2=minimum_area,
        stirrup_shear_capacity_provided_kn=provided_capacity,
        provided_stirrup_spacing_mm=reinforcement.stirrup_spacing_mm,
        maximum_stirrup_spacing_mm=maximum_spacing,
        maximum_stress_is_safe=maximum_safe,
        minimum_stirrup_area_is_safe=minimum_safe,
        stirrup_strength_is_safe=strength_safe,
        stirrup_spacing_is_safe=spacing_safe,
        is_safe=all((maximum_safe, minimum_safe, strength_safe, spacing_safe)),
    )


@clause(
    "26.2.1",
    "26.2.1.1",
    "26.3.2",
    "26.4",
    "26.5.1.1",
    "26.5.1.3",
    "26.5.1.5",
    "26.5.1.6",
    "38.1",
    "G-1.1",
    "40.1",
    "40.2",
    "40.4",
)
def check_property_line_strap_footing_strength(
    footing_input: StrapFootingDesignInput,
) -> StrapFootingStrengthResult:
    """Check the G0-frozen strap reinforcement and detailing schedule.

    Valid but inadequate provision returns ``FAIL``. Inputs outside the frozen
    geometry, action, material, or detailing contract raise the typed contract
    error without producing a disposition.
    """

    if not isinstance(footing_input, StrapFootingDesignInput):
        raise StrapFootingContractError(
            "footing_input must be a StrapFootingDesignInput"
        )
    actions = analyze_property_line_strap_footing(footing_input.analysis)
    flexure = _check_flexure(footing_input, actions)
    side_face = _check_side_face(footing_input)
    shear = _check_shear(footing_input, actions, flexure)
    reasons: list[str] = []
    if not actions.gross_service_bearing_within_allowable:
        reasons.append("Approved gross service bearing pressure is exceeded.")
    if not flexure.is_safe:
        reasons.append("Supplied longitudinal flexure/detailing is inadequate.")
    if not side_face.is_safe:
        reasons.append("Supplied side-face reinforcement is inadequate.")
    if not shear.is_safe:
        reasons.append("Supplied vertical shear reinforcement is inadequate.")
    if not reasons:
        reasons.append(
            "Every represented service, strength and detailing check passes."
        )
    disposition = (
        StrapFootingDesignDisposition.PASS
        if actions.gross_service_bearing_within_allowable
        and flexure.is_safe
        and side_face.is_safe
        and shear.is_safe
        else StrapFootingDesignDisposition.FAIL
    )
    return StrapFootingStrengthResult(
        input=footing_input,
        actions=actions,
        flexure=flexure,
        side_face=side_face,
        shear=shear,
        disposition=disposition,
        reasons=tuple(reasons),
        clause_refs=_CLAUSE_REFS,
        source_refs=_SOURCE_REFS
        + (
            footing_input.material.material_basis_reference,
            footing_input.reinforcement.detailing_basis_reference,
            footing_input.reinforcement.durability_basis_reference,
        ),
        limitations=_LIMITATIONS,
    )
