"""Replay frozen COL07 actions, tie levels and artifact identity."""

from __future__ import annotations

import csv
import importlib
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import column
from structural_lib.services.capabilities import get_supported_is456_capability_document

_REFERENCE = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-029-col07-column-member.json"
)
_CASES = json.loads(_REFERENCE.read_text())["cases"]


@pytest.mark.parametrize("name", tuple(_CASES))
def test_column_detailing_reference(name):
    case = _CASES[name]
    reference = case["expected"]
    request = column.load_column_member_detailing(json.dumps(case["request"]))
    result = column.check_column_member_detailing(request)
    assert result.engineering_status.value == reference["status"]
    assert result.qualified_review_required
    if reference["issue"]:
        assert reference["issue"] in {issue.code for issue in result.issues}

    payload = result.to_dict()
    calc = payload["calculation"]
    assert calc["end_required_mm"] == pytest.approx(reference["end_required_mm"])
    assert calc["lap_required_mm"] == pytest.approx(reference["lap_required_mm"])
    assert calc["hoop_stations_mm"] == reference["hoop_stations_mm"]
    rows = [row for row in calc["actions"] if row["shear"] is not None]
    assert len(rows) == len(reference["shear_rows"])
    for actual, expected in zip(rows, reference["shear_rows"], strict=True):
        assert actual["station_mm"] == expected["station_mm"]
        for key, value in expected.items():
            if key != "station_mm":
                assert actual["shear"][key] == pytest.approx(value, abs=1e-8)
        assert actual["action"] in case["request"]["actions"]
    if name == "continuous":
        governing = calc["governing_shear"]
        assert governing["combination_id"] == "U1"
        assert governing["station_mm"] == 150
        assert governing["shear"]["credited_hoop_id"] == "H"
    if name == "lap_numeric_pass":
        check = next(c for c in calc["checks"] if c["code"] == "COLUMN.LAP_LENGTH")
        assert check["status"] == "PASS"
        assert check["actual_mm"] == 700
        assert calc["laps"][0]["bar_ids"] == ["C1", "C2"]

    input_hash = payload["envelope"]["result_identity"]["input_hash"]
    report = column.render_column_member_detailing_html(result)
    svg = column.render_column_member_detailing_svg(result)
    assert svg in report
    for output in (report, svg):
        for token in (
            input_hash,
            request.identity.member_id,
            request.basis.analysis_revision,
            request.basis.detailing_revision,
            reference["status"],
        ):
            assert token in output
    root = ElementTree.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    projected = {}
    for line in root.findall(".//svg:line[@data-bar-id]", ns):
        projected.setdefault(line.attrib["data-bar-id"], []).append(
            float(line.attrib["data-station-mm"])
        )
    assert projected == {
        bar["bar_id"]: bar["stations_mm"] for bar in calc["transverse"]
    }
    rendered_csv = column.render_column_member_bbs_csv(result)
    if not reference["bbs_available"]:
        assert rendered_csv is None
        assert calc["bbs"] is None
        return
    bbs = calc["bbs"]
    assert bbs["quantity"] == reference["bbs_quantity"]
    assert bbs["total_length_mm"] == pytest.approx(reference["bbs_length_mm"])
    assert bbs["total_weight_kg"] == pytest.approx(reference["bbs_weight_kg"])
    csv_rows = list(csv.DictReader(StringIO(rendered_csv)))
    assert len(csv_rows) == len(bbs["rows"])
    assert sum(int(row["quantity"]) for row in csv_rows) == bbs["quantity"]
    for row in csv_rows:
        assert row["member_id"] == request.identity.member_id
        assert row["input_hash"] == input_hash
        assert row["analysis_revision"] == request.basis.analysis_revision
        assert row["detailing_revision"] == request.basis.detailing_revision
        assert row["bar_id"] in report
        if row["role"] != "longitudinal":
            assert int(row["quantity"]) == len(projected[row["bar_id"]])


def test_member_detailing_capability_resolves():
    document = get_supported_is456_capability_document()
    column_info = next(
        row for row in document["capabilities"] if row["capability_id"] == "column"
    )
    profile = next(
        row
        for row in column_info["python_profiles"]
        if row["operation"] == "check_column_member_detailing"
    )
    module = importlib.import_module(profile["module"])
    request = getattr(module, profile["loader"])(_CASES["continuous"]["request"])
    assert request.schema_version == profile["request_schema"]
    assert (
        getattr(module, profile["operation"])(request).workflow_id
        == profile["workflow_id"]
    )


_MIXED_CASES = json.loads(
    _REFERENCE.with_name("library-029-col07-mixed-member.json").read_text()
)["cases"]


@pytest.mark.parametrize("name", _MIXED_CASES)
def test_positioned_mixed_member_quantities_and_outputs(name):
    fixture = _MIXED_CASES[name]
    request = column.load_positioned_column_member_detailing(fixture["request"])
    result = column.check_column_member_detailing(request)
    expected = fixture["expected"]
    assert result.engineering_status.value == expected["status"]
    identity = result.to_dict()["envelope"]["result_identity"]["input_hash"]
    drawing = column.render_column_member_detailing_svg(result)
    assert identity in drawing
    report = column.render_column_member_detailing_html(result)
    assert drawing in report and identity in report
    bbs = column.render_column_member_bbs_csv(result)
    if expected["status"] != "PASS":
        assert bbs is None
        return
    assert bbs is not None and identity in bbs
    calculation = result.to_dict()["calculation"]
    assert calculation["hoop_stations_mm"] == expected["hoop_stations_mm"]
    assert calculation["end_required_mm"] == pytest.approx(expected["end_required_mm"])
    for row, reference in zip(calculation["actions"], expected["shear"], strict=True):
        assert row["section"]["status"] == "PASS"
        for key, value in reference.items():
            assert row["shear"][key] == pytest.approx(value)
    rows = list(csv.DictReader(StringIO(bbs)))
    lengths = {
        row["bar_id"]: float(row["cut_length_mm"])
        for row in rows
        if row["role"] == "cross_tie"
    }
    assert lengths == pytest.approx(expected["cross_tie_cut_mm"])
    for key in ("quantity", "total_length_mm", "total_weight_kg"):
        assert calculation["bbs"][key] == pytest.approx(expected[key])
    assert len([row for row in rows if row["role"] == "longitudinal"]) == 12
    assert len(ElementTree.fromstring(drawing).findall(".//{*}circle")) == 12
