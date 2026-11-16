"""Frozen BEAM05 T-beam separated-lap acceptance reference."""

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
    / "docs/verification/library-030-beam05-t-lap-reference.json"
)
REFERENCE_SHA256 = "aa42d95069449f3df30edd60cb715896b9faa89cf2ed5f55b4d2ed54c58bc011"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]
TOLERANCES = REFERENCE["absolute_tolerances"]


def _approx(expected: float, kind: str):
    return pytest.approx(expected, abs=TOLERANCES[kind])


def _row_id(row: dict) -> str:
    return row["action"]["row_id"]


def _anchor_summary(row: dict) -> dict:
    outputs = row["anchorage"]["outputs"]
    checks = outputs["checks"]
    return {
        "support_id": row["anchorage"]["effective_inputs"]["request"]["value"]["paths"][
            0
        ]["support_id"],
        "direction": row["anchorage"]["effective_inputs"]["request"]["value"]["paths"][
            0
        ]["direction"],
        "straight_available_mm": checks[0]["available_straight_length_mm"],
        "development_required_mm": checks[0]["required_development_length_mm"],
        "checked_bar_ids": [check["bar_id"] for check in checks],
    }


def test_t_lap_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_t_lap_reference(name: str) -> None:
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(case["request"])
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"]
    assert {issue.code for issue in result.issues} >= set(
        expected["required_issue_codes"]
    )
    assert (drawing is not None) is expected["checked_drawing_available"]
    assert (schedule is not None) is expected["bbs_available"]
    if expected["status"] != "PASS":
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        return

    assert drawing is not None and schedule is not None
    lap = result.calculation["lap"]
    (splice,) = lap["lap_result"]["outputs"]["splice_checks"]
    assert splice["actual_length_mm"] == _approx(expected["overlap_mm"], "length_mm")
    assert splice["required_length_mm"] == _approx(
        expected["required_lap_mm"], "length_mm"
    )
    assert result.envelope.result_identity.input_hash in report
    assert request.member.analysis_revision in report
    assert request.member.reinforcement_revision in report
    assert drawing in report
    assert "Clear distance between lap pieces 27.5 mm" in report
    assert "Overlap from 1550 to 2850 mm" in report
    for check, governor in expected["governing_acceptance_rows"].items():
        assert f"{check} · {governor['row_id']}" in report
    if name == "t_lap":
        interval = expected["lap_interval_by_combination"]["U2"]
        assert (
            f"Effective sagging flange width {expected['effective_flange_width_mm']:g} mm"
            in report
        )
        assert (
            f"Governing lap moment U2:LAP-START · {interval['maximum_moment_knm']:.3f} kN·m "
            f"against {interval['half_capacity_knm']:.3f} kN·m." in report
        )
        assert (
            "Web-only moment resistance for positive support anchorage 296.852 kN·m"
            in report
        )

    _assert_rows_and_capacities(result.calculation, expected)
    _assert_sections_and_bbs(
        drawing,
        schedule,
        expected,
        result.envelope.result_identity.input_hash,
        result.calculation["paths"]["result_id"],
    )


def _assert_rows_and_capacities(calculation: dict, expected: dict) -> None:
    strength = calculation["strength"]
    lap = calculation["lap"]

    overlap = {row["row_id"]: row for row in lap["stress_rows"]}
    assert overlap.keys() == expected["overlap_rows"].keys()
    for row_id, reference in expected["overlap_rows"].items():
        assert overlap[row_id]["moment_knm"] == _approx(
            reference["moment_knm"], "moment_knm"
        )
        assert overlap[row_id]["shear_kn"] == _approx(reference["shear_kn"], "force_kn")
        assert overlap[row_id]["half_capacity_knm"] == _approx(
            reference["half_capacity_knm"], "moment_knm"
        )

    primary = {_row_id(row): row for row in strength["rows"]}
    partner = {_row_id(row): row for row in lap["partner_rows"]}
    for reference in expected["signed_rows"]:
        actual = (
            primary[reference["row_id"]]
            if reference["layout"] == "upstream"
            else partner[reference["row_id"]]
        )
        assert actual["station"]["x_mm"] == _approx(
            reference["station_mm"], "length_mm"
        )
        assert actual["tension_face"] == reference["tension_face"]
        assert actual["diagnostic_only"] is reference["diagnostic_only"]
        assert actual["action"]["mu_knm"] == _approx(
            reference["moment_knm"], "moment_knm"
        )
        assert actual["action"]["vu_kn"] == _approx(reference["shear_kn"], "force_kn")
        assert actual["flexure_utilization"] == _approx(
            reference["flexure_utilization"], "ratio"
        )
        assert actual["shear_utilization"] == _approx(
            reference["shear_utilization"], "ratio"
        )

    assert strength["governing_rows"] == {
        kind: reference["row_id"]
        for kind, reference in expected["governing_acceptance_rows"].items()
    }
    for face in ("bottom", "top"):
        reference = expected["strength_by_layout"]["upstream"][face]
        flexure = strength["flexural_sections"][face]["outputs"]
        shear = strength["shear_sections"][face]["outputs"]
        assert flexure["capacity_knm"] == _approx(
            reference["capacity_knm"], "moment_knm"
        )
        assert flexure["effective_depth_mm"] == _approx(
            reference["effective_depth_mm"], "length_mm"
        )
        assert (
            flexure["uses_compression_flange"] is reference["uses_compression_flange"]
        )
        assert shear["provided_capacity_kn"] == _approx(
            reference["shear_capacity_kn"], "force_kn"
        )

    anchors = {
        _row_id(row): _anchor_summary(row)
        for row in [*strength["rows"], *lap["partner_rows"]]
        if row["anchorage"] is not None
    }
    for row_id, reference in expected["support_anchorage"].items():
        actual = anchors[row_id]
        assert actual["support_id"] == reference["support_id"]
        assert actual["direction"] == reference["direction"]
        assert actual["straight_available_mm"] == _approx(
            reference["straight_available_mm"], "length_mm"
        )
        assert actual["development_required_mm"] == _approx(
            reference["development_required_mm"], "length_mm"
        )
        assert set(actual["checked_bar_ids"]) == set(reference["checked_bar_ids"])
        if "positive_support" in reference:
            source = (
                partner[row_id]
                if "B1-3-partner" in reference["positive_support"]["bottom_bar_ids"]
                else primary[row_id]
            )
            positive = source["positive_support_anchorage"]["outputs"]["checks"]
            assert {check["bar_id"] for check in positive} == set(
                reference["positive_support"]["bottom_bar_ids"]
            )
            for check in positive:
                assert check["anchorage_beyond_support_centre_mm"] == _approx(
                    reference["positive_support"]["extension_beyond_centre_mm"],
                    "length_mm",
                )
                assert check["available_for_criterion_mm"] == _approx(
                    reference["positive_support"]["available_mm"], "length_mm"
                )
                assert (
                    check["moment_shear_contribution_mm"]
                    + check["anchorage_beyond_support_centre_mm"]
                ) == _approx(
                    reference["positive_support"]["m_over_v_plus_extension_mm"],
                    "length_mm",
                )
    if expected["effective_flange_width_mm"] is not None:
        assert lap["web_only_anchor_moment_knm"] == _approx(
            expected["strength_by_layout"]["upstream"]["bottom_web"]["capacity_knm"],
            "moment_knm",
        )


