# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Rigid equal-pressure statics for the bounded property-line strap footing."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456.strap_footing.models import (
    StrapFootingAnalysisInput,
    StrapFootingContractError,
    StrapFootingGeometryInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "StrapFootingAnalysisResult",
    "StrapFootingClearSpanActionResult",
    "StrapFootingGeometryResult",
    "StrapFootingLoadCase",
    "StrapFootingLoadCaseResult",
    "StrapFootingTensionFace",
    "analyze_property_line_strap_footing",
    "resolve_property_line_strap_geometry",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 34.1, 34.1.2, 34.2.3.1",
    "IS456-2000-A5",
    "IS456-AMD6-2024",
    "NPTEL-AFE-C3-STRAP Section 3.6.1 and Fig. 3.2",
    "INDIA-2-STRAP-HAND-01",
)
_PRESSURE_RELATIVE_TOLERANCE = 1e-6
_ZERO_ABSOLUTE_TOLERANCE = 1e-9


class StrapFootingLoadCase(StrEnum):
    """Action levels represented by the frozen model."""

    SERVICE = "service"
    FACTORED = "factored"


class StrapFootingTensionFace(StrEnum):
    """Tension face implied by the clear-strap moment sign convention."""

    BOTTOM = "bottom"
    TOP = "top"
    NONE = "none"


@dataclass(frozen=True)
class StrapFootingGeometryResult:
    """Resolved coordinates and dimensions for the G0-frozen topology."""

    input: StrapFootingGeometryInput
    exterior_footing_area_m2: float
    interior_footing_area_m2: float
    exterior_footing_centroid_x_mm: float
    interior_footing_centroid_x_mm: float
    exterior_column_eccentricity_mm: float
    reaction_spacing_mm: float
    exterior_footing_inner_edge_x_mm: float
    interior_footing_outer_edge_x_mm: float
    interior_footing_inner_edge_x_mm: float
    clear_strap_start_x_mm: float
    clear_strap_end_x_mm: float
    clear_strap_length_mm: float
    clear_strap_centroid_x_mm: float
    clear_span_to_overall_depth_ratio: float
    rigid_equal_pressure_eligible: bool
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class StrapFootingLoadCaseResult:
    """Reactions, pressure, bearing and equilibrium for one action level."""

    load_case: StrapFootingLoadCase
    exterior_column_load_kn: float
    interior_column_load_kn: float
    clear_strap_line_load_kn_per_m: float
    clear_strap_total_load_kn: float
    total_downward_load_kn: float
    exterior_reaction_kn: float
    interior_reaction_kn: float
    exterior_net_pressure_kn_per_m2: float
    interior_net_pressure_kn_per_m2: float
    pressure_relative_mismatch: float
    equal_uniform_net_pressure: bool
    exterior_footing_carrier_kn_per_m2: float
    interior_footing_carrier_kn_per_m2: float
    exterior_gross_pressure_kn_per_m2: float
    interior_gross_pressure_kn_per_m2: float
    vertical_equilibrium_residual_kn: float
    moment_equilibrium_residual_kn_m: float


@dataclass(frozen=True)
class StrapFootingClearSpanActionResult:
    """Signed shear and moment envelope across the clear strap.

    Upward shear is positive. Positive moment denotes bottom tension and
    negative moment denotes top tension.
    """

    load_case: StrapFootingLoadCase
    exterior_face_x_mm: float
    exterior_face_shear_kn: float
    exterior_face_moment_kn_m: float
    interior_face_x_mm: float
    interior_face_shear_kn: float
    interior_face_moment_kn_m: float
    governing_shear_demand_kn: float
    governing_shear_x_mm: float
    governing_moment_demand_kn_m: float
    governing_moment_signed_kn_m: float
    governing_moment_x_mm: float
    governing_tension_face: StrapFootingTensionFace


@dataclass(frozen=True)
class StrapFootingAnalysisResult:
    """Complete action result for the bounded property-line strap system."""

    input: StrapFootingAnalysisInput
    geometry: StrapFootingGeometryResult
    service: StrapFootingLoadCaseResult
    factored: StrapFootingLoadCaseResult
    service_clear_strap: StrapFootingClearSpanActionResult
    factored_clear_strap: StrapFootingClearSpanActionResult
    common_factored_multiplier: float
    allowable_gross_bearing_pressure_kn_per_m2: float
    exterior_service_bearing_utilization: float
    interior_service_bearing_utilization: float
    exterior_service_bearing_within_allowable: bool
    interior_service_bearing_within_allowable: bool
    gross_service_bearing_within_allowable: bool
    source_refs: tuple[str, ...]


