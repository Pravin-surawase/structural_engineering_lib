"""Replay the frozen COL07 circular tied-column contact-lap cases.

The fixture is intentionally the engineering oracle: this test reaches the
feature only through the public column façade and checks the released report,
drawing and schedule contracts as well as the calculation payload.
"""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import column

_ROOT = Path(__file__).resolve().parents[3]
_FIXTURE = json.loads(
    (
        _ROOT / "docs/verification/library-030-col07-circular-lap-reference.json"
    ).read_text()
)
_CASES = _FIXTURE["cases"]
_TOL = _FIXTURE["absolute_tolerances"]
_PASS = "circular_contact_lap"
_LAP_SCALARS = (
    "lap_provided_mm",
    "lap_required_mm",
    "contact_centre_distance_mm",
    "maximum_lap_pitch_mm",
    "minimum_gross_stress_nmm2",
)


def _tolerance(key: str) -> float:
    if key.endswith("_knm"):
        return _TOL["moment_knm"]
    if key.endswith("_kn"):
        return _TOL["force_kn"]
    if key.endswith("_nmm2"):
        return _TOL["stress_nmm2"]
    if "ratio" in key or key in {"alpha_n", "utilization"}:
        return _TOL["ratio"]
    if key.endswith("_kg"):
        return _TOL["mass_kg"]
    return _TOL["length_mm"]


def _assert_reference(actual, expected, key: str = "") -> None:
    """Compare fixture values while allowing product-only presentation fields."""
    if isinstance(expected, dict):
        for name, value in expected.items():
            assert name in actual
            _assert_reference(actual[name], value, name)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for received, wanted in zip(actual, expected, strict=True):
            _assert_reference(received, wanted, key)
    elif isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=0, abs=_tolerance(key))
    else:
        assert actual == expected


@pytest.mark.parametrize("name", tuple(_CASES))
def test_circular_contact_lap_reference_cases(name: str) -> None:
    case = _CASES[name]
    expected = case["expected"]
    request = column.load_circular_column_detailing(case["request"])
    result = column.check_circular_column_detailing(request)
    wire = result.to_dict()
    calculation = wire["calculation"]

    assert result.engineering_status.value == expected["status"]
    assert [issue.code for issue in result.issues] == expected["issues"]
    lap = calculation["lap"]
    if lap is not None:
        for key in _LAP_SCALARS:
            assert lap[key] == pytest.approx(expected[key], rel=0, abs=_tolerance(key))

    input_hash = wire["envelope"]["result_identity"]["input_hash"]
    report = column.render_circular_detailing_html(result)
    drawing = column.render_circular_detailing_svg(result)
    schedule = column.render_circular_detailing_bbs_csv(result)
    assert input_hash in report

    if expected["status"] != "PASS":
        assert drawing is None
        assert schedule is None
        assert "<svg" not in report.lower()
        assert expected["issues"][0] in report
        assert lap is None or any(key in lap for key in _LAP_SCALARS)
        return

    assert drawing is not None and schedule is not None
    assert drawing in report
    assert input_hash in drawing and input_hash in schedule
    assert "Lap 840 mm · required 797.5 mm" in report
    assert "Lap ring pitch 75 mm · limit 75 mm" in report
    assert "Minimum gross-section compressive stress +0.585902 N/mm²" in report
    _assert_pass_calculation(calculation, expected)
    _assert_pass_artifacts(drawing, schedule, expected, input_hash)


