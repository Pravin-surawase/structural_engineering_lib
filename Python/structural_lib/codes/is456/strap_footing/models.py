# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed contracts for the bounded INDIA-2 property-line strap footing."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

__all__ = [
    "StrapFootingActionInput",
    "StrapFootingAnalysisInput",
    "StrapFootingAnalysisMethod",
    "StrapFootingApprovalInput",
    "StrapFootingContractError",
    "StrapFootingGeometryInput",
    "StrapFootingDesignInput",
    "StrapFootingMaterialInput",
    "StrapFootingPressureModel",
    "StrapFootingReinforcementInput",
]


_SUPPORTED_CONCRETE_GRADES_NMM2 = (20.0, 25.0, 30.0, 35.0, 40.0)
_SUPPORTED_STEEL_GRADES_NMM2 = (415.0, 500.0)
_SUPPORTED_BAR_DIAMETERS_MM = (8.0, 10.0, 12.0, 16.0, 20.0, 25.0, 32.0, 36.0)


class StrapFootingContractError(ValueError):
    """Raised when input is outside the G0-frozen strap-footing scope."""


class StrapFootingAnalysisMethod(StrEnum):
    """Analysis method admitted by the first strap-footing workflow."""

    RIGID_EQUAL_PRESSURE = "rigid_equal_pressure"


class StrapFootingPressureModel(StrEnum):
    """Soil-pressure model admitted by the first strap-footing workflow."""

    EQUAL_UNIFORM_NET = "equal_uniform_net"


