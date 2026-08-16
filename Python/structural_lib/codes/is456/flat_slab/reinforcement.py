# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Bounded flexure, provided bars, and serviceability for flat slabs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.flat_slab.geometry import FlatSlabDirection
from structural_lib.codes.is456.flat_slab.models import (
    FlatSlabContractError,
    FlatSlabPanelInput,
)
from structural_lib.codes.is456.flat_slab.moments import (
    FlatSlabDirectionMoments,
    FlatSlabMomentResult,
    calculate_regular_interior_flat_slab_moments,
)
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.slab.detailing import (
    ProvidedSlabBars,
    SlabReinforcementRegionResult,
    check_slab_reinforcement_region,
)
from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.slab.serviceability import (
    SlabServiceabilityInput,
    SlabServiceabilityResult,
    check_slab_span_depth_serviceability,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "FlatSlabDetailingInput",
    "FlatSlabDirectionDetailingInput",
    "FlatSlabDirectionReinforcementResult",
    "FlatSlabRegionReinforcementResult",
    "FlatSlabReinforcementResult",
    "design_regular_interior_flat_slab_reinforcement",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 23.2.1, 26.3.3, 26.5.2.1, 31.2.1, "
    "31.7.1, 31.7.2, 31.7.3, 38.1; Figure 16",
    "IS456-2000-A6",
    "INDIA-2-FLAT-G0-NO-DROP-STRAIGHT-BAR-BOUNDARY",
)
_BASE_CONTINUOUS_SPAN_DEPTH_LIMIT = 26.0
_FLAT_SLAB_SPAN_DEPTH_FACTOR = 0.9
_SUPPORT_TOP_EXTENSION_FACTOR = 0.30


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


@dataclass(frozen=True)
class FlatSlabDirectionDetailingInput:
    """Caller-provided straight bars and support-top extension in one direction."""

    column_strip_negative_bars: ProvidedSlabBars
    column_strip_positive_bars: ProvidedSlabBars
    middle_strip_negative_bars: ProvidedSlabBars
    middle_strip_positive_bars: ProvidedSlabBars
    support_top_extension_from_face_mm: float

    def __post_init__(self) -> None:
        for name in (
            "column_strip_negative_bars",
            "column_strip_positive_bars",
            "middle_strip_negative_bars",
            "middle_strip_positive_bars",
        ):
            if not isinstance(getattr(self, name), ProvidedSlabBars):
                raise FlatSlabContractError(f"{name} must be a ProvidedSlabBars")
        object.__setattr__(
            self,
            "support_top_extension_from_face_mm",
            _positive_finite(
                self.support_top_extension_from_face_mm,
                "support_top_extension_from_face_mm",
                "mm",
            ),
        )


@dataclass(frozen=True)
class FlatSlabDetailingInput:
    """Bounded FLAT-C input with explicit bars and retained review evidence."""

    panel: FlatSlabPanelInput
    x: FlatSlabDirectionDetailingInput
    y: FlatSlabDirectionDetailingInput
    straight_bars_only: bool
    all_bottom_bars_continuous: bool
    splices_present: bool
    detailing_basis_reference: str
    serviceability_acceptance_reference: str
    serviceability_acceptance_acknowledged: bool

    def __post_init__(self) -> None:
        if not isinstance(self.panel, FlatSlabPanelInput):
            raise FlatSlabContractError("panel must be a FlatSlabPanelInput")
        for name in ("x", "y"):
            if not isinstance(getattr(self, name), FlatSlabDirectionDetailingInput):
                raise FlatSlabContractError(
                    f"{name} must be a FlatSlabDirectionDetailingInput"
                )
        if self.straight_bars_only is not True:
            raise FlatSlabContractError("straight_bars_only must be explicitly True")
        if self.all_bottom_bars_continuous is not True:
            raise FlatSlabContractError(
                "all_bottom_bars_continuous must be explicitly True"
            )
        if self.splices_present is not False:
            raise FlatSlabContractError("splices_present must be explicitly False")
        if self.serviceability_acceptance_acknowledged is not True:
            raise FlatSlabContractError(
                "serviceability_acceptance_acknowledged must be explicitly True"
            )
        object.__setattr__(
            self,
            "detailing_basis_reference",
            _non_blank(self.detailing_basis_reference, "detailing_basis_reference"),
        )
        object.__setattr__(
            self,
            "serviceability_acceptance_reference",
            _non_blank(
                self.serviceability_acceptance_reference,
                "serviceability_acceptance_reference",
            ),
        )


