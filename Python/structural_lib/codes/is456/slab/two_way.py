# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""P10 bounded two-way slab flexure using qualified external coefficients.

This module intentionally contains no coefficient table, lookup, interpolation,
or assertion that externally supplied coefficients are correct.  It supports
only one caller-declared interior solid rectangular panel configuration.
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
from structural_lib.codes.is456.slab.external_coefficients import (
    ExternalCoefficientReviewStatus,
    ExternalTwoWaySlabCoefficientRecord,
)
from structural_lib.codes.is456.slab.models import SlabClassification, SlabContractError
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID",
    "TwoWaySlabCornerTorsionStatus",
    "TwoWaySlabFlexuralDirectionResult",
    "TwoWaySlabFlexureInput",
    "TwoWaySlabFlexureResult",
    "TwoWaySlabFlexureStatus",
    "design_supported_interior_two_way_slab_flexure",
]


SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID = (
    "P10-INTERIOR-SOLID-RECTANGULAR-FOUR-EDGES-CONTINUOUS-01"
)
_DEFAULT_STRIP_WIDTH_MM = 1000.0
_MIN_FCK_N_PER_MM2 = 20.0
_MAX_FCK_N_PER_MM2 = 80.0
_SUPPORTED_FY_N_PER_MM2 = (250.0, 415.0, 500.0)
_SOURCE_REFS: tuple[str, ...] = (
    "IS456-CONSOLIDATED-PDF-SHA256: 964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
    "IS456-AMENDMENT-6-JUN-2024-SHA256: 4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881",
    "IS456-AMENDMENT-6-SLAB-CHANGE: none",
    "P10-EXT-COEFF-01: Mx = alpha_x * wu * Lx^2; My = alpha_y * wu * Lx^2",
    "P7-RC-RECT-01: C = 0.36*fck*b*xu; z = d - 0.42*xu",
)
_EXCLUSIONS: tuple[str, ...] = (
    "P10 excludes bar selection, spacing, minimum steel, and reinforcement detailing.",
    "P10 excludes serviceability, shear, punching shear, load combinations, and load-pattern design.",
    "P10 excludes edge and corner panels, discontinuous edges, flat slabs, ribbed slabs, openings, and FEM analysis.",
    "P10 does not look up, interpolate, verify, or claim correctness of external coefficients.",
)
_P11_DEPENDENCY = "P11 dependency: a qualified structural engineer must complete the excluded design and detailing checks before construction use."


class TwoWaySlabFlexureStatus(StrEnum):
    """Status for this flexure-only P10 result."""

    FLEXURE_ONLY_PENDING_P11 = "flexure_only_pending_p11"


class TwoWaySlabCornerTorsionStatus(StrEnum):
    """Corner-torsion state for the single supported interior-panel case."""

    NOT_REQUIRED_FOR_SUPPORTED_INTERIOR_PANEL = (
        "not_required_for_supported_interior_panel"
    )


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


def _nonblank_string(value: str, field_name: str) -> str:
    """Require an explicit qualified acceptance reference."""
    if not isinstance(value, str) or not value.strip():
        raise SlabContractError(f"{field_name} must be a non-blank string")
    return value


def _supported_fy(value: float) -> bool:
    """Return whether a grade has an explicit limiting neutral-axis ratio."""
    return any(abs(value - grade) < 0.5 for grade in _SUPPORTED_FY_N_PER_MM2)


