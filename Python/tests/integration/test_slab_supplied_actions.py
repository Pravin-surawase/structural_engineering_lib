# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Frozen public-facade coverage for supplied slab action rows (SL06)."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

from structural_lib.design.is456 import slab

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = json.loads(
    (ROOT / "docs/verification/library-030-sl06-actions.json").read_text()
)
EXAMPLE = runpy.run_path(
    str(ROOT / "Python/examples/slab_supplied_action_references.py")
)
request_payload = EXAMPLE["request_payload"]
TOLERANCES = FIXTURE["absolute_tolerances"]


def _value(value: object) -> object:
    """Accept the public enum values without depending on their enum class."""
    return getattr(value, "value", value)


def _request(specimen_name: str, route_name: str, scenario: str = "baseline"):
    payload = request_payload(FIXTURE, specimen_name, route_name, scenario)
    return slab.load_action_set(payload)


def _assert_governors(calculation, expected: dict[str, object]) -> None:
    expected = {
        **expected,
        **{
            check_id.replace(".torsion_area_per_layer", ".torsion_bar_diameter"): min(
                calculation.rows
            )
            for check_id, row_id in expected.items()
            if check_id.endswith(".torsion_area_per_layer") and row_id is not None
        },
    }
    assert calculation.governing_ids == expected
    assert set(calculation.governing_rows) == set(expected)
    for check_id, row_id in expected.items():
        governing_row = calculation.governing_rows[check_id]
        if row_id is None:
            assert governing_row is None
        else:
            assert governing_row is calculation.rows[row_id]


def _check_tolerance(check_id: str) -> float:
    if ".area" in check_id or "torsion_area" in check_id:
        return TOLERANCES["reinforcement_mm2_per_m"]
    if check_id.endswith((".diameter", ".spacing", "reviewed_span_depth")):
        return TOLERANCES["length_mm"]
    return TOLERANCES["actions_knm_per_m_or_kn_per_m"]


def _assert_row(
    row, expected: dict[str, object], *, service_held: bool = False
) -> None:
    assert row.signed_moments_knm_per_m == pytest.approx(
        expected["actions"]["signed_moments_knm_per_m"],
        abs=TOLERANCES["actions_knm_per_m_or_kn_per_m"],
        rel=0,
    )
    assert row.support_shear_magnitude_kn_per_m == pytest.approx(
        expected["actions"]["support_shear_magnitude_kn_per_m"],
        abs=TOLERANCES["actions_knm_per_m_or_kn_per_m"],
        rel=0,
    )
    added_corner_checks = {
        check_id.replace(".torsion_area_per_layer", ".torsion_bar_diameter")
        for check_id, frozen in expected["checks"].items()
        if check_id.endswith(".torsion_area_per_layer")
        and frozen["status"] != "NOT_APPLICABLE"
    }
    assert set(row.checks) == set(expected["checks"]) | added_corner_checks
    for check_id in added_corner_checks:
        actual = row.checks[check_id]
        b04 = FIXTURE["specimens"]["B04"]
        assert actual.demand == b04["reinforcement_inputs"]["torsion_bar_diameter_mm"]
        assert (
            actual.limit
            == b04["geometry_material_and_support_inputs"]["thickness_mm"] / 8
        )
        assert _value(actual.status) == "PASS"
    for check_id, frozen in expected["checks"].items():
        actual = row.checks[check_id]
        if service_held and check_id == "reviewed_span_depth":
            assert actual.demand is None
            assert actual.limit is None
            assert actual.utilization is None
            assert _value(actual.status) == "HOLD"
            continue
        tolerance = _check_tolerance(check_id)
        assert actual.demand == pytest.approx(frozen["demand"], abs=tolerance, rel=0)
        assert actual.limit == pytest.approx(frozen["limit"], abs=tolerance, rel=0)
        if frozen["utilization"] is None:
            assert actual.utilization is None
        else:
            assert actual.utilization == pytest.approx(
                frozen["utilization"], abs=TOLERANCES["utilization"], rel=0
            )
        assert _value(actual.status) == frozen["status"]
    assert _value(row.uls) == expected["uls_status"]
    assert _value(row.reviewed_service) == (
        "HOLD" if service_held else expected["reviewed_service_status"]
    )


@pytest.mark.parametrize("route_name", ("external", "builtin"))
def test_b04_action_sets_report_oversized_corner_bars_separately(route_name):
    payload = request_payload(FIXTURE, "B04", route_name, "baseline")
    payload["reinforcement"]["torsion_bar_diameter_mm"] = 25
    result = slab.check_action_set(slab.load_action_set(payload))
    assert _value(result.engineering_status) == "FAIL"
    for row in result.calculation.rows.values():
        for corner in ("x_min_y_min", "x_min_y_max", "x_max_y_min"):
            diameter = row.checks[f"{corner}.torsion_bar_diameter"]
            assert diameter.demand == 25
            assert diameter.limit == 20
            assert diameter.utilization == 1.25
            assert _value(diameter.status) == "FAIL"
            assert (
                _value(row.checks[f"{corner}.torsion_area_per_layer"].status) == "PASS"
            )
        assert "x_max_y_max.torsion_bar_diameter" not in row.checks
    assert result.calculation.governing_ids["x_min_y_min.torsion_bar_diameter"] == "A"


def _assert_row_provenance(specimen_name: str, route_name: str, row) -> None:
    """The normalized row retains the selected coefficient provenance."""
    coefficients = row.coefficients
    route = FIXTURE["specimens"][specimen_name]["coefficient_routes"][route_name]
    assert coefficients is not None
    assert coefficients.verified_by_library is route["verified_by_library"]
    if route_name == "builtin":
        assert coefficients.table_id == route["table_id"]
        if "case_id" in route:
            assert coefficients.case_id == route["case_id"]
    else:
        assert (
            coefficients.source_reference
            == route["inputs"]["coefficient_source_reference"]
        )