@dataclass(frozen=True)
class FlatSlabRegionReinforcementResult:
    """Flexure and provided-bar result for one design region."""

    region_id: str
    factored_moment_knm: float
    strip_width_mm: float
    ast_required_total_mm2: float
    ast_required_mm2_per_m: float
    neutral_axis_depth_mm: float
    limiting_neutral_axis_depth_mm: float
    limiting_moment_knm: float
    provided_check: SlabReinforcementRegionResult
    flat_slab_maximum_spacing_mm: float
    flat_slab_spacing_passed: bool

    @property
    def is_adequate(self) -> bool:
        return self.provided_check.is_adequate and self.flat_slab_spacing_passed


@dataclass(frozen=True)
class FlatSlabDirectionReinforcementResult:
    """Four design regions and support-top extension in one direction."""

    direction: FlatSlabDirection
    column_strip_negative: FlatSlabRegionReinforcementResult
    column_strip_positive: FlatSlabRegionReinforcementResult
    middle_strip_negative: FlatSlabRegionReinforcementResult
    middle_strip_positive: FlatSlabRegionReinforcementResult
    required_support_top_extension_from_face_mm: float
    provided_support_top_extension_from_face_mm: float
    support_top_extension_passed: bool

    @property
    def is_adequate(self) -> bool:
        return self.support_top_extension_passed and all(
            region.is_adequate
            for region in (
                self.column_strip_negative,
                self.column_strip_positive,
                self.middle_strip_negative,
                self.middle_strip_positive,
            )
        )


@dataclass(frozen=True)
class FlatSlabReinforcementResult:
    """Both-direction FLAT-C flexure/detailing and reviewed L/d comparison."""

    input: FlatSlabDetailingInput
    moments: FlatSlabMomentResult
    x: FlatSlabDirectionReinforcementResult
    y: FlatSlabDirectionReinforcementResult
    x_serviceability: SlabServiceabilityResult
    y_serviceability: SlabServiceabilityResult
    direct_deflection_status: str
    crack_width_status: str
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]

    @property
    def is_reinforcement_and_detailing_adequate(self) -> bool:
        return self.x.is_adequate and self.y.is_adequate

    @property
    def is_span_depth_satisfied(self) -> bool:
        return self.x_serviceability.is_satisfied and self.y_serviceability.is_satisfied


