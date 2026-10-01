# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Independent source/continuum regressions for the approved column correction.

Expected values were generated without structural_lib imports, then frozen.
Analytical and quadrature values remain distinct; nominal axial caps and the
representative Fig23 steel law are not mistaken for exact IS curves.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from structural_lib.codes.is456.column._strain_compatibility import (
    COLUMN_SECTION_METHOD,
    concrete_stress_at_strain,
    extreme_compression_strain,
    rectangular_concrete_resultants,
)
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check
from structural_lib.codes.is456.column.long_column import design_long_column
from structural_lib.codes.is456.column.pmm import (
    _fiber_grid,
    _section_response,
    create_symmetric_two_face_layout,
)
from structural_lib.codes.is456.column.slenderness import (
    _balanced_load_for_additional_moment,
    calculate_additional_moment,
)
from structural_lib.codes.is456.column.uniaxial import (
    _pm_envelope_point,
    design_short_column_uniaxial,
    pm_interaction_curve,
)
from structural_lib.core.errors import DimensionError
from structural_lib.core.materials import Steel
from structural_lib.services.column_api import (
    calculate_additional_moment_is456,
    design_long_column_is456,
    design_short_column_uniaxial_is456,
    pm_interaction_curve_is456,
)

_REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "data/benchmark_vectors/column_strain_compatibility.json"
    ).read_text(encoding="utf-8")
)
_AREA = _REFERENCE["source"]["Asc_mm2"]


@pytest.mark.parametrize("ratio", (1, 1.05, 1.5, 2, 7 / 3, 3, 20, 1000, 1e12, math.inf))
def test_full_compression_plane_preserves_neutral_axis_and_code_constraint(ratio):
    depth = 450.0
    xu = ratio * depth
    top = extreme_compression_strain(xu, depth)
    far = top * (1 - depth / xu)
    assert top + 0.75 * far == pytest.approx(0.0035, abs=1e-17)
    assert top * (1 - (3 * depth / 7) / xu) == pytest.approx(0.002, abs=1e-17)
    assert top >= far >= 0
    if math.isfinite(xu):
        assert top * (1 - xu / xu) == 0
    else:
        assert top == far == 0.002


@pytest.mark.parametrize(
    "state", _REFERENCE["states"], ids=lambda s: f"Fe{s['fy_nmm2']:g}-k{s['xu_over_D']}"
)
def test_section_response_matches_frozen_independent_continuum(state):
    xu = math.inf if state["xu_over_D"] is None else state["xu_over_D"] * 450.0
    c, m = rectangular_concrete_resultants(xu, 230.0, 450.0, 20.0)
    assert c == pytest.approx(state["concrete_force_n"], abs=1e-6)
    assert m == pytest.approx(state["quad_moment_center_nmm"], abs=1e-5)
    assert c == pytest.approx(state["quad_force_n"], abs=1e-6)
    p, moment = _pm_envelope_point(
        xu, 230.0, 450.0, 20.0, state["fy_nmm2"], _AREA / 2, 50.0
    )
    assert p == pytest.approx(state["Pu_kN"], abs=1e-8)
    assert moment == pytest.approx(state["Mu_kNm"], abs=1e-8)
    for bar in state["bars"]:
        assert concrete_stress_at_strain(bar["strain"], 20.0) == pytest.approx(
            bar["concrete_stress_nmm2"], abs=1e-12
        )


@pytest.mark.parametrize("ratio", (1, 1.05, 1.5, 2, 3, 20))
@pytest.mark.parametrize("theta", (0.0, 180.0))
def test_fiber_full_compression_matches_independent_response_and_opposite_face(
    ratio, theta
):
    state = next(
        s
        for s in _REFERENCE["states"]
        if s["fy_nmm2"] == 415 and s["xu_over_D"] == ratio
    )
    layout = create_symmetric_two_face_layout(
        b_mm=230,
        D_mm=450,
        Asc_mm2=_AREA,
        d_prime_mm=50,
        material=Steel(fy=415, steel_type="Fe415"),
    )
    x, y, area = _fiber_grid(230, 450, 8, 128)
    result = _section_response(
        theta_deg=theta,
        neutral_axis_depth_mm=ratio * 450,
        b_mm=230,
        D_mm=450,
        fck_nmm2=20,
        reinforcement=layout,
        fiber_x_mm=x,
        fiber_y_mm=y,
        fiber_area_mm2=area,
    )
    sign = 1 if theta == 0 else -1
    # Bounds cover midpoint quadrature at 128 depth cells; no material-model allowance.
    assert result.Pu_kN == pytest.approx(state["Pu_kN"], abs=0.02)
    assert result.Mx_kNm == pytest.approx(sign * state["Mu_kNm"], abs=0.003)
    assert result.My_kNm == pytest.approx(0, abs=1e-12)
    strains = [bar["strain"] for bar in state["bars"]]
    assert result.min_steel_strain == pytest.approx(min(strains), abs=1e-16)
    assert result.max_steel_strain == pytest.approx(max(strains), abs=1e-16)


