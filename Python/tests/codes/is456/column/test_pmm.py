# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Experimental generalized-reinforcement and P-M-M section tests.

The symmetric-layout comparisons are regression gates against the existing
supported Cl. 39.5 P-M implementation. They are not independent validation of
the experimental fiber solver.
"""

from __future__ import annotations

import json

import pytest

from structural_lib import (
    ColumnReinforcementBar,
    ColumnReinforcementLayout,
    PMMInteractionSurface,
    Steel,
    create_symmetric_column_layout_is456,
    experimental_pmm_interaction_surface_is456,
    pm_interaction_curve_is456,
    pm_interaction_slice_for_layout_is456,
)
from structural_lib.core.errors import DimensionError, MaterialError


def _new_moment_at_axial_load(slice_, axial_load_kN: float, axis: str) -> float:
    points = sorted(slice_.points, key=lambda point: point.Pu_kN)
    for first, second in zip(points, points[1:], strict=False):
        if first.Pu_kN <= axial_load_kN <= second.Pu_kN:
            fraction = (axial_load_kN - first.Pu_kN) / (second.Pu_kN - first.Pu_kN)
            first_moment = getattr(first, axis)
            second_moment = getattr(second, axis)
            return abs(first_moment + fraction * (second_moment - first_moment))
    raise AssertionError(f"No experimental slice bracket for Pu={axial_load_kN}")


def _legacy_moment_at_axial_load(curve, axial_load_kN: float) -> float:
    points = sorted(curve.points)
    for (first_p, first_m), (second_p, second_m) in zip(
        points, points[1:], strict=False
    ):
        if first_p <= axial_load_kN <= second_p:
            fraction = (axial_load_kN - first_p) / (second_p - first_p)
            return first_m + fraction * (second_m - first_m)
    raise AssertionError(f"No legacy curve bracket for Pu={axial_load_kN}")


@pytest.fixture
def symmetric_layout() -> ColumnReinforcementLayout:
    return create_symmetric_column_layout_is456(
        b_mm=300.0,
        D_mm=500.0,
        Asc_mm2=3000.0,
        d_prime_mm=75.0,
        fy_nmm2=415.0,
    )


def test_symmetric_adapter_preserves_two_face_area(
    symmetric_layout: ColumnReinforcementLayout,
) -> None:
    assert symmetric_layout.total_area_mm2 == pytest.approx(3000.0)
    assert len(symmetric_layout.bars) == 4
    assert {(bar.x_mm, bar.y_mm) for bar in symmetric_layout.bars} == {
        (-75.0, -175.0),
        (75.0, -175.0),
        (-75.0, 175.0),
        (75.0, 175.0),
    }
    assert sum(bar.area_mm2 for bar in symmetric_layout.bars if bar.y_mm > 0) == (
        pytest.approx(1500.0)
    )
    assert sum(bar.area_mm2 for bar in symmetric_layout.bars if bar.y_mm < 0) == (
        pytest.approx(1500.0)
    )


def test_layout_serialization_preserves_material_and_units(
    symmetric_layout: ColumnReinforcementLayout,
) -> None:
    payload = symmetric_layout.to_dict()
    assert payload["bars"][0]["material"] == {
        "fy_nmm2": 415.0,
        "es_nmm2": 200000.0,
        "grade": "Fe415",
    }
    json.dumps(payload)


def test_section_rejects_bar_outside_gross_rectangle() -> None:
    layout = ColumnReinforcementLayout(
        bars=(
            ColumnReinforcementBar(
                x_mm=151.0,
                y_mm=0.0,
                area_mm2=500.0,
                material=Steel(fy=415.0, steel_type="Fe415"),
            ),
        )
    )
    with pytest.raises(DimensionError, match="outside the section"):
        pm_interaction_slice_for_layout_is456(300.0, 500.0, 25.0, layout)


def test_section_rejects_non_is456_steel_modulus() -> None:
    layout = ColumnReinforcementLayout(
        bars=(
            ColumnReinforcementBar(
                x_mm=0.0,
                y_mm=0.0,
                area_mm2=1200.0,
                material=Steel(fy=415.0, Es=195000.0, steel_type="Fe415"),
            ),
        )
    )
    with pytest.raises(MaterialError, match="requires Es=200000"):
        pm_interaction_slice_for_layout_is456(300.0, 500.0, 25.0, layout)


@pytest.mark.parametrize(
    ("theta_deg", "axis", "legacy_width", "legacy_depth"),
    (
        (0.0, "Mx_kNm", 300.0, 500.0),
        (90.0, "My_kNm", 500.0, 300.0),
    ),
)
def test_symmetric_uniaxial_slices_match_supported_pm_curve(
    symmetric_layout: ColumnReinforcementLayout,
    theta_deg: float,
    axis: str,
    legacy_width: float,
    legacy_depth: float,
) -> None:
    experimental = pm_interaction_slice_for_layout_is456(
        300.0,
        500.0,
        25.0,
        symmetric_layout,
        theta_deg=theta_deg,
        n_fibers_x=48,
        n_fibers_y=64,
        n_depths=160,
    )
    supported = pm_interaction_curve_is456(
        b_mm=legacy_width,
        D_mm=legacy_depth,
        fck_nmm2=25.0,
        fy_nmm2=415.0,
        Asc_mm2=3000.0,
        d_prime_mm=75.0,
        n_points=400,
    )

    for axial_load_kN in (0.0, 500.0, 800.0, 1200.0, 1600.0, 2000.0):
        new_moment = _new_moment_at_axial_load(experimental, axial_load_kN, axis)
        legacy_moment = _legacy_moment_at_axial_load(supported, axial_load_kN)
        tolerance = 0.05 if axial_load_kN == 2000.0 else 0.02
        assert new_moment == pytest.approx(legacy_moment, rel=tolerance)


def test_surface_uses_exact_cl39_3_axial_cap(
    symmetric_layout: ColumnReinforcementLayout,
) -> None:
    surface = experimental_pmm_interaction_surface_is456(
        300.0,
        500.0,
        25.0,
        symmetric_layout,
        n_angles=4,
        n_fibers_x=12,
        n_fibers_y=16,
        n_depths=32,
    )
    expected_kN = (
        0.4 * 25.0 * (300.0 * 500.0 - 3000.0) + 0.67 * 415.0 * 3000.0
    ) / 1000.0
    assert surface.nominal_axial_point.Pu_kN == pytest.approx(expected_kN)
    assert surface.nominal_axial_point.Mx_kNm == pytest.approx(0.0, abs=1e-12)
    assert surface.nominal_axial_point.My_kNm == pytest.approx(0.0, abs=1e-12)


def test_asymmetric_intermediate_bars_change_directional_capacity() -> None:
    steel = Steel(fy=415.0, steel_type="Fe415")
    layout = ColumnReinforcementLayout(
        bars=(
            ColumnReinforcementBar(-80.0, 180.0, 900.0, steel),
            ColumnReinforcementBar(80.0, 180.0, 900.0, steel),
            ColumnReinforcementBar(0.0, 100.0, 700.0, steel),
            ColumnReinforcementBar(0.0, -180.0, 500.0, steel),
        ),
        layout_id="ASYMMETRIC-WITH-INTERMEDIATE-BAR",
    )
    positive_y = pm_interaction_slice_for_layout_is456(
        300.0, 500.0, 25.0, layout, theta_deg=0.0, n_depths=96
    )
    negative_y = pm_interaction_slice_for_layout_is456(
        300.0, 500.0, 25.0, layout, theta_deg=180.0, n_depths=96
    )

    positive_capacity = _new_moment_at_axial_load(positive_y, 1000.0, "Mx_kNm")
    negative_capacity = _new_moment_at_axial_load(negative_y, 1000.0, "Mx_kNm")
    assert positive_capacity > 1.4 * negative_capacity


def test_full_surface_is_explicitly_experimental_and_biaxial(
    symmetric_layout: ColumnReinforcementLayout,
) -> None:
    surface = experimental_pmm_interaction_surface_is456(
        300.0,
        500.0,
        25.0,
        symmetric_layout,
        n_angles=8,
        n_fibers_x=12,
        n_fibers_y=16,
        n_depths=40,
    )

    assert isinstance(surface, PMMInteractionSurface)
    assert surface.experimental is True
    assert len(surface.slices) == 8
    assert surface.point_count > 8
    diagonal = surface.slices[1]
    assert diagonal.theta_deg == pytest.approx(45.0)
    assert any(
        abs(point.Mx_kNm) > 1.0 and abs(point.My_kNm) > 1.0 for point in diagonal.points
    )
    assert any("Bresler Cl. 39.6" in warning for warning in surface.warnings)
    json.dumps(surface.to_dict())
