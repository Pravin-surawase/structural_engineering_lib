# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed contracts for the bounded INDIA-2 Clause 29 deep-beam case."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

__all__ = [
    "DeepBeamActionInput",
    "DeepBeamContractError",
    "DeepBeamGeometry",
    "DeepBeamLeverArmCase",
    "DeepBeamSupportType",
]


class DeepBeamContractError(ValueError):
    """Raised when an input is outside the frozen INDIA-2 deep-beam scope."""


class DeepBeamSupportType(StrEnum):
    """Support systems admitted by the first Clause 29 workflow."""

    SIMPLY_SUPPORTED = "simply_supported"


class DeepBeamLeverArmCase(StrEnum):
    """Normalized Clause 29.2 simply supported lever-arm branches."""

    RATIO_BELOW_ONE = "effective_span_to_depth_below_one"
    RATIO_ONE_TO_TWO = "effective_span_to_depth_from_one_to_below_two"


def _positive_finite(value: float, field_name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise DeepBeamContractError(f"{field_name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise DeepBeamContractError(
            f"{field_name} must be finite and positive in {unit}"
        )
    return normalized


def _non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeepBeamContractError(f"{field_name} must be a non-blank string")
    return value.strip()


@dataclass(frozen=True)
class DeepBeamGeometry:
    """Caller-confirmed geometry and external bearing/nodal prerequisite.

    All dimensions are in mm. Only a simply supported, top-loaded, solid
    rectangular member without openings, dapped ends, or hanging action is
    admitted by the first INDIA-2 deep-beam workflow.
    """

    centre_to_centre_span_mm: float
    clear_span_mm: float
    overall_depth_mm: float
    beam_width_mm: float
    support_type: DeepBeamSupportType
    solid_rectangular_section: bool
    openings_present: bool
    dapped_ends_present: bool
    top_loaded: bool
    hanging_action_required: bool
    bearing_nodal_zone_verified: bool
    geometry_basis_reference: str
    bearing_nodal_zone_reference: str

    def __post_init__(self) -> None:
        for name in (
            "centre_to_centre_span_mm",
            "clear_span_mm",
            "overall_depth_mm",
            "beam_width_mm",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name, "mm"),
            )
        if self.clear_span_mm >= self.centre_to_centre_span_mm:
            raise DeepBeamContractError(
                "clear_span_mm must be less than centre_to_centre_span_mm"
            )
        if self.support_type is not DeepBeamSupportType.SIMPLY_SUPPORTED:
            raise DeepBeamContractError(
                "support_type must be DeepBeamSupportType.SIMPLY_SUPPORTED"
            )
        if self.solid_rectangular_section is not True:
            raise DeepBeamContractError(
                "solid_rectangular_section must be explicitly True"
            )
        if self.openings_present is not False:
            raise DeepBeamContractError("openings_present must be explicitly False")
        if self.dapped_ends_present is not False:
            raise DeepBeamContractError("dapped_ends_present must be explicitly False")
        if self.top_loaded is not True:
            raise DeepBeamContractError("top_loaded must be explicitly True")
        if self.hanging_action_required is not False:
            raise DeepBeamContractError(
                "hanging_action_required must be explicitly False"
            )
        if self.bearing_nodal_zone_verified is not True:
            raise DeepBeamContractError(
                "bearing_nodal_zone_verified must be explicitly True"
            )
        object.__setattr__(
            self,
            "geometry_basis_reference",
            _non_blank(self.geometry_basis_reference, "geometry_basis_reference"),
        )
        object.__setattr__(
            self,
            "bearing_nodal_zone_reference",
            _non_blank(
                self.bearing_nodal_zone_reference,
                "bearing_nodal_zone_reference",
            ),
        )


@dataclass(frozen=True)
class DeepBeamActionInput:
    """Geometry, material grades, and caller-supplied positive design moment."""

    geometry: DeepBeamGeometry
    concrete_grade_nmm2: float
    steel_grade_nmm2: float
    factored_positive_moment_knm: float
    action_basis_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, DeepBeamGeometry):
            raise DeepBeamContractError("geometry must be a DeepBeamGeometry")
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
            raise DeepBeamContractError(
                "concrete_grade_nmm2 must be a standard M20-M60 grade"
            )
        steel_grade = _positive_finite(
            self.steel_grade_nmm2,
            "steel_grade_nmm2",
            "N/mm2",
        )
        if steel_grade not in {415.0, 500.0}:
            raise DeepBeamContractError(
                "steel_grade_nmm2 must be Fe415 or Fe500 for this route"
            )
        object.__setattr__(self, "concrete_grade_nmm2", concrete_grade)
        object.__setattr__(self, "steel_grade_nmm2", steel_grade)
        object.__setattr__(
            self,
            "factored_positive_moment_knm",
            _positive_finite(
                self.factored_positive_moment_knm,
                "factored_positive_moment_knm",
                "kN m",
            ),
        )
        object.__setattr__(
            self,
            "action_basis_reference",
            _non_blank(self.action_basis_reference, "action_basis_reference"),
        )
