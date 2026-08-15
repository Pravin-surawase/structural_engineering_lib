# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration for the bounded IS 456 braced-wall workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from structural_lib.codes.is456.wall import (
    BracedWallAxialInput,
    BracedWallAxialResult,
    BracedWallGeometry,
    WallAxialStatus,
    WallContractError,
    WallDirectionalReinforcementResult,  # noqa: F401 - typed transport mapping
    WallReinforcementInput,
    WallReinforcementKind,
    WallReinforcementResult,
    WallRotationRestraint,
    check_braced_wall_axial_capacity,
    check_wall_minimum_reinforcement,
)

__all__ = [
    "BracedWallDesignInput",
    "BracedWallDesignProvenance",
    "BracedWallDesignResult",
    "design_braced_wall_is456",
]


_SUPPORTED_CASE = (
    "One regular 100-200 mm thick, one-grid, Clause 32.2 braced reinforced-"
    "concrete wall under caller-supplied factored in-plane vertical compression; "
    "the workflow checks empirical axial capacity and caller-provided Clause "
    "32.5 minimum reinforcement."
)
_HELD_CASES = (
    "Applied moment, horizontal action, wall shear, combined flexure, openings, and out-of-plane behavior are excluded.",
    "Walls thicker than 200 mm, two reinforcement grids, and transverse-enclosure design are excluded.",
    "Global analysis, load generation, load combinations, bar selection, anchorage, lap, crack width, and direct deflection are excluded.",
    "Seismic/shear-wall provisions and IS 13920 detailing are excluded.",
    "PASS is bounded software evidence; qualified engineering review and professional approval remain required.",
)


@dataclass(frozen=True)
class BracedWallDesignInput:
    """Explicit geometry, action, material, reinforcement, and provenance input."""

    case_id: str
    unsupported_height_mm: float
    lateral_restraint_spacing_mm: float
    wall_length_mm: float
    wall_thickness_mm: float
    concrete_grade_nmm2: float
    factored_axial_load_kn: float
    supplied_eccentricity_mm: float
    vertical_bar_diameter_mm: float
    vertical_bar_spacing_mm: float
    horizontal_bar_diameter_mm: float
    horizontal_bar_spacing_mm: float
    bracing_basis_reference: str
    action_basis_reference: str
    reinforcement_basis_reference: str
    rotation_restraint: Literal["restrained_both_ends", "not_restrained_both_ends"] = (
        "restrained_both_ends"
    )
    reinforcement_kind: Literal[
        "deformed_415_or_greater", "other_bars", "welded_wire_fabric"
    ] = "deformed_415_or_greater"
    bracing_elements_in_two_directions: Literal[True] = True
    lateral_forces_resisted_by_bracing_system: Literal[True] = True
    diaphragm_transfer_confirmed: Literal[True] = True
    lateral_connection_capacity_confirmed: Literal[True] = True


@dataclass(frozen=True)
class BracedWallDesignProvenance:
    """Stable workflow identity and source boundary for one wall result."""

    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    load_generation_status: str
    bracing_basis_reference: str
    action_basis_reference: str
    reinforcement_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class BracedWallDesignResult:
    """Composed wall evidence with retained supported and held boundaries."""

    case_id: str
    status: WallAxialStatus
    axial: BracedWallAxialResult
    reinforcement: WallReinforcementResult
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: BracedWallDesignProvenance
    qualified_review_required: bool = True
    complete_engineering_design_approved: bool = False


def _require_non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WallContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _source_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def design_braced_wall_is456(
    request: BracedWallDesignInput,
) -> BracedWallDesignResult:
    """Compose the sole supported braced-wall axial and detailing workflow."""
    if not isinstance(request, BracedWallDesignInput):
        raise WallContractError("request must be a BracedWallDesignInput")
    case_id = _require_non_blank(request.case_id, "case_id")
    bracing_reference = _require_non_blank(
        request.bracing_basis_reference,
        "bracing_basis_reference",
    )
    action_reference = _require_non_blank(
        request.action_basis_reference,
        "action_basis_reference",
    )
    reinforcement_reference = _require_non_blank(
        request.reinforcement_basis_reference,
        "reinforcement_basis_reference",
    )
    try:
        rotation_restraint = WallRotationRestraint(request.rotation_restraint)
    except (TypeError, ValueError) as error:
        raise WallContractError(
            "rotation_restraint must name a supported braced-wall end condition"
        ) from error
    try:
        reinforcement_kind = WallReinforcementKind(request.reinforcement_kind)
    except (TypeError, ValueError) as error:
        raise WallContractError(
            "reinforcement_kind must name a supported Clause 32.5 category"
        ) from error

    geometry = BracedWallGeometry(
        unsupported_height_mm=request.unsupported_height_mm,
        lateral_restraint_spacing_mm=request.lateral_restraint_spacing_mm,
        wall_length_mm=request.wall_length_mm,
        wall_thickness_mm=request.wall_thickness_mm,
        rotation_restraint=rotation_restraint,
        bracing_elements_in_two_directions=(request.bracing_elements_in_two_directions),
        lateral_forces_resisted_by_bracing_system=(
            request.lateral_forces_resisted_by_bracing_system
        ),
        diaphragm_transfer_confirmed=request.diaphragm_transfer_confirmed,
        lateral_connection_capacity_confirmed=(
            request.lateral_connection_capacity_confirmed
        ),
        bracing_basis_reference=bracing_reference,
    )
    axial = check_braced_wall_axial_capacity(
        BracedWallAxialInput(
            geometry=geometry,
            concrete_grade_nmm2=request.concrete_grade_nmm2,
            factored_axial_load_kn=request.factored_axial_load_kn,
            supplied_eccentricity_mm=request.supplied_eccentricity_mm,
            action_basis_reference=action_reference,
        )
    )
    reinforcement = check_wall_minimum_reinforcement(
        WallReinforcementInput(
            geometry=geometry,
            reinforcement_kind=reinforcement_kind,
            vertical_bar_diameter_mm=request.vertical_bar_diameter_mm,
            vertical_bar_spacing_mm=request.vertical_bar_spacing_mm,
            horizontal_bar_diameter_mm=request.horizontal_bar_diameter_mm,
            horizontal_bar_spacing_mm=request.horizontal_bar_spacing_mm,
            reinforcement_basis_reference=reinforcement_reference,
        )
    )
    status = (
        WallAxialStatus.PASS
        if axial.status is WallAxialStatus.PASS
        and reinforcement.status is WallAxialStatus.PASS
        else WallAxialStatus.FAIL
    )
    sources = _source_refs(axial.source_refs, reinforcement.source_refs)
    provenance = BracedWallDesignProvenance(
        schema_version="1.0",
        code_edition="IS 456:2000",
        workflow="design_braced_wall_is456",
        case_id=case_id,
        benchmark_id="INDIA-2-WALL-HAND-01",
        load_generation_status=axial.load_generation_status,
        bracing_basis_reference=bracing_reference,
        action_basis_reference=action_reference,
        reinforcement_basis_reference=reinforcement_reference,
        clause_refs=(
            "32.2.1",
            "32.2.2",
            "32.2.3",
            "32.2.4",
            "32.2.5",
            "32.5",
            "32.5.1",
            "32.5.2",
        ),
        source_refs=sources,
    )
    return BracedWallDesignResult(
        case_id=case_id,
        status=status,
        axial=axial,
        reinforcement=reinforcement,
        supported_case=_SUPPORTED_CASE,
        held_cases=_HELD_CASES,
        provenance=provenance,
    )
