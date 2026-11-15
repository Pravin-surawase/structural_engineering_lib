"""Replay the independent instantaneous response under declared service loads."""

import json
from copy import deepcopy
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


@pytest.mark.parametrize(
    "vertical,horizontal,passes",
    (
        (14.9, 18.5, False),
        (15.0, 18.5, True),
        (16.0, 18.5, True),
        (16.0, 17.4, False),
        (16.0, 17.5, True),
    ),
)
def test_directional_spacing_in_section_and_service(vertical, horizontal, passes):
    payload = deepcopy(CASES["multilayer"]["request"])
    member = payload["member"]
    member.update(
        width_mm=230,
        depth_mm=450,
        aggregate_size_mm=12.5,
        link_diameter_mm=10,
        link_spacing_mm=250,
        fck_nmm2=25,
        fy_nmm2=415,
    )
    bottom_x = [115 + (i - 2) * (12 + horizontal) for i in range(5)]
    member["bars"] = [
        {
            "bar_id": f"{face}-{layer}-{index}",
            "diameter_mm": 12,
            "face": face,
            "layer": layer,
            "x_from_left_mm": x,
            "y_from_top_mm": y,
        }
        for face, layer, y, xs in (
            ("top", 1, 47, (80, 150)),
            ("bottom", 1, 400, bottom_x),
            ("bottom", 2, 400 - 12 - vertical, bottom_x),
        )
        for index, x in enumerate(xs)
    ]
    payload["span_mm"] = 5000
    payload["service_load"]["uniform_load_kn_per_m"] = 25
    section = beam.check_section(beam.load_section(member))
    instantaneous = beam.check_instantaneous_service(
        beam.load_instantaneous_service(payload)
    )
    assert section.geometry.engineering == ("pass" if passes else "fail")
    assert (instantaneous.calculation["instantaneous"] is not None) is passes
    if not passes:
        direction = "Vertical" if vertical < 15 else "Horizontal"
        assert any(direction in item.message for item in section.geometry.diagnostics)

    if (vertical, horizontal) == (16.0, 18.5):
        payload["schema_version"] = "is456-beam-finite-service-history-input/v1"
        payload["history"] = {
            "sustained_load": {
                **payload["service_load"],
                "combination_id": "SLS-SUSTAINED",
                "uniform_load_kn_per_m": 15,
            },
            "loading_age_days": 28,
            "at_finishes": {
                "age_days": 90,
                "creep_coefficient": 1.0,
                "shrinkage_strain": 0.0001,
            },
            "at_assessment": {
                "age_days": 365,
                "creep_coefficient": 1.5,
                "shrinkage_strain": 0.0002,
            },
            "relative_humidity_percent": 60,
            "notional_size_mm": 150,
            "finish_added_load_kn_per_m": 0,
            "source_reference": "Synthetic finite-age admission check on the 5+5 cage",
            "bending_basis": "downward_gravity",
        }
        finite = beam.check_finite_service_history(
            beam.load_finite_service_history(payload)
        )
        assert finite.calculation["history"] is not None
