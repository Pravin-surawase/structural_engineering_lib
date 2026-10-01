"""Independent known-depth Annex G branch and demand-equilibrium regressions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.codes.is456.beam.flexure import (
    calculate_mu_lim_flanged,
    design_doubly_reinforced,
    design_flanged_beam,
)
from structural_lib.services.api import design_flanged_beam_is456

_REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[1]
        / "data/benchmark_vectors/flanged_branch_reference.json"
    ).read_text(encoding="utf-8")
)


def service_inputs(case):
    section = case["inputs"]
    return {
        "units": "IS456",
        "beam_type": "T",
        "moment_region": "sagging",
        "load_case_basis": "single_factored_case",
        "mu_knm": case["mu_knm"],
        "vu_kn": 0,
        "bw_mm": section["bw"],
        "D_mm": section["d_total"],
        "d_mm": section["d"],
        "span_mm": 6000,
        "flange_thickness_mm": section["Df"],
        "flange_overhang_left_mm": (section["bf"] - section["bw"]) / 2,
        "flange_overhang_right_mm": (section["bf"] - section["bw"]) / 2,
        "fck_nmm2": section["fck"],
        "fy_nmm2": section["fy"],
    }


@pytest.mark.parametrize("case", _REFERENCE["cases"], ids=lambda c: c["id"])
def test_flange_state_matches_independent_force_and_moment(case):
    section, expected = case["inputs"], case["expected"]
    result = design_flanged_beam(**section, mu_knm=case["mu_knm"])
    assert result.is_safe
    assert result.xu == pytest.approx(expected["xu"], abs=1e-9)
    assert result.xu <= result.xu_max
    assert result.Ast_required == pytest.approx(expected["Ast_required"], abs=1e-8)
    assert result.Asc_required == 0
    assert calculate_mu_lim_flanged(
        **{k: v for k, v in section.items() if k != "d_total"}
    ) == pytest.approx(expected["Mu_lim"], abs=1e-9)
    if case["branch"] != "rectangular":
        assert result.Mu_lim == pytest.approx(expected["Mu_lim"], abs=1e-9)
        assert result.clause_refs["xu"] == (
            "IS 456 Annex G-2.2"
            if case["branch"] == "limiting"
            else "IS 456 Annex G-2.3"
        )
    if expected["yf"] is None:
        concrete_force = 0.36 * section["fck"] * section["bf"] * result.xu
        moment = concrete_force * (section["d"] - 0.42 * result.xu)
    else:
        web = 0.36 * section["fck"] * section["bw"] * result.xu
        flange = (
            0.45 * section["fck"] * (section["bf"] - section["bw"]) * expected["yf"]
        )
        concrete_force = web + flange
        moment = web * (section["d"] - 0.42 * result.xu)
        moment += flange * (section["d"] - expected["yf"] / 2)
    assert moment == pytest.approx(case["mu_knm"] * 1e6, abs=1e-6, rel=1e-12)
    assert 0.87 * section["fy"] * result.Ast_required == pytest.approx(
        concrete_force, abs=1e-6, rel=1e-12
    )
    if section["bf"] > section["bw"]:
        service = design_flanged_beam_is456(**service_inputs(case))
        assert service.bf_effective_mm == section["bf"]
        assert service.design.flexure == result
        # A valid flexural state can exceed the separate Table 19 lookup
        # domain. Retain that consumer failure instead of clamping pt.
        independent_pt = expected["Ast_required"] * 100 / (section["bw"] * section["d"])
        if 0.15 <= independent_pt <= 3.0:
            assert service.is_ok
        else:
            assert not service.is_ok
            assert any(
                "Table 19 range" in check for check in service.design.failed_checks
            )


@pytest.mark.parametrize("case", _REFERENCE["unsupported"], ids=lambda c: c["id"])
def test_rounded_branch_gap_cannot_be_reported_as_a_converged_safe_design(case):
    assert case["gap_knm"] > 0
    result = design_flanged_beam(**case["inputs"], mu_knm=case["mu_knm"])
    assert not result.is_safe
    assert result.Ast_required == result.xu == 0
    assert [e.code for e in result.errors] == ["E_FLEXURE_005"]
    assert result.clause_refs["xu"] == "IS 456 Annex G-2.3"
    service = design_flanged_beam_is456(**service_inputs(case))
    assert not service.is_ok
    assert service.design.flexure == result
    assert any(check.startswith("flexure") for check in service.design.failed_checks)


@pytest.mark.parametrize("df", (216.0, 225.0, 280.0))
def test_flange_containing_the_limit_uses_rectangular_compression_with_retained_cap(df):
    # G-2.1 defines the concrete geometry; this checks reuse of the unchanged
    # rectangular compression-steel routine, not an independent steel-law oracle.
    capacity = 0.36 * 25 * 600 * 216 * (450 - 0.42 * 216) / 1e6
    moment = 1.05 * capacity
    result = design_flanged_beam(300, 600, 450, df, 500, moment, 25, 415)
    rectangular = design_doubly_reinforced(600, 450, 50, 500, moment, 25, 415)
    assert result.is_safe
    assert result.Mu_lim == pytest.approx(capacity, abs=1e-9)
    assert result.xu == result.xu_max == 216
    assert result.Ast_required == rectangular.Ast_required
    assert result.Asc_required == rectangular.Asc_required > 0
    assert result.Ast_max == 0.04 * 300 * 500
