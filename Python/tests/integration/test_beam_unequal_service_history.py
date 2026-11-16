"""Frozen public-API replay for unequal-span finite service history."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from structural_lib.design.is456 import beam

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-serv02-unequal-span.json"
)
REFERENCE_SHA256 = "b9c61eba1a54318fac4dfc79ca2ec389344ad5b7682017e1feb197db9c1d6c25"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]
RECEIPT_COLLECTIONS = (
    "signed_rows",
    "span_deflections",
    "deflection_extrema",
    "crack_sections",
)


def test_unequal_service_history_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


def test_sustained_support_shear_must_match_its_signed_side() -> None:
    payload = deepcopy(CASES["unequal_history"]["request"])
    row = next(
        r for r in payload["member"]["actions"] if r["row_id"] == "SLS-45-G:B-RIGHT"
    )
    row["vu_kn"] *= -1
    result = beam.check_finite_service_history(
        beam.load_finite_service_history(payload)
    )
    assert result.engineering_status.value == "HOLD"
    assert "BEAM.SERVICE_ROWS_HELD" in {item.code for item in result.issues}
    assert result.calculation["history"] is None


def test_restrained_shrinkage_requires_its_own_service_evidence() -> None:
    payload = deepcopy(CASES["unequal_history"]["request"])
    payload["unequal_span_basis"]["axial_restraint"] = "restrained"
    result = beam.check_finite_service_history(
        beam.load_finite_service_history(payload)
    )
    assert result.engineering_status.value == "HOLD"
    assert "BEAM.HISTORY_PROFILE_HELD" in {item.code for item in result.issues}
    assert result.calculation["history"] is None


@pytest.mark.parametrize("name", CASES)
def test_unequal_service_history_replays_public_artifacts(name: str) -> None:
    """The frozen request is passed unchanged through every public route."""
    case = CASES[name]
    source = deepcopy(case["request"])
    request = beam.load_finite_service_history(source)
    assert source == case["request"]

    result = beam.check_finite_service_history(request)
    report = beam.render_finite_service_history_html(result)
    expected = case["expected"]

    assert result.engineering_status.value == expected["status"]
    assert result.identity.case_id == case["request"]["identity"]["case_id"]
    assert "Beam finite service history" in report
    assert expected["status"] in report

    if expected["status"] == "HOLD":
        assert {issue.code for issue in result.issues} >= {expected["issue"]}
        assert result.calculation["history"] is None
        assert "History held." in report
        assert all(issue.message in report for issue in result.issues)
        return

    if expected["status"] == "FAIL":
        assert expected["issue"] in {issue.code for issue in result.issues}
        history = result.calculation["history"]
        assert history is not None
        assert (
            history["governing_crack_station_id"]
            == expected["governing_crack_station_id"]
        )
        assert expected["governing_crack_station_id"] in report
        assert (
            history["crack_checks"][expected["governing_crack_station_id"]][
                "engineering"
            ]
            == "fail"
        )
        return

    _assert_history_receipt(result.calculation["history"], expected)
    _assert_unequal_report(report, case["request"], expected)


def _assert_history_receipt(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    assert actual is not None
    for age in ("initial", "at_finishes", "at_assessment"):
        _assert_subset(actual[age], expected[age])

    for collection in RECEIPT_COLLECTIONS:
        _assert_unordered_rows(actual[collection], expected[collection])

    for key in (
        "governing_deflection_station_id",
        "governing_after_finishes_station_id",
        "governing_crack_station_id",
    ):
        assert actual[key] == expected[key]
    assert actual["uniform_shrinkage_curvature_per_mm"] == pytest.approx(
        expected["uniform_shrinkage_curvature_per_mm"], abs=1e-6
    )


def _assert_unordered_rows(
    actual: list[dict[str, Any]], expected: list[dict[str, Any]]
) -> None:
    """Compare the frozen receipt keys/values while allowing producer order."""
    assert len(actual) == len(expected)
    actual_by_key = {_row_key(row): row for row in actual}
    expected_by_key = {_row_key(row): row for row in expected}
    assert actual_by_key.keys() == expected_by_key.keys()
    for key, expected_row in expected_by_key.items():
        actual_row = actual_by_key[key]
        assert actual_row.keys() == expected_row.keys()
        _assert_subset(actual_row, expected_row)


def _row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    if "row_id" in row:
        return (row["row_id"],)
    if "span_id" in row:
        return (row["span_id"], row["station_id"])
    return (row["station_id"], row["tension_face"])


def _assert_subset(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    assert actual.keys() >= expected.keys()
    for key, value in expected.items():
        observed = actual[key]
        if isinstance(value, float):
            assert observed == pytest.approx(value, abs=1e-6)
        else:
            assert observed == value


def _assert_unequal_report(
    report: str, request: dict[str, Any], expected: dict[str, Any]
) -> None:
    assert "Beam finite service history" in report
    assert "PASS" in report
    for station_key in (
        "governing_deflection_station_id",
        "governing_after_finishes_station_id",
        "governing_crack_station_id",
    ):
        assert expected[station_key] in report
    centres = [support["centre_mm"] for support in request["member"]["supports"]]
    for span_mm in (centres[1] - centres[0], centres[2] - centres[1]):
        assert f"{span_mm:g}" in report
