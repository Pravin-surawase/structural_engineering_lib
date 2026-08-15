# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed contracts for the bounded INDIA-2 Clause 32 braced-wall case."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

__all__ = [
    "BracedWallAxialInput",
    "BracedWallGeometry",
    "WallAxialStatus",
    "WallContractError",
    "WallReinforcementInput",
    "WallReinforcementKind",
    "WallRotationRestraint",
]


class WallContractError(ValueError):
    """Raised when an input is outside the frozen INDIA-2 wall scope."""


class WallRotationRestraint(StrEnum):
    """Clause 32.2.4 end-rotation cases for a braced wall."""

    RESTRAINED_BOTH_ENDS = "restrained_both_ends"
    NOT_RESTRAINED_BOTH_ENDS = "not_restrained_both_ends"


class WallAxialStatus(StrEnum):
    """Strength disposition for the accepted empirical axial check."""

    PASS = "PASS"  # nosec B105
    FAIL = "FAIL"


class WallReinforcementKind(StrEnum):
    """Clause 32.5 material categories for minimum wall reinforcement."""

    DEFORMED_415_OR_GREATER = "deformed_415_or_greater"
    OTHER_BARS = "other_bars"
    WELDED_WIRE_FABRIC = "welded_wire_fabric"


def positive_finite(value: float, field_name: str, unit: str) -> float:
    """Normalize a positive finite engineering input or fail closed."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise WallContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise WallContractError(f"{field_name} must be finite and positive in {unit}")
    return normalized


def nonnegative_finite(value: float, field_name: str, unit: str) -> float:
    """Normalize a non-negative finite engineering input or fail closed."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise WallContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0.0:
        raise WallContractError(
            f"{field_name} must be finite and non-negative in {unit}"
        )
    return normalized


@dataclass(frozen=True)
class BracedWallGeometry:
    """Caller-confirmed geometry and bracing basis for one wall strip.

    All dimensions are in mm. INDIA-2-WALL accepts 100-200 mm wall thickness
    and one reinforcement grid; the detailing checks are added in WALL-B.
    """

    unsupported_height_mm: float
    lateral_restraint_spacing_mm: float
    wall_length_mm: float
    wall_thickness_mm: float
    rotation_restraint: WallRotationRestraint
    bracing_elements_in_two_directions: bool
    lateral_forces_resisted_by_bracing_system: bool
    diaphragm_transfer_confirmed: bool
    lateral_connection_capacity_confirmed: bool
    bracing_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "unsupported_height_mm",
            "lateral_restraint_spacing_mm",
            "wall_length_mm",
            "wall_thickness_mm",
        ):
            object.__setattr__(
                self,
                name,
                positive_finite(getattr(self, name), name, "mm"),
            )
        if not 100.0 <= self.wall_thickness_mm <= 200.0:
            raise WallContractError(
                "wall_thickness_mm must be from 100 through 200 mm for "
                "the one-grid INDIA-2 wall scope"
            )
        if not isinstance(self.rotation_restraint, WallRotationRestraint):
            raise WallContractError(
                "rotation_restraint must be a WallRotationRestraint"
            )
        confirmations = (
            "bracing_elements_in_two_directions",
            "lateral_forces_resisted_by_bracing_system",
            "diaphragm_transfer_confirmed",
            "lateral_connection_capacity_confirmed",
        )
        for name in confirmations:
            if getattr(self, name) is not True:
                raise WallContractError(
                    f"{name} must be explicitly True for the Clause 32.2.1 "
                    "braced-wall scope"
                )
        if (
            not isinstance(self.bracing_basis_reference, str)
            or not self.bracing_basis_reference.strip()
        ):
            raise WallContractError(
                "bracing_basis_reference must be a non-blank caller reference"
            )
        object.__setattr__(
            self, "bracing_basis_reference", self.bracing_basis_reference.strip()
        )


@dataclass(frozen=True)
class BracedWallAxialInput:
    """Geometry, material, and caller-supplied factored axial compression."""

    geometry: BracedWallGeometry
    concrete_grade_nmm2: float
    factored_axial_load_kn: float
    supplied_eccentricity_mm: float
    action_basis_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, BracedWallGeometry):
            raise WallContractError("geometry must be a BracedWallGeometry")
        grade = positive_finite(
            self.concrete_grade_nmm2,
            "concrete_grade_nmm2",
            "N/mm2",
        )
        accepted_grades = {20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0}
        if grade not in accepted_grades:
            raise WallContractError(
                "concrete_grade_nmm2 must be a standard M20-M60 grade"
            )
        object.__setattr__(self, "concrete_grade_nmm2", grade)
        object.__setattr__(
            self,
            "factored_axial_load_kn",
            positive_finite(
                self.factored_axial_load_kn,
                "factored_axial_load_kn",
                "kN",
            ),
        )
        object.__setattr__(
            self,
            "supplied_eccentricity_mm",
            nonnegative_finite(
                self.supplied_eccentricity_mm,
                "supplied_eccentricity_mm",
                "mm",
            ),
        )
        if (
            not isinstance(self.action_basis_reference, str)
            or not self.action_basis_reference.strip()
        ):
            raise WallContractError(
                "action_basis_reference must be a non-blank caller reference"
            )
        object.__setattr__(
            self, "action_basis_reference", self.action_basis_reference.strip()
        )


@dataclass(frozen=True)
class WallReinforcementInput:
    """Caller-provided one-grid vertical and horizontal wall reinforcement.

    Bar diameters and spacings are in mm. The accepted wall geometry limits the
    packet to a single reinforcement grid; this contract checks provided steel
    and never selects bars.
    """

    geometry: BracedWallGeometry
    reinforcement_kind: WallReinforcementKind
    vertical_bar_diameter_mm: float
    vertical_bar_spacing_mm: float
    horizontal_bar_diameter_mm: float
    horizontal_bar_spacing_mm: float
    reinforcement_basis_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, BracedWallGeometry):
            raise WallContractError("geometry must be a BracedWallGeometry")
        if not isinstance(self.reinforcement_kind, WallReinforcementKind):
            raise WallContractError(
                "reinforcement_kind must be a WallReinforcementKind"
            )
        for name in (
            "vertical_bar_diameter_mm",
            "vertical_bar_spacing_mm",
            "horizontal_bar_diameter_mm",
            "horizontal_bar_spacing_mm",
        ):
            object.__setattr__(
                self,
                name,
                positive_finite(getattr(self, name), name, "mm"),
            )
        if self.reinforcement_kind in {
            WallReinforcementKind.DEFORMED_415_OR_GREATER,
            WallReinforcementKind.WELDED_WIRE_FABRIC,
        } and (
            self.vertical_bar_diameter_mm > 16.0
            or self.horizontal_bar_diameter_mm > 16.0
        ):
            raise WallContractError(
                "bar diameter must not exceed 16 mm for the selected Clause "
                "32.5 minimum-ratio category"
            )
        if (
            not isinstance(self.reinforcement_basis_reference, str)
            or not self.reinforcement_basis_reference.strip()
        ):
            raise WallContractError(
                "reinforcement_basis_reference must be a non-blank caller reference"
            )
        object.__setattr__(
            self,
            "reinforcement_basis_reference",
            self.reinforcement_basis_reference.strip(),
        )
