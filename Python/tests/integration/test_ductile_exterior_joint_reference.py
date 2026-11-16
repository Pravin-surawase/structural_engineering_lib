"""Replay the independent exterior-joint fixture through the public API."""

from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from structural_lib.design.is13920 import joint
from structural_lib.services.bbs import calculate_bar_weight

DIRECTORY = Path(__file__).parents[3] / "docs/verification"
FIXTURE = DIRECTORY / "library-030-duct02-exterior-joint.json"
VERSION = "ductile-exterior-joint/v1"


@pytest.fixture(scope="module")
def reference() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _request(reference, changes=None):
    return joint.load_joint(
        {
            **reference["request"],
            "schema_version": VERSION,
            "applicability_reference": "Declared IS 13920 regular exterior specimen.",
            **(changes or {}),
        }
    )


def _match(actual, expected, path="calculation"):
    if isinstance(expected, dict):
        for name, value in expected.items():
            _match(actual[name], value, f"{path}.{name}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, (item, value) in enumerate(zip(actual, expected, strict=True)):
            _match(item, value, f"{path}[{index}]")
    elif isinstance(expected, float):
        assert math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-6), path
    else:
        assert actual == expected, path


def test_exterior_strength_detail_and_artifacts(reference):
    request = _request(reference)
    result = joint.check_joint(request)

    assert isinstance(request, joint.DuctileExteriorJointRequestV1)
    assert isinstance(joint.load_joint(request.model_dump_json()), type(request))
    assert result.status == "PASS"
    assert result.to_dict()["workflow_id"] == "DUCT02_EXTERIOR_JOINT"
    assert result.envelope.result_identity.contract_version == VERSION
    _match(result.calculation, reference["expected"])

    assert joint.render_joint_svg(result) is None
    assert joint.render_joint_bbs_csv(result) is None
    current = _request(reference, {"assembly": "Changed site assembly review."})
    assert joint.render_joint_svg(result, current=current) is None
    assert joint.render_joint_bbs_csv(result, current=current) is None

    expected = reference["expected"]["placement"]
    svg = joint.render_joint_svg(result, current=request)
    bbs = joint.render_joint_bbs_csv(result, current=request)
    report = joint.render_joint_html(result, current=request)
    assert svg is not None and bbs is not None and result.input_hash in report
    assert "946.25" in report and "949" in report
    assert "EQ2-Y+" in report
    assert request.action_revision in svg and result.input_hash in svg

    nodes = [node.attrib for node in ET.fromstring(svg).iter()]
    hooks = {
        attrs["data-bar-id"]: attrs
        for attrs in nodes
        if attrs.get("data-local-beyond-face") == "true"
    }
    assert len(hooks) == 8
    for hook in expected["x_hook_paths"]:
        attrs = hooks[hook["bar_id"]]
        assert float(attrs["data-bend-radius-mm"]) == hook["bend_centreline_radius_mm"]
        assert (
            json.loads(attrs["data-bend-centre-xyz-mm"]) == hook["bend_centre_xyz_mm"]
        )
        assert json.loads(attrs["data-tail-end-xyz-mm"]) == hook["tail_end_xyz_mm"]
        # SVG sweep follows the bend centre and reverses for the upturned bars.
        sweep = 1 if "TOP" in hook["bar_id"] else 0
        path = attrs["d"].split()
        assert int(path[path.index("A") + 5]) == sweep

    y_paths = {
        attrs["data-bar-id"]: attrs for attrs in nodes if "data-level-z-mm" in attrs
    }
    assert len(y_paths) == 8
    for path in expected["y_through_paths"]:
        attrs = y_paths[path["bar_id"]]
        assert json.loads(attrs["data-path-start-xyz-mm"]) == path["points_mm"][0]
        assert json.loads(attrs["data-path-end-xyz-mm"]) == path["points_mm"][1]

    schedule = {row["bar_mark"]: row for row in csv.DictReader(io.StringIO(bbs))}
    assert len(schedule) == 11
    assert {
        (attrs["data-bar-mark"], float(attrs["data-station-mm"]))
        for attrs in nodes
        if "data-station-mm" in attrs
    } == {
        (mark, station)
        for mark, tie in expected["joint_tie_marks"].items()
        for station in tie["stations_mm"]
    }
    for mark, expected_mark in expected["joint_tie_marks"].items():
        row = schedule[mark]
        assert row["schedule_scope"] == "in_core_order"
        assert row["input_hash"] == result.input_hash
        assert int(row["quantity"]) == expected_mark["quantity"]
        cut = float(row["cut_length_mm"])
        assert cut == pytest.approx(expected_mark["nominal_cut_length_mm"])
        assert float(row["total_weight_kg"]) == pytest.approx(
            calculate_bar_weight(
                expected_mark["diameter_mm"],
                expected_mark["quantity"] * expected_mark["nominal_cut_length_mm"],
                round_weight=False,
            )
        )
    for hook in expected["x_hook_paths"]:
        row = schedule[hook["bar_id"]]
        assert row["schedule_scope"] == "local_beyond_face_geometry_not_order_total"
        assert row["cut_length_mm"] == row["total_weight_kg"] == ""
        assert float(row["local_beyond_face_length_mm"]) == pytest.approx(
            hook["centreline_length_beyond_face_mm"]
        )


CONTROLS = (
    "weak_column",
    "weak_joint_core",
    "widely_spaced_link_groups",
    "short_bottom_hook",
    "overlapping_vertical_hooks",
    "missing_orthogonal_negative",
    "missing_terminated_paths",
    "stale_revision",
    "missing_joint_mechanism",
)


@pytest.mark.parametrize("control", CONTROLS)
def test_exterior_control_withholds_checked_artifacts(reference, control):
    case = reference["controls"][control]
    request = _request(reference, case["changes"])
    result = joint.check_joint(request)
    expected = case["expected"]
    assert result.status == expected["status"]
    if result.status == "FAIL":
        assert [key for key, ok in result.calculation["checks"].items() if not ok] == (
            expected["failed_checks"]
        )
    else:
        assert result.calculation["reason"] == expected["reason"]
    assert joint.render_joint_svg(result, current=request) is None
    assert joint.render_joint_bbs_csv(result, current=request) is None
    assert all(issue.code in joint.render_joint_html(result) for issue in result.issues)


def test_non_touching_opposed_tails_can_still_fail_concrete_clearance(reference):
    hooks = reference["request"]["x_hooks"]
    request = _request(
        reference,
        {"x_hooks": {**hooks, "BOTTOM": {**hooks["BOTTOM"], "tip_x_mm": 473}}},
    )
    result = joint.check_joint(request)
    placement = result.calculation["placement"]
    assert all(
        entry["adverse_clearance_mm"] > 0
        for entry in placement["pair_clearances"].values()
    )
    assert placement["opposed_parallel_tail_clear_mm"] == 24.5
    assert placement["required_parallel_tail_clear_mm"] == 25
    assert result.status == "FAIL"
    assert not placement["fit_checks"]["opposed_parallel_tail_spacing"]
    assert joint.render_joint_svg(result, current=request) is None
    assert joint.render_joint_bbs_csv(result, current=request) is None
