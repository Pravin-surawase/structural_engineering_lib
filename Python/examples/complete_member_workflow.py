"""LIB-MEMBER-WORKFLOW-001: one frozen ordinary beam, through BBS and report.

Run with the current library build:
    python3 complete_member_workflow.py --output-dir /tmp/complete-beam

The case is retained here so this file also runs against an installed wheel
outside the source tree. This is a qualified worked case, not a general design
profile or professional approval. The acceptance record is in
docs/planning/library-usability-improvement.md. All calculations use public APIs;
the supplied SLS section evidence is independently checked in the workflow tests.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from structural_lib import beam as b
from structural_lib import construction as c
from structural_lib import reporting as r

PROFILE = "LIB-MEMBER-WORKFLOW-001"
MEMBER = "B1"
DETAIL = "continuous-2T20-2T12-L8-r1"
SOURCE = "IS 456:2000 through Amendment 6; frozen LIB-MEMBER-WORKFLOW-001 case"
SOURCE_IDENTITIES = (
    "IS 456:2000 with Amendment 5, reaffirmed 2021; controlled PDF SHA256 "
    "964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
    "IS 456 Amendment 6:2024; controlled PDF SHA256 "
    "4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881",
)

# Frozen before executing any leaf: missing/failed results cannot shrink this set.
RULES = (
    ("geometry", "structural.reinforcement_geometry.evaluate/v1", "is456-wp01-v1"),
    ("depth", "structural.reinforcement.effective_depth/v1", "is456-wp01-v1"),
    ("flexure", "is456.beam.flexure.check/v1", "is456-wp01-v1"),
    ("shear", "is456.beam.shear.check/v1", "is456-wp02-v1"),
    ("torsion", "is456.beam.torsion.check/v1", "is456-wp02-v1"),
    ("deflection", "is456.beam.deflection.check/v1", "is456-wp04-v1"),
    ("crack", "is456.beam.crack_width.check/v1", "is456-wp04-v1"),
    ("anchorage", "is456.beam.anchorage.check/v1", "is456-amd6-wp05-v1"),
    ("continuity", "is456.beam.lap_curtailment.check/v1", "is456-amd6-wp05-v1"),
    (
        "arrangement",
        "structural.reinforcement_arrangement.check/v1",
        "is456-amd6-wp05-v1",
    ),
    (
        "paths",
        "structural.reinforcement_paths.resolve/v1",
        "reinforcement-geometry-wp06-v1",
    ),
    ("seismic", "is456.beam.seismic_detailing.check/v1", "is13920-2016-amd2-wp05-v1"),
)

LEAF_RESULTS = {f"{name}@{MEMBER}": name for name, _, _ in RULES if name != "anchorage"}
LEAF_RESULTS.update(
    {
        f"anchorage@{bar}-{side}": f"anchorage-{bar}-{side}"
        for bar in ("B1", "B2", "T1", "T2")
        for side in ("left", "right")
    }
)

CASE_ADMISSION = (
    "Mild exposure: M25 >= M20; nominal cover 25 >= 20 mm (Tables 5/16). "
    "Specified mix: water/cement <= 0.55 and cement >= 300 kg/m3, 20 mm aggregate.",
    "Lateral restraints at bearings: 5000 <= min(60*300,250*300^2/450) mm (23.3).",
    "Clear span 4600 mm plus d=450 mm exceeds centre span 5000 mm; effective span is 5000 mm (22.2).",
    "Depth 500 mm does not trigger >750 mm side-face reinforcement (26.5.1.3).",
    "All bottom bars extend into both supports; the required one-third fraction is exceeded (26.2.3.3a).",
    "Ordinary shear links use two 90 degree hooks and 80 mm tangent tails >= 8*8 mm (26.2.2.4). "
    "Overlapping closure arcs occupy planes 10 mm apart, greater than the 8 mm bar diameter.",
    "SLS cracked elastic section: Ec=25000, Es=200000 N/mm2; ignore tension concrete, "
    "subtract displaced compression concrete; no tension-stiffening reduction of surface strain.",
    "Fig 4 tension factor conservatively 1.0 for p=0.46542%, fs=96.0373 N/mm2; "
    "no compression/flange enhancement. This is span/depth screening, not calculated deflection.",
    "No axial force, weak-axis moment, torsion, seismic frame role, laps, cutoffs, "
    "support congestion, special fire rating or watertightness requirement in this case.",
)


@dataclass(frozen=True)
class Workflow:
    results: dict[str, b.OperationResult]
    member_request: b.MemberDesignRequest
    package_request: r.CalculationPackageRequest

    @property
    def package(self) -> dict[str, Any]:
        return self.results["package"].outputs["calculation_package"]


def _completed(result: b.OperationResult) -> b.OperationResult:
    if result.execution is not b.ExecutionState.COMPLETED:
        raise ValueError(result.to_dict())
    return result


def _leaf(leaf_id: str, result: b.OperationResult) -> b.MemberLeafEvidence:
    """Copy numerical summaries from the actual check, without changing states."""
    name = LEAF_RESULTS[leaf_id]
    output = result.outputs
    values: dict[str, Any] = {}
    if name == "flexure":
        check = output["checks"][0]
        values = {
            "required_value": check["demand_knm"],
            "supplied_value": check["capacity_knm"],
            "unit": "kNm",
            "governing_utilization": check["utilization"],
        }
    elif name == "shear":
        check = max(output["checks"], key=lambda item: item["utilization"])
        values = {
            "required_value": abs(check["signed_demand_kn"]),
            "supplied_value": check["capacity_kn"],
            "unit": "kN",
            "governing_utilization": check["utilization"],
        }
    elif name.startswith("anchorage-"):
        check = output["checks"][0]
        values = {
            "required_value": check["required_development_length_mm"],
            "supplied_value": check["available_for_criterion_mm"],
            "unit": "mm",
            "governing_utilization": check["utilization"],
        }
    elif name == "crack":
        values = {
            "required_value": output["calculated_crack_width_mm"],
            "supplied_value": output["limit_mm"],
            "unit": "mm",
            "governing_utilization": output["utilization"],
        }
    elif name == "deflection":
        actual, allowed = (
            output["actual_span_depth_ratio"],
            output["allowable_span_depth_ratio"],
        )
        values = {
            "required_value": actual,
            "supplied_value": allowed,
            "unit": "ratio",
            "governing_utilization": actual / allowed,
        }
    return b.MemberLeafEvidence.from_result(leaf_id, result, **values)


def run_workflow(
    *,
    ultimate_load_n_per_mm: float = 12,
    left_bar_end_mm: float = -175,
    omit_checks: tuple[str, ...] = (),
) -> Workflow:
    """Replay the frozen case, with explicit failure/missing-evidence probes.

    Probe parameters are not a general design interface. SLS remains its own
    retained load case when an ultimate overload is tested.
    """
    results: dict[str, b.OperationResult] = {}
    bars = tuple(
        b.BarPosition(name, diameter, x, y, face)
        for name, diameter, x, y, face in (
            ("B1", 20, 50, 450, b.Face.BOTTOM),
            ("B2", 20, 250, 450, b.Face.BOTTOM),
            ("T1", 12, 50, 50, b.Face.TOP),
            ("T2", 12, 250, 50, b.Face.TOP),
        )
    )
    axes = b.LocalAxes(
        "B1-axes", b.Vector3(1, 0, 0), b.Vector3(0, 1, 0), b.Vector3(0, 0, 1)
    )
    results["topology"] = _completed(
        b.define_beam_topology(
            b.BeamTopologyRequest(
                MEMBER,
                axes,
                (
                    b.PhysicalSupport("A", 0, -200, 200),
                    b.PhysicalSupport("B", 5000, 4800, 5200),
                ),
                (
                    b.PhysicalSpan(
                        "S1",
                        "A",
                        "B",
                        450,
                        (b.SectionRegion("R1", "300x500", 0, 5000),),
                    ),
                ),
                (b.AnalysisElementMapping("E1", "S1", 0, 5000),),
            )
        )
    )
    for name, load in (("ULS", ultimate_load_n_per_mm), ("SLS", 8)):
        analysis = _completed(
            b.solve_beam_line(
                b.BeamLineRequest(
                    "B1-simple",
                    name,
                    (
                        b.BeamNode("A", 0, True, False),
                        b.BeamNode("B", 5000, True, False),
                    ),
                    (b.BeamElement("E1", "S1", "A", "B", 25000, 3125000000, -load),),
                    station_intervals=50,
                )
            )
        )
        results[f"analysis-{name}"] = analysis
        results[f"actions-{name}"] = _completed(
            b.normalize_action_snapshot(
                b.RawActionSnapshot(
                    "public-python-beam-line",
                    "B1-simple",
                    analysis.calculation_id,
                    analysis.result_id,
                    b.ForceUnit.N,
                    b.MomentUnit.N_MM,
                    b.LengthUnit.MM,
                    (axes,),
                    tuple(
                        b.RawActionRow(
                            f"{name}-{index}",
                            MEMBER,
                            "S1",
                            MEMBER,
                            "E1",
                            axes.axis_id,
                            station["x_mm"],
                            station["distance_from_start_mm"],
                            name,
                            "static",
                            None,
                            b.ActionConcurrency.STATIC_CONCURRENT,
                            0,
                            station["v2_n"],
                            0,
                            0,
                            0,
                            station["m3_nmm"],
                        )
                        for index, station in enumerate(analysis.outputs["stations"])
                    ),
                )
            )
        )
    uls = results["analysis-ULS"].outputs["stations"]
    moment = max(row["m3_nmm"] for row in uls) / 1e6
    shear = max(abs(row["v2_n"]) for row in uls) / 1000
    geometry = b.ReinforcementGeometryRequest(PROFILE, 300, 500, 25, 8, 25, bars)
    results["geometry"] = b.evaluate_geometry(geometry)
    results["depth"] = b.effective_depth(geometry, b.Face.BOTTOM)
    capacity_request = b.FlexuralCapacityRequest(
        PROFILE, b.SectionKind.RECTANGULAR, 300, 500, 25, 415, bars, b.Face.BOTTOM
    )
    results["capacity"] = b.flexural_capacity(capacity_request)
    capacity = results["capacity"].outputs
    results["flexure"] = b.check_flexure(
        b.FlexureCheckRequest(capacity_request, positive_design_moment_knm=moment)
    )
    link = b.TransverseLink("L8", 8, 2, 2, 150, 415, True, 242, 442)
    results["shear"] = b.check_shear(
        b.ShearCheckRequest(
            (
                b.ShearCapacityRequest(
                    PROFILE,
                    b.ShearAxis.V2,
                    300,
                    450,
                    25,
                    capacity["tension_steel_area_mm2"],
                    link,
                ),
            ),
            tuple(
                b.ShearDemand(f"ULS-{index}", b.ShearAxis.V2, abs(row["v2_n"]) / 1000)
                for index, row in enumerate(uls)
            ),
        )
    )
    # Zero torsion, concurrent with the governing flexural source row.
    results["torsion"] = b.check_torsion(
        b.TorsionCheckRequest(
            PROFILE,
            b.ConcurrentActionRow(
                "ULS-25",
                "S1-mid",
                b.ActionBasis.STATIC_CONCURRENT,
                0,
                0,
                0,
                0,
                moment,
                results["actions-ULS"].result_id,
            ),
            capacity_request,
            link,
            tuple(bar.bar_id for bar in bars),
        )
    )
    results["deflection"] = b.check_deflection(
        b.DeflectionCheckRequest(
            PROFILE,
            b.DeflectionMethod.SPAN_DEPTH_SCREENING,
            screening=b.DeflectionScreeningBasis(
                5000,
                450,
                b.SupportCondition.SIMPLY_SUPPORTED,
                1,
                1,
                1,
                results["topology"].result_id,
                CASE_ADMISSION[7],
            ),
        )
    )
    results["crack"] = b.check_crack_width(
        b.CrackWidthCheckRequest(
            PROFILE,
            MEMBER,
            "S1-mid",
            "SLS-25",
            DETAIL,
            300,
            500,
            104.82470668199647,
            b.Face.BOTTOM,
            bars,
            150,
            96.03729860524084,
            415,
            200000,
            0.0005497433967678369,
            b.CrackWidthLimitRequest(PROFILE, b.ExposureClass.MILD, False),
        )
    )
    for side, face, centre, direction in (
        ("left", 200, 0, b.AnchorageDirection.DECREASING_X),
        ("right", 4800, 5000, b.AnchorageDirection.INCREASING_X),
    ):
        for bar in bars:
            bottom = bar.face is b.Face.BOTTOM
            results[f"anchorage-{bar.bar_id}-{side}"] = b.check_anchorage(
                b.AnchorageCheckRequest(
                    PROFILE,
                    MEMBER,
                    DETAIL,
                    (
                        b.AnchoragePath(
                            bar.bar_id,
                            f"{side}-face" if bottom else "midspan",
                            (
                                b.AnchorageLocation.SIMPLE_SUPPORT
                                if bottom
                                else b.AnchorageLocation.DISCONTINUITY
                            ),
                            direction,
                            left_bar_end_mm,
                            5175,
                            face if bottom else 2500,
                            side if bottom else None,
                            face if bottom else None,
                            centre if bottom else None,
                            (),
                            None,
                            b.DevelopmentLengthRequest(
                                PROFILE,
                                bar.diameter_mm,
                                0.87 * 415,
                                415,
                                25,
                                b.BarSurface.DEFORMED,
                                (
                                    b.StressState.TENSION
                                    if bottom
                                    else b.StressState.COMPRESSION
                                ),
                            ),
                            (
                                b.SimpleSupportAnchorageEvidence(
                                    capacity["capacity_knm"] * 1e6,
                                    shear * 1000,
                                    ("ULS-0" if side == "left" else "ULS-50",),
                                )
                                if bottom
                                else None
                            ),
                        ),
                    ),
                )
            )
    longitudinal = tuple(
        b.LongitudinalBarPath(
            bar.bar_id,
            bar.face.value,
            (
                b.ReinforcementRole.BOTTOM_LONGITUDINAL
                if bar.face is b.Face.BOTTOM
                else b.ReinforcementRole.TOP_LONGITUDINAL
            ),
            bar.diameter_mm,
            1,
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            left_bar_end_mm,
            5175,
            0.87 * 415,
        )
        for bar in bars
    )
    results["continuity"] = b.check_laps_and_curtailment(
        b.LapCurtailmentCheckRequest(
            PROFILE,
            MEMBER,
            "S1",
            results["actions-ULS"].result_id,
            DETAIL,
            200,
            4800,
            450,
            25,
            415,
            b.BarSurface.DEFORMED,
            longitudinal,
            tuple(
                b.StationSteelDemand(
                    f"ULS-{index}",
                    row["x_mm"],
                    b.ReinforcementRole.BOTTOM_LONGITUDINAL,
                    capacity["minimum_tension_steel_area_mm2"],
                    abs(row["v2_n"]),
                    results["shear"].outputs["checks"][index]["capacity_kn"] * 1000,
                    f"ULS-{index}",
                )
                for index, row in enumerate(uls)
                if 200 <= row["x_mm"] <= 4800
            ),
            (),
            (),
        )
    )
    results["arrangement"] = b.check_reinforcement_arrangement(
        b.ReinforcementArrangementCheckRequest(
            PROFILE,
            MEMBER,
            "uniform-section",
            DETAIL,
            300,
            500,
            25,
            20,
            longitudinal,
            (b.LinkCage("L8", 8, 29, 271, 29, 471, 16, True),),
            (
                b.ReinforcementRole.BOTTOM_LONGITUDINAL,
                b.ReinforcementRole.TOP_LONGITUDINAL,
            ),
            1,
        )
    )
    results["seismic"] = b.check_seismic_detailing(
        b.SeismicDetailingCheckRequest(PROFILE, b.SeismicApplicability.ORDINARY_IS456)
    )

    results["project"] = _completed(
        b.create_beam_project(
            b.BeamProjectRequest(
                b.BeamProjectDefinition(
                    PROFILE, "Complete ordinary beam worked case", "r1"
                ),
                b.StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
                tuple(
                    b.RevisionBinding(name, revision, SOURCE)
                    for name, _, revision in RULES
                ),
                b.BeamDesignProfile(
                    PROFILE,
                    "complete-profile-r1",
                    "IS 456:2000",
                    b.SeismicDesignProfile.ORDINARY_IS456,
                    tuple(
                        b.DesignCheckRule(
                            name,
                            operation,
                            (
                                b.CheckScope.BAR_END
                                if name == "anchorage"
                                else b.CheckScope.MEMBER
                            ),
                            (
                                b.ApplicabilityState.NOT_APPLICABLE
                                if name == "seismic"
                                else b.ApplicabilityState.APPLICABLE
                            ),
                            SOURCE,
                            name,
                        )
                        for name, operation, _ in RULES
                    ),
                    (
                        b.DesignCriterion("cover", 25, "mm", CASE_ADMISSION[0]),
                        b.DesignCriterion(
                            "lateral-restraint-spacing", 5000, "mm", CASE_ADMISSION[1]
                        ),
                    ),
                ),
            )
        )
    )
    project = results["project"].output_as("project", b.BeamProject)
    seeds = tuple(
        b.BarPathSeed(
            bar.bar_id,
            bar.face.value,
            (
                b.BarPathRole.BOTTOM_LONGITUDINAL
                if bar.face is b.Face.BOTTOM
                else b.BarPathRole.TOP_LONGITUDINAL
            ),
            1,
            bar.diameter_mm,
            415,
            tuple(
                b.PathNode(
                    str(station),
                    b.PathPoint(station, bar.x_from_left_mm, bar.y_from_top_mm),
                )
                for station in (left_bar_end_mm, 5175)
            ),
        )
        for bar in bars
    )
    # Two 90-degree hooks with 80 mm clear tangent tails, separated by 10 mm
    # along the member. This is an open fabrication path forming a closed cage;
    # it is not an invented welded closed loop. Radii below are centreline radii.
    link_vertices = (
        (0, 129, 29),
        (0, 29, 29),
        (0, 29, 471),
        (10, 271, 471),
        (10, 271, 29),
        (10, 29, 29),
        (10, 29, 129),
    )
    seeds += tuple(
        b.BarPathSeed(
            f"L8-{station}",
            "L8",
            b.BarPathRole.TRANSVERSE_LINK,
            1,
            8,
            415,
            tuple(
                b.PathNode(
                    str(index),
                    b.PathPoint(station + offset, x, y),
                    20 if 0 < index < 6 else None,
                    (
                        (
                            b.BendKind.HOOK
                            if index in (1, 5)
                            else b.BendKind.STANDARD_BEND
                        )
                        if 0 < index < 6
                        else None
                    ),
                )
                for index, (offset, x, y) in enumerate(link_vertices)
            ),
        )
        for station in range(-75, 5026, 150)
    )
    results["paths"] = _completed(
        b.resolve_bar_paths(
            b.BarPathRequest(
                PROFILE,
                project.project_basis_id,
                project.profile.revision_id,
                MEMBER,
                "S1",
                results["topology"].result_id,
                DETAIL,
                b.MemberLocalCoordinateSystem(
                    "B1-local",
                    "member_station_x",
                    "section_x_from_left",
                    "section_y_from_top",
                ),
                -200,
                5200,
                300,
                500,
                seeds,
                (12000,),
            )
        )
    )
    member_request = b.MemberDesignRequest(
        project,
        MEMBER,
        results["topology"].result_id,
        results["actions-ULS"].result_id,
        DETAIL,
        "complete-scope-r1",
        tuple(
            b.MemberScopeInstance(
                f"{bar.bar_id}-{side}", b.CheckScope.BAR_END, "complete-scope-r1"
            )
            for bar in bars
            for side in ("left", "right")
        ),
        (
            b.EffectiveDepthIteration(
                1,
                DETAIL,
                450,
                tuple(
                    results[name].result_id
                    for name in LEAF_RESULTS.values()
                    if name != "seismic"
                ),
                True,
            ),
        ),
        tuple(
            _leaf(leaf_id, results[name])
            for leaf_id, name in LEAF_RESULTS.items()
            if name not in omit_checks
        ),
    )
    results["member"] = b.design_member(member_request)
    schedule = results["paths"].output_as("reinforcement_schedule", b.BarPathOutput)
    schedule_binding = r.result_binding(results["paths"], "reinforcement_schedule")
    results["bbs"] = _completed(
        c.create_bbs(
            c.BbsRequest(
                PROFILE,
                project.project_basis_id,
                MEMBER,
                DETAIL,
                schedule_binding.result_id,
                schedule_binding.output_payload_id,
                schedule,
                c.ShapeConvention("centreline", "r1"),
                c.CuttingStockPolicy("12m-stock", "r1", (12000,), 3, 500),
                7850,
                link_zones=(
                    c.LinkPlacementZone("all-links", "L8", -75, 5025, 150, True, True),
                ),
            )
        )
    )
    bbs = results["bbs"].output_as("bbs", c.BbsOutput)
    bbs_binding = r.result_binding(results["bbs"], "bbs")
    results["quantities"] = _completed(
        c.calculate_construction_quantities(
            c.ConstructionQuantityRequest(
                PROFILE,
                project.project_basis_id,
                MEMBER,
                DETAIL,
                bbs_binding.result_id,
                bbs_binding.output_payload_id,
                bbs,
                "whole-beam-no-overlap",
                "soffit-two-sides-ends-no-bearing-contact",
                (
                    c.ConcreteNetSegment(
                        "concrete", MEMBER, "M25", "B1-volume", 150000, 5400, False
                    ),
                ),
                tuple(
                    c.FormworkContactFace(
                        name,
                        MEMBER,
                        category,
                        f"B1-{name}",
                        area,
                        c.FormworkMeasurementState.INCLUDED,
                    )
                    for name, category, area in (
                        ("soffit", c.FormworkFaceCategory.SOFFIT, 300 * 4600),
                        ("left", c.FormworkFaceCategory.SIDE_LEFT, 500 * 5400),
                        ("right", c.FormworkFaceCategory.SIDE_RIGHT, 500 * 5400),
                        ("ends", c.FormworkFaceCategory.END_BULKHEAD, 2 * 300 * 500),
                    )
                ),
            )
        )
    )
    quantities = results["quantities"].output_as(
        "quantities", c.ConstructionQuantityOutput
    )
    member = results["member"].output_as("member_design", b.MemberDesignOutput)
    package_request = r.CalculationPackageRequest(
        r.CalculationPackageMetadata(
            PROFILE,
            project.project.name,
            "r1",
            MEMBER,
            "r1",
            "python-structural-engineering-v1",
            tuple(binding.revision_id for binding in project.code_data_revisions),
            "2026-09-27T00:00:00+00:00",
        ),
        r.CalculationPackageProfile(
            PROFILE,
            "r1",
            "complete-beam-r1",
            tuple(LEAF_RESULTS),
            (
                "inputs",
                "calculations",
                "reinforcement",
                "quantities",
                "drawings",
                "signatures",
            ),
        ),
        member,
        r.result_binding(results["member"], "member_design"),
        schedule,
        schedule_binding,
        bbs,
        bbs_binding,
        quantities,
        r.result_binding(results["quantities"], "quantities"),
        None,
        None,
        CASE_ADMISSION + SOURCE_IDENTITIES,
        tuple(
            r.CalculationTrace(
                f"trace-{item.expectation.leaf_id}",
                item.expectation.leaf_id,
                "; ".join(
                    results[
                        LEAF_RESULTS[item.expectation.leaf_id]
                    ].provenance.source_references
                ),
                results[
                    LEAF_RESULTS[item.expectation.leaf_id]
                ].provenance.method_revision_id,
                json.dumps(
                    results[LEAF_RESULTS[item.expectation.leaf_id]].effective_inputs,
                    sort_keys=True,
                ),
                item.evidence.required_value if item.evidence else None,
                item.evidence.supplied_value if item.evidence else None,
                item.evidence.selected_value if item.evidence else None,
                item.evidence.unit if item.evidence else None,
                item.evidence.governing_utilization if item.evidence else None,
                member.governing_leaf_id == item.expectation.leaf_id,
            )
            for item in member.leaf_qualifications
        ),
        (
            r.DrawingView(
                "physical-paths",
                "bar_schedule",
                DETAIL,
                tuple(
                    r.DrawingDatum(
                        bar.bar_id,
                        results["paths"].result_id,
                        bar.bar_mark,
                        str(bar.developed_centreline_length_mm),
                        "mm",
                    )
                    for bar in schedule.paths
                ),
            ),
        ),
        (
            "One frozen ordinary beam with the stated source inputs and case-admission evidence.",
            "Centroid flexure with conservative displaced-concrete deduction; not a general multilayer strain solver.",
            "Span/depth screening does not report calculated long-term displacement.",
            "Engineering/package readiness is separate from professional approval and construction issue.",
        ),
    )
    results["package"] = _completed(r.create_calculation_package(package_request))
    return Workflow(results, member_request, package_request)


def write_artifacts(workflow: Workflow, output_dir: Path) -> None:
    """Render the unchanged semantic package; all artifacts retain its issue state."""
    output_dir.mkdir(parents=True, exist_ok=True)
    package = workflow.package
    payload = {
        "case_admission": CASE_ADMISSION,
        "source_identities": SOURCE_IDENTITIES,
        "results": {
            name: result.to_dict() for name, result in workflow.results.items()
        },
    }
    (output_dir / "calculation.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    schedule = workflow.package_request.schedule
    bbs = workflow.package_request.bbs
    bbs_by_path = {path_id: row for row in bbs.rows for path_id in row.source_path_ids}
    with (output_dir / "bbs.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            (
                "issue_state",
                "bar_id",
                "mark",
                "diameter_mm",
                "length_mm",
                "fabrication_cut_length_mm",
                "shape_code",
                "path_result_id",
                "bbs_result_id",
            )
        )
        for bar in schedule.paths:
            bbs_row = bbs_by_path[bar.bar_id]
            writer.writerow(
                (
                    package["issue_state"],
                    bar.bar_id,
                    bar.bar_mark,
                    bar.diameter_mm,
                    bar.developed_centreline_length_mm,
                    bbs_row.fabrication_cut_length_each_mm,
                    bbs_row.shape_code,
                    workflow.results["paths"].result_id,
                    workflow.results["bbs"].result_id,
                )
            )

    def number(value: float | None) -> str:
        return "—" if value is None else f"{value:.3f}"

    rows = "".join(
        f"<tr><td>{html.escape(leaf['leaf_id'])}</td><td>"
        f"{'qualified' if leaf['qualified'] else 'unqualified'}</td><td>"
        f"{number(leaf['required_value'])}</td><td>{number(leaf['provided_value'])}</td><td>{leaf['unit'] or ''}</td><td>"
        f"{html.escape(', '.join(leaf['reason_codes']))}</td></tr>"
        for leaf in package["leaves"]
    )
    bar_rows = "".join(
        f"<tr><td>{html.escape(row.bar_mark)}</td><td>{row.diameter_mm:g}</td>"
        f"<td>{row.scheduled_bar_count}</td><td>{row.fabrication_cut_length_each_mm:.3f}</td>"
        f"<td>{row.theoretical_mass_kg:.3f}</td></tr>"
        for row in bbs.rows
    )
    admission = "".join(f"<li>{html.escape(item)}</li>" for item in CASE_ADMISSION)
    quantities = workflow.package_request.quantities
    flexure = workflow.results["flexure"].outputs["checks"][0]
    shear = max(
        workflow.results["shear"].outputs["checks"],
        key=lambda item: item["utilization"],
    )
    document = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>B1 calculation report</title><style>body{{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 24px}}
td,th{{text-align:left;padding:8px;border-bottom:1px solid #ddd}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}
</style><h1>B1 — {html.escape(package['issue_state'].upper())}</h1>
<p>300 × 500 mm, 5 m span, M25 / Fe415. Professional approval: none.</p>
<p>Member engineering state: <strong>{html.escape(str(workflow.results['member'].engineering))}</strong>.
ULS moment {flexure['demand_knm']:.3f} kNm; ULS shear {abs(shear['signed_demand_kn']):.3f} kN.
SLS midspan moment 25 kNm. Bottom 2T20, top 2T12, two-leg 8 mm links at 150 mm.</p>
<h2>Frozen inputs and admission</h2><ul>{admission}</ul>
<h2>All 19 required checks</h2>
<p>ULS and SLS are separate cases. Values below are demand/limit comparisons; inspect the retained effective inputs.</p>
<p>Anchorage compares Ld with the equivalent available length, including three times actual support extension.
An ordinary seismic non-applicability result is explicitly qualified. Blank numerical cells use the retained geometric or identity checks.</p>
<table><tr><th>Required check</th><th>Qualification</th><th>Demand</th><th>Capacity/limit</th><th>Unit</th><th>Reason</th></tr>{rows}</table>
<h2>Physical bar schedule</h2>
<table><tr><th>Mark</th><th>Diameter (mm)</th><th>Count</th><th>Cut length each (mm)</th><th>Mass (kg)</th></tr>{bar_rows}</table>
<p>Scheduled steel {bbs.scheduled_steel_mass_kg:.3f} kg; concrete {quantities.concrete_volume_m3:.3f} m³;
formwork {quantities.formwork_area_m2:.3f} m². Exact paths, bends, hooks, stock allocation and measurement policies remain in the package.</p>
<p><a href="calculation.json">Download all calculations and inputs</a> · <a href="bbs.csv">Download physical bar rows</a>.
Both files carry the package issue state. These files do not supply professional approval or fabrication drawings.</p>
<details><summary>Retained package: sources, inputs, calculations, paths and identities</summary>
<pre>{html.escape(json.dumps(package, indent=2))}</pre></details></html>"""
    (output_dir / "report.html").write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    workflow = run_workflow()
    if args.output_dir:
        write_artifacts(workflow, args.output_dir)
    print(
        json.dumps(
            {
                "member": workflow.results["member"].engineering,
                "issue_state": workflow.package["issue_state"],
                "required_checks": len(LEAF_RESULTS),
                "physical_bars": len(workflow.package_request.schedule.paths),
                "steel_kg": workflow.package_request.bbs.scheduled_steel_mass_kg,
                "professional_approval": workflow.package["active_approval"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
