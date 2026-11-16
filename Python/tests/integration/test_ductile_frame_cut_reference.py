"""Compare the public PROJECT03 frame cut to the independent frozen reference."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is13920 import frame

VERIFY = Path(__file__).parents[3] / "docs/verification"
FIXTURE = VERIFY / "library-030-project03-ductile-frame.json"
ACTIONS = VERIFY / "library-030-project03-frame-actions.json"

CONTROLS = (
    "column_boundary_biaxial_overload",
    "missing_boundary_leg",
    "missing_required_direction_row",
    "same_steel_mismatched_axes",
    "short_exterior_bottom_tail",
    "stale_project_revision",
    "unbalanced_beam_at_j2",
)


def _source() -> dict:
    return json.loads(ACTIONS.read_bytes())


def _fixture() -> dict:
    return json.loads(FIXTURE.read_bytes())


def _compare(actual, expected, path="calculation"):
    if isinstance(expected, dict):
        for name, value in expected.items():
            _compare(actual[name], value, f"{path}.{name}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, (row, value) in enumerate(zip(actual, expected, strict=True)):
            _compare(row, value, f"{path}[{index}]")
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        assert math.isclose(actual, expected, abs_tol=1e-6, rel_tol=1e-8), path
    else:
        assert actual == expected, path


def test_public_frame_reproduces_frozen_mechanics_and_signed_inventory():
    document = _fixture()
    assert (
        hashlib.sha256(ACTIONS.read_bytes()).hexdigest()
        == document["source_packet"]["sha256"]
    )
    request = frame.load_frame(ACTIONS.read_bytes())
    result = frame.check_frame(request)
    assert result.status == "PASS"
    _compare(result.calculation, document["expected"])
    assert result.to_dict()["workflow_id"] == "PROJECT03_DUCTILE_FRAME_CUT"
    assert (
        result.calculation["site_insertion_status"]
        == "REQUIRES_CONSTRUCTION_SEQUENCE_EVIDENCE"
    )
    assert set(result.calculation["joint_input_hashes"]) == {"J1", "J2"}
    assert result.request.action_revision == "PROJECT03-CUT-R1"

    for direction, names in request.required_combinations.items():
        for index, combination in enumerate(names):
            mapped = result.calculation["joint_action_requests"]
            for joint in ("J1", "J2"):
                actions = mapped[joint]["directions"][direction][index]
                assert actions["combination_id"] == combination
                assert actions["orthogonal_downward_reaction_kn"] > 0
                columns = request.actions[combination].columns
                above = columns[f"C-{joint}-upper"].near_face.force_kn[2]
                below = -columns[f"C-{joint}-lower"].near_face.force_kn[2]
                assert below == pytest.approx(
                    above
                    + sum(actions["beam_on_joint_downward_shear_kn"].values())
                    + actions["orthogonal_downward_reaction_kn"]
                )


def test_frame_exports_share_cut_marks_and_explicit_current_identity():
    request = frame.load_frame(ACTIONS.read_bytes())
    result = frame.check_frame(request)
    metadata = _fixture()["expected"]["artifact_reconciliation"]
    assert frame.render_frame_svg(result) is None
    assert frame.render_frame_bbs_csv(result) is None
    current = request.model_copy(
        update={"applicability_reference": "Reviewed applicability on another source."}
    )
    assert frame.render_frame_svg(result, current=current) is None
    assert frame.render_frame_bbs_csv(result, current=current) is None

    svg = frame.render_frame_svg(result, current=request)
    bbs = frame.render_frame_bbs_csv(result, current=request)
    report = frame.render_frame_html(result)
    assert svg and bbs
    assert "817 resolved cuts" in report and "46.39 mm" in report
    assert all(str(id_) in report for id_ in request.actions)
    assert result.input_hash in report and result.input_hash in svg

    root = ElementTree.fromstring(svg)
    nodes = list(root.iter())
    bar_meta = {
        node.attrib["data-bar-id"]: node.attrib
        for node in nodes
        if "data-bar-id" in node.attrib
    }
    assert set(bar_meta) == set(metadata["shared_longitudinal_sources"])
    assert len([node for node in nodes if "data-section-bar" in node.attrib]) == 8
    assert {
        node.attrib["data-section-mark"]
        for node in nodes
        if "data-section-mark" in node.attrib
    } == {"BX12-M", "BX12-O"}
    for name, paths in metadata["shared_longitudinal_sources"].items():
        assert [
            bar_meta[name]["data-interior-path"],
            bar_meta[name]["data-exterior-path"],
        ] == paths
    tie_meta = {
        node.attrib["data-mark"]: [
            float(child.attrib["data-station-mm"])
            for child in node
            if "data-station-mm" in child.attrib
        ]
        for node in nodes
        if "data-mark" in node.attrib
    }

    rows = list(csv.DictReader(io.StringIO(bbs)))
    actual = {row["bar_mark"]: row for row in rows}
    assert len(actual) == len(rows) == 22
    assert set(actual) == set(metadata["checked_tie_and_beam_cut_marks"])
    assert sum(int(row["quantity"]) for row in rows) == 817
    assert sum(float(row["total_mass_kg"]) for row in rows) == pytest.approx(
        metadata["cut_weight_kg"]
    )
    for name, frozen in metadata["checked_tie_and_beam_cut_marks"].items():
        row = actual[name]
        assert row["scope"] == "DESIGN_REVIEW"
        assert row["action_revision"] == request.action_revision
        assert row["input_hash"] == result.input_hash
        assert int(row["quantity"]) == frozen["quantity"]
        assert float(row["cut_length_mm"]) == pytest.approx(frozen["cut_mm"])
        if "stations_mm" in frozen:
            assert tie_meta[name] == frozen["stations_mm"]
            assert list(map(float, row["stations_mm"].split())) == frozen["stations_mm"]
        else:
            assert row["bar_ids"].split() == frozen["bar_ids"]
            for ident in frozen["bar_ids"]:
                assert float(bar_meta[ident]["data-cut-mm"]) == pytest.approx(
                    frozen["cut_mm"]
                )


@pytest.mark.parametrize("name", CONTROLS)
def test_frozen_refusals_withhold_both_checked_exports(name):
    data = _source()
    control = _fixture()["controls"][name]
    parent = data
    for token in control["path"][:-1]:
        parent = parent[token]
    if control["operation"] == "delete":
        del parent[control["path"][-1]]
    else:
        parent[control["path"][-1]] = control["value"]
    request = frame.load_frame(data)
    result = frame.check_frame(request)
    expected = control["expected"]
    assert result.status == expected["status"]
    _compare(
        result.calculation,
        {
            key: value
            for key, value in expected.items()
            if key != "failed_column_boundaries"
        },
    )
    if "failed_column_boundaries" in expected:
        failed = {
            member: row["governing_flexure"]
            for member, row in result.calculation["column_legs"].items()
            if not row["pass"]
        }
        assert set(failed) == set(expected["failed_column_boundaries"])
        _compare(failed, expected["failed_column_boundaries"])
    assert frame.render_frame_svg(result, current=request) is None
    assert frame.render_frame_bbs_csv(result, current=request) is None
    assert all(issue.code in frame.render_frame_html(result) for issue in result.issues)


def test_centre_grid_clash_is_a_design_failure():
    data = _source()
    data["detailing"]["center_fill_mm"]["BX12-M"][0] = 2118
    request = frame.load_frame(data)
    result = frame.check_frame(request)
    assert result.status == "FAIL"
    assert result.calculation["failed_checks"] == ["shared_beam_constructible_geometry"]
    assert frame.render_frame_bbs_csv(result, current=request) is None
    assert frame.render_frame_svg(result, current=request) is None


def test_exterior_column_end_pitch_is_used_in_strength_and_schedule():
    data = _source()
    data["joint_geometry"]["J2"]["column_end_pitch_mm"] = 70
    request = frame.load_frame(data)
    result = frame.check_frame(request)
    assert result.status == "PASS", result.issues
    data = result.calculation
    assert data["column_legs"]["C-J2-upper"]["adverse_transverse_pitch_mm"] == 72
    assert data["column_legs"]["C-J1-upper"]["adverse_transverse_pitch_mm"] == 67
    assert data["artifact_reconciliation"]["checked_tie_and_beam_cut_marks"][
        "C-J2-upper:C-W"
    ]["stations_mm"][:2] == [40, 110]
