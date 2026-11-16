"""Frozen DUCT01 interior-joint acceptance through the public facade."""

from __future__ import annotations

import copy
import csv
import io
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from structural_lib.design.is13920 import joint

FIXTURE = (
    Path(__file__).parents[3]
    / "docs/verification/library-030-duct01-interior-joint.json"
)
APPLICABILITY = "Declared IS 13920 regular interior specimen."


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text())


def _request(document: dict, changes: dict | None = None):
    value = copy.deepcopy(document["request"])
    value["applicability_reference"] = APPLICABILITY
    if changes:
        value.update(copy.deepcopy(changes))
    return joint.load_joint(value)


def _assert_expected(actual, expected, *, path: str = "") -> None:
    """Compare every frozen baseline key while admitting new cage evidence."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), path
        for key, value in expected.items():
            _assert_expected(actual[key], value, path=f"{path}.{key}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, value in enumerate(expected):
            _assert_expected(actual[index], value, path=f"{path}[{index}]")
    elif isinstance(expected, float):
        if path.endswith("equilibrium_residual_n") and abs(expected) < 1e-5:
            assert abs(actual) < 1e-5, path
        else:
            assert math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-6), path
    else:
        assert actual == expected, path


def _apply_action_override(value: dict, override: dict) -> None:
    for row in value["directions"][override["direction"]]:
        if row["combination_id"] == override["combination_id"]:
            row[override["field"]] = copy.deepcopy(override["value"])
            return
    raise AssertionError(f"No action row {override['combination_id']}")


def test_duct01_frozen_baseline_and_checked_artifacts() -> None:
    document = _fixture()
    request = _request(document)
    result = joint.check_joint(request)

    assert result.status == "PASS"
    _assert_expected(result.calculation, document["expected"])
    encoded = result.to_dict()
    assert encoded["request"] == request.model_dump(mode="json")
    _assert_expected(encoded["calculation"], document["expected"])
    detached = result.calculation
    detached["status"] = "altered"
    assert result.calculation["status"] == "PASS"

    svg = joint.render_joint_svg(result, current=request)
    csv_text = joint.render_joint_bbs_csv(result, current=request)
    report = joint.render_joint_html(result, current=request)
    assert svg is not None and csv_text is not None
    root = ET.fromstring(svg)
    nodes = list(root.iter())
    stations = [
        node.attrib["data-station-mm"] for node in nodes if "data-piece" in node.attrib
    ]
    assert len(stations) == sum(
        len(item["stations_mm"])
        for item in document["expected"]["placement"][
            "column_transverse_joint_marks"
        ].values()
    )
    beam_paths = [node for node in nodes if "data-path-start-mm" in node.attrib]
    assert {node.attrib["data-section-plane"] for node in beam_paths} == {"X", "Y"}
    assert {
        (node.attrib["data-path-start-mm"], node.attrib["data-path-end-mm"])
        for node in beam_paths
    } == {("-1400", "1950")}
    assert {node.attrib["data-across-mm"] for node in beam_paths} == {
        "115",
        "220",
        "330",
        "435",
    }
    seats = {
        node.attrib["data-seat"]: node.attrib
        for node in nodes
        if "data-seat" in node.attrib
    }
    assert (seats["X-minus"]["x1"], seats["X-minus"]["x2"]) == ("0", "0")
    assert (seats["Y-minus"]["y1"], seats["Y-minus"]["y2"]) == ("0", "0")
    assert {node.attrib["data-relative-level-mm"] for node in beam_paths} == {
        "62",
        "538",
        "105",
        "495",
    }
    hooks = [node for node in nodes if node.attrib.get("data-hook-angle-deg") == "135"]
    assert len(hooks) == 2
    assert {
        (
            hook.attrib["data-bend-radius-mm"],
            hook.attrib["data-hook-tail-mm"],
            hook.attrib["data-hook-ramp-mm"],
            hook.attrib["data-hook-rise-mm"],
        )
        for hook in hooks
    } == {("32", "120", "60", "18")}
    assert all(
        float(coordinate) >= 0
        for hook in hooks
        for coordinate in hook.attrib["d"].split()
        if coordinate not in {"M", "A", "L"}
    )
    assert svg in report
    assert all(
        f'data-check="{name}"' in report for name in result.calculation["governing"]
    )

    rows = list(csv.DictReader(io.StringIO(csv_text)))
    expected_marks = document["expected"]["placement"]["column_transverse_joint_marks"]
    assert [row["bar_mark"] for row in rows] == ["C-H", "C-TX", "C-TY"]
    for row in rows:
        expected = expected_marks[row["bar_mark"]]
        assert int(row["quantity"]) == expected["quantity"]
        assert math.isclose(
            float(row["cut_length_mm"]), expected["cut_mm"], abs_tol=1e-6
        )
        kg = math.pi * (0.012 / 2) ** 2 * float(row["total_length_mm"]) / 1000 * 7850
        assert math.isclose(float(row["total_weight_kg"]), kg, abs_tol=1e-9)
        assert row["input_hash"] == result.input_hash
        assert row["joint_id"] == "J1"

    stale = _request(document, {"cage_action_revision": "DUCT01-DECLARED-R0"})
    assert joint.render_joint_svg(result, current=stale) is None
    assert joint.render_joint_bbs_csv(result, current=stale) is None


def test_duct01_frozen_fail_hold_controls_and_artifact_withholding() -> None:
    document = _fixture()
    statuses = {"FAIL": 0, "HOLD": 0}
    for name, control in document["controls"].items():
        value = copy.deepcopy(document["request"])
        value["applicability_reference"] = APPLICABILITY
        value.update(copy.deepcopy(control.get("changes", {})))
        if override := control.get("action_override"):
            _apply_action_override(value, override)
        request = joint.load_joint(value)
        result = joint.check_joint(request)
        expected = control["expected"]
        assert result.status == expected["status"], name
        statuses[result.status] += 1
        if result.status == "FAIL":
            assert (
                sorted(
                    issue.code.removeprefix("JOINT.").lower() for issue in result.issues
                )
                == expected["failed_checks"]
            ), name
            if "governing" in expected:
                _assert_expected(
                    result.calculation["governing"][expected["failed_checks"][0]],
                    expected["governing"],
                    path=name,
                )
        else:
            assert result.calculation["reason"] == expected["reason"], name
        assert joint.render_joint_svg(result, current=request) is None, name
        assert joint.render_joint_bbs_csv(result, current=request) is None, name
        assert result.status in joint.render_joint_html(result, current=request), name
    assert statuses == {"FAIL": 7, "HOLD": 4}
