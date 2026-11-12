"""Replay COL03 independent signed capacities through the public column API."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

_ROOT = Path(__file__).resolve().parents[3]
_REFERENCE = json.loads(
    (_ROOT / "docs/verification/library-029-col03-mixed-column.json").read_text()
)
_CASES = _REFERENCE["cases"]


def _check(payload):
    return column.check_positioned_rectangular_member(
        column.load_positioned_rectangular_member(payload)
    )


def _assert_ray(actual, expected):
    tolerance = _REFERENCE["tolerances"]
    for field in ("capacity_knm", "xu_mm", "mx_knm", "my_knm"):
        limit = tolerance["xu_mm"] if field == "xu_mm" else tolerance["capacity_knm"]
        assert actual[field] == pytest.approx(expected[field], abs=limit, rel=0)
    assert abs((actual["normal_deg"] - expected["normal_deg"] + 180) % 360 - 180) <= (
        tolerance["normal_deg"]
    )
    assert abs(actual["axial_residual_kn"]) <= tolerance["residual_kn_or_knm"]
    assert abs(actual["transverse_residual_knm"]) <= tolerance["residual_kn_or_knm"]
    assert actual["p_kn"] == pytest.approx(
        expected["p_kn"], abs=tolerance["residual_kn_or_knm"], rel=0
    )


@pytest.mark.parametrize("case", tuple(_CASES))
def test_col03_signed_strength_and_member_dispositions(case):
    row = _CASES[case]
    request = column.load_positioned_rectangular_member(row["request"])
    assert (
        column.load_positioned_rectangular_member(request.model_dump_json()) == request
    )
    result = column.check_positioned_rectangular_member(request)
    calculation = result.calculation
    strength = calculation["strength"]
    expected = row["expected"]
    assert result.engineering_status == row["member_status"]
    assert result.qualified_review_required
    assert calculation["strength_status"] == expected["strength_status"]
    assert calculation["restraint_status"] == (
        "FAIL" if case == "original_50_mm" else "PASS"
    )
    assert strength["steel_area_mm2"] == pytest.approx(expected["steel_area_mm2"])
    assert strength["puz_kn"] == pytest.approx(expected["puz_kn"])
    assert strength["alpha_n"] == pytest.approx(expected["alpha_n"])
    for axis, ray in expected["axes"].items():
        _assert_ray(strength["axes"][axis], ray)
    _assert_ray(strength["demand"], expected["demand"])
    for name in ("contour_ratio", "direct_ratio", "governing_ratio"):
        assert strength[name] == pytest.approx(
            expected[name], abs=_REFERENCE["tolerances"]["ratio"], rel=0
        )
    for axis in ("x", "y"):
        assert strength["minimum_eccentricity_ratios"][axis] == pytest.approx(
            expected["minimum_eccentricity_ratios"][axis]
        )

    bars = calculation["cage"]["bars"]
    assert [
        {
            key: bar[key]
            for key in (
                "bar_id",
                "row",
                "diameter_mm",
                "x_from_left_mm",
                "y_from_top_mm",
            )
        }
        for bar in bars
    ] == row["request"]["reinforcement"]["bars"]
    html = column.render_positioned_rectangular_member_html(result)
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    assert payload["envelope"]["result_identity"]["input_hash"] in html
    assert f"Engineering status {row['member_status']}" in html
    for bar in bars:
        assert f"<title>{bar['bar_id']}</title>" in html

    if case == "original_50_mm":
        assert "COLUMN.TIE_ENCLOSURE" in {issue.code for issue in result.issues}
        assert not calculation["cross_ties"]
    else:
        detail = _REFERENCE["local_detail_reference"]
        for key in (
            "longitudinal_count_by_diameter_mm",
            "perimeter_count_per_pitch",
            "cross_tie_count_per_pitch",
        ):
            assert calculation["section_quantities"][key] == detail[key]
        for key in ("tie_centreline_width_mm", "tie_centreline_depth_mm"):
            assert calculation["cage"][key] == detail[key]
        assert min(
            link["minimum_inner_bar_clearance_mm"] for link in calculation["cross_ties"]
        ) == pytest.approx(detail["minimum_clear_between_cross_tie_and_inner_bar_mm"])
        for link in calculation["cross_ties"]:
            tie_id = link["tie_id"]
            assert link["centreline_length_mm"] == pytest.approx(
                detail["link_centreline_lengths_mm"][tie_id]
            )
            assert f"<title>{tie_id}</title>" in html
            assert len(link["hooks"]) == 2
        assert "<path" in html
        checks = {check["code"]: check for check in calculation["checks"]}
        assert checks["COLUMN.TIE_DIAMETER"]["limit"] == detail["tie_min_diameter_mm"]
        assert checks["COLUMN.TIE_SPACING"]["limit"] == detail["maximum_pitch_mm"]
        assert (
            checks["COLUMN.CROSS_TIE_RESTRAINT_SPAN"]["limit"]
            == detail["maximum_corner_restraint_span_mm"]
        )
        assert (
            checks["COLUMN.INNER_ROW_RESTRAINT"]["actual"]
            == detail["minimum_inner_clear_to_concrete_face_mm"]
        )


@pytest.mark.parametrize(
    ("case", "issue"),
    (
        ("missing_cross_tie", "COLUMN.CROSS_TIE_REQUIRED"),
        ("intersecting_cross_tie", "COLUMN.CROSS_TIE_BAR_CLEARANCE"),
        ("same_tie_level", "COLUMN.CROSS_TIE_LEVELS"),
        ("wide_pitch", "COLUMN.TIE_SPACING"),
        ("slender", "COLUMN.SHORT_PROFILE"),
    ),
)
def test_col03_restraint_and_profile_controls(case, issue):
    payload = deepcopy(_CASES["admitted_12_bar"]["request"])
    reinforcement = payload["reinforcement"]
    if case == "missing_cross_tie":
        reinforcement["cross_ties"].pop()
    elif case == "intersecting_cross_tie":
        reinforcement["cross_ties"][0]["hook_side"] = "positive"
    elif case == "same_tie_level":
        reinforcement["cross_ties"][1]["station_offset_mm"] = 15
    elif case == "wide_pitch":
        reinforcement["tie"]["spacing_mm"] = 257
    elif case == "slender":
        payload["geometry"].update(
            unsupported_length_mm=6000, end_condition="HINGED_HINGED"
        )
    result = _check(payload)
    assert result.engineering_status == _REFERENCE["controls"][case]
    assert issue in {item.code for item in result.issues}
    assert result.calculation["strength_status"] == (
        "HOLD" if case == "slender" else "PASS"
    )


def test_col03_rejects_coincident_centres_before_calculation():
    payload = deepcopy(_CASES["admitted_12_bar"]["request"])
    bars = payload["reinforcement"]["bars"]
    bars[1].update(
        x_from_left_mm=bars[0]["x_from_left_mm"], y_from_top_mm=bars[0]["y_from_top_mm"]
    )
    with pytest.raises(InputContractError, match="coincident or overlap"):
        column.load_positioned_rectangular_member(payload)
