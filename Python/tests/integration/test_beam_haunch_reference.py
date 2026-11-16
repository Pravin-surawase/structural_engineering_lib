"""Frozen BEAM05 variable-depth haunch acceptance reference."""

import csv
import hashlib
import html
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_lap_placement_reference import _assert_reference

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-haunch.json"
)
REFERENCE_SHA256 = "fe2b416d67f011d962e17f7baec55cd8abfd683e430f7d9d4a54098f813ba5ac"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]
HAUNCH_KEYS = (
    "rows",
    "bend_checks",
    "link_checks",
    "bottom_segments",
    "minimum_link_cover_mm",
    "bottom_bar_soffit_cover_bound_mm",
    "face_bar_clear_spacing_mm",
    "minimum_axial_opening_mm",
    "support_development_mm",
    "required_tension_development_mm",
)


def test_haunch_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_haunch_reference_replays_public_artifacts(name: str) -> None:
    """The frozen request is supplied unchanged to the public API."""
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

    if expected["status"] != "PASS":
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        if "row" in expected:
            row = next(
                row
                for row in result.calculation["haunch"]["rows"]
                if row["row_id"] == expected["row"]["row_id"]
            )
            _assert_reference(row, expected["row"])
        return

    assert drawing is not None and schedule is not None
    assert drawing in report
    _assert_haunch_result(result, report, drawing, schedule, expected)


def _assert_haunch_result(
    result, report: str, drawing: str, schedule: str, expected: dict
) -> None:
    calculation = result.calculation
    haunch = calculation["haunch"]
    assert haunch.keys() >= set(HAUNCH_KEYS)
    _assert_reference(
        haunch["bend_checks"],
        [
            {
                **row,
                "required_compression_development_mm": float(
                    row["required_compression_development_mm"]
                ),
            }
            for row in expected["bend_checks"]
        ],
    )
    _assert_reference(
        {key: haunch[key] for key in HAUNCH_KEYS if key != "bend_checks"},
        {key: expected[key] for key in HAUNCH_KEYS if key != "bend_checks"},
    )

    # The exact independent take-off remains the BBS authority; CSV is only
    # its public serialization and must retain the result identity.
    bbs = calculation["bbs"]["outputs"]["bbs"]
    actual_cuts = {
        row["bar_mark"]: [
            row["diameter_mm"],
            row["scheduled_bar_count"],
            row["fabrication_cut_length_each_mm"],
        ]
        for row in bbs["rows"]
    }
    assert actual_cuts.keys() == {row["bar_mark"] for row in expected["bbs"]["rows"]}
    for row in expected["bbs"]["rows"]:
        assert actual_cuts[row["bar_mark"]] == pytest.approx(
            [row["diameter_mm"], row["quantity"], row["cut_mm"]], abs=1e-8
        )
    assert bbs["scheduled_steel_mass_kg"] == pytest.approx(expected["bbs"]["mass_kg"])
    _assert_csv_rows(schedule, expected["bbs"]["rows"], result)
    _assert_drawing(drawing, expected, result)
    _assert_report(report, expected)


def _assert_csv_rows(schedule: str, expected_rows: list[dict], result) -> None:
    rows = list(csv.DictReader(StringIO(schedule)))
    assert len(rows) == len(expected_rows)
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    path_id = result.calculation["paths"]["result_id"]
    frozen_by_mark = {row["bar_mark"]: row for row in expected_rows}
    for actual in rows:
        expected = frozen_by_mark[actual["bar_mark"]]
        assert actual["bar_mark"] == expected["bar_mark"]
        assert float(actual["diameter_mm"]) == pytest.approx(expected["diameter_mm"])
        assert int(actual["quantity"]) == expected["quantity"]
        assert float(actual["cut_mm"]) == pytest.approx(expected["cut_mm"])
        assert actual["input_hash"] == identity.input_hash
        assert actual["path_result_id"] == path_id
    assert sum(int(row["quantity"]) for row in rows) == expected_quantity(expected_rows)


def expected_quantity(rows: list[dict]) -> int:
    return sum(row["quantity"] for row in rows)


def _assert_drawing(drawing: str, expected: dict, result) -> None:
    root = ElementTree.fromstring(drawing)
    elevation = root.findall(".//{*}svg[@data-view='haunch-elevation']")
    section = root.findall(".//{*}svg[@data-view='haunch-section']")
    assert len(elevation) == len(section) == 1
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    assert identity.input_hash in drawing
    assert result.calculation["paths"]["result_id"] in drawing

    bends = root.findall(".//*[@data-haunch-bend]")
    assert len(bends) == len(expected["bend_checks"])
    assert {bend.attrib["data-haunch-bend"] for bend in bends} == {
        row["node_id"] for row in expected["bend_checks"]
    }

    links = root.findall(".//*[@data-link-station]")
    assert len(links) == len(expected["link_checks"])
    assert [float(link.attrib["data-link-station"]) for link in links] == [
        row["station_mm"] for row in expected["link_checks"]
    ]


def _assert_report(report: str, expected: dict) -> None:
    # Signed correction values are audit data, not merely the absolute shear
    # demand used by the strength check.  The report must disclose both them
    # and the curved-bar/bend evidence.
    for row in expected["rows"]:
        if row["shear_adjustment_kn"]:
            assert row["row_id"] in report
            assert f"{row['shear_adjustment_kn']:.3f}" in report
    for bend in expected["bend_checks"]:
        assert bend["node_id"] in report
        assert f"{bend['demand_per_bar_kn']:.3f}" in report
        assert f"{bend['resistance_per_bar_kn']:.3f}" in report
