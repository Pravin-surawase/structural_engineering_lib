"""Replay the frozen FLOW03 placement, edit and artifact controls."""

import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import beam

REFERENCE = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-flow03-two-layer-edit.json"
)
SHA256 = "1258a69caa7de21eec0080451f6bb613179a038cae01676245fe70f09f43929b"
FIXTURE = json.loads(REFERENCE.read_text(encoding="utf-8"))
CASES = FIXTURE["cases"]
ISSUES = {
    "empty_corner": "BEAM.EDIT_CORNER_RESTRAINT",
    "congested": "BEAM.EDIT_SPACING",
    "short_form_opening": "BEAM.EDIT_FORM_OPENING",
    "missing_cross_tie": "BEAM.EDIT_INTERMEDIATE_RESTRAINT",
    "stale_analysis": "BEAM.EDIT_STALE_RESULT",
    "stiffness_dependent": "BEAM.EDIT_ANALYSIS_REFRESH_REQUIRED",
    "missing_placement": "BEAM.EDIT_PLACEMENT_HELD",
}
SVG = {"svg": "http://www.w3.org/2000/svg"}


def _request(case):
    raw = deepcopy(FIXTURE["base_request"])
    current = case.get("current_analysis_revision")
    if current is not None:
        raw["member"]["current_analysis_revision"] = current
    frozen_service = FIXTURE["base_expected"]["service"]
    raw["layered_cage"] = {
        "placement": case.get("placement", FIXTURE["placement"]),
        "cross_tie": case.get("cross_tie", FIXTURE["cross_tie"]),
        "service": {
            "analysis_revision": raw["member"]["analysis_revision"],
            "uniform_load_kn_per_m": frozen_service["unfactored_udl_kn_per_m_per_span"],
            "source_reference": frozen_service["source_reference"],
        },
    }
    return beam.load_continuous_detailing(raw)


def _matches(actual, expected):
    if isinstance(expected, dict):
        for key, value in expected.items():
            _matches(actual[key], value)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for entry, target in zip(actual, expected, strict=True):
            _matches(entry, target)
    elif type(expected) in (float, int):
        assert actual == pytest.approx(expected, rel=1e-9, abs=1e-9)
    else:
        assert actual == expected


def _verify_checks(result, expected):
    actual = result.to_dict()["calculation"]
    cage = actual["layered_cage"]
    nominal = actual["strength"]
    for field in (
        "placement",
        "end_anchorage",
        "service",
        "placement_limit_section_rechecks",
    ):
        _matches(cage[field], expected[field])
    assert (
        cage["service"]["reinforcement_revision"]
        == result.request.member.reinforcement_revision
    )
    assert (
        cage["service"]["analysis_revision"] == result.request.member.analysis_revision
    )
    target = expected["strength"]
    for field in ("governing_flexure_row_id", "governing_acceptance_shear_row_id"):
        assert cage[field] == target[field]
    for face, section in target["section_by_face"].items():
        flexure = nominal["flexural_sections"][face]["outputs"]
        shear = nominal["shear_sections"][face]["outputs"]
        _matches(
            flexure,
            {
                field: section[field]
                for field in (
                    "effective_depth_mm",
                    "capacity_knm",
                    "tension_steel_area_mm2",
                    "over_reinforced",
                )
                if field in section
            },
        )
        _matches(flexure["tension_steel_area_mm2"], section["tension_area_mm2"])
        _matches(
            flexure["equilibrium_neutral_axis_depth_mm"], section["neutral_axis_mm"]
        )
        _matches(shear["provided_capacity_kn"], section["shear_capacity_kn"])
        responses = flexure["bar_responses"]
        _matches(
            {item["bar_id"]: item["strain"] for item in responses},
            section["bar_strains"],
        )
        _matches(
            {item["bar_id"]: item["net_force_n"] for item in responses},
            section["bar_net_forces_n"],
        )
    rows = {row["action"]["row_id"]: row for row in nominal["rows"]}
    assert set(rows) == set(target["signed_rows"])
    for row_id, wanted in target["signed_rows"].items():
        row = rows[row_id]
        _matches(row["action"]["mu_knm"], wanted["moment_knm"])
        _matches(row["action"]["vu_kn"], wanted["shear_kn"])
        if wanted["moment_knm"] == 0:
            # A support centreline row has no physical tension face at zero
            # moment. The owner reports the smaller of the two shear capacities.
            assert row["diagnostic_only"] and row["tension_face"] is None
            assert row["flexure_utilization"] == 0
            shear_limit = min(
                check["shear_capacity_kn"]
                for check in target["section_by_face"].values()
            )
            _matches(row["shear_utilization"], abs(wanted["shear_kn"]) / shear_limit)
            continue
        for field in ("tension_face", "flexure_utilization", "shear_utilization"):
            _matches(row[field], wanted[field])
    assert rows[cage["governing_flexure_row_id"]]["diagnostic_only"]
    assert not rows[cage["governing_acceptance_shear_row_id"]]["diagnostic_only"]


