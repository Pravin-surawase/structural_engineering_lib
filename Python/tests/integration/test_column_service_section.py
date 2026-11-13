"""Replay independent column service stresses and signed equilibrium evidence."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import column

CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-sec03-column-service.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("case", CASES)
def test_service_section_matches_frozen_independent_reference(case):
    fixture = CASES[case]
    request = column.load_service_section(json.dumps(fixture["request"]))
    result = column.check_service_section(request)
    wire = result.to_dict()
    assert result.engineering_status.value == fixture["status"]
    assert wire["calculation"]["member_acceptance"] == "NOT_EVALUATED"
    assert wire["calculation"]["detailing_acceptance"] == "NOT_EVALUATED"
    state = wire["calculation"]["section_state"]
    expected = fixture["expected"]
    assert state["properties"] == pytest.approx(
        expected["properties"], rel=1e-7, abs=0.001
    )
    for name in (
        "strain_at_centroid",
        "strain_gradient_x_per_mm",
        "strain_gradient_y_per_mm",
        "max_concrete_compression_nmm2",
    ):
        assert state[name] == pytest.approx(expected[name], rel=1e-7, abs=1e-13)

    b, depth = (
        (request.geometry.diameter_mm, request.geometry.diameter_mm)
        if request.geometry.shape == "circular"
        else (request.geometry.b_mm, request.geometry.D_mm)
    )
    reconstructed = state["gross_concrete_actions"].copy()
    for item, original in zip(state["bars"], request.bars, strict=True):
        assert item["bar"] == original.model_dump(mode="json")
        strain = expected["bar_strains"][original.bar_id]
        assert item["strain"] == pytest.approx(strain, abs=5e-12)
        assert item["steel_stress_nmm2"] == pytest.approx(
            request.moduli.es_nmm2 * strain, abs=1e-6
        )
        force = item["net_axial_kn"]
        reconstructed["p_kn"] += force
        reconstructed["mx_knm"] += force * (depth / 2 - original.y_from_top_mm) / 1000
        reconstructed["my_knm"] += force * (b / 2 - original.x_from_left_mm) / 1000
    assert reconstructed == pytest.approx(request.actions.model_dump(), abs=1e-7)
    assert state["equilibrated_actions"] == pytest.approx(reconstructed, abs=1e-8)
    assert max(map(abs, state["residual_actions"].values())) < 1e-7
    identity = wire["envelope"]["result_identity"]["input_hash"]
    report = column.render_service_section_html(result)
    assert identity in report and "<svg" in report
    assert f"<th>{request.bars[0].bar_id}</th>" in report
    assert "Qualified review required" in report
    if case in (
        "biaxial",
        "reflected",
        "outside_linear_range",
        "rectangle_cracked",
        "circle_cracked",
    ):
        assert state["neutral_axis_angle_deg"] == pytest.approx(
            expected["neutral_axis_angle_deg"], abs=1e-6
        )
        assert len(state["neutral_axis_from_top_left_mm"]) == 2
        for x, y in state["neutral_axis_from_top_left_mm"]:
            strain = (
                state["strain_at_centroid"]
                + state["strain_gradient_x_per_mm"] * (x - b / 2)
                + state["strain_gradient_y_per_mm"] * (y - depth / 2)
            )
            assert abs(strain) < 1e-12
    else:
        assert state["neutral_axis_angle_deg"] is None
        assert state["neutral_axis_from_top_left_mm"] == []
    if case == "all_tension":
        assert state["compression_polygon_from_top_left_mm"] == []
    if case == "outside_linear_range":
        assert result.issues[0].code == "COLUMN.SERVICE_CONCRETE_RANGE_HELD"
    json.dumps(wire, allow_nan=False)


def test_service_section_uses_strict_intake_and_holds_beyond_yield():
    request = deepcopy(CASES["all_tension"]["request"])
    request["actions"]["p_kn"] = -1800
    result = column.check_service_section(column.load_service_section(request))
    assert result.engineering_status.value == "HOLD"
    assert [issue.code for issue in result.issues] == [
        "COLUMN.SERVICE_STEEL_RANGE_HELD"
    ]
    request["bars"][1] = request["bars"][0]
    with pytest.raises(column.InputContractError):
        column.load_service_section(request)
