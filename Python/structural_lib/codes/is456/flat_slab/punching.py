# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Centred interior-column punching check for the bounded flat-slab route."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456.flat_slab.models import (
    FlatSlabContractError,
    FlatSlabPanelInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "FlatSlabPunchingInput",
    "FlatSlabPunchingResult",
    "FlatSlabPunchingStatus",
    "check_regular_interior_flat_slab_punching",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 31.6.1, 31.6.2.1, 31.6.3.1, 31.6.3.2",
    "IS456-2000-A6",
    "INDIA-2-FLAT-G0-CENTRED-INTERIOR-PUNCHING-BOUNDARY",
)
_REACTION_ABS_TOL_KN = 1e-6


def _positive_finite(value: float, field_name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise FlatSlabContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise FlatSlabContractError(
            f"{field_name} must be finite and positive in {unit}"
        )
    return normalized


def _non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FlatSlabContractError(f"{field_name} must be a non-blank string")
    return value.strip()


class FlatSlabPunchingStatus(StrEnum):
    """Outcomes admitted by the no-punching-reinforcement route."""

    SAFE_WITHOUT_PUNCHING_REINFORCEMENT = "safe_without_punching_reinforcement"
    PUNCHING_REINFORCEMENT_OR_REDESIGN_REQUIRED = (
        "punching_reinforcement_or_redesign_required"
    )
    REDESIGN_REQUIRED = "redesign_required"


@dataclass(frozen=True)
class FlatSlabPunchingInput:
    """Explicit reaction and applicability evidence for FLAT-D.

    ``factored_support_reaction_kn`` is supplied by the caller and must match
    the uniform tributary reaction of the frozen equal-panel topology. This
    preserves the load-analysis provenance instead of silently inventing a
    support action inside the punching calculation.
    """

    panel: FlatSlabPanelInput
    factored_support_reaction_kn: float
    centred_concentric_reaction: bool
    full_critical_perimeter_available: bool
    no_punching_reinforcement_provided: bool
    qualified_review_required: bool
    support_reaction_basis_reference: str
    punching_basis_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.panel, FlatSlabPanelInput):
            raise FlatSlabContractError("panel must be a FlatSlabPanelInput")
        object.__setattr__(
            self,
            "factored_support_reaction_kn",
            _positive_finite(
                self.factored_support_reaction_kn,
                "factored_support_reaction_kn",
                "kN",
            ),
        )
        for name in (
            "centred_concentric_reaction",
            "full_critical_perimeter_available",
            "no_punching_reinforcement_provided",
            "qualified_review_required",
        ):
            if getattr(self, name) is not True:
                raise FlatSlabContractError(f"{name} must be explicitly True")
        object.__setattr__(
            self,
            "support_reaction_basis_reference",
            _non_blank(
                self.support_reaction_basis_reference,
                "support_reaction_basis_reference",
            ),
        )
        object.__setattr__(
            self,
            "punching_basis_reference",
            _non_blank(self.punching_basis_reference, "punching_basis_reference"),
        )


@dataclass(frozen=True)
class FlatSlabPunchingResult:
    """Punching demand, concrete boundaries, and bounded route disposition."""

    input: FlatSlabPunchingInput
    expected_uniform_tributary_reaction_kn: float
    critical_section_side_x_mm: float
    critical_section_side_y_mm: float
    critical_perimeter_mm: float
    critical_enclosed_area_mm2: float
    factored_load_inside_critical_section_kn: float
    punching_shear_force_kn: float
    nominal_punching_stress_n_per_mm2: float
    column_aspect_ratio_beta_c: float
    size_factor_ks: float
    basic_concrete_shear_strength_n_per_mm2: float
    no_reinforcement_capacity_n_per_mm2: float
    mandatory_redesign_boundary_n_per_mm2: float
    no_reinforcement_utilization: float
    status: FlatSlabPunchingStatus
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]

    @property
    def is_adequate_without_punching_reinforcement(self) -> bool:
        return self.status is (
            FlatSlabPunchingStatus.SAFE_WITHOUT_PUNCHING_REINFORCEMENT
        )


