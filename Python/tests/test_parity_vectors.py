"""
Parity Test Runner — Python ↔ VBA Validation

This module loads parity_test_vectors.json and runs the same test cases
that VBA should also run. Matching results across both implementations
ensures parity.

Usage:
    pytest tests/test_parity_vectors.py -v
    pytest tests/test_parity_vectors.py -v -k "flexure"
"""

import json
import pytest
from pathlib import Path

from structural_lib import flexure, shear, detailing, serviceability, bbs


# =============================================================================
# Load Test Vectors
# =============================================================================


def load_vectors() -> dict:
    """Load parity test vectors from JSON file."""
    vectors_path = Path(__file__).parent / "data" / "parity_test_vectors.json"
    with open(vectors_path, "r", encoding="utf-8") as f:
        return json.load(f)


VECTORS = load_vectors()
TOLERANCES = VECTORS["tolerance_rules"]


def within_tolerance(actual: float, expected: float, key: str) -> bool:
    """Check if actual value is within tolerance of expected."""
    # Get tolerance from rules, default to 1% relative tolerance
    abs_tol = TOLERANCES.get(key, 0.01 * abs(expected) if expected != 0 else 0.01)
    return abs(actual - expected) <= abs_tol


# =============================================================================
# Flexure Singly Reinforced Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    VECTORS.get("flexure_singly", []),
    ids=lambda v: v["id"],
)
def test_flexure_singly(vector):
    """Test singly reinforced flexure design against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    result = flexure.design_singly_reinforced(
        inp["b_mm"],
        inp["d_mm"],
        inp["d_total_mm"],
        inp["mu_knm"],
        inp["fck_nmm2"],
        inp["fy_nmm2"],
    )

    # Check is_safe
    assert result.is_safe == exp["is_safe"], f"is_safe mismatch for {vector['id']}"

    # Check Mu,lim if expected
    if "mu_lim_knm" in exp:
        assert within_tolerance(
            result.mu_lim, exp["mu_lim_knm"], "mu_knm"
        ), f"Mu,lim mismatch: {result.mu_lim} vs {exp['mu_lim_knm']}"

    # Check Ast
    if "ast_required_mm2" in exp:
        assert within_tolerance(
            result.ast_required, exp["ast_required_mm2"], "ast_mm2"
        ), f"Ast mismatch: {result.ast_required} vs {exp['ast_required_mm2']}"

    # Check section type
    if "section_type" in exp:
        assert (
            result.section_type.name == exp["section_type"]
        ), f"Section type mismatch: {result.section_type.name} vs {exp['section_type']}"


# =============================================================================
# Flexure Doubly Reinforced Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    VECTORS.get("flexure_doubly", []),
    ids=lambda v: v["id"],
)
def test_flexure_doubly(vector):
    """Test doubly reinforced flexure design against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    result = flexure.design_doubly_reinforced(
        inp["b_mm"],
        inp["d_mm"],
        inp["d_dash_mm"],
        inp["d_total_mm"],
        inp["mu_knm"],
        inp["fck_nmm2"],
        inp["fy_nmm2"],
    )

    assert result.is_safe == exp["is_safe"]

    if "ast_required_mm2" in exp:
        assert within_tolerance(
            result.ast_required, exp["ast_required_mm2"], "ast_mm2"
        ), f"Ast mismatch: {result.ast_required} vs {exp['ast_required_mm2']}"

    if "asc_required_mm2" in exp:
        assert within_tolerance(
            result.asc_required, exp["asc_required_mm2"], "asc_mm2"
        ), f"Asc mismatch: {result.asc_required} vs {exp['asc_required_mm2']}"


# =============================================================================
# Flexure Flanged Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    VECTORS.get("flexure_flanged", []),
    ids=lambda v: v["id"],
)
def test_flexure_flanged(vector):
    """Test flanged beam flexure design against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    result = flexure.design_flanged_beam(
        inp["bw_mm"],
        inp["bf_mm"],
        inp["d_mm"],
        inp["Df_mm"],
        inp["d_total_mm"],
        inp["mu_knm"],
        inp["fck_nmm2"],
        inp["fy_nmm2"],
    )

    assert result.is_safe == exp["is_safe"]

    if "ast_required_mm2" in exp:
        assert within_tolerance(
            result.ast_required, exp["ast_required_mm2"], "ast_mm2"
        ), f"Ast mismatch: {result.ast_required} vs {exp['ast_required_mm2']}"


# =============================================================================
# Shear Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    VECTORS.get("shear", []),
    ids=lambda v: v["id"],
)
def test_shear(vector):
    """Test shear design against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    result = shear.design_shear(
        vu_kn=inp["vu_kn"],
        b=inp["b_mm"],
        d=inp["d_mm"],
        fck=inp["fck_nmm2"],
        fy=inp["fy_nmm2"],
        asv=inp["asv_mm2"],
        pt=inp["pt_percent"],
    )

    assert result.is_safe == exp["is_safe"]

    if "tv_nmm2" in exp:
        assert within_tolerance(
            result.tv, exp["tv_nmm2"], "stress_nmm2"
        ), f"τv mismatch: {result.tv} vs {exp['tv_nmm2']}"

    if "tc_nmm2" in exp:
        assert within_tolerance(
            result.tc, exp["tc_nmm2"], "stress_nmm2"
        ), f"τc mismatch: {result.tc} vs {exp['tc_nmm2']}"

    if "spacing_mm" in exp:
        assert within_tolerance(
            result.spacing, exp["spacing_mm"], "spacing_mm"
        ), f"Spacing mismatch: {result.spacing} vs {exp['spacing_mm']}"


