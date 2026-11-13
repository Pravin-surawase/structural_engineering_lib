"""Compare signed BEAM03/04 section results with independent per-bar values."""

import json
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam

CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-beam03-beam04-sections.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("case", CASES)
def test_signed_section_reference(case):
    fixture = CASES[case]
    request = fixture["request"]
    if fixture.get("status") == "BLOCKED":
        with pytest.raises(beam.InputContractError, match="overhang"):
            beam.load_section(request)
        return
    result = beam.check_section(beam.load_section(json.dumps(request)))
    if fixture.get("status") == "HOLD":
        assert result.ultimate_status == "HOLD"
        assert result.geometry is None and not result.flexural_sections
        assert result.result_envelope.overall_status.value == "STALE"
        return

    assert result.ultimate_status == "FAIL"
    assert result.effective_flange_width_mm == fixture["effective_flange_width_mm"]
    assert result.geometry is not None
    assert result.geometry.engineering.value == "pass"
    rows = {row.action.row_id: row for row in result.rows}
    assert rows["SAG:SECTION"].section_status == fixture["sagging_status"]
    assert rows["HOG:SECTION"].section_status == fixture["hogging_status"]
    assert rows["SAG:SECTION"].tension_face == "bottom"
    assert rows["HOG:SECTION"].tension_face == "top"
    for face, expected in fixture["sections"].items():
        values = result.flexural_sections[face].outputs
        for output, key in (
            ("equilibrium_neutral_axis_depth_mm", "neutral_axis_mm"),
            ("limiting_neutral_axis_depth_mm", "limiting_neutral_axis_mm"),
            ("effective_depth_mm", "effective_depth_mm"),
            ("capacity_knm", "capacity_knm"),
            ("concrete_compression_force_n", "concrete_compression_force_n"),
            ("tension_steel_area_mm2", "tension_area_mm2"),
        ):
            assert values[output] == pytest.approx(expected[key], rel=1e-8)
        for key in ("uses_compression_flange", "over_reinforced"):
            assert values[key] is expected[key]
        assert abs(values["force_residual_n"]) < 1e-6
        shear = result.shear_sections[face]
        assert (
            shear.effective_inputs["web_width_mm"]["value"]
            == expected["shear_web_width_mm"]
        )
        assert shear.outputs["provided_capacity_kn"] == pytest.approx(
            expected["shear_capacity_kn"]
        )
        bar_states = {bar["bar_id"]: bar for bar in values["bar_responses"]}
        assert set(bar_states) == set(expected["bar_strains"])
        for bar in request["bars"]:
            state = bar_states[bar["bar_id"]]
            assert state["layer"] == bar["layer"]
            assert state["strain"] == pytest.approx(
                expected["bar_strains"][bar["bar_id"]]
            )
            assert state["net_force_n"] == pytest.approx(
                expected["bar_net_forces_n"][bar["bar_id"]]
            )
    report = beam.render_section_html(result)
    identity = result.to_dict()["result_envelope"]["result_identity"]["input_hash"]
    assert identity in report
    assert all(bar["bar_id"] in report for bar in request["bars"])
    json.dumps(result.to_dict(), allow_nan=False)


def test_section_can_pass_with_only_admitted_sagging_row():
    request = CASES["l"]["request"]
    sagging = {
        **request,
        "actions": [row for row in request["actions"] if row["mu_knm"] > 0],
        "combinations": [
            combo
            for combo in request["combinations"]
            if combo["combination_id"] == "SAG"
        ],
    }
    result = beam.check_section(beam.load_section(sagging))
    assert result.ultimate_status == "PASS"
