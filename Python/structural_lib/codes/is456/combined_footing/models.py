# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed contracts for the bounded INDIA-2 combined-footing case."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

__all__ = [
    "CombinedFootingActionInput",
    "CombinedFootingAnalysisMethod",
    "CombinedFootingContractError",
    "CombinedFootingDesignInput",
    "CombinedFootingGeometryInput",
    "CombinedFootingInput",
    "CombinedFootingMaterialInput",
    "CombinedFootingPressureModel",
    "CombinedFootingReinforcementInput",
    "CombinedFootingSupportingAreaBasis",
    "CombinedFootingTransferInput",
]


_SUPPORTED_CONCRETE_GRADES_NMM2 = (20.0, 25.0, 30.0, 35.0, 40.0)
_SUPPORTED_STEEL_GRADES_NMM2 = (415.0, 500.0)
_SUPPORTED_BAR_DIAMETERS_MM = (8.0, 10.0, 12.0, 16.0, 20.0, 25.0, 32.0, 36.0)


class CombinedFootingContractError(ValueError):
    """Raised when an input is outside the G0-frozen combined-footing scope."""


class CombinedFootingAnalysisMethod(StrEnum):
    """Analysis methods admitted by the first combined-footing workflow."""

    CONVENTIONAL_RIGID = "conventional_rigid"


class CombinedFootingPressureModel(StrEnum):
    """Soil-pressure models admitted by the first combined-footing workflow."""

    UNIFORM = "uniform"


class CombinedFootingSupportingAreaBasis(StrEnum):
    """Approved geometry basis for the supporting concrete bearing area."""

    LARGEST_FRUSTUM_1V_2H = "largest_frustum_1v_2h"


