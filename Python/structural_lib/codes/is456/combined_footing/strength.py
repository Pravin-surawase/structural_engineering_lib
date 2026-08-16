# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strength and detailing checks for the bounded combined-footing case."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.beam.detailing import get_bond_stress
from structural_lib.codes.is456.combined_footing.analysis import (
    CombinedFootingActionResult,
    analyze_symmetric_combined_footing,
)
from structural_lib.codes.is456.combined_footing.models import (
    CombinedFootingContractError,
    CombinedFootingDesignInput,
)
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.tables import get_tc_value
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "CombinedFootingDesignDisposition",
    "CombinedFootingFlexureResult",
    "CombinedFootingLoadTransferResult",
    "CombinedFootingOneWayShearResult",
    "CombinedFootingPunchingResult",
    "CombinedFootingStrengthResult",
    "check_symmetric_combined_footing_strength",
]


_SOURCE_REFS = (
    "IS456-2000-A5:sha256:964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
    "IS456-AMD6-2024:sha256:4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881",
    "NPTEL-AFE-C3 Sections 3.7, 3.8 and 3.14",
    "INDIA-2-COMBINED-HAND-01",
)
_CLAUSE_REFS = (
    "IS 456:2000 Cl. 26.2.1, 26.2.1.1, 26.3.2 and 26.3.3",
    "IS 456:2000 Cl. 26.4.2.2, 26.5.2.1 and 26.5.2.2",
    "IS 456:2000 Cl. 31.6.1, 31.6.2.1 and 31.6.3.1",
    "IS 456:2000 Cl. 34.1, 34.2.3.1, 34.2.4.1 and 34.2.4.3",
    "IS 456:2000 Cl. 34.3, 34.4, 34.4.1-34.4.3 and 34.5.1",
    "IS 456:2000 Cl. 38.1 and Annex G-1.1; Cl. 40.1 and 40.2; Table 19",
)
_LIMITATIONS = (
    "Two equal concentric loads on two identical square columns only.",
    "Rigid rectangular constant-depth footing with approved uniform pressure only.",
    "No shear or punching reinforcement is selected or designed.",
    "No coated, bundled, spliced, curtailed or automatically selected bars.",
    "Soil capacity, settlement, durability selection and construction approval remain external.",
    "Qualified engineering review is required; software output is not professional approval.",
)
_MINIMUM_SLAB_STEEL_RATIO = 0.0012
_MINIMUM_FOOTING_COVER_MM = 50.0
_MINIMUM_TRANSFER_STEEL_RATIO = 0.005
_MINIMUM_TRANSFER_BAR_COUNT = 4
_MAXIMUM_DOWEL_INCREMENT_MM = 3.0


class CombinedFootingDesignDisposition(StrEnum):
    """Aggregate outcomes admitted by the represented strength workflow."""

    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"


@dataclass(frozen=True)
class CombinedFootingFlexureResult:
    """One supplied reinforcement set checked against one flexural region."""

    region: str
    design_width_mm: float
    effective_depth_mm: float
    overall_depth_mm: float
    factored_moment_kn_m: float
    flexural_steel_required_mm2: float | None
    minimum_steel_ratio: float
    minimum_steel_required_mm2: float
    governing_steel_required_mm2: float | None
    provided_bar_diameter_mm: float
    provided_bar_spacing_mm: float
    provided_steel_area_mm2: float
    provided_steel_ratio_percent: float
    maximum_bar_diameter_mm: float
    maximum_bar_spacing_mm: float
    provided_clear_spacing_mm: float
    minimum_clear_spacing_mm: float
    provided_nominal_cover_mm: float
    minimum_nominal_cover_mm: float
    tension_design_bond_stress_nmm2: float
    required_tension_development_length_mm: float
    available_straight_anchorage_each_end_mm: float
    singly_reinforced_capacity_is_sufficient: bool
    reinforcement_area_is_safe: bool
    bar_diameter_is_safe: bool
    bar_spacing_is_safe: bool
    clear_spacing_is_safe: bool
    nominal_cover_is_safe: bool
    anchorage_is_safe: bool
    is_safe: bool


