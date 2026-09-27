"""Independent frozen-case arithmetic and the public input-to-artifact journey."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def example():
    script = (
        Path(__file__).resolve().parents[2] / "examples" / "complete_member_workflow.py"
    )
    spec = importlib.util.spec_from_file_location("complete_member_workflow", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def workflow(example):
    return example.run_workflow()


def test_complete_case_preserves_all_checks_physical_bars_and_artifact_identity(
    example, workflow, tmp_path
):
    assert workflow.results["member"].engineering == "pass"
    assert workflow.package["issue_state"] == "issue_ready"
    assert workflow.package["active_approval"] is False
    assert len(workflow.package["leaves"]) == 19
    assert all(leaf["qualified"] for leaf in workflow.package["leaves"])
    assert {
        leaf["leaf_id"]
        for leaf in workflow.package["leaves"]
        if leaf["leaf_id"].startswith("anchorage@")
    } == {
        f"anchorage@{bar}-{end}"
        for bar in ("B1", "B2", "T1", "T2")
        for end in ("left", "right")
    }
    schedule = workflow.package_request.schedule
    assert len(schedule.paths) == 39  # four longitudinal bars plus 35 hooked stirrups
    assert {path.bar_id for path in schedule.paths} == {
        datum.datum_id for datum in workflow.package_request.drawings[0].data
    }
    assert (
        schedule.detail_revision_id
        == workflow.package_request.member_result.reinforcement_revision_id
    )
    assert (
        schedule.topology_revision_id
        == workflow.package_request.member_result.topology_revision_id
    )
    example.write_artifacts(workflow, tmp_path)
    saved = json.loads((tmp_path / "calculation.json").read_text(encoding="utf-8"))
    assert (
        saved["results"]["member"]["result_id"] == workflow.results["member"].result_id
    )
    assert (
        saved["results"]["package"]["outputs"]["calculation_package"]
        == workflow.package
    )
    with (tmp_path / "bbs.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 39
    assert {row["issue_state"] for row in rows} == {"issue_ready"}
    assert {row["path_result_id"] for row in rows} == {
        workflow.results["paths"].result_id
    }
    assert "ISSUE_READY" in (tmp_path / "report.html").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "missing",
    (
        "geometry",
        "depth",
        "flexure",
        "shear",
        "torsion",
        "deflection",
        "crack",
        "continuity",
        "arrangement",
        "paths",
        "seismic",
        "anchorage-B1-left",
        "anchorage-B1-right",
        "anchorage-B2-left",
        "anchorage-B2-right",
        "anchorage-T1-left",
        "anchorage-T1-right",
        "anchorage-T2-left",
        "anchorage-T2-right",
    ),
)
def test_each_required_missing_check_remains_visible_and_draft(example, missing):
    workflow = example.run_workflow(omit_checks=(missing,))
    assert workflow.results["member"].engineering == "not_evaluated"
    assert workflow.package["issue_state"] == "draft"
    assert len(workflow.package["leaves"]) == 19
    unqualified = [leaf for leaf in workflow.package["leaves"] if not leaf["qualified"]]
    assert len(unqualified) == 1
    assert unqualified[0]["result_id"] is None
    assert "LEAF.MISSING" in unqualified[0]["reason_codes"]


@pytest.mark.parametrize(
    "probe,failing_leaf",
    (
        ({"ultimate_load_n_per_mm": 40}, "flexure@B1"),
        ({"left_bar_end_mm": 195}, "anchorage@B1-left"),
    ),
)
def test_real_engineering_failures_cannot_export_accepted_artifacts(
    example, probe, failing_leaf, tmp_path
):
    workflow = example.run_workflow(**probe)
    assert workflow.results["member"].engineering == "fail"
    assert workflow.package["issue_state"] == "draft"
    leaf = next(
        leaf for leaf in workflow.package["leaves"] if leaf["leaf_id"] == failing_leaf
    )
    assert not leaf["qualified"]
    example.write_artifacts(workflow, tmp_path)
    with (tmp_path / "bbs.csv").open(encoding="utf-8", newline="") as stream:
        assert {row["issue_state"] for row in csv.DictReader(stream)} == {"draft"}
    assert "ISSUE_READY" not in (tmp_path / "report.html").read_text(encoding="utf-8")


def test_independent_statics_and_single_layer_force_equilibrium(workflow):
    for name, load in (("ULS", 12), ("SLS", 8)):
        stations = workflow.results[f"analysis-{name}"].outputs["stations"]
        for row in stations:
            x = row["x_mm"]
            assert row["m3_nmm"] == pytest.approx(load * x * (5000 - x) / 2, abs=1e-7)
            assert abs(row["v2_n"]) == pytest.approx(abs(load * (2500 - x)), abs=1e-8)
    # Independently reduce equilibrium to a quadratic. For this one-layer
    # compression group every individual bar remains elastic, so centroid and
    # per-bar strains coincide. The declared profile deducts 0.446 fck at Asc.
    ast, asc = 2 * math.pi * 20**2 / 4, 2 * math.pi * 12**2 / 4
    force = 0.87 * 415 * ast
    a = 0.36 * 25 * 300
    coefficient = asc * (200000 * 0.0035 - 0.446 * 25) - force
    x = (-coefficient + math.sqrt(coefficient**2 + 4 * a * asc * 700 * 50)) / (2 * a)
    per_bar_strain = 0.0035 * (x - 50) / x
    assert per_bar_strain < 0.00144  # below Fe415's first inelastic point
    compression = asc * (200000 * per_bar_strain - 0.446 * 25)
    moment = (a * x * (450 - 0.42 * x) + compression * 400) / 1e6
    actual = workflow.results["capacity"].outputs
    assert actual["equilibrium_neutral_axis_depth_mm"] == pytest.approx(x, abs=1e-10)
    assert actual["capacity_knm"] == pytest.approx(moment, abs=1e-10)
    assert actual["minimum_tension_steel_area_mm2"] == pytest.approx(
        0.85 * 300 * 450 / 415
    )
    assert actual["maximum_tension_steel_area_mm2"] == 6000


def test_independent_service_section_and_source_limits(workflow):
    # Cracked transformed section from first moments about the neutral axis;
    # compression steel replaces concrete, and tension stiffening is omitted.
    ast, asc = 200 * math.pi, 72 * math.pi
    modular_ratio = 200000 / (5000 * math.sqrt(25))
    q = modular_ratio * ast + (modular_ratio - 1) * asc
    x = (
        -q
        + math.sqrt(
            q * q
            + 2 * 300 * (modular_ratio * ast * 450 + (modular_ratio - 1) * asc * 50)
        )
    ) / 300
    inertia = (
        300 * x**3 / 3
        + modular_ratio * ast * (450 - x) ** 2
        + (modular_ratio - 1) * asc * (x - 50) ** 2
    )
    stress = 25e6 * modular_ratio * (450 - x) / inertia
    surface_strain = stress / 200000 * (500 - x) / (450 - x)
    distance = math.hypot(100, 50) - 10
    width = 3 * distance * surface_strain / (1 + 2 * (distance - 40) / (500 - x))
    output = workflow.results["crack"].outputs
    assert output["neutral_axis_depth_mm"] == pytest.approx(x, abs=1e-10)
    assert output["service_steel_stress_n_per_mm2"] == pytest.approx(stress, abs=1e-10)
    assert output["calculated_crack_width_mm"] == pytest.approx(width, abs=1e-12)
    assert output["limit_mm"] == 0.3
    screening = workflow.results["deflection"].outputs
    assert screening["actual_span_depth_ratio"] == 5000 / 450
    assert screening["allowable_span_depth_ratio"] == 20
    assert screening["result_kind"] == "screening_not_calculated_displacement"


def test_independent_shear_anchorage_and_physical_bbs(workflow):
    # Table 19, M25: (pt=.25%, tau=.36), (pt=.5%, tau=.49).
    pt = 100 * (200 * math.pi) / (300 * 450)
    tau = 0.36 + (pt - 0.25) / 0.25 * (0.49 - 0.36)
    link_area = 2 * math.pi * 8**2 / 4
    resistance = (tau * 300 * 450 + 0.87 * 415 * link_area * 450 / 150) / 1000
    assert workflow.results["shear"].outputs["checks"][0][
        "capacity_kn"
    ] == pytest.approx(resistance)
    assert link_area / (300 * 150) > 0.4 / (0.87 * 415)
    ld = 20 * 0.87 * 415 / (4 * 1.4 * 1.6)
    for side in ("left", "right"):
        check = workflow.results[f"anchorage-B1-{side}"].outputs["checks"][0]
        assert check["required_development_length_mm"] == pytest.approx(ld)
        assert check["available_straight_length_mm"] == 375
        assert check["available_for_criterion_mm"] == 1125
    # Independently sum the seven-vertex polyline and five right-angle fillets.
    # The bottom leg moves 10 mm along the member; it is not a flat closed loop.
    link_length = (
        2 * 100 + 2 * 442 + 242 + math.hypot(242, 10) + 5 * 20 * (math.pi / 2 - 2)
    )
    paths = workflow.package_request.schedule.paths
    for path in paths:
        assert path.developed_centreline_length_mm == pytest.approx(
            link_length if path.bar_mark == "L8" else 5350
        )
        if path.bar_mark == "L8":
            assert path.closed is False
            assert path.segments[0].centreline_length_mm == 80
            assert path.segments[-1].centreline_length_mm == 80
            assert sum(segment.bend_kind == "hook" for segment in path.segments) == 2
    mass = (
        (
            2 * 5350 * (math.pi * 20**2 / 4 + math.pi * 12**2 / 4)
            + 35 * link_length * math.pi * 8**2 / 4
        )
        * 7850
        / 1e9
    )
    assert workflow.package_request.bbs.scheduled_steel_mass_kg == pytest.approx(mass)
    assert workflow.package_request.quantities.concrete_volume_m3 == pytest.approx(0.81)
    assert workflow.package_request.quantities.formwork_area_m2 == pytest.approx(7.08)
