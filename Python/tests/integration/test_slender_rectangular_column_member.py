"""Replay frozen COL04 cases through the public package and output renderers."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib import get_supported_is456_capability_document
from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

_ROOT = Path(__file__).resolve().parents[3]
_REFERENCE = json.loads(
    (_ROOT / "docs/verification/library-029-col04-slender-column.json").read_text()
)
_CASES = _REFERENCE["cases"]
_TOL = _REFERENCE["tolerances"]
_SVG_NS = {"s": "http://www.w3.org/2000/svg"}


def _approx(expected, tolerance):
    return pytest.approx(expected, abs=_TOL[tolerance], rel=0)


def _ray(actual, expected):
    for field in ("mx_knm", "my_knm", "capacity_knm"):
        assert actual[field] == _approx(expected[field], "moment_knm")
    assert actual["xu_mm"] == _approx(expected["xu_mm"], "xu_mm")
    for field in ("axial_residual_kn", "transverse_residual_knm"):
        assert abs(actual[field]) <= _TOL["residual_kn_or_knm"]


@pytest.mark.parametrize("case", tuple(_CASES))
def test_col04_against_frozen_references(case):
    row = _CASES[case]
    expected = row["expected"]
    if expected["member_status"] == "REJECT":
        for payload in (row["request"], json.dumps(row["request"])):
            with pytest.raises(InputContractError) as caught:
                column.load_slender_rectangular_member(payload)
            assert caught.value.issues[0].code == expected["issue"]
        return

    request = column.load_slender_rectangular_member(row["request"])
    assert column.load_slender_rectangular_member(request.model_dump_json()) == request
    result = column.check_slender_rectangular_member(request)
    calculation = result.calculation
    assert result.qualified_review_required
    assert result.engineering_status == expected["member_status"]
    assert calculation["restraint_status"] == expected["restraint_status"]
    assert calculation["strength_status"] == expected["strength_status"]
    assert calculation["basis"] == request.actions.basis
    assert calculation["combination_id"] == request.actions.combination_id
    assert calculation["analysis_revision"] == request.analysis_revision
    for axis, targets in expected["axes"].items():
        actual = calculation["axes"][axis]
        assert actual["classification"] == targets["classification"]
        assert actual["slenderness"] == _approx(targets["slenderness"], "ratio")
        for field in (
            "minimum_eccentricity_mm",
            "initial_moment_knm",
            "end_floor_knm",
            "additional_moment_knm",
        ):
            assert actual[field] == _approx(targets[field], "moment_knm")

    strength = calculation["strength"]
    if "issue" in expected:
        assert strength is None
        assert expected["issue"] in {issue.code for issue in result.issues}
    else:
        assert strength["puz_kn"] == _approx(expected["puz_kn"], "residual_kn_or_knm")
        assert strength["alpha_n"] == _approx(expected["alpha_n"], "ratio")
        assert strength["governing_id"] == expected["governing_id"]
        assert strength["governing_ratio"] == _approx(
            expected["governing_ratio"], "ratio"
        )
        for axis, ray in expected["capacities"].items():
            _ray(strength["axes"][axis], ray)
        assert strength["minimum_eccentricity_ratios"] == _approx(
            expected["minimum_eccentricity_ratios"], "ratio"
        )
        assert strength["evaluated"].keys() == expected["evaluated"].keys()
        for identifier, pair in expected["evaluated"].items():
            actual = strength["evaluated"][identifier]
            for field in ("mx_knm", "my_knm"):
                assert actual[field] == _approx(pair[field], "moment_knm")
            for field in ("ratio", "contour_ratio", "direct_ratio"):
                assert actual[field] == _approx(pair[field], "ratio")
            if "demand" in pair:
                _ray(actual["demand"], pair["demand"])
            if identifier.startswith("EQUIVALENT-"):
                assert actual["station_mm"] is None
                assert actual["kind"] == "equivalent_design_pair"

    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    input_hash = payload["envelope"]["result_identity"]["input_hash"]
    report = column.render_slender_rectangular_member_html(result)
    drawing = column.render_slender_rectangular_member_svg(result)
    assert drawing in report
    assert input_hash in drawing
    assert f"Engineering status {expected['member_status']}" in report
    svg = ElementTree.fromstring(drawing)
    bars = svg.findall("s:circle", _SVG_NS)
    assert len(bars) == len(calculation["cage"]["bars"])
    for circle, bar in zip(bars, calculation["cage"]["bars"], strict=True):
        assert circle.findtext("s:title", namespaces=_SVG_NS) == bar["bar_id"]
        assert float(circle.attrib["cx"]) == bar["x_from_left_mm"]
        assert float(circle.attrib["cy"]) == bar["y_from_top_mm"]
    assert [
        line.findtext("s:title", namespaces=_SVG_NS)
        for line in svg.findall("s:line", _SVG_NS)
    ] == [tie["tie_id"] for tie in calculation["cross_ties"]]


def test_physical_column_profiles_are_discoverable_and_resolve():
    capabilities = get_supported_is456_capability_document()["capabilities"]
    info = next(item for item in capabilities if item["capability_id"] == "column")
    profiles = {entry["operation"]: entry for entry in info["python_profiles"]}
    assert profiles.keys() == {
        "check_four_corner_member",
        "check_tied_rectangular_member",
        "check_positioned_rectangular_member",
        "check_slender_rectangular_member",
        "check_circular_member",
    }
    for profile in profiles.values():
        module = importlib.import_module(profile["module"])
        assert profile["loader"] in module.__all__
        assert callable(getattr(module, profile["operation"]))
        assert (_ROOT / profile["example"]).is_file()
    profile = profiles["check_slender_rectangular_member"]
    module = importlib.import_module(profile["module"])
    request = getattr(module, profile["loader"])(_CASES["minor_slender"]["request"])
    assert request.schema_version == profile["request_schema"]
    result = getattr(module, profile["operation"])(request)
    assert result.workflow_id == profile["workflow_id"]
    assert result.engineering_status == "PASS"