def _finite_real(value: object, field_name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise StrapFootingContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise StrapFootingContractError(f"{field_name} must be finite in {unit}")
    return normalized


def _positive_finite(value: object, field_name: str, unit: str) -> float:
    normalized = _finite_real(value, field_name, unit)
    if normalized <= 0.0:
        raise StrapFootingContractError(f"{field_name} must be positive in {unit}")
    return normalized


def _nonnegative_finite(value: object, field_name: str, unit: str) -> float:
    normalized = _finite_real(value, field_name, unit)
    if normalized < 0.0:
        raise StrapFootingContractError(f"{field_name} must be non-negative in {unit}")
    return normalized


def _non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StrapFootingContractError(f"{field_name} must be non-blank")
    return value.strip()


def _require_bool(value: object, field_name: str, expected: bool) -> None:
    if value is not expected:
        raise StrapFootingContractError(f"{field_name} must be explicitly {expected}")


def _supported_discrete_value(
    value: object,
    field_name: str,
    unit: str,
    supported: tuple[float, ...],
) -> float:
    normalized = _positive_finite(value, field_name, unit)
    if normalized not in supported:
        choices = ", ".join(f"{candidate:g}" for candidate in supported)
        raise StrapFootingContractError(f"{field_name} must be one of {choices} {unit}")
    return normalized


@dataclass(frozen=True)
class StrapFootingGeometryInput:
    """Caller-confirmed geometry for the G0-frozen property-line system.

    All dimensions and global longitudinal coordinates are in mm. ``x = 0``
    is the property-line edge of the exterior footing. The interior footing is
    centred on the interior column. The clear strap extends from the exterior
    footing inner edge to the interior footing outer edge.
    """

    exterior_footing_length_mm: float
    exterior_footing_width_mm: float
    exterior_footing_depth_mm: float
    interior_footing_length_mm: float
    interior_footing_width_mm: float
    interior_footing_depth_mm: float
    exterior_column_side_mm: float
    interior_column_side_mm: float
    exterior_column_center_x_mm: float
    interior_column_center_x_mm: float
    strap_width_mm: float
    strap_overall_depth_mm: float
    strap_effective_depth_mm: float
    footing_count: int
    column_count: int
    footings_rectangular: bool
    footings_parallel: bool
    footings_constant_depth: bool
    columns_square: bool
    columns_and_strap_share_centerline: bool
    interior_column_centered_on_footing: bool
    strap_straight_and_prismatic: bool
    strap_centered_across_footings: bool
    foundation_on_soil: bool
    strap_soil_contact: bool
    openings_present: bool
    pedestals_present: bool
    analysis_method: StrapFootingAnalysisMethod
    pressure_model: StrapFootingPressureModel
    geometry_basis_reference: str
    rigidity_basis_reference: str
    strap_isolation_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "exterior_footing_length_mm",
            "exterior_footing_width_mm",
            "exterior_footing_depth_mm",
            "interior_footing_length_mm",
            "interior_footing_width_mm",
            "interior_footing_depth_mm",
            "exterior_column_side_mm",
            "interior_column_side_mm",
            "exterior_column_center_x_mm",
            "interior_column_center_x_mm",
            "strap_width_mm",
            "strap_overall_depth_mm",
            "strap_effective_depth_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )

        for name, value, expected in (
            ("footing_count", self.footing_count, 2),
            ("column_count", self.column_count, 2),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise StrapFootingContractError(f"{name} must be an integer")
            if value != expected:
                raise StrapFootingContractError(
                    f"{name} must equal {expected} for the frozen strap-footing case"
                )

        for name in (
            "footings_rectangular",
            "footings_parallel",
            "footings_constant_depth",
            "columns_square",
            "columns_and_strap_share_centerline",
            "interior_column_centered_on_footing",
            "strap_straight_and_prismatic",
            "strap_centered_across_footings",
            "foundation_on_soil",
        ):
            _require_bool(getattr(self, name), name, True)
        for name in (
            "strap_soil_contact",
            "openings_present",
            "pedestals_present",
        ):
            _require_bool(getattr(self, name), name, False)

        if self.analysis_method is not StrapFootingAnalysisMethod.RIGID_EQUAL_PRESSURE:
            raise StrapFootingContractError(
                "analysis_method must be StrapFootingAnalysisMethod.RIGID_EQUAL_PRESSURE"
            )
        if self.pressure_model is not StrapFootingPressureModel.EQUAL_UNIFORM_NET:
            raise StrapFootingContractError(
                "pressure_model must be StrapFootingPressureModel.EQUAL_UNIFORM_NET"
            )

        for name in (
            "exterior_footing_depth_mm",
            "interior_footing_depth_mm",
        ):
            if getattr(self, name) < 150.0:
                raise StrapFootingContractError(
                    f"{name} must be at least 150 mm for a footing on soil"
                )
        if self.strap_effective_depth_mm >= self.strap_overall_depth_mm:
            raise StrapFootingContractError(
                "strap_effective_depth_mm must be less than strap_overall_depth_mm"
            )
        if self.strap_width_mm > min(
            self.exterior_footing_width_mm,
            self.interior_footing_width_mm,
        ):
            raise StrapFootingContractError(
                "strap_width_mm must not exceed either footing width"
            )

        for prefix in ("exterior", "interior"):
            column_side = getattr(self, f"{prefix}_column_side_mm")
            footing_length = getattr(self, f"{prefix}_footing_length_mm")
            footing_width = getattr(self, f"{prefix}_footing_width_mm")
            if column_side >= min(footing_length, footing_width):
                raise StrapFootingContractError(
                    f"{prefix}_column_side_mm must be less than both footing dimensions"
                )

        exterior_left_face = (
            self.exterior_column_center_x_mm - self.exterior_column_side_mm / 2.0
        )
        exterior_right_face = (
            self.exterior_column_center_x_mm + self.exterior_column_side_mm / 2.0
        )
        if (
            exterior_left_face <= 0.0
            or exterior_right_face >= self.exterior_footing_length_mm
        ):
            raise StrapFootingContractError(
                "the complete exterior column plan must lie inside the exterior footing"
            )
        exterior_centroid = self.exterior_footing_length_mm / 2.0
        if self.exterior_column_center_x_mm >= exterior_centroid:
            raise StrapFootingContractError(
                "exterior column must be eccentric toward the property-line edge"
            )

        interior_left_edge = (
            self.interior_column_center_x_mm - self.interior_footing_length_mm / 2.0
        )
        if interior_left_edge <= self.exterior_footing_length_mm:
            raise StrapFootingContractError(
                "footings must have positive clear separation along the strap"
            )
        clear_span = interior_left_edge - self.exterior_footing_length_mm
        if clear_span / self.strap_overall_depth_mm <= 2.5:
            raise StrapFootingContractError(
                "clear strap span-to-overall-depth ratio must exceed 2.5"
            )

        for name in (
            "geometry_basis_reference",
            "rigidity_basis_reference",
            "strap_isolation_basis_reference",
        ):
            object.__setattr__(
                self,
                name,
                _non_blank(getattr(self, name), name),
            )


@dataclass(frozen=True)
class StrapFootingActionInput:
    """Caller-approved service and factored actions for the frozen system."""

    service_exterior_column_load_kn: float
    service_interior_column_load_kn: float
    factored_exterior_column_load_kn: float
    factored_interior_column_load_kn: float
    service_clear_strap_line_load_kn_per_m: float
    factored_clear_strap_line_load_kn_per_m: float
    service_exterior_footing_carrier_kn_per_m2: float
    service_interior_footing_carrier_kn_per_m2: float
    factored_exterior_footing_carrier_kn_per_m2: float
    factored_interior_footing_carrier_kn_per_m2: float
    allowable_gross_bearing_pressure_kn_per_m2: float
    load_combination_approved: bool
    bearing_and_settlement_approved: bool
    equal_uniform_pressure_approved: bool
    footing_carrier_basis_approved: bool
    strap_line_load_basis_approved: bool
    load_pattern_compatible: bool
    column_moments_present: bool
    horizontal_actions_present: bool
    uplift_or_load_reversal_present: bool
    independently_factored_or_patterned_actions_present: bool
    load_basis_reference: str
    bearing_settlement_basis_reference: str
    footing_carrier_basis_reference: str
    strap_line_load_basis_reference: str
    load_pattern_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "service_exterior_column_load_kn",
            "service_interior_column_load_kn",
            "factored_exterior_column_load_kn",
            "factored_interior_column_load_kn",
            "allowable_gross_bearing_pressure_kn_per_m2",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "kN or kN/m2"),
            )
        for name in (
            "service_clear_strap_line_load_kn_per_m",
            "factored_clear_strap_line_load_kn_per_m",
            "service_exterior_footing_carrier_kn_per_m2",
            "service_interior_footing_carrier_kn_per_m2",
            "factored_exterior_footing_carrier_kn_per_m2",
            "factored_interior_footing_carrier_kn_per_m2",
        ):
            object.__setattr__(
                self,
                name,
                _nonnegative_finite(getattr(self, name), name, "kN/m or kN/m2"),
            )

        factor = (
            self.factored_exterior_column_load_kn / self.service_exterior_column_load_kn
        )
        if factor < 1.0:
            raise StrapFootingContractError(
                "factored actions must not be less than their service actions"
            )
        pairs = (
            (
                "interior column",
                self.service_interior_column_load_kn,
                self.factored_interior_column_load_kn,
            ),
            (
                "clear strap line load",
                self.service_clear_strap_line_load_kn_per_m,
                self.factored_clear_strap_line_load_kn_per_m,
            ),
            (
                "exterior footing carrier",
                self.service_exterior_footing_carrier_kn_per_m2,
                self.factored_exterior_footing_carrier_kn_per_m2,
            ),
            (
                "interior footing carrier",
                self.service_interior_footing_carrier_kn_per_m2,
                self.factored_interior_footing_carrier_kn_per_m2,
            ),
        )
        for label, service, factored in pairs:
            if service == 0.0:
                if factored != 0.0:
                    raise StrapFootingContractError(
                        f"zero service {label} requires zero factored {label}"
                    )
                continue
            if not math.isclose(
                factored / service,
                factor,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                raise StrapFootingContractError(
                    "all factored/service action ratios must share one common multiplier"
                )

        for name in (
            "load_combination_approved",
            "bearing_and_settlement_approved",
            "equal_uniform_pressure_approved",
            "footing_carrier_basis_approved",
            "strap_line_load_basis_approved",
            "load_pattern_compatible",
        ):
            _require_bool(getattr(self, name), name, True)
        for name in (
            "column_moments_present",
            "horizontal_actions_present",
            "uplift_or_load_reversal_present",
            "independently_factored_or_patterned_actions_present",
        ):
            _require_bool(getattr(self, name), name, False)

        for name in (
            "load_basis_reference",
            "bearing_settlement_basis_reference",
            "footing_carrier_basis_reference",
            "strap_line_load_basis_reference",
            "load_pattern_basis_reference",
        ):
            object.__setattr__(
                self,
                name,
                _non_blank(getattr(self, name), name),
            )

    @property
    def common_factored_multiplier(self) -> float:
        """Return the enforced factored-to-service action multiplier."""

        return (
            self.factored_exterior_column_load_kn / self.service_exterior_column_load_kn
        )


@dataclass(frozen=True)
class StrapFootingApprovalInput:
    """External footing, transfer, and construction prerequisites."""

    exterior_footing_design_verified: bool
    interior_footing_design_verified: bool
    column_and_strap_transfer_verified: bool
    footing_reinforcement_and_anchorage_verified: bool
    supporting_areas_verified: bool
    construction_clearances_verified: bool
    exterior_footing_verification_reference: str
    interior_footing_verification_reference: str
    transfer_verification_reference: str
    construction_verification_reference: str

    def __post_init__(self) -> None:
        for name in (
            "exterior_footing_design_verified",
            "interior_footing_design_verified",
            "column_and_strap_transfer_verified",
            "footing_reinforcement_and_anchorage_verified",
            "supporting_areas_verified",
            "construction_clearances_verified",
        ):
            _require_bool(getattr(self, name), name, True)
        for name in (
            "exterior_footing_verification_reference",
            "interior_footing_verification_reference",
            "transfer_verification_reference",
            "construction_verification_reference",
        ):
            object.__setattr__(
                self,
                name,
                _non_blank(getattr(self, name), name),
            )


@dataclass(frozen=True)
class StrapFootingAnalysisInput:
    """Complete input to the bounded property-line strap action kernel."""

    geometry: StrapFootingGeometryInput
    actions: StrapFootingActionInput
    approvals: StrapFootingApprovalInput

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, StrapFootingGeometryInput):
            raise StrapFootingContractError(
                "geometry must be a StrapFootingGeometryInput"
            )
        if not isinstance(self.actions, StrapFootingActionInput):
            raise StrapFootingContractError("actions must be a StrapFootingActionInput")
        if not isinstance(self.approvals, StrapFootingApprovalInput):
            raise StrapFootingContractError(
                "approvals must be a StrapFootingApprovalInput"
            )


