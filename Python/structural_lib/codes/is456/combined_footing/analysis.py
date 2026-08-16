# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Rigid uniform-pressure actions for the bounded combined footing."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456.combined_footing.models import (
    CombinedFootingContractError,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "CombinedFootingActionResult",
    "CombinedFootingGeometryResult",
    "CombinedFootingSectionAction",
    "CombinedFootingSectionKind",
    "CombinedFootingTensionFace",
    "CombinedFootingTransverseAction",
    "analyze_symmetric_combined_footing",
    "resolve_symmetric_combined_footing_geometry",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 34.1, 34.1.2, 34.2.3.1, 34.2.4.1",
    "IS456-2000-A5",
    "IS456-AMD6-2024",
    "NPTEL-AFE-C3 Sections 3.7, 3.8, 3.14",
)
_ZERO_TOLERANCE = 1e-9


class CombinedFootingTensionFace(StrEnum):
    """Tension face implied by the longitudinal moment sign convention."""

    BOTTOM = "bottom"
    TOP = "top"
    NONE = "none"


class CombinedFootingSectionKind(StrEnum):
    """Named whole-width longitudinal equilibrium sections."""

    LEFT_FREE_EDGE = "left_free_edge"
    LEFT_OUTER_ONE_WAY_SHEAR = "left_outer_one_way_shear"
    LEFT_OUTER_COLUMN_FACE = "left_outer_column_face"
    LEFT_INNER_COLUMN_FACE = "left_inner_column_face"
    LEFT_INNER_ONE_WAY_SHEAR = "left_inner_one_way_shear"
    INTER_COLUMN_MIDPOINT = "inter_column_midpoint"
    RIGHT_INNER_ONE_WAY_SHEAR = "right_inner_one_way_shear"
    RIGHT_INNER_COLUMN_FACE = "right_inner_column_face"
    RIGHT_OUTER_COLUMN_FACE = "right_outer_column_face"
    RIGHT_OUTER_ONE_WAY_SHEAR = "right_outer_one_way_shear"
    RIGHT_FREE_EDGE = "right_free_edge"


@dataclass(frozen=True)
class CombinedFootingGeometryResult:
    """Resolved geometry for the G0-frozen symmetric rectangular footing."""

    input: CombinedFootingGeometryInput
    plan_area_m2: float
    footing_centroid_x_mm: float
    column_spacing_mm: float
    inter_column_clear_gap_mm: float
    equal_end_projection_mm: float
    transverse_column_face_cantilever_mm: float
    punching_critical_side_mm: float
    punching_area_each_m2: float
    punching_perimeter_each_mm: float
    rigid_uniform_pressure_eligible: bool
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class CombinedFootingSectionAction:
    """Signed whole-width shear and moment at one longitudinal section.

    Upward shear is positive. Positive moment denotes bottom tension; negative
    moment denotes top tension.
    """

    kind: CombinedFootingSectionKind
    x_mm: float
    shear_kn: float
    moment_kn_m: float
    tension_face: CombinedFootingTensionFace

    @property
    def shear_demand_kn(self) -> float:
        """Absolute one-way shear demand at this section."""

        return abs(self.shear_kn)

    @property
    def moment_demand_kn_m(self) -> float:
        """Absolute flexural demand at this section."""

        return abs(self.moment_kn_m)


@dataclass(frozen=True)
class CombinedFootingTransverseAction:
    """Spread-footing transverse cantilever action per metre length."""

    column_face_cantilever_mm: float
    moment_kn_m_per_m: float
    one_way_shear_section_from_column_face_mm: float
    one_way_shear_demand_kn_per_m: float


