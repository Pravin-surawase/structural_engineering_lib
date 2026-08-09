# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""P7 flexural slice for a simply supported solid one-way slab strip.

This module is intentionally limited to a caller-supplied factored uniform
area load, an effective short span already carried by the P6 geometry, and a
positive design strip.  It does not select loads, supports, detailing, or
serviceability checks.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.slab.classification import (
    classify_solid_rectangular_slab,
)
from structural_lib.codes.is456.slab.models import (
    SlabClassification,
    SlabContractError,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "OneWaySlabFlexureInput",
    "OneWaySlabFlexureResult",
    "OneWaySlabFlexureStatus",
    "SlabFlexureGoverningCheck",
    "design_simply_supported_one_way_slab_flexure",
]


_DEFAULT_STRIP_WIDTH_MM = 1000.0
_MIN_FCK_N_PER_MM2 = 20.0
_MAX_FCK_N_PER_MM2 = 80.0
_SUPPORTED_FY_N_PER_MM2 = (250.0, 415.0, 500.0)
_SOURCE_REFS: tuple[str, ...] = (
    "IS456-CONSOLIDATED-PDF-SHA256: 964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
    "IS456-AMENDMENT-6-JUN-2024-SHA256: 4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881",
    "IS456-AMENDMENT-6-SLAB-CHANGE: none",
    "P7-SS-UDL-01: Mu = wu * Lx^2 / 8",
    "P7-RC-RECT-01: C = 0.36*fck*b*xu; z = d - 0.42*xu",
)
_P8_LIMITATIONS: tuple[str, ...] = (
    "P8 HOLD: minimum reinforcement is pending.",
    "P8 HOLD: bar selection, spacing, and reinforcement detailing are pending.",
    "P8 HOLD: deflection and cracking serviceability checks are pending.",
    "P8 HOLD: shear design is pending.",
    "REVIEW LIMITATION: load combinations, support moments, continuity, cantilevers, and load patterns are not inferred.",
)


class OneWaySlabFlexureStatus(StrEnum):
    """Status of the intentionally incomplete P7 flexural result."""

    FLEXURE_ONLY_PENDING_P8 = "flexure_only_pending_p8"


@dataclass(frozen=True)
class SlabFlexureGoverningCheck:
    """A passed P7 domain or flexural-resistance check with explicit units."""

    check_id: str
    actual: float
    limit: float
    unit: str
    comparison: str


