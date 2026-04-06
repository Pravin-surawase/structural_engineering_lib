"""Golden vector tests for IS 456 column functions.

Every test is marked @pytest.mark.golden and uses hand-verified reference
values from IS 456:2000 formulas / SP:16 Design Aids.

References:
    IS 456:2000, Cl 25.1.2, 25.2, 25.4, 39.3, 39.4, 39.5, 39.6, 39.7
    SP:16:1980, Charts 25-64
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.codes.is456.column.axial import (
    classify_column,
    effective_length,
    min_eccentricity,
    short_axial_capacity,
)
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check
from structural_lib.codes.is456.column.helical import check_helical_reinforcement
from structural_lib.codes.is456.column.long_column import design_long_column
from structural_lib.codes.is456.column.slenderness import calculate_additional_moment
from structural_lib.codes.is456.column.uniaxial import (
    design_short_column_uniaxial,
    pm_interaction_curve,
)
from structural_lib.core.data_types import ColumnClassification, EndCondition


def _load_vectors() -> dict:
    path = Path(__file__).parent.parent / "data" / "golden_vectors_is456.json"
    return json.loads(path.read_text(encoding="utf-8"))


_VECTORS = _load_vectors()


# ═══════════════════════════════════════════════════════════════════════════
# Effective Length — IS 456 Cl 25.2, Table 28
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_effective_length_cases"],
    ids=lambda v: v["case_id"],
)
def test_effective_length_golden(vector: dict):
    """GOLDEN: Effective length per IS 456 Table 28.
    Source: IS 456:2000, Table 28 (recommended values)
    """
    inp = vector["inputs"]
    end_cond = EndCondition[inp["end_condition"]]
    le = effective_length(
        l_mm=inp["l_mm"],
        end_condition=end_cond,
        use_theoretical=inp.get("use_theoretical", False),
    )
    expected = vector["expected"]["le_mm"]
    tol = vector.get("tolerance", 1e-12)
    assert le == pytest.approx(expected, rel=tol), (
        f"IS 456 Table 28 mismatch: {end_cond.name}, " f"got {le}, expected {expected}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Column Classification — IS 456 Cl 25.1.2
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_classification_cases"],
    ids=lambda v: v["case_id"],
)
def test_classify_column_golden(vector: dict):
    """GOLDEN: Column classification (short vs slender) per IS 456 Cl 25.1.2.
    Source: IS 456:2000, Cl 25.1.2 — le/D < 12 → short, >= 12 → slender
    """
    inp = vector["inputs"]
    result = classify_column(le_mm=inp["le_mm"], D_mm=inp["D_mm"])
    expected_cls = ColumnClassification[vector["expected"]["classification"]]
    assert result == expected_cls, (
        f"le/D = {inp['le_mm']/inp['D_mm']:.2f}, "
        f"expected {expected_cls.name}, got {result.name}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Minimum Eccentricity — IS 456 Cl 25.4
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_min_eccentricity_cases"],
    ids=lambda v: v["case_id"],
)
def test_min_eccentricity_golden(vector: dict):
    """GOLDEN: Minimum eccentricity per IS 456 Cl 25.4.
    Source: IS 456:2000, Cl 25.4 — e_min = max(l/500 + D/30, 20mm)
    """
    inp = vector["inputs"]
    e_min = min_eccentricity(
        l_unsupported_mm=inp["l_unsupported_mm"],
        D_mm=inp["D_mm"],
    )
    expected = vector["expected"]["e_min_mm"]
    tol = vector.get("tolerance", 1e-12)
    assert e_min == pytest.approx(expected, rel=tol), (
        f"IS 456 Cl 25.4: L={inp['l_unsupported_mm']}, D={inp['D_mm']}, "
        f"got {e_min}, expected {expected}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Short Column Axial Capacity — IS 456 Cl 39.3
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_axial_cases"],
    ids=lambda v: v["case_id"],
)
def test_short_axial_capacity_golden(vector: dict):
    """GOLDEN: Short column axial capacity per IS 456 Cl 39.3.
    Source: IS 456:2000, Cl 39.3 — Pu = 0.4*fck*Ac + 0.67*fy*Asc
    """
    inp = vector["inputs"]
    result = short_axial_capacity(
        fck=inp["fck"],
        fy=inp["fy"],
        Ag_mm2=inp["Ag_mm2"],
        Asc_mm2=inp["Asc_mm2"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.001)

    assert result.Pu_kN == pytest.approx(exp["Pu_kN"], rel=tol)
    assert result.Ac_mm2 == pytest.approx(exp["Ac_mm2"], rel=tol)
    assert result.steel_ratio == pytest.approx(exp["steel_ratio"], rel=tol)
    assert result.classification == ColumnClassification.SHORT


# ═══════════════════════════════════════════════════════════════════════════
# P-M Interaction Curve — IS 456 Cl 39.5
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_pm_curve_cases"],
    ids=lambda v: v["case_id"],
)
def test_pm_interaction_curve_golden(vector: dict):
    """GOLDEN: P-M interaction curve per IS 456 Cl 39.5.
    Source: IS 456:2000, Cl 39.5, SP:16 Charts 27-62
    """
    inp = vector["inputs"]
    result = pm_interaction_curve(
        b_mm=inp["b_mm"],
        D_mm=inp["D_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
        Asc_mm2=inp["Asc_mm2"],
        d_prime_mm=inp["d_prime_mm"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.001)

    assert result.Pu_0_kN == pytest.approx(exp["Pu_0_kN"], rel=tol)
    assert result.Pu_bal_kN == pytest.approx(exp["Pu_bal_kN"], rel=tol)
    assert result.Mu_bal_kNm == pytest.approx(exp["Mu_bal_kNm"], rel=tol)
    assert result.Mu_0_kNm == pytest.approx(exp["Mu_0_kNm"], rel=tol)
    assert len(result.points) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Uniaxial Bending Design — IS 456 Cl 39.5
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_uniaxial_cases"],
    ids=lambda v: v["case_id"],
)
def test_uniaxial_design_golden(vector: dict):
    """GOLDEN: Short column uniaxial check per IS 456 Cl 39.5.
    Source: IS 456:2000, Cl 39.5 (P-M interaction)
    """
    inp = vector["inputs"]
    result = design_short_column_uniaxial(
        Pu_kN=inp["Pu_kN"],
        Mu_kNm=inp["Mu_kNm"],
        b_mm=inp["b_mm"],
        D_mm=inp["D_mm"],
        le_mm=inp["le_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
        Asc_mm2=inp["Asc_mm2"],
        d_prime_mm=inp["d_prime_mm"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.01)

    assert result.is_safe is exp["is_safe"]
    assert result.Pu_cap_kN == pytest.approx(exp["Pu_cap_kN"], rel=tol)
    assert result.Mu_cap_kNm == pytest.approx(exp["Mu_cap_kNm"], rel=tol)
    assert result.utilization_ratio == pytest.approx(exp["utilization_ratio"], rel=tol)


# ═══════════════════════════════════════════════════════════════════════════
# Biaxial Bending Check — IS 456 Cl 39.6
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_biaxial_cases"],
    ids=lambda v: v["case_id"],
)
def test_biaxial_bending_golden(vector: dict):
    """GOLDEN: Biaxial bending check per IS 456 Cl 39.6.
    Source: IS 456:2000, Cl 39.6 — Bresler load contour
    """
    inp = vector["inputs"]
    result = biaxial_bending_check(
        Pu_kN=inp["Pu_kN"],
        Mux_kNm=inp["Mux_kNm"],
        Muy_kNm=inp["Muy_kNm"],
        b_mm=inp["b_mm"],
        D_mm=inp["D_mm"],
        le_mm=inp["le_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
        Asc_mm2=inp["Asc_mm2"],
        d_prime_mm=inp["d_prime_mm"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.01)

    assert result.is_safe is exp["is_safe"]
    assert result.Puz_kN == pytest.approx(exp["Puz_kN"], rel=tol)
    assert result.alpha_n == pytest.approx(exp["alpha_n"], rel=tol)
    assert result.interaction_ratio == pytest.approx(exp["interaction_ratio"], rel=tol)
    assert result.Mux1_kNm == pytest.approx(exp["Mux1_kNm"], rel=tol)
    assert result.Muy1_kNm == pytest.approx(exp["Muy1_kNm"], rel=tol)


# ═══════════════════════════════════════════════════════════════════════════
# Additional Moment (Slenderness) — IS 456 Cl 39.7.1
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_additional_moment_cases"],
    ids=lambda v: v["case_id"],
)
def test_additional_moment_golden(vector: dict):
    """GOLDEN: Additional moment for slender columns per IS 456 Cl 39.7.1.
    Source: IS 456:2000, Cl 39.7.1 — eadd = le²/(2000·D)
    """
    inp = vector["inputs"]
    result = calculate_additional_moment(
        Pu_kN=inp["Pu_kN"],
        b_mm=inp["b_mm"],
        D_mm=inp["D_mm"],
        lex_mm=inp["lex_mm"],
        ley_mm=inp["ley_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
        Asc_mm2=inp["Asc_mm2"],
        d_prime_mm=inp["d_prime_mm"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.01)

    assert result.is_slender_x is exp["is_slender_x"]
    assert result.is_slender_y is exp["is_slender_y"]
    assert result.eadd_x_mm == pytest.approx(exp["eadd_x_mm"], rel=tol)
    assert result.eadd_y_mm == pytest.approx(exp["eadd_y_mm"], abs=0.1)
    assert result.Max_kNm == pytest.approx(exp["Max_kNm"], rel=tol)
    assert result.May_kNm == pytest.approx(exp["May_kNm"], abs=0.1)
    assert result.k == pytest.approx(exp["k"], rel=tol)


# ═══════════════════════════════════════════════════════════════════════════
# Long Column Design — IS 456 Cl 39.7
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_long_design_cases"],
    ids=lambda v: v["case_id"],
)
def test_long_column_design_golden(vector: dict):
    """GOLDEN: Long column design per IS 456 Cl 39.7.
    Source: IS 456:2000, Cl 39.7, 39.7.1, 39.7.1.1
    """
    inp = vector["inputs"]
    result = design_long_column(
        Pu_kN=inp["Pu_kN"],
        M1x_kNm=inp["M1x_kNm"],
        M2x_kNm=inp["M2x_kNm"],
        M1y_kNm=inp["M1y_kNm"],
        M2y_kNm=inp["M2y_kNm"],
        b_mm=inp["b_mm"],
        D_mm=inp["D_mm"],
        lex_mm=inp["lex_mm"],
        ley_mm=inp["ley_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
        Asc_mm2=inp["Asc_mm2"],
        d_prime_mm=inp["d_prime_mm"],
        braced=inp.get("braced", True),
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.01)

    assert result.is_safe is exp["is_safe"]
    assert result.is_slender_x is exp["is_slender_x"]
    assert result.is_slender_y is exp["is_slender_y"]
    assert result.Mux_design_kNm == pytest.approx(exp["Mux_design_kNm"], rel=tol)
    assert result.Muy_design_kNm == pytest.approx(exp["Muy_design_kNm"], rel=tol)
    assert result.interaction_ratio == pytest.approx(exp["interaction_ratio"], rel=tol)
    assert result.governing_check == exp["governing_check"]
    assert result.k == pytest.approx(exp["k"], rel=tol)


# ═══════════════════════════════════════════════════════════════════════════
# Helical Reinforcement — IS 456 Cl 39.4
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["column_helical_cases"],
    ids=lambda v: v["case_id"],
)
def test_helical_reinforcement_golden(vector: dict):
    """GOLDEN: Helical reinforcement check per IS 456 Cl 39.4.
    Source: IS 456:2000, Cl 39.4, 26.5.3.2
    """
    inp = vector["inputs"]
    result = check_helical_reinforcement(
        D_mm=inp["D_mm"],
        D_core_mm=inp["D_core_mm"],
        fck=inp["fck"],
        fy=inp["fy"],
        d_helix_mm=inp["d_helix_mm"],
        pitch_mm=inp["pitch_mm"],
        Pu_axial_kN=inp["Pu_axial_kN"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 0.001)

    assert result.is_adequate is exp["is_adequate"]
    assert result.Pu_enhanced_kN == pytest.approx(exp["Pu_enhanced_kN"], rel=tol)
    assert result.helical_ratio_provided == pytest.approx(
        exp["helical_ratio_provided"], rel=tol
    )
    assert result.helical_ratio_required == pytest.approx(
        exp["helical_ratio_required"], rel=tol
    )
    assert result.pitch_ok is exp["pitch_ok"]
    assert result.enhancement_factor == pytest.approx(1.05, rel=1e-6)


# ═══════════════════════════════════════════════════════════════════════════
# Determinism check — all column golden vectors should be repeatable
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.golden
def test_column_golden_vectors_deterministic():
    """Column design functions must be perfectly deterministic."""
    # Short axial
    r1 = short_axial_capacity(fck=25, fy=415, Ag_mm2=160000, Asc_mm2=1963.4954)
    r2 = short_axial_capacity(fck=25, fy=415, Ag_mm2=160000, Asc_mm2=1963.4954)
    assert r1.Pu_kN == r2.Pu_kN

    # Uniaxial
    r3 = design_short_column_uniaxial(
        Pu_kN=1000,
        Mu_kNm=100,
        b_mm=400,
        D_mm=400,
        le_mm=2600,
        fck=25,
        fy=415,
        Asc_mm2=1963.4954,
        d_prime_mm=50,
    )
    r4 = design_short_column_uniaxial(
        Pu_kN=1000,
        Mu_kNm=100,
        b_mm=400,
        D_mm=400,
        le_mm=2600,
        fck=25,
        fy=415,
        Asc_mm2=1963.4954,
        d_prime_mm=50,
    )
    assert r3.utilization_ratio == r4.utilization_ratio
    assert r3.Pu_cap_kN == r4.Pu_cap_kN