@dataclass(frozen=True)
class CombinedFootingOneWayShearResult:
    """Concrete-only wide-beam shear check at one critical plane."""

    section: str
    factored_shear_demand_kn: float
    design_width_mm: float
    effective_depth_mm: float
    tension_reinforcement_area_mm2: float
    tension_reinforcement_percent: float
    table_19_lookup_reinforcement_percent: float
    nominal_shear_stress_nmm2: float
    concrete_design_shear_strength_nmm2: float
    utilization: float
    is_safe_without_shear_reinforcement: bool


@dataclass(frozen=True)
class CombinedFootingPunchingResult:
    """Concrete-only two-way shear check at one full column perimeter."""

    column: str
    factored_column_load_kn: float
    net_factored_pressure_kn_per_m2: float
    critical_enclosed_area_m2: float
    critical_perimeter_mm: float
    effective_depth_mm: float
    factored_punching_shear_kn: float
    nominal_punching_stress_nmm2: float
    column_aspect_ratio_beta_c: float
    size_factor_ks: float
    concrete_capacity_nmm2: float
    utilization: float
    is_safe_without_punching_reinforcement: bool


@dataclass(frozen=True)
class CombinedFootingLoadTransferResult:
    """Bearing and compression-dowel check at one identical column."""

    column: str
    factored_column_load_kn: float
    loaded_area_mm2: float
    effective_supporting_area_mm2: float
    bearing_enhancement_factor: float
    actual_bearing_stress_nmm2: float
    supported_column_bearing_capacity_kn: float
    supporting_footing_bearing_capacity_kn: float
    governing_concrete_member: str
    governing_concrete_bearing_capacity_kn: float
    concrete_bearing_without_transfer_is_safe: bool
    excess_force_kn: float
    excess_transfer_steel_area_mm2: float
    minimum_transfer_steel_area_mm2: float
    required_transfer_steel_area_mm2: float
    provided_transfer_steel_area_mm2: float
    minimum_dowel_count: int
    provided_dowel_count: int
    maximum_dowel_diameter_mm: float
    provided_dowel_diameter_mm: float
    footing_compression_design_bond_stress_nmm2: float
    column_compression_design_bond_stress_nmm2: float
    required_development_into_footing_mm: float
    required_development_into_column_mm: float
    available_development_into_footing_mm: float
    available_development_into_column_mm: float
    reinforcement_area_is_safe: bool
    bar_count_is_safe: bool
    dowel_diameter_is_safe: bool
    footing_development_is_safe: bool
    column_development_is_safe: bool
    is_safe: bool


@dataclass(frozen=True)
class CombinedFootingStrengthResult:
    """Composed service, strength, detailing, and transfer disposition."""

    input: CombinedFootingDesignInput
    actions: CombinedFootingActionResult
    top_longitudinal_flexure: CombinedFootingFlexureResult
    bottom_longitudinal_flexure: CombinedFootingFlexureResult
    transverse_flexure: CombinedFootingFlexureResult
    longitudinal_one_way_shear: tuple[
        CombinedFootingOneWayShearResult,
        CombinedFootingOneWayShearResult,
        CombinedFootingOneWayShearResult,
        CombinedFootingOneWayShearResult,
    ]
    transverse_one_way_shear: CombinedFootingOneWayShearResult
    punching: tuple[CombinedFootingPunchingResult, CombinedFootingPunchingResult]
    load_transfer: tuple[
        CombinedFootingLoadTransferResult,
        CombinedFootingLoadTransferResult,
    ]
    disposition: CombinedFootingDesignDisposition
    reasons: tuple[str, ...]
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    qualified_review_required: bool = True
    complete_engineering_approval: bool = False

    @property
    def is_safe_within_supported_scope(self) -> bool:
        """Return whether every represented comparison passes."""

        return self.disposition is CombinedFootingDesignDisposition.PASS


def _bar_area_mm2(diameter_mm: float) -> float:
    return math.pi * diameter_mm**2 / 4.0


def _provided_area_mm2(
    *,
    width_mm: float,
    diameter_mm: float,
    spacing_mm: float,
) -> float:
    return width_mm * _bar_area_mm2(diameter_mm) / spacing_mm


def _tension_development_length_mm(
    *,
    diameter_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
) -> tuple[float, float]:
    bond_stress = get_bond_stress(fck_nmm2, "deformed")
    development_length = diameter_mm * 0.87 * fy_nmm2 / (4.0 * bond_stress)
    return bond_stress, development_length