def _positive_finite(value: object, field_name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise CombinedFootingContractError(
            f"{field_name} must be a real value in {unit}"
        )
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise CombinedFootingContractError(
            f"{field_name} must be finite and positive in {unit}"
        )
    return normalized


def _non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CombinedFootingContractError(f"{field_name} must be non-blank")
    return value.strip()


def _require_bool(value: object, field_name: str, expected: bool) -> None:
    if value is not expected:
        raise CombinedFootingContractError(
            f"{field_name} must be explicitly {expected}"
        )


def _supported_discrete_value(
    value: object,
    field_name: str,
    unit: str,
    supported: tuple[float, ...],
) -> float:
    normalized = _positive_finite(value, field_name, unit)
    if normalized not in supported:
        choices = ", ".join(f"{candidate:g}" for candidate in supported)
        raise CombinedFootingContractError(
            f"{field_name} must be one of {choices} {unit}"
        )
    return normalized


@dataclass(frozen=True)
class CombinedFootingGeometryInput:
    """Caller-confirmed geometry and rigid-analysis eligibility.

    Dimensions are in mm. The type deliberately represents only two identical
    square columns centred across one rectangular, constant-depth footing.
    Explicit applicability carriers prevent alternate foundation systems from
    entering through omitted or defaulted assumptions.
    """

    footing_length_mm: float
    footing_width_mm: float
    overall_depth_mm: float
    effective_depth_mm: float
    column_side_mm: float
    left_column_center_x_mm: float
    right_column_center_x_mm: float
    column_count: int
    columns_identical: bool
    columns_square: bool
    columns_centered_across_width: bool
    foundation_on_soil: bool
    constant_depth: bool
    openings_present: bool
    pedestals_present: bool
    analysis_method: CombinedFootingAnalysisMethod
    pressure_model: CombinedFootingPressureModel
    rigid_footing_verified: bool
    rigidity_basis_reference: str
    geometry_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "footing_length_mm",
            "footing_width_mm",
            "overall_depth_mm",
            "effective_depth_mm",
            "column_side_mm",
            "left_column_center_x_mm",
            "right_column_center_x_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )

        if isinstance(self.column_count, bool) or not isinstance(
            self.column_count, int
        ):
            raise CombinedFootingContractError("column_count must be an integer")
        if self.column_count != 2:
            raise CombinedFootingContractError(
                "column_count must equal 2 for the frozen combined-footing case"
            )
        if self.footing_length_mm <= self.footing_width_mm:
            raise CombinedFootingContractError(
                "footing_length_mm must exceed footing_width_mm for the rectangular route"
            )
        if self.overall_depth_mm < 150.0:
            raise CombinedFootingContractError(
                "overall_depth_mm must be at least 150 mm for a footing on soil"
            )
        if self.effective_depth_mm >= self.overall_depth_mm:
            raise CombinedFootingContractError(
                "effective_depth_mm must be less than overall_depth_mm"
            )
        if self.column_side_mm >= self.footing_width_mm:
            raise CombinedFootingContractError(
                "column_side_mm must be less than footing_width_mm"
            )
        if self.left_column_center_x_mm >= self.right_column_center_x_mm:
            raise CombinedFootingContractError(
                "left_column_center_x_mm must be less than right_column_center_x_mm"
            )

        for name in (
            "columns_identical",
            "columns_square",
            "columns_centered_across_width",
            "foundation_on_soil",
            "constant_depth",
            "rigid_footing_verified",
        ):
            _require_bool(getattr(self, name), name, True)
        for name in ("openings_present", "pedestals_present"):
            _require_bool(getattr(self, name), name, False)

        if self.analysis_method is not CombinedFootingAnalysisMethod.CONVENTIONAL_RIGID:
            raise CombinedFootingContractError(
                "analysis_method must be CombinedFootingAnalysisMethod.CONVENTIONAL_RIGID"
            )
        if self.pressure_model is not CombinedFootingPressureModel.UNIFORM:
            raise CombinedFootingContractError(
                "pressure_model must be CombinedFootingPressureModel.UNIFORM"
            )

        left_end_projection = self.left_column_center_x_mm - self.column_side_mm / 2.0
        right_end_projection = self.footing_length_mm - (
            self.right_column_center_x_mm + self.column_side_mm / 2.0
        )
        if left_end_projection <= 0.0 or right_end_projection <= 0.0:
            raise CombinedFootingContractError(
                "both complete column faces must lie inside the footing length"
            )
        if not math.isclose(
            left_end_projection,
            right_end_projection,
            rel_tol=0.0,
            abs_tol=1e-6,
        ):
            raise CombinedFootingContractError(
                "column positions must provide equal longitudinal end projections"
            )
        if left_end_projection + 1e-9 < self.effective_depth_mm:
            raise CombinedFootingContractError(
                "equal end projection must be at least effective_depth_mm"
            )

        clear_gap = (
            self.right_column_center_x_mm
            - self.left_column_center_x_mm
            - self.column_side_mm
        )
        if clear_gap + 1e-9 < 2.0 * self.effective_depth_mm:
            raise CombinedFootingContractError(
                "clear inter-column gap must be at least twice effective_depth_mm"
            )
        transverse_cantilever = (self.footing_width_mm - self.column_side_mm) / 2.0
        if transverse_cantilever + 1e-9 < self.effective_depth_mm:
            raise CombinedFootingContractError(
                "transverse column-face cantilever must be at least effective_depth_mm"
            )

        critical_side = self.column_side_mm + self.effective_depth_mm
        if critical_side >= self.footing_width_mm:
            raise CombinedFootingContractError(
                "complete transverse punching perimeter must lie inside the footing"
            )
        left_punch_edge = self.left_column_center_x_mm - critical_side / 2.0
        right_punch_edge = self.right_column_center_x_mm + critical_side / 2.0
        if left_punch_edge <= 0.0 or right_punch_edge >= self.footing_length_mm:
            raise CombinedFootingContractError(
                "both complete longitudinal punching perimeters must lie inside the footing"
            )
        if (
            self.right_column_center_x_mm - self.left_column_center_x_mm
            <= critical_side
        ):
            raise CombinedFootingContractError(
                "column punching perimeters must not overlap"
            )

        object.__setattr__(
            self,
            "rigidity_basis_reference",
            _non_blank(self.rigidity_basis_reference, "rigidity_basis_reference"),
        )
        object.__setattr__(
            self,
            "geometry_basis_reference",
            _non_blank(self.geometry_basis_reference, "geometry_basis_reference"),
        )


@dataclass(frozen=True)
class CombinedFootingActionInput:
    """Approved-basis service and factored actions for the symmetric case."""

    service_axial_load_each_kn: float
    factored_axial_load_each_kn: float
    service_uniform_carrier_kn_per_m2: float
    factored_uniform_carrier_kn_per_m2: float
    allowable_gross_bearing_pressure_kn_per_m2: float
    load_combination_approved: bool
    bearing_and_settlement_approved: bool
    pressure_uniformity_approved: bool
    distributed_carrier_cancellation_approved: bool
    column_moments_present: bool
    horizontal_actions_present: bool
    uplift_or_load_reversal_present: bool
    load_basis_reference: str
    bearing_settlement_basis_reference: str
    cancellation_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "service_axial_load_each_kn",
            "factored_axial_load_each_kn",
            "service_uniform_carrier_kn_per_m2",
            "factored_uniform_carrier_kn_per_m2",
            "allowable_gross_bearing_pressure_kn_per_m2",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "kN or kN/m2"),
            )

        if self.factored_axial_load_each_kn < self.service_axial_load_each_kn:
            raise CombinedFootingContractError(
                "factored_axial_load_each_kn must not be less than service load"
            )
        column_factor = (
            self.factored_axial_load_each_kn / self.service_axial_load_each_kn
        )
        carrier_factor = (
            self.factored_uniform_carrier_kn_per_m2
            / self.service_uniform_carrier_kn_per_m2
        )
        if not math.isclose(
            column_factor,
            carrier_factor,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise CombinedFootingContractError(
                "column and distributed carrier factored/service ratios must match"
            )

        for name in (
            "load_combination_approved",
            "bearing_and_settlement_approved",
            "pressure_uniformity_approved",
            "distributed_carrier_cancellation_approved",
        ):
            _require_bool(getattr(self, name), name, True)
        for name in (
            "column_moments_present",
            "horizontal_actions_present",
            "uplift_or_load_reversal_present",
        ):
            _require_bool(getattr(self, name), name, False)

        for name in (
            "load_basis_reference",
            "bearing_settlement_basis_reference",
            "cancellation_basis_reference",
        ):
            object.__setattr__(
                self,
                name,
                _non_blank(getattr(self, name), name),
            )


@dataclass(frozen=True)
class CombinedFootingInput:
    """Complete input to the bounded combined-footing action kernel."""

    geometry: CombinedFootingGeometryInput
    actions: CombinedFootingActionInput

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, CombinedFootingGeometryInput):
            raise CombinedFootingContractError(
                "geometry must be a CombinedFootingGeometryInput"
            )
        if not isinstance(self.actions, CombinedFootingActionInput):
            raise CombinedFootingContractError(
                "actions must be a CombinedFootingActionInput"
            )


