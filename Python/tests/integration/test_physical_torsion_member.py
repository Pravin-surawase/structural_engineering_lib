"""D2 frozen mechanics/physical checks, actual artifacts, and retained D3 HOLD."""

from __future__ import annotations

import csv
import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from structural_lib import beam as b
from structural_lib.codes.is456.beam.detailing import ordinary_link_anchorage_limits

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/physical_torsion_member.py"))
REFERENCE = json.loads(
    (ROOT / "docs/verification/library-027-torsion-physical.json").read_text(
        encoding="utf-8"
    )
)


@pytest.fixture(scope="module")
def workflow():
    return EXAMPLE["run_workflow"]()


def request_for(workflow, name, request_type):
    return TypeAdapter(request_type).validate_python(
        workflow.results[name].effective_inputs["request"]["value"]
    )


def test_frozen_primary_actions_and_signed_receiver_transfer(workflow):
    assert workflow.d2_status == "PASS"
    target = REFERENCE["expected"]
    rows = workflow.results["actions"].outputs["rows"]
    for row, expected in zip(rows, target["action_rows"], strict=True):
        assert row["object_station_mm"] == expected["station_mm"]
        for key, unit in (("v2", 1000), ("m3", 1e6), ("t", 1e6)):
            source_field = (
                "torsion_knm"
                if key == "t"
                else key + ("_kn" if key == "v2" else "_knm")
            )
            output_field = key + ("_n" if key == "v2" else "_nmm")
            assert row[output_field] / unit == pytest.approx(
                expected[source_field], abs=1e-8, rel=0
            )
        torsion = workflow.results[f"torsion-{row['object_station_mm']}"]
        assert (
            torsion.effective_inputs["action"]["value"]["source_identity"]
            == row["row_id"]
        )
    transfer = workflow.results["support_transfer"]
    assert transfer.engineering == "pass"
    assert transfer.outputs["global_equilibrium_pass"] is True
    for check in transfer.outputs["checks"]:
        assert (
            check["external_torque_knm"] == target["external_torque_reaction_each_knm"]
        )
        assert check["force_kn"] == target["vertical_reaction_each_kn"]
        assert check["receiver_moment_knm"] == pytest.approx(
            target["receiver_peak_moment_knm"], abs=1e-8
        )
        assert check["receiver_shear_kn"] == pytest.approx(
            target["receiver_peak_shear_kn"], abs=1e-8
        )
        assert [
            n["vertical_reaction_n"] / 1000
            for n in check["receiver_analysis"]["outputs"]["nodes"]
        ] == pytest.approx(target["receiver_reactions_kn"], abs=1e-8)
        for owner in ("receiver_geometry", "receiver_flexure", "receiver_shear"):
            assert check[owner]["engineering"] == "pass"


def test_every_face_end_has_full_stress_direct_tension_anchorage(workflow):
    target = REFERENCE["expected"]
    anchors = [r for k, r in workflow.results.items() if k.startswith("anchorage-")]
    assert len(anchors) == 8
    for result in anchors:
        assert result.engineering == "pass"
        path = result.effective_inputs["request"]["value"]["paths"][0]
        assert path["development"]["stress_state"] == "tension"
        assert (
            path["development"]["bar_stress_n_per_mm2"]
            == target["tension_bar_stress_nmm2"]
        )
        check = result.outputs["checks"][0]
        assert check["criterion"] == "direct_development"
        assert check["required_development_length_mm"] == pytest.approx(
            target["tension_development_mm"], abs=1e-8
        )
        assert (
            check["available_straight_length_mm"]
            == target["available_direct_tension_mm"]
        )


def test_full_expected_set_and_d3_hold_survive_d2_pass(workflow):
    member = workflow.results["member"].output_as("member_design", b.MemberDesignOutput)
    assert len(member.expected_leaves) == 29
    assert sum(q.qualified for q in member.leaf_qualifications) == 26
    assert {
        q.expectation.rule_id for q in member.leaf_qualifications if not q.qualified
    } == {"crack", "deflection", "torsional_sls"}
    assert workflow.results["member"].engineering == "not_evaluated"
    assert member.qualified is False
    assert (
        workflow.results["package"].outputs["calculation_package"]["issue_state"]
        == "draft"
    )


