"""Replay the frozen COL07 circular tied-column single-plane shear cases."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import column

_REFERENCE = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-col07-circular-shear.json"
)
_FIXTURE = json.loads(_REFERENCE.read_text())
_CASES = _FIXTURE["cases"]
_TOLERANCES = _FIXTURE["absolute_tolerances"]


def _assert_shear_row(actual: dict, expected: dict) -> None:
    """Compare the frozen engineering values while retaining product-only fields."""
    assert actual["status"] == ("PASS" if expected["utilization"] <= 1 else "FAIL")
    assert actual["ring_mark"] == "R1"
    assert (
        actual["credited_legs"]
        == _FIXTURE["supplied_shear_basis"]["credit_closed_ring_legs"]
    )
    for key, value in expected.items():
        if isinstance(value, (int, float)):
            tolerance = (
                _TOLERANCES["ratio"]
                if key in {"axial_factor", "utilization", "table_19_tc_nmm2"}
                else (
                    _TOLERANCES["force_kn"]
                    if key.endswith("_kn")
                    else _TOLERANCES["length_mm"]
                )
            )
            assert actual[key] == pytest.approx(value, rel=0, abs=tolerance)
        else:
            assert actual[key] == value


@pytest.mark.parametrize("name", tuple(_CASES))
def test_circular_tied_single_plane_shear_reference(name: str) -> None:
    case = _CASES[name]
    expected = case["expected"]
    request = column.load_circular_column_detailing(
        {**case["request"], "shear_basis": _FIXTURE["supplied_shear_basis"]}
    )
    result = column.check_circular_column_detailing(request)
    assert result.engineering_status.value == expected["status"]
    assert [issue.code for issue in result.issues] == (
        [expected["issue"]] if expected["issue"] is not None else []
    )

    wire = result.to_dict()
    calculation = wire["calculation"]
    assert calculation["shear_status"] == expected["status"]
    assert calculation["end_required_mm"] == pytest.approx(
        expected["straight_end_required_mm"], abs=_TOLERANCES["length_mm"]
    )
    assert calculation["transverse"]["bar_id"] == "R1"
    assert calculation["transverse"]["stations_mm"] == expected["ring_stations_mm"]

    rows = calculation["shear_rows"]
    if expected["status"] == "HOLD":
        assert rows == []
        assert calculation["governing_shear"] is None
    else:
        assert len(rows) == len(expected["evaluated_shear_rows"])
        for actual, reference in zip(
            rows, expected["evaluated_shear_rows"], strict=True
        ):
            _assert_shear_row(actual, reference)
        _assert_shear_row(calculation["governing_shear"], expected["governing_action"])

    input_hash = wire["envelope"]["result_identity"]["input_hash"]
    report = column.render_circular_detailing_html(result)
    drawing = column.render_circular_detailing_svg(result)
    schedule = column.render_circular_detailing_bbs_csv(result)
    assert input_hash in report
    assert request.basis.analysis_revision in report
    assert request.basis.detailing_revision in report
    if expected["governing_action"] is not None:
        governing = expected["governing_action"]
        assert "Single-plane shear" in report
        assert "Governing shear" in report
        assert governing["combination_id"] in report
        assert str(governing["signed_demand_kn"]) in report
        assert f"V{governing['shear_plane']}" in report

    if not expected["bbs_available"]:
        assert expected["issue"] in report and "BBS held." in report
        assert calculation["bbs"] is None
        assert drawing is None
        assert schedule is None
        return

    assert drawing is not None and schedule is not None
    assert drawing in report
    assert request.basis.analysis_revision in drawing
    assert request.basis.detailing_revision in drawing
    assert expected["governing_action"]["combination_id"] in drawing
    root = ElementTree.fromstring(drawing)
    assert (
        root.attrib["data-governing-shear"]
        == expected["governing_action"]["combination_id"]
    )
    assert float(root.attrib["data-governing-station-mm"]) == pytest.approx(
        expected["governing_action"]["station_mm"], abs=_TOLERANCES["length_mm"]
    )
    rings = root.findall(".//{*}line[@data-station-mm][@data-mark='R1']")
    assert [float(ring.attrib["data-station-mm"]) for ring in rings] == expected[
        "ring_stations_mm"
    ]

    bbs = calculation["bbs"]
    assert bbs["quantity"] == expected["bbs_quantity"]
    assert bbs["total_weight_kg"] == pytest.approx(
        expected["bbs_mass_kg"], abs=_TOLERANCES["mass_kg"]
    )
    assert len(bbs["rows"]) == expected["longitudinal_count"] + 1
    bbs_rows = list(csv.DictReader(StringIO(schedule)))
    assert sum(int(row["quantity"]) for row in bbs_rows) == expected["bbs_quantity"]
    assert sum(float(row["total_weight_kg"]) for row in bbs_rows) == pytest.approx(
        expected["bbs_mass_kg"], abs=_TOLERANCES["mass_kg"]
    )
    ring = next(row for row in bbs_rows if row["bar_id"] == "R1")
    assert int(ring["quantity"]) == expected["ring_count"]
    assert float(ring["cut_length_mm"]) == pytest.approx(
        expected["ring_cut_mm"], abs=_TOLERANCES["length_mm"]
    )
    assert all(row["input_hash"] == input_hash for row in bbs_rows)
    assert all(
        row["analysis_revision"] == request.basis.analysis_revision
        and row["detailing_revision"] == request.basis.detailing_revision
        for row in bbs_rows
    )
    longitudinal = [row for row in bbs_rows if row["role"] == "longitudinal"]
    assert len(longitudinal) == expected["longitudinal_count"]
    assert {float(row["cut_length_mm"]) for row in longitudinal} == {
        expected["longitudinal_cut_mm"]
    }
    assert {row["governing_shear_combination_id"] for row in bbs_rows} == {
        expected["governing_action"]["combination_id"]
    }
    assert {float(row["governing_shear_station_mm"]) for row in bbs_rows} == {
        expected["governing_action"]["station_mm"]
    }