def test_curve_retains_separate_nominal_axial_cap_and_named_profile():
    curve = pm_interaction_curve(230, 450, 20, 415, _AREA, 50, n_points=100)
    nominal = (0.4 * 20 * (230 * 450 - _AREA) + 0.67 * 415 * _AREA) / 1000
    raw_p, raw_m = _pm_envelope_point(math.inf, 230, 450, 20, 415, _AREA / 2, 50)
    assert curve.Pu_0_kN == pytest.approx(nominal, abs=1e-9)
    assert raw_p > nominal
    assert raw_m == 0
    assert max(p for p, _ in curve.points) <= nominal + 1e-9
    assert curve.points[-1] == pytest.approx((nominal, 0), abs=1e-9)
    assert curve.method == _REFERENCE["source"]["method"] == COLUMN_SECTION_METHOD
    assert curve.to_dict()["method"] == COLUMN_SECTION_METHOD


def test_public_pm_curve_matches_independent_source_benchmark_and_service():
    expected = _REFERENCE["consumers"]["GC-PM1"]
    core = pm_interaction_curve(400, 400, 25, 415, expected["inputs"]["steel_area"], 50)
    service = pm_interaction_curve_is456(
        400, 400, 25, 415, expected["inputs"]["steel_area"], 50
    )
    for name in ("Pu_0_kN", "Pu_bal_kN", "Mu_bal_kNm", "Mu_0_kNm"):
        assert getattr(core, name) == pytest.approx(expected[name], abs=1e-8)
        assert getattr(service, name) == getattr(core, name)
    assert service.method == COLUMN_SECTION_METHOD


def test_public_uniaxial_matches_independent_discrete_and_continuous_references():
    expected = _REFERENCE["consumers"]["GC-UNI1"]
    kwargs = {
        "Pu_kN": 1000,
        "Mu_kNm": 100,
        "b_mm": 400,
        "D_mm": 400,
        "le_mm": 2600,
        "Asc_mm2": expected["inputs"]["steel_area"],
        "d_prime_mm": 50,
    }
    result = design_short_column_uniaxial(fck=25, fy=415, **kwargs)
    service = design_short_column_uniaxial_is456(fck_nmm2=25, fy_nmm2=415, **kwargs)
    for name in ("Pu_cap_kN", "Mu_cap_kNm"):
        assert getattr(result, name) == pytest.approx(
            expected["sampled"][name], abs=0.005
        )
        # Separate continuum comparison includes the declared 200-point interpolation error.
        assert getattr(result, name) == pytest.approx(
            expected["continuous"][name], abs=0.02
        )
    assert result.utilization_ratio == pytest.approx(
        expected["sampled"]["utilization_ratio"], abs=0.00005
    )
    assert result.is_safe == expected["sampled"]["is_safe"]
    assert service == result


def test_biaxial_consumer_matches_independent_code_interaction():
    expected = _REFERENCE["consumers"]["GC-BI1"]
    result = biaxial_bending_check(
        Pu_kN=1200,
        Mux_kNm=80,
        Muy_kNm=60,
        b_mm=400,
        D_mm=500,
        le_mm=3000,
        fck=25,
        fy=415,
        Asc_mm2=2400,
        d_prime_mm=50,
    )
    for name in ("Mux1_kNm", "Muy1_kNm", "Puz_kN"):
        assert getattr(result, name) == pytest.approx(expected[name], abs=0.005)
    assert result.interaction_ratio == pytest.approx(
        expected["interaction_ratio"], abs=0.00005
    )
    assert result.is_safe == expected["is_safe"]