def _zero_small(value: float) -> float:
    if math.isclose(value, 0.0, rel_tol=0.0, abs_tol=_ZERO_ABSOLUTE_TOLERANCE):
        return 0.0
    return value


def _tension_face(moment_kn_m: float) -> StrapFootingTensionFace:
    if math.isclose(
        moment_kn_m,
        0.0,
        rel_tol=0.0,
        abs_tol=_ZERO_ABSOLUTE_TOLERANCE,
    ):
        return StrapFootingTensionFace.NONE
    if moment_kn_m > 0.0:
        return StrapFootingTensionFace.BOTTOM
    return StrapFootingTensionFace.TOP


@clause("34.1", "34.1.2")
def resolve_property_line_strap_geometry(
    geometry: StrapFootingGeometryInput,
) -> StrapFootingGeometryResult:
    """Resolve coordinates only for the G0-approved property-line topology."""

    if not isinstance(geometry, StrapFootingGeometryInput):
        raise StrapFootingContractError("geometry must be a StrapFootingGeometryInput")
    exterior_centroid = geometry.exterior_footing_length_mm / 2.0
    interior_centroid = geometry.interior_column_center_x_mm
    interior_outer_edge = interior_centroid - geometry.interior_footing_length_mm / 2.0
    interior_inner_edge = interior_centroid + geometry.interior_footing_length_mm / 2.0
    clear_start = geometry.exterior_footing_length_mm
    clear_end = interior_outer_edge
    clear_length = clear_end - clear_start
    return StrapFootingGeometryResult(
        input=geometry,
        exterior_footing_area_m2=(
            geometry.exterior_footing_length_mm
            * geometry.exterior_footing_width_mm
            / 1_000_000.0
        ),
        interior_footing_area_m2=(
            geometry.interior_footing_length_mm
            * geometry.interior_footing_width_mm
            / 1_000_000.0
        ),
        exterior_footing_centroid_x_mm=exterior_centroid,
        interior_footing_centroid_x_mm=interior_centroid,
        exterior_column_eccentricity_mm=(
            exterior_centroid - geometry.exterior_column_center_x_mm
        ),
        reaction_spacing_mm=interior_centroid - exterior_centroid,
        exterior_footing_inner_edge_x_mm=clear_start,
        interior_footing_outer_edge_x_mm=interior_outer_edge,
        interior_footing_inner_edge_x_mm=interior_inner_edge,
        clear_strap_start_x_mm=clear_start,
        clear_strap_end_x_mm=clear_end,
        clear_strap_length_mm=clear_length,
        clear_strap_centroid_x_mm=(clear_start + clear_end) / 2.0,
        clear_span_to_overall_depth_ratio=(
            clear_length / geometry.strap_overall_depth_mm
        ),
        rigid_equal_pressure_eligible=True,
        source_refs=_SOURCE_REFS
        + (
            geometry.geometry_basis_reference,
            geometry.rigidity_basis_reference,
            geometry.strap_isolation_basis_reference,
        ),
    )


