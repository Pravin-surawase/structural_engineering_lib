"""Replay the independent instantaneous response under declared service loads."""

import json
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam

CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-serv01-beam-service.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("name", CASES)
def test_instantaneous_service_agrees_with_independent_response(name):
    case = CASES[name]
    request = beam.load_instantaneous_service(json.dumps(case["request"]))
    result = beam.check_instantaneous_service(request)
    wire = result.to_dict()
    assert wire["calculation"]["long_term_status"] == "HOLD"
    report = beam.render_instantaneous_service_html(result)
    assert wire["envelope"]["result_identity"]["input_hash"] in report
    assert "Long-term HOLD" in report and "Qualified review required" in report
    expected = case["expected"]
    if expected is None:
        assert result.engineering_status.value == "HOLD"
        assert wire["calculation"]["instantaneous"] is None
        if name == "stale_reinforcement":
            assert wire["envelope"]["freshness_status"] == "STALE"
        return
    assert result.engineering_status.value == (
        "FAIL" if name.endswith("tight_limit") else "PASS"
    )
    response = wire["calculation"]["instantaneous"]
    assert response["deflection_mm"] == pytest.approx(
        expected["maximum_deflection_mm"], abs=1e-8
    )
    x = response["deflection_x_mm"]
    if x > request.span_mm:
        x = 2 * request.span_mm - x
    assert x == pytest.approx(expected["maximum_deflection_x_mm"], abs=1e-6)
    assert (
        abs(response["analysis"]["outputs"]["equilibrium"]["force_residual_n"]) < 1e-6
    )
    for actual, reference, moment in zip(
        response["sections"],
        [expected[key] for key in ("midpoint", "support") if expected[key] is not None],
        [expected["midpoint_moment_knm"]]
        + ([expected["support_centre_moment_knm"]] if expected["support"] else []),
        strict=True,
    ):
        assert actual["moment_knm"] == pytest.approx(moment, abs=1e-8)
        assert actual["tension_face"] == reference["tension_face"]
        for key in ("cracking_moment_knm", "neutral_axis_mm", "cracked_inertia_mm4"):
            assert actual[key] == pytest.approx(reference[key], rel=1e-10)
        assert actual["crack"]["outputs"]["calculated_crack_width_mm"] == pytest.approx(
            reference["width_mm"], abs=1e-8
        )
        assert [bar["bar_id"] for bar in actual["bars"]] == [
            bar.bar_id for bar in request.member.bars
        ]
    json.dumps(wire, allow_nan=False)
