"""COL02 public entry point against independently frozen reference values."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

_ROOT = Path(__file__).resolve().parents[3]
_INPUT = runpy.run_path(
    str(_ROOT / "Python/examples/tied_rectangular_column_member.py")
)["member_input"]
_REFERENCE = json.loads(
    (_ROOT / "docs/verification/library-029-col02-rectangular-column.json").read_text()
)


@pytest.mark.parametrize("layout", tuple(_REFERENCE["layouts"]))
@pytest.mark.parametrize("action", tuple(_REFERENCE["actions_knm"]))
def test_tied_column_matches_frozen_actual_cage(layout, action):
    mx, my = _REFERENCE["actions_knm"][action]
    request = column.load_tied_rectangular_member(_INPUT(layout, mx, my))
    assert column.load_tied_rectangular_member(request.model_dump_json()) == request
    result = column.check_tied_rectangular_member(request)
    calculation = result.calculation
    strength = calculation["strength"]
    expected = _REFERENCE["layouts"][layout]
    tolerance = _REFERENCE["production_tolerances"]
    assert result.engineering_status == expected["actions"][action]["strength_status"]
    assert result.qualified_review_required
    assert result.request.actions.mx_knm == mx
    assert result.request.actions.my_knm == my
    common = _REFERENCE["common_expected"]
    assert calculation["effective_length_mm"] == common["effective_length_mm"]
    checks = calculation["checks"]
    short = next(check for check in checks if check["code"] == "COLUMN.SHORT_PROFILE")
    assert short["slenderness_x"] == common["slenderness_x"]
    assert short["slenderness_y"] == common["slenderness_y"]
    cage = calculation["cage"]
    for field, reference in (
        ("tie_centreline_width_mm", "tie_centerline_width_mm"),
        ("tie_centreline_depth_mm", "tie_centerline_depth_mm"),
        ("minimum_tie_diameter_mm", "minimum_tie_diameter_mm"),
        ("maximum_tie_spacing_mm", "maximum_tie_spacing_mm"),
    ):
        assert cage[field] == common[reference]
    spans = [
        check for check in checks if check["code"] == "COLUMN.MIDPOINT_RESTRAINT_SPAN"
    ]
    assert len(spans) == len(expected["cross_ties"])
    assert all(check["limit"] == common["maximum_restraint_span_mm"] for check in spans)
    bars = {
        bar["bar_id"]: [bar["x_from_left_mm"], bar["y_from_top_mm"]]
        for bar in cage["bars"]
    }
    assert bars == expected["bars_from_left_top_mm"]
    assert cage["supplied_steel_area_mm2"] == pytest.approx(expected["steel_area_mm2"])
    assert [
        {
            "tie_id": tie["tie_id"],
            "restrained_bar_ids": list(tie["restrained_bar_ids"]),
            "station_offset_mm": tie["station_offset_mm"],
        }
        for tie in calculation["cross_ties"]
    ] == expected["cross_ties"]
    for tie in calculation["cross_ties"]:
        first, second = tie["restrained_bar_ids"]
        assert list(tie["start_mm"]) == bars[first]
        assert list(tie["end_mm"]) == bars[second]
        assert tie["pitch_mm"] == _REFERENCE["inputs"]["tie_spacing_mm"]

    assert strength["puz_kn"] == pytest.approx(expected["puz_kn"])
    assert strength["alpha_n"] == pytest.approx(expected["alpha_n"])
    for axis in ("x", "y"):
        eccentricity = strength[f"minimum_eccentricity_{axis}_mm"]
        assert eccentricity == common[f"minimum_eccentricity_{axis}_mm"]
        assert (
            request.actions.pu_kn * eccentricity / 1000
            == common[f"minimum_moment_{axis}_knm"]
        )
    for axis, expected_face in (
        ("x", "bottom" if mx < 0 else "top"),
        ("y", "right" if my < 0 else "left"),
    ):
        state = strength["axes"][axis]
        assert state["compression_face"] == expected_face
        for field in ("capacity_knm", "xu_mm", "axial_residual_kn"):
            assert state[field] == pytest.approx(
                expected["axes"][axis][field], abs=tolerance[field], rel=0
            )
        assert {bar["bar_id"] for bar in state["bars"]} == set(bars)
    for name in ("interaction_ratio", "governing_ratio"):
        assert strength[name] == pytest.approx(
            expected["actions"][action][name],
            abs=tolerance["interaction_ratio"],
            rel=0,
        )
    if action == "minimum":
        assert strength["governing_basis"] == "minimum_eccentricity_y"
        assert strength["interaction_ratio"] == 0
    if action in ("biaxial", "overload"):
        html = column.render_tied_rectangular_member_html(result)
        json_payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
        assert json_payload["envelope"]["result_identity"]["input_hash"] in html
        assert f"Engineering status {result.engineering_status.value}" in html
        assert "<svg" in html
        for bar in bars:
            assert f"<title>{bar}</title>" in html


@pytest.mark.parametrize(
    ("layout", "rotated_layout"),
    (
        ("eight_bar", "eight_bar"),
        ("six_bar_omit_x_face_midpoints", "six_bar_omit_y_face_midpoints"),
        ("six_bar_omit_y_face_midpoints", "six_bar_omit_x_face_midpoints"),
    ),
)
def test_rotating_the_member_swaps_fixed_axial_capacities(layout, rotated_layout):
    original = column.check_tied_rectangular_member(
        column.load_tied_rectangular_member(_INPUT(layout))
    ).calculation["strength"]
    rotated_payload = _INPUT(rotated_layout, 35, -50)
    rotated_payload["geometry"].update(b_mm=400, D_mm=300)
    rotated = column.check_tied_rectangular_member(
        column.load_tied_rectangular_member(rotated_payload)
    ).calculation["strength"]
    assert rotated["axes"]["x"]["capacity_knm"] == pytest.approx(
        original["axes"]["y"]["capacity_knm"]
    )
    assert rotated["axes"]["y"]["capacity_knm"] == pytest.approx(
        original["axes"]["x"]["capacity_knm"]
    )
    assert rotated["governing_ratio"] == pytest.approx(original["governing_ratio"])


@pytest.mark.parametrize(
    ("control", "code"),
    (
        ("missing_perimeter_tie", "COLUMN.TIE_REQUIRED"),
        ("missing_midpoint_cross_tie", "COLUMN.MIDPOINT_TIE_REQUIRED"),
        ("wrong_midpoint_cross_tie", "COLUMN.MIDPOINT_TIE_PAIR"),
        ("duplicate_cross_tie_station", "COLUMN.MIDPOINT_TIE_LEVELS"),
        ("short_hook_tail", "COLUMN.TIE_HOOK_TAIL"),
        ("wide_pitch", "COLUMN.TIE_SPACING"),
        ("45_mm_centre_offset", "COLUMN.TIE_ENCLOSURE"),
        ("slender", "COLUMN.SHORT_PROFILE"),
        ("outside_partial_compression", "COLUMN.PM_BASIS"),
        ("axial_at_or_above_puz", "COLUMN.AXIAL_LIMIT"),
    ),
)
def test_tied_member_fails_closed(control, code):
    payload = _INPUT()
    reinforcement = payload["reinforcement"]
    tie = reinforcement["tie"]
    cross_ties = reinforcement["cross_ties"]
    if control == "missing_perimeter_tie":
        reinforcement["tie"] = None
    elif control == "missing_midpoint_cross_tie":
        cross_ties.pop()
    elif control == "wrong_midpoint_cross_tie":
        cross_ties[0]["restrained_bar_ids"] = ["M_LEFT", "M_TOP"]
    elif control == "duplicate_cross_tie_station":
        cross_ties[1]["station_offset_mm"] = cross_ties[0]["station_offset_mm"]
    elif control == "short_hook_tail":
        tie["hook_tail_mm"] = 47
    elif control == "wide_pitch":
        tie["spacing_mm"] = 301
    elif control == "45_mm_centre_offset":
        reinforcement["bar_center_offset_mm"] = 45
    elif control == "slender":
        payload["geometry"].update(
            unsupported_length_mm=6000, end_condition="HINGED_HINGED"
        )
    elif control == "outside_partial_compression":
        payload["actions"]["pu_kn"] = 1800
    elif control == "axial_at_or_above_puz":
        payload["actions"]["pu_kn"] = 2500
    result = column.check_tied_rectangular_member(
        column.load_tied_rectangular_member(payload)
    )
    assert result.engineering_status == _REFERENCE["controls"][control]
    assert code in {issue.code for issue in result.issues}
    strength = result.calculation["strength"]
    assert strength is None or strength["governing_ratio"] is None
    assert code in column.render_tied_rectangular_member_html(result)
    json.dumps(result.to_dict(), allow_nan=False)


def test_tied_member_rejects_out_of_member_station():
    payload = _INPUT()
    payload["actions"]["check_station_mm"] = 3001
    with pytest.raises(InputContractError, match="within the unsupported length"):
        column.load_tied_rectangular_member(payload)


def test_bars_far_inside_the_perimeter_do_not_pass_restraint():
    payload = _INPUT()
    payload["reinforcement"]["bar_center_offset_mm"] = 65
    result = column.check_tied_rectangular_member(
        column.load_tied_rectangular_member(payload)
    )
    assert result.engineering_status == "FAIL"
    assert "COLUMN.PERIMETER_RESTRAINT_INSET" in {issue.code for issue in result.issues}
    assert result.calculation["strength"] is None
