"""Exercise both public section operations against independent frozen values."""

import json
import math
import runpy
from dataclasses import replace
from pathlib import Path

import pytest

from structural_lib import beam

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/beam_section_closure.py"))
FIXTURE = json.loads(
    (ROOT / "docs/verification/library-027-beam-section-closure.json").read_text()
)


def _group(group, group_id):
    if group is None:
        return None
    return beam.SectionShearReinforcement(
        group_id,
        math.fsum(math.pi * diameter**2 / 4 for diameter in group["diameters_mm"]),
        group["fy_nmm2"],
        group["angle_deg"],
        group["spacing_mm"],
    )


def _request(case):
    section = FIXTURE["shear_section"]
    return beam.SuppliedSectionShearRequest(
        case["id"],
        section["web_width_mm"],
        section["effective_depth_mm"],
        section["fck_nmm2"],
        section["longitudinal_area_mm2"],
        _group(case["stirrups"], "stirrups"),
        _group(case["bent_up_bars"], "bent"),
    )


@pytest.mark.parametrize("case", FIXTURE["shear_cases"], ids=lambda case: case["id"])
def test_public_supplied_shear_reference(case):
    result = beam.supplied_section_shear_capacity(_request(case))
    assert result.execution == "completed"
    assert result.engineering == case["engineering"]
    assert result.provenance.method_revision_id == "is456-supplied-section-shear-v1"
    for key, expected in case["expected"].items():
        assert result.outputs[key] == pytest.approx(
            expected, rel=0, abs=FIXTURE["shear_abs_tolerances"][key]
        )
    assert result.outputs["longitudinal_percentage_actual"] == 1.0
    if case["id"].endswith("_only"):
        assert {d.code for d in result.diagnostics} == {
            "SHEAR.MINIMUM_REINFORCEMENT",
            "SHEAR.BENT_UP_LIMIT",
        }


def test_vertical_and_inclined_spacing_and_minimum_provision():
    request = _request(FIXTURE["shear_cases"][0])
    vertical = replace(request.stirrups, spacing_mm=250)
    request = replace(request, effective_depth_mm=300, stirrups=vertical)
    vertical_result = beam.supplied_section_shear_capacity(request)
    assert vertical_result.outputs["stirrup_maximum_spacing_mm"] == 225
    assert {d.code for d in vertical_result.diagnostics} == {"SHEAR.SPACING"}
    inclined = replace(vertical, inclination_deg=45)
    inclined_result = beam.supplied_section_shear_capacity(
        replace(request, stirrups=inclined)
    )
    assert inclined_result.outputs["stirrup_maximum_spacing_mm"] == 300
    assert inclined_result.engineering == "pass"
    too_small = replace(inclined, area_mm2=50)
    result = beam.supplied_section_shear_capacity(replace(request, stirrups=too_small))
    assert {d.code for d in result.diagnostics} == {"SHEAR.MINIMUM_REINFORCEMENT"}


@pytest.mark.parametrize(
    "changes",
    [
        {"inclination_deg": 60},
        {"spacing_mm": None},
        {"spacing_mm": 0},
        {"area_mm2": float("nan")},
    ],
)
def test_invalid_stirrup_group_returns_rejected_input(changes):
    request = _request(FIXTURE["shear_cases"][0])
    request = replace(request, stirrups=replace(request.stirrups, **changes))
    result = beam.supplied_section_shear_capacity(request)
    assert result.execution == "rejected_input"
    assert result.engineering == "not_evaluated"
    assert not result.outputs
    assert {d.code for d in result.diagnostics} == {"INPUT.RANGE"}


def test_same_reinforcement_cannot_be_counted_twice():
    request = _request(
        next(
            case
            for case in FIXTURE["shear_cases"]
            if case["id"] == "vertical_and_single"
        )
    )
    bent = replace(request.bent_up_bars, group_id=request.stirrups.group_id)
    result = beam.supplied_section_shear_capacity(replace(request, bent_up_bars=bent))
    assert result.execution == "rejected_input"
    assert {d.code for d in result.diagnostics} == {"INPUT.CONFLICT"}


@pytest.mark.parametrize("case", FIXTURE["flanged_cases"], ids=lambda case: case["id"])
def test_public_sagging_flange_reference(case):
    section = FIXTURE["flanged_section"]
    df = case["flange_thickness_mm"]
    result = EXAMPLE["sagging_section"](
        df,
        web_width_mm=section["bw_mm"],
        flange_width_mm=section["bf_mm"],
        depth_mm=section["depth_mm"],
        fck_nmm2=section["fck_nmm2"],
        fy_nmm2=section["fy_nmm2"],
        tension_layers=tuple(
            (layer["y_mm"], tuple(layer["diameters_mm"]))
            for layer in section["tension_layers"]
        ),
    )
    if case["branch"] == "rounded_force_gap":
        assert result.applicability == "not_applicable"
        assert result.engineering == "not_evaluated"
        assert not result.outputs
        assert {d.code for d in result.diagnostics} == {"FLEXURE.FLANGE_FORCE_GAP"}
        return
    assert result.engineering == "pass"
    for key, expected in case["expected"].items():
        assert result.outputs[key] == pytest.approx(
            expected, rel=0, abs=FIXTURE["flanged_abs_tolerances"][key]
        )
    x = result.outputs["equilibrium_neutral_axis_depth_mm"]
    branch = (
        "within_flange"
        if x <= df
        else ("web_full_flange" if df / x <= 0.43 else "web_reduced_flange")
    )
    assert branch == case["branch"]
    assert result.outputs["force_residual_n"] == pytest.approx(0, abs=1e-6)


def test_example_prints_scoped_results(capsys):
    EXAMPLE["main"]()
    payload = json.loads(capsys.readouterr().out)
    assert payload["shear"]["inclined"]["engineering"] == "pass"
    assert payload["shear"]["inclined_and_over_limit_repeated"]["engineering"] == "fail"
    assert payload["flexure"]["web_full_flange"]["provenance"][
        "method_revision_id"
    ] == ("is456-flexural-capacity-flanged-web-v1")