@dataclass(frozen=True)
class CombinedFootingMaterialInput:
    """Material grades admitted by the bounded strength check.

    Stresses are in N/mm2. Coated reinforcement remains outside this packet
    because its revised Amendment 6 bond basis is a separately held case.
    """

    footing_concrete_grade_nmm2: float
    column_concrete_grade_nmm2: float
    steel_grade_nmm2: float
    uncoated_deformed_bars: bool
    material_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "footing_concrete_grade_nmm2",
            "column_concrete_grade_nmm2",
        ):
            object.__setattr__(
                self,
                name,
                _supported_discrete_value(
                    getattr(self, name),
                    name,
                    "N/mm2",
                    _SUPPORTED_CONCRETE_GRADES_NMM2,
                ),
            )
        object.__setattr__(
            self,
            "steel_grade_nmm2",
            _supported_discrete_value(
                self.steel_grade_nmm2,
                "steel_grade_nmm2",
                "N/mm2",
                _SUPPORTED_STEEL_GRADES_NMM2,
            ),
        )
        _require_bool(
            self.uncoated_deformed_bars,
            "uncoated_deformed_bars",
            True,
        )
        object.__setattr__(
            self,
            "material_basis_reference",
            _non_blank(self.material_basis_reference, "material_basis_reference"),
        )


