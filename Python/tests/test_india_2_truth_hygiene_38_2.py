"""INDIA-2 Clause 38.2 truth-hygiene acceptance tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from structural_lib.codes.is456.beam.flexure import (
    calculate_ast_required,
    design_doubly_reinforced,
    design_singly_reinforced,
)
from structural_lib.codes.is456.common.stress_blocks import (
    calculate_ast_from_rectangular_stress_block,
    concrete_moment_capacity,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _lib.indian_code_manifest import build_manifest  # noqa: E402


def test_exact_rectangular_stress_block_closes_equilibrium() -> None:
    ast_mm2, xu_mm = calculate_ast_from_rectangular_stress_block(
        b_mm=230.0,
        d_mm=450.0,
        factored_moment_knm=100.0,
        fck_n_per_mm2=20.0,
        fy_n_per_mm2=415.0,
    )

    assert ast_mm2 == pytest.approx(721.3841475189461)
    assert xu_mm == pytest.approx(157.2800401338862)
    assert concrete_moment_capacity(20.0, 230.0, xu_mm, 450.0) == pytest.approx(
        100.0 * 1_000_000.0
    )


def test_exact_arithmetic_prevents_false_safe_maximum_steel_result() -> None:
    result = design_singly_reinforced(
        b=300.0,
        d=500.0,
        d_total=550.0,
        mu_knm=572.05,
        fck=55.0,
        fy=250.0,
    )

    assert result.Ast_required == pytest.approx(6600.050311675635)
    assert result.Ast_max == pytest.approx(6600.0)
    assert result.is_safe is False
    assert [error.code for error in result.errors] == ["E_FLEXURE_003"]


def test_live_beam_traceability_uses_controlled_source_identifiers() -> None:
    assert calculate_ast_required._is456_clauses == ["38.1", "G-1.1"]
    assert design_singly_reinforced._is456_clauses == ["38.1", "G-1.1"]
    assert design_doubly_reinforced._is456_clauses == [
        "38.1",
        "G-1.1",
        "G-1.2",
    ]

    singly = design_singly_reinforced(230.0, 450.0, 500.0, 100.0, 20.0, 415.0)
    doubly = design_doubly_reinforced(300.0, 450.0, 50.0, 500.0, 250.0, 25.0, 500.0)
    assert singly.clause_refs["Ast"] == "IS 456 Cl 38.1, Annex G-1.1"
    assert doubly.clause_refs["Asc"] == "IS 456 Annex G-1.2"


def test_registry_and_generated_manifest_reject_nonexistent_38_subclauses() -> None:
    registry = json.loads(
        (REPO_ROOT / "Python/structural_lib/codes/is456/clauses.json").read_text(
            encoding="utf-8"
        )
    )
    assert registry["metadata"]["total_clauses"] == len(registry["clauses"])
    assert {"38.2", "38.3", "38.4"}.isdisjoint(registry["clauses"])
    assert "G-1.2" in registry["annexures"]

    is456 = next(
        standard
        for standard in build_manifest()["standards"]
        if standard["namespace"] == "IS456:2000"
    )
    references = {item["reference"]: item for item in is456["references"]}
    assert {"38.2", "38.3", "38.4"}.isdisjoint(references)
    assert references["G-1.2"]["functions"] == [
        "structural_lib.codes.is456.beam.flexure.design_doubly_reinforced"
    ]
    assert is456["registration_summary"]["registration_only_references"] == 0


def test_active_clause_maps_do_not_publish_nonexistent_38_subclauses() -> None:
    clause_map_json = (REPO_ROOT / "docs/reference/clause-map.json").read_text(
        encoding="utf-8"
    )
    clause_map_md = (REPO_ROOT / "docs/reference/clause-map.md").read_text(
        encoding="utf-8"
    )
    for invalid_reference in ("38.2", "38.3", "38.4"):
        assert invalid_reference not in clause_map_json
        assert invalid_reference not in clause_map_md
