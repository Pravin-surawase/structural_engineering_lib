"""Packet E independent member references, physical controls and real exports."""

from __future__ import annotations

import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from structural_lib import beam as b
from structural_lib.codes.is456.beam.flanged_serviceability import cracked_t_section

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/t_beam_member.py"))
REPLAY = runpy.run_path(str(ROOT / "docs/verification/replay_library_027_t_member.py"))
REFERENCE = json.loads(
    (ROOT / "docs/verification/library-027-t-beam-member.json").read_text(
        encoding="utf-8"
    )
)


@pytest.fixture(scope="module")
def main_workflow():
    return EXAMPLE["run_workflow"]()


@pytest.mark.parametrize("case", ("main", "width-limited"))
def test_independent_full_member_and_every_export(case, tmp_path, main_workflow):
    workflow = main_workflow if case == "main" else EXAMPLE["run_workflow"](case=case)
    EXAMPLE["write_artifacts"](workflow, tmp_path)
    receipt = REPLAY["reconcile"](tmp_path, REFERENCE, case=case, status="PASS")
    assert receipt["qualified"] == receipt["expected"] == 30
    assert workflow.results["member"].engineering is b.EngineeringState.PASS
    assert (
        workflow.results["member"].completeness
        is b.CompletenessState.COMPLETE_FOR_SCOPE
    )
    REPLAY["replay_public_requests"](tmp_path)
    if case == "main":
        REPLAY["public_controls"](tmp_path)


@pytest.mark.parametrize(
    ("probe", "status", "responsible"),
    (
        ("overload", "FAIL", "flexure"),
        ("insufficient-bars", "FAIL", "flexure"),
        ("service-fail", "FAIL", "crack"),
        ("short-anchor", "FAIL", "anchorage-B1-left"),
        ("short-hook", "FAIL", "hooks"),
        ("missing-support", "HOLD", "action_basis"),
        ("missing-flange", "HOLD", "flange_participation"),
        ("missing-service", "HOLD", "t_serviceability"),
        ("depth-conflict", "FAIL", "action_basis"),
        ("shoulder-bar", "FAIL", "t_geometry"),
        ("end-cover", "FAIL", "t_geometry"),
    ),
)
def test_actual_failure_hold_inputs_survive_all_exports(
    probe, status, responsible, tmp_path
):
    workflow = EXAMPLE["run_workflow"](probe=probe)
    source = workflow.results[responsible]
    assert source.engineering == (
        b.EngineeringState.FAIL
        if status == "FAIL"
        else b.EngineeringState.NOT_EVALUATED
    )
    EXAMPLE["write_artifacts"](workflow, tmp_path)
    REPLAY["reconcile"](tmp_path, REFERENCE, case="main", status=status)
    if probe == "service-fail":
        assert (
            workflow.results["flexure"].engineering
            == workflow.results["shear"].engineering
            == "pass"
        )
        assert workflow.results["crack"].outputs["limit_mm"] == 0.05
        assert workflow.results["member"].engineering == "fail"
    if probe in ("overload", "depth-conflict", "shoulder-bar"):
        # A known failure does not erase other missing/unsupported evidence.
        assert workflow.results["member"].engineering == "not_evaluated"
        assert workflow.results["member"].completeness == "partial"
    if probe == "shoulder-bar":
        geometry = workflow.flange_request.action_basis.geometry
        assert (
            b.resolve_bar_paths(geometry.paths).engineering == "pass"
        )  # rectangular envelope alone
        assert any(d.code == "T_GEOMETRY.BAR_COVER" for d in source.diagnostics)
        assert (
            geometry.bars[0].x_from_left_mm
            < geometry.section.web_left_from_flange_left_mm
        )
    if probe == "insufficient-bars":
        capacity = workflow.results["capacity"].outputs
        assert (
            capacity["tension_steel_area_mm2"]
            < capacity["minimum_tension_steel_area_mm2"]
        )
        assert workflow.member_request.reinforcement_revision_id.startswith("4T8-")
    if probe == "end-cover":
        assert all(
            workflow.results[f"anchorage-{bar}-{side}"].engineering == "pass"
            for bar in ("B1", "B2", "B3", "B4", "T1", "T2")
            for side in ("left", "right")
        )
        assert any(d.code == "T_GEOMETRY.END_COVER" for d in source.diagnostics)


