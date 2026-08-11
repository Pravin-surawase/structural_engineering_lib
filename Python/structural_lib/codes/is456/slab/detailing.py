# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Reusable provided-bar checks for slab reinforcement regions."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.slab.models import SlabContractError

__all__ = [
    "ProvidedSlabBars",
    "SlabReinforcementRegionResult",
    "check_slab_reinforcement_region",
    "minimum_slab_reinforcement_mm2_per_m",
]


@dataclass(frozen=True)
class ProvidedSlabBars:
    diameter_mm: float
    spacing_mm: float

    def __post_init__(self) -> None:
        for name in ("diameter_mm", "spacing_mm"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SlabContractError(f"{name} must be a real value in mm")
            normalized = float(value)
            if not math.isfinite(normalized) or normalized <= 0.0:
                raise SlabContractError(f"{name} must be finite and positive in mm")
            object.__setattr__(self, name, normalized)

    @property
    def area_mm2_per_m(self) -> float:
        return math.pi * self.diameter_mm**2 / 4.0 * 1000.0 / self.spacing_mm


def minimum_slab_reinforcement_mm2_per_m(
    *, overall_depth_mm: float, fy_n_per_mm2: float
) -> float:
    if abs(fy_n_per_mm2 - 250.0) < 0.5:
        ratio = 0.0015
    elif any(abs(fy_n_per_mm2 - grade) < 0.5 for grade in (415.0, 500.0)):
        ratio = 0.0012
    else:
        raise SlabContractError("fy_n_per_mm2 must be 250, 415, or 500")
    return ratio * 1000.0 * overall_depth_mm


@dataclass(frozen=True)
class SlabReinforcementRegionResult:
    region_id: str
    required_for_moment_mm2_per_m: float
    minimum_required_mm2_per_m: float
    governing_required_mm2_per_m: float
    provided_mm2_per_m: float
    maximum_diameter_mm: float
    maximum_spacing_mm: float
    area_passed: bool
    diameter_passed: bool
    spacing_passed: bool

    @property
    def is_adequate(self) -> bool:
        return self.area_passed and self.diameter_passed and self.spacing_passed


def check_slab_reinforcement_region(
    *,
    region_id: str,
    required_for_moment_mm2_per_m: float,
    bars: ProvidedSlabBars,
    overall_depth_mm: float,
    effective_depth_mm: float,
    fy_n_per_mm2: float,
    distribution_only: bool = False,
) -> SlabReinforcementRegionResult:
    if not region_id.strip():
        raise SlabContractError("region_id must be non-blank")
    if required_for_moment_mm2_per_m < 0.0:
        raise SlabContractError("required_for_moment_mm2_per_m cannot be negative")
    minimum = minimum_slab_reinforcement_mm2_per_m(
        overall_depth_mm=overall_depth_mm, fy_n_per_mm2=fy_n_per_mm2
    )
    required = max(required_for_moment_mm2_per_m, minimum)
    maximum_diameter = overall_depth_mm / 8.0
    maximum_spacing = min(
        5.0 * effective_depth_mm if distribution_only else 3.0 * effective_depth_mm,
        450.0 if distribution_only else 300.0,
    )
    provided = bars.area_mm2_per_m
    return SlabReinforcementRegionResult(
        region_id=region_id,
        required_for_moment_mm2_per_m=required_for_moment_mm2_per_m,
        minimum_required_mm2_per_m=minimum,
        governing_required_mm2_per_m=required,
        provided_mm2_per_m=provided,
        maximum_diameter_mm=maximum_diameter,
        maximum_spacing_mm=maximum_spacing,
        area_passed=provided >= required,
        diameter_passed=bars.diameter_mm <= maximum_diameter,
        spacing_passed=bars.spacing_mm <= maximum_spacing,
    )
