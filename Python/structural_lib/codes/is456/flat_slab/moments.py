# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 31 direct-design moments for the bounded interior flat-slab panel."""

from __future__ import annotations

from dataclasses import dataclass

from structural_lib.codes.is456.flat_slab.geometry import (
    FlatSlabDirection,
    FlatSlabDirectionGeometry,
    FlatSlabGeometryResult,
    resolve_regular_interior_flat_slab_geometry,
)
from structural_lib.codes.is456.flat_slab.models import (
    FlatSlabContractError,
    FlatSlabPanelInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "FlatSlabDirectionMoments",
    "FlatSlabMomentResult",
    "calculate_regular_interior_flat_slab_moments",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 31.4.2.2, 31.4.3.2, 31.4.4, " "31.5.5.1, 31.5.5.3, 31.5.5.4",
    "IS456-2000-A6",
)


@dataclass(frozen=True)
class FlatSlabDirectionMoments:
    """Direct-design moment distribution in one panel direction."""

    direction: FlatSlabDirection
    factored_uniform_load_kn_per_m2: float
    transverse_span_m: float
    governing_clear_span_m: float
    design_load_on_panel_strip_kn: float
    total_static_moment_knm: float
    total_negative_moment_knm: float
    total_positive_moment_knm: float
    column_strip_negative_moment_knm: float
    column_strip_positive_moment_knm: float
    middle_strip_negative_moment_knm: float
    middle_strip_positive_moment_knm: float


@dataclass(frozen=True)
class FlatSlabMomentResult:
    """Both-direction moments for the G0-approved square interior panel."""

    input: FlatSlabPanelInput
    geometry: FlatSlabGeometryResult
    x: FlatSlabDirectionMoments
    y: FlatSlabDirectionMoments
    source_refs: tuple[str, ...]


def _calculate_direction(
    *,
    geometry: FlatSlabDirectionGeometry,
    factored_uniform_load_kn_per_m2: float,
) -> FlatSlabDirectionMoments:
    transverse_span_m = geometry.transverse_span_mm / 1000.0
    governing_clear_span_m = geometry.governing_clear_span_mm / 1000.0

    # IS 456:2000, 31.4.2.2. With W = wu*l2*ln, Mo = W*ln/8.
    design_load_on_panel_strip_kn = (
        factored_uniform_load_kn_per_m2 * transverse_span_m * governing_clear_span_m
    )
    total_static_moment_knm = (
        design_load_on_panel_strip_kn * governing_clear_span_m / 8.0
    )

    # The frozen route admits only an interior span under identical full loading.
    total_negative_moment_knm = 0.65 * total_static_moment_knm
    total_positive_moment_knm = 0.35 * total_static_moment_knm
    column_strip_negative_moment_knm = 0.75 * total_negative_moment_knm
    column_strip_positive_moment_knm = 0.60 * total_positive_moment_knm
    middle_strip_negative_moment_knm = (
        total_negative_moment_knm - column_strip_negative_moment_knm
    )
    middle_strip_positive_moment_knm = (
        total_positive_moment_knm - column_strip_positive_moment_knm
    )

    return FlatSlabDirectionMoments(
        direction=geometry.direction,
        factored_uniform_load_kn_per_m2=factored_uniform_load_kn_per_m2,
        transverse_span_m=transverse_span_m,
        governing_clear_span_m=governing_clear_span_m,
        design_load_on_panel_strip_kn=design_load_on_panel_strip_kn,
        total_static_moment_knm=total_static_moment_knm,
        total_negative_moment_knm=total_negative_moment_knm,
        total_positive_moment_knm=total_positive_moment_knm,
        column_strip_negative_moment_knm=column_strip_negative_moment_knm,
        column_strip_positive_moment_knm=column_strip_positive_moment_knm,
        middle_strip_negative_moment_knm=middle_strip_negative_moment_knm,
        middle_strip_positive_moment_knm=middle_strip_positive_moment_knm,
    )


@clause("31.4.2.2", "31.4.3.2", "31.4.4", "31.5.5.1", "31.5.5.3", "31.5.5.4")
def calculate_regular_interior_flat_slab_moments(
    panel: FlatSlabPanelInput,
) -> FlatSlabMomentResult:
    """Calculate bounded direct-design moments in both panel directions."""
    if not isinstance(panel, FlatSlabPanelInput):
        raise FlatSlabContractError("panel must be a FlatSlabPanelInput")

    geometry = resolve_regular_interior_flat_slab_geometry(panel)
    factored_load = panel.gravity_load.factored_uniform_load_kn_per_m2
    return FlatSlabMomentResult(
        input=panel,
        geometry=geometry,
        x=_calculate_direction(
            geometry=geometry.x,
            factored_uniform_load_kn_per_m2=factored_load,
        ),
        y=_calculate_direction(
            geometry=geometry.y,
            factored_uniform_load_kn_per_m2=factored_load,
        ),
        source_refs=_SOURCE_REFS
        + (
            panel.geometry.geometry_basis_reference,
            panel.gravity_load.load_basis_reference,
        ),
    )