def _load_case_result(
    *,
    load_case: StrapFootingLoadCase,
    geometry: StrapFootingGeometryResult,
    exterior_column_load_kn: float,
    interior_column_load_kn: float,
    clear_strap_line_load_kn_per_m: float,
    exterior_footing_carrier_kn_per_m2: float,
    interior_footing_carrier_kn_per_m2: float,
) -> StrapFootingLoadCaseResult:
    x_q1_m = geometry.input.exterior_column_center_x_mm / 1000.0
    x_q2_m = geometry.input.interior_column_center_x_mm / 1000.0
    x_r1_m = geometry.exterior_footing_centroid_x_mm / 1000.0
    x_r2_m = geometry.interior_footing_centroid_x_mm / 1000.0
    x_w_m = geometry.clear_strap_centroid_x_mm / 1000.0
    clear_length_m = geometry.clear_strap_length_mm / 1000.0
    strap_total_load = clear_strap_line_load_kn_per_m * clear_length_m
    total_downward = (
        exterior_column_load_kn + interior_column_load_kn + strap_total_load
    )

    reaction_spacing_m = x_r2_m - x_r1_m
    exterior_reaction = (
        exterior_column_load_kn * (x_r2_m - x_q1_m)
        + strap_total_load * (x_r2_m - x_w_m)
    ) / reaction_spacing_m
    interior_reaction = total_downward - exterior_reaction
    if exterior_reaction <= 0.0 or interior_reaction <= 0.0:
        raise StrapFootingContractError(
            f"{load_case.value} actions produce a non-positive footing reaction"
        )

    exterior_pressure = exterior_reaction / geometry.exterior_footing_area_m2
    interior_pressure = interior_reaction / geometry.interior_footing_area_m2
    pressure_relative_mismatch = abs(exterior_pressure - interior_pressure) / max(
        exterior_pressure,
        interior_pressure,
    )
    equal_pressure = pressure_relative_mismatch <= _PRESSURE_RELATIVE_TOLERANCE
    if not equal_pressure:
        raise StrapFootingContractError(
            f"{load_case.value} net footing pressures must be equal within "
            f"relative tolerance {_PRESSURE_RELATIVE_TOLERANCE:g}; "
            f"observed mismatch {pressure_relative_mismatch:.12g}"
        )

    vertical_residual = exterior_reaction + interior_reaction - total_downward
    moment_residual = (
        exterior_reaction * x_r1_m
        + interior_reaction * x_r2_m
        - exterior_column_load_kn * x_q1_m
        - interior_column_load_kn * x_q2_m
        - strap_total_load * x_w_m
    )
    return StrapFootingLoadCaseResult(
        load_case=load_case,
        exterior_column_load_kn=exterior_column_load_kn,
        interior_column_load_kn=interior_column_load_kn,
        clear_strap_line_load_kn_per_m=clear_strap_line_load_kn_per_m,
        clear_strap_total_load_kn=strap_total_load,
        total_downward_load_kn=total_downward,
        exterior_reaction_kn=exterior_reaction,
        interior_reaction_kn=interior_reaction,
        exterior_net_pressure_kn_per_m2=exterior_pressure,
        interior_net_pressure_kn_per_m2=interior_pressure,
        pressure_relative_mismatch=pressure_relative_mismatch,
        equal_uniform_net_pressure=True,
        exterior_footing_carrier_kn_per_m2=exterior_footing_carrier_kn_per_m2,
        interior_footing_carrier_kn_per_m2=interior_footing_carrier_kn_per_m2,
        exterior_gross_pressure_kn_per_m2=(
            exterior_pressure + exterior_footing_carrier_kn_per_m2
        ),
        interior_gross_pressure_kn_per_m2=(
            interior_pressure + interior_footing_carrier_kn_per_m2
        ),
        vertical_equilibrium_residual_kn=_zero_small(vertical_residual),
        moment_equilibrium_residual_kn_m=_zero_small(moment_residual),
    )


def _clear_span_actions(
    *,
    load_case: StrapFootingLoadCase,
    geometry: StrapFootingGeometryResult,
    load_result: StrapFootingLoadCaseResult,
) -> StrapFootingClearSpanActionResult:
    exterior_face_x_m = geometry.clear_strap_start_x_mm / 1000.0
    exterior_column_x_m = geometry.input.exterior_column_center_x_mm / 1000.0
    exterior_reaction_x_m = geometry.exterior_footing_centroid_x_mm / 1000.0
    clear_length_m = geometry.clear_strap_length_mm / 1000.0
    line_load = load_result.clear_strap_line_load_kn_per_m

    exterior_shear = (
        load_result.exterior_reaction_kn - load_result.exterior_column_load_kn
    )
    exterior_moment = load_result.exterior_reaction_kn * (
        exterior_face_x_m - exterior_reaction_x_m
    ) - load_result.exterior_column_load_kn * (exterior_face_x_m - exterior_column_x_m)
    interior_shear = exterior_shear - line_load * clear_length_m
    interior_moment = (
        exterior_moment
        + exterior_shear * clear_length_m
        - line_load * clear_length_m**2 / 2.0
    )

    shear_candidates = (
        (abs(exterior_shear), geometry.clear_strap_start_x_mm),
        (abs(interior_shear), geometry.clear_strap_end_x_mm),
    )
    governing_shear, governing_shear_x = max(shear_candidates, key=lambda item: item[0])

    moment_candidates = [
        (
            abs(exterior_moment),
            exterior_moment,
            geometry.clear_strap_start_x_mm,
        ),
        (
            abs(interior_moment),
            interior_moment,
            geometry.clear_strap_end_x_mm,
        ),
    ]
    if line_load > 0.0:
        critical_local_x_m = exterior_shear / line_load
        if 0.0 < critical_local_x_m < clear_length_m:
            critical_moment = (
                exterior_moment
                + exterior_shear * critical_local_x_m
                - line_load * critical_local_x_m**2 / 2.0
            )
            moment_candidates.append(
                (
                    abs(critical_moment),
                    critical_moment,
                    geometry.clear_strap_start_x_mm + critical_local_x_m * 1000.0,
                )
            )
    governing_moment, governing_signed_moment, governing_moment_x = max(
        moment_candidates,
        key=lambda item: item[0],
    )

    return StrapFootingClearSpanActionResult(
        load_case=load_case,
        exterior_face_x_mm=geometry.clear_strap_start_x_mm,
        exterior_face_shear_kn=_zero_small(exterior_shear),
        exterior_face_moment_kn_m=_zero_small(exterior_moment),
        interior_face_x_mm=geometry.clear_strap_end_x_mm,
        interior_face_shear_kn=_zero_small(interior_shear),
        interior_face_moment_kn_m=_zero_small(interior_moment),
        governing_shear_demand_kn=governing_shear,
        governing_shear_x_mm=governing_shear_x,
        governing_moment_demand_kn_m=governing_moment,
        governing_moment_signed_kn_m=_zero_small(governing_signed_moment),
        governing_moment_x_mm=governing_moment_x,
        governing_tension_face=_tension_face(governing_signed_moment),
    )