def _design_region(
    *,
    region_id: str,
    factored_moment_knm: float,
    strip_width_mm: float,
    bars: ProvidedSlabBars,
    overall_depth_mm: float,
    effective_depth_mm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
) -> FlatSlabRegionReinforcementResult:
    xu_max_over_d = materials.get_xu_max_d(fy_n_per_mm2)
    limiting_neutral_axis_depth_mm = xu_max_over_d * effective_depth_mm
    limiting_moment_knm = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * fck_n_per_mm2
        * strip_width_mm
        * effective_depth_mm**2
        / 1_000_000.0
    )
    if factored_moment_knm > limiting_moment_knm:
        raise FlatSlabContractError(
            f"{region_id} moment exceeds the singly reinforced rectangular capacity"
        )
    try:
        ast_required_total_mm2, neutral_axis_depth_mm = (
            calculate_ast_from_rectangular_stress_block(
                b_mm=strip_width_mm,
                d_mm=effective_depth_mm,
                factored_moment_knm=factored_moment_knm,
                fck_n_per_mm2=fck_n_per_mm2,
                fy_n_per_mm2=fy_n_per_mm2,
            )
        )
        if neutral_axis_depth_mm > limiting_neutral_axis_depth_mm:
            raise FlatSlabContractError(
                f"{region_id} stress-block root exceeds the limiting depth"
            )
        ast_required_mm2_per_m = ast_required_total_mm2 / (strip_width_mm / 1000.0)
        provided_check = check_slab_reinforcement_region(
            region_id=region_id,
            required_for_moment_mm2_per_m=ast_required_mm2_per_m,
            bars=bars,
            overall_depth_mm=overall_depth_mm,
            effective_depth_mm=effective_depth_mm,
            fy_n_per_mm2=fy_n_per_mm2,
        )
    except SlabContractError as exc:
        raise FlatSlabContractError(str(exc)) from exc

    flat_slab_maximum_spacing_mm = 2.0 * overall_depth_mm
    return FlatSlabRegionReinforcementResult(
        region_id=region_id,
        factored_moment_knm=factored_moment_knm,
        strip_width_mm=strip_width_mm,
        ast_required_total_mm2=ast_required_total_mm2,
        ast_required_mm2_per_m=ast_required_mm2_per_m,
        neutral_axis_depth_mm=neutral_axis_depth_mm,
        limiting_neutral_axis_depth_mm=limiting_neutral_axis_depth_mm,
        limiting_moment_knm=limiting_moment_knm,
        provided_check=provided_check,
        flat_slab_maximum_spacing_mm=flat_slab_maximum_spacing_mm,
        flat_slab_spacing_passed=bars.spacing_mm <= flat_slab_maximum_spacing_mm,
    )


