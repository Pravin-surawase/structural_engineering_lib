# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Golden vector tests for IS 456 footing functions — TASK-720 Part 3.

Covers all four footing sub-modules:
- bearing: size_footing (Cl 34.1), bearing_stress_enhancement (Cl 34.4),
           check_bearing_pressure (Cl 34.4)
- flexure: footing_flexure (Cl 34.2.3.1)
- one_way_shear: footing_one_way_shear (Cl 34.2.4.1)
- punching_shear: footing_punching_shear (Cl 31.6.1)

Golden vectors are loaded from tests/data/golden_vectors_is456.json.
These tests are PERMANENT — expected values must never change.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.codes.is456.footing.bearing import (
    bearing_stress_enhancement,
    check_bearing_pressure,
    size_footing,
)
from structural_lib.codes.is456.footing.flexure import footing_flexure
from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear
from structural_lib.codes.is456.footing.punching_shear import footing_punching_shear
from structural_lib.core.data_types import FootingType


def _load_vectors() -> dict:
    path = Path(__file__).parent.parent / "data" / "golden_vectors_is456.json"
    return json.loads(path.read_text(encoding="utf-8"))


_VECTORS = _load_vectors()

_FOOTING_TYPE_MAP = {
    "ISOLATED_SQUARE": FootingType.ISOLATED_SQUARE,
    "ISOLATED_RECTANGULAR": FootingType.ISOLATED_RECTANGULAR,
}


