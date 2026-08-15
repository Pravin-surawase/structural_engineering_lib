# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 33 geometry for the bounded straight-flight staircase case."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.staircase.models import (
    StaircaseContractError,
    StraightFlightStairGeometry,
)
from structural_lib.codes.is456.traceability import clause

__all__ = ["StraightFlightGeometryResult", "resolve_straight_flight_geometry"]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 33.1(c) and Cl. 33.3",
    "NPTEL-M9L20-EX9.1",
)


@dataclass(frozen=True)
class StraightFlightGeometryResult:
    """Resolved horizontal span and slope geometry with explicit mm units."""

    input: StraightFlightStairGeometry
    effective_span_mm: float
    inclined_step_length_mm: float
    slope_factor: float
    slope_angle_degrees: float
    inclined_going_length_mm: float
    source_refs: tuple[str, ...]


@clause("33.1", "33.3")
def resolve_straight_flight_geometry(
    geometry: StraightFlightStairGeometry,
) -> StraightFlightGeometryResult:
    """Resolve the frozen collinear-landing support and waist-depth geometry."""
    if not isinstance(geometry, StraightFlightStairGeometry):
        raise StaircaseContractError("geometry must be a StraightFlightStairGeometry")
    inclined_step_length_mm = math.hypot(geometry.riser_mm, geometry.tread_mm)
    slope_factor = inclined_step_length_mm / geometry.tread_mm
    return StraightFlightGeometryResult(
        input=geometry,
        effective_span_mm=(
            geometry.lower_landing_effective_length_mm
            + geometry.going_mm
            + geometry.upper_landing_effective_length_mm
        ),
        inclined_step_length_mm=inclined_step_length_mm,
        slope_factor=slope_factor,
        slope_angle_degrees=math.degrees(
            math.atan2(geometry.riser_mm, geometry.tread_mm)
        ),
        inclined_going_length_mm=geometry.going_mm * slope_factor,
        source_refs=_SOURCE_REFS,
    )
