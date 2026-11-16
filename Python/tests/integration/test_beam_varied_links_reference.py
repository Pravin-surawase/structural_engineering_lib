"""Acceptance replay for frozen BEAM05 varied-link-zone cases."""

import csv
import hashlib
import html
import json
from copy import deepcopy
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_lap_placement_reference import _assert_reference

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-varied-links.json"
)
REFERENCE_SHA256 = "e7265425ad6b50e09dfdd12d44c59f3b2d447b32a6bd99076b63bf7356f04787"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]


def test_varied_links_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_varied_links_reference_replays_public_artifacts(name: str) -> None:
    """The frozen request is the product contract, not test-built input."""
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(case["request"])
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"]
    assert {issue.code for issue in result.issues} >= set(
        expected.get("required_issue_codes", [])
    )

    # Uniform requests deliberately retain their historical single-link workflow.
    if name == "uniform":
        assert "link_zones" not in result.calculation
        _assert_legacy_uniform_row(result.calculation, expected)

    # New zone evidence must survive both qualified production and a strength FAIL.
    if name in {"varied", "dense_required", "right_transition_overload"}:
        link_zones = result.calculation["link_zones"]
        assert link_zones["maximum_pitch_mm"] == REFERENCE["maximum_pitch_mm"]
        if "zones" in expected:
            _assert_reference(link_zones["zones"], expected["zones"])
        _assert_reference(link_zones["transitions"], expected["transitions"])

    if expected["status"] != "PASS":
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        return

    assert drawing is not None and schedule is not None
    assert drawing in report
    _assert_public_artifacts(result, report, drawing, schedule, expected)


def test_varied_zones_require_support_face_rows_in_every_uls_combination() -> None:
    request_data = deepcopy(CASES["dense_required"]["request"])
    member = request_data["member"]
    member["combinations"][1]["required_station_ids"].remove("B-LEFT-FACE")
    member["actions"] = [
        action for action in member["actions"] if action["row_id"] != "U2:B-LEFT-FACE"
    ]
    result = beam.check_continuous_detailing(
        beam.load_continuous_detailing(request_data)
    )
    assert result.engineering_status.value == "HOLD"
    assert "BEAM_MEMBER_COVERAGE_MISSING" in {issue.code for issue in result.issues}
    assert beam.render_continuous_detailing_svg(result) is None
    assert beam.render_continuous_detailing_bbs_csv(result) is None


def _assert_legacy_uniform_row(calculation: dict, expected: dict) -> None:
    """Pin the legacy single row to strength shear and BBS, without new zones."""
    (reference,) = expected["zones"]
    strength_rows = {
        row["action"]["row_id"]: row for row in calculation["strength"]["rows"]
    }
    strength_row = strength_rows[reference["governing_row_id"]]
    assert strength_row["action"]["vu_kn"] == pytest.approx(
        reference["governing_shear_kn"]
    )
    bbs = calculation["bbs"]["outputs"]["bbs"]
    (link_zone,) = bbs["link_zones"]
    assert link_zone["count"] == reference["quantity"]
    assert link_zone["stations_x_mm"] == reference["stations_mm"]


def _assert_public_artifacts(
    result, report: str, drawing: str, schedule: str, expected: dict
) -> None:
    calculation = result.calculation
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    path_id = calculation["paths"]["result_id"]
    assert identity.input_hash in drawing and path_id in drawing

    bbs = calculation["bbs"]["outputs"]["bbs"]
    _assert_bbs_link_zones(bbs, expected["zones"])
    _assert_schedule(schedule, expected["bbs"], identity.input_hash, path_id)
    _assert_elevation_and_section(
        drawing, expected["drawing"], calculation.get("link_zones")
    )
    paths = calculation["paths"]["outputs"]["reinforcement_schedule"]["paths"]
    for path in paths:
        if path["role"] in ("top_longitudinal", "bottom_longitudinal"):
            p = path["segments"][0]["start"]
            assert [
                p["section_x_from_left_mm"],
                p["section_y_from_top_mm"],
            ] == pytest.approx(expected["drawing"]["bar_axes_mm"][path["bar_id"]])

    for zone in expected["zones"]:
        assert zone["governing_row_id"] in report
    for transition in expected["transitions"]:
        assert transition["row_id"] in report


def _assert_bbs_link_zones(bbs: dict, expected_zones: list[dict]) -> None:
    actual = {zone["zone_id"]: zone for zone in bbs["link_zones"]}
    if len(expected_zones) == 1 and "UNIFORM" not in actual:
        # The historical row remains named for its span rather than its test zone.
        assert len(actual) == 1
        actual = {expected_zones[0]["zone_id"]: next(iter(actual.values()))}
    assert actual.keys() == {zone["zone_id"] for zone in expected_zones}
    for zone in expected_zones:
        row = actual[zone["zone_id"]]
        assert row["count"] == zone["quantity"]
        assert row["stations_x_mm"] == zone["stations_mm"]


def _assert_schedule(
    schedule: str, expected: dict, input_hash: str, path_id: str
) -> None:
    rows = list(csv.DictReader(StringIO(schedule)))
    assert all(
        row["input_hash"] == input_hash and row["path_result_id"] == path_id
        for row in rows
    )
    links = [row for row in rows if row["role"] == "transverse_link"]
    assert sum(int(row["quantity"]) for row in links) == expected["link_count"]
    assert all(
        float(row["cut_mm"]) == pytest.approx(expected["link_cut_mm"]) for row in links
    )
    longitudinal = [row for row in rows if row["role"] != "transverse_link"]
    assert (
        sum(int(row["quantity"]) for row in longitudinal)
        == expected["longitudinal_count"]
    )
    assert all(
        float(row["cut_mm"]) == pytest.approx(expected["longitudinal_cut_mm"])
        for row in longitudinal
    )
    assert sum(float(row["mass_kg"]) for row in rows) == pytest.approx(
        expected["mass_kg"]
    )


def _assert_elevation_and_section(
    drawing: str, expected: dict, zones: dict | None
) -> None:
    root = ElementTree.fromstring(drawing)
    lines = root.findall(".//{*}line")
    projected_links = [
        line
        for line in lines
        if line.attrib.get("x1") == line.attrib.get("x2")
        and "data-bar-id" in line.attrib
    ]
    assert [float(line.attrib["x1"]) for line in projected_links] == expected[
        "link_stations_mm"
    ]

    if zones is None:
        return
    labels = root.findall(".//{*}g[@data-link-zone]")
    for label, zone in zip(labels, zones["zones"], strict=True):
        assert label.attrib["data-link-zone"] == zone["zone_id"]
        assert float(label.attrib["data-spacing-mm"]) == zone["spacing_mm"]
        assert label.attrib["data-start"] == (
            "inclusive" if zone["include_start"] else "exclusive"
        )
        assert label.attrib["data-end"] == (
            "inclusive" if zone["include_end"] else "exclusive"
        )
    (panel,) = root.findall(".//{*}svg[@data-view='section']")
    axes = {
        point.attrib["data-bar-id"]: (
            float(point.attrib["cx"]),
            float(point.attrib["cy"]),
        )
        for point in panel.findall("{*}circle")
    }
    assert axes.keys() == expected["bar_axes_mm"].keys()
    for bar_id, coordinates in axes.items():
        assert coordinates == pytest.approx(expected["bar_axes_mm"][bar_id])