@pytest.mark.parametrize("balance", _REFERENCE["slenderness_balanced_states"])
def test_additional_moment_pb_uses_prescribed_strain_independently_of_grade(balance):
    section = balance["inputs"]
    inputs = {
        "b_mm": section["width"],
        "D_mm": section["depth"],
        "fck": section["fck"],
        "fy": section["fy"],
        "Asc_mm2": section["steel_area"],
        "d_prime_mm": section["cover"],
    }
    # Geometric anchor follows directly from the two prescribed face strains.
    assert balance["xu_mm"] == pytest.approx(2800 / 11, abs=1e-12)
    assert balance["state"]["eps_top"] == 0.0035
    assert balance["state"]["bars"][1]["strain"] == pytest.approx(-0.002, abs=1e-17)
    assert _balanced_load_for_additional_moment(**inputs) == pytest.approx(
        balance["state"]["Pu_kN"], abs=1e-8
    )
    result = calculate_additional_moment(Pu_kN=1000, lex_mm=6300, ley_mm=3000, **inputs)
    service = calculate_additional_moment_is456(
        Pu_kN=1000,
        lex_mm=6300,
        ley_mm=3000,
        fck_nmm2=inputs["fck"],
        fy_nmm2=inputs["fy"],
        **{k: v for k, v in inputs.items() if k not in ("fck", "fy")},
    )
    assert result == service
    assert result.Pb_kN == pytest.approx(balance["state"]["Pu_kN"], abs=1e-8)


@pytest.mark.parametrize("expected", _REFERENCE["consumers"]["long_column_sign_and_pb"])
def test_long_column_preserves_curvature_and_clause_pb_through_service(expected):
    section = expected["inputs"]
    inputs = {
        name: expected[name]
        for name in (
            "Pu_kN",
            "M1x_kNm",
            "M2x_kNm",
            "M1y_kNm",
            "M2y_kNm",
            "lex_mm",
            "ley_mm",
            "l_unsupported_mm",
            "braced",
        )
    }
    inputs.update(
        b_mm=section["width"],
        D_mm=section["depth"],
        fck=section["fck"],
        fy=section["fy"],
        Asc_mm2=section["steel_area"],
        d_prime_mm=section["cover"],
    )
    result = design_long_column(**inputs)
    service = design_long_column_is456(
        fck_nmm2=inputs["fck"],
        fy_nmm2=inputs["fy"],
        **{k: v for k, v in inputs.items() if k not in ("fck", "fy")},
    )
    assert service == result
    for name in (
        "Puz_kN",
        "Pb_kN",
        "Max_kNm",
        "May_kNm",
        "Mux_design_kNm",
        "Muy_design_kNm",
    ):
        assert getattr(result, name) == pytest.approx(expected[name], abs=0.005)
    assert result.k == pytest.approx(expected["k"], abs=0.00005)
    assert result.interaction_ratio == pytest.approx(
        expected["interaction_ratio"], abs=0.00005
    )
    assert result.is_safe == expected["is_safe"]


def test_long_column_consumer_matches_independent_reduced_moment_and_interaction():
    expected = _REFERENCE["consumers"]["long_column"]
    result = design_long_column(
        Pu_kN=1100,
        M1x_kNm=50,
        M2x_kNm=80,
        M1y_kNm=30,
        M2y_kNm=50,
        b_mm=300,
        D_mm=500,
        lex_mm=6500,
        ley_mm=4000,
        fck=25,
        fy=415,
        Asc_mm2=3000,
        d_prime_mm=50,
        l_unsupported_mm=5000,
    )
    for name in (
        "Puz_kN",
        "Pb_kN",
        "Max_kNm",
        "May_kNm",
        "Mux_design_kNm",
        "Muy_design_kNm",
    ):
        assert getattr(result, name) == pytest.approx(expected[name], abs=0.005)
    assert result.k == pytest.approx(expected["k"], abs=0.00005)
    assert result.interaction_ratio == pytest.approx(
        expected["interaction_ratio"], abs=0.00005
    )
    assert result.is_safe == expected["is_safe"]


