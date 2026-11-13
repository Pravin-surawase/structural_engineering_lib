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
_CORNER_CASES = json.loads(
    _FIXTURE.with_name("library-029-col07-corner-splice.json").read_text()
)["cases"]


def _centres(bars, suffix):
    return {
        bar["bar_id"].removesuffix(suffix): [
            bar["x_from_left_mm"],
            bar["y_from_top_mm"],
        ]
        for bar in bars
    }


@pytest.mark.parametrize(
    "case",
    [pytest.param(case, id=name) for name, case in _CASES.items()]
    + [pytest.param(case, id=f"corner-{name}") for name, case in _CORNER_CASES.items()],
)
def test_contact_splice_reference(case):
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
    for key in ("minimum_unrelated_bar_clear_mm", "minimum_link_clear_mm"):
        assert splice[key] == pytest.approx(expected[key])
    is_corner = "upper_centres_mm" in expected
    required = expected["required_lap_mm" if is_corner else "contact_lap_required_mm"]
    assert splice["required_lap_mm"] == pytest.approx(required)
    assert splice["end_mm"] - splice["start_mm"] == expected["overlap_mm"]
    assert calc["laps"][0]["required_mm"] == splice["required_lap_mm"]
    if is_corner:
        assert splice["corner_level_clear_mm"] == expected["minimum_level_clear_mm"]
        assert splice["corner_end_cover_mm"] == expected["minimum_end_cover_mm"]
        assert [row["shear"]["d_mm"] for row in calc["actions"]] == expected[
            "shear_depths_mm"
        ]
        assert "Supplemental corner link level clearance 4.00 mm" in report
        assert (
            _centres(splice["sections"]["upper"]["bars"], "-U")
            == expected["upper_centres_mm"]
        )
    else:
        assert splice["steel_ratio"] == pytest.approx(expected["steel_ratio"])
        for label, suffix in (("lower", "-L"), ("upper", "-U")):
            assert (
                _centres(splice["sections"][label]["bars"], suffix)
                == expected[f"{label}_bar_centres_mm"]
            )

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
    mark = "CL" if is_corner else "LX"
    assert overlap.find(f"svg:g[@data-link-mark='{mark}']", ns) is not None
    if is_corner:
        # Above the lap the spine mirrors to y=96, away from M_TOP.
        cx = root.find(
            ".//svg:g[@data-section='upper']/svg:g[@data-link-mark='CX']/svg:path", ns
        )
        assert cx is not None and cx.get("d") == "M 60 96 L 240 96"
        left = root.find(".//svg:line[@data-piece-id='C1-L']", ns)
        right = root.find(".//svg:line[@data-piece-id='C2-L']", ns)
        assert (
            left is not None and right is not None and left.get("x1") != right.get("x1")
        )
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
