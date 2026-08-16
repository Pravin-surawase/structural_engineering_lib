# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 31 geometry, eligibility, and strip widths for the bounded panel."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456.flat_slab.models import (
    FlatSlabContractError,
    FlatSlabPanelInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "FlatSlabDirection",
    "FlatSlabDirectionGeometry",
    "FlatSlabGeometryResult",
    "resolve_regular_interior_flat_slab_geometry",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 31.1.1, 31.2.1, 31.3.1, 31.4.1",
    "IS456-2000-A6",
)


class FlatSlabDirection(StrEnum):
    """Orthogonal panel directions."""

    X = "x"
    Y = "y"


@dataclass(frozen=True)
class FlatSlabDirectionGeometry:
    """Clear-span and design-strip geometry in one direction, all in mm."""

    direction: FlatSlabDirection
    centre_to_centre_span_mm: float
    transverse_span_mm: float
    support_width_mm: float
    face_to_face_clear_span_mm: float
    minimum_clear_span_component_mm: float
    governing_clear_span_mm: float
    column_strip_half_width_mm: float
    column_strip_total_width_mm: float
    middle_strip_width_mm: float


@dataclass(frozen=True)
class FlatSlabGeometryResult:
    """Resolved G0 topology and exact Clause 31 applicability carriers."""

    input: FlatSlabPanelInput
    x: FlatSlabDirectionGeometry
    y: FlatSlabDirectionGeometry
    minimum_slab_thickness_mm: float
    service_live_dead_ratio: float
    expected_factored_uniform_load_kn_per_m2: float
    direct_design_eligible: bool
    source_refs: tuple[str, ...]


def _resolve_direction(
    *,
    direction: FlatSlabDirection,
    centre_span_mm: float,
    transverse_span_mm: float,
    support_width_mm: float,
) -> FlatSlabDirectionGeometry:
    face_to_face = centre_span_mm - support_width_mm
    minimum_component = 0.65 * centre_span_mm
    governing_clear_span = max(face_to_face, minimum_component)
    half_column_strip = min(0.25 * transverse_span_mm, 0.25 * centre_span_mm)
    total_column_strip = 2.0 * half_column_strip
    middle_strip = transverse_span_mm - total_column_strip
    return FlatSlabDirectionGeometry(
        direction=direction,
        centre_to_centre_span_mm=centre_span_mm,
        transverse_span_mm=transverse_span_mm,
        support_width_mm=support_width_mm,
        face_to_face_clear_span_mm=face_to_face,
        minimum_clear_span_component_mm=minimum_component,
        governing_clear_span_mm=governing_clear_span,
        column_strip_half_width_mm=half_column_strip,
        column_strip_total_width_mm=total_column_strip,
        middle_strip_width_mm=middle_strip,
    )


@clause("31.1.1", "31.2.1", "31.3.1", "31.4.1")
def resolve_regular_interior_flat_slab_geometry(
    panel: FlatSlabPanelInput,
) -> FlatSlabGeometryResult:
    """Resolve geometry only for the G0-approved square interior panel."""
    if not isinstance(panel, FlatSlabPanelInput):
        raise FlatSlabContractError("panel must be a FlatSlabPanelInput")

    geometry = panel.geometry
    x = _resolve_direction(
        direction=FlatSlabDirection.X,
        centre_span_mm=geometry.centre_to_centre_span_x_mm,
        transverse_span_mm=geometry.centre_to_centre_span_y_mm,
        support_width_mm=geometry.column_width_x_mm,
    )
    y = _resolve_direction(
        direction=FlatSlabDirection.Y,
        centre_span_mm=geometry.centre_to_centre_span_y_mm,
        transverse_span_mm=geometry.centre_to_centre_span_x_mm,
        support_width_mm=geometry.column_width_y_mm,
    )
    gravity_load = panel.gravity_load
    return FlatSlabGeometryResult(
        input=panel,
        x=x,
        y=y,
        minimum_slab_thickness_mm=125.0,
        service_live_dead_ratio=(
            gravity_load.service_live_load_kn_per_m2
            / gravity_load.service_dead_load_kn_per_m2
        ),
        expected_factored_uniform_load_kn_per_m2=1.5
        * (
            gravity_load.service_dead_load_kn_per_m2
            + gravity_load.service_live_load_kn_per_m2
        ),
        direct_design_eligible=True,
        source_refs=_SOURCE_REFS
        + (
            geometry.geometry_basis_reference,
            panel.material.material_basis_reference,
            gravity_load.load_basis_reference,
        ),
    )
