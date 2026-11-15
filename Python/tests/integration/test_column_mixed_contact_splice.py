"""Frozen integration evidence for the COL07 mixed-diameter contact splice."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import column

_FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-col07-mixed-splice.json"
)
_CASES = json.loads(_FIXTURE.read_bytes())["cases"]


def _check(checks, code):
    return next(check for check in checks if check["code"] == code)


def _approx(actual, expected):
    for key, value in expected.items():
        key = "demand_kn" if key == "signed_demand_kn" else key
        if key == "pitch_limit_mm":
            continue
        if isinstance(value, dict):
            _approx(actual[key], value)
        elif isinstance(value, list):
            assert actual[key] == pytest.approx(value)
        elif isinstance(value, (float, int)):
            assert actual[key] == pytest.approx(value, abs=0.001)
        else:
            assert actual[key] == value


def _actions(calculation):
    return {row["combination_id"]: row for row in calculation["actions"]}


def test_mixed_contact_splice_baseline_geometry_sections_shear_and_outputs():
    case = _CASES["mixed_contact_splice"]
    expected = case["expected"]
    request = column.load_positioned_column_member_detailing(case["request"])
    result = column.check_column_member_detailing(request)
    payload = result.to_dict()
    calculation = payload["calculation"]

    assert result.engineering_status.value == "PASS"
    splice = calculation["contact_splice"]
    lap = calculation["laps"][0]
    assert lap["provided_mm"] == expected["provided_lap_mm"]
    assert lap["required_mm"] == pytest.approx(expected["required_contact_lap_mm"])
    assert splice["required_lap_mm"] == pytest.approx(
        expected["required_contact_lap_mm"]
    )
    assert splice["end_support_distances_mm"] == pytest.approx(
        expected["restraint_distances_outer_inner_inner_outer_mm"]
    )
    assert (
        splice["transverse_level_clear_mm"]
        == expected["minimum_transverse_level_clear_mm"]
    )
    assert (
        splice["transverse_end_cover_mm"] == expected["minimum_end_face_link_cover_mm"]
    )
    assert splice["steel_ratio"] == pytest.approx(
        expected["geometry"]["overlap_steel_ratio"]
    )
    assert splice["minimum_unrelated_bar_clear_mm"] == pytest.approx(
        expected["geometry"]["minimum_unrelated_clear_mm"]
    )
    assert splice["minimum_link_clear_mm"] == pytest.approx(
        expected["geometry"]["lx_seat_clear_mm"]
    )
    assert splice["lap_stations_mm"] == expected["transverse_stations_mm"]["LX"]
    checks = calculation["checks"]
    pitch = _check(checks, "COLUMN.LAP_TIE_PITCH")
    assert (pitch["actual_mm"], pitch["limit_mm"]) == (
        expected["maximum_lap_hoop_pitch_mm"],
        expected["approved_pitch_limit_mm"],
    )
    development = _check(checks, "COLUMN.END_DEVELOPMENT")
    lengths = {
        float(key): value
        for key, value in development["required_by_diameter_mm"].items()
    }
    assert lengths == pytest.approx(
        {
            float(key): value
            for key, value in expected["required_end_projection_by_diameter_mm"].items()
        }
    )
    assert (
        max(lengths, key=lengths.__getitem__)
        == expected["governing_end_projection_diameter_mm"]
    )
    compression = _check(checks, "COLUMN.LAP_COMPRESSION_BASIS")
    assert compression["status"] == "PASS"
    assert (
        compression["minimum_gross_stress_nmm2"]
        >= (expected["u2_interval_compression"]["minimum_gross_stress_nmm2"])
    )

    actions = _actions(calculation)
    assert actions.keys() == expected["actions"].keys()
    for combination_id, reference in expected["actions"].items():
        actual = actions[combination_id]
        assert actual["station_mm"] == reference["station_mm"]
        assert actual["section"]["governing_layout"] == reference["governing_section"]
        _approx(actual["shear"], reference["shear"])
        assert (
            actual["section"]["splice_layouts"].keys() == reference["sections"].keys()
        )
        for layout, section in reference["sections"].items():
            measured = actual["section"]["splice_layouts"][layout]
            assert measured["governing_ratio"] == pytest.approx(
                section["governing_ratio"], abs=0.001
            )
            for axis, axis_reference in section["axes"].items():
                assert measured["axes"][axis]["capacity_knm"] == pytest.approx(
                    axis_reference["capacity_knm"], abs=0.12
                )
    assert (
        calculation["governing_shear"]["combination_id"]
        == expected["governing_shear_row"]
    )
    assert (
        calculation["governing_section"]["combination_id"]
        == expected["governing_section_row"]
    )
    assert set(actions["U2"]["section"]["splice_layouts"]) == {"lower", "upper"}

    identity = payload["envelope"]["result_identity"]["input_hash"]
    report = column.render_column_member_detailing_html(result)
    drawing = column.render_column_member_detailing_svg(result)
    schedule = column.render_column_member_bbs_csv(result)
    assert schedule is not None and drawing in report
    for report_value in (
        "Governing supplied section: U1 at 250 mm",
        "Governing supplied shear: U1 at 250 mm",
        "The Ø20 bars govern end development.",
        "<td>1170–1810</td><td>640</td><td>638.00</td>",
        "130 pieces · 167.374 m · 179.888 kg",
    ):
        assert report_value in report
    for output in (report, drawing, schedule):
        for token in (
            identity,
            request.identity.member_id,
            request.basis.analysis_revision,
            request.basis.detailing_revision,
        ):
            assert token in output
    bbs = calculation["bbs"]
    assert bbs["quantity"] == expected["bbs_quantity"]
    assert bbs["total_length_mm"] == pytest.approx(expected["bbs_total_mm"])
    assert bbs["total_weight_kg"] == pytest.approx(expected["bbs_mass_kg"])
    rows = {row["bar_id"]: row for row in csv.DictReader(StringIO(schedule))}
    assert rows.keys() == expected["cuts_qty_length_diameter"].keys()
    for mark, (quantity, length, diameter) in expected[
        "cuts_qty_length_diameter"
    ].items():
        row = rows[mark]
        assert (int(row["quantity"]), float(row["diameter_mm"])) == (quantity, diameter)
        assert float(row["cut_length_mm"]) == pytest.approx(length)
        assert row["input_hash"] == identity
        assert row["analysis_revision"] == "A1" and row["detailing_revision"] == "D2"
    svg = ElementTree.fromstring(drawing)
    lines = {
        line.get("data-piece-id"): line
        for line in svg.findall(".//{*}line[@data-piece-id]")
    }
    assert lines.keys() == expected["longitudinal_pieces"].keys()
    for mark, piece in expected["longitudinal_pieces"].items():
        assert float(lines[mark].get("data-start-mm")) == pytest.approx(
            piece["start_mm"]
        )
        assert float(lines[mark].get("data-end-mm")) == pytest.approx(piece["end_mm"])
    drawn_stations = {}
    for line in svg.findall(".//{*}line[@data-station-mm]"):
        drawn_stations.setdefault(line.get("data-bar-id"), []).append(
            float(line.get("data-station-mm"))
        )
    assert drawn_stations == expected["transverse_stations_mm"]
    for label in ("lower", "overlap", "upper"):
        section = svg.find(f".//{{*}}g[@data-section='{label}']")
        assert section is not None
        marks = {
            link.get("data-link-mark")
            for link in section.findall("{*}g[@data-link-mark]")
        }
        assert marks == {"Y1", "Y2", "LX" if label == "overlap" else "X1"}
        for mark in ("L1", "R1"):
            if label != "upper":
                lower = section.find(f".//{{*}}circle[@data-piece-mark='{mark}-L']")
                assert lower is not None
                assert [float(lower.get(axis)) for axis in ("cx", "cy")] == (
                    expected["geometry"]["lower_centres_mm"][mark]
                )
            if label != "lower":
                upper = section.find(f".//{{*}}circle[@data-piece-mark='{mark}-U']")
                assert upper is not None
                assert [float(upper.get(axis)) for axis in ("cx", "cy")] == (
                    expected["geometry"]["partner_centres_mm"][mark]
                )


@pytest.mark.parametrize(
    "name",
    (
        "short_lap",
        "congested_partner",
        "missing_end_restraint",
        "short_anchor",
        "inadequate_shear",
        "numeric_only",
        "missing_compression_basis",
    ),
)
def test_mixed_contact_splice_fail_and_hold_controls_withhold_artifacts(name):
    case = _CASES[name]
    expected = case["expected"]
    result = column.check_column_member_detailing(
        column.load_positioned_column_member_detailing(case["request"])
    )
    calculation = result.to_dict()["calculation"]
    assert result.engineering_status.value == expected["status"]
    assert [issue.code for issue in result.issues] == [expected["governing_issue"]]
    assert any(
        check["status"] == expected["status"]
        for check in calculation["checks"]
        if check["code"] == expected["governing_issue"]
    )
    assert calculation["bbs"] is None
    assert column.render_column_member_bbs_csv(result) is None
    report = column.render_column_member_detailing_html(result)
    drawing = column.render_column_member_detailing_svg(result)
    assert drawing in report and expected["governing_issue"] in report

    splice = calculation["contact_splice"]
    if name == "short_lap":
        assert calculation["laps"][0]["provided_mm"] == expected["provided_lap_mm"]
        assert splice["required_lap_mm"] == pytest.approx(
            expected["required_contact_lap_mm"]
        )
    elif name == "congested_partner":
        control = _check(calculation["checks"], expected["governing_issue"])
        assert control["limiting_bar_ids"] == expected["governing_pair"]
        assert control["actual_mm"] == pytest.approx(expected["minimum_clear_mm"])
        assert control["limit_mm"] == expected["required_clear_mm"]
    elif name == "missing_end_restraint":
        assert splice["end_support_distances_mm"] == pytest.approx(
            expected["restraint_distances_mm"]
        )
    elif name == "short_anchor":
        checks = [
            check
            for check in calculation["checks"]
            if check["code"] == "COLUMN.END_DEVELOPMENT"
        ]
        assert any(
            check["actual_mm"] == expected["provided_mm"]
            and check["required_mm"] == pytest.approx(expected["required_mm"])
            for check in checks
        )
    elif name == "inadequate_shear":
        actual = _actions(calculation)["U1"]["shear"]
        _approx(actual, {key: expected[key] for key in actual if key in expected})
        assert actual["demand_kn"] == expected["signed_demand_kn"]
