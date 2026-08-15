# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 29.1-29.3.1 geometry for simply supported deep beams."""

from __future__ import annotations

from dataclasses import dataclass

from structural_lib.codes.is456.deep_beam.models import (
    DeepBeamContractError,
    DeepBeamGeometry,
    DeepBeamLeverArmCase,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "DeepBeamGeometryResult",
    "resolve_simply_supported_deep_beam_geometry",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 29.1-29.3.1",
    "IS456-2000-A6",
)


@dataclass(frozen=True)
class DeepBeamGeometryResult:
    """Resolved effective span, classification, lever arm, and tie zone."""

    input: DeepBeamGeometry
    centre_to_centre_span_component_mm: float
    clear_span_component_mm: float
    effective_span_mm: float
    effective_span_to_depth_ratio: float
    lever_arm_case: DeepBeamLeverArmCase
    lever_arm_mm: float
    positive_reinforcement_zone_depth_mm: float
    source_refs: tuple[str, ...]


@clause("29.1", "29.2", "29.3.1")
def resolve_simply_supported_deep_beam_geometry(
    geometry: DeepBeamGeometry,
) -> DeepBeamGeometryResult:
    """Resolve the sole supported Clause 29 simply supported geometry."""
    if not isinstance(geometry, DeepBeamGeometry):
        raise DeepBeamContractError("geometry must be a DeepBeamGeometry")

    centre_component = geometry.centre_to_centre_span_mm
    clear_component = 1.15 * geometry.clear_span_mm
    effective_span = min(centre_component, clear_component)
    ratio = effective_span / geometry.overall_depth_mm
    if ratio >= 2.0:
        raise DeepBeamContractError(
            "effective_span_mm / overall_depth_mm must be less than 2.0 "
            "for the simply supported Clause 29 route"
        )

    if ratio < 1.0:
        lever_arm_case = DeepBeamLeverArmCase.RATIO_BELOW_ONE
        lever_arm_mm = 0.6 * effective_span
    else:
        lever_arm_case = DeepBeamLeverArmCase.RATIO_ONE_TO_TWO
        lever_arm_mm = 0.2 * (effective_span + 2.0 * geometry.overall_depth_mm)

    reinforcement_zone_depth = 0.25 * geometry.overall_depth_mm - 0.05 * effective_span
    return DeepBeamGeometryResult(
        input=geometry,
        centre_to_centre_span_component_mm=centre_component,
        clear_span_component_mm=clear_component,
        effective_span_mm=effective_span,
        effective_span_to_depth_ratio=ratio,
        lever_arm_case=lever_arm_case,
        lever_arm_mm=lever_arm_mm,
        positive_reinforcement_zone_depth_mm=reinforcement_zone_depth,
        source_refs=_SOURCE_REFS
        + (
            geometry.geometry_basis_reference,
            geometry.bearing_nodal_zone_reference,
        ),
    )