@pytest.mark.parametrize(
    "change",
    (
        "stale_actions",
        "missing_peak",
        "wrong_load",
        "nonzero_torsion",
        "hogging",
        "same_case",
    ),
)
def test_stale_conflicting_or_unadmitted_action_basis_is_hold(main_workflow, change):
    request = main_workflow.flange_request.action_basis
    snapshot = request.total_service_actions
    if change == "stale_actions":
        snapshot = replace(snapshot, freshness=b.FreshnessState.STALE)
    else:
        raw = TypeAdapter(b.RawActionSnapshot).validate_python(
            snapshot.effective_inputs["snapshot"]["value"]
        )
        rows = raw.rows
        if change == "missing_peak":
            rows = tuple(row for row in rows if row.object_station != 3000)
        if change == "wrong_load":
            rows = tuple(replace(row, v2=row.v2 + 100) for row in rows)
        if change == "nonzero_torsion":
            rows = tuple(replace(row, t=1000) for row in rows)
        if change == "hogging":
            rows = tuple(
                replace(row, m3=-1e6) if row.object_station == 3000 else row
                for row in rows
            )
        if change == "same_case":
            rows = tuple(replace(row, load_case_id="ULS") for row in rows)
        snapshot = b.normalize_action_snapshot(replace(raw, rows=rows))
    result = b.check_t_action_basis(replace(request, total_service_actions=snapshot))
    assert result.engineering == "not_evaluated" and result.completeness == "partial"


@pytest.mark.parametrize(
    "change",
    (
        "missing_monolithic",
        "nonmonolithic",
        "parallel_main",
        "missing_strip",
        "asymmetric_adjacency",
        "stale_strip_geometry",
    ),
)
def test_flange_admission_never_waives_missing_or_unsupported_provision(
    main_workflow, change
):
    request = main_workflow.flange_request
    if change == "missing_monolithic":
        request = replace(request, monolithic_reference=None)
    if change == "nonmonolithic":
        request = replace(request, integrally_cast=False)
    if change == "parallel_main":
        request = replace(request, slab_main_direction="parallel_to_beam")
    if change == "missing_strip":
        request = replace(request, strip=None)
    if change == "asymmetric_adjacency":
        request = replace(request, adjacent_clear_distance_right_mm=800)
    if change == "stale_strip_geometry":
        request = replace(
            request, strip=replace(request.strip, parent_geometry_revision_id="old")
        )
    assert b.check_t_flange_participation(request).engineering == "not_evaluated"


def test_actual_insufficient_flange_main_steel_fails_without_software_error(
    main_workflow,
):
    request = main_workflow.flange_request
    strip = request.strip
    paths = replace(
        strip.paths,
        detail_revision_id="slab-insufficient-r1",
        paths=tuple(
            (
                replace(seed, diameter_mm=2)
                if seed.role is b.BarPathRole.FLANGE_TRANSVERSE
                else seed
            )
            for seed in strip.paths.paths
        ),
    )
    failed = b.check_t_flange_participation(
        replace(request, strip=replace(strip, paths=paths))
    )
    assert failed.engineering == "fail"
    assert (
        failed.outputs["strip_main_area_per_m_mm2"]
        < failed.outputs["strip_limits"]["minimum_area_per_m_each_direction_mm2"]
    )


