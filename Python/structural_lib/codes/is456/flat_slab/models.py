# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed contracts for the bounded INDIA-2 Clause 31 flat-slab case."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

__all__ = [
    "FlatSlabAnalysisMethod",
    "FlatSlabContractError",
    "FlatSlabGravityLoad",
    "FlatSlabGridGeometry",
    "FlatSlabMaterial",
    "FlatSlabPanelInput",
    "FlatSlabPanelLocation",
]


class FlatSlabContractError(ValueError):
    """Raised when an input is outside the frozen INDIA-2 flat-slab scope."""


class FlatSlabAnalysisMethod(StrEnum):
    """Analysis methods admitted by the first flat-slab workflow."""

    DIRECT_DESIGN = "direct_design"


class FlatSlabPanelLocation(StrEnum):
    """Panel locations admitted by the first flat-slab workflow."""

    INTERIOR = "interior"


def _positive_finite(value: float, field_name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise FlatSlabContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise FlatSlabContractError(
            f"{field_name} must be finite and positive in {unit}"
        )
    return normalized


def _positive_integer(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise FlatSlabContractError(f"{field_name} must be a positive integer")
    return value


def _non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FlatSlabContractError(f"{field_name} must be a non-blank string")
    return value.strip()


@dataclass(frozen=True)
class FlatSlabGridGeometry:
    """Caller-confirmed geometry for the first equal-span square panel.

    All dimensions are in mm. The contract deliberately rejects every
    topology that would require exterior-panel, drop/head, opening, offset,
    unequal-span, equivalent-frame, or FEM treatment.
    """

    centre_to_centre_span_x_mm: float
    centre_to_centre_span_y_mm: float
    continuous_span_count_x: int
    continuous_span_count_y: int
    column_width_x_mm: float
    column_width_y_mm: float
    overall_depth_mm: float
    conservative_effective_depth_mm: float
    analysis_method: FlatSlabAnalysisMethod
    panel_location: FlatSlabPanelLocation
    all_spans_equal_x: bool
    all_spans_equal_y: bool
    columns_offset_from_grid: bool
    solid_slab: bool
    drop_present: bool
    column_head_present: bool
    marginal_beam_or_wall_present: bool
    openings_present: bool
    geometry_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "centre_to_centre_span_x_mm",
            "centre_to_centre_span_y_mm",
            "column_width_x_mm",
            "column_width_y_mm",
            "overall_depth_mm",
            "conservative_effective_depth_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )
        for name in ("continuous_span_count_x", "continuous_span_count_y"):
            object.__setattr__(
                self,
                name,
                _positive_integer(getattr(self, name), name),
            )
            if getattr(self, name) < 3:
                raise FlatSlabContractError(
                    f"{name} must be at least 3 for the direct design route"
                )

        if not math.isclose(
            self.centre_to_centre_span_x_mm,
            self.centre_to_centre_span_y_mm,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise FlatSlabContractError(
                "centre_to_centre spans must be equal for the square-panel route"
            )
        if not math.isclose(
            self.column_width_x_mm,
            self.column_width_y_mm,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise FlatSlabContractError(
                "column widths must be equal for the square-column route"
            )
        if self.column_width_x_mm >= self.centre_to_centre_span_x_mm:
            raise FlatSlabContractError(
                "column_width_x_mm must be less than the panel span"
            )
        if self.column_width_y_mm >= self.centre_to_centre_span_y_mm:
            raise FlatSlabContractError(
                "column_width_y_mm must be less than the panel span"
            )
        if self.overall_depth_mm < 125.0:
            raise FlatSlabContractError(
                "overall_depth_mm must be at least 125 mm for a flat slab"
            )
        if self.conservative_effective_depth_mm >= self.overall_depth_mm:
            raise FlatSlabContractError(
                "conservative_effective_depth_mm must be less than overall_depth_mm"
            )
        if self.analysis_method is not FlatSlabAnalysisMethod.DIRECT_DESIGN:
            raise FlatSlabContractError(
                "analysis_method must be FlatSlabAnalysisMethod.DIRECT_DESIGN"
            )
        if self.panel_location is not FlatSlabPanelLocation.INTERIOR:
            raise FlatSlabContractError(
                "panel_location must be FlatSlabPanelLocation.INTERIOR"
            )

        required_true = (
            "all_spans_equal_x",
            "all_spans_equal_y",
            "solid_slab",
        )
        for name in required_true:
            if getattr(self, name) is not True:
                raise FlatSlabContractError(f"{name} must be explicitly True")
        required_false = (
            "columns_offset_from_grid",
            "drop_present",
            "column_head_present",
            "marginal_beam_or_wall_present",
            "openings_present",
        )
        for name in required_false:
            if getattr(self, name) is not False:
                raise FlatSlabContractError(f"{name} must be explicitly False")
        object.__setattr__(
            self,
            "geometry_basis_reference",
            _non_blank(self.geometry_basis_reference, "geometry_basis_reference"),
        )


@dataclass(frozen=True)
class FlatSlabMaterial:
    """Concrete and reinforcement grades for the G0-frozen case."""

    concrete_grade_nmm2: float
    steel_grade_nmm2: float
    uncoated_deformed_bars: bool
    material_basis_reference: str

    def __post_init__(self) -> None:
        concrete_grade = _positive_finite(
            self.concrete_grade_nmm2,
            "concrete_grade_nmm2",
            "N/mm2",
        )
        if concrete_grade not in {
            20.0,
            25.0,
            30.0,
            35.0,
            40.0,
            45.0,
            50.0,
            55.0,
            60.0,
        }:
            raise FlatSlabContractError(
                "concrete_grade_nmm2 must be a standard M20-M60 grade"
            )
        steel_grade = _positive_finite(
            self.steel_grade_nmm2,
            "steel_grade_nmm2",
            "N/mm2",
        )
        if steel_grade not in {415.0, 500.0}:
            raise FlatSlabContractError(
                "steel_grade_nmm2 must be Fe415 or Fe500 for this route"
            )
        if self.uncoated_deformed_bars is not True:
            raise FlatSlabContractError(
                "uncoated_deformed_bars must be explicitly True"
            )
        object.__setattr__(self, "concrete_grade_nmm2", concrete_grade)
        object.__setattr__(self, "steel_grade_nmm2", steel_grade)
        object.__setattr__(
            self,
            "material_basis_reference",
            _non_blank(self.material_basis_reference, "material_basis_reference"),
        )


@dataclass(frozen=True)
class FlatSlabGravityLoad:
    """Approved-basis uniform gravity actions; the library generates no load."""

    service_dead_load_kn_per_m2: float
    service_live_load_kn_per_m2: float
    factored_uniform_load_kn_per_m2: float
    self_weight_included: bool
    identical_full_loading_on_represented_panels: bool
    patterned_loading_required: bool
    unbalanced_or_lateral_moment_transfer_present: bool
    load_combination_approved: bool
    load_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "service_dead_load_kn_per_m2",
            "service_live_load_kn_per_m2",
            "factored_uniform_load_kn_per_m2",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "kN/m2"),
            )
        live_dead_ratio = (
            self.service_live_load_kn_per_m2 / self.service_dead_load_kn_per_m2
        )
        if live_dead_ratio > 0.5 + 1e-12:
            raise FlatSlabContractError(
                "service live/dead load ratio must not exceed 0.5 for this route"
            )
        expected_factored_load = 1.5 * (
            self.service_dead_load_kn_per_m2 + self.service_live_load_kn_per_m2
        )
        if not math.isclose(
            self.factored_uniform_load_kn_per_m2,
            expected_factored_load,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise FlatSlabContractError(
                "factored_uniform_load_kn_per_m2 must equal 1.5 times the "
                "service dead-plus-live load for this route"
            )
        required_true = (
            "self_weight_included",
            "identical_full_loading_on_represented_panels",
            "load_combination_approved",
        )
        for name in required_true:
            if getattr(self, name) is not True:
                raise FlatSlabContractError(f"{name} must be explicitly True")
        required_false = (
            "patterned_loading_required",
            "unbalanced_or_lateral_moment_transfer_present",
        )
        for name in required_false:
            if getattr(self, name) is not False:
                raise FlatSlabContractError(f"{name} must be explicitly False")
        object.__setattr__(
            self,
            "load_basis_reference",
            _non_blank(self.load_basis_reference, "load_basis_reference"),
        )


@dataclass(frozen=True)
class FlatSlabPanelInput:
    """Complete typed input foundation for later FLAT-B-D calculations."""

    geometry: FlatSlabGridGeometry
    material: FlatSlabMaterial
    gravity_load: FlatSlabGravityLoad

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, FlatSlabGridGeometry):
            raise FlatSlabContractError("geometry must be a FlatSlabGridGeometry")
        if not isinstance(self.material, FlatSlabMaterial):
            raise FlatSlabContractError("material must be a FlatSlabMaterial")
        if not isinstance(self.gravity_load, FlatSlabGravityLoad):
            raise FlatSlabContractError("gravity_load must be a FlatSlabGravityLoad")
