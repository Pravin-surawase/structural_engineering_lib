"""Frozen source-profile, sign/clipping and independent compression-bar checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.codes.is456.beam.flexure import (
    design_doubly_reinforced,
    design_flanged_beam,
)
from structural_lib.codes.is456.materials import STEEL_STRAIN_METHOD, get_steel_stress
from structural_lib.codes.is456.section_materials import section_steel_stress

_REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[1]
        / "data/benchmark_vectors/material_profile_reference.json"
    ).read_text(encoding="utf-8")
)


@pytest.mark.parametrize("state", _REFERENCE["steel_states"], ids=lambda s: s["id"])
def test_representative_steel_matches_frozen_decimal_source(state):
    actual = get_steel_stress(state["strain"], state["fy"])
    assert actual == pytest.approx(state["stress_nmm2"], abs=1e-10)
    assert actual == section_steel_stress(state["strain"], state["fy"])
    assert abs(actual) <= state["fy"] / 1.15 + 1e-12
    assert get_steel_stress(-state["strain"], state["fy"]) == pytest.approx(
        -actual, abs=1e-12
    )
    assert STEEL_STRAIN_METHOD == _REFERENCE["source"]["method"]


@pytest.mark.parametrize("case", _REFERENCE["doubly_reinforced"], ids=lambda c: c["id"])
def test_compression_steel_force_and_demand_match_independent_anchors(case):
    inputs, expected = case["inputs"], case["expected"]
    result = design_doubly_reinforced(**inputs)
    assert result.Mu_lim == pytest.approx(expected["Mu_lim"], abs=1e-9)
    assert result.xu == pytest.approx(expected["xu"], abs=1e-9)
    assert result.Asc_required == pytest.approx(expected["Asc_required"], abs=1e-8)
    assert result.Ast_required == pytest.approx(expected["Ast_required"], abs=1e-8)
    assert result.Ast_max == expected["Ast_max"]
    assert result.is_safe == expected["is_safe"]
    excess = (
        result.Asc_required
        * (expected["fsc"] - expected["fcc"])
        * (inputs["d"] - inputs["d_dash"])
    )
    assert excess / 1e6 + result.Mu_lim == pytest.approx(inputs["mu_knm"], abs=1e-9)
    tension = 0.87 * inputs["fy"] * result.Ast_required
    compression = 0.36 * inputs["fck"] * inputs["b"] * result.xu
    compression += result.Asc_required * (expected["fsc"] - expected["fcc"])
    assert tension == pytest.approx(compression, abs=1e-6)


@pytest.mark.parametrize(
    "case", _REFERENCE["flanged_compression"], ids=lambda c: c["id"]
)
def test_inherited_flange_compression_consumers_preserve_independent_equilibrium(case):
    inputs, expected = case["inputs"], case["expected"]
    result = design_flanged_beam(**inputs)
    for name in ("Mu_lim", "xu", "Ast_required", "Asc_required", "Ast_max"):
        assert getattr(result, name) == pytest.approx(expected[name], abs=1e-8), name
    assert result.is_safe == expected["is_safe"]
    added_force = result.Asc_required * (expected["fsc"] - expected["fcc"])
    assert 0.87 * inputs["fy"] * result.Ast_required == pytest.approx(
        expected["base_compression_force_n"] + added_force, abs=1e-6
    )
    assert result.Mu_lim + added_force * (
        inputs["d"] - inputs["d_dash"]
    ) / 1e6 == pytest.approx(inputs["mu_knm"], abs=1e-8)