def _assert_sections_and_bbs(
    drawing: str, schedule: str, expected: dict, input_hash: str, path_id: str
) -> None:
    assert input_hash in drawing and path_id in drawing
    root = ElementTree.fromstring(drawing)
    lines = {
        line.attrib["data-bar-id"]: line.attrib for line in root.findall(".//{*}line")
    }
    extents = expected["drawing"]["bar_extents_mm"]
    for bar_id, (start, end) in extents.items():
        assert float(lines[bar_id]["x1"]) == _approx(start, "length_mm")
        assert float(lines[bar_id]["x2"]) == _approx(end, "length_mm")
    assert (
        sorted(float(lines[mark]["x1"]) for mark in lines.keys() - extents.keys())
        == expected["drawing"]["link_stations_mm"]
    )

    panels = root.findall("{*}svg[@data-view='section']")
    assert len(panels) == 3
    phases = ("before", "overlap", "after")
    for panel, phase in zip(panels, phases, strict=True):
        outline = panel.find("{*}path[@data-outline='concrete']")
        assert outline is not None
        left_top, right_top, *outline_rest = expected["drawing"]["section_outline_mm"]
        path = [f"M{left_top[0]:g} {left_top[1]:g}", f"H{right_top[0]:g}"]
        previous_x, _ = right_top
        for x, y in outline_rest:
            path.append(f"V{y:g}" if x == previous_x else f"H{x:g}")
            previous_x = x
        assert outline.attrib["d"] == " ".join([*path, "Z"])
        link = panel.find("{*}rect[@data-outline='web-link']")
        assert link is not None
        left, top, right, bottom = expected["drawing"]["web_link_centreline_bounds_mm"]
        assert (
            float(link.attrib["x"]),
            float(link.attrib["y"]),
            float(link.attrib["x"]) + float(link.attrib["width"]),
            float(link.attrib["y"]) + float(link.attrib["height"]),
        ) == pytest.approx(
            (left, top, right, bottom),
            abs=TOLERANCES["length_mm"],
        )
        points = {
            point.attrib["data-bar-id"]: point.attrib
            for point in panel.findall("{*}circle")
        }
        centres = expected["drawing"]["section_centres"][phase]
        assert points.keys() == centres.keys()
        for bar_id, (x, y, layer) in centres.items():
            assert float(points[bar_id]["cx"]) == _approx(x, "length_mm")
            assert float(points[bar_id]["cy"]) == _approx(y, "length_mm")
            assert int(points[bar_id]["data-layer"]) == layer

    rows = {row["bar_mark"]: row for row in csv.DictReader(StringIO(schedule))}
    assert all(
        row["input_hash"] == input_hash and row["path_result_id"] == path_id
        for row in rows.values()
    )
    assert rows.keys() == expected["bbs"]["rows_qty_cut_mm_diameter_mm"].keys()
    for mark, (quantity, cut_mm, diameter_mm) in expected["bbs"][
        "rows_qty_cut_mm_diameter_mm"
    ].items():
        assert int(rows[mark]["quantity"]) == quantity
        assert float(rows[mark]["cut_mm"]) == _approx(cut_mm, "length_mm")
        assert float(rows[mark]["diameter_mm"]) == _approx(diameter_mm, "length_mm")
    assert (
        sum(int(row["quantity"]) for row in rows.values())
        == expected["bbs"]["total_quantity"]
    )
    assert sum(
        float(row["cut_mm"]) * int(row["quantity"]) for row in rows.values()
    ) == _approx(expected["bbs"]["total_length_mm"], "length_mm")
    assert sum(float(row["mass_kg"]) for row in rows.values()) == _approx(
        expected["bbs"]["total_mass_kg"], "mass_kg"
    )