# ─── Footing Bearing / Sizing (GF1–GF6) ─────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    [v for v in _VECTORS["footing_bearing_cases"] if v["function"] == "size_footing"],
    ids=lambda v: v["case_id"],
)
def test_footing_size_golden(vector: dict):
    """GOLDEN: Footing sizing per IS 456 Cl 34.1."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 1e-12)

    result = size_footing(
        P_service_kN=inp["P_service_kN"],
        q_safe_kPa=inp["q_safe_kPa"],
        a_mm=inp["a_mm"],
        b_mm=inp["b_mm"],
        M_service_kNm=inp.get("M_service_kNm", 0.0),
        footing_type=_FOOTING_TYPE_MAP[inp["footing_type"]],
    )

    exp = vector["expected"]
    assert result.L_mm == exp["L_mm"]
    assert result.B_mm == exp["B_mm"]
    assert result.q_max_kPa == pytest.approx(exp["q_max_kPa"], rel=tol)
    assert result.q_min_kPa == pytest.approx(exp["q_min_kPa"], rel=tol)
    assert result.pressure_type == exp["pressure_type"]
    assert result.utilization_ratio == pytest.approx(exp["utilization_ratio"], rel=tol)
    assert result.is_safe is exp["is_safe"]


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    [
        v
        for v in _VECTORS["footing_bearing_cases"]
        if v["function"] == "bearing_stress_enhancement"
    ],
    ids=lambda v: v["case_id"],
)
def test_bearing_stress_enhancement_golden(vector: dict):
    """GOLDEN: Bearing stress enhancement per IS 456 Cl 34.4."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 1e-12)

    result = bearing_stress_enhancement(
        fck=inp["fck"],
        A1_mm2=inp["A1_mm2"],
        A2_mm2=inp["A2_mm2"],
    )

    exp = vector["expected"]
    assert result.basic_stress_mpa == pytest.approx(exp["basic_stress_mpa"], rel=tol)
    assert result.enhancement_factor == pytest.approx(
        exp["enhancement_factor"], rel=tol
    )
    assert result.permissible_stress_mpa == pytest.approx(
        exp["permissible_stress_mpa"], rel=tol
    )


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    [
        v
        for v in _VECTORS["footing_bearing_cases"]
        if v["function"] == "check_bearing_pressure"
    ],
    ids=lambda v: v["case_id"],
)
def test_check_bearing_pressure_golden(vector: dict):
    """GOLDEN: Bearing pressure check at column-footing interface per IS 456 Cl 34.4."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 1e-12)

    result = check_bearing_pressure(
        Pu_kN=inp["Pu_kN"],
        fck=inp["fck"],
        column_b_mm=inp["column_b_mm"],
        column_D_mm=inp["column_D_mm"],
        footing_B_mm=inp["footing_B_mm"],
        footing_L_mm=inp["footing_L_mm"],
    )

    exp = vector["expected"]
    assert result.actual_stress_mpa == pytest.approx(exp["actual_stress_mpa"], rel=tol)
    assert result.permissible_stress_mpa == pytest.approx(
        exp["permissible_stress_mpa"], rel=tol
    )
    assert result.enhancement_factor == pytest.approx(
        exp["enhancement_factor"], rel=tol
    )
    assert result.utilization_ratio == pytest.approx(exp["utilization_ratio"], rel=tol)
    assert result.is_safe is exp["is_safe"]


# ─── Footing Flexure (GF7–GF8) ──────────────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["footing_flexure_cases"],
    ids=lambda v: v["case_id"],
)
def test_footing_flexure_golden(vector: dict):
    """GOLDEN: Footing flexural design per IS 456 Cl 34.2.3.1."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 1e-12)

    result = footing_flexure(
        Pu_kN=inp["Pu_kN"],
        L_mm=inp["L_mm"],
        B_mm=inp["B_mm"],
        d_mm=inp["d_mm"],
        a_mm=inp["a_mm"],
        b_mm=inp["b_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
    )

    exp = vector["expected"]
    # L-direction
    assert result.Mu_L_kNm == pytest.approx(exp["Mu_L_kNm"], rel=tol)
    assert result.Ast_L_mm2 == pytest.approx(exp["Ast_L_mm2"], rel=tol)
    assert result.pt_L_percent == pytest.approx(exp["pt_L_percent"], rel=tol)
    assert result.cantilever_L_mm == pytest.approx(exp["cantilever_L_mm"], rel=tol)
    # B-direction
    assert result.Mu_B_kNm == pytest.approx(exp["Mu_B_kNm"], rel=tol)
    assert result.Ast_B_mm2 == pytest.approx(exp["Ast_B_mm2"], rel=tol)
    assert result.pt_B_percent == pytest.approx(exp["pt_B_percent"], rel=tol)
    assert result.cantilever_B_mm == pytest.approx(exp["cantilever_B_mm"], rel=tol)
    # General
    assert result.is_safe is exp["is_safe"]
    assert result.central_band_fraction == pytest.approx(
        exp["central_band_fraction"], rel=tol
    )


# ─── Footing One-Way Shear (GF9–GF10) ───────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["footing_shear_cases"],
    ids=lambda v: v["case_id"],
)
def test_footing_one_way_shear_golden(vector: dict):
    """GOLDEN: Footing one-way shear check per IS 456 Cl 34.2.4.1(a)."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 1e-12)

    result = footing_one_way_shear(
        Pu_kN=inp["Pu_kN"],
        L_mm=inp["L_mm"],
        B_mm=inp["B_mm"],
        d_mm=inp["d_mm"],
        a_mm=inp["a_mm"],
        b_mm=inp["b_mm"],
        fck=inp["fck"],
        pt=inp["pt"],
    )

    exp = vector["expected"]
    assert result.tau_v_nmm2 == pytest.approx(exp["tau_v_nmm2"], rel=tol)
    assert result.tau_c_nmm2 == pytest.approx(exp["tau_c_nmm2"], rel=tol)
    assert result.Vu_kN == pytest.approx(exp["Vu_kN"], rel=tol)
    assert result.utilization_ratio == pytest.approx(exp["utilization_ratio"], rel=tol)
    assert result.is_safe is exp["is_safe"]
    assert result.governing_direction == exp["governing_direction"]


# ─── Footing Punching Shear (GF11–GF12) ─────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["footing_punching_cases"],
    ids=lambda v: v["case_id"],
)
def test_footing_punching_shear_golden(vector: dict):
    """GOLDEN: Footing punching shear check per IS 456 Cl 31.6.1."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 1e-12)

    result = footing_punching_shear(
        Pu_kN=inp["Pu_kN"],
        L_mm=inp["L_mm"],
        B_mm=inp["B_mm"],
        d_mm=inp["d_mm"],
        a_mm=inp["a_mm"],
        b_mm=inp["b_mm"],
        fck=inp["fck"],
    )

    exp = vector["expected"]
    assert result.tau_v_nmm2 == pytest.approx(exp["tau_v_nmm2"], rel=tol)
    assert result.tau_c_nmm2 == pytest.approx(exp["tau_c_nmm2"], rel=tol)
    assert result.perimeter_mm == pytest.approx(exp["perimeter_mm"], rel=tol)
    assert result.Vu_punch_kN == pytest.approx(exp["Vu_punch_kN"], rel=tol)
    assert result.beta_c == pytest.approx(exp["beta_c"], rel=tol)
    assert result.ks == pytest.approx(exp["ks"], rel=tol)
    assert result.utilization_ratio == pytest.approx(exp["utilization_ratio"], rel=tol)
    assert result.is_safe is exp["is_safe"]


# ─── Determinism check ──────────────────────────────────────────────────────


@pytest.mark.golden
def test_footing_golden_vectors_are_deterministic():
    """Verify footing functions produce identical results on repeated calls."""
    r1 = footing_punching_shear(
        Pu_kN=1200, L_mm=1500, B_mm=1500, d_mm=400, a_mm=400, b_mm=400, fck=25
    )
    r2 = footing_punching_shear(
        Pu_kN=1200, L_mm=1500, B_mm=1500, d_mm=400, a_mm=400, b_mm=400, fck=25
    )
    assert r1.tau_v_nmm2 == r2.tau_v_nmm2
    assert r1.utilization_ratio == r2.utilization_ratio

    r3 = footing_flexure(
        Pu_kN=1200, L_mm=1500, B_mm=1500, d_mm=400, a_mm=400, b_mm=400, fck=25, fy=415
    )
    r4 = footing_flexure(
        Pu_kN=1200, L_mm=1500, B_mm=1500, d_mm=400, a_mm=400, b_mm=400, fck=25, fy=415
    )
    assert r3.Ast_L_mm2 == r4.Ast_L_mm2
    assert r3.Mu_L_kNm == r4.Mu_L_kNm