def _check_flexure(
    *,
    region: str,
    width_mm: float,
    effective_depth_mm: float,
    overall_depth_mm: float,
    moment_kn_m: float,
    fck_nmm2: float,
    fy_nmm2: float,
    diameter_mm: float,
    spacing_mm: float,
    aggregate_size_mm: float,
    nominal_cover_mm: float,
    available_anchorage_mm: float,
) -> CombinedFootingFlexureResult:
    xu_max_over_d = materials.get_xu_max_d(fy_nmm2)
    limiting_moment_kn_m = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * fck_nmm2
        * width_mm
        * effective_depth_mm**2
        / 1_000_000.0
    )
    capacity_is_sufficient = moment_kn_m <= limiting_moment_kn_m
    flexural_area: float | None = None
    if capacity_is_sufficient:
        flexural_area, _ = calculate_ast_from_rectangular_stress_block(
            b_mm=width_mm,
            d_mm=effective_depth_mm,
            factored_moment_knm=moment_kn_m,
            fck_n_per_mm2=fck_nmm2,
            fy_n_per_mm2=fy_nmm2,
        )
    minimum_area = _MINIMUM_SLAB_STEEL_RATIO * width_mm * overall_depth_mm
    required_area = (
        max(flexural_area, minimum_area) if flexural_area is not None else None
    )
    provided_area = _provided_area_mm2(
        width_mm=width_mm,
        diameter_mm=diameter_mm,
        spacing_mm=spacing_mm,
    )
    maximum_diameter = overall_depth_mm / 8.0
    maximum_spacing = min(3.0 * effective_depth_mm, 300.0)
    clear_spacing = spacing_mm - diameter_mm
    minimum_clear_spacing = max(diameter_mm, aggregate_size_mm + 5.0)
    bond_stress, required_development = _tension_development_length_mm(
        diameter_mm=diameter_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
    )
    area_is_safe = required_area is not None and provided_area >= required_area
    diameter_is_safe = diameter_mm <= maximum_diameter
    spacing_is_safe = spacing_mm <= maximum_spacing
    clear_spacing_is_safe = clear_spacing >= minimum_clear_spacing
    cover_is_safe = nominal_cover_mm >= _MINIMUM_FOOTING_COVER_MM
    anchorage_is_safe = available_anchorage_mm >= required_development
    is_safe = all(
        (
            capacity_is_sufficient,
            area_is_safe,
            diameter_is_safe,
            spacing_is_safe,
            clear_spacing_is_safe,
            cover_is_safe,
            anchorage_is_safe,
        )
    )
    return CombinedFootingFlexureResult(
        region=region,
        design_width_mm=width_mm,
        effective_depth_mm=effective_depth_mm,
        overall_depth_mm=overall_depth_mm,
        factored_moment_kn_m=moment_kn_m,
        flexural_steel_required_mm2=flexural_area,
        minimum_steel_ratio=_MINIMUM_SLAB_STEEL_RATIO,
        minimum_steel_required_mm2=minimum_area,
        governing_steel_required_mm2=required_area,
        provided_bar_diameter_mm=diameter_mm,
        provided_bar_spacing_mm=spacing_mm,
        provided_steel_area_mm2=provided_area,
        provided_steel_ratio_percent=100.0
        * provided_area
        / (width_mm * overall_depth_mm),
        maximum_bar_diameter_mm=maximum_diameter,
        maximum_bar_spacing_mm=maximum_spacing,
        provided_clear_spacing_mm=clear_spacing,
        minimum_clear_spacing_mm=minimum_clear_spacing,
        provided_nominal_cover_mm=nominal_cover_mm,
        minimum_nominal_cover_mm=_MINIMUM_FOOTING_COVER_MM,
        tension_design_bond_stress_nmm2=bond_stress,
        required_tension_development_length_mm=required_development,
        available_straight_anchorage_each_end_mm=available_anchorage_mm,
        singly_reinforced_capacity_is_sufficient=capacity_is_sufficient,
        reinforcement_area_is_safe=area_is_safe,
        bar_diameter_is_safe=diameter_is_safe,
        bar_spacing_is_safe=spacing_is_safe,
        clear_spacing_is_safe=clear_spacing_is_safe,
        nominal_cover_is_safe=cover_is_safe,
        anchorage_is_safe=anchorage_is_safe,
        is_safe=is_safe,
    )