def _verify_artifacts(result, expected):
    request = result.request
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)
    assert drawing is not None and schedule is not None
    report = beam.render_continuous_detailing_html(result, current=request)
    assert drawing in report
    assert request.member.reinforcement_revision in report
    assert request.member.analysis_revision in report
    assert "Governing signed flexure row <code>U2:B1" in report
    assert "Governing acceptance shear row <code>U2:BF1" in report
    assert "Concrete consolidation opening 63 mm" in report

    identity = result.envelope.result_identity.input_hash
    geometry = result.calculation["paths"]
    assert identity in report and identity in drawing
    assert geometry["result_id"] in drawing
    root = ElementTree.fromstring(drawing)
    circles = {
        node.attrib["data-bar-id"]: [
            float(node.attrib["cx"]),
            float(node.attrib["cy"]),
            2 * float(node.attrib["r"]),
            int(node.attrib["data-layer"]),
        ]
        for node in root.findall(".//svg:circle[@data-bar-id]", SVG)
    }
    target = expected["drawing"]
    assert circles == target["section_centres_and_diameters"]
    tie = root.find(".//svg:path[@data-outline='centre-cross-tie']", SVG)
    assert tie is not None and tie.attrib["d"].count("A18 18") == 2
    tie_mark = tie.attrib["data-bar-mark"]
    assert (
        float(tie.attrib["data-station-mm"])
        == target["centre_cross_tie_stations_mm"][0]
    )
    tie_elevation = root.findall(".//svg:line[@data-cross-tie]", SVG)
    assert all(item.attrib["data-cross-tie"] == tie_mark for item in tie_elevation)
    assert [float(item.attrib["x1"]) for item in tie_elevation] == target[
        "centre_cross_tie_stations_mm"
    ]
    web = root.find(".//svg:rect[@data-outline='web-link']", SVG)
    assert web is not None
    x, y, w, h = (float(web.attrib[key]) for key in ("x", "y", "width", "height"))
    assert [x, y, x + w, y + h] == target["outer_hoop_centreline_bounds_mm"]

    paths = geometry["outputs"]["reinforcement_schedule"]["paths"]
    long_paths = {
        path["bar_id"]: [
            path["segments"][0]["start"]["station_x_mm"],
            path["segments"][-1]["end"]["station_x_mm"],
        ]
        for path in paths
        if path["role"] != "transverse_link"
    }
    assert long_paths == target["bar_extents_mm"]
    cross_ties = [path for path in paths if path["bar_mark"] == tie_mark]
    assert [p["segments"][0]["start"]["station_x_mm"] for p in cross_ties] == target[
        "centre_cross_tie_stations_mm"
    ]
    segments = cross_ties[0]["segments"]

    def xy(point):
        return [point["section_x_from_left_mm"], point["section_y_from_top_mm"]]

    _matches(
        [xy(segments[0]["start"]), xy(segments[-1]["end"])],
        target["cross_tie_tail_points_mm"],
    )
    _matches(
        [xy(segments[2]["start"]), xy(segments[2]["end"])],
        target["cross_tie_tangent_points_mm"],
    )
    assert [
        segment["bend_angle_degrees"]
        for segment in segments
        if segment["kind"] == "bend_arc"
    ] == pytest.approx([135, 135])
    bbs = result.calculation["bbs"]["outputs"]["bbs"]
    assert bbs["detail_revision_id"] == request.member.reinforcement_revision
    assert bbs["schedule_result_id"] == geometry["result_id"]
    assert {zone["bar_mark"]: zone["stations_x_mm"] for zone in bbs["link_zones"]} == {
        tie_mark: target["centre_cross_tie_stations_mm"],
        f"{request.member.member_id}-L8": target["outer_hoop_stations_mm"],
    }
    marks = list(csv.DictReader(io.StringIO(schedule)))
    for row in marks:
        assert (
            row["input_hash"] == identity
            and row["path_result_id"] == geometry["result_id"]
        )
    _matches(
        {
            row["bar_mark"]: [
                int(row["quantity"]),
                float(row["cut_mm"]),
                float(row["diameter_mm"]),
            ]
            for row in marks
        },
        expected["bbs"]["rows_qty_cut_mm_diameter_mm"],
    )
    assert (
        sum(int(row["quantity"]) for row in marks) == expected["bbs"]["total_quantity"]
    )
    _matches(
        sum(float(row["mass_kg"]) for row in marks), expected["bbs"]["total_mass_kg"]
    )
    _matches(
        sum(float(row["total_mm"]) for row in marks), expected["bbs"]["total_length_mm"]
    )


