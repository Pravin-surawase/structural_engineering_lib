"""Replay independent circular tied and spiral cases through the public API."""

from __future__ import annotations

import importlib
import json
from copy import deepcopy
from math import cos, pi, sin
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib import get_supported_is456_capability_document
from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

_ROOT = Path(__file__).resolve().parents[3]
_REFERENCE = json.loads(
    (_ROOT / "docs/verification/library-029-col05-circular-column.json").read_text()
)
_CASES = _REFERENCE["cases"]
_TOL = _REFERENCE["tolerances"]
_NS = {"s": "http://www.w3.org/2000/svg"}


def _ray(actual, expected):
    for key in ("capacity_knm", "mx_knm", "my_knm"):
        assert actual[key] == pytest.approx(
            expected[key], abs=_TOL["moment_knm"], rel=0
        )
    assert actual["xu_mm"] == pytest.approx(expected["xu_mm"], abs=_TOL["xu_mm"], rel=0)
    assert (
        abs((actual["normal_deg"] - expected["normal_deg"] + 180) % 360 - 180)
        <= _TOL["normal_deg"]
    )
    for key in ("axial_residual_kn", "transverse_residual_knm"):
        assert abs(actual[key]) <= _TOL["residual_kn_or_knm"]


@pytest.mark.parametrize("case", tuple(_CASES))
def test_circular_member_frozen_cases(case):
    row = _CASES[case]
    request = column.load_circular_member(row["request"])
    assert request == column.load_circular_member(request.model_dump_json())
    result = column.check_circular_member(request)
    calc = result.calculation
    expected = row["expected"]
    assert result.qualified_review_required
    assert result.engineering_status == expected["member_status"]
    for key in ("strength_status", "restraint_status", "spiral_enhancement_eligible"):
        assert calc[key] == expected[key]
    for key in (
        "gross_area_mm2",
        "steel_area_mm2",
        "gross_inertia_mm4",
        "minimum_eccentricity_mm",
        "puz_kn",
    ):
        assert calc[key] == pytest.approx(expected[key], rel=1e-10)
    assert calc["detail"] == pytest.approx(expected["detail"], rel=1e-10)

    strength = calc["strength"]
    if "strength" in expected:
        wanted = expected["strength"]
        assert strength["method"] == wanted["method"]
        assert strength["enhancement_factor"] == wanted["enhancement_factor"]
        assert strength["governing_ratio"] == pytest.approx(
            wanted["governing_ratio"], abs=_TOL["ratio"], rel=0
        )
        if wanted["method"] == "short_axial":
            for key in ("axial_capacity_kn", "tied_axial_capacity_kn"):
                assert strength[key] == pytest.approx(wanted[key], abs=0.01, rel=0)
        else:
            for key in ("contour_ratio", "direct_ratio", "alpha_n"):
                assert strength[key] == pytest.approx(
                    wanted[key], abs=_TOL["ratio"], rel=0
                )
            assert strength["minimum_eccentricity_ratios"] == pytest.approx(
                wanted["minimum_eccentricity_ratios"], abs=_TOL["ratio"], rel=0
            )
            for axis, ray in wanted["axes"].items():
                _ray(strength["axes"][axis], ray)
            if "demand" in wanted:
                _ray(strength["demand"], wanted["demand"])
            else:
                assert strength["demand"] is None
    else:
        assert strength is None

    drawing = column.render_circular_member_svg(result)
    report = column.render_circular_member_html(result)
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    assert payload["envelope"]["result_identity"]["input_hash"] in drawing
    assert drawing in report
    assert f"Engineering status {expected['member_status']}" in report
    svg = ElementTree.fromstring(drawing)
    steel = request.reinforcement
    centre = request.geometry.diameter_mm / 2
    circles = svg.findall("s:circle", _NS)
    assert float(circles[0].attrib["r"]) == centre
    bar_circles = circles[1:]
    if steel.transverse is not None:
        hoop, *bar_circles = bar_circles
        assert steel.transverse.tie_id in hoop.findtext("s:title", namespaces=_NS)
        assert (
            2 * float(hoop.attrib["r"])
            == expected["detail"]["transverse_centreline_diameter_mm"]
        )
    assert len(bar_circles) == steel.bar_count
    for i, circle in enumerate(bar_circles):
        angle = steel.first_bar_angle_deg * pi / 180 + 2 * pi * i / steel.bar_count
        assert circle.findtext("s:title", namespaces=_NS) == f"B{i + 1:02d}"
        assert float(circle.attrib["cx"]) == pytest.approx(
            centre + steel.ring_radius_mm * cos(angle)
        )
        assert float(circle.attrib["cy"]) == pytest.approx(
            centre + steel.ring_radius_mm * sin(angle)
        )


def test_outside_longitudinal_bar_rejected():
    request = deepcopy(_CASES["tied"]["request"])
    request["reinforcement"]["ring_radius_mm"] = 220
    with pytest.raises(InputContractError):
        column.load_circular_member(request)


def test_circular_profile_resolves_from_capability_document():
    doc = get_supported_is456_capability_document()
    capability = next(
        item for item in doc["capabilities"] if item["capability_id"] == "column"
    )
    profile = next(
        item
        for item in capability["python_profiles"]
        if item["operation"] == "check_circular_member"
    )
    module = importlib.import_module(profile["module"])
    assert (_ROOT / profile["example"]).is_file()
    request = getattr(module, profile["loader"])(_CASES["spiral"]["request"])
    assert request.schema_version == profile["request_schema"]
    result = getattr(module, profile["operation"])(request)
    assert result.workflow_id == profile["workflow_id"]
    assert result.engineering_status == "PASS"