def test_paths_hooks_and_all_exports_match_frozen_layout(workflow, tmp_path):
    target = REFERENCE["expected"]
    schedule = workflow.package_request.schedule
    assert len(schedule.paths) == target["physical_path_count"]
    hooks = workflow.results["hooks"]
    assert hooks.engineering == "pass"
    assert len(hooks.outputs["checks"]) == target["link_count"]
    for check in hooks.outputs["checks"]:
        assert check["tails_mm"] == target["actual_link_tails_mm"]
        assert check["minimum_tail_mm"] == target["ordinary_90_tail_minimum_mm"]
    for path in schedule.paths:
        expected = (
            target["link_path_length_mm"]
            if path.role is b.BarPathRole.TRANSVERSE_LINK
            else target["longitudinal_path_length_mm"]
        )
        assert path.developed_centreline_length_mm == pytest.approx(
            expected, abs=1e-8, rel=0
        )
    EXAMPLE["write_artifacts"](workflow, tmp_path)
    payload = json.loads((tmp_path / "calculation.json").read_text(encoding="utf-8"))
    report = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert payload["d2_status"] == "PASS" and payload["d3_status"] == "HOLD"
    assert "D2 PASS" in report and "D3 serviceability: HOLD" in report
    with (tmp_path / "bbs.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(schedule.paths)
    assert {r["issue_state"] for r in rows} == {"draft"}
    for row, path in zip(rows, schedule.paths, strict=True):
        assert row["bar_id"] == path.bar_id
        assert float(row["length_mm"]) == path.developed_centreline_length_mm
        assert row["path_result_id"] == workflow.results["paths"].result_id
        assert row["bbs_result_id"] == workflow.results["bbs"].result_id
    for q in workflow.package_request.member_result.leaf_qualifications:
        assert q.expectation.leaf_id in report
    assert workflow.results["paths"].result_id in report
    assert workflow.results["bbs"].result_id in report


@pytest.mark.parametrize(
    ("controls", "failed"),
    (
        ({"bar_start_mm": 0}, "anchorage-TL-left"),
        ({"hook_tail_node_mm": 112}, "hooks"),
        ({"link_pitch_mm": 125}, "hooks"),
        ({"reverse_right_couple": True}, "support_transfer"),
        ({"receiver_bar_diameter_mm": 6}, "support_transfer"),
        ({"load_n_per_mm": 100}, "flexure"),
    ),
)
def test_inadequate_physical_provision_fails_with_draft_artifacts(controls, failed):
    w = EXAMPLE["run_workflow"](**controls)
    assert w.d2_status == "FAIL"
    assert w.results[failed].engineering == "fail"
    assert w.results["package"].outputs["calculation_package"]["issue_state"] == "draft"


def test_missing_transfer_is_hold_and_cannot_shrink_expected_checks(workflow):
    w = EXAMPLE["run_workflow"](omit_checks=("support_transfer",))
    assert w.d2_status == "HOLD"
    member = w.results["member"].output_as("member_design", b.MemberDesignOutput)
    assert len(member.expected_leaves) == 29
    q = next(
        q
        for q in member.leaf_qualifications
        if q.expectation.rule_id == "support_transfer"
    )
    assert q.reason_codes == ("LEAF.MISSING",)
    req = request_for(workflow, "support_transfer", b.TorsionSupportTransferRequest)
    assert (
        b.check_torsion_support_transfer(replace(req, supports=())).engineering
        == "not_evaluated"
    )


def test_actual_longitudinal_paths_cannot_differ_from_checked_cage(workflow):
    req = request_for(workflow, "hooks", b.ClosedLinkDetailRequest)
    paths = replace(
        req.paths, paths=tuple(p for p in req.paths.paths if p.bar_id != "TL")
    )
    result = b.check_closed_link_detail(replace(req, paths=paths))
    assert result.engineering == "fail"
    assert "LINK.LONGITUDINAL_PATH_BINDING" in {d.code for d in result.diagnostics}


@pytest.mark.parametrize(
    "change", ("wrong_member", "wrong_nodes", "wrong_bars", "wrong_load_case", "stale")
)
def test_receiver_and_source_are_bound_to_actual_scope(workflow, change):
    req = request_for(workflow, "support_transfer", b.TorsionSupportTransferRequest)
    support = req.supports[0]
    if change == "stale":
        req = replace(
            req,
            action_snapshot=replace(
                req.action_snapshot, freshness=b.FreshnessState.STALE
            ),
        )
    else:
        if change == "wrong_member":
            support = replace(
                support,
                receiver_analysis=replace(
                    support.receiver_analysis, model_id="other-member"
                ),
            )
        if change == "wrong_nodes":
            support = replace(
                support,
                receiver_analysis=replace(
                    support.receiver_analysis,
                    nodes=tuple(
                        replace(n, x_mm=n.x_mm + 1)
                        for n in support.receiver_analysis.nodes
                    ),
                ),
            )
        if change == "wrong_load_case":
            support = replace(
                support,
                receiver_analysis=replace(
                    support.receiver_analysis, load_case_id="other-case"
                ),
            )
        if change == "wrong_bars":
            support = replace(
                support,
                receiver_section=replace(
                    support.receiver_section,
                    bars=tuple(
                        replace(p, x_from_left_mm=1500)
                        for p in support.receiver_section.bars
                    ),
                ),
            )
        req = replace(req, supports=(support, req.supports[1]))
    assert b.check_torsion_support_transfer(req).engineering != "pass"


def test_zero_torsion_retains_station_method_compatibility():
    w = EXAMPLE["run_workflow"](torsion_eccentricity_mm=0)
    assert w.d2_status == "PASS"
    for name, result in w.results.items():
        if name.startswith("torsion-"):
            assert result.provenance.method_revision_id == "is456-torsion-check-wp02-v2"


@pytest.mark.parametrize(("angle", "tail"), ((90, 64), (135, 48), (180, 32)))
def test_ordinary_link_source_limits_have_no_seismic_floor(angle, tail):
    assert ordinary_link_anchorage_limits(8, angle) == (tail, 4)


def test_mild_mix_requirements_are_actual_checks(workflow):
    req = request_for(workflow, "durability", b.MildDurabilityRequest)
    for change in (
        {"nominal_cover_mm": 19},
        {"cement_content_kg_per_m3": 299},
        {"cement_content_kg_per_m3": 451},
        {"water_cement_ratio": 0.56},
        {"concrete_grade_nmm2": 19},
    ):
        assert b.check_mild_durability(replace(req, **change)).engineering == "fail"
    assert (
        b.check_mild_durability(replace(req, exposure="severe")).applicability
        == "not_applicable"
    )
    pcc = replace(req, cement_type="portland_calcined_clay_limestone")
    failed = b.check_mild_durability(pcc)
    assert failed.engineering == "fail"
    assert (
        failed.outputs["maximum_water_cement_ratio"]
        == REFERENCE["expected"]["mild_pcc_limestone_water_cement_maximum_ratio"]
    )
    assert (
        b.check_mild_durability(replace(pcc, water_cement_ratio=0.50)).engineering
        == "pass"
    )
    assert (
        b.check_mild_durability(replace(req, cement_type="unknown")).applicability
        == "not_applicable"
    )


def test_opposite_torsion_sign_has_balanced_same_orientation_support_couples():
    workflow = EXAMPLE["run_workflow"](torsion_eccentricity_mm=-50)
    assert workflow.d2_status == "PASS"
    transfer = workflow.results["support_transfer"]
    assert transfer.outputs["global_equilibrium_pass"] is True
    assert [c["external_torque_knm"] for c in transfer.outputs["checks"]] == [1.5, 1.5]
