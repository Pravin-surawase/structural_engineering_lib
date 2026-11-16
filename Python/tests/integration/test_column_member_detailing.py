"""Replay frozen COL07 actions, tie levels and artifact identity."""

from __future__ import annotations

import csv
import importlib
import json
from copy import deepcopy
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
_TWO_PLANE_CASES = json.loads(
    _REFERENCE.with_name("library-030-col07-two-plane-shear.json").read_text()
)["cases"]


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
    rendered_csv = column.render_column_member_bbs_csv(result)
    if name == "combined_shear":
        assert svg is None
        assert "Checked drawing withheld" in report
        assert rendered_csv is None
        assert "COLUMN.COMBINED_SHEAR" in {issue.code for issue in result.issues}
        return
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


@pytest.mark.parametrize("name", _TWO_PLANE_CASES)
def test_two_plane_shear_reference_and_checked_outputs(name):
    case = _TWO_PLANE_CASES[name]
    expected = case["expected"]
    request = column.load_column_member_detailing(case["request"])
    result = column.check_column_member_detailing(request)
    wire = result.to_dict()
    calculation = wire["calculation"]
    report = column.render_column_member_detailing_html(result)
    drawing = column.render_column_member_detailing_svg(result)
    schedule = column.render_column_member_bbs_csv(result)

    assert result.engineering_status.value == expected["status"]
    assert f"Column member detailing · {expected['status']}" in report
    assert (drawing is not None) is expected["checked_drawing_available"]
    assert (schedule is not None) is expected["bbs_available"]
    if expected["issue"]:
        assert expected["issue"] in {issue.code for issue in result.issues}
        assert expected["issue"] in report
    if not expected["checked_drawing_available"]:
        assert "Checked drawing withheld" in report
        assert "<svg" not in report
    if not expected["bbs_available"]:
        assert "BBS withheld" in report
        assert calculation["bbs"] is None

    rows = [row for row in calculation["actions"] if row["shear"] is not None]
    if not expected["evaluated_shear_rows"]:
        assert rows == []
        assert calculation["governing_shear"] is None
        return

    assert len(rows) == 1
    shear = rows[0]["shear"]
    assert shear["direction"] == "xy"
    assert shear["status"] == expected["status"]
    assert (
        shear["interaction_basis"]
        == case["request"]["basis"]["two_plane_interaction_basis"]
    )
    assert shear["interaction_limit"] == pytest.approx(
        expected["governing_action"]["interaction_limit"]
    )
    assert shear["interaction_utilization"] == pytest.approx(
        expected["governing_action"]["interaction_utilization"]
    )
    assert shear["utilization"] == pytest.approx(shear["interaction_utilization"])
    assert shear["governing_check"] == expected["governing_action"]["check"]
    assert {(plane["direction"], plane["demand_kn"]) for plane in shear["planes"]} == {
        (plane["direction"], plane["signed_demand_kn"])
        for plane in expected["evaluated_shear_rows"]
    }
    expected_by_direction = {
        plane["direction"]: plane for plane in expected["evaluated_shear_rows"]
    }
    for plane in shear["planes"]:
        reference = expected_by_direction[plane["direction"]]
        assert plane["status"] == ("PASS" if reference["utilization"] <= 1 else "FAIL")
        for actual_key, expected_key in (
            ("demand_kn", "signed_demand_kn"),
            ("width_mm", "web_width_mm"),
            ("d_mm", "d_mm"),
            ("pitch_mm", "pitch_mm"),
            ("pitch_limit_mm", "pitch_limit_mm"),
            ("base_concrete_stress_nmm2", "table_19_tc_nmm2"),
            ("concrete_crushing_stress_nmm2", "table_20_tc_max_nmm2"),
            ("effective_hoop_area_mm2", "effective_hoop_area_mm2"),
            ("capacity_kn", "capacity_kn"),
            ("utilization", "utilization"),
        ):
            assert plane[actual_key] == pytest.approx(reference[expected_key])
        assert plane["link_spacing_pass"] is reference["link_spacing_pass"]
        assert plane["governing_check"] == "COLUMN.SHEAR_CAPACITY"

    governing = calculation["governing_shear"]
    assert governing["combination_id"] == expected["governing_action"]["combination_id"]
    assert governing["station_mm"] == expected["governing_action"]["station_mm"]
    assert governing["shear"] == shear
    assert "shared hoop interaction" in report.lower()
    assert f"{shear['interaction_utilization']:.4f}" in report
    if expected["status"] != "PASS":
        return

    assert drawing is not None and "Shared-hoop interaction" in drawing
    assert drawing in report
    assert schedule is not None
    bbs = calculation["bbs"]
    physical = expected["physical_bbs_reference"]
    assert bbs["quantity"] == physical["bbs_quantity"] == 83
    assert bbs["total_length_mm"] == pytest.approx(physical["bbs_length_mm"])
    assert bbs["total_length_mm"] == pytest.approx(88850)
    assert bbs["total_weight_kg"] == pytest.approx(physical["bbs_weight_kg"])
    assert bbs["total_weight_kg"] == pytest.approx(112.949681, abs=1e-6)
    csv_rows = list(csv.DictReader(StringIO(schedule)))
    hoop = next(row for row in csv_rows if row["bar_id"] == "H")
    assert float(hoop["cut_length_mm"]) == pytest.approx(physical["hoop_cut_mm"])
    svg = ElementTree.fromstring(drawing)
    assert [
        float(line.attrib["data-station-mm"])
        for line in svg.iter()
        if line.attrib.get("data-bar-id") == "H"
    ] == physical["hoop_stations_mm"]