def _check_one_way_shear(
    *,
    section: str,
    demand_kn: float,
    width_mm: float,
    effective_depth_mm: float,
    tension_area_mm2: float,
    fck_nmm2: float,
) -> CombinedFootingOneWayShearResult:
    reinforcement_percent = 100.0 * tension_area_mm2 / (width_mm * effective_depth_mm)
    table_lookup_percent = min(max(reinforcement_percent, 0.15), 3.0)
    nominal_stress = demand_kn * 1000.0 / (width_mm * effective_depth_mm)
    concrete_strength = get_tc_value(fck_nmm2, table_lookup_percent)
    utilization = nominal_stress / concrete_strength
    return CombinedFootingOneWayShearResult(
        section=section,
        factored_shear_demand_kn=demand_kn,
        design_width_mm=width_mm,
        effective_depth_mm=effective_depth_mm,
        tension_reinforcement_area_mm2=tension_area_mm2,
        tension_reinforcement_percent=reinforcement_percent,
        table_19_lookup_reinforcement_percent=table_lookup_percent,
        nominal_shear_stress_nmm2=nominal_stress,
        concrete_design_shear_strength_nmm2=concrete_strength,
        utilization=utilization,
        is_safe_without_shear_reinforcement=nominal_stress <= concrete_strength,
    )


def _check_punching(
    *,
    column: str,
    actions: CombinedFootingActionResult,
    fck_nmm2: float,
) -> CombinedFootingPunchingResult:
    column_load = actions.input.actions.factored_axial_load_each_kn
    punching_force = column_load - (
        actions.net_factored_structural_pressure_kn_per_m2
        * actions.geometry.punching_area_each_m2
    )
    if punching_force <= 0.0:
        raise CombinedFootingContractError(
            "factored punching shear force must remain positive at each column"
        )
    geometry = actions.input.geometry
    beta_c = 1.0
    ks = min(1.0, 0.5 + beta_c)
    capacity = ks * 0.25 * math.sqrt(fck_nmm2)
    nominal_stress = (
        punching_force
        * 1000.0
        / (actions.geometry.punching_perimeter_each_mm * geometry.effective_depth_mm)
    )
    return CombinedFootingPunchingResult(
        column=column,
        factored_column_load_kn=column_load,
        net_factored_pressure_kn_per_m2=(
            actions.net_factored_structural_pressure_kn_per_m2
        ),
        critical_enclosed_area_m2=actions.geometry.punching_area_each_m2,
        critical_perimeter_mm=actions.geometry.punching_perimeter_each_mm,
        effective_depth_mm=geometry.effective_depth_mm,
        factored_punching_shear_kn=punching_force,
        nominal_punching_stress_nmm2=nominal_stress,
        column_aspect_ratio_beta_c=beta_c,
        size_factor_ks=ks,
        concrete_capacity_nmm2=capacity,
        utilization=nominal_stress / capacity,
        is_safe_without_punching_reinforcement=nominal_stress <= capacity,
    )


