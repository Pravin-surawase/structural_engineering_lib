# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed contracts for the bounded INDIA-2 straight-flight staircase case."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

__all__ = [
    "StairSpanDirection",
    "StairSupportCase",
    "StaircaseContractError",
    "StraightFlightActionInput",
    "StraightFlightLoads",
    "StraightFlightStairGeometry",
]


class StaircaseContractError(ValueError):
    """Raised when an input is outside the frozen INDIA-2 staircase scope."""


class StairSupportCase(StrEnum):
    """Support arrangements named at the boundary; only one is accepted."""

    LANDINGS_SPAN_WITH_FLIGHT = "landings_span_with_flight"
    BEAMS_AT_TOP_AND_BOTTOM_RISERS = "beams_at_top_and_bottom_risers"
    STRINGER_SUPPORTED = "stringer_supported"


class StairSpanDirection(StrEnum):
    """Potential span directions; INDIA-2 accepts longitudinal behavior only."""

    LONGITUDINAL = "longitudinal"
    TRANSVERSE = "transverse"


def positive_finite(value: float, field_name: str, unit: str) -> float:
    """Normalize a positive finite engineering input or fail closed."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise StaircaseContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise StaircaseContractError(
            f"{field_name} must be finite and positive in {unit}"
        )
    return normalized


def nonnegative_finite(value: float, field_name: str, unit: str) -> float:
    """Normalize a non-negative finite engineering input or fail closed."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise StaircaseContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0.0:
        raise StaircaseContractError(
            f"{field_name} must be finite and non-negative in {unit}"
        )
    return normalized


@dataclass(frozen=True)
class StraightFlightStairGeometry:
    """Geometry for one longitudinal flight and two collinear landing segments.

    All dimensions are in mm. The three horizontal segment lengths run from
    the lower outer support centre to the upper outer support centre.
    """

    lower_landing_effective_length_mm: float
    going_mm: float
    upper_landing_effective_length_mm: float
    flight_width_mm: float
    riser_mm: float
    tread_mm: float
    waist_thickness_mm: float
    landing_thickness_mm: float
    support_case: StairSupportCase = StairSupportCase.LANDINGS_SPAN_WITH_FLIGHT
    span_direction: StairSpanDirection = StairSpanDirection.LONGITUDINAL
    landings_collinear: bool = True
    has_stringer_beams: bool = False
    is_cast_in_situ_solid: bool = True

    def __post_init__(self) -> None:
        for name in (
            "lower_landing_effective_length_mm",
            "going_mm",
            "upper_landing_effective_length_mm",
            "flight_width_mm",
            "riser_mm",
            "tread_mm",
            "waist_thickness_mm",
            "landing_thickness_mm",
        ):
            object.__setattr__(
                self,
                name,
                positive_finite(getattr(self, name), name, "mm"),
            )
        if self.support_case is not StairSupportCase.LANDINGS_SPAN_WITH_FLIGHT:
            raise StaircaseContractError(
                "support_case must be landings_span_with_flight for INDIA-2"
            )
        if self.span_direction is not StairSpanDirection.LONGITUDINAL:
            raise StaircaseContractError(
                "span_direction must be longitudinal for INDIA-2"
            )
        if self.landings_collinear is not True:
            raise StaircaseContractError(
                "landings_collinear must be explicitly True for INDIA-2"
            )
        if self.has_stringer_beams is not False:
            raise StaircaseContractError(
                "has_stringer_beams must be explicitly False for INDIA-2"
            )
        if self.is_cast_in_situ_solid is not True:
            raise StaircaseContractError(
                "is_cast_in_situ_solid must be explicitly True for INDIA-2"
            )


@dataclass(frozen=True)
class StraightFlightLoads:
    """Caller load carriers plus explicit concrete self-weight inputs.

    Superimposed actions are unfactored area loads on horizontal plan in kN/m2.
    Landing shares are caller decisions; this type does not generate IS 875
    actions or infer an open-well system.
    """

    lower_landing_superimposed_service_load_kn_per_m2: float
    flight_superimposed_service_load_kn_per_m2: float
    upper_landing_superimposed_service_load_kn_per_m2: float
    lower_landing_load_share: float
    upper_landing_load_share: float
    concrete_unit_weight_kn_per_m3: float
    ultimate_load_factor: float
    load_basis_reference: str

    def __post_init__(self) -> None:
        for name in (
            "lower_landing_superimposed_service_load_kn_per_m2",
            "flight_superimposed_service_load_kn_per_m2",
            "upper_landing_superimposed_service_load_kn_per_m2",
        ):
            object.__setattr__(
                self,
                name,
                nonnegative_finite(getattr(self, name), name, "kN/m2"),
            )
        for name in ("lower_landing_load_share", "upper_landing_load_share"):
            share = positive_finite(getattr(self, name), name, "ratio")
            if share > 1.0:
                raise StaircaseContractError(f"{name} must not exceed 1.0")
            object.__setattr__(self, name, share)
        object.__setattr__(
            self,
            "concrete_unit_weight_kn_per_m3",
            positive_finite(
                self.concrete_unit_weight_kn_per_m3,
                "concrete_unit_weight_kn_per_m3",
                "kN/m3",
            ),
        )
        object.__setattr__(
            self,
            "ultimate_load_factor",
            positive_finite(self.ultimate_load_factor, "ultimate_load_factor", "ratio"),
        )
        if (
            not isinstance(self.load_basis_reference, str)
            or not self.load_basis_reference.strip()
        ):
            raise StaircaseContractError(
                "load_basis_reference must be a non-blank caller reference"
            )
        object.__setattr__(
            self, "load_basis_reference", self.load_basis_reference.strip()
        )


@dataclass(frozen=True)
class StraightFlightActionInput:
    """Accepted geometry and load carriers for the three-segment analysis."""

    geometry: StraightFlightStairGeometry
    loads: StraightFlightLoads

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, StraightFlightStairGeometry):
            raise StaircaseContractError(
                "geometry must be a StraightFlightStairGeometry"
            )
        if not isinstance(self.loads, StraightFlightLoads):
            raise StaircaseContractError("loads must be a StraightFlightLoads")