@dataclass(frozen=True)
class CombinedFootingActionResult:
    """Equilibrium, pressure, and critical actions for the bounded case."""

    input: CombinedFootingInput
    geometry: CombinedFootingGeometryResult
    service_column_resultant_kn: float
    service_column_resultant_x_mm: float
    service_total_vertical_load_kn: float
    service_total_resultant_x_mm: float
    gross_service_pressure_kn_per_m2: float
    gross_service_bearing_utilization: float
    gross_service_bearing_within_allowable: bool
    factored_column_resultant_kn: float
    factored_column_resultant_x_mm: float
    factored_total_vertical_load_kn: float
    gross_factored_pressure_kn_per_m2: float
    net_factored_structural_pressure_kn_per_m2: float
    upward_line_load_kn_per_m: float
    service_resultant_alignment_residual_mm: float
    factored_resultant_alignment_residual_mm: float
    left_free_edge: CombinedFootingSectionAction
    left_outer_one_way_shear: CombinedFootingSectionAction
    left_outer_column_face: CombinedFootingSectionAction
    left_inner_column_face: CombinedFootingSectionAction
    left_inner_one_way_shear: CombinedFootingSectionAction
    inter_column_midpoint: CombinedFootingSectionAction
    right_inner_one_way_shear: CombinedFootingSectionAction
    right_inner_column_face: CombinedFootingSectionAction
    right_outer_column_face: CombinedFootingSectionAction
    right_outer_one_way_shear: CombinedFootingSectionAction
    right_free_edge: CombinedFootingSectionAction
    transverse: CombinedFootingTransverseAction
    vertical_equilibrium_residual_kn: float
    moment_equilibrium_residual_kn_m: float
    source_refs: tuple[str, ...]


def _tension_face(moment_kn_m: float) -> CombinedFootingTensionFace:
    if math.isclose(moment_kn_m, 0.0, rel_tol=0.0, abs_tol=_ZERO_TOLERANCE):
        return CombinedFootingTensionFace.NONE
    if moment_kn_m > 0.0:
        return CombinedFootingTensionFace.BOTTOM
    return CombinedFootingTensionFace.TOP


def _section_action(
    *,
    kind: CombinedFootingSectionKind,
    x_mm: float,
    upward_line_load_kn_per_m: float,
    factored_column_load_each_kn: float,
    left_column_x_mm: float,
    right_column_x_mm: float,
) -> CombinedFootingSectionAction:
    x_m = x_mm / 1000.0
    left_column_x_m = left_column_x_mm / 1000.0
    right_column_x_m = right_column_x_mm / 1000.0
    shear_kn = upward_line_load_kn_per_m * x_m
    moment_kn_m = upward_line_load_kn_per_m * x_m**2 / 2.0
    for column_x_m in (left_column_x_m, right_column_x_m):
        if x_m >= column_x_m:
            shear_kn -= factored_column_load_each_kn
            moment_kn_m -= factored_column_load_each_kn * (x_m - column_x_m)
    if math.isclose(shear_kn, 0.0, rel_tol=0.0, abs_tol=_ZERO_TOLERANCE):
        shear_kn = 0.0
    if math.isclose(moment_kn_m, 0.0, rel_tol=0.0, abs_tol=_ZERO_TOLERANCE):
        moment_kn_m = 0.0
    return CombinedFootingSectionAction(
        kind=kind,
        x_mm=x_mm,
        shear_kn=shear_kn,
        moment_kn_m=moment_kn_m,
        tension_face=_tension_face(moment_kn_m),
    )


@clause("34.1", "34.2.3.1", "34.2.4.1")
def resolve_symmetric_combined_footing_geometry(
    geometry: CombinedFootingGeometryInput,
) -> CombinedFootingGeometryResult:
    """Resolve geometry only for the G0-approved symmetric rigid case."""

    if not isinstance(geometry, CombinedFootingGeometryInput):
        raise CombinedFootingContractError(
            "geometry must be a CombinedFootingGeometryInput"
        )
    critical_side = geometry.column_side_mm + geometry.effective_depth_mm
    return CombinedFootingGeometryResult(
        input=geometry,
        plan_area_m2=(
            geometry.footing_length_mm * geometry.footing_width_mm / 1_000_000.0
        ),
        footing_centroid_x_mm=geometry.footing_length_mm / 2.0,
        column_spacing_mm=(
            geometry.right_column_center_x_mm - geometry.left_column_center_x_mm
        ),
        inter_column_clear_gap_mm=(
            geometry.right_column_center_x_mm
            - geometry.left_column_center_x_mm
            - geometry.column_side_mm
        ),
        equal_end_projection_mm=(
            geometry.left_column_center_x_mm - geometry.column_side_mm / 2.0
        ),
        transverse_column_face_cantilever_mm=(
            geometry.footing_width_mm - geometry.column_side_mm
        )
        / 2.0,
        punching_critical_side_mm=critical_side,
        punching_area_each_m2=critical_side**2 / 1_000_000.0,
        punching_perimeter_each_mm=4.0 * critical_side,
        rigid_uniform_pressure_eligible=True,
        source_refs=_SOURCE_REFS
        + (
            geometry.rigidity_basis_reference,
            geometry.geometry_basis_reference,
        ),
    )