@dataclass(frozen=True)
class StrapFootingMaterialInput:
    """Material grades admitted by the bounded strap strength check."""

    strap_concrete_grade_nmm2: float
    steel_grade_nmm2: float
    uncoated_deformed_bars: bool
    material_basis_reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "strap_concrete_grade_nmm2",
            _supported_discrete_value(
                self.strap_concrete_grade_nmm2,
                "strap_concrete_grade_nmm2",
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
class StrapFootingReinforcementInput:
    """Caller-supplied strap bars and approved detailing carriers.

    Valid but inadequate provision produces ``FAIL``. Unsupported layouts,
    material forms, or missing approvals fail closed before calculation.
    """

    top_bar_count: int
    top_bar_diameter_mm: float
    bottom_bar_count: int
    bottom_bar_diameter_mm: float
    side_face_bar_count_each_face: int
    side_face_bar_diameter_mm: float
    side_face_vertical_spacing_mm: float
    stirrup_leg_count: int
    stirrup_diameter_mm: float
    stirrup_spacing_mm: float
    nominal_cover_mm: float
    required_nominal_cover_mm: float
    maximum_aggregate_size_mm: float
    available_top_anchorage_exterior_mm: float
    available_top_anchorage_interior_mm: float
    available_bottom_anchorage_exterior_mm: float
    available_bottom_anchorage_interior_mm: float
    vertical_closed_stirrups: bool
    straight_anchorage: bool
    bars_bundled: bool
    bars_spliced: bool
    bars_curtailed: bool
    reinforcement_schedule_approved: bool
    effective_depth_basis_approved: bool
    durability_cover_basis_approved: bool
    detailing_basis_reference: str
    durability_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "top_bar_count",
            "bottom_bar_count",
            "side_face_bar_count_each_face",
            "stirrup_leg_count",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise StrapFootingContractError(f"{name} must be an integer")
            if value < 2:
                raise StrapFootingContractError(
                    f"{name} must be at least 2 for the represented layout"
                )
        for name in (
            "top_bar_diameter_mm",
            "bottom_bar_diameter_mm",
            "side_face_bar_diameter_mm",
            "stirrup_diameter_mm",
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
            "side_face_vertical_spacing_mm",
            "stirrup_spacing_mm",
            "nominal_cover_mm",
            "required_nominal_cover_mm",
            "maximum_aggregate_size_mm",
            "available_top_anchorage_exterior_mm",
            "available_top_anchorage_interior_mm",
            "available_bottom_anchorage_exterior_mm",
            "available_bottom_anchorage_interior_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )
        for name in (
            "vertical_closed_stirrups",
            "straight_anchorage",
            "reinforcement_schedule_approved",
            "effective_depth_basis_approved",
            "durability_cover_basis_approved",
        ):
            _require_bool(getattr(self, name), name, True)
        for name in ("bars_bundled", "bars_spliced", "bars_curtailed"):
            _require_bool(getattr(self, name), name, False)
        for name in ("detailing_basis_reference", "durability_basis_reference"):
            object.__setattr__(
                self,
                name,
                _non_blank(getattr(self, name), name),
            )


@dataclass(frozen=True)
class StrapFootingDesignInput:
    """Complete input to the bounded strap strength composition."""

    analysis: StrapFootingAnalysisInput
    material: StrapFootingMaterialInput
    reinforcement: StrapFootingReinforcementInput

    def __post_init__(self) -> None:
        for name, expected_type in (
            ("analysis", StrapFootingAnalysisInput),
            ("material", StrapFootingMaterialInput),
            ("reinforcement", StrapFootingReinforcementInput),
        ):
            if not isinstance(getattr(self, name), expected_type):
                raise StrapFootingContractError(
                    f"{name} must be a {expected_type.__name__}"
                )
