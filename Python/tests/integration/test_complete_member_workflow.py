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
    # Independent SciPy reference is generated without production imports.
    reference = json.loads(
        (
            Path(__file__).resolve().parents[3]
            / "contracts/structural-engineering/conformance/wp01-per-bar-vectors.json"
        ).read_text(encoding="utf-8")
    )
    expected = next(
        v["expected"] for v in reference["vectors"] if v["id"] == "workflow-001"
    )
    x = expected["neutral_axis_depth_mm"]
    ast, asc = 200 * math.pi, 72 * math.pi
    strain = 0.0035 * (1 - 50 / x)
    assert strain < 0.8 * (415 / 1.15) / 200000
    ratio = strain / 0.002
    displaced = (0.67 / 1.5) * 25 * (2 * ratio - ratio * ratio)
    compression = asc * (200000 * strain - displaced)
    assert 0.36 * 25 * 300 * x + compression == pytest.approx(
        ast * 415 / 1.15, abs=1e-7
    )
    moment = (0.36 * 25 * 300 * x * (450 - 0.42 * x) + compression * 400) / 1e6
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


@pytest.fixture(scope="module")
def multilayer(example):
    return example.run_workflow(multilayer=True)


def test_multilayer_complete_case_and_independent_sls_bbs(
    example, multilayer, tmp_path
):
    result = multilayer.results
    assert result["member"].engineering == "pass"
    assert multilayer.package["issue_state"] == "issue_ready"
    assert multilayer.package["active_approval"] is False
    assert len(multilayer.package["leaves"]) == 27
    assert all(leaf["qualified"] for leaf in multilayer.package["leaves"])
    assert len(multilayer.package_request.schedule.paths) == 43
    assert result["capacity"].outputs["effective_depth_mm"] == 412.5
    assert result["capacity"].outputs["capacity_knm"] == pytest.approx(
        235.95656263285005, abs=1e-7, rel=0
    )
    for name, load in (("ULS", 36), ("SLS", 24)):
        for row in result[f"analysis-{name}"].outputs["stations"]:
            x = row["x_mm"]
            assert row["m3_nmm"] == pytest.approx(load * x * (5000 - x) / 2, abs=1e-7)
            assert abs(row["v2_n"]) == pytest.approx(abs(load * (2500 - x)), abs=1e-8)
    # Solve the transformed-section first moment independently, then sum each
    # row's second moment. Both top layers lie inside this cracked neutral axis.
    layers = [
        (2 * math.pi * 25**2 / 4, 450, 8),
        (2 * math.pi * 25**2 / 4, 375, 8),
        (2 * math.pi * 16**2 / 4, 50, 7),
        (2 * math.pi * 12**2 / 4, 125, 7),
    ]
    q = sum(n * area for area, y, n in layers)
    first = sum(n * area * y for area, y, n in layers)
    x = (-q + math.sqrt(q * q + 600 * first)) / 300
    assert x > 125
    inertia = 300 * x**3 / 3 + sum(n * area * (y - x) ** 2 for area, y, n in layers)
    stress = 75e6 * 8 * (412.5 - x) / inertia
    surface = 75e6 * (500 - x) / (25000 * inertia)
    distance = math.hypot(100, 50) - 12.5
    width = 3 * distance * surface / (1 + 2 * (distance - 37.5) / (500 - x))
    crack = result["crack"].outputs
    assert crack["neutral_axis_depth_mm"] == pytest.approx(x, abs=1e-9)
    assert crack["service_steel_stress_n_per_mm2"] == pytest.approx(stress, abs=1e-9)
    assert crack["calculated_crack_width_mm"] == pytest.approx(width, abs=1e-10)
    assert result["deflection"].outputs["actual_span_depth_ratio"] == 5000 / 412.5
    link_length = (
        2 * 100 + 2 * 442 + 242 + math.hypot(242, 10) + 100 * (math.pi / 2 - 2)
    )
    mass = (
        (
            5350 * sum(area for area, y, n in layers)
            + 35 * link_length * math.pi * 8**2 / 4
        )
        * 7850
        / 1e9
    )
    assert multilayer.package_request.bbs.scheduled_steel_mass_kg == pytest.approx(mass)
    assert multilayer.package_request.quantities.concrete_volume_m3 == pytest.approx(
        0.81
    )
    for bar in ("B1", "B2", "B3", "B4"):
        for side in ("left", "right"):
            anchorage = result[f"anchorage-{bar}-{side}"].outputs["checks"][0]
            assert anchorage["required_development_length_mm"] == pytest.approx(
                25 * 0.87 * 415 / (4 * 1.4 * 1.6)
            )
            assert anchorage["available_for_criterion_mm"] == 1125
    example.write_artifacts(multilayer, tmp_path)
    saved = json.loads((tmp_path / "calculation.json").read_text(encoding="utf-8"))
    assert (
        saved["results"]["capacity"]["outputs"]["bar_responses"]
        == result["capacity"].outputs["bar_responses"]
    )
    report = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert "All 27 required checks" in report
    assert "Per-bar section equilibrium" in report
    with (tmp_path / "bbs.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 43
    assert {row["issue_state"] for row in rows} == {"issue_ready"}


MULTILAYER_LEAVES = [
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
]
MULTILAYER_LEAVES += [
    f"anchorage-{bar}-{side}"
    for bar in ("B1", "B2", "B3", "B4", "T1", "T2", "T3", "T4")
    for side in ("left", "right")
]


@pytest.mark.parametrize("missing", MULTILAYER_LEAVES)
def test_multilayer_missing_required_evidence_stays_draft(example, missing):
    workflow = example.run_workflow(multilayer=True, omit_checks=(missing,))
    assert workflow.results["member"].engineering == "not_evaluated"
    assert workflow.package["issue_state"] == "draft"
    assert len(workflow.package["leaves"]) == 27
    leaf_id = next(
        key for key, value in workflow.leaf_results.items() if value == missing
    )
    assert not next(
        leaf for leaf in workflow.package["leaves"] if leaf["leaf_id"] == leaf_id
    )["qualified"]


@pytest.mark.parametrize(
    "probe", [{"ultimate_load_n_per_mm": 90}, {"left_bar_end_mm": 195}]
)
def test_multilayer_failed_engineering_stays_draft(example, probe, tmp_path):
    workflow = example.run_workflow(multilayer=True, **probe)
    assert workflow.results["member"].engineering == "fail"
    assert workflow.package["issue_state"] == "draft"
    example.write_artifacts(workflow, tmp_path)
    assert "ISSUE_READY" not in (tmp_path / "report.html").read_text(encoding="utf-8")
    with (tmp_path / "bbs.csv").open(encoding="utf-8", newline="") as stream:
        assert {row["issue_state"] for row in csv.DictReader(stream)} == {"draft"}