def _check_load_transfer(
    *,
    column: str,
    design_input: CombinedFootingDesignInput,
    loaded_area_mm2: float,
) -> CombinedFootingLoadTransferResult:
    transfer = design_input.transfer
    material = design_input.material
    column_load_kn = design_input.analysis.actions.factored_axial_load_each_kn
    supporting_area = transfer.effective_supporting_area_each_mm2
    if supporting_area < loaded_area_mm2:
        raise CombinedFootingContractError(
            "effective_supporting_area_each_mm2 must be at least the loaded column area"
        )

    enhancement = min(math.sqrt(supporting_area / loaded_area_mm2), 2.0)
    column_capacity_kn = (
        0.45 * material.column_concrete_grade_nmm2 * loaded_area_mm2 / 1000.0
    )
    footing_capacity_kn = (
        0.45
        * material.footing_concrete_grade_nmm2
        * enhancement
        * loaded_area_mm2
        / 1000.0
    )
    if column_capacity_kn <= footing_capacity_kn:
        governing_member = "supported_column"
        governing_capacity_kn = column_capacity_kn
    else:
        governing_member = "supporting_footing"
        governing_capacity_kn = footing_capacity_kn
    excess_force_kn = max(0.0, column_load_kn - governing_capacity_kn)
    excess_area = excess_force_kn * 1000.0 / (0.87 * material.steel_grade_nmm2)
    minimum_area = _MINIMUM_TRANSFER_STEEL_RATIO * loaded_area_mm2
    required_area = max(excess_area, minimum_area)
    provided_area = transfer.dowel_count_each * _bar_area_mm2(
        transfer.dowel_diameter_mm
    )
    maximum_dowel_diameter = (
        transfer.column_longitudinal_bar_diameter_mm + _MAXIMUM_DOWEL_INCREMENT_MM
    )

    footing_compression_bond = 1.25 * get_bond_stress(
        material.footing_concrete_grade_nmm2,
        "deformed",
    )
    column_compression_bond = 1.25 * get_bond_stress(
        material.column_concrete_grade_nmm2,
        "deformed",
    )
    required_into_footing = (
        transfer.dowel_diameter_mm
        * 0.87
        * material.steel_grade_nmm2
        / (4.0 * footing_compression_bond)
    )
    required_into_column = (
        transfer.dowel_diameter_mm
        * 0.87
        * material.steel_grade_nmm2
        / (4.0 * column_compression_bond)
    )
    area_is_safe = provided_area >= required_area
    count_is_safe = transfer.dowel_count_each >= _MINIMUM_TRANSFER_BAR_COUNT
    diameter_is_safe = transfer.dowel_diameter_mm <= maximum_dowel_diameter
    footing_development_is_safe = (
        transfer.available_dowel_development_into_footing_mm >= required_into_footing
    )
    column_development_is_safe = (
        transfer.available_dowel_development_into_column_mm >= required_into_column
    )
    is_safe = all(
        (
            area_is_safe,
            count_is_safe,
            diameter_is_safe,
            footing_development_is_safe,
            column_development_is_safe,
        )
    )
    return CombinedFootingLoadTransferResult(
        column=column,
        factored_column_load_kn=column_load_kn,
        loaded_area_mm2=loaded_area_mm2,
        effective_supporting_area_mm2=supporting_area,
        bearing_enhancement_factor=enhancement,
        actual_bearing_stress_nmm2=column_load_kn * 1000.0 / loaded_area_mm2,
        supported_column_bearing_capacity_kn=column_capacity_kn,
        supporting_footing_bearing_capacity_kn=footing_capacity_kn,
        governing_concrete_member=governing_member,
        governing_concrete_bearing_capacity_kn=governing_capacity_kn,
        concrete_bearing_without_transfer_is_safe=column_load_kn
        <= governing_capacity_kn,
        excess_force_kn=excess_force_kn,
        excess_transfer_steel_area_mm2=excess_area,
        minimum_transfer_steel_area_mm2=minimum_area,
        required_transfer_steel_area_mm2=required_area,
        provided_transfer_steel_area_mm2=provided_area,
        minimum_dowel_count=_MINIMUM_TRANSFER_BAR_COUNT,
        provided_dowel_count=transfer.dowel_count_each,
        maximum_dowel_diameter_mm=maximum_dowel_diameter,
        provided_dowel_diameter_mm=transfer.dowel_diameter_mm,
        footing_compression_design_bond_stress_nmm2=footing_compression_bond,
        column_compression_design_bond_stress_nmm2=column_compression_bond,
        required_development_into_footing_mm=required_into_footing,
        required_development_into_column_mm=required_into_column,
        available_development_into_footing_mm=(
            transfer.available_dowel_development_into_footing_mm
        ),
        available_development_into_column_mm=(
            transfer.available_dowel_development_into_column_mm
        ),
        reinforcement_area_is_safe=area_is_safe,
        bar_count_is_safe=count_is_safe,
        dowel_diameter_is_safe=diameter_is_safe,
        footing_development_is_safe=footing_development_is_safe,
        column_development_is_safe=column_development_is_safe,
        is_safe=is_safe,
    )


