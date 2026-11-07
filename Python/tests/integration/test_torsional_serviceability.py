"""Frozen D3 mechanics, full member admission, and meaningful refusal controls."""

from __future__ import annotations

import csv
import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from structural_lib import beam as b
from structural_lib.codes.is456.beam.torsion_serviceability import (
    lampert_cracked_stiffness,
)

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/physical_torsion_member.py"))
REFERENCE = json.loads(
    (ROOT / "docs/verification/library-027-torsion-serviceability.json").read_text()
)


@pytest.fixture(scope="module")
def workflow():
    return EXAMPLE["run_workflow"](include_serviceability=True)


@pytest.fixture(scope="module")
def service_request(workflow):
    return TypeAdapter(b.TorsionalServiceabilityRequest).validate_python(
        workflow.results["torsional_sls"].effective_inputs["request"]["value"]
    )


def test_frozen_service_values_and_independent_published_example(workflow):
    service = workflow.results["torsional_sls"]
    assert service.engineering == "pass"
    target = REFERENCE["expected"]
    for key in (
        "short_term_neutral_axis_mm",
        "short_term_cracked_inertia_mm4",
        "long_term_neutral_axis_mm",
        "long_term_cracked_inertia_mm4",
        "bottom_steel_stress_nmm2",
        "elastic_tension_surface_strain",
        "lampert_stiffness_nmm2",
        "longitudinal_ratio",
        "transverse_ratio",
        "midspan_relative_twist_rad",
        "edge_torsional_displacement_mm",
    ):
        assert service.outputs[key] == pytest.approx(target[key], rel=1e-12, abs=1e-12)
    deformation = workflow.results["deflection"].outputs
    assert deformation["total_final_deflection_mm"] == pytest.approx(
        target["final_total_edge_deflection_mm"], rel=0, abs=1e-8
    )
    assert deformation["after_finishes_deflection_mm"] == pytest.approx(
        target["after_finishes_edge_deflection_upper_bound_mm"], rel=0, abs=1e-8
    )
    assert deformation["total_limit_mm"] == target["total_limit_mm"]
    assert deformation["after_finishes_limit_mm"] == target["after_finishes_limit_mm"]
    assert workflow.results["crack"].outputs[
        "calculated_crack_width_mm"
    ] == pytest.approx(target["flexural_crack_width_upper_bound_mm"], rel=0, abs=1e-8)
    assert service.outputs["torsional_crack_width_mm"] is None
    assert (
        service.outputs["indirect_torsional_crack_control"]
        == "IS456_ANNEX_B_SERVICE_STRESS_AND_ACTUAL_DETAIL"
    )
    paper = lampert_cracked_stiffness(200000, 434125, 2660, 0.045, 0.015)
    assert paper == pytest.approx(target["paper_stiffness_nmm2"], rel=1e-12)
    assert abs(paper / 1e9 - 104100) < 50
    for key, expected_key in (
        ("primary_tension_stress_nmm2", "wsm_primary_tension_stress_nmm2"),
        ("compression_stress_nmm2", "wsm_primary_compression_stress_nmm2"),
        ("equivalent_shear_stress_nmm2", "wsm_equivalent_shear_stress_nmm2"),
        (
            "full_equivalent_shear_link_stress_nmm2",
            "wsm_full_equivalent_shear_link_stress_nmm2",
        ),
    ):
        assert max(r[key] for r in service.outputs["wsm_rows"]) == pytest.approx(
            target[expected_key], rel=0, abs=1e-8
        )


def test_service_actions_reconstruct_original_concurrent_uls(workflow, service_request):
    request = service_request
    assert request.history.permanent_load_n_per_mm == 5
    assert request.history.permanent_eccentricity_mm == 0
    assert request.history.imposed_load_n_per_mm == 3
    assert request.history.imposed_eccentricity_mm == pytest.approx(400 / 3)
    total = workflow.results["actions-SLS"].outputs["rows"]
    permanent = workflow.results["actions-PERMANENT"].outputs["rows"]
    ultimate = workflow.results["actions"].outputs["rows"]
    for sls, sustained, uls in zip(total, permanent, ultimate, strict=True):
        for key in ("v2_n", "m3_nmm", "t_nmm"):
            assert uls[key] == pytest.approx(1.5 * sls[key], rel=0, abs=1e-8)
        assert sustained["t_nmm"] == 0
        assert (
            len({sls["load_case_id"], sustained["load_case_id"], uls["load_case_id"]})
            == 3
        )
    assert max(abs(r["t_nmm"]) for r in total) == 1e6


def test_all_31_obligations_qualify_without_engineering_approval(workflow):
    member = workflow.results["member"].output_as("member_design", b.MemberDesignOutput)
    assert workflow.d2_status == workflow.d3_status == "PASS"
    assert member.qualified and len(member.leaf_qualifications) == 31
    assert all(q.qualified for q in member.leaf_qualifications)
    package = workflow.results["package"].outputs["calculation_package"]
    assert package["issue_state"] == "issue_ready"
    assert workflow.results["member"].approval == "unreviewed"


def test_strength_pass_does_not_hide_service_stress_failure(tmp_path):
    workflow = EXAMPLE["run_workflow"](include_serviceability=True, load_n_per_mm=21)
    assert workflow.d2_status == "PASS"
    assert workflow.d3_status == "FAIL"
    assert workflow.results["torsional_sls"].engineering == "fail"
    assert (
        max(
            row["compression_stress_nmm2"]
            for row in workflow.results["torsional_sls"].outputs["wsm_rows"]
        )
        > 8.5
    )
    assert workflow.results["member"].engineering == "fail"
    assert (
        workflow.results["package"].outputs["calculation_package"]["issue_state"]
        == "draft"
    )
    EXAMPLE["write_artifacts"](workflow, tmp_path)
    assert "D3 serviceability: FAIL" in (tmp_path / "report.html").read_text()