def _design_direction(
    *,
    moments: FlatSlabDirectionMoments,
    detailing: FlatSlabDirectionDetailingInput,
    column_strip_width_mm: float,
    middle_strip_width_mm: float,
    overall_depth_mm: float,
    effective_depth_mm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
) -> FlatSlabDirectionReinforcementResult:
    prefix = moments.direction.value
    column_negative = _design_region(
        region_id=f"{prefix}.column_strip_negative",
        factored_moment_knm=moments.column_strip_negative_moment_knm,
        strip_width_mm=column_strip_width_mm,
        bars=detailing.column_strip_negative_bars,
        overall_depth_mm=overall_depth_mm,
        effective_depth_mm=effective_depth_mm,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    column_positive = _design_region(
        region_id=f"{prefix}.column_strip_positive",
        factored_moment_knm=moments.column_strip_positive_moment_knm,
        strip_width_mm=column_strip_width_mm,
        bars=detailing.column_strip_positive_bars,
        overall_depth_mm=overall_depth_mm,
        effective_depth_mm=effective_depth_mm,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    middle_negative = _design_region(
        region_id=f"{prefix}.middle_strip_negative",
        factored_moment_knm=moments.middle_strip_negative_moment_knm,
        strip_width_mm=middle_strip_width_mm,
        bars=detailing.middle_strip_negative_bars,
        overall_depth_mm=overall_depth_mm,
        effective_depth_mm=effective_depth_mm,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    middle_positive = _design_region(
        region_id=f"{prefix}.middle_strip_positive",
        factored_moment_knm=moments.middle_strip_positive_moment_knm,
        strip_width_mm=middle_strip_width_mm,
        bars=detailing.middle_strip_positive_bars,
        overall_depth_mm=overall_depth_mm,
        effective_depth_mm=effective_depth_mm,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    required_extension = (
        _SUPPORT_TOP_EXTENSION_FACTOR * moments.governing_clear_span_m * 1000.0
    )
    return FlatSlabDirectionReinforcementResult(
        direction=moments.direction,
        column_strip_negative=column_negative,
        column_strip_positive=column_positive,
        middle_strip_negative=middle_negative,
        middle_strip_positive=middle_positive,
        required_support_top_extension_from_face_mm=required_extension,
        provided_support_top_extension_from_face_mm=(
            detailing.support_top_extension_from_face_mm
        ),
        support_top_extension_passed=(
            detailing.support_top_extension_from_face_mm >= required_extension
        ),
    )


def _serviceability(
    *,
    effective_span_mm: float,
    effective_depth_mm: float,
    acceptance_reference: str,
) -> SlabServiceabilityResult:
    try:
        return check_slab_span_depth_serviceability(
            SlabServiceabilityInput(
                effective_span_mm=effective_span_mm,
                effective_depth_mm=effective_depth_mm,
                reviewed_base_span_depth_limit=_BASE_CONTINUOUS_SPAN_DEPTH_LIMIT,
                reviewed_aggregate_modification_factor=(_FLAT_SLAB_SPAN_DEPTH_FACTOR),
                limit_source_reference=(
                    "IS 456:2000 Cl. 23.2.1 and 31.2.1; " "INDIA-2-FLAT-G0-NO-DROP"
                ),
                limit_source_is_approved=True,
                qualified_acceptance_reference=acceptance_reference,
                qualified_acceptance_acknowledged=True,
            )
        )
    except SlabContractError as exc:
        raise FlatSlabContractError(str(exc)) from exc


@clause(
    "23.2.1",
    "26.3.3",
    "26.5.2.1",
    "31.2.1",
    "31.7.1",
    "31.7.2",
    "31.7.3",
    "Figure 16",
    "38.1",
)
def design_regular_interior_flat_slab_reinforcement(
    design_input: FlatSlabDetailingInput,
) -> FlatSlabReinforcementResult:
    """Design/check FLAT-C regions and reviewed L/d for the frozen panel."""
    if not isinstance(design_input, FlatSlabDetailingInput):
        raise FlatSlabContractError("design_input must be a FlatSlabDetailingInput")

    moments = calculate_regular_interior_flat_slab_moments(design_input.panel)
    geometry = moments.geometry
    panel_geometry = design_input.panel.geometry
    material = design_input.panel.material
    common = {
        "overall_depth_mm": panel_geometry.overall_depth_mm,
        "effective_depth_mm": panel_geometry.conservative_effective_depth_mm,
        "fck_n_per_mm2": material.concrete_grade_nmm2,
        "fy_n_per_mm2": material.steel_grade_nmm2,
    }
    x = _design_direction(
        moments=moments.x,
        detailing=design_input.x,
        column_strip_width_mm=geometry.x.column_strip_total_width_mm,
        middle_strip_width_mm=geometry.x.middle_strip_width_mm,
        **common,
    )
    y = _design_direction(
        moments=moments.y,
        detailing=design_input.y,
        column_strip_width_mm=geometry.y.column_strip_total_width_mm,
        middle_strip_width_mm=geometry.y.middle_strip_width_mm,
        **common,
    )
    x_serviceability = _serviceability(
        effective_span_mm=geometry.x.centre_to_centre_span_mm,
        effective_depth_mm=panel_geometry.conservative_effective_depth_mm,
        acceptance_reference=design_input.serviceability_acceptance_reference,
    )
    y_serviceability = _serviceability(
        effective_span_mm=geometry.y.centre_to_centre_span_mm,
        effective_depth_mm=panel_geometry.conservative_effective_depth_mm,
        acceptance_reference=design_input.serviceability_acceptance_reference,
    )
    return FlatSlabReinforcementResult(
        input=design_input,
        moments=moments,
        x=x,
        y=y,
        x_serviceability=x_serviceability,
        y_serviceability=y_serviceability,
        direct_deflection_status=x_serviceability.direct_deflection_status,
        crack_width_status=x_serviceability.crack_width_status,
        source_refs=_SOURCE_REFS
        + (
            design_input.detailing_basis_reference,
            design_input.serviceability_acceptance_reference,
        ),
        limitations=(
            "Direct deflection and crack-width calculations remain held.",
            "Bar selection, bends, splices, anchorage, and congestion design remain held.",
            "Only the no-drop equal-span square interior-panel Figure 16 boundary is admitted.",
            "Punching is a separate composed-workflow check; moment transfer remains held.",
        ),
    )
