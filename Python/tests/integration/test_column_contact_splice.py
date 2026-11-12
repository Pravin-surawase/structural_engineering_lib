"""Frozen independent geometry, section and schedule checks for COL07 contact laps."""

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
    / "docs/verification/library-029-col07-contact-splice.json"
)
_CASES = json.loads(_FIXTURE.read_text())["cases"]


@pytest.mark.parametrize("name", tuple(_CASES))
def test_contact_splice_reference(name):
    case = _CASES[name]
    expected = case["expected"]
    result = column.check_column_member_detailing(
        column.load_column_member_detailing(json.dumps(case["request"]))
    )
    data = result.to_dict()
    calc = data["calculation"]
    assert result.engineering_status.value == expected["status"]
    if expected["issue"]:
        assert expected["issue"] in {issue.code for issue in result.issues}
    report = column.render_column_member_detailing_html(result)
    drawing = column.render_column_member_detailing_svg(result)
    bbs = column.render_column_member_bbs_csv(result)
    assert (bbs is not None) == expected["bbs_available"]
    assert drawing in report
    root = ElementTree.fromstring(drawing)
    identity = data["envelope"]["result_identity"]["input_hash"]
    assert identity in report and identity in drawing
    if bbs is None:
        assert calc["bbs"] is None
        return

    splice = calc["contact_splice"]
    assert splice["lap_stations_mm"] == expected["lap_stations_mm"]
    assert splice["end_support_distances_mm"] == expected["end_support_distances_mm"]
    for key in (
        "minimum_unrelated_bar_clear_mm",
        "minimum_link_clear_mm",
        "steel_ratio",
    ):
        assert splice[key] == pytest.approx(expected[key])
    assert splice["required_lap_mm"] == pytest.approx(
        expected["contact_lap_required_mm"]
    )
    assert splice["end_mm"] - splice["start_mm"] == expected["overlap_mm"]
    assert calc["laps"][0]["required_mm"] == splice["required_lap_mm"]
    for name, suffix in (("lower", "-L"), ("upper", "-U")):
        actual_centres = {
            bar["bar_id"].removesuffix(suffix): [
                bar["x_from_left_mm"],
                bar["y_from_top_mm"],
            ]
            for bar in splice["sections"][name]["bars"]
        }
        assert actual_centres == expected[f"{name}_bar_centres_mm"]

    for row, ref in zip(calc["actions"], expected["section_rows"], strict=True):
        assert row["station_mm"] == ref["station_mm"]
        layouts = row["section"]["splice_layouts"]
        assert layouts.keys() == ref["capacities_knm"].keys()
        for label, axes in ref["capacities_knm"].items():
            for axis, capacity in axes.items():
                assert layouts[label]["axes"][axis]["capacity_knm"] == pytest.approx(
                    capacity, abs=0.003
                )

    schedule = calc["bbs"]
    assert schedule["quantity"] == expected["bbs_quantity"]
    assert schedule["total_length_mm"] == pytest.approx(expected["bbs_total_mm"])
    assert schedule["total_weight_kg"] == pytest.approx(expected["bbs_mass_kg"])
    rows = {row["bar_id"]: row for row in csv.DictReader(StringIO(bbs))}
    assert rows.keys() == expected["cuts"].keys()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    elevations = {
        piece.attrib["data-piece-id"]: (
            float(piece.attrib["data-start-mm"]),
            float(piece.attrib["data-end-mm"]),
        )
        for piece in root.findall(".//svg:line[@data-piece-id]", ns)
    }
    assert len(elevations) == 10
    overlap = root.find(".//svg:g[@data-section='overlap']", ns)
    assert len(overlap.findall("svg:circle", ns)) == 10
    assert overlap.find("svg:g[@data-link-mark='LX']", ns) is not None
    for mark, (quantity, cut, diameter) in expected["cuts"].items():
        row = rows[mark]
        assert row["input_hash"] == identity
        assert row["analysis_revision"] == "A1" and row["detailing_revision"] == "D1"
        assert int(row["quantity"]) == quantity
        assert float(row["cut_length_mm"]) == pytest.approx(cut)
        assert float(row["diameter_mm"]) == diameter
        assert mark in report
        if mark in elevations:
            start, end = elevations[mark]
            assert end - start == cut
        else:
            assert (
                len(root.findall(f".//svg:line[@data-bar-id='{mark}']", ns)) == quantity
            )