def _positive_finite(value: float, field_name: str, unit: str) -> float:
    """Normalize a positive finite engineering input or fail closed."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{field_name} must be a real value in {unit}")

    normalized = float(value)
    if not math.isfinite(normalized):
        raise SlabContractError(f"{field_name} must be finite in {unit}")
    if normalized <= 0.0:
        raise SlabContractError(f"{field_name} must be positive in {unit}")
    return normalized


def _supported_fy(value: float) -> bool:
    """Return whether ``value`` is a P7 grade with an explicit xu,max/d ratio."""
    return any(abs(value - grade) < 0.5 for grade in _SUPPORTED_FY_N_PER_MM2)


@dataclass(frozen=True)
class OneWaySlabFlexureInput:
    """Caller-supplied data for one simply supported slab design strip.

    ``geometry`` contains the caller-supplied effective spans in mm.  When its
    optional strip width is absent, this P7 slice explicitly uses one metre.
    ``factored_area_load_kn_per_m2`` is already factored; this type never
    combines characteristic loads or applies load factors.
    """

    geometry: SolidRectangularSlabGeometry
    d_mm: float
    factored_area_load_kn_per_m2: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, SolidRectangularSlabGeometry):
            raise SlabContractError(
                "geometry must be a SolidRectangularSlabGeometry with effective spans in mm"
            )

        d_mm = _positive_finite(self.d_mm, "d_mm", "mm")
        if d_mm >= self.geometry.thickness_mm:
            raise SlabContractError(
                "d_mm must be less than geometry.thickness_mm for this solid slab strip"
            )
        object.__setattr__(self, "d_mm", d_mm)
        object.__setattr__(
            self,
            "factored_area_load_kn_per_m2",
            _positive_finite(
                self.factored_area_load_kn_per_m2,
                "factored_area_load_kn_per_m2",
                "kN/m2",
            ),
        )

        fck = _positive_finite(self.fck_n_per_mm2, "fck_n_per_mm2", "N/mm2")
        if not _MIN_FCK_N_PER_MM2 <= fck <= _MAX_FCK_N_PER_MM2:
            raise SlabContractError(
                "fck_n_per_mm2 must be within the P7 rectangular stress-block domain "
                "of 20 to 80 N/mm2"
            )
        object.__setattr__(self, "fck_n_per_mm2", fck)

        fy = _positive_finite(self.fy_n_per_mm2, "fy_n_per_mm2", "N/mm2")
        if not _supported_fy(fy):
            raise SlabContractError(
                "fy_n_per_mm2 must be one of the P7 supported grades: 250, 415, or 500 N/mm2"
            )
        object.__setattr__(self, "fy_n_per_mm2", fy)


@dataclass(frozen=True)
class OneWaySlabFlexureResult:
    """P7 flexural demand and raw steel requirement for one slab strip."""

    input: OneWaySlabFlexureInput
    effective_short_span_mm: float
    design_strip_width_mm: float
    line_load_kn_per_m: float
    factored_moment_knm: float
    ast_required_mm2: float
    neutral_axis_depth_mm: float
    limiting_moment_knm: float
    governing_checks: tuple[SlabFlexureGoverningCheck, ...]
    status: OneWaySlabFlexureStatus
    limitations: tuple[str, ...]
    source_refs: tuple[str, ...]


@clause("24.1", "38.1")
def design_simply_supported_one_way_slab_flexure(
    design_input: OneWaySlabFlexureInput,
) -> OneWaySlabFlexureResult:
    """Calculate P7 flexure for one simply supported solid one-way slab strip.

    The caller supplies factored uniform area load and effective spans.  The
    function converts area load to line load over a one-metre or explicit
    strip, applies P7-SS-UDL-01, and solves P7-RC-RECT-01 for raw tension
    steel.  A result always retains P8 limits instead of implying a completed
    reinforcement design.
    """
    if not isinstance(design_input, OneWaySlabFlexureInput):
        raise SlabContractError("design_input must be a OneWaySlabFlexureInput")

    classification = classify_solid_rectangular_slab(design_input.geometry)
    if classification.classification is not SlabClassification.ONE_WAY:
        raise SlabContractError(
            "P7 supports only one-way slabs with Ly/Lx greater than 2.0"
        )

    strip_width_mm = design_input.geometry.strip_width_mm or _DEFAULT_STRIP_WIDTH_MM
    strip_width_m = strip_width_mm / 1000.0
    line_load_kn_per_m = design_input.factored_area_load_kn_per_m2 * strip_width_m
    effective_short_span_mm = design_input.geometry.short_effective_span_mm
    effective_short_span_m = effective_short_span_mm / 1000.0
    factored_moment_knm = (
        line_load_kn_per_m * effective_short_span_m * effective_short_span_m / 8.0
    )

    xu_max_over_d = materials.get_xu_max_d(design_input.fy_n_per_mm2)
    limiting_moment_knm = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * design_input.fck_n_per_mm2
        * strip_width_mm
        * design_input.d_mm
        * design_input.d_mm
        / 1_000_000.0
    )
    if factored_moment_knm > limiting_moment_knm:
        raise SlabContractError(
            "factored moment exceeds the P7 singly reinforced rectangular capacity"
        )

    ast_required_mm2, neutral_axis_depth_mm = (
        calculate_ast_from_rectangular_stress_block(
            b_mm=strip_width_mm,
            d_mm=design_input.d_mm,
            factored_moment_knm=factored_moment_knm,
            fck_n_per_mm2=design_input.fck_n_per_mm2,
            fy_n_per_mm2=design_input.fy_n_per_mm2,
        )
    )
    if neutral_axis_depth_mm > xu_max_over_d * design_input.d_mm:
        raise SlabContractError(
            "P7 stress-block root exceeds the supported limiting neutral-axis depth"
        )

    return OneWaySlabFlexureResult(
        input=design_input,
        effective_short_span_mm=effective_short_span_mm,
        design_strip_width_mm=strip_width_mm,
        line_load_kn_per_m=line_load_kn_per_m,
        factored_moment_knm=factored_moment_knm,
        ast_required_mm2=ast_required_mm2,
        neutral_axis_depth_mm=neutral_axis_depth_mm,
        limiting_moment_knm=limiting_moment_knm,
        governing_checks=(
            SlabFlexureGoverningCheck(
                check_id="P7-ONE-WAY-01",
                actual=classification.span_ratio_ly_lx,
                limit=2.0,
                unit="ratio Ly/Lx",
                comparison=">",
            ),
            SlabFlexureGoverningCheck(
                check_id="P7-DEPTH-01",
                actual=design_input.d_mm,
                limit=design_input.geometry.thickness_mm,
                unit="mm",
                comparison="<",
            ),
            SlabFlexureGoverningCheck(
                check_id="P7-MU-01",
                actual=factored_moment_knm,
                limit=limiting_moment_knm,
                unit="kN m",
                comparison="<=",
            ),
        ),
        status=OneWaySlabFlexureStatus.FLEXURE_ONLY_PENDING_P8,
        limitations=_P8_LIMITATIONS,
        source_refs=_SOURCE_REFS,
    )
