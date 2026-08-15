# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 32.5 minimum reinforcement checks for the bounded wall case."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.traceability import clause
from structural_lib.codes.is456.wall.models import (
    WallAxialStatus,
    WallContractError,
    WallReinforcementInput,
    WallReinforcementKind,
)

__all__ = [
    "WallDirectionalReinforcementResult",
    "WallReinforcementResult",
    "check_wall_minimum_reinforcement",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 32.5-32.5.2",
    "IS456-2000-A6",
)


@dataclass(frozen=True)
class WallDirectionalReinforcementResult:
    """Required and caller-provided reinforcement for one wall direction."""

    minimum_ratio: float
    required_area_mm2_per_m: float
    provided_area_mm2_per_m: float
    provided_ratio: float
    maximum_spacing_mm: float
    provided_spacing_mm: float
    area_status: WallAxialStatus
    spacing_status: WallAxialStatus

    @property
    def status(self) -> WallAxialStatus:
        """Return PASS only when both area and spacing checks pass."""
        if (
            self.area_status is WallAxialStatus.PASS
            and self.spacing_status is WallAxialStatus.PASS
        ):
            return WallAxialStatus.PASS
        return WallAxialStatus.FAIL


@dataclass(frozen=True)
class WallReinforcementResult:
    """Clause 32.5 one-grid minimum-reinforcement disposition."""

    input: WallReinforcementInput
    vertical: WallDirectionalReinforcementResult
    horizontal: WallDirectionalReinforcementResult
    transverse_enclosure_required: bool
    source_refs: tuple[str, ...]

    @property
    def status(self) -> WallAxialStatus:
        """Return PASS only when both reinforcement directions pass."""
        if (
            self.vertical.status is WallAxialStatus.PASS
            and self.horizontal.status is WallAxialStatus.PASS
            and not self.transverse_enclosure_required
        ):
            return WallAxialStatus.PASS
        return WallAxialStatus.FAIL


def _provided_area_mm2_per_m(diameter_mm: float, spacing_mm: float) -> float:
    return math.pi * diameter_mm**2 / 4.0 * 1000.0 / spacing_mm


def _direction_result(
    *,
    minimum_ratio: float,
    wall_thickness_mm: float,
    bar_diameter_mm: float,
    bar_spacing_mm: float,
) -> WallDirectionalReinforcementResult:
    gross_area_mm2_per_m = wall_thickness_mm * 1000.0
    required_area_mm2_per_m = minimum_ratio * gross_area_mm2_per_m
    provided_area_mm2_per_m = _provided_area_mm2_per_m(
        bar_diameter_mm,
        bar_spacing_mm,
    )
    provided_ratio = provided_area_mm2_per_m / gross_area_mm2_per_m
    maximum_spacing_mm = min(3.0 * wall_thickness_mm, 450.0)
    return WallDirectionalReinforcementResult(
        minimum_ratio=minimum_ratio,
        required_area_mm2_per_m=required_area_mm2_per_m,
        provided_area_mm2_per_m=provided_area_mm2_per_m,
        provided_ratio=provided_ratio,
        maximum_spacing_mm=maximum_spacing_mm,
        provided_spacing_mm=bar_spacing_mm,
        area_status=(
            WallAxialStatus.PASS
            if provided_area_mm2_per_m >= required_area_mm2_per_m
            else WallAxialStatus.FAIL
        ),
        spacing_status=(
            WallAxialStatus.PASS
            if bar_spacing_mm <= maximum_spacing_mm
            else WallAxialStatus.FAIL
        ),
    )


@clause("32.5", "32.5.1", "32.5.2")
def check_wall_minimum_reinforcement(
    reinforcement_input: WallReinforcementInput,
) -> WallReinforcementResult:
    """Check caller-provided wall steel against Clause 32.5 minimums.

    The geometry contract already excludes walls thicker than 200 mm, for which
    Clause 32.5.1 requires two reinforcement grids. If the provided vertical
    ratio exceeds 0.01, this bounded route fails closed because the Clause
    32.5.2 transverse-enclosure exception no longer applies automatically.
    """
    if not isinstance(reinforcement_input, WallReinforcementInput):
        raise WallContractError("reinforcement_input must be a WallReinforcementInput")

    if reinforcement_input.reinforcement_kind in {
        WallReinforcementKind.DEFORMED_415_OR_GREATER,
        WallReinforcementKind.WELDED_WIRE_FABRIC,
    }:
        vertical_minimum_ratio = 0.0012
        horizontal_minimum_ratio = 0.0020
    else:
        vertical_minimum_ratio = 0.0015
        horizontal_minimum_ratio = 0.0025

    thickness_mm = reinforcement_input.geometry.wall_thickness_mm
    vertical = _direction_result(
        minimum_ratio=vertical_minimum_ratio,
        wall_thickness_mm=thickness_mm,
        bar_diameter_mm=reinforcement_input.vertical_bar_diameter_mm,
        bar_spacing_mm=reinforcement_input.vertical_bar_spacing_mm,
    )
    horizontal = _direction_result(
        minimum_ratio=horizontal_minimum_ratio,
        wall_thickness_mm=thickness_mm,
        bar_diameter_mm=reinforcement_input.horizontal_bar_diameter_mm,
        bar_spacing_mm=reinforcement_input.horizontal_bar_spacing_mm,
    )
    transverse_enclosure_required = vertical.provided_ratio > 0.01

    return WallReinforcementResult(
        input=reinforcement_input,
        vertical=vertical,
        horizontal=horizontal,
        transverse_enclosure_required=transverse_enclosure_required,
        source_refs=_SOURCE_REFS + (reinforcement_input.reinforcement_basis_reference,),
    )