@clause("34.1", "34.2.3.1")
def analyze_property_line_strap_footing(
    footing_input: StrapFootingAnalysisInput,
) -> StrapFootingAnalysisResult:
    """Calculate reactions, bearing and clear-strap actions for the frozen case."""

    if not isinstance(footing_input, StrapFootingAnalysisInput):
        raise StrapFootingContractError(
            "footing_input must be a StrapFootingAnalysisInput"
        )
    geometry = resolve_property_line_strap_geometry(footing_input.geometry)
    actions = footing_input.actions

    service = _load_case_result(
        load_case=StrapFootingLoadCase.SERVICE,
        geometry=geometry,
        exterior_column_load_kn=actions.service_exterior_column_load_kn,
        interior_column_load_kn=actions.service_interior_column_load_kn,
        clear_strap_line_load_kn_per_m=(actions.service_clear_strap_line_load_kn_per_m),
        exterior_footing_carrier_kn_per_m2=(
            actions.service_exterior_footing_carrier_kn_per_m2
        ),
        interior_footing_carrier_kn_per_m2=(
            actions.service_interior_footing_carrier_kn_per_m2
        ),
    )
    factored = _load_case_result(
        load_case=StrapFootingLoadCase.FACTORED,
        geometry=geometry,
        exterior_column_load_kn=actions.factored_exterior_column_load_kn,
        interior_column_load_kn=actions.factored_interior_column_load_kn,
        clear_strap_line_load_kn_per_m=(
            actions.factored_clear_strap_line_load_kn_per_m
        ),
        exterior_footing_carrier_kn_per_m2=(
            actions.factored_exterior_footing_carrier_kn_per_m2
        ),
        interior_footing_carrier_kn_per_m2=(
            actions.factored_interior_footing_carrier_kn_per_m2
        ),
    )
    service_clear_strap = _clear_span_actions(
        load_case=StrapFootingLoadCase.SERVICE,
        geometry=geometry,
        load_result=service,
    )
    factored_clear_strap = _clear_span_actions(
        load_case=StrapFootingLoadCase.FACTORED,
        geometry=geometry,
        load_result=factored,
    )
    allowable = actions.allowable_gross_bearing_pressure_kn_per_m2
    exterior_bearing_utilization = service.exterior_gross_pressure_kn_per_m2 / allowable
    interior_bearing_utilization = service.interior_gross_pressure_kn_per_m2 / allowable
    exterior_bearing_safe = service.exterior_gross_pressure_kn_per_m2 <= allowable
    interior_bearing_safe = service.interior_gross_pressure_kn_per_m2 <= allowable

    return StrapFootingAnalysisResult(
        input=footing_input,
        geometry=geometry,
        service=service,
        factored=factored,
        service_clear_strap=service_clear_strap,
        factored_clear_strap=factored_clear_strap,
        common_factored_multiplier=actions.common_factored_multiplier,
        allowable_gross_bearing_pressure_kn_per_m2=allowable,
        exterior_service_bearing_utilization=exterior_bearing_utilization,
        interior_service_bearing_utilization=interior_bearing_utilization,
        exterior_service_bearing_within_allowable=exterior_bearing_safe,
        interior_service_bearing_within_allowable=interior_bearing_safe,
        gross_service_bearing_within_allowable=(
            exterior_bearing_safe and interior_bearing_safe
        ),
        source_refs=_SOURCE_REFS
        + (
            actions.load_basis_reference,
            actions.bearing_settlement_basis_reference,
            actions.footing_carrier_basis_reference,
            actions.strap_line_load_basis_reference,
            actions.load_pattern_basis_reference,
            footing_input.approvals.exterior_footing_verification_reference,
            footing_input.approvals.interior_footing_verification_reference,
            footing_input.approvals.transfer_verification_reference,
            footing_input.approvals.construction_verification_reference,
        ),
    )
