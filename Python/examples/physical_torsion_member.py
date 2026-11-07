"""Run the frozen D2 physical torsion member; D3 serviceability stays HOLD.

Standalone base-install example. Run with --output-dir to write bound draft
JSON, BBS CSV and HTML. Receiver checks stop at crosshead section strength.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from dataclasses import dataclass
from pathlib import Path

from structural_lib import beam as b
from structural_lib import construction as c
from structural_lib import reporting as r

PROFILE = "LIB-027-D2"
MEMBER = "TORSION-B1"
DETAIL = "4T20-L8-100-r1"
SOURCE = "IS 456:2000 through Amendment 6; frozen LIB-027-D2 physical case"
STATIONS = (0, 500, 850, 2500, 4150, 4500, 5000)
RULES = (
    (
        "geometry",
        "structural.reinforcement_geometry.evaluate/v1",
        "is456-wp01-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "depth",
        "structural.reinforcement.effective_depth/v1",
        "is456-wp01-v1",
        b.CheckScope.MEMBER,
    ),
    ("flexure", "is456.beam.flexure.check/v1", "is456-wp01-v1", b.CheckScope.MEMBER),
    ("shear", "is456.beam.shear.check/v1", "is456-wp02-v1", b.CheckScope.MEMBER),
    ("torsion", "is456.beam.torsion.check/v1", "is456-wp02-v1", b.CheckScope.STATION),
    (
        "anchorage",
        "is456.beam.anchorage.check/v1",
        "is456-amd6-wp05-v1",
        b.CheckScope.BAR_END,
    ),
    (
        "continuity",
        "is456.beam.lap_curtailment.check/v1",
        "is456-amd6-wp05-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "arrangement",
        "structural.reinforcement_arrangement.check/v1",
        "is456-amd6-wp05-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "paths",
        "structural.reinforcement_paths.resolve/v1",
        "reinforcement-geometry-wp06-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "hooks",
        "is456.beam.closed_link_detail.check/v1",
        "is456-physical-torsion-d2-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "durability",
        "is456.beam.mild_durability.check/v1",
        "is456-physical-torsion-d2-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "support_transfer",
        "structural.beam.torsion_support_transfer.check/v1",
        "is456-physical-torsion-d2-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "seismic",
        "is456.beam.seismic_detailing.check/v1",
        "is13920-2016-amd2-wp05-v1",
        b.CheckScope.MEMBER,
    ),
    (
        "deflection",
        "is456.beam.deflection.check/v1",
        "is456-wp04-v1",
        b.CheckScope.MEMBER,
    ),
    ("crack", "is456.beam.crack_width.check/v1", "is456-wp04-v1", b.CheckScope.MEMBER),
    (
        "torsional_sls",
        "is456.beam.torsional_serviceability.check/v1",
        None,
        b.CheckScope.MEMBER,
    ),
)
SLS_NAMES = {"deflection", "crack", "torsional_sls"}


@dataclass(frozen=True)
class Workflow:
    results: dict[str, b.OperationResult]
    member_request: b.MemberDesignRequest
    package_request: r.CalculationPackageRequest
    d2_status: str


def run_workflow(
    *,
    load_n_per_mm: float = 12,
    torsion_eccentricity_mm: float = 50,
    bar_start_mm: float = -450,
    link_pitch_mm: float = 100,
    hook_tail_node_mm: float = 129,
    omit_checks: tuple[str, ...] = (),
    reverse_right_couple: bool = False,
    receiver_bar_diameter_mm: float = 20,
) -> Workflow:
    """Frozen demonstration plus explicit failure controls; not a general solver."""
    results: dict[str, b.OperationResult] = {}
    axes = b.LocalAxes(
        "B1-axes", b.Vector3(1, 0, 0), b.Vector3(0, 1, 0), b.Vector3(0, 0, 1)
    )
    bars = tuple(
        b.BarPosition(name, 20, x, y, face)
        for name, x, y, face in (
            ("TL", 50, 50, b.Face.TOP),
            ("TR", 250, 50, b.Face.TOP),
            ("BL", 50, 350, b.Face.BOTTOM),
            ("BR", 250, 350, b.Face.BOTTOM),
        )
    )
    section = b.FlexuralCapacityRequest(
        PROFILE, b.SectionKind.RECTANGULAR, 300, 400, 25, 415, bars, b.Face.BOTTOM
    )
    link = b.TransverseLink("L8", 8, 2, 2, link_pitch_mm, 415, True, 242, 342)
    topology = b.BeamTopologyRequest(
        MEMBER,
        axes,
        (
            b.PhysicalSupport("A", 0, -500, 500),
            b.PhysicalSupport("B", 5000, 4500, 5500),
        ),
        (
            b.PhysicalSpan(
                "S1", "A", "B", 350, (b.SectionRegion("R1", "300x400", 0, 5000),)
            ),
        ),
        (b.AnalysisElementMapping("E1", "S1", 0, 5000),),
    )
    results["topology"] = b.define_beam_topology(topology)
    analysis = b.BeamLineRequest(
        "B1-static",
        "ULS",
        (b.BeamNode("A", 0, True, False), b.BeamNode("B", 5000, True, False)),
        (
            b.BeamElement(
                "E1", "S1", "A", "B", 25000, 300 * 400**3 / 12, -load_n_per_mm
            ),
        ),
        station_intervals=100,
    )
    results["analysis"] = b.solve_beam_line(analysis)
    solved = {row["x_mm"]: row for row in results["analysis"].outputs["stations"]}
    # T is independently specified from the eccentric-load free body. The
    # planar solver supplies V/M only; no torsional stiffness is inferred.
    raw = tuple(
        b.RawActionRow(
            f"ULS-{x}",
            MEMBER,
            "S1",
            "B1",
            "E1",
            axes.axis_id,
            x,
            x,
            "ULS",
            "static",
            None,
            b.ActionConcurrency.STATIC_CONCURRENT,
            0,
            solved[x]["v2_n"],
            0,
            load_n_per_mm * torsion_eccentricity_mm * (2500 - x),
            0,
            solved[x]["m3_nmm"],
        )
        for x in STATIONS
    )
    results["actions"] = b.normalize_action_snapshot(
        b.RawActionSnapshot(
            "eccentric-UDL-static-equilibrium",
            "B1-static",
            results["analysis"].calculation_id,
            results["analysis"].result_id,
            b.ForceUnit.N,
            b.MomentUnit.N_MM,
            b.LengthUnit.MM,
            (axes,),
            raw,
        )
    )
    rows = results["actions"].outputs["rows"]
    geometry = b.ReinforcementGeometryRequest(PROFILE, 300, 400, 25, 8, 25, bars)
    results["geometry"] = b.evaluate_geometry(geometry)
    results["depth"] = b.effective_depth(geometry, b.Face.BOTTOM)
    results["flexure"] = b.check_flexure(
        b.FlexureCheckRequest(
            section, positive_design_moment_knm=max(row["m3_nmm"] for row in rows) / 1e6
        )
    )
    results["shear"] = b.check_shear(
        b.ShearCheckRequest(
            (
                b.ShearCapacityRequest(
                    PROFILE,
                    b.ShearAxis.V2,
                    300,
                    350,
                    25,
                    2 * 3.141592653589793 * 20**2 / 4,
                    link,
                ),
            ),
            tuple(
                b.ShearDemand(row["source_row_id"], b.ShearAxis.V2, row["v2_n"] / 1000)
                for row in rows
            ),
        )
    )
    for row in rows:
        x = row["object_station_mm"]
        results[f"torsion-{x}"] = b.check_torsion(
            b.TorsionCheckRequest(
                PROFILE,
                b.ConcurrentActionRow(
                    row["source_row_id"],
                    f"S-{x}",
                    b.ActionBasis.STATIC_CONCURRENT,
                    row["v2_n"] / 1000,
                    0,
                    row["t_nmm"] / 1e6,
                    0,
                    row["m3_nmm"] / 1e6,
                    row["row_id"],
                ),
                section,
                link,
                tuple(bar.bar_id for bar in bars),
            )
        )
    longitudinal = tuple(
        b.LongitudinalBarPath(
            bar.bar_id,
            bar.face.value + "-T20",
            (
                b.ReinforcementRole.TOP_LONGITUDINAL
                if bar.face is b.Face.TOP
                else b.ReinforcementRole.BOTTOM_LONGITUDINAL
            ),
            20,
            1,
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            bar_start_mm,
            5450,
            0.87 * 415,
        )
        for bar in bars
    )
    for side, face, centre, direction in (
        ("left", 500, 0, b.AnchorageDirection.DECREASING_X),
        ("right", 4500, 5000, b.AnchorageDirection.INCREASING_X),
    ):
        for bar in bars:
            results[f"anchorage-{bar.bar_id}-{side}"] = b.check_anchorage(
                b.AnchorageCheckRequest(
                    PROFILE,
                    MEMBER,
                    DETAIL,
                    (
                        b.AnchoragePath(
                            bar.bar_id,
                            f"{side}-face",
                            b.AnchorageLocation.DIRECT_SUPPORT,
                            direction,
                            bar_start_mm,
                            5450,
                            face,
                            "A" if side == "left" else "B",
                            face,
                            centre,
                            (),
                            None,
                            b.DevelopmentLengthRequest(
                                PROFILE,
                                20,
                                0.87 * 415,
                                415,
                                25,
                                b.BarSurface.DEFORMED,
                                b.StressState.TENSION,
                            ),
                            b.SimpleSupportAnchorageEvidence(
                                results["flexure"].outputs["checks"][0]["capacity_knm"]
                                * 1e6,
                                load_n_per_mm * 2500,
                                (f"ULS-{0 if side=='left' else 5000}",),
                            ),
                        ),
                    ),
                )
            )
    # Full design-stress provision, rather than an inferred applied-load steel
    # stress or capacity ratio, supplies a conservative demand on BOTH faces.
    demands = tuple(
        b.StationSteelDemand(
            f"{row['source_row_id']}-{role.value}",
            row["object_station_mm"],
            role,
            2 * 3.141592653589793 * 20**2 / 4,
            abs(row["v2_n"]),
            results["shear"].outputs["checks"][0]["capacity_kn"] * 1000,
            row["source_row_id"],
        )
        for row in rows
        if 500 <= row["object_station_mm"] <= 4500
        for role in (
            b.ReinforcementRole.TOP_LONGITUDINAL,
            b.ReinforcementRole.BOTTOM_LONGITUDINAL,
        )
    )
    results["continuity"] = b.check_laps_and_curtailment(
        b.LapCurtailmentCheckRequest(
            PROFILE,
            MEMBER,
            "S1",
            results["actions"].result_id,
            DETAIL,
            500,
            4500,
            350,
            25,
            415,
            b.BarSurface.DEFORMED,
            longitudinal,
            demands,
            (),
            (),
        )
    )
    cage = b.LinkCage("L8", 8, 29, 271, 29, 371, 16, True)
    arrangement_request = b.ReinforcementArrangementCheckRequest(
        PROFILE,
        MEMBER,
        "uniform",
        DETAIL,
        300,
        400,
        25,
        20,
        longitudinal,
        (cage,),
        (b.ReinforcementRole.TOP_LONGITUDINAL, b.ReinforcementRole.BOTTOM_LONGITUDINAL),
        1,
    )
    results["arrangement"] = b.check_reinforcement_arrangement(arrangement_request)
    results["durability"] = b.check_mild_durability(
        b.MildDurabilityRequest(
            PROFILE, DETAIL, 25, 25, 20, 300, 0.55, "ordinary_portland"
        )
    )
    results["seismic"] = b.check_seismic_detailing(
        b.SeismicDetailingCheckRequest(PROFILE, b.SeismicApplicability.ORDINARY_IS456)
    )
    project_result = b.create_beam_project(
        b.BeamProjectRequest(
            b.BeamProjectDefinition(PROFILE, "D2 physical torsion beam", "r1"),
            b.StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
            tuple(
                b.RevisionBinding(name, revision, SOURCE)
                for name, _, revision, _ in RULES
                if revision
            ),
            b.BeamDesignProfile(
                PROFILE,
                "d2-with-d3-obligations-r1",
                "IS 456:2000",
                b.SeismicDesignProfile.ORDINARY_IS456,
                tuple(
                    b.DesignCheckRule(
                        name,
                        op,
                        scope,
                        (
                            b.ApplicabilityState.NOT_APPLICABLE
                            if name == "seismic"
                            else b.ApplicabilityState.APPLICABLE
                        ),
                        SOURCE,
                        name if rev else None,
                    )
                    for name, op, rev, scope in RULES
                ),
                (b.DesignCriterion("cover", 25, "mm", SOURCE),),
            ),
        )
    )
    results["project"] = project_result
    project = project_result.output_as("project", b.BeamProject)
    seeds = tuple(
        b.BarPathSeed(
            bar.bar_id,
            bar.face.value + "-T20",
            (
                b.BarPathRole.TOP_LONGITUDINAL
                if bar.face is b.Face.TOP
                else b.BarPathRole.BOTTOM_LONGITUDINAL
            ),
            1,
            20,
            415,
            (
                b.PathNode(
                    "start",
                    b.PathPoint(bar_start_mm, bar.x_from_left_mm, bar.y_from_top_mm),
                ),
                b.PathNode(
                    "end", b.PathPoint(5450, bar.x_from_left_mm, bar.y_from_top_mm)
                ),
            ),
        )
        for bar in bars
    )
    vertices = (
        (0, hook_tail_node_mm, 29),
        (0, 29, 29),
        (0, 29, 371),
        (10, 271, 371),
        (10, 271, 29),
        (10, 29, 29),
        (10, 29, 129),
    )
    seeds += tuple(
        b.BarPathSeed(
            f"L8-{x}",
            "L8",
            b.BarPathRole.TRANSVERSE_LINK,
            1,
            8,
            415,
            tuple(
                b.PathNode(
                    str(i),
                    b.PathPoint(x + offset, y, z),
                    20 if 0 < i < 6 else None,
                    (
                        b.BendKind.HOOK
                        if i in (1, 5)
                        else b.BendKind.STANDARD_BEND if 0 < i < 6 else None
                    ),
                )
                for i, (offset, y, z) in enumerate(vertices)
            ),
        )
        for x in range(50, 4951, 100)
    )
    path_request = b.BarPathRequest(
        PROFILE,
        project.project_basis_id,
        project.profile.revision_id,
        MEMBER,
        "S1",
        results["topology"].result_id,
        DETAIL,
        b.MemberLocalCoordinateSystem(
            "B1-local", "member_station_x", "section_x_from_left", "section_y_from_top"
        ),
        -500,
        5500,
        300,
        400,
        seeds,
        (12000,),
    )
    results["paths"] = b.resolve_bar_paths(path_request)
    if "reinforcement_schedule" not in results["paths"].outputs:
        raise ValueError(results["paths"].diagnostics)
    results["hooks"] = b.check_closed_link_detail(
        b.ClosedLinkDetailRequest(
            path_request, cage, link, arrangement_request, 0, 5000
        )
    )
    supports = []
    reaction = load_n_per_mm * 2500 / 1000
    torque = load_n_per_mm * torsion_eccentricity_mm * 2500 / 1e6
    for name, x in (("A", 0), ("B", 5000)):
        receiver = f"CROSSHEAD-{name}"
        forces = (
            reaction / 2 - torque * 1000 / 200,
            reaction / 2 + torque * 1000 / 200,
        )
        if name == "B" and reverse_right_couple:
            forces = forces[::-1]
        lines = tuple(
            b.BearingReactionLine(f"{name}-{z}", z, force)
            for z, force in zip((1400, 1600), forces, strict=True)
        )
        receiver_axes = b.LocalAxes(
            "receiver-axes", b.Vector3(0, 0, 1), b.Vector3(0, 1, 0), b.Vector3(-1, 0, 0)
        )
        rtop = b.BeamTopologyRequest(
            receiver,
            receiver_axes,
            (
                b.PhysicalSupport("CL", 0, -500, 500),
                b.PhysicalSupport("CR", 3000, 2500, 3500),
            ),
            (
                b.PhysicalSpan(
                    "CS", "CL", "CR", 350, (b.SectionRegion("R", "1000x400", 0, 3000),)
                ),
            ),
            (b.AnalysisElementMapping("CE", "CS", 0, 3000),),
        )
        ranalysis = b.BeamLineRequest(
            receiver,
            "ULS",
            (b.BeamNode("CL", 0, True, False), b.BeamNode("CR", 3000, True, False)),
            (b.BeamElement("CE", "CS", "CL", "CR", 25000, 1000 * 400**3 / 12),),
            tuple(
                b.BeamPointLoad(
                    "CE", line.receiver_station_mm, -line.upward_reaction_kn * 1000
                )
                for line in lines
            ),
            station_intervals=30,
        )
        rbars = tuple(
            b.BarPosition(f"{face.value}-{y}", receiver_bar_diameter_mm, y, z, face)
            for face, z in ((b.Face.TOP, 50), (b.Face.BOTTOM, 350))
            for y in (50, 350, 650, 950)
        )
        rsection = b.FlexuralCapacityRequest(
            PROFILE, b.SectionKind.RECTANGULAR, 1000, 400, 25, 415, rbars, b.Face.BOTTOM
        )
        supports.append(
            b.TorqueSupportDetail(
                name,
                f"ULS-{x}",
                x,
                reaction,
                -torque,
                rtop,
                ranalysis,
                rsection,
                b.TransverseLink("C-L8", 8, 4, 4, 100, 415, True, 942, 342),
                25,
                lines,
                1500,
                "Two named vertical bearing lines into a transverse RC crosshead; receiver end supports are the supporting-system boundary.",
            )
        )
    results["support_transfer"] = b.check_torsion_support_transfer(
        b.TorsionSupportTransferRequest(
            PROFILE,
            MEMBER,
            DETAIL,
            results["actions"],
            topology,
            section,
            load_n_per_mm * 5,
            2 * torque,
            tuple(supports),
        )
    )
    leaf_map = {
        f"{name}@{MEMBER}": name
        for name, _, _, scope in RULES
        if scope is b.CheckScope.MEMBER and name not in SLS_NAMES
    }
    leaf_map.update({f"torsion@S-{x}": f"torsion-{x}" for x in STATIONS})
    leaf_map.update(
        {
            f"anchorage@{bar.bar_id}-{side}": f"anchorage-{bar.bar_id}-{side}"
            for bar in bars
            for side in ("left", "right")
        }
    )
    scopes = tuple(
        b.MemberScopeInstance(f"S-{x}", b.CheckScope.STATION, "d2-scope-r1")
        for x in STATIONS
    )
    scopes += tuple(
        b.MemberScopeInstance(
            f"{bar.bar_id}-{side}", b.CheckScope.BAR_END, "d2-scope-r1"
        )
        for bar in bars
        for side in ("left", "right")
    )
    member_request = b.MemberDesignRequest(
        project,
        MEMBER,
        results["topology"].result_id,
        results["actions"].result_id,
        DETAIL,
        "d2-scope-r1",
        scopes,
        (
            b.EffectiveDepthIteration(
                1,
                DETAIL,
                350,
                tuple(
                    results[name].result_id
                    for name in leaf_map.values()
                    if name != "seismic"
                ),
                True,
            ),
        ),
        tuple(
            b.MemberLeafEvidence.from_result(leaf, results[name])
            for leaf, name in leaf_map.items()
            if name not in omit_checks
        ),
    )
    results["member"] = b.design_member(member_request)
    member = results["member"].output_as("member_design", b.MemberDesignOutput)
    d2_checks = [
        q for q in member.leaf_qualifications if q.expectation.rule_id not in SLS_NAMES
    ]
    d2_status = (
        "FAIL"
        if any(
            q.evidence and q.evidence.engineering is b.EngineeringState.FAIL
            for q in d2_checks
        )
        else "PASS" if all(q.qualified for q in d2_checks) else "HOLD"
    )
    schedule = results["paths"].output_as("reinforcement_schedule", b.BarPathOutput)
    path_binding = r.result_binding(results["paths"], "reinforcement_schedule")
    results["bbs"] = c.create_bbs(
        c.BbsRequest(
            PROFILE,
            project.project_basis_id,
            MEMBER,
            DETAIL,
            path_binding.result_id,
            path_binding.output_payload_id,
            schedule,
            c.ShapeConvention("centreline", "r1"),
            c.CuttingStockPolicy("12m", "r1", (12000,), 3, 500),
            7850,
            link_zones=(
                c.LinkPlacementZone("all-links", "L8", 50, 4950, 100, True, True),
            ),
        )
    )
    bbs = results["bbs"].output_as("bbs", c.BbsOutput)
    bbs_binding = r.result_binding(results["bbs"], "bbs")
    results["quantities"] = c.calculate_construction_quantities(
        c.ConstructionQuantityRequest(
            PROFILE,
            project.project_basis_id,
            MEMBER,
            DETAIL,
            bbs_binding.result_id,
            bbs_binding.output_payload_id,
            bbs,
            "primary-only-before-support-union",
            "soffit-and-two-sides",
            (
                c.ConcreteNetSegment(
                    "primary", MEMBER, "M25", "primary-prism", 120000, 6000, False
                ),
            ),
            tuple(
                c.FormworkContactFace(
                    name, MEMBER, kind, name, area, c.FormworkMeasurementState.INCLUDED
                )
                for name, kind, area in (
                    ("soffit", c.FormworkFaceCategory.SOFFIT, 300 * 4000),
                    ("left", c.FormworkFaceCategory.SIDE_LEFT, 400 * 6000),
                    ("right", c.FormworkFaceCategory.SIDE_RIGHT, 400 * 6000),
                )
            ),
        )
    )
    quantities = results["quantities"].output_as(
        "quantities", c.ConstructionQuantityOutput
    )
    notes = (
        SOURCE,
        "D2 physical/ULS checks only. D3 serviceability remains HOLD; all artifacts are draft.",
        "Receiver section flexure/shear checked from actual bearing forces; receiver support/contact/foundation design is outside this beam packet.",
        "Primary concrete prism quantity only; support union/overlap measurement and receiver steel are excluded.",
    )
    package_request = r.CalculationPackageRequest(
        r.CalculationPackageMetadata(
            PROFILE,
            "D2 physical torsion beam",
            "r1",
            MEMBER,
            "r1",
            "python-structural-engineering-v1",
            tuple(x.revision_id for x in project.code_data_revisions),
            "2026-11-07T00:00:00+00:00",
        ),
        r.CalculationPackageProfile(
            PROFILE,
            "r1",
            "d2-with-d3-hold",
            tuple(q.expectation.leaf_id for q in member.leaf_qualifications),
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
        path_binding,
        bbs,
        bbs_binding,
        quantities,
        r.result_binding(results["quantities"], "quantities"),
        None,
        None,
        notes,
        tuple(
            r.CalculationTrace(
                q.expectation.leaf_id,
                q.expectation.leaf_id,
                SOURCE,
                q.evidence.method_revision_id if q.evidence else "NOT_EVALUATED",
                (
                    json.dumps(
                        results[leaf_map[q.expectation.leaf_id]].effective_inputs,
                        sort_keys=True,
                    )
                    if q.expectation.leaf_id in leaf_map
                    else "Missing serviceability basis"
                ),
                None,
                None,
                None,
                None,
                None,
                False,
            )
            for q in member.leaf_qualifications
        ),
        (
            r.DrawingView(
                "physical-paths",
                "bar_schedule",
                DETAIL,
                tuple(
                    r.DrawingDatum(
                        p.bar_id,
                        results["paths"].result_id,
                        p.bar_mark,
                        str(p.developed_centreline_length_mm),
                        "mm",
                    )
                    for p in schedule.paths
                ),
            ),
        ),
        notes,
    )
    results["package"] = r.create_calculation_package(package_request)
    return Workflow(results, member_request, package_request, d2_status)


def write_artifacts(workflow: Workflow, directory: Path) -> None:
    """Write the checked physical paths and unchanged draft package identities."""
    directory.mkdir(parents=True, exist_ok=True)
    package = workflow.results["package"].outputs["calculation_package"]
    payload = {
        "d2_status": workflow.d2_status,
        "d3_status": "HOLD",
        "results": {
            name: result.to_dict() for name, result in workflow.results.items()
        },
    }
    (directory / "calculation.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    schedule = workflow.package_request.schedule
    with (directory / "bbs.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            (
                "issue_state",
                "bar_id",
                "mark",
                "diameter_mm",
                "length_mm",
                "path_result_id",
                "bbs_result_id",
            )
        )
        for path in schedule.paths:
            writer.writerow(
                (
                    package["issue_state"],
                    path.bar_id,
                    path.bar_mark,
                    path.diameter_mm,
                    path.developed_centreline_length_mm,
                    workflow.results["paths"].result_id,
                    workflow.results["bbs"].result_id,
                )
            )
    member = workflow.results["member"].output_as("member_design", b.MemberDesignOutput)
    checks = "".join(
        f"<tr><td>{html.escape(q.expectation.leaf_id)}</td><td>{'QUALIFIED' if q.qualified else ' / '.join(q.reason_codes)}</td></tr>"
        for q in member.leaf_qualifications
    )
    physical_rows = "".join(
        f"<tr><td>{html.escape(p.bar_id)}</td><td>{p.diameter_mm:g}</td><td>{p.developed_centreline_length_mm:.9f}</td></tr>"
        for p in schedule.paths
    )
    transfer = workflow.results["support_transfer"].outputs.get("checks", ())
    support_rows = "".join(
        f"<tr><td>{html.escape(check['support_id'])}</td><td>{check['force_kn']:.6f}</td><td>{check['external_torque_knm']:.6f}</td><td>{check['receiver_moment_knm']:.6f}</td><td>{check['receiver_shear_kn']:.6f}</td></tr>"
        for check in transfer
    )
    document = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>D2 physical torsion beam</title>
<style>body{{font:16px system-ui;max-width:1100px;margin:32px auto}}td,th{{padding:6px;border-bottom:1px solid #ddd}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style>
<h1>D2 {workflow.d2_status} — {html.escape(package['issue_state'].upper())}</h1><p>D3 serviceability: HOLD. Full-member acceptance: HOLD.</p>
<p>300 × 400 mm; 5000 mm support centres, 4000 mm clear; four Ø20 continuous bars and Ø8/100 closed links.
Two-sided full-stress tension anchorage is checked at both support faces. Actual actions and transfer checks appear below.</p>
<table><thead><tr><th>Required check</th><th>Qualification</th></tr></thead><tbody>{checks}</tbody></table>
<h2>Support transfer</h2><table><thead><tr><th>Support</th><th>Vertical reaction (kN)</th><th>External torque (kNm)</th><th>Receiver moment (kNm)</th><th>Receiver shear (kN)</th></tr></thead><tbody>{support_rows}</tbody></table>
<h2>Checked physical paths</h2><table><thead><tr><th>Bar</th><th>Diameter (mm)</th><th>Centreline length (mm)</th></tr></thead><tbody>{physical_rows}</tbody></table>
<p>Physical paths: {len(schedule.paths)}. Receiver section strength is included; support/contact/foundation design remains with its supporting-system owner.</p>
<p><a href="calculation.json">Calculations and inputs</a> · <a href="bbs.csv">Physical BBS</a></p>
<pre>Package: {html.escape(package['calculation_package_id'])}\nPaths: {workflow.results['paths'].result_id}\nBBS: {workflow.results['bbs'].result_id}</pre>
<details><summary>Bound calculation package</summary><pre>{html.escape(json.dumps(package,indent=2))}</pre></details></html>"""
    (directory / "report.html").write_text(document, encoding="utf-8")


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
                "d2_status": workflow.d2_status,
                "d3_status": "HOLD",
                "member": workflow.results["member"].engineering,
                "issue_state": workflow.results["package"].outputs[
                    "calculation_package"
                ]["issue_state"],
                "physical_paths": len(workflow.package_request.schedule.paths),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