def test_new_public_schema_and_strict_json_round_trip(workflow, service_request):
    request = service_request
    adapter = TypeAdapter(b.TorsionalServiceabilityRequest)
    assert adapter.json_schema()["properties"]
    restored = adapter.validate_json(adapter.dump_json(request), strict=True)
    assert (
        b.check_torsional_serviceability(restored).result_id
        == workflow.results["torsional_sls"].result_id
    )


@pytest.mark.parametrize(
    "change",
    (
        "history",
        "sustained_torque",
        "long_duration",
        "thermal",
        "nonuniform_shrinkage",
        "support_boundary",
        "asymmetric_receiver",
        "settlement",
        "stale_actions",
        "wrong_row",
        "missing_peak",
        "missing_imposed_time",
        "finite_duration",
        "before_finishes",
    ),
)
def test_missing_or_unsupported_service_basis_retains_hold(service_request, change):
    request = service_request
    history = request.history
    if change == "history":
        request = replace(request, history=None)
    elif change in {
        "sustained_torque",
        "long_duration",
        "thermal",
        "nonuniform_shrinkage",
        "support_boundary",
        "missing_imposed_time",
        "finite_duration",
        "before_finishes",
    }:
        fields = {
            "sustained_torque": {"permanent_eccentricity_mm": 1},
            "long_duration": {"imposed_load_is_transient": False},
            "thermal": {"temperature_effects_applicable": True},
            "nonuniform_shrinkage": {"shrinkage_is_uniform": False},
            "support_boundary": {"receiver_end_boundary": "unknown"},
            "missing_imposed_time": {"imposed_application_age_days": None},
            "finite_duration": {"imposed_application_age_days": 3649},
            "before_finishes": {
                "imposed_application_age_days": 40,
                "imposed_assessment_age_days": 40,
            },
        }[change]
        request = replace(request, history=replace(history, **fields))
    elif change in {"asymmetric_receiver", "settlement"}:
        transfer = request.support_transfer
        support = transfer.supports[0]
        analysis = support.receiver_analysis
        if change == "asymmetric_receiver":
            analysis = replace(
                analysis,
                elements=tuple(
                    replace(e, second_moment_mm4=e.second_moment_mm4 * 1.1)
                    for e in analysis.elements
                ),
            )
        else:
            analysis = replace(
                analysis,
                nodes=tuple(
                    replace(n, vertical_displacement_mm=1) for n in analysis.nodes
                ),
            )
        support = replace(support, receiver_analysis=analysis)
        request = replace(
            request,
            support_transfer=replace(
                transfer, supports=(support, transfer.supports[1])
            ),
        )
    elif change == "stale_actions":
        request = replace(
            request,
            service_actions=replace(
                request.service_actions, freshness=b.FreshnessState.STALE
            ),
        )
    else:
        source = request.service_actions
        rows = [dict(r) for r in source.outputs["rows"]]
        if change == "missing_peak":
            rows = [r for r in rows if r["object_station_mm"] != 2431.372549019608]
        else:
            rows[0]["t_nmm"] *= -1
        request = replace(
            request,
            service_actions=replace(source, outputs={**source.outputs, "rows": rows}),
        )
    assert b.check_torsional_serviceability(request).engineering == "not_evaluated"


@pytest.mark.parametrize("eccentricity", (0, -50))
def test_zero_and_reverse_torsion_complete_the_same_member(eccentricity):
    workflow = EXAMPLE["run_workflow"](
        include_serviceability=True, torsion_eccentricity_mm=eccentricity
    )
    assert workflow.d2_status == workflow.d3_status == "PASS"
    twist = workflow.results["torsional_sls"].outputs["midspan_relative_twist_rad"]
    assert twist == 0 if eccentricity == 0 else twist < 0


def test_full_outputs_reconcile_and_missing_history_cannot_issue(workflow, tmp_path):
    EXAMPLE["write_artifacts"](workflow, tmp_path)
    record = json.loads((tmp_path / "calculation.json").read_text())
    assert record["d2_status"] == record["d3_status"] == "PASS"
    html = (tmp_path / "report.html").read_text()
    assert "D3 serviceability: PASS" in html and "ISSUE_READY" in html
    for qualification in workflow.package_request.member_result.leaf_qualifications:
        assert qualification.expectation.leaf_id in html
    assert f"{REFERENCE['expected']['final_total_edge_deflection_mm']:.9f}" in html
    quantities = workflow.results["quantities"].outputs["quantities"]
    assert quantities["steel_scheduled_mass_kg"] == pytest.approx(
        84.34798360289798, rel=0, abs=1e-8
    )
    assert quantities["concrete_volume_m3"] == 0.72
    assert quantities["formwork_area_m2"] == 6
    assert f"{quantities['steel_scheduled_mass_kg']:.9f}" in html
    with (tmp_path / "bbs.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 54 and {r["issue_state"] for r in rows} == {"issue_ready"}
    for row, path in zip(rows, workflow.package_request.schedule.paths, strict=True):
        assert row["bar_id"] == path.bar_id
        assert float(row["length_mm"]) == path.developed_centreline_length_mm
        assert row["path_result_id"] == workflow.results["paths"].result_id
        assert row["bbs_result_id"] == workflow.results["bbs"].result_id
    held = EXAMPLE["run_workflow"](
        include_serviceability=True, omit_service_history=True
    )
    assert held.d3_status == "HOLD"
    assert not held.results["member"].outputs["member_design"]["qualified"]
    assert (
        held.results["package"].outputs["calculation_package"]["issue_state"] == "draft"
    )