@pytest.mark.parametrize(
    "change", ("extra_bar", "wrong_face_role", "missing_bar", "geometry_revision")
)
def test_global_projection_keeps_exact_current_six_bar_identity(main_workflow, change):
    request = main_workflow.flange_request.action_basis.geometry
    paths = request.paths
    if change == "geometry_revision":
        request = replace(request, expected_geometry_revision_id="old")
    elif change == "extra_bar":
        extra = replace(paths.paths[0], bar_id="UNDECLARED", bar_mark="UNDECLARED")
        request = replace(request, paths=replace(paths, paths=paths.paths + (extra,)))
    elif change == "wrong_face_role":
        request = replace(
            request,
            paths=replace(
                paths,
                paths=(replace(paths.paths[0], role=b.BarPathRole.TOP_LONGITUDINAL),)
                + paths.paths[1:],
            ),
        )
    else:
        request = replace(request, paths=replace(paths, paths=paths.paths[1:]))
    result = b.check_t_geometry(request)
    assert result.engineering != "pass"


def test_projected_web_paths_resolve_and_six_bar_hook_binding_is_exact(main_workflow):
    geometry = main_workflow.results["t_geometry"]
    projected = geometry.output_as("web_paths", b.BarPathRequest)
    assert projected.section_width_mm == 300
    assert projected.coordinate_system.datum_id.endswith(":web")
    assert b.resolve_bar_paths(projected).engineering == "pass"
    assert main_workflow.results["hooks"].engineering == "pass"
    request = TypeAdapter(b.ClosedLinkDetailRequest).validate_python(
        main_workflow.results["hooks"].effective_inputs["request"]["value"]
    )
    missing = replace(
        request,
        arrangement=replace(request.arrangement, bars=request.arrangement.bars[:-1]),
    )
    assert b.check_closed_link_detail(missing).engineering == "fail"
    assert all(
        c["tails_mm"] == [80, 80]
        for c in main_workflow.results["hooks"].outputs["checks"]
    )


def test_zero_torsion_t_disposition_does_not_admit_nonzero_t(main_workflow):
    output = main_workflow.results["torsion"]
    assert (
        output.engineering == "pass"
        and output.outputs["torsion_resistance_computed"] is False
    )
    inputs = output.effective_inputs
    request = TypeAdapter(b.TBeamActionBasisRequest).validate_python(
        inputs["request"]["value"]
    )
    raw = TypeAdapter(b.RawActionSnapshot).validate_python(
        request.ultimate_actions.effective_inputs["snapshot"]["value"]
    )
    torqued = b.normalize_action_snapshot(
        replace(raw, rows=tuple(replace(row, t=1000) for row in raw.rows))
    )
    assert (
        b.check_t_zero_torsion(replace(request, ultimate_actions=torqued)).engineering
        == "not_evaluated"
    )


def test_source_screen_domain_is_not_extrapolated(main_workflow):
    request = main_workflow.service_request
    assert (
        b.check_t_serviceability(replace(request, concrete_grade_nmm2=30)).engineering
        == "not_evaluated"
    )
    assert (
        b.check_t_serviceability(replace(request, crack_limit=None)).engineering
        == "not_evaluated"
    )


def test_elastic_t_na_in_web_and_at_flange_boundary_are_component_references():
    # Independent hand antiderivatives, no engine-generated expected values.
    # At x=Df150: Fc first moment=1000*150²/2; 8As(500-150)=Fc.
    area = 1000 * 150**2 / (2 * 8 * (500 - 150))
    axis, inertia = cracked_t_section(
        300, 1000, 150, 550, ((500, area),), 25000, 200000
    )
    assert axis == pytest.approx(150, abs=1e-10, rel=0)
    assert inertia == pytest.approx(5_062_500_000, abs=1e-3, rel=0)
    # Thin flange: x100 > Df50, concrete first moment4,125,000 mm³.
    axis, inertia = cracked_t_section(
        300, 1000, 50, 550, ((500, 1289.0625),), 25000, 200000
    )
    assert axis == pytest.approx(100, abs=1e-10, rel=0)
    assert inertia == pytest.approx(1_954_166_666.6666667, abs=1e-3, rel=0)
    # These prove the mechanical owner; they do not advertise new fully
    # qualified physical slab/cage/member profiles.