@dataclass(frozen=True)
class TwoWaySlabFlexureInput:
    """Explicit P10 inputs for one supported interior two-way slab panel.

    ``coefficient_record`` must be a P9 record for the exact P10 support-case
    identifier.  Because P9 always retains ``review_required``, P10 requires a
    separate qualified acceptance reference and literal ``True`` acknowledgement.
    """

    coefficient_record: ExternalTwoWaySlabCoefficientRecord
    qualified_coefficient_acceptance_reference: str
    qualified_coefficient_acceptance_acknowledged: bool
    is_interior_solid_rectangular_panel: bool
    all_four_edges_continuous: bool
    factored_area_load_kn_per_m2: float
    d_x_mm: float
    d_y_mm: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float

    def __post_init__(self) -> None:
        if not isinstance(self.coefficient_record, ExternalTwoWaySlabCoefficientRecord):
            raise SlabContractError(
                "coefficient_record must be an ExternalTwoWaySlabCoefficientRecord"
            )
        record = self.coefficient_record
        if (
            record.support_case_id
            != SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID
        ):
            raise SlabContractError(
                "P10 supports only its exact interior continuous support_case_id"
            )
        if record.review_status is not ExternalCoefficientReviewStatus.REVIEW_REQUIRED:
            raise SlabContractError(
                "P10 requires the P9 review_required coefficient record"
            )
        if record.coefficient_correctness_is_verified is not False:
            raise SlabContractError(
                "P10 cannot accept a P9 coefficient correctness verification"
            )
        if self.is_interior_solid_rectangular_panel is not True:
            raise SlabContractError(
                "is_interior_solid_rectangular_panel must be explicitly True for P10"
            )
        if self.all_four_edges_continuous is not True:
            raise SlabContractError(
                "all_four_edges_continuous must be explicitly True for P10"
            )
        object.__setattr__(
            self,
            "qualified_coefficient_acceptance_reference",
            _nonblank_string(
                self.qualified_coefficient_acceptance_reference,
                "qualified_coefficient_acceptance_reference",
            ),
        )
        if self.qualified_coefficient_acceptance_acknowledged is not True:
            raise SlabContractError(
                "qualified_coefficient_acceptance_acknowledged must be explicitly True"
            )

        classification = classify_solid_rectangular_slab(record.geometry)
        if classification.classification is not SlabClassification.TWO_WAY:
            raise SlabContractError("P10 requires geometry classified as two_way")
        object.__setattr__(
            self,
            "factored_area_load_kn_per_m2",
            _positive_finite(
                self.factored_area_load_kn_per_m2,
                "factored_area_load_kn_per_m2",
                "kN/m2",
            ),
        )
        for field_name in ("d_x_mm", "d_y_mm"):
            depth = _positive_finite(getattr(self, field_name), field_name, "mm")
            if depth >= record.geometry.thickness_mm:
                raise SlabContractError(
                    f"{field_name} must be less than geometry.thickness_mm for P10"
                )
            object.__setattr__(self, field_name, depth)

        fck = _positive_finite(self.fck_n_per_mm2, "fck_n_per_mm2", "N/mm2")
        if not _MIN_FCK_N_PER_MM2 <= fck <= _MAX_FCK_N_PER_MM2:
            raise SlabContractError(
                "fck_n_per_mm2 must be within the P10 rectangular stress-block domain of 20 to 80 N/mm2"
            )
        object.__setattr__(self, "fck_n_per_mm2", fck)

        fy = _positive_finite(self.fy_n_per_mm2, "fy_n_per_mm2", "N/mm2")
        if not _supported_fy(fy):
            raise SlabContractError(
                "fy_n_per_mm2 must be one of the P10 supported grades: 250, 415, or 500 N/mm2"
            )
        object.__setattr__(self, "fy_n_per_mm2", fy)


@dataclass(frozen=True)
class TwoWaySlabFlexuralDirectionResult:
    """Raw flexural demand and steel for one P10 direction and design strip."""

    direction: str
    coefficient: float
    factored_moment_knm: float
    ast_required_mm2: float
    neutral_axis_depth_mm: float
    limiting_neutral_axis_depth_mm: float
    limiting_moment_knm: float


@dataclass(frozen=True)
class TwoWaySlabFlexureResult:
    """P10 two-way flexural output with acceptance provenance and exclusions."""

    input: TwoWaySlabFlexureInput
    effective_short_span_mm: float
    design_strip_width_mm: float
    line_load_kn_per_m: float
    x_direction: TwoWaySlabFlexuralDirectionResult
    y_direction: TwoWaySlabFlexuralDirectionResult
    coefficient_source_reference: str
    coefficient_source_is_approved: bool
    qualified_coefficient_acceptance_reference: str
    qualified_coefficient_acceptance_acknowledged: bool
    corner_torsion_status: TwoWaySlabCornerTorsionStatus
    status: TwoWaySlabFlexureStatus
    source_refs: tuple[str, ...]
    assumptions: tuple[str, ...]
    exclusions: tuple[str, ...]
    units: tuple[tuple[str, str], ...]
    is_supported: bool
    p11_dependency: str


def _direction_result(
    *,
    direction: str,
    coefficient: float,
    line_load_kn_per_m: float,
    effective_short_span_m: float,
    strip_width_mm: float,
    d_mm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    xu_max_over_d: float,
) -> TwoWaySlabFlexuralDirectionResult:
    """Calculate one direction and reject a demand beyond its limiting capacity."""
    factored_moment_knm = coefficient * line_load_kn_per_m * effective_short_span_m**2
    limiting_moment_knm = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * fck_n_per_mm2
        * strip_width_mm
        * d_mm**2
        / 1_000_000.0
    )
    if factored_moment_knm > limiting_moment_knm:
        raise SlabContractError(
            f"P10 {direction}-direction factored moment exceeds the singly reinforced rectangular capacity"
        )
    ast_required_mm2, neutral_axis_depth_mm = (
        calculate_ast_from_rectangular_stress_block(
            b_mm=strip_width_mm,
            d_mm=d_mm,
            factored_moment_knm=factored_moment_knm,
            fck_n_per_mm2=fck_n_per_mm2,
            fy_n_per_mm2=fy_n_per_mm2,
        )
    )
    limiting_neutral_axis_depth_mm = xu_max_over_d * d_mm
    if neutral_axis_depth_mm > limiting_neutral_axis_depth_mm:
        raise SlabContractError(
            f"P10 {direction}-direction stress-block root exceeds the limiting neutral-axis depth"
        )
    return TwoWaySlabFlexuralDirectionResult(
        direction=direction,
        coefficient=coefficient,
        factored_moment_knm=factored_moment_knm,
        ast_required_mm2=ast_required_mm2,
        neutral_axis_depth_mm=neutral_axis_depth_mm,
        limiting_neutral_axis_depth_mm=limiting_neutral_axis_depth_mm,
        limiting_moment_knm=limiting_moment_knm,
    )