# =============================================================================
# Detailing Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    [v for v in VECTORS.get("detailing", []) if "ld_mm" in v.get("expected", {})],
    ids=lambda v: v["id"],
)
def test_development_length(vector):
    """Test development length calculation against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    ld = detailing.calculate_development_length(
        bar_dia=inp["bar_dia_mm"],
        fck=inp["fck_nmm2"],
        fy=inp["fy_nmm2"],
        bar_type=inp.get("bar_type", "deformed"),
    )

    assert within_tolerance(
        ld, exp["ld_mm"], "length_mm"
    ), f"Ld mismatch: {ld} vs {exp['ld_mm']}"


@pytest.mark.parametrize(
    "vector",
    [
        v
        for v in VECTORS.get("detailing", [])
        if "lap_length_mm" in v.get("expected", {})
    ],
    ids=lambda v: v["id"],
)
def test_lap_length(vector):
    """Test lap length calculation against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    lap = detailing.calculate_lap_length(
        bar_dia=inp["bar_dia_mm"],
        fck=inp["fck_nmm2"],
        fy=inp["fy_nmm2"],
        bar_type=inp.get("bar_type", "deformed"),
        is_seismic=inp.get("is_seismic", False),
        in_tension=inp.get("in_tension", True),
    )

    assert within_tolerance(
        lap, exp["lap_length_mm"], "length_mm"
    ), f"Lap length mismatch: {lap} vs {exp['lap_length_mm']}"


@pytest.mark.parametrize(
    "vector",
    [v for v in VECTORS.get("detailing", []) if "spacing_mm" in v.get("expected", {})],
    ids=lambda v: v["id"],
)
def test_bar_spacing(vector):
    """Test bar spacing calculation against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    spacing = detailing.calculate_bar_spacing(
        b=inp["b_mm"],
        cover=inp["cover_mm"],
        stirrup_dia=inp["stirrup_dia_mm"],
        bar_dia=inp["bar_dia_mm"],
        bar_count=inp["bar_count"],
    )

    assert within_tolerance(
        spacing, exp["spacing_mm"], "spacing_mm"
    ), f"Spacing mismatch: {spacing} vs {exp['spacing_mm']}"


# =============================================================================
# Serviceability Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    [
        v
        for v in VECTORS.get("serviceability", [])
        if "ld_ratio" in v.get("expected", {})
    ],
    ids=lambda v: v["id"],
)
def test_deflection_span_depth(vector):
    """Test deflection span/depth check against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    result = serviceability.check_deflection_span_depth(
        span_mm=inp["span_mm"],
        d_mm=inp["d_mm"],
        support_condition=inp["support_condition"],
    )

    assert result.is_ok == exp["is_ok"]

    if "ld_ratio" in exp:
        assert within_tolerance(
            result.computed["ld_ratio"], exp["ld_ratio"], "ratio"
        ), f"L/d ratio mismatch: {result.computed['ld_ratio']} vs {exp['ld_ratio']}"


@pytest.mark.parametrize(
    "vector",
    [v for v in VECTORS.get("serviceability", []) if "wcr_mm" in v.get("expected", {})],
    ids=lambda v: v["id"],
)
def test_crack_width(vector):
    """Test crack width check against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    result = serviceability.check_crack_width(
        exposure_class=inp["exposure_class"],
        limit_mm=inp["limit_mm"],
        acr_mm=inp["acr_mm"],
        cmin_mm=inp["cmin_mm"],
        h_mm=inp["h_mm"],
        x_mm=inp["x_mm"],
        epsilon_m=inp["epsilon_m"],
    )

    assert result.is_ok == exp["is_ok"]


# =============================================================================
# BBS Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    [v for v in VECTORS.get("bbs", []) if "weight_kg" in v.get("expected", {})],
    ids=lambda v: v["id"],
)
def test_bar_weight(vector):
    """Test bar weight calculation against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    weight = bbs.calculate_bar_weight(
        diameter_mm=inp["diameter_mm"],
        length_mm=inp["length_mm"],
    )

    assert (
        abs(weight - exp["weight_kg"]) < 0.02
    ), f"Weight mismatch: {weight} vs {exp['weight_kg']}"


@pytest.mark.parametrize(
    "vector",
    [v for v in VECTORS.get("bbs", []) if "cut_length_mm" in v.get("expected", {})],
    ids=lambda v: v["id"],
)
def test_stirrup_cut_length(vector):
    """Test stirrup cut length calculation against parity vectors."""
    inp = vector["inputs"]
    exp = vector["expected"]

    cut_length = bbs.calculate_stirrup_cut_length(
        b_mm=inp["b_mm"],
        D_mm=inp["D_mm"],
        cover_mm=inp["cover_mm"],
        stirrup_dia_mm=inp["stirrup_dia_mm"],
    )

    assert within_tolerance(
        cut_length, exp["cut_length_mm"], "length_mm"
    ), f"Cut length mismatch: {cut_length} vs {exp['cut_length_mm']}"


# =============================================================================
# Summary Report
# =============================================================================


def test_parity_vector_coverage():
    """Ensure all vector categories are covered."""
    categories = [
        "flexure_singly",
        "flexure_doubly",
        "flexure_flanged",
        "shear",
        "detailing",
        "serviceability",
        "bbs",
    ]

    for cat in categories:
        assert cat in VECTORS, f"Missing category: {cat}"
        assert len(VECTORS[cat]) > 0, f"Empty category: {cat}"

    # Print summary
    print("\n=== Parity Vector Summary ===")
    for cat in categories:
        print(f"  {cat}: {len(VECTORS[cat])} vectors")
