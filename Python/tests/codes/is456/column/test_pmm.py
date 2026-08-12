# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Experimental generalized-reinforcement and P-M-M section tests.

The 45-degree point is independently derived by closed-form continuum
integration. Symmetric principal-axis comparisons remain secondary regression
evidence against the supported Cl. 39.5 implementation.
"""

from __future__ import annotations

import json
import math

import pytest

from structural_lib.codes.is456.column.pmm import (
    _fiber_grid,
    _section_response,
    create_symmetric_two_face_layout,
    experimental_pmm_interaction_surface,
    pm_interaction_slice_for_layout,
)
from structural_lib.codes.is456.column.uniaxial import pm_interaction_curve
from structural_lib.core.data_types import (
    ColumnReinforcementBar,
    ColumnReinforcementLayout,
    PMMInteractionSurface,
)
from structural_lib.core.errors import DimensionError, MaterialError
from structural_lib.core.materials import Steel


def _moment_at_axial_load(slice_, axial_load_kN: float, axis: str) -> float:
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
    raise AssertionError(f"No supported curve bracket for Pu={axial_load_kN}")


def _signed_moments_at_axial_load(slice_, axial_load_kN: float) -> tuple[float, float]:
    points = sorted(slice_.points, key=lambda point: point.Pu_kN)
    for first, second in zip(points, points[1:], strict=False):
        if first.Pu_kN <= axial_load_kN <= second.Pu_kN:
            fraction = (axial_load_kN - first.Pu_kN) / (second.Pu_kN - first.Pu_kN)
            mx_kNm = first.Mx_kNm + fraction * (second.Mx_kNm - first.Mx_kNm)
            my_kNm = first.My_kNm + fraction * (second.My_kNm - first.My_kNm)
            return mx_kNm, my_kNm
    raise AssertionError(f"No experimental slice bracket for Pu={axial_load_kN}")


@pytest.fixture
def steel() -> Steel:
    return Steel(fy=415.0, steel_type="Fe415")


@pytest.fixture
def symmetric_layout(steel: Steel) -> ColumnReinforcementLayout:
    return create_symmetric_two_face_layout(
        b_mm=300.0,
        D_mm=500.0,
        Asc_mm2=3000.0,
        d_prime_mm=75.0,
        material=steel,
    )


def test_symmetric_adapter_preserves_area_coordinates_and_units(
    symmetric_layout: ColumnReinforcementLayout,
) -> None:
    assert symmetric_layout.total_area_mm2 == pytest.approx(3000.0)
    assert {(bar.x_mm, bar.y_mm) for bar in symmetric_layout.bars} == {
        (-75.0, -175.0),
        (75.0, -175.0),
        (-75.0, 175.0),
        (75.0, 175.0),
    }
    assert symmetric_layout.to_dict()["bars"][0]["material"] == {
        "fy_nmm2": 415.0,
        "es_nmm2": 200000.0,
        "grade": "Fe415",
    }
    json.dumps(symmetric_layout.to_dict())


def test_section_rejects_bar_outside_gross_rectangle(steel: Steel) -> None:
    layout = ColumnReinforcementLayout(
        bars=(ColumnReinforcementBar(151.0, 0.0, 500.0, steel),)
    )
    with pytest.raises(DimensionError, match="outside the section"):
        pm_interaction_slice_for_layout(
            b_mm=300.0,
            D_mm=500.0,
            fck_nmm2=25.0,
            reinforcement=layout,
        )


def test_section_rejects_non_is456_steel_modulus() -> None:
    material = Steel(fy=415.0, Es=195000.0, steel_type="Fe415")
    layout = ColumnReinforcementLayout(
        bars=(ColumnReinforcementBar(0.0, 0.0, 1200.0, material),)
    )
    with pytest.raises(MaterialError, match="requires Es=200000"):
        pm_interaction_slice_for_layout(
            b_mm=300.0,
            D_mm=500.0,
            fck_nmm2=25.0,
            reinforcement=layout,
        )


@pytest.mark.parametrize(
    ("theta_deg", "axis", "legacy_width", "legacy_depth"),
    ((0.0, "Mx_kNm", 300.0, 500.0), (90.0, "My_kNm", 500.0, 300.0)),
)
def test_symmetric_principal_slices_match_supported_pm_curve(
    symmetric_layout: ColumnReinforcementLayout,
    theta_deg: float,
    axis: str,
    legacy_width: float,
    legacy_depth: float,
) -> None:
    experimental = pm_interaction_slice_for_layout(
        b_mm=300.0,
        D_mm=500.0,
        fck_nmm2=25.0,
        reinforcement=symmetric_layout,
        theta_deg=theta_deg,
        n_fibers_x=48,
        n_fibers_y=64,
        n_depths=160,
    )
    supported = pm_interaction_curve(
        b_mm=legacy_width,
        D_mm=legacy_depth,
        fck=25.0,
        fy=415.0,
        Asc_mm2=3000.0,
        d_prime_mm=75.0,
        n_points=400,
    )
    for axial_load_kN in (0.0, 500.0, 800.0, 1200.0, 1600.0, 2000.0):
        experimental_moment = _moment_at_axial_load(experimental, axial_load_kN, axis)
        supported_moment = _legacy_moment_at_axial_load(supported, axial_load_kN)
        tolerance = 0.05 if axial_load_kN == 2000.0 else 0.02
        assert experimental_moment == pytest.approx(supported_moment, rel=tolerance)


def test_oblique_response_matches_independent_closed_form_benchmark(
    steel: Steel,
) -> None:
    """Benchmark the root strain-plane kernel independently at theta=45°.

    The expected values are closed-form concrete integrals plus exact bar-force
    arithmetic, documented in ``docs/verification/column-pmm-benchmark.md``.
    """
    layout = create_symmetric_two_face_layout(
        b_mm=200.0,
        D_mm=200.0,
        Asc_mm2=1600.0,
        d_prime_mm=25.0,
        material=steel,
        layout_id="ANALYTICAL-45-DEG",
    )
    # A square mesh preserves the benchmark geometry's exact x/y symmetry.
    fiber_x_mm, fiber_y_mm, fiber_area_mm2 = _fiber_grid(200.0, 200.0, 128, 128)
    result = _section_response(
        theta_deg=45.0,
        neutral_axis_depth_mm=100.0 * math.sqrt(2.0),
        b_mm=200.0,
        D_mm=200.0,
        fck_nmm2=25.0,
        reinforcement=layout,
        fiber_x_mm=fiber_x_mm,
        fiber_y_mm=fiber_y_mm,
        fiber_area_mm2=fiber_area_mm2,
    )
    assert result.Pu_kN == pytest.approx(145.723673469, abs=0.02)
    assert result.Mx_kNm == pytest.approx(26.906093629, abs=0.001)
    assert result.My_kNm == pytest.approx(-26.906093629, abs=0.001)
    assert result.max_concrete_strain == pytest.approx(0.0035, rel=0.02)


def test_oblique_slice_preserves_independent_benchmark_signs(steel: Steel) -> None:
    layout = create_symmetric_two_face_layout(
        b_mm=200.0,
        D_mm=200.0,
        Asc_mm2=1600.0,
        d_prime_mm=25.0,
        material=steel,
        layout_id="ANALYTICAL-45-DEG",
    )
    slice_ = pm_interaction_slice_for_layout(
        b_mm=200.0,
        D_mm=200.0,
        fck_nmm2=25.0,
        reinforcement=layout,
        theta_deg=45.0,
        n_fibers_x=96,
        n_fibers_y=96,
        n_depths=240,
    )
    mx_kNm, my_kNm = _signed_moments_at_axial_load(slice_, 145.723673469)

    assert mx_kNm == pytest.approx(26.906093629, abs=0.01)
    assert my_kNm == pytest.approx(-26.906093629, abs=0.01)


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("n_fibers_x", 8.5),
        ("n_fibers_y", True),
        ("n_depths", 64.0),
    ),
)
def test_slice_rejects_non_integer_sampling_controls(
    symmetric_layout: ColumnReinforcementLayout,
    name: str,
    value: object,
) -> None:
    kwargs = {name: value}
    with pytest.raises(ValueError, match=f"{name} must be an integer"):
        pm_interaction_slice_for_layout(
            b_mm=300.0,
            D_mm=500.0,
            fck_nmm2=25.0,
            reinforcement=symmetric_layout,
            **kwargs,
        )


@pytest.mark.parametrize("n_angles", (4.5, True))
def test_surface_rejects_non_integer_angle_count(
    symmetric_layout: ColumnReinforcementLayout,
    n_angles: object,
) -> None:
    with pytest.raises(ValueError, match="n_angles must be an integer"):
        experimental_pmm_interaction_surface(
            b_mm=300.0,
            D_mm=500.0,
            fck_nmm2=25.0,
            reinforcement=symmetric_layout,
            n_angles=n_angles,
        )


def test_surface_uses_exact_cl39_3_axial_cap_and_experimental_boundary(
    symmetric_layout: ColumnReinforcementLayout,
) -> None:
    surface = experimental_pmm_interaction_surface(
        b_mm=300.0,
        D_mm=500.0,
        fck_nmm2=25.0,
        reinforcement=symmetric_layout,
        n_angles=4,
        n_fibers_x=12,
        n_fibers_y=16,
        n_depths=32,
    )
    expected_kN = (
        0.4 * 25.0 * (300.0 * 500.0 - 3000.0) + 0.67 * 415.0 * 3000.0
    ) / 1000.0
    assert isinstance(surface, PMMInteractionSurface)
    assert surface.experimental is True
    assert surface.nominal_axial_point.Pu_kN == pytest.approx(expected_kN)
    assert surface.nominal_axial_point.Mx_kNm == pytest.approx(0.0, abs=1e-12)
    assert surface.nominal_axial_point.My_kNm == pytest.approx(0.0, abs=1e-12)
    assert any("Bresler Cl. 39.6" in warning for warning in surface.warnings)
    json.dumps(surface.to_dict())
