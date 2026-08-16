# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration for the bounded regular interior flat-slab workflow."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from structural_lib.codes.is456.flat_slab import (
    FlatSlabAnalysisMethod,
    FlatSlabContractError,
    FlatSlabDetailingInput,
    FlatSlabDirectionDetailingInput,
    FlatSlabGravityLoad,
    FlatSlabGridGeometry,
    FlatSlabMaterial,
    FlatSlabPanelInput,
    FlatSlabPanelLocation,
    FlatSlabPunchingInput,
    FlatSlabPunchingResult,
    FlatSlabReinforcementResult,
    check_regular_interior_flat_slab_punching,
    design_regular_interior_flat_slab_reinforcement,
)
from structural_lib.codes.is456.slab.detailing import ProvidedSlabBars

__all__ = [
    "RegularInteriorFlatSlabDesignInput",
    "RegularInteriorFlatSlabDesignProvenance",
    "RegularInteriorFlatSlabDesignResult",
    "RegularInteriorFlatSlabDesignStatus",
    "build_regular_interior_flat_slab_design_input",
    "design_regular_interior_flat_slab_is456",
]


_SUPPORTED_CASE = (
    "One equal-span square interior solid flat-slab panel in a grid of at least "
    "three continuous spans each way, designed by the direct design method under "
    "identical full uniform gravity loading, with a square centred column, no drop "
    "or head, caller-provided straight bars, reviewed span/depth acceptance, and "
    "one full-perimeter concrete-only punching check."
)
_HELD_CASES = (
    "Unequal or rectangular panels, fewer than three continuous spans, exterior panels, edge/corner or offset columns, drops, column heads, marginal beams or walls, and openings are excluded.",
    "Patterned or nonuniform loading, point or line loads, load-combination or envelope generation, lateral action, and unbalanced moment transfer are excluded.",
    "Equivalent-frame analysis, FEM, nonlinear analysis, transfer slabs, post-tensioning, prestress, seismic diaphragm/action design, and progressive-collapse design are excluded.",
    "Punching reinforcement, automatic depth/bar selection, bends, splices, anchorage layout, congestion, direct deflection, crack width, fire, and professional approval are excluded.",
)
_CLAUSE_REFS = (
    "31.1.1",
    "31.2.1",
    "31.3.1",
    "31.4.1",
    "31.4.2.2",
    "31.4.3.2",
    "31.4.4",
    "31.5.5.1",
    "31.5.5.3",
    "31.5.5.4",
    "23.2.1",
    "26.3.3",
    "26.5.2.1",
    "31.7.1",
    "31.7.2",
    "31.7.3",
    "Figure 16",
    "38.1",
    "31.6.1",
    "31.6.2.1",
    "31.6.3.1",
    "31.6.3.2",
)


class RegularInteriorFlatSlabDesignStatus(StrEnum):
    """Aggregate bounded workflow disposition."""

    PASS = "PASS"  # nosec B105
    FAIL = "FAIL"


@dataclass(frozen=True)
class RegularInteriorFlatSlabDesignInput:
    """Shared panel, provided bars, reaction, and retained review evidence."""

    case_id: str
    panel: FlatSlabPanelInput
    x: FlatSlabDirectionDetailingInput
    y: FlatSlabDirectionDetailingInput
    factored_support_reaction_kn: float
    straight_bars_only: bool
    all_bottom_bars_continuous: bool
    splices_present: bool
    serviceability_acceptance_acknowledged: bool
    centred_concentric_reaction: bool
    full_critical_perimeter_available: bool
    no_punching_reinforcement_provided: bool
    qualified_review_required: bool
    detailing_basis_reference: str
    serviceability_acceptance_reference: str
    support_reaction_basis_reference: str
    punching_basis_reference: str


@dataclass(frozen=True)
class RegularInteriorFlatSlabDesignProvenance:
    """Stable workflow, benchmark, source, and caller evidence identity."""

    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    support_reaction_status: str
    serviceability_verification_status: str
    geometry_basis_reference: str
    material_basis_reference: str
    load_basis_reference: str
    detailing_basis_reference: str
    serviceability_acceptance_reference: str
    support_reaction_basis_reference: str
    punching_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class RegularInteriorFlatSlabDesignResult:
    """Composed FLAT-A-D evidence with supported and held boundaries."""

    case_id: str
    status: RegularInteriorFlatSlabDesignStatus
    reinforcement: FlatSlabReinforcementResult
    punching: FlatSlabPunchingResult
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: RegularInteriorFlatSlabDesignProvenance
    qualified_review_required: bool = True
    complete_engineering_design_approved: bool = False


def _require_non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FlatSlabContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _source_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise FlatSlabContractError(f"{field_name} must be an object")
    return dict(value)


def _direction_from_mapping(
    value: object, field_name: str
) -> FlatSlabDirectionDetailingInput:
    values = _mapping(value, field_name)
    try:
        return FlatSlabDirectionDetailingInput(
            column_strip_negative_bars=ProvidedSlabBars(
                **_mapping(
                    values.pop("column_strip_negative_bars"),
                    f"{field_name}.column_strip_negative_bars",
                )
            ),
            column_strip_positive_bars=ProvidedSlabBars(
                **_mapping(
                    values.pop("column_strip_positive_bars"),
                    f"{field_name}.column_strip_positive_bars",
                )
            ),
            middle_strip_negative_bars=ProvidedSlabBars(
                **_mapping(
                    values.pop("middle_strip_negative_bars"),
                    f"{field_name}.middle_strip_negative_bars",
                )
            ),
            middle_strip_positive_bars=ProvidedSlabBars(
                **_mapping(
                    values.pop("middle_strip_positive_bars"),
                    f"{field_name}.middle_strip_positive_bars",
                )
            ),
            **values,
        )
    except KeyError as exc:
        raise FlatSlabContractError(
            f"{field_name} is missing required provided-bar input"
        ) from exc