@clause("34.1", "34.2.3.1", "34.2.4.1")
def analyze_symmetric_combined_footing(
    footing_input: CombinedFootingInput,
) -> CombinedFootingActionResult:
    """Generate service pressure and factored actions for the frozen case.

    The service bearing carrier includes column loads plus the approved uniform
    footing-self-weight/overburden pressure. Structural actions use the net
    factored column pressure after the matching distributed carrier cancels;
    the input contract requires explicit approval and equal load factors for
    that cancellation.
    """

    if not isinstance(footing_input, CombinedFootingInput):
        raise CombinedFootingContractError(
            "footing_input must be a CombinedFootingInput"
        )
    geometry_input = footing_input.geometry
    actions = footing_input.actions
    geometry = resolve_symmetric_combined_footing_geometry(geometry_input)
    area_m2 = geometry.plan_area_m2
    centroid_x_mm = geometry.footing_centroid_x_mm

    service_column_resultant = 2.0 * actions.service_axial_load_each_kn
    service_column_resultant_x = (
        actions.service_axial_load_each_kn * geometry_input.left_column_center_x_mm
        + actions.service_axial_load_each_kn * geometry_input.right_column_center_x_mm
    ) / service_column_resultant
    service_carrier_kn = actions.service_uniform_carrier_kn_per_m2 * area_m2
    service_total = service_column_resultant + service_carrier_kn
    service_total_x = (
        service_column_resultant * service_column_resultant_x
        + service_carrier_kn * centroid_x_mm
    ) / service_total
    gross_service_pressure = service_total / area_m2

    factored_column_resultant = 2.0 * actions.factored_axial_load_each_kn
    factored_column_resultant_x = (
        actions.factored_axial_load_each_kn * geometry_input.left_column_center_x_mm
        + actions.factored_axial_load_each_kn * geometry_input.right_column_center_x_mm
    ) / factored_column_resultant
    factored_carrier_kn = actions.factored_uniform_carrier_kn_per_m2 * area_m2
    factored_total = factored_column_resultant + factored_carrier_kn
    gross_factored_pressure = factored_total / area_m2
    net_factored_pressure = (
        gross_factored_pressure - actions.factored_uniform_carrier_kn_per_m2
    )
    upward_line_load = net_factored_pressure * (
        geometry_input.footing_width_mm / 1000.0
    )

    half_column = geometry_input.column_side_mm / 2.0
    d_mm = geometry_input.effective_depth_mm
    left_outer_face_x = geometry_input.left_column_center_x_mm - half_column
    left_inner_face_x = geometry_input.left_column_center_x_mm + half_column
    right_inner_face_x = geometry_input.right_column_center_x_mm - half_column
    right_outer_face_x = geometry_input.right_column_center_x_mm + half_column
    midpoint_x = (
        geometry_input.left_column_center_x_mm + geometry_input.right_column_center_x_mm
    ) / 2.0

    def section(
        kind: CombinedFootingSectionKind, x_mm: float
    ) -> CombinedFootingSectionAction:
        return _section_action(
            kind=kind,
            x_mm=x_mm,
            upward_line_load_kn_per_m=upward_line_load,
            factored_column_load_each_kn=actions.factored_axial_load_each_kn,
            left_column_x_mm=geometry_input.left_column_center_x_mm,
            right_column_x_mm=geometry_input.right_column_center_x_mm,
        )

    left_free_edge = section(CombinedFootingSectionKind.LEFT_FREE_EDGE, 0.0)
    left_outer_shear = section(
        CombinedFootingSectionKind.LEFT_OUTER_ONE_WAY_SHEAR,
        left_outer_face_x - d_mm,
    )
    left_outer_face = section(
        CombinedFootingSectionKind.LEFT_OUTER_COLUMN_FACE,
        left_outer_face_x,
    )
    left_inner_face = section(
        CombinedFootingSectionKind.LEFT_INNER_COLUMN_FACE,
        left_inner_face_x,
    )
    left_inner_shear = section(
        CombinedFootingSectionKind.LEFT_INNER_ONE_WAY_SHEAR,
        left_inner_face_x + d_mm,
    )
    midpoint = section(
        CombinedFootingSectionKind.INTER_COLUMN_MIDPOINT,
        midpoint_x,
    )
    right_inner_shear = section(
        CombinedFootingSectionKind.RIGHT_INNER_ONE_WAY_SHEAR,
        right_inner_face_x - d_mm,
    )
    right_inner_face = section(
        CombinedFootingSectionKind.RIGHT_INNER_COLUMN_FACE,
        right_inner_face_x,
    )
    right_outer_face = section(
        CombinedFootingSectionKind.RIGHT_OUTER_COLUMN_FACE,
        right_outer_face_x,
    )
    right_outer_shear = section(
        CombinedFootingSectionKind.RIGHT_OUTER_ONE_WAY_SHEAR,
        right_outer_face_x + d_mm,
    )
    right_free_edge = section(
        CombinedFootingSectionKind.RIGHT_FREE_EDGE,
        geometry_input.footing_length_mm,
    )

    transverse_cantilever_m = geometry.transverse_column_face_cantilever_mm / 1000.0
    transverse_shear_length_m = max(
        transverse_cantilever_m - d_mm / 1000.0,
        0.0,
    )
    transverse = CombinedFootingTransverseAction(
        column_face_cantilever_mm=geometry.transverse_column_face_cantilever_mm,
        moment_kn_m_per_m=(net_factored_pressure * transverse_cantilever_m**2 / 2.0),
        one_way_shear_section_from_column_face_mm=d_mm,
        one_way_shear_demand_kn_per_m=(
            net_factored_pressure * transverse_shear_length_m
        ),
    )

    return CombinedFootingActionResult(
        input=footing_input,
        geometry=geometry,
        service_column_resultant_kn=service_column_resultant,
        service_column_resultant_x_mm=service_column_resultant_x,
        service_total_vertical_load_kn=service_total,
        service_total_resultant_x_mm=service_total_x,
        gross_service_pressure_kn_per_m2=gross_service_pressure,
        gross_service_bearing_utilization=(
            gross_service_pressure / actions.allowable_gross_bearing_pressure_kn_per_m2
        ),
        gross_service_bearing_within_allowable=(
            gross_service_pressure <= actions.allowable_gross_bearing_pressure_kn_per_m2
        ),
        factored_column_resultant_kn=factored_column_resultant,
        factored_column_resultant_x_mm=factored_column_resultant_x,
        factored_total_vertical_load_kn=factored_total,
        gross_factored_pressure_kn_per_m2=gross_factored_pressure,
        net_factored_structural_pressure_kn_per_m2=net_factored_pressure,
        upward_line_load_kn_per_m=upward_line_load,
        service_resultant_alignment_residual_mm=(service_total_x - centroid_x_mm),
        factored_resultant_alignment_residual_mm=(
            factored_column_resultant_x - centroid_x_mm
        ),
        left_free_edge=left_free_edge,
        left_outer_one_way_shear=left_outer_shear,
        left_outer_column_face=left_outer_face,
        left_inner_column_face=left_inner_face,
        left_inner_one_way_shear=left_inner_shear,
        inter_column_midpoint=midpoint,
        right_inner_one_way_shear=right_inner_shear,
        right_inner_column_face=right_inner_face,
        right_outer_column_face=right_outer_face,
        right_outer_one_way_shear=right_outer_shear,
        right_free_edge=right_free_edge,
        transverse=transverse,
        vertical_equilibrium_residual_kn=right_free_edge.shear_kn,
        moment_equilibrium_residual_kn_m=right_free_edge.moment_kn_m,
        source_refs=_SOURCE_REFS
        + (
            geometry_input.rigidity_basis_reference,
            geometry_input.geometry_basis_reference,
            actions.load_basis_reference,
            actions.bearing_settlement_basis_reference,
            actions.cancellation_basis_reference,
        ),
    )
