# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration for the bounded IS 456 simply supported deep beam."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from structural_lib.codes.is456.deep_beam import (
    DeepBeamActionInput,
    DeepBeamCheckStatus,
    DeepBeamContractError,
    DeepBeamGeometry,
    DeepBeamReinforcementInput,
    DeepBeamReinforcementResult,
    DeepBeamSupportType,
    check_simply_supported_deep_beam_reinforcement,
)

__all__ = [
    "SimplySupportedDeepBeamDesignInput",
    "SimplySupportedDeepBeamDesignProvenance",
    "SimplySupportedDeepBeamDesignResult",
    "design_simply_supported_deep_beam_is456",
]


_SUPPORTED_CASE = (
    "One simply supported, single-span, solid rectangular, top-loaded Clause "
    "29 deep beam without openings, dapped ends, or hanging action; the caller "
    "supplies one positive factored moment, provided positive tie/detailing, and "
    "external bearing/compression-nodal verification."
)
_HELD_CASES = (
    "Continuous and cantilever deep beams, negative moment, openings, dapped ends, corbels, coupling beams, hollow/flanged/irregular sections, prestress, and hanging action are excluded.",
    "The workflow does not generate loads or reactions and does not calculate bearing, support, compression-strut, or nodal-zone capacity.",
    "Automatic section or bar selection, bundles, splices, transverse-enclosure design, crack width, deflection, fire, and seismic/IS 13920 checks are excluded.",
    "Generalized strut-and-tie modelling, nonlinear analysis, FEM, professional approval, and release authorization are excluded.",
)


@dataclass(frozen=True)
class SimplySupportedDeepBeamDesignInput:
    """Explicit geometry, action, reinforcement, topology, and evidence input."""

    case_id: str
    centre_to_centre_span_mm: float
    clear_span_mm: float
    overall_depth_mm: float
    beam_width_mm: float
    concrete_grade_nmm2: float
    steel_grade_nmm2: float
    factored_positive_moment_knm: float
    main_bar_count: int
    main_bar_diameter_mm: float
    furthest_main_bar_from_tension_face_mm: float
    main_bars_continuous_between_supports: bool
    main_bars_bundled: Literal[False]
    main_bar_splices_present: Literal[False]
    left_support_embedment_mm: float
    right_support_embedment_mm: float
    face_grid_count: int
    vertical_side_bar_diameter_mm: float
    vertical_side_bar_spacing_mm: float
    horizontal_side_bar_diameter_mm: float
    horizontal_side_bar_spacing_mm: float
    geometry_basis_reference: str
    bearing_nodal_zone_reference: str
    action_basis_reference: str
    reinforcement_basis_reference: str
    support_type: Literal["simply_supported"]
    solid_rectangular_section: Literal[True]
    openings_present: Literal[False]
    dapped_ends_present: Literal[False]
    top_loaded: Literal[True]
    hanging_action_required: Literal[False]
    bearing_nodal_zone_verified: Literal[True]


@dataclass(frozen=True)
class SimplySupportedDeepBeamDesignProvenance:
    """Workflow, public clause/source, benchmark, and caller evidence identity."""

    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    bearing_nodal_zone_status: str
    geometry_basis_reference: str
    bearing_nodal_zone_reference: str
    action_basis_reference: str
    reinforcement_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class SimplySupportedDeepBeamDesignResult:
    """Public composed evidence with its supported and held boundaries."""

    case_id: str
    status: DeepBeamCheckStatus
    reinforcement: DeepBeamReinforcementResult
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: SimplySupportedDeepBeamDesignProvenance
    qualified_review_required: bool = True
    complete_engineering_design_approved: bool = False

    @property
    def shear_deemed_satisfied_within_clause_29_scope(self) -> bool:
        return self.reinforcement.shear_deemed_satisfied_within_clause_29_scope


