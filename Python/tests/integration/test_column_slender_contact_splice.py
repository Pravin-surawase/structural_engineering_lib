"""Frozen COL07 slender-column contact-lap acceptance evidence."""

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
    / "docs/verification/library-030-col07-slender-lap-reference.json"
)
_REFERENCE = json.loads(_FIXTURE.read_text())
_CASES = _REFERENCE["cases"]
_TOLERANCES = _REFERENCE["absolute_tolerances"]


def _approx(value, tolerance="length_mm"):
    return pytest.approx(value, abs=_TOLERANCES[tolerance], rel=0)


@pytest.mark.parametrize("name", tuple(_CASES))
def test_slender_contact_splice_frozen_reference(name):
    """Replay all S2 decisions, withholding checked outputs outside PASS."""
    fixture = _CASES[name]
    expected = fixture["expected"]
    request = column.load_slender_column_member_detailing(fixture["request"])
    result = column.check_column_member_detailing(request)
    wire = result.to_dict()
    calculation = wire["calculation"]
    report = column.render_column_member_detailing_html(result)
    drawing = column.render_column_member_detailing_svg(result)
    schedule = column.render_column_member_bbs_csv(result)

    assert result.engineering_status.value == expected["status"]
    issues = {issue.code for issue in result.issues}
    if expected["issue"] is None:
        assert not issues
    else:
        assert expected["issue"] in issues
    assert bool(drawing) is expected["svg_available"]
    assert bool(schedule) is expected["bbs_available"]
    assert f"Column member detailing · {expected['status']}" in report

    if name != "s1_pass":
        # A diagnostic report survives every non-PASS outcome, but checked
        # drawing/schedule output must never be embedded or returned.
        assert expected["issue"] in report
        assert drawing is None
        assert schedule is None
        assert "Checked drawing withheld" in report
        assert "BBS withheld" in report
        assert calculation["bbs"] is None
        assert "<svg" not in report
        if "lap_actual_mm" in expected:
            lap = calculation["laps"][0]
            assert lap["provided_mm"] == _approx(expected["lap_actual_mm"])
            assert lap["required_mm"] == _approx(expected["lap_required_mm"])
        if "minimum_supplied_lap_stress_nmm2" in expected:
            check = next(
                row for row in calculation["checks"] if row["code"] == expected["issue"]
            )
            assert check["minimum_gross_stress_nmm2"] == _approx(
                expected["minimum_supplied_lap_stress_nmm2"], "stress_nmm2"
            )
        if "actual_contact_centre_distance_mm" in expected:
            check = next(
                row for row in calculation["checks"] if row["code"] == expected["issue"]
            )
            assert (
                check["actual_separation_mm"]
                == expected["actual_contact_centre_distance_mm"]
            )
            assert (
                check["required_separation_mm"]
                == expected["required_contact_centre_distance_mm"]
            )
        return

    identity = wire["envelope"]["result_identity"]["input_hash"]
    assert drawing is not None and schedule is not None
    assert drawing in report
    for rendered in (report, drawing, schedule):
        assert identity in rendered

    splice = calculation["contact_splice"]
    assert splice["end_mm"] - splice["start_mm"] == _approx(expected["lap_actual_mm"])
    assert splice["required_lap_mm"] == _approx(expected["lap_required_mm"])
    assert calculation["end_required_mm"] == _approx(
        expected["end_development_required_mm"]
    )
    lap_check = next(
        check
        for check in calculation["checks"]
        if check["code"] == "COLUMN.LAP_COMPRESSION_BASIS"
    )
    assert lap_check["minimum_gross_stress_nmm2"] == _approx(
        min(expected["gross_kern_stress_nmm2"]), "stress_nmm2"
    )
    hoop = next(
        series for series in calculation["transverse"] if series["role"] == "hoop"
    )
    assert [
        station
        for station in hoop["stations_mm"]
        if splice["start_mm"] <= station <= splice["end_mm"]
    ] == expected["lap_hoop_stations_mm"]
    assert splice["lap_stations_mm"] == expected["lap_link_stations_mm"]
    assert splice["end_support_distances_mm"] == expected["end_support_distances_mm"]
    assert splice["minimum_unrelated_bar_clear_mm"] == _approx(
        expected["minimum_unrelated_clear_mm"]
    )
    assert splice["minimum_link_clear_mm"] == _approx(expected["minimum_3d_clear_mm"])

    # Explicit physical phases preserve the lower and upper bar populations at MID.
    sections = {
        (action["station_id"], label): layout
        for action in calculation["actions"]
        for label, layout in action["section"]["splice_layouts"].items()
    }
    assert set(sections) == {
        ("A", "lower"),
        ("MID", "lower"),
        ("MID", "upper"),
        ("B", "upper"),
    }
    for reference in expected["section_phase_checks"]:
        label = (
            "lower"
            if reference["physical_phase"].endswith("LOWER")
            or reference["physical_phase"] == "LOWER_ONLY"
            else "upper"
        )
        actual = sections[(reference["station_id"], label)]
        assert actual["physical_phase"] == reference["physical_phase"]
        assert actual["governing_ratio"] == _approx(reference["ratio"], "section_ratio")
        assert actual["contour_ratio"] == _approx(
            reference["contour_ratio"], "section_ratio"
        )
        assert actual["direct_ratio"] == _approx(
            reference["direct_ratio"], "section_ratio"
        )
        assert actual["puz_kn"] == pytest.approx(reference["puz_kn"], abs=0.001, rel=0)
        assert actual["alpha_n"] == _approx(reference["alpha_n"], "section_ratio")
        assert actual["axes"]["x_negative"]["capacity_knm"] == _approx(
            reference["capacity_x_knm"], "moment_knm"
        )
        assert actual["axes"]["y_positive"]["capacity_knm"] == _approx(
            reference["capacity_y_knm"], "moment_knm"
        )
    governing = calculation["governing_section"]
    assert governing["combination_id"] == "U1"
    assert governing["station_id"] == "MID"
    assert governing["section"]["governing_layout"] == "upper"
    assert governing["section"]["physical_phase"] == "OVERLAP_UPPER"
    assert governing["section"]["utilization"] == _approx(
        expected["governing_section"]["ratio"], "section_ratio"
    )

    bbs = calculation["bbs"]
    assert bbs["quantity"] == expected["bbs_quantity"]
    assert bbs["total_length_mm"] == _approx(expected["bbs_total_mm"])
    assert bbs["total_weight_kg"] == _approx(expected["bbs_mass_kg"], "mass_kg")
    rows = {row["bar_id"]: row for row in csv.DictReader(StringIO(schedule))}
    assert rows.keys() == expected["cuts"].keys()
    for mark, (quantity, cut_length, diameter) in expected["cuts"].items():
        row = rows[mark]
        assert int(row["quantity"]) == quantity
        assert float(row["cut_length_mm"]) == _approx(cut_length)
        assert float(row["diameter_mm"]) == _approx(diameter)
        assert row["input_hash"] == identity
        assert mark in report

    root = ElementTree.fromstring(drawing)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    assert [
        float(marker.attrib["data-station-mm"])
        for marker in root.findall(".//svg:*[@data-marker='lap-boundary']", ns)
    ] == expected["svg_markers"]["member_z_mm"]
    assert [
        float(marker.attrib["data-station-mm"])
        for marker in root.findall(".//svg:*[@data-station-mm]", ns)
        if marker.attrib.get("data-bar-id") == "S1-LINK"
    ] == expected["svg_markers"]["lap_link_stations_mm"]
    overlap = root.find(".//svg:g[@data-section='overlap']", ns)
    assert overlap is not None
    centres = [
        [float(circle.attrib["cx"]), float(circle.attrib["cy"])]
        for circle in overlap.findall("svg:circle", ns)
        if circle.attrib["data-piece-mark"]
        in {"M_LEFT-L", "M_RIGHT-L", "M_LEFT-U", "M_RIGHT-U"}
    ]
    assert centres == expected["svg_markers"]["side_pair_centres_mm"]