@clause("24.1", "24.4", "38.1")
def design_supported_interior_two_way_slab_flexure(
    design_input: TwoWaySlabFlexureInput,
) -> TwoWaySlabFlexureResult:
    """Calculate P10 moments and raw steel for one declared interior panel.

    The area load is converted to a line load over the default 1 m or explicit
    design strip.  The caller-supplied P9 coefficients then give
    ``Mx = alpha_x * wu * Lx^2`` and ``My = alpha_y * wu * Lx^2``.  Here ``wu``
    is that strip line load in kN/m.  P10 validates acceptance provenance but
    never validates the coefficients themselves.
    """
    if not isinstance(design_input, TwoWaySlabFlexureInput):
        raise SlabContractError("design_input must be a TwoWaySlabFlexureInput")

    record = design_input.coefficient_record
    geometry = record.geometry
    strip_width_mm = geometry.strip_width_mm or _DEFAULT_STRIP_WIDTH_MM
    line_load_kn_per_m = (
        design_input.factored_area_load_kn_per_m2 * strip_width_mm / 1000.0
    )
    effective_short_span_mm = geometry.short_effective_span_mm
    effective_short_span_m = effective_short_span_mm / 1000.0
    xu_max_over_d = materials.get_xu_max_d(design_input.fy_n_per_mm2)
    x_direction = _direction_result(
        direction="x",
        coefficient=record.alpha_x,
        line_load_kn_per_m=line_load_kn_per_m,
        effective_short_span_m=effective_short_span_m,
        strip_width_mm=strip_width_mm,
        d_mm=design_input.d_x_mm,
        fck_n_per_mm2=design_input.fck_n_per_mm2,
        fy_n_per_mm2=design_input.fy_n_per_mm2,
        xu_max_over_d=xu_max_over_d,
    )
    y_direction = _direction_result(
        direction="y",
        coefficient=record.alpha_y,
        line_load_kn_per_m=line_load_kn_per_m,
        effective_short_span_m=effective_short_span_m,
        strip_width_mm=strip_width_mm,
        d_mm=design_input.d_y_mm,
        fck_n_per_mm2=design_input.fck_n_per_mm2,
        fy_n_per_mm2=design_input.fy_n_per_mm2,
        xu_max_over_d=xu_max_over_d,
    )
    return TwoWaySlabFlexureResult(
        input=design_input,
        effective_short_span_mm=effective_short_span_mm,
        design_strip_width_mm=strip_width_mm,
        line_load_kn_per_m=line_load_kn_per_m,
        x_direction=x_direction,
        y_direction=y_direction,
        coefficient_source_reference=record.coefficient_source_reference,
        coefficient_source_is_approved=record.coefficient_source_is_approved,
        qualified_coefficient_acceptance_reference=(
            design_input.qualified_coefficient_acceptance_reference
        ),
        qualified_coefficient_acceptance_acknowledged=(
            design_input.qualified_coefficient_acceptance_acknowledged
        ),
        corner_torsion_status=(
            TwoWaySlabCornerTorsionStatus.NOT_REQUIRED_FOR_SUPPORTED_INTERIOR_PANEL
        ),
        status=TwoWaySlabFlexureStatus.FLEXURE_ONLY_PENDING_P11,
        source_refs=_SOURCE_REFS + record.source_ids,
        assumptions=(
            "The caller declares a solid rectangular interior panel with all four edges continuous.",
            "P9 retains review_required; qualified acceptance is caller-supplied provenance, not coefficient verification by P10.",
            "Effective spans are caller-supplied in mm; Lx is the P6 normalized short span.",
            "The factored uniform area load is supplied by the caller and is converted to the stated design strip.",
        ),
        exclusions=_EXCLUSIONS,
        units=(
            ("effective_short_span", "mm"),
            ("design_strip_width", "mm"),
            ("line_load", "kN/m"),
            ("factored_moment", "kN m"),
            ("steel_area", "mm2"),
            ("neutral_axis_depth", "mm"),
            ("concrete_strength", "N/mm2"),
            ("steel_strength", "N/mm2"),
            ("coefficient", "dimensionless"),
        ),
        is_supported=True,
        p11_dependency=_P11_DEPENDENCY,
    )