def test_two_layer_edit_and_outputs_match_frozen_cage():
    assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest() == SHA256
    base_request = _request({})
    base = beam.check_continuous_detailing(base_request)
    assert base.engineering_status.value == "PASS"
    _verify_checks(base, FIXTURE["base_expected"])
    _verify_artifacts(base, FIXTURE["base_expected"])
    case = CASES["edited"]
    result = beam.recheck_continuous_bar_edit(
        base_request,
        base,
        beam.BeamBarEditV1.model_validate(case["edit"]),
        analysis_basis=case["analysis_basis"],
    )
    assert result.engineering_status.value == case["expected"]["status"]
    _verify_checks(result, case["expected"])
    _verify_artifacts(result, case["expected"])
    assert (
        result.request.member.reinforcement_revision
        != base_request.member.reinforcement_revision
    )
    assert result.request.member.actions == base_request.member.actions
    assert (
        beam.render_continuous_detailing_bbs_csv(base, current=result.request) is None
    )
    assert beam.render_continuous_detailing_svg(base, current=result.request) is None
    assert (
        beam.render_continuous_detailing_bbs_csv(result, current=base_request) is None
    )
    assert "HOLD · stale result" in beam.render_continuous_detailing_html(
        base, current=result.request
    )


@pytest.mark.parametrize("name", ISSUES)
def test_two_layer_edit_controls_withhold_checked_artifacts(name):
    case = CASES[name]
    current = _request(case)
    base = _request({}) if name == "stale_analysis" else current
    previous = beam.check_continuous_detailing(base)
    result = beam.recheck_continuous_bar_edit(
        current,
        previous,
        beam.BeamBarEditV1.model_validate(case["edit"]),
        analysis_basis=case["analysis_basis"],
    )
    assert result.engineering_status.value == case["expected"]["status"]
    assert ISSUES[name] in {issue.code for issue in result.issues}
    assert beam.render_continuous_detailing_svg(result, current=result.request) is None
    assert (
        beam.render_continuous_detailing_bbs_csv(result, current=result.request) is None
    )
    report = beam.render_continuous_detailing_html(result, current=result.request)
    assert "BBS held." in report and "<svg" not in report.lower()
    if name == "empty_corner":
        placement = result.calculation["layered_cage"]["placement"]
        assert not placement["outer_corner_checks"]["T1-1"]["seated_through_tolerance"]
        assert min(placement["worst_horizontal_clearance_mm"]["top-1"]) == 35
    if name == "congested":
        placement = result.calculation["layered_cage"]["placement"]
        assert min(placement["worst_horizontal_clearance_mm"]["bottom-2"]) == 10