@pytest.mark.parametrize("pitch,status", [(120, "PASS"), (140, "FAIL")])
@pytest.mark.parametrize("two_plane", [False, True])
def test_actual_shear_zone_requires_minimum_hoop_steel(pitch, status, two_plane):
    request = deepcopy(
        _TWO_PLANE_CASES["two_plane_pass"]["request"]
        if two_plane
        else _CASES["six_bar_omit_x_face_midpoints"]["request"]
    )
    request["tie_fy_nmm2"] = 250
    request["tie_zones"][1]["pitch_mm"] = pitch
    request["actions"] = [
        {
            "combination_id": "U1",
            "check_station_mm": 1500,
            "pu_kn": 500,
            "mx_knm": 30,
            "my_knm": 21,
            "vx_kn": -40 if two_plane else -70,
            "vy_kn": 30 if two_plane else 0,
        }
    ]
    result = column.check_column_member_detailing(
        column.load_column_member_detailing(request)
    )
    calculation = result.calculation
    assert result.engineering_status.value == status
    shear = calculation["governing_shear"]["shear"]
    plane_x = shear["planes"][0] if two_plane else shear
    assert plane_x["direction"] == "x"
    assert plane_x["pitch_mm"] == pitch
    assert plane_x["utilization"] < 1
    assert plane_x["minimum_shear_reinforcement_pitch_limit_mm"] == pytest.approx(
        136.65928043
    )
    assert plane_x["geometric_pitch_limit_mm"] == 180
    if two_plane:
        assert shear["planes"][1]["link_spacing_pass"]
        assert (shear["interaction_utilization"] is not None) == (status == "PASS")
    report = column.render_column_member_detailing_html(result)
    assert "136.659 mm" in report
    assert (column.render_column_member_detailing_svg(result) is not None) == (
        status == "PASS"
    )
    assert (column.render_column_member_bbs_csv(result) is not None) == (
        status == "PASS"
    )
    if status == "FAIL":
        assert shear["governing_check"] == "COLUMN.SHEAR_MINIMUM_REINFORCEMENT"
        assert "COLUMN.SHEAR_MINIMUM_REINFORCEMENT" in {
            issue.code for issue in result.issues
        }
        assert "<svg" not in report
        if two_plane:
            assert "Interaction withheld because a link pitch check failed" in report


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


def test_mixed_column_cage_requires_all_four_corner_bars():
    payload = deepcopy(_MIXED_CASES["mixed_continuous"]["request"])
    bars = payload["reinforcement"]["bars"]
    corner = next(bar for bar in bars if bar["bar_id"] == "C4")
    corner["y_from_top_mm"] = 360
    request = column.load_positioned_column_member_detailing(payload)
    result = column.check_column_member_detailing(request)

    assert result.engineering_status.value == "FAIL"
    assert {issue.code for issue in result.issues} == {"COLUMN.PERIMETER_RESTRAINT"}
    assert column.render_column_member_bbs_csv(result) is None
    drawing = column.render_column_member_detailing_svg(result)
    assert drawing is not None
    assert "FAIL" in ElementTree.fromstring(drawing).find("{*}title").text


_SLENDER_CASES = json.loads(
    _REFERENCE.with_name("library-029-col07-slender-member.json").read_text()
)["cases"]


@pytest.mark.parametrize("name", _SLENDER_CASES)
def test_slender_member_action_binding_and_schedule(name):
    case = _SLENDER_CASES[name]
    expected = case["expected"]
    request = column.load_slender_column_member_detailing(case["request"])
    result = column.check_column_member_detailing(request)
    assert result.engineering_status.value == expected["status"]
    wire = result.to_dict()
    calculation = wire["calculation"]
    identity = wire["envelope"]["result_identity"]["input_hash"]
    report = column.render_column_member_detailing_html(result)
    drawing = column.render_column_member_detailing_svg(result)
    schedule = column.render_column_member_bbs_csv(result)
    assert identity in report and identity in drawing and drawing in report
    if name == "stale_analysis":
        assert wire["envelope"]["freshness_status"] == "STALE"
    if name == "unmatched_second_order":
        assert calculation["slender_member"] is None
    if "shear" in expected:
        actual = calculation["actions"][1]["shear"]
        if expected["shear"] is None:
            assert actual is None
            assert "COLUMN.COMBINED_SHEAR" in {issue.code for issue in result.issues}
        else:
            assert actual is not None
            assert actual["credited_hoop_id"] == "HOOP"
            for key, value in expected["shear"].items():
                assert actual[key] == (
                    pytest.approx(value) if isinstance(value, (int, float)) else value
                )
            assert "Governing supplied shear: U1 at 3000 mm" in report
    if expected["status"] != "PASS":
        assert schedule is None
        return
    assert schedule is not None and identity in schedule
    assert calculation["hoop_stations_mm"] == expected["hoop_stations_mm"]
    strength = calculation["slender_member"]["calculation"]["strength"]
    assert strength["governing_id"] == expected["governing_id"]
    assert strength["governing_ratio"] == pytest.approx(
        expected["governing_ratio"], rel=1e-4
    )
    assert calculation["bbs"]["quantity"] == expected["quantity"]
    assert calculation["bbs"]["total_length_mm"] == pytest.approx(
        expected["total_length_mm"]
    )
    assert calculation["bbs"]["total_weight_kg"] == pytest.approx(expected["mass_kg"])
