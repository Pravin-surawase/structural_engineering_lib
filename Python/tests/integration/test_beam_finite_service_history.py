"""Check supplied finite-age history and actual layers against frozen values."""

import json
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam

CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-serv02-beam-history.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("name", CASES)
def test_finite_service_history_matches_independent_calculation(name):
    case = CASES[name]
    request = beam.load_finite_service_history(json.dumps(case["request"]))
    result = beam.check_finite_service_history(request)
    wire = result.to_dict()
    assert result.engineering_status.value == case["status"]
    report = beam.render_finite_service_history_html(result)
    assert wire["envelope"]["result_identity"]["input_hash"] in report
    assert "Qualified review required" in report
    state = wire["calculation"]["history"]
    expected = case["expected"]
    if expected is None:
        assert state is None and "History held" in report
        return
    for stage in ("at_finishes", "at_assessment"):
        for quantity, value in expected[stage].items():
            assert state[stage][quantity] == pytest.approx(value, rel=1e-9)
    if "cracks" in expected:
        assert state["deflection_station_mm"] == pytest.approx(
            expected["deflection_station_mm"]
        )
        for quantity in ("initial_total_mm", "initial_sustained_mm"):
            assert state[quantity] == pytest.approx(expected[quantity])
        assert state["deflection"]["outputs"][
            "after_finishes_deflection_mm"
        ] == pytest.approx(expected["after_finishes_mm"])
        for section in state["crack_sections"]:
            fixture = expected["cracks"][section["tension_face"]]
            assert section["neutral_axis_mm"] == pytest.approx(
                fixture["neutral_axis_mm"]
            )
            assert section["surface_strain"] == pytest.approx(fixture["surface_strain"])
            crack = section["crack"]
            width = crack["outputs"]["calculated_crack_width_mm"] if crack else 0
            assert width == pytest.approx(fixture["width_mm"])
        assert "top ·" in report and "0.14198 mm" in report
        return
    for quantity in (
        "initial_total_mm",
        "initial_sustained_mm",
        "flexural_neutral_axis_mm",
        "flexural_surface_strain",
    ):
        assert state[quantity] == pytest.approx(expected[quantity], rel=1e-9)
    assert state["deflection"]["outputs"][
        "after_finishes_deflection_mm"
    ] == pytest.approx(expected["after_finishes_mm"], abs=1e-8)
    assert state["crack"]["outputs"]["calculated_crack_width_mm"] == pytest.approx(
        expected["flexural_width_mm"], abs=1e-8
    )
    assert [bar["bar_id"] for bar in state["flexural_bars"]] == [
        bar.bar_id for bar in request.member.bars
    ]
    if name == "tight_crack_limit":
        assert state["deflection"]["engineering"] == "pass"
        assert state["crack"]["engineering"] == "fail"
        assert (
            wire["calculation"]["instantaneous"]["sections"][0]["crack"]["engineering"]
            == "pass"
        )
    assert "Day 90" in report and "Day 365" in report and "0.16474 mm" in report
    json.dumps(wire, allow_nan=False)