def build_regular_interior_flat_slab_design_input(
    payload: Mapping[str, Any],
) -> RegularInteriorFlatSlabDesignInput:
    """Build the service contract from an already transport-validated mapping."""
    values = dict(payload)
    try:
        geometry_values = _mapping(values.pop("geometry"), "geometry")
        analysis_method = FlatSlabAnalysisMethod(geometry_values.pop("analysis_method"))
        panel_location = FlatSlabPanelLocation(geometry_values.pop("panel_location"))
        panel = FlatSlabPanelInput(
            geometry=FlatSlabGridGeometry(
                **geometry_values,
                analysis_method=analysis_method,
                panel_location=panel_location,
            ),
            material=FlatSlabMaterial(**_mapping(values.pop("material"), "material")),
            gravity_load=FlatSlabGravityLoad(
                **_mapping(values.pop("gravity_load"), "gravity_load")
            ),
        )
        x = _direction_from_mapping(values.pop("x"), "x")
        y = _direction_from_mapping(values.pop("y"), "y")
        return RegularInteriorFlatSlabDesignInput(
            **values,
            panel=panel,
            x=x,
            y=y,
        )
    except FlatSlabContractError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise FlatSlabContractError(
            "transport payload does not match the regular interior flat-slab input"
        ) from exc


def design_regular_interior_flat_slab_is456(
    request: RegularInteriorFlatSlabDesignInput,
) -> RegularInteriorFlatSlabDesignResult:
    """Compose the sole G0-approved direct-design and punching workflow."""
    if not isinstance(request, RegularInteriorFlatSlabDesignInput):
        raise FlatSlabContractError(
            "request must be a RegularInteriorFlatSlabDesignInput"
        )
    case_id = _require_non_blank(request.case_id, "case_id")
    if not isinstance(request.panel, FlatSlabPanelInput):
        raise FlatSlabContractError("panel must be a FlatSlabPanelInput")
    for name in ("x", "y"):
        if not isinstance(getattr(request, name), FlatSlabDirectionDetailingInput):
            raise FlatSlabContractError(
                f"{name} must be a FlatSlabDirectionDetailingInput"
            )

    reinforcement = design_regular_interior_flat_slab_reinforcement(
        FlatSlabDetailingInput(
            panel=request.panel,
            x=request.x,
            y=request.y,
            straight_bars_only=request.straight_bars_only,
            all_bottom_bars_continuous=request.all_bottom_bars_continuous,
            splices_present=request.splices_present,
            detailing_basis_reference=request.detailing_basis_reference,
            serviceability_acceptance_reference=(
                request.serviceability_acceptance_reference
            ),
            serviceability_acceptance_acknowledged=(
                request.serviceability_acceptance_acknowledged
            ),
        )
    )
    punching = check_regular_interior_flat_slab_punching(
        FlatSlabPunchingInput(
            panel=request.panel,
            factored_support_reaction_kn=request.factored_support_reaction_kn,
            centred_concentric_reaction=request.centred_concentric_reaction,
            full_critical_perimeter_available=(
                request.full_critical_perimeter_available
            ),
            no_punching_reinforcement_provided=(
                request.no_punching_reinforcement_provided
            ),
            qualified_review_required=request.qualified_review_required,
            support_reaction_basis_reference=(request.support_reaction_basis_reference),
            punching_basis_reference=request.punching_basis_reference,
        )
    )
    status = (
        RegularInteriorFlatSlabDesignStatus.PASS
        if reinforcement.is_reinforcement_and_detailing_adequate
        and reinforcement.is_span_depth_satisfied
        and punching.is_adequate_without_punching_reinforcement
        else RegularInteriorFlatSlabDesignStatus.FAIL
    )
    source_refs = _source_refs(
        reinforcement.source_refs,
        punching.source_refs,
        (
            "IS456-PUBLIC-DISTRIBUTION-001",
            "INDIA-2-FLAT-HAND-01",
        ),
    )
    panel = request.panel
    provenance = RegularInteriorFlatSlabDesignProvenance(
        schema_version="1.0",
        code_edition="IS 456:2000 through Amendment 6",
        workflow="design_regular_interior_flat_slab_is456",
        case_id=case_id,
        benchmark_id="INDIA-2-FLAT-HAND-01",
        action_generation_status=(
            "not_generated_caller_supplied_approved_uniform_gravity_actions"
        ),
        support_reaction_status=(
            "caller_supplied_checked_against_frozen_uniform_tributary_basis"
        ),
        serviceability_verification_status=(
            "reviewed_span_depth_only_direct_deflection_and_crack_width_held"
        ),
        geometry_basis_reference=panel.geometry.geometry_basis_reference,
        material_basis_reference=panel.material.material_basis_reference,
        load_basis_reference=panel.gravity_load.load_basis_reference,
        detailing_basis_reference=request.detailing_basis_reference,
        serviceability_acceptance_reference=(
            request.serviceability_acceptance_reference
        ),
        support_reaction_basis_reference=request.support_reaction_basis_reference,
        punching_basis_reference=request.punching_basis_reference,
        clause_refs=_CLAUSE_REFS,
        source_refs=source_refs,
    )
    return RegularInteriorFlatSlabDesignResult(
        case_id=case_id,
        status=status,
        reinforcement=reinforcement,
        punching=punching,
        supported_case=_SUPPORTED_CASE,
        held_cases=_HELD_CASES,
        provenance=provenance,
    )