def _require_non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeepBeamContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _source_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def design_simply_supported_deep_beam_is456(
    request: SimplySupportedDeepBeamDesignInput,
) -> SimplySupportedDeepBeamDesignResult:
    """Compose the sole bounded Clause 29 positive-reinforcement workflow."""
    if not isinstance(request, SimplySupportedDeepBeamDesignInput):
        raise DeepBeamContractError(
            "request must be a SimplySupportedDeepBeamDesignInput"
        )

    case_id = _require_non_blank(request.case_id, "case_id")
    geometry_reference = _require_non_blank(
        request.geometry_basis_reference, "geometry_basis_reference"
    )
    bearing_reference = _require_non_blank(
        request.bearing_nodal_zone_reference, "bearing_nodal_zone_reference"
    )
    action_reference = _require_non_blank(
        request.action_basis_reference, "action_basis_reference"
    )
    reinforcement_reference = _require_non_blank(
        request.reinforcement_basis_reference, "reinforcement_basis_reference"
    )
    try:
        support_type = DeepBeamSupportType(request.support_type)
    except (TypeError, ValueError) as error:
        raise DeepBeamContractError(
            "support_type must name the supported simply supported case"
        ) from error

    geometry = DeepBeamGeometry(
        centre_to_centre_span_mm=request.centre_to_centre_span_mm,
        clear_span_mm=request.clear_span_mm,
        overall_depth_mm=request.overall_depth_mm,
        beam_width_mm=request.beam_width_mm,
        support_type=support_type,
        solid_rectangular_section=request.solid_rectangular_section,
        openings_present=request.openings_present,
        dapped_ends_present=request.dapped_ends_present,
        top_loaded=request.top_loaded,
        hanging_action_required=request.hanging_action_required,
        bearing_nodal_zone_verified=request.bearing_nodal_zone_verified,
        geometry_basis_reference=geometry_reference,
        bearing_nodal_zone_reference=bearing_reference,
    )
    action = DeepBeamActionInput(
        geometry=geometry,
        concrete_grade_nmm2=request.concrete_grade_nmm2,
        steel_grade_nmm2=request.steel_grade_nmm2,
        factored_positive_moment_knm=request.factored_positive_moment_knm,
        action_basis_reference=action_reference,
    )
    reinforcement = check_simply_supported_deep_beam_reinforcement(
        DeepBeamReinforcementInput(
            action=action,
            main_bar_count=request.main_bar_count,
            main_bar_diameter_mm=request.main_bar_diameter_mm,
            furthest_main_bar_from_tension_face_mm=(
                request.furthest_main_bar_from_tension_face_mm
            ),
            main_bars_continuous_between_supports=(
                request.main_bars_continuous_between_supports
            ),
            main_bars_bundled=request.main_bars_bundled,
            main_bar_splices_present=request.main_bar_splices_present,
            left_support_embedment_mm=request.left_support_embedment_mm,
            right_support_embedment_mm=request.right_support_embedment_mm,
            face_grid_count=request.face_grid_count,
            vertical_side_bar_diameter_mm=request.vertical_side_bar_diameter_mm,
            vertical_side_bar_spacing_mm=request.vertical_side_bar_spacing_mm,
            horizontal_side_bar_diameter_mm=(request.horizontal_side_bar_diameter_mm),
            horizontal_side_bar_spacing_mm=request.horizontal_side_bar_spacing_mm,
            reinforcement_basis_reference=reinforcement_reference,
        )
    )
    source_refs = _source_refs(
        reinforcement.source_refs,
        (
            "IS456-PUBLIC-DISTRIBUTION-001",
            "NPTEL-RCD-DEEP-W7",
            "INDIA-2-DEEP-HAND-01",
        ),
    )
    provenance = SimplySupportedDeepBeamDesignProvenance(
        schema_version="1.0",
        code_edition="IS 456:2000 through Amendment 6",
        workflow="design_simply_supported_deep_beam_is456",
        case_id=case_id,
        benchmark_id="INDIA-2-DEEP-HAND-01",
        action_generation_status=(
            "not_generated_caller_supplied_positive_factored_moment"
        ),
        bearing_nodal_zone_status=("external_prerequisite_confirmed_not_calculated"),
        geometry_basis_reference=geometry_reference,
        bearing_nodal_zone_reference=bearing_reference,
        action_basis_reference=action_reference,
        reinforcement_basis_reference=reinforcement_reference,
        clause_refs=(
            "29",
            "29.1",
            "29.2",
            "29.3",
            "29.3.1",
            "29.3.4",
            "26.2.1",
            "26.2.1.1",
            "32.5",
            "32.5.1",
            "32.5.2",
        ),
        source_refs=source_refs,
    )
    return SimplySupportedDeepBeamDesignResult(
        case_id=case_id,
        status=reinforcement.status,
        reinforcement=reinforcement,
        supported_case=_SUPPORTED_CASE,
        held_cases=_HELD_CASES,
        provenance=provenance,
    )