@pytest.mark.parametrize("expected", _REFERENCE["consumers"]["long_column_axes"])
def test_plane_specific_reduction_matches_independent_axis_and_curvature_cases(
    expected,
):
    section = expected["inputs"]
    geometry = {
        "b_mm": section["width"],
        "D_mm": section["depth"],
        "fck": section["fck"],
        "fy": section["fy"],
        "Asc_mm2": section["steel_area"],
        "d_prime_mm": section["cover"],
        "Pu_kN": expected["Pu_kN"],
        "lex_mm": expected["lex_mm"],
        "ley_mm": expected["ley_mm"],
    }
    inputs = {
        **geometry,
        **{
            name: expected[name]
            for name in (
                "M1x_kNm",
                "M2x_kNm",
                "M1y_kNm",
                "M2y_kNm",
                "braced",
                "l_unsupported_mm",
            )
        },
    }
    long = design_long_column(**inputs)
    service_long = design_long_column_is456(
        fck_nmm2=inputs["fck"],
        fy_nmm2=inputs["fy"],
        **{k: v for k, v in inputs.items() if k not in ("fck", "fy")},
    )
    additional = calculate_additional_moment(**geometry)
    service_additional = calculate_additional_moment_is456(
        fck_nmm2=geometry["fck"],
        fy_nmm2=geometry["fy"],
        **{k: v for k, v in geometry.items() if k not in ("fck", "fy")},
    )
    assert service_long == long
    assert service_additional == additional
    for name in ("Pb_x_kN", "Pb_y_kN", "Max_reduced_kNm", "May_reduced_kNm"):
        assert getattr(long, name) == pytest.approx(expected[name], abs=0.005)
        assert getattr(additional, name) == pytest.approx(expected[name], abs=1e-8)
    for name in ("k_x", "k_y"):
        assert getattr(long, name) == pytest.approx(expected[name], abs=0.00005)
        assert getattr(additional, name) == pytest.approx(expected[name], abs=1e-12)
    for result in (long, additional):
        assert result.k == result.k_x
        assert result.Pb_kN == result.Pb_x_kN
        assert result.reduction_method == _REFERENCE["source"]["slenderness_method"]
    for name in ("Mux_design_kNm", "Muy_design_kNm", "Puz_kN"):
        assert getattr(long, name) == pytest.approx(expected[name], abs=0.005)
    assert long.interaction_ratio == pytest.approx(
        expected["interaction_ratio"], abs=0.00005
    )
    assert long.is_safe == expected["is_safe"]
    # An orientation must satisfy the prescribed tension strain in both planes.
    assert expected["tension_strain_39_7"] == pytest.approx(-0.002, abs=1e-17)
    assert expected["tension_strain_y_39_7"] == pytest.approx(-0.002, abs=1e-17)
    if geometry["b_mm"] == geometry["D_mm"]:
        assert additional.k_x == additional.k_y
        assert additional.Pb_x_kN == additional.Pb_y_kN


@pytest.mark.parametrize("owner", (calculate_additional_moment, design_long_column))
def test_equivalent_two_face_cover_must_fit_both_section_dimensions(owner):
    inputs = {
        "Pu_kN": 1000,
        "b_mm": 100,
        "D_mm": 450,
        "lex_mm": 3000,
        "ley_mm": 3000,
        "fck": 25,
        "fy": 415,
        "Asc_mm2": 900,
        "d_prime_mm": 60,
    }
    if owner is design_long_column:
        inputs.update(M1x_kNm=0, M2x_kNm=0, M1y_kNm=0, M2y_kNm=0, l_unsupported_mm=3000)
    with pytest.raises(DimensionError, match="Cover"):
        owner(**inputs)


def test_axis_relabelling_preserves_the_independent_material_profile_anchor():
    common = {
        "Pu_kN": 1000,
        "fck": 25,
        "fy": 415,
        "Asc_mm2": 2700,
        "d_prime_mm": 50,
        "l_unsupported_mm": 6300,
        "braced": True,
    }
    x = design_long_column(
        **common,
        b_mm=300,
        D_mm=450,
        lex_mm=6300,
        ley_mm=3000,
        M1x_kNm=161,
        M2x_kNm=161,
        M1y_kNm=0,
        M2y_kNm=0,
    )
    y = design_long_column(
        **common,
        b_mm=450,
        D_mm=300,
        lex_mm=3000,
        ley_mm=6300,
        M1x_kNm=0,
        M2x_kNm=0,
        M1y_kNm=161,
        M2y_kNm=161,
    )
    assert x.k_x == y.k_y
    assert x.k_y == y.k_x
    assert x.Pb_x_kN == y.Pb_y_kN
    assert x.Pb_y_kN == y.Pb_x_kN
    # The frozen predecessor used five-point/.87 steel and was unsafe at
    # 1.0013. The independently regenerated full Fig23 reference is stronger
    # at this state; its safety change must agree in both orientations.
    independent = _REFERENCE["consumers"]["long_column_axes"][0]
    assert (
        x.Mux_design_kNm == y.Muy_design_kNm == round(independent["Mux_design_kNm"], 2)
    )
    assert x.Muy_design_kNm == y.Mux_design_kNm == 22.6
    nominal_puz = (0.45 * 25 * (300 * 450 - 2700) + 0.75 * 415 * 2700) / 1000
    assert x.Puz_kN == y.Puz_kN == nominal_puz
    assert (
        x.interaction_ratio
        == y.interaction_ratio
        == round(independent["interaction_ratio"], 4)
    )
    assert x.is_safe is y.is_safe is independent["is_safe"]
