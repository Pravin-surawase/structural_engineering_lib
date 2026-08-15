# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration for the bounded IS 456 straight-flight staircase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from structural_lib.codes.is456.staircase import (
    StaircaseContractError,
    StaircaseDesignStatus,
    StairSpanDirection,
    StairSupportCase,
    StraightFlightActionInput,
    StraightFlightActionResult,
    StraightFlightDesignInput,
    StraightFlightDesignResult,
    StraightFlightGeometryResult,
    StraightFlightLoads,
    StraightFlightStairGeometry,
    analyze_straight_flight_actions,
    design_straight_flight_staircase,
)

__all__ = [
    "StraightFlightStaircaseInput",
    "StraightFlightStaircaseProvenance",
    "StraightFlightStaircaseResult",
    "design_straight_flight_staircase_is456",
]


_SUPPORTED_CASE = (
    "One cast-in-situ solid longitudinal straight waist-slab flight with two "
    "collinear landing effective segments spanning between outer beam or wall "
    "supports; horizontal-plan actions use explicit caller-supplied load shares, "
    "superimposed service loads, concrete unit weight, and ultimate load factor."
)
_HELD_CASES = (
    "Dog-legged, open-well, quarter-turn, half-turn, bifurcated, cantilever, spiral, transverse, precast, and stringer-supported stairs are excluded.",
    "IS 875 load generation, project load combinations, load patterns, continuity, redistribution, concentrated actions, and seismic behavior are excluded.",
    "Modification factors, direct deflection, crack width, development-length layout, landing torsion, and automatic bar selection remain held.",
    "PASS is bounded software evidence; qualified engineering review and professional approval remain required.",
)


@dataclass(frozen=True)
class StraightFlightStaircaseInput:
    """Explicit geometry, action provenance, materials, and supplied bars."""

    case_id: str
    lower_landing_effective_length_mm: float
    going_mm: float
    upper_landing_effective_length_mm: float
    flight_width_mm: float
    riser_mm: float
    tread_mm: float
    waist_thickness_mm: float
    landing_thickness_mm: float
    lower_landing_superimposed_service_load_kn_per_m2: float
    flight_superimposed_service_load_kn_per_m2: float
    upper_landing_superimposed_service_load_kn_per_m2: float
    lower_landing_load_share: float
    upper_landing_load_share: float
    concrete_unit_weight_kn_per_m3: float
    ultimate_load_factor: float
    load_basis_reference: str
    effective_depth_mm: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float
    main_bar_diameter_mm: float
    main_bar_spacing_mm: float
    distribution_bar_diameter_mm: float
    distribution_bar_spacing_mm: float
    support_case: Literal["landings_span_with_flight"] = "landings_span_with_flight"
    span_direction: Literal["longitudinal"] = "longitudinal"
    landings_collinear: Literal[True] = True
    has_stringer_beams: Literal[False] = False
    is_cast_in_situ_solid: Literal[True] = True


@dataclass(frozen=True)
class StraightFlightStaircaseProvenance:
    """Stable workflow identity and source boundary for one result."""

    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    load_basis_reference: str
    load_generation_status: str
    benchmark_id: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class StraightFlightStaircaseResult:
    """Composed bounded staircase evidence with retained public limitations."""

    case_id: str
    status: StaircaseDesignStatus
    geometry: StraightFlightGeometryResult
    actions: StraightFlightActionResult
    design: StraightFlightDesignResult
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: StraightFlightStaircaseProvenance
    qualified_review_required: bool = True
    complete_engineering_design_approved: bool = False


def _require_non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StaircaseContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _source_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def design_straight_flight_staircase_is456(
    request: StraightFlightStaircaseInput,
) -> StraightFlightStaircaseResult:
    """Compose the sole supported straight-flight staircase workflow."""
    if not isinstance(request, StraightFlightStaircaseInput):
        raise StaircaseContractError("request must be a StraightFlightStaircaseInput")
    case_id = _require_non_blank(request.case_id, "case_id")
    load_basis_reference = _require_non_blank(
        request.load_basis_reference, "load_basis_reference"
    )
    geometry_input = StraightFlightStairGeometry(
        lower_landing_effective_length_mm=(request.lower_landing_effective_length_mm),
        going_mm=request.going_mm,
        upper_landing_effective_length_mm=(request.upper_landing_effective_length_mm),
        flight_width_mm=request.flight_width_mm,
        riser_mm=request.riser_mm,
        tread_mm=request.tread_mm,
        waist_thickness_mm=request.waist_thickness_mm,
        landing_thickness_mm=request.landing_thickness_mm,
        support_case=StairSupportCase(request.support_case),
        span_direction=StairSpanDirection(request.span_direction),
        landings_collinear=request.landings_collinear,
        has_stringer_beams=request.has_stringer_beams,
        is_cast_in_situ_solid=request.is_cast_in_situ_solid,
    )
    loads = StraightFlightLoads(
        lower_landing_superimposed_service_load_kn_per_m2=(
            request.lower_landing_superimposed_service_load_kn_per_m2
        ),
        flight_superimposed_service_load_kn_per_m2=(
            request.flight_superimposed_service_load_kn_per_m2
        ),
        upper_landing_superimposed_service_load_kn_per_m2=(
            request.upper_landing_superimposed_service_load_kn_per_m2
        ),
        lower_landing_load_share=request.lower_landing_load_share,
        upper_landing_load_share=request.upper_landing_load_share,
        concrete_unit_weight_kn_per_m3=request.concrete_unit_weight_kn_per_m3,
        ultimate_load_factor=request.ultimate_load_factor,
        load_basis_reference=load_basis_reference,
    )
    actions = analyze_straight_flight_actions(
        StraightFlightActionInput(geometry=geometry_input, loads=loads)
    )
    design = design_straight_flight_staircase(
        StraightFlightDesignInput(
            actions=actions,
            effective_depth_mm=request.effective_depth_mm,
            fck_n_per_mm2=request.fck_n_per_mm2,
            fy_n_per_mm2=request.fy_n_per_mm2,
            main_bar_diameter_mm=request.main_bar_diameter_mm,
            main_bar_spacing_mm=request.main_bar_spacing_mm,
            distribution_bar_diameter_mm=request.distribution_bar_diameter_mm,
            distribution_bar_spacing_mm=request.distribution_bar_spacing_mm,
        )
    )
    sources = _source_refs(actions.source_refs, design.source_refs)
    provenance = StraightFlightStaircaseProvenance(
        schema_version="1.0",
        code_edition="IS 456:2000",
        workflow="design_straight_flight_staircase_is456",
        case_id=case_id,
        load_basis_reference=load_basis_reference,
        load_generation_status=actions.load_generation_status,
        benchmark_id="NPTEL-M9L20-EX9.1",
        clause_refs=(
            "23.2.1",
            "26.3.3",
            "26.5.2.1",
            "33.1-33.3",
            "38.1",
            "40.1-40.2",
        ),
        source_refs=sources,
    )
    return StraightFlightStaircaseResult(
        case_id=case_id,
        status=design.status,
        geometry=actions.geometry,
        actions=actions,
        design=design,
        supported_case=_SUPPORTED_CASE,
        held_cases=_HELD_CASES,
        provenance=provenance,
    )
