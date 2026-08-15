# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 29 positive tie, anchorage, and side-face reinforcement checks."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.deep_beam.geometry import (
    DeepBeamGeometryResult,
    resolve_simply_supported_deep_beam_geometry,
)
from structural_lib.codes.is456.deep_beam.models import (
    DeepBeamCheckStatus,
    DeepBeamContractError,
    DeepBeamReinforcementInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "DeepBeamAnchorageResult",
    "DeepBeamPlacementResult",
    "DeepBeamReinforcementResult",
    "DeepBeamSideFaceDirectionResult",
    "DeepBeamTieResult",
    "check_simply_supported_deep_beam_reinforcement",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 29.1(b), 29.2, 29.3.1, 29.3.4",
    "IS 456:2000 Cl. 26.2.1-26.2.1.1, 32.5-32.5.2",
    "IS456-2000-A6",
    "IS456-AMD3-DEEP-SIDEFACE",
)

_PLAIN_TENSION_BOND_STRESS_NMM2 = {
    20.0: 1.2,
    25.0: 1.4,
    30.0: 1.5,
    35.0: 1.7,
    40.0: 1.9,
    45.0: 1.9,
    50.0: 1.9,
    55.0: 1.9,
    60.0: 1.9,
}
_DEFORMED_BAR_BOND_FACTOR = 1.6
_DESIGN_STEEL_STRESS_FACTOR = 0.87
_DEEP_BEAM_EMBEDMENT_FACTOR = 0.8


@dataclass(frozen=True)
class DeepBeamTieResult:
    """Required and caller-provided positive tension-tie steel."""

    required_area_mm2: float
    provided_area_mm2: float
    design_steel_stress_nmm2: float
    status: DeepBeamCheckStatus


@dataclass(frozen=True)
class DeepBeamPlacementResult:
    """Positive tie placement within the Clause 29.3.1 tension-face zone."""

    permitted_zone_depth_mm: float
    furthest_bar_distance_mm: float
    status: DeepBeamCheckStatus


@dataclass(frozen=True)
class DeepBeamAnchorageResult:
    """Development length and both support-face embedment checks."""

    design_steel_stress_nmm2: float
    design_bond_stress_nmm2: float
    development_length_mm: float
    required_embedment_mm: float
    left_embedment_mm: float
    right_embedment_mm: float
    left_status: DeepBeamCheckStatus
    right_status: DeepBeamCheckStatus

    @property
    def status(self) -> DeepBeamCheckStatus:
        if (
            self.left_status is DeepBeamCheckStatus.PASS
            and self.right_status is DeepBeamCheckStatus.PASS
        ):
            return DeepBeamCheckStatus.PASS
        return DeepBeamCheckStatus.FAIL


@dataclass(frozen=True)
class DeepBeamSideFaceDirectionResult:
    """Minimum area and spacing check for one side-face direction."""

    minimum_ratio: float
    required_area_mm2_per_m: float
    provided_area_mm2_per_m: float
    provided_ratio: float
    required_face_grid_count: int
    provided_face_grid_count: int
    maximum_spacing_mm: float
    provided_spacing_mm: float
    area_status: DeepBeamCheckStatus
    spacing_status: DeepBeamCheckStatus

    @property
    def status(self) -> DeepBeamCheckStatus:
        if (
            self.area_status is DeepBeamCheckStatus.PASS
            and self.spacing_status is DeepBeamCheckStatus.PASS
        ):
            return DeepBeamCheckStatus.PASS
        return DeepBeamCheckStatus.FAIL


@dataclass(frozen=True)
class DeepBeamReinforcementResult:
    """Composed disposition for the bounded Clause 29 reinforcement route."""

    input: DeepBeamReinforcementInput
    geometry: DeepBeamGeometryResult
    positive_tie: DeepBeamTieResult
    placement: DeepBeamPlacementResult
    continuity_status: DeepBeamCheckStatus
    anchorage: DeepBeamAnchorageResult
    vertical_side_face: DeepBeamSideFaceDirectionResult
    horizontal_side_face: DeepBeamSideFaceDirectionResult
    external_bearing_nodal_prerequisite_satisfied: bool
    source_refs: tuple[str, ...]
    qualified_review_required: bool = True
    complete_engineering_approval: bool = False

    @property
    def status(self) -> DeepBeamCheckStatus:
        checks = (
            self.positive_tie.status,
            self.placement.status,
            self.continuity_status,
            self.anchorage.status,
            self.vertical_side_face.status,
            self.horizontal_side_face.status,
        )
        if (
            all(check is DeepBeamCheckStatus.PASS for check in checks)
            and self.external_bearing_nodal_prerequisite_satisfied
        ):
            return DeepBeamCheckStatus.PASS
        return DeepBeamCheckStatus.FAIL

    @property
    def shear_deemed_satisfied_within_clause_29_scope(self) -> bool:
        """Report the bounded Clause 29 statement only for an overall pass."""
        return self.status is DeepBeamCheckStatus.PASS


def _status(condition: bool) -> DeepBeamCheckStatus:
    return DeepBeamCheckStatus.PASS if condition else DeepBeamCheckStatus.FAIL