@dataclass(frozen=True)
class CombinedFootingReinforcementInput:
    """Caller-supplied bars and detailing evidence for the frozen case.

    Diameters, spacings, cover, aggregate size and available straight
    anchorage are in mm. Inadequate but otherwise valid provision produces a
    design ``FAIL``; values outside the represented material/layout domain
    fail closed at this contract.
    """

    top_longitudinal_diameter_mm: float
    top_longitudinal_spacing_mm: float
    bottom_longitudinal_diameter_mm: float
    bottom_longitudinal_spacing_mm: float
    transverse_diameter_mm: float
    transverse_spacing_mm: float
    nominal_cover_mm: float
    aggregate_size_mm: float
    available_top_longitudinal_anchorage_each_end_mm: float
    available_bottom_longitudinal_anchorage_each_end_mm: float
    available_transverse_anchorage_each_edge_mm: float
    straight_uncoated_deformed_bars: bool
    effective_depth_basis_approved: bool
    reinforcement_schedule_approved: bool
    detailing_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "top_longitudinal_diameter_mm",
            "bottom_longitudinal_diameter_mm",
            "transverse_diameter_mm",
        ):
            object.__setattr__(
                self,
                name,
                _supported_discrete_value(
                    getattr(self, name),
                    name,
                    "mm",
                    _SUPPORTED_BAR_DIAMETERS_MM,
                ),
            )
        for name in (
            "top_longitudinal_spacing_mm",
            "bottom_longitudinal_spacing_mm",
            "transverse_spacing_mm",
            "nominal_cover_mm",
            "aggregate_size_mm",
            "available_top_longitudinal_anchorage_each_end_mm",
            "available_bottom_longitudinal_anchorage_each_end_mm",
            "available_transverse_anchorage_each_edge_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )
        for name in (
            "straight_uncoated_deformed_bars",
            "effective_depth_basis_approved",
            "reinforcement_schedule_approved",
        ):
            _require_bool(getattr(self, name), name, True)
        object.__setattr__(
            self,
            "detailing_basis_reference",
            _non_blank(self.detailing_basis_reference, "detailing_basis_reference"),
        )


@dataclass(frozen=True)
class CombinedFootingTransferInput:
    """Approved bearing-frustum and dowel provision at both equal columns.

    The represented columns are identical, so one explicit provision applies
    at each column. Areas are in mm2 and lengths are in mm.
    """

    effective_supporting_area_each_mm2: float
    effective_supporting_area_basis: CombinedFootingSupportingAreaBasis
    effective_supporting_area_approved: bool
    dowel_count_each: int
    dowel_diameter_mm: float
    column_longitudinal_bar_diameter_mm: float
    available_dowel_development_into_footing_mm: float
    available_dowel_development_into_column_mm: float
    uncoated_deformed_dowels: bool
    transfer_basis_reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "effective_supporting_area_each_mm2",
            _positive_finite(
                self.effective_supporting_area_each_mm2,
                "effective_supporting_area_each_mm2",
                "mm2",
            ),
        )
        if self.effective_supporting_area_basis is not (
            CombinedFootingSupportingAreaBasis.LARGEST_FRUSTUM_1V_2H
        ):
            raise CombinedFootingContractError(
                "effective_supporting_area_basis must be "
                "CombinedFootingSupportingAreaBasis.LARGEST_FRUSTUM_1V_2H"
            )
        _require_bool(
            self.effective_supporting_area_approved,
            "effective_supporting_area_approved",
            True,
        )
        if isinstance(self.dowel_count_each, bool) or not isinstance(
            self.dowel_count_each, int
        ):
            raise CombinedFootingContractError("dowel_count_each must be an integer")
        if self.dowel_count_each <= 0:
            raise CombinedFootingContractError(
                "dowel_count_each must be a positive integer"
            )
        object.__setattr__(
            self,
            "dowel_diameter_mm",
            _supported_discrete_value(
                self.dowel_diameter_mm,
                "dowel_diameter_mm",
                "mm",
                _SUPPORTED_BAR_DIAMETERS_MM,
            ),
        )
        column_bar_diameter = _positive_finite(
            self.column_longitudinal_bar_diameter_mm,
            "column_longitudinal_bar_diameter_mm",
            "mm",
        )
        if column_bar_diameter > 36.0:
            raise CombinedFootingContractError(
                "column_longitudinal_bar_diameter_mm above 36 mm requires the held "
                "Clause 34.4.4 arrangement"
            )
        object.__setattr__(
            self,
            "column_longitudinal_bar_diameter_mm",
            _supported_discrete_value(
                column_bar_diameter,
                "column_longitudinal_bar_diameter_mm",
                "mm",
                _SUPPORTED_BAR_DIAMETERS_MM,
            ),
        )
        for name in (
            "available_dowel_development_into_footing_mm",
            "available_dowel_development_into_column_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )
        _require_bool(
            self.uncoated_deformed_dowels,
            "uncoated_deformed_dowels",
            True,
        )
        object.__setattr__(
            self,
            "transfer_basis_reference",
            _non_blank(self.transfer_basis_reference, "transfer_basis_reference"),
        )


@dataclass(frozen=True)
class CombinedFootingDesignInput:
    """Complete input to the bounded combined-footing strength composition."""

    analysis: CombinedFootingInput
    material: CombinedFootingMaterialInput
    reinforcement: CombinedFootingReinforcementInput
    transfer: CombinedFootingTransferInput

    def __post_init__(self) -> None:
        expected_types = (
            ("analysis", CombinedFootingInput),
            ("material", CombinedFootingMaterialInput),
            ("reinforcement", CombinedFootingReinforcementInput),
            ("transfer", CombinedFootingTransferInput),
        )
        for name, expected_type in expected_types:
            if not isinstance(getattr(self, name), expected_type):
                raise CombinedFootingContractError(
                    f"{name} must be a {expected_type.__name__}"
                )
