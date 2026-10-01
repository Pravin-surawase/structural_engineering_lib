"""Source-defined SLS anchors and explicit unsupported consumer outcomes."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from structural_lib.codes.is456.beam.serviceability import (
    SLS_METHOD,
    calculate_creep_deflection,
    calculate_effective_moment_of_inertia,
    calculate_shrinkage_curvature,
    check_deflection_level_b,
    check_deflection_level_c,
    get_creep_coefficient,
)

_REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[1]
        / "data/benchmark_vectors/sls_annexc_reference.json"
    ).read_text(encoding="utf-8")
)


@pytest.mark.parametrize("state", _REFERENCE["states"], ids=lambda s: s["id"])
def test_service_components_match_independent_decimal_and_virtual_work(state):
    actual = check_deflection_level_c(**state["inputs"])
    expected = state["expected"]
    assert actual.computed["method"] == _REFERENCE["source"]["method"] == SLS_METHOD
    assert actual.is_ok == expected["is_ok"]
    for key in (
        "mcr_knm",
        "icr_mm4",
        "igross_mm4",
        "ieff_mm4",
        "delta_immediate_mm",
        "delta_creep_mm",
        "delta_shrinkage_mm",
        "delta_total_mm",
        "delta_limit_mm",
        "creep_coefficient",
        "shrinkage_curvature",
    ):
        assert getattr(actual, key) == pytest.approx(
            expected[key], rel=2e-12, abs=1e-12
        ), key
    for key in (
        "x_mm",
        "z_mm",
        "ec_nmm2",
        "delta_permanent_initial_mm",
        "delta_permanent_long_term_mm",
        "permanent_concrete_stress_nmm2",
    ):
        assert actual.computed[key] == pytest.approx(
            expected[key], rel=2e-12, abs=1e-12
        ), key
    for path in ("permanent_initial_section", "permanent_long_term_section"):
        for key in ("x_mm", "ec_nmm2", "icr_mm4", "ieff_mm4"):
            assert actual.computed[path][key] == pytest.approx(
                expected[path][key], rel=2e-12
            )
    assert actual.icr_mm4 <= actual.ieff_mm4 <= actual.igross_mm4
    assert actual.computed["load_basis"] == "UNFACTORED_SERVICE"
    assert actual.delta_total_mm == pytest.approx(
        actual.delta_immediate_mm + actual.delta_creep_mm + actual.delta_shrinkage_mm
    )


@pytest.mark.parametrize("case", _REFERENCE["unsupported"], ids=lambda s: s["id"])
def test_unqualified_sls_domain_never_returns_a_safe_total(case):
    result = check_deflection_level_c(**case["inputs"])
    assert not result.is_ok
    assert result.computed["status"] == case["expected_status"]
    assert math.isinf(result.delta_total_mm)
    assert result.computed["reason"]


@pytest.mark.parametrize(
    "state",
    [_REFERENCE["states"][0], _REFERENCE["states"][1], _REFERENCE["states"][30]],
)
def test_level_b_reports_immediate_but_holds_missing_long_term_basis(state):
    inputs = state["inputs"]
    accepted = {
        k: v
        for k, v in inputs.items()
        if k
        not in (
            "age_at_loading_days",
            "relative_humidity_percent",
            "shrinkage_strain",
            "ma_sustained_knm",
            "ma_live_knm",
        )
    }
    result = check_deflection_level_b(
        **accepted, ma_service_knm=inputs["ma_sustained_knm"] + inputs["ma_live_knm"]
    )
    assert not result.is_ok
    assert result.computed["status"] == "HOLD_UNSUPPORTED"
    assert result.delta_short_mm == pytest.approx(
        state["expected"]["delta_immediate_mm"], rel=2e-12
    )
    assert math.isinf(result.delta_total_mm)


def test_scalar_helpers_require_the_missing_source_geometry_or_stiffness():
    with pytest.raises(ValueError, match="neutral axis"):
        calculate_effective_moment_of_inertia(
            mcr_knm=40, ma_knm=80, igross_mm4=3e9, icr_mm4=1e9
        )
    with pytest.raises(ValueError, match="overall depth"):
        calculate_shrinkage_curvature(d_mm=450, ast_mm2=1200, b_mm=300)
    with pytest.raises(ValueError, match="effective Ec"):
        calculate_creep_deflection(delta_sustained_mm=5, creep_coefficient=1.6)
    with pytest.raises(ValueError, match="no interpolation"):
        get_creep_coefficient(age_at_loading_days=14)