@clause("31.6.1", "31.6.2.1", "31.6.3.1", "31.6.3.2")
def check_regular_interior_flat_slab_punching(
    punching_input: FlatSlabPunchingInput,
) -> FlatSlabPunchingResult:
    """Check the full centred square-column punching perimeter.

    The function checks concrete-only adequacy. If the no-reinforcement limit
    is exceeded, this route fails rather than designing punching reinforcement.
    It separately identifies the Clause 31.6.3.2 mandatory-redesign boundary.
    """
    if not isinstance(punching_input, FlatSlabPunchingInput):
        raise FlatSlabContractError("punching_input must be a FlatSlabPunchingInput")

    panel = punching_input.panel
    geometry = panel.geometry
    gravity_load = panel.gravity_load
    span_x_m = geometry.centre_to_centre_span_x_mm / 1000.0
    span_y_m = geometry.centre_to_centre_span_y_mm / 1000.0
    expected_reaction_kn = (
        gravity_load.factored_uniform_load_kn_per_m2 * span_x_m * span_y_m
    )
    if not math.isclose(
        punching_input.factored_support_reaction_kn,
        expected_reaction_kn,
        rel_tol=0.0,
        abs_tol=_REACTION_ABS_TOL_KN,
    ):
        raise FlatSlabContractError(
            "factored_support_reaction_kn must match the uniform tributary "
            "reaction for the frozen equal-panel topology"
        )

    effective_depth_mm = geometry.conservative_effective_depth_mm
    critical_side_x_mm = geometry.column_width_x_mm + effective_depth_mm
    critical_side_y_mm = geometry.column_width_y_mm + effective_depth_mm
    critical_perimeter_mm = 2.0 * (critical_side_x_mm + critical_side_y_mm)
    critical_enclosed_area_mm2 = critical_side_x_mm * critical_side_y_mm
    factored_load_inside_kn = (
        gravity_load.factored_uniform_load_kn_per_m2
        * critical_enclosed_area_mm2
        / 1_000_000.0
    )
    punching_shear_force_kn = (
        punching_input.factored_support_reaction_kn - factored_load_inside_kn
    )
    if punching_shear_force_kn <= 0.0:
        raise FlatSlabContractError(
            "factored punching shear force must remain positive at the critical section"
        )

    nominal_stress = (
        punching_shear_force_kn * 1000.0 / (critical_perimeter_mm * effective_depth_mm)
    )
    beta_c = min(geometry.column_width_x_mm, geometry.column_width_y_mm) / max(
        geometry.column_width_x_mm, geometry.column_width_y_mm
    )
    ks = min(1.0, 0.5 + beta_c)
    basic_concrete_strength = 0.25 * math.sqrt(panel.material.concrete_grade_nmm2)
    no_reinforcement_capacity = ks * basic_concrete_strength
    mandatory_redesign_boundary = 1.5 * basic_concrete_strength
    utilization = nominal_stress / no_reinforcement_capacity

    if nominal_stress <= no_reinforcement_capacity:
        status = FlatSlabPunchingStatus.SAFE_WITHOUT_PUNCHING_REINFORCEMENT
    elif nominal_stress <= mandatory_redesign_boundary:
        status = FlatSlabPunchingStatus.PUNCHING_REINFORCEMENT_OR_REDESIGN_REQUIRED
    else:
        status = FlatSlabPunchingStatus.REDESIGN_REQUIRED

    return FlatSlabPunchingResult(
        input=punching_input,
        expected_uniform_tributary_reaction_kn=expected_reaction_kn,
        critical_section_side_x_mm=critical_side_x_mm,
        critical_section_side_y_mm=critical_side_y_mm,
        critical_perimeter_mm=critical_perimeter_mm,
        critical_enclosed_area_mm2=critical_enclosed_area_mm2,
        factored_load_inside_critical_section_kn=factored_load_inside_kn,
        punching_shear_force_kn=punching_shear_force_kn,
        nominal_punching_stress_n_per_mm2=nominal_stress,
        column_aspect_ratio_beta_c=beta_c,
        size_factor_ks=ks,
        basic_concrete_shear_strength_n_per_mm2=basic_concrete_strength,
        no_reinforcement_capacity_n_per_mm2=no_reinforcement_capacity,
        mandatory_redesign_boundary_n_per_mm2=mandatory_redesign_boundary,
        no_reinforcement_utilization=utilization,
        status=status,
        source_refs=_SOURCE_REFS
        + (
            geometry.geometry_basis_reference,
            panel.material.material_basis_reference,
            gravity_load.load_basis_reference,
            punching_input.support_reaction_basis_reference,
            punching_input.punching_basis_reference,
        ),
        limitations=(
            "Centred concentric reaction at a square interior column only.",
            "Full unobstructed critical perimeter with no opening or free edge only.",
            "No unbalanced moment transfer is included.",
            "Punching reinforcement is neither selected nor designed.",
            "Qualified engineering review and project approval remain required.",
        ),
    )