@clause(
    "26.2.1",
    "26.2.1.1",
    "26.3.2",
    "26.3.3",
    "26.4.2.2",
    "26.5.2.1",
    "26.5.2.2",
    "31.6.1",
    "31.6.2.1",
    "31.6.3.1",
    "34.1",
    "34.2.3.1",
    "34.2.4.1",
    "34.2.4.3",
    "34.3",
    "34.4",
    "34.4.1",
    "34.4.2",
    "34.4.3",
    "34.5.1",
    "38.1",
    "G-1.1",
    "40.1",
    "40.2",
)
def check_symmetric_combined_footing_strength(
    footing_input: CombinedFootingDesignInput,
) -> CombinedFootingStrengthResult:
    """Check the G0-frozen reinforcement, shear, punching and transfer scope.

    Valid but inadequate provision returns ``FAIL``. Geometry, materials,
    action models, or approvals outside the frozen contract raise
    :class:`CombinedFootingContractError` without producing a disposition.
    """

    if not isinstance(footing_input, CombinedFootingDesignInput):
        raise CombinedFootingContractError(
            "footing_input must be a CombinedFootingDesignInput"
        )
    actions = analyze_symmetric_combined_footing(footing_input.analysis)
    geometry = footing_input.analysis.geometry
    material = footing_input.material
    reinforcement = footing_input.reinforcement
    width_mm = geometry.footing_width_mm
    d_mm = geometry.effective_depth_mm
    overall_depth_mm = geometry.overall_depth_mm

    top_flexure = _check_flexure(
        region="inter_column_top_full_width",
        width_mm=width_mm,
        effective_depth_mm=d_mm,
        overall_depth_mm=overall_depth_mm,
        moment_kn_m=actions.inter_column_midpoint.moment_demand_kn_m,
        fck_nmm2=material.footing_concrete_grade_nmm2,
        fy_nmm2=material.steel_grade_nmm2,
        diameter_mm=reinforcement.top_longitudinal_diameter_mm,
        spacing_mm=reinforcement.top_longitudinal_spacing_mm,
        aggregate_size_mm=reinforcement.aggregate_size_mm,
        nominal_cover_mm=reinforcement.nominal_cover_mm,
        available_anchorage_mm=(
            reinforcement.available_top_longitudinal_anchorage_each_end_mm
        ),
    )
    bottom_moment = max(
        actions.left_outer_column_face.moment_demand_kn_m,
        actions.left_inner_column_face.moment_demand_kn_m,
        actions.right_inner_column_face.moment_demand_kn_m,
        actions.right_outer_column_face.moment_demand_kn_m,
    )
    bottom_flexure = _check_flexure(
        region="exterior_column_face_bottom_full_width",
        width_mm=width_mm,
        effective_depth_mm=d_mm,
        overall_depth_mm=overall_depth_mm,
        moment_kn_m=bottom_moment,
        fck_nmm2=material.footing_concrete_grade_nmm2,
        fy_nmm2=material.steel_grade_nmm2,
        diameter_mm=reinforcement.bottom_longitudinal_diameter_mm,
        spacing_mm=reinforcement.bottom_longitudinal_spacing_mm,
        aggregate_size_mm=reinforcement.aggregate_size_mm,
        nominal_cover_mm=reinforcement.nominal_cover_mm,
        available_anchorage_mm=(
            reinforcement.available_bottom_longitudinal_anchorage_each_end_mm
        ),
    )
    transverse_flexure = _check_flexure(
        region="transverse_column_face_per_metre",
        width_mm=1000.0,
        effective_depth_mm=d_mm,
        overall_depth_mm=overall_depth_mm,
        moment_kn_m=actions.transverse.moment_kn_m_per_m,
        fck_nmm2=material.footing_concrete_grade_nmm2,
        fy_nmm2=material.steel_grade_nmm2,
        diameter_mm=reinforcement.transverse_diameter_mm,
        spacing_mm=reinforcement.transverse_spacing_mm,
        aggregate_size_mm=reinforcement.aggregate_size_mm,
        nominal_cover_mm=reinforcement.nominal_cover_mm,
        available_anchorage_mm=(
            reinforcement.available_transverse_anchorage_each_edge_mm
        ),
    )

    longitudinal_shear = (
        _check_one_way_shear(
            section="left_outer",
            demand_kn=actions.left_outer_one_way_shear.shear_demand_kn,
            width_mm=width_mm,
            effective_depth_mm=d_mm,
            tension_area_mm2=bottom_flexure.provided_steel_area_mm2,
            fck_nmm2=material.footing_concrete_grade_nmm2,
        ),
        _check_one_way_shear(
            section="left_inner",
            demand_kn=actions.left_inner_one_way_shear.shear_demand_kn,
            width_mm=width_mm,
            effective_depth_mm=d_mm,
            tension_area_mm2=top_flexure.provided_steel_area_mm2,
            fck_nmm2=material.footing_concrete_grade_nmm2,
        ),
        _check_one_way_shear(
            section="right_inner",
            demand_kn=actions.right_inner_one_way_shear.shear_demand_kn,
            width_mm=width_mm,
            effective_depth_mm=d_mm,
            tension_area_mm2=top_flexure.provided_steel_area_mm2,
            fck_nmm2=material.footing_concrete_grade_nmm2,
        ),
        _check_one_way_shear(
            section="right_outer",
            demand_kn=actions.right_outer_one_way_shear.shear_demand_kn,
            width_mm=width_mm,
            effective_depth_mm=d_mm,
            tension_area_mm2=bottom_flexure.provided_steel_area_mm2,
            fck_nmm2=material.footing_concrete_grade_nmm2,
        ),
    )
    transverse_shear = _check_one_way_shear(
        section="transverse_per_metre",
        demand_kn=actions.transverse.one_way_shear_demand_kn_per_m,
        width_mm=1000.0,
        effective_depth_mm=d_mm,
        tension_area_mm2=transverse_flexure.provided_steel_area_mm2,
        fck_nmm2=material.footing_concrete_grade_nmm2,
    )
    punching = (
        _check_punching(
            column="left",
            actions=actions,
            fck_nmm2=material.footing_concrete_grade_nmm2,
        ),
        _check_punching(
            column="right",
            actions=actions,
            fck_nmm2=material.footing_concrete_grade_nmm2,
        ),
    )
    loaded_area_mm2 = geometry.column_side_mm**2
    load_transfer = (
        _check_load_transfer(
            column="left",
            design_input=footing_input,
            loaded_area_mm2=loaded_area_mm2,
        ),
        _check_load_transfer(
            column="right",
            design_input=footing_input,
            loaded_area_mm2=loaded_area_mm2,
        ),
    )

    reasons: list[str] = []
    if not actions.gross_service_bearing_within_allowable:
        reasons.append("Approved gross service bearing pressure is exceeded.")
    for flexure_result in (top_flexure, bottom_flexure, transverse_flexure):
        if not flexure_result.is_safe:
            reasons.append(
                f"Reinforcement/detailing is inadequate at {flexure_result.region}."
            )
    for shear_result in (*longitudinal_shear, transverse_shear):
        if not shear_result.is_safe_without_shear_reinforcement:
            reasons.append(
                f"Concrete-only one-way shear is inadequate at {shear_result.section}."
            )
    for punching_result in punching:
        if not punching_result.is_safe_without_punching_reinforcement:
            reasons.append(
                "Concrete-only punching shear is inadequate at the "
                f"{punching_result.column} column."
            )
    for transfer_result in load_transfer:
        if not transfer_result.is_safe:
            reasons.append(
                "Bearing/dowel transfer provision is inadequate at the "
                f"{transfer_result.column} column."
            )

    if reasons:
        disposition = CombinedFootingDesignDisposition.FAIL
    else:
        disposition = CombinedFootingDesignDisposition.PASS
        reasons.append(
            "Every represented service, strength and detailing check passes."
        )

    return CombinedFootingStrengthResult(
        input=footing_input,
        actions=actions,
        top_longitudinal_flexure=top_flexure,
        bottom_longitudinal_flexure=bottom_flexure,
        transverse_flexure=transverse_flexure,
        longitudinal_one_way_shear=longitudinal_shear,
        transverse_one_way_shear=transverse_shear,
        punching=punching,
        load_transfer=load_transfer,
        disposition=disposition,
        reasons=tuple(reasons),
        clause_refs=_CLAUSE_REFS,
        source_refs=_SOURCE_REFS
        + actions.source_refs
        + (
            material.material_basis_reference,
            reinforcement.detailing_basis_reference,
            footing_input.transfer.transfer_basis_reference,
        ),
        limitations=_LIMITATIONS,
    )
