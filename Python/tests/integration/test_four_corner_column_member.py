"""Physical column entry-point, independent reference and export verification."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "Python/examples/four_corner_column_member.py"
BUILD_INPUT = runpy.run_path(str(EXAMPLE))["member_input"]
FIXTURE = json.loads(
    (ROOT / "docs/verification/library-027-four-corner-column.json").read_text(
        encoding="utf-8"
    )
)


@pytest.mark.parametrize("axis", ("x", "y"))
def test_physical_column_matches_independent_reference_and_section_layers(axis):
    request = column.load_four_corner_member(BUILD_INPUT(axis))
    assert column.load_four_corner_member(request.model_dump_json()) == request
    result = column.check_four_corner_member(request)
    expected = FIXTURE["axes"][axis]["expected"]
    cage, strength = result.calculation["cage"], result.calculation["strength"]
    assert result.engineering_status == "PASS"
    assert result.envelope.overall_status == "PASS"
    assert result.qualified_review_required
    for field in (
        "supplied_steel_area_mm2",
        "steel_ratio",
        "bar_centroid_offset_mm",
        "minimum_tie_diameter_mm",
        "maximum_tie_spacing_mm",
    ):
        assert cage[field] == pytest.approx(expected[field], abs=1e-8, rel=0)
    assert [(bar["x_from_left_mm"], bar["y_from_top_mm"]) for bar in cage["bars"]] == [
        (60, 60),
        (240, 60),
        (240, 340),
        (60, 340),
    ]
    tolerances = FIXTURE["owner_comparison_tolerances"]
    for field, reference in (
        ("utilization_ratio", "continuous_utilization"),
        ("Pu_cap_kN", "continuous_pu_capacity_kn"),
        ("Mu_cap_kNm", "continuous_mu_capacity_knm"),
    ):
        assert strength[field] == pytest.approx(
            expected[reference], abs=tolerances[field], rel=0
        )
    assert strength["e_min_mm"] == expected["minimum_eccentricity_mm"]
    assert result.calculation["effective_length_mm"] == expected["effective_length_mm"]

    # Rotate the actual four bars into the selected section depth coordinates.
    width, depth = (300, 400) if axis == "x" else (400, 300)
    coordinate = "y_from_top_mm" if axis == "x" else "x_from_left_mm"
    depths = sorted({bar[coordinate] for bar in cage["bars"]})
    section = column.layered_section_response(
        column.load_layered_section(
            {
                "b_mm": width,
                "D_mm": depth,
                "xu_mm": expected["xu_mm"],
                "fck_nmm2": 25,
                "fy_nmm2": 415,
                "layers": [
                    {"depth_from_top_mm": y, "count": 2, "diameter_mm": 20}
                    for y in depths
                ],
            }
        )
    )
    assert section.axial_kn == pytest.approx(
        expected["continuous_pu_capacity_kn"], abs=1e-6, rel=0
    )
    assert section.centroid_moment_knm == pytest.approx(
        expected["continuous_mu_capacity_knm"], abs=1e-6, rel=0
    )

    html = column.render_four_corner_member_html(result)
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    assert payload["envelope"]["result_identity"]["input_hash"] in html
    for check in payload["calculation"]["checks"]:
        assert check["code"] in html
    for bar in cage["bars"]:
        assert f"<td>{bar['bar_id']}</td>" in html
    assert "<strong>Engineering status PASS</strong>" in html


@pytest.mark.parametrize(
    ("field", "value", "codes"),
    (
        ("corner_inset_mm", 0, {"COLUMN.TIE_ENCLOSURE"}),
        ("longitudinal_bar_diameter_mm", 12, {"COLUMN.STEEL_MIN"}),
        ("nominal_cover_mm", 180, {"COLUMN.BAR_CENTRES", "COLUMN.TIE_BEND_FIT"}),
    ),
)
def test_inadequate_physical_arrangement_is_a_failed_result(field, value, codes):
    payload = BUILD_INPUT()
    payload["reinforcement"][field] = value
    result = column.check_four_corner_member(column.load_four_corner_member(payload))
    assert result.engineering_status == "FAIL"
    assert codes <= {issue.code for issue in result.issues}


def test_long_face_is_checked_instead_of_average_perimeter_spacing():
    payload = BUILD_INPUT()
    payload["geometry"]["D_mm"] = 500
    result = column.check_four_corner_member(column.load_four_corner_member(payload))
    assert result.engineering_status == "FAIL"
    assert "COLUMN.PERIPHERAL_SPACING" in {issue.code for issue in result.issues}


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("diameter_mm", 4, "COLUMN.TIE_DIAMETER"),
        ("spacing_mm", 350, "COLUMN.TIE_SPACING"),
        ("closed", False, "COLUMN.TIE_CLOSED"),
        ("hook_tail_mm", 47, "COLUMN.TIE_HOOK_TAIL"),
        ("hook_tail_mm", 2000, "COLUMN.TIE_HOOK_FIT"),
        ("hook_angle_deg", 90, "COLUMN.TIE_HOOK_ANGLE"),
        ("internal_bend_radius_mm", 15, "COLUMN.TIE_BEND_RADIUS"),
    ),
)
def test_actual_tie_decisions_survive_the_html_export(field, value, code):
    payload = BUILD_INPUT()
    payload["reinforcement"]["tie"][field] = value
    result = column.check_four_corner_member(column.load_four_corner_member(payload))
    assert result.engineering_status == "FAIL"
    assert code in {issue.code for issue in result.issues}
    html = column.render_four_corner_member_html(result)
    assert "<strong>Engineering status FAIL</strong>" in html
    assert code in html


def test_missing_tie_and_slender_scope_hold_capacity():
    payload = BUILD_INPUT()
    payload["reinforcement"]["tie"] = None
    result = column.check_four_corner_member(column.load_four_corner_member(payload))
    assert result.engineering_status == "HOLD"
    assert result.calculation["cage"] is None
    assert result.calculation["strength"] is None
    assert {issue.code for issue in result.issues} == {"COLUMN.TIE_REQUIRED"}
    assert "Engineering status HOLD" in column.render_four_corner_member_html(result)

    payload = BUILD_INPUT()
    payload["geometry"].update(
        unsupported_length_mm=6000, end_condition="HINGED_HINGED"
    )
    result = column.check_four_corner_member(column.load_four_corner_member(payload))
    assert result.engineering_status == "HOLD"
    assert result.calculation["strength"] is None
    assert "COLUMN.SHORT_PROFILE" in {issue.code for issue in result.issues}


def test_minimum_eccentricity_uses_the_actual_unsupported_length():
    payload = BUILD_INPUT()
    payload["actions"]["moment_knm"] = 0
    result = column.check_four_corner_member(column.load_four_corner_member(payload))
    assert result.calculation["strength"]["Mu_kNm"] == 10


@pytest.mark.parametrize(
    "change", ("nonfinite", "coercion", "unknown_field", "duplicate_key")
)
def test_public_loader_rejects_malformed_input(change):
    payload = BUILD_INPUT()
    if change == "nonfinite":
        payload["actions"]["pu_kn"] = float("nan")
    if change == "coercion":
        payload["geometry"]["braced"] = 1
    if change == "unknown_field":
        payload["reinforcement"]["bar_count"] = 6
    if change == "duplicate_key":
        payload = json.dumps(payload).replace(
            '"pu_kn": 500', '"pu_kn": 500, "pu_kn": 800'
        )
    with pytest.raises(InputContractError):
        column.load_four_corner_member(payload)


def test_example_writes_consistent_json_and_html_controls(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(EXAMPLE), "--output-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    summary = json.loads(completed.stdout)
    assert {key: value["status"] for key, value in summary.items()} == {
        "axis_x": "PASS",
        "axis_y": "PASS",
        "overload": "FAIL",
        "insufficient_tie": "FAIL",
        "missing_tie": "HOLD",
    }
    for name, expected in summary.items():
        payload = json.loads((tmp_path / f"{name}.json").read_text(encoding="utf-8"))
        html = (tmp_path / f"{name}.html").read_text(encoding="utf-8")
        assert payload["envelope"]["engineering_status"] == expected["status"]
        assert expected["input_hash"] in html
        assert f"Engineering status {expected['status']}" in html