def _assert_pass_calculation(calculation: dict, expected: dict) -> None:
    lap = calculation["lap"]
    assert isinstance(lap, dict)
    for key, value in expected.items():
        if key in {
            "status",
            "issues",
            "checked_drawing_available",
            "bbs_available",
            "strength_by_phase",
            "governing_strength",
            "bbs",
        }:
            continue
        assert key in lap
        _assert_reference(lap[key], value, key)
    pieces = lap["pieces"]
    assert [piece["bar_id"] for piece in pieces] == [
        "B1-L",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B1-U",
    ]
    piece_extents = {
        "B1-L": (-1000, 1970),
        "B1-U": (1130, 4000),
        **{f"B{index}": (-1000, 4000) for index in range(2, 9)},
    }
    for piece in pieces:
        assert set(piece) == {
            "bar_id",
            "diameter_mm",
            "start_mm",
            "end_mm",
            "x_mm",
            "y_mm",
        }
        assert piece["diameter_mm"] == 20
        assert (piece["start_mm"], piece["end_mm"]) == piece_extents[piece["bar_id"]]
        x_mm, y_mm = expected["overlap_centres_from_column_centre_mm"][piece["bar_id"]]
        assert piece["x_mm"] == pytest.approx(x_mm, abs=_TOL["length_mm"])
        assert piece["y_mm"] == pytest.approx(y_mm, abs=_TOL["length_mm"])

    phases = calculation["strength_by_phase"]
    assert len(phases) == len(expected["strength_by_phase"])
    for actual, reference in zip(phases, expected["strength_by_phase"], strict=True):
        _assert_reference(actual, reference)
        assert actual["status"] == "PASS"
        for key in ("station_mm", "pu_kn", "mx_knm", "my_knm"):
            assert key in actual
    _assert_reference(calculation["governing_strength"], expected["governing_strength"])
    assert [
        (row["combination_id"], row["station_id"])
        for row in calculation["governing_strength"]
    ] == [
        ("U1", "MID"),
        ("U1", "B"),
    ]

    bbs = calculation["bbs"]
    assert bbs["quantity"] == expected["bbs"]["quantity"]
    assert bbs["total_length_mm"] == pytest.approx(expected["bbs"]["length_mm"])
    assert bbs["total_weight_kg"] == pytest.approx(
        expected["bbs"]["mass_kg"], rel=0, abs=_TOL["mass_kg"]
    )
    assert len(bbs["rows"]) == len(expected["bbs"]["rows_qty_cut_mm_diameter_mm"])
    for row in bbs["rows"]:
        quantity, cut_mm, diameter_mm = expected["bbs"]["rows_qty_cut_mm_diameter_mm"][
            row["bar_id"]
        ]
        assert (row["quantity"], row["cut_length_mm"], row["diameter_mm"]) == (
            quantity,
            cut_mm,
            diameter_mm,
        )


def _assert_pass_artifacts(
    drawing: str, schedule: str, expected: dict, input_hash: str
) -> None:
    svg = ElementTree.fromstring(drawing)
    assert svg.attrib["data-lap-id"] == "CL1"
    assert svg.attrib["data-ring-mark"] == "R1"
    lap_zone = svg.find(".//{*}rect[@class='lap-zone'][@data-lap-id='CL1']")
    assert lap_zone is not None
    assert [
        float(lap_zone.attrib[key]) for key in ("data-start-mm", "data-end-mm")
    ] == expected["overlap_bounds_mm"]
    rings = svg.findall(".//{*}line[@class='ring-station'][@data-mark='R1']")
    assert [float(ring.attrib["data-station-mm"]) for ring in rings] == expected[
        "ring_stations_mm"
    ]
    assert {
        piece.attrib["data-bar-id"]
        for piece in svg.findall(".//{*}line[@class='longitudinal-piece']")
    } >= {"B1-L", "B1-U"}
    assert [
        float(bracket.attrib["data-station-mm"])
        for bracket in svg.findall(
            ".//{*}line[@class='lap-bracket'][@data-lap-id='CL1']"
        )
    ] == expected["lap_end_bracket_stations_mm"]
    positions = svg.findall(".//{*}circle[@class='overlap-position']")
    assert len(positions) == 25
    assert [
        (row.attrib["data-combination-id"], row.attrib["data-station-id"])
        for row in svg.findall(".//{*}text[@class='strength-check']")
    ] == [("U1", "MID"), ("U1", "B")]
    for position in positions:
        bar_id = position.attrib["data-bar-id"]
        if bar_id in {"B1-L", "B1-U"}:
            x_mm, y_mm = expected["overlap_centres_from_column_centre_mm"][bar_id]
            assert float(position.attrib["data-x-mm"]) == pytest.approx(
                x_mm, abs=_TOL["length_mm"]
            )
            assert float(position.attrib["data-y-mm"]) == pytest.approx(
                y_mm, abs=_TOL["length_mm"]
            )
    rows = list(csv.DictReader(StringIO(schedule)))
    assert len(rows) == len(expected["bbs"]["rows_qty_cut_mm_diameter_mm"])
    assert all(row["input_hash"] == input_hash for row in rows)
    assert sum(int(row["quantity"]) for row in rows) == expected["bbs"]["quantity"]
    assert sum(float(row["total_length_mm"]) for row in rows) == pytest.approx(
        expected["bbs"]["length_mm"], abs=_TOL["length_mm"]
    )
    assert sum(float(row["total_weight_kg"]) for row in rows) == pytest.approx(
        expected["bbs"]["mass_kg"], abs=_TOL["mass_kg"]
    )
