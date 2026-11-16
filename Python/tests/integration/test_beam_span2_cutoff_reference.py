"""Acceptance replay for the frozen reverse-direction span-two cutoff cases."""

import csv
import hashlib
import html
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import beam

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-span2-cutoff-reference.json"
)
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
TOLERANCES = REFERENCE["absolute_tolerances"]


def test_span_two_cutoff_reference_is_frozen():
    assert (
        hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest()
        == "b6e97bf62ff4c37ee95fee95acd5e8c9fe76832a2ffb26ea5138091dfe9d766d"
    )


@pytest.mark.parametrize("name", REFERENCE["cases"])
def test_span_two_cutoff_reference_replays_public_artifacts(name):
    """Keep the second-span reverse cutoff and its withholding gates stable."""
    case = REFERENCE["cases"][name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(case["request"])
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status == expected["status"]
    assert report is not None
    assert {issue.code for issue in result.issues} >= set(
        expected.get("required_issue_codes", [])
    )

    if name == "first_span_control":
        # This predecessor case is deliberately retained as an unchanged control.
        assert drawing is not None and schedule is not None
        cutoff = result.calculation["cutoff"]
        assert "cutoff_direction" not in cutoff
        assert cutoff["theoretical_station_mm"] == pytest.approx(2500)
        assert cutoff["termination_station_mm"] == pytest.approx(3500)
        assert float(
            next(
                row
                for row in csv.DictReader(StringIO(schedule))
                if row["bar_mark"].endswith("-cutoff")
            )["cut_mm"]
        ) == pytest.approx(expected["cut_mm"])
        return

    if expected["status"] != "PASS":
        assert drawing is schedule is result.calculation["bbs"] is None
        assert "BBS held." in report and "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        if expected["status"] == "FAIL":
            cutoff = result.calculation["cutoff"]
            assert cutoff["cutoff_direction"] == "decreasing_x"
            assert cutoff["termination_station_mm"] == pytest.approx(
                expected["termination_station_mm"]
            )
            assert cutoff["actual_extension_mm"] == pytest.approx(
                expected["available_extension_mm"]
            )
            path = cutoff["anchorage"]["effective_inputs"]["request"]["value"]["paths"][
                0
            ]
            assert path["direction"] == "decreasing_x"
            assert (path["path_start_x_mm"], path["path_end_x_mm"]) == pytest.approx(
                expected["physical_cut_bar_extent_mm"]
            )
        else:
            issue_paths = {issue.path for issue in result.issues}
            if expected["missing_required_rows"]:
                assert issue_paths >= {
                    f"combinations.{row_id.replace(':', '.')}"
                    for row_id in expected["missing_required_rows"]
                }
            else:
                assert "analysis_revision" in issue_paths
        return

    cutoff = result.calculation["cutoff"]
    assert cutoff["cutoff_direction"] == expected["cutoff_direction"] == "decreasing_x"
    assert cutoff["theoretical_station_mm"] == pytest.approx(
        expected["theoretical_station_mm"]
    )
    assert cutoff["termination_station_mm"] == pytest.approx(
        expected["termination_station_mm"]
    )
    assert cutoff["actual_extension_mm"] == pytest.approx(
        expected["available_extension_mm"]
    )
    assert cutoff["required_extension_mm"] == pytest.approx(
        expected["required_extension_mm"]
    )
    assert cutoff["termination_shear_limit_kn"] == pytest.approx(
        expected["termination_limit_kn"]
    )
    assert cutoff["continuing_bar_ids"] == expected["continuing_bar_ids"]

    (development,) = cutoff["anchorage"]["outputs"]["checks"]
    path = cutoff["anchorage"]["effective_inputs"]["request"]["value"]["paths"][0]
    assert development["required_development_length_mm"] == pytest.approx(
        expected["development_mm"]
    )
    assert path["direction"] == "decreasing_x"
    assert (path["path_start_x_mm"], path["path_end_x_mm"]) == pytest.approx(
        expected["physical_cut_bar_extent_mm"]
    )

    governor = expected["governing_termination_shear"]
    termination_rows = {row["row_id"]: row for row in cutoff["termination_rows"]}
    assert termination_rows[governor["row_id"]]["shear_kn"] == pytest.approx(
        governor["shear_kn"]
    )
    assert all(row["passes_two_thirds"] for row in termination_rows.values())
    assert f"{governor['row_id']} · {governor['shear_kn']:g} kN · PASS" in report
    assert f"Termination shear limit {governor['limit_kn']:.3f} kN." in report
    assert (
        f"Development from {expected['theoretical_station_mm']:g} mm toward decreasing x."
        in report
    )
    assert (
        f"Required straight development {expected['development_mm']:.3f} mm." in report
    )

    rows = {row["action"]["row_id"]: row for row in cutoff["reduced_section_rows"]}
    assert rows.keys() == expected["reduced_rows"].keys()
    for row_id, reference in expected["reduced_rows"].items():
        row = rows[row_id]
        assert row["action"]["mu_knm"] == pytest.approx(reference["moment_knm"])
        assert row["action"]["vu_kn"] == pytest.approx(reference["shear_kn"])
        assert row["station"]["x_mm"] == pytest.approx(reference["station_mm"])
        assert row["diagnostic_only"] is reference["diagnostic_only"]
        assert row["flexure_utilization"] == pytest.approx(
            reference["flexure_utilization"], abs=TOLERANCES["ratio"]
        )
        assert row["shear_utilization"] == pytest.approx(reference["shear_utilization"])

    assert drawing is not None and schedule is not None
    input_hash = result.envelope.result_identity.input_hash
    path_id = result.calculation["paths"]["result_id"]
    assert input_hash in drawing and path_id in drawing and drawing in report
    root = ElementTree.fromstring(drawing)
    theoretical, termination = root.findall("{*}svg[@data-view='section']")
    assert float(theoretical.attrib["data-station-mm"]) == pytest.approx(5500)
    assert float(termination.attrib["data-station-mm"]) == pytest.approx(4500)
    cut_bar_id = request.cutoff.bar_id
    theoretical_bars = {
        point.attrib["data-bar-id"] for point in theoretical.findall("{*}circle")
    }
    termination_bars = {
        point.attrib["data-bar-id"] for point in termination.findall("{*}circle")
    }
    assert cut_bar_id in theoretical_bars
    assert cut_bar_id not in termination_bars
    line = root.find(f".//{{*}}line[@data-bar-id='{cut_bar_id}']")
    assert line is not None
    assert sorted(
        (float(line.attrib["x1"]), float(line.attrib["x2"]))
    ) == pytest.approx(expected["physical_cut_bar_extent_mm"])

    table = list(csv.DictReader(StringIO(schedule)))
    assert all(
        row["input_hash"] == input_hash and row["path_result_id"] == path_id
        for row in table
    )
    (link,) = (row for row in table if row["role"] == "transverse_link")
    assert int(link["quantity"]) == expected["link_count"]
    assert float(link["cut_mm"]) == pytest.approx(
        expected["link_cut_mm"], abs=TOLERANCES["length_mm"]
    )
    bar_rows = {row["bar_mark"]: row for row in table if row is not link}
    assert bar_rows.keys() == expected["marks"].keys()
    for mark, quantity in expected["marks"].items():
        assert int(bar_rows[mark]["quantity"]) == quantity
        length_key = "cut_mm" if mark.endswith("-cutoff") else "full_cut_mm"
        assert float(bar_rows[mark]["cut_mm"]) == pytest.approx(
            expected[length_key], abs=TOLERANCES["length_mm"]
        )
    assert sum(float(row["mass_kg"]) for row in table) == pytest.approx(
        expected["mass_kg"], abs=TOLERANCES["mass_kg"]
    )