def _assert_normalized_rows(specimen_name: str, route_name: str, calculation) -> None:
    """All control routes retain row identity, actions, checks and provenance."""
    for row_id, row in calculation.rows.items():
        assert row.input.row_id == row_id
        assert row.input.coefficient_basis is not None
        assert isinstance(row.signed_moments_knm_per_m, dict)
        assert row.support_shear_magnitude_kn_per_m >= 0
        assert row.checks
        assert row.owner_result is not None
        for check in row.checks.values():
            if _value(check.status) != "HOLD":
                assert check.demand is not None
                assert check.limit is not None
            assert _value(check.status) in {"PASS", "FAIL", "HOLD", "NOT_APPLICABLE"}
        _assert_row_provenance(specimen_name, route_name, row)


@pytest.mark.parametrize("specimen_name", ("B02", "B04"))
@pytest.mark.parametrize("route_name", ("external", "builtin"))
def test_baseline_rows_are_lossless_and_frozen(
    specimen_name: str, route_name: str
) -> None:
    specimen = FIXTURE["specimens"][specimen_name]
    envelope = slab.check_action_set(_request(specimen_name, route_name))
    result = envelope.calculation

    assert set(result.rows) == set(specimen["rows"])
    for row_id, frozen in specimen["rows"].items():
        row = result.rows[row_id]
        assert row.input.row_id == row_id
        assert row.input.factored_area_load_kn_per_m2 == pytest.approx(
            frozen["input"]["factored_area_load_kn_per_m2"]
        )
        assert row.input.coefficient_basis is not None
        _assert_row(row, frozen["expected"])
        _assert_row_provenance(specimen_name, route_name, row)

    expected_status = specimen["expected_status"]
    assert _value(result.coverage) == expected_status["coverage"]
    assert _value(result.uls) == expected_status["uls"]
    assert _value(result.reviewed_service) == expected_status["reviewed_service"]
    assert _value(envelope.engineering_status) == expected_status["engineering"]
    assert result.missing_required_row_ids == ()
    _assert_governors(result, specimen["expected_governing_ids"])


@pytest.mark.parametrize("specimen_name", ("B02", "B04"))
@pytest.mark.parametrize("route_name", ("external", "builtin"))
@pytest.mark.parametrize("scenario", ("reordered", "exact_tie"))
def test_row_order_and_tie_controls_have_frozen_governors(
    specimen_name: str, route_name: str, scenario: str
) -> None:
    control = FIXTURE["specimens"][specimen_name]["controls"][scenario]
    envelope = slab.check_action_set(_request(specimen_name, route_name, scenario))
    result = envelope.calculation

    _assert_normalized_rows(specimen_name, route_name, result)
    specimen = FIXTURE["specimens"][specimen_name]
    for row_id, row in result.rows.items():
        expected = specimen["rows"]["A" if scenario == "exact_tie" else row_id][
            "expected"
        ]
        _assert_row(row, expected)
    assert _value(result.coverage) == control["coverage"]
    _assert_governors(result, control["expected_governing_ids"])


@pytest.mark.parametrize("specimen_name", ("B02", "B04"))
@pytest.mark.parametrize("route_name", ("external", "builtin"))
def test_duplicate_row_ids_are_rejected_at_load(
    specimen_name: str, route_name: str
) -> None:
    with pytest.raises(slab.InputContractError):
        _request(specimen_name, route_name, "duplicate_id")


@pytest.mark.parametrize("specimen_name", ("B02", "B04"))
@pytest.mark.parametrize("route_name", ("external", "builtin"))
def test_missing_required_row_retains_available_evaluation(
    specimen_name: str, route_name: str
) -> None:
    control = FIXTURE["specimens"][specimen_name]["controls"]["missing_B"]
    envelope = slab.check_action_set(_request(specimen_name, route_name, "missing_B"))
    result = envelope.calculation

    _assert_normalized_rows(specimen_name, route_name, result)
    assert set(result.rows) == {"A"}
    assert _value(result.coverage) == control["coverage"]
    assert result.missing_required_row_ids == tuple(control["missing_required_row_ids"])
    assert _value(result.uls) == control["available_uls"]
    assert _value(result.reviewed_service) == control["available_reviewed_service"]
    assert _value(envelope.engineering_status) == control["engineering"]
    _assert_governors(result, control["available_governing_ids"])
    _assert_row(
        result.rows["A"], FIXTURE["specimens"][specimen_name]["rows"]["A"]["expected"]
    )


@pytest.mark.parametrize("specimen_name", ("B02", "B04"))
@pytest.mark.parametrize("route_name", ("external", "builtin"))
def test_missing_shared_service_basis_holds_service_without_losing_uls(
    specimen_name: str, route_name: str
) -> None:
    specimen = FIXTURE["specimens"][specimen_name]
    control = specimen["controls"]["missing_shared_service_basis"]
    envelope = slab.check_action_set(
        _request(specimen_name, route_name, "missing_shared_service_basis")
    )
    result = envelope.calculation

    _assert_normalized_rows(specimen_name, route_name, result)
    assert _value(result.uls) == control["uls"]
    assert _value(result.reviewed_service) == control["reviewed_service"]
    assert _value(envelope.engineering_status) == control["engineering"]
    _assert_governors(result, control["expected_governing_ids"])
    for row_id, frozen in specimen["rows"].items():
        row = result.rows[row_id]
        _assert_row(row, frozen["expected"], service_held=True)
        assert _value(row.uls) == frozen["expected"]["uls_status"]
        assert _value(row.reviewed_service) == "HOLD"