def _side_face_result(
    *,
    minimum_ratio: float,
    beam_width_mm: float,
    face_grid_count: int,
    bar_diameter_mm: float,
    bar_spacing_mm: float,
) -> DeepBeamSideFaceDirectionResult:
    gross_area_mm2_per_m = beam_width_mm * 1000.0
    required_area_mm2_per_m = minimum_ratio * gross_area_mm2_per_m
    one_bar_area_mm2 = math.pi * bar_diameter_mm**2 / 4.0
    provided_area_mm2_per_m = (
        face_grid_count * one_bar_area_mm2 * 1000.0 / bar_spacing_mm
    )
    maximum_spacing_mm = min(3.0 * beam_width_mm, 450.0)
    return DeepBeamSideFaceDirectionResult(
        minimum_ratio=minimum_ratio,
        required_area_mm2_per_m=required_area_mm2_per_m,
        provided_area_mm2_per_m=provided_area_mm2_per_m,
        provided_ratio=provided_area_mm2_per_m / gross_area_mm2_per_m,
        required_face_grid_count=2 if beam_width_mm > 200.0 else 1,
        provided_face_grid_count=face_grid_count,
        maximum_spacing_mm=maximum_spacing_mm,
        provided_spacing_mm=bar_spacing_mm,
        area_status=_status(provided_area_mm2_per_m >= required_area_mm2_per_m),
        spacing_status=_status(bar_spacing_mm <= maximum_spacing_mm),
    )


@clause(
    "29.1",
    "29.2",
    "29.3.1",
    "29.3.4",
    "26.2.1",
    "26.2.1.1",
    "32.5",
    "32.5.1",
    "32.5.2",
)
def check_simply_supported_deep_beam_reinforcement(
    reinforcement_input: DeepBeamReinforcementInput,
) -> DeepBeamReinforcementResult:
    """Check the caller-provided positive tie and side-face reinforcement.

    A vertical side-face ratio above one percent fails closed because the
    transverse-enclosure route remains outside this bounded implementation.
    """
    if not isinstance(reinforcement_input, DeepBeamReinforcementInput):
        raise DeepBeamContractError(
            "reinforcement_input must be a DeepBeamReinforcementInput"
        )

    action = reinforcement_input.action
    geometry = resolve_simply_supported_deep_beam_geometry(action.geometry)
    design_steel_stress = _DESIGN_STEEL_STRESS_FACTOR * action.steel_grade_nmm2

    required_tie_area = (
        action.factored_positive_moment_knm
        * 1_000_000.0
        / (design_steel_stress * geometry.lever_arm_mm)
    )
    provided_tie_area = (
        reinforcement_input.main_bar_count
        * math.pi
        * reinforcement_input.main_bar_diameter_mm**2
        / 4.0
    )
    positive_tie = DeepBeamTieResult(
        required_area_mm2=required_tie_area,
        provided_area_mm2=provided_tie_area,
        design_steel_stress_nmm2=design_steel_stress,
        status=_status(provided_tie_area >= required_tie_area),
    )
    placement = DeepBeamPlacementResult(
        permitted_zone_depth_mm=geometry.positive_reinforcement_zone_depth_mm,
        furthest_bar_distance_mm=(
            reinforcement_input.furthest_main_bar_from_tension_face_mm
        ),
        status=_status(
            reinforcement_input.furthest_main_bar_from_tension_face_mm
            <= geometry.positive_reinforcement_zone_depth_mm
        ),
    )

    plain_bond_stress = _PLAIN_TENSION_BOND_STRESS_NMM2[action.concrete_grade_nmm2]
    design_bond_stress = plain_bond_stress * _DEFORMED_BAR_BOND_FACTOR
    development_length = (
        reinforcement_input.main_bar_diameter_mm
        * design_steel_stress
        / (4.0 * design_bond_stress)
    )
    required_embedment = _DEEP_BEAM_EMBEDMENT_FACTOR * development_length
    anchorage = DeepBeamAnchorageResult(
        design_steel_stress_nmm2=design_steel_stress,
        design_bond_stress_nmm2=design_bond_stress,
        development_length_mm=development_length,
        required_embedment_mm=required_embedment,
        left_embedment_mm=reinforcement_input.left_support_embedment_mm,
        right_embedment_mm=reinforcement_input.right_support_embedment_mm,
        left_status=_status(
            reinforcement_input.left_support_embedment_mm >= required_embedment
        ),
        right_status=_status(
            reinforcement_input.right_support_embedment_mm >= required_embedment
        ),
    )

    vertical = _side_face_result(
        minimum_ratio=0.0012,
        beam_width_mm=action.geometry.beam_width_mm,
        face_grid_count=reinforcement_input.face_grid_count,
        bar_diameter_mm=reinforcement_input.vertical_side_bar_diameter_mm,
        bar_spacing_mm=reinforcement_input.vertical_side_bar_spacing_mm,
    )
    if vertical.provided_ratio > 0.01:
        raise DeepBeamContractError(
            "vertical side-face reinforcement ratio above 0.01 requires the "
            "held transverse-enclosure route"
        )
    horizontal = _side_face_result(
        minimum_ratio=0.0020,
        beam_width_mm=action.geometry.beam_width_mm,
        face_grid_count=reinforcement_input.face_grid_count,
        bar_diameter_mm=reinforcement_input.horizontal_side_bar_diameter_mm,
        bar_spacing_mm=reinforcement_input.horizontal_side_bar_spacing_mm,
    )

    return DeepBeamReinforcementResult(
        input=reinforcement_input,
        geometry=geometry,
        positive_tie=positive_tie,
        placement=placement,
        continuity_status=_status(
            reinforcement_input.main_bars_continuous_between_supports
        ),
        anchorage=anchorage,
        vertical_side_face=vertical,
        horizontal_side_face=horizontal,
        external_bearing_nodal_prerequisite_satisfied=(
            action.geometry.bearing_nodal_zone_verified
        ),
        source_refs=_SOURCE_REFS
        + (
            action.geometry.geometry_basis_reference,
            action.geometry.bearing_nodal_zone_reference,
            action.action_basis_reference,
            reinforcement_input.reinforcement_basis_reference,
        ),
    )
