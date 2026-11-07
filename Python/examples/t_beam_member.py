"""Replay the qualified Packet E T member from a base installed package.

The selected T owns its concrete strip and six-bar web cage. The local
transverse slab strip retains a separate owner/path record, is checked for
flange participation, and is excluded from the beam steel BBS/quantities.
No whole-floor, support-system or professional approval is implied.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from structural_lib import beam as b
from structural_lib import construction as c
from structural_lib import reporting as r
from structural_lib.codes.is456.beam.flanged_serviceability import gross_t_section
from structural_lib.codes.is456.beam.flexure import calculate_effective_flange_width

SOURCE = "IS456:2000 through Amendment6; frozen LIB-027-E ordinary monolithic sagging T member"
SOURCE_IDENTITIES = (
    "Controlled IS456 collection SHA256 964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
    "Controlled Amendment6 SHA256 4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881",
)
RULES = (
    ("geometry", "structural.reinforcement_geometry.evaluate/v1", "is456-wp01-v1"),
    ("depth", "structural.reinforcement.effective_depth/v1", "is456-wp01-v1"),
    ("flexure", "is456.beam.flexure.check/v1", "is456-wp01-v1"),
    ("shear", "is456.beam.shear.check/v1", "is456-wp02-v1"),
    ("torsion", "is456.beam.t_zero_torsion.check/v1", "is456-physical-t-member-e-v1"),
    ("deflection", "is456.beam.deflection.check/v1", "is456-wp04-v1"),
    ("crack", "is456.beam.crack_width.check/v1", "is456-wp04-v1"),
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
    ("hooks", "is456.beam.closed_link_detail.check/v1", "is456-physical-torsion-d2-v1"),
    (
        "durability",
        "is456.beam.mild_durability.check/v1",
        "is456-physical-torsion-d2-v1",
    ),
    ("t_geometry", "structural.beam.t_geometry.check/v1", "physical-t-section-e-v1"),
    (
        "flange_participation",
        "is456.beam.t_flange_participation.check/v1",
        "is456-t-flange-physical-strip-e-v1",
    ),
    (
        "stability",
        "is456.beam.t_lateral_stability.check/v1",
        "is456-physical-t-member-e-v1",
    ),
    (
        "action_basis",
        "structural.beam.t_action_basis.check/v1",
        "is456-physical-t-member-e-v1",
    ),
    (
        "t_serviceability",
        "is456.beam.t_serviceability.check/v1",
        "is456-t-screen-actual-section-e-v1",
    ),
    ("seismic", "is456.beam.seismic_detailing.check/v1", "is13920-2016-amd2-wp05-v1"),
    ("anchorage", "is456.beam.anchorage.check/v1", "is456-amd6-wp05-v1"),
)


@dataclass(frozen=True)
class Workflow:
    results: dict[str, b.OperationResult]
    member_request: b.MemberDesignRequest
    package_request: r.CalculationPackageRequest
    flange_request: b.TFlangeParticipationRequest
    service_request: b.TServiceabilityRequest
    case: str

    @property
    def status(self) -> str:
        member = self.results["member"].output_as("member_design", b.MemberDesignOutput)
        known_failure = any(
            q.evidence
            and q.evidence.engineering is b.EngineeringState.FAIL
            and set(q.reason_codes) == {"LEAF.FAIL"}
            for q in member.leaf_qualifications
        )
        return "PASS" if member.qualified else "FAIL" if known_failure else "HOLD"


def _leaf(leaf_id: str, name: str, result: b.OperationResult) -> b.MemberLeafEvidence:
    """Transport numerical summaries from the actual check without inference."""
    output = result.outputs
    values: dict[str, Any] = {}
    if name == "flexure" and output.get("checks"):
        check = output["checks"][0]
        values = {
            "required_value": check["demand_knm"],
            "supplied_value": check["capacity_knm"],
            "unit": "kNm",
            "governing_utilization": check["utilization"],
        }
    elif name == "shear" and output.get("checks"):
        check = max(output["checks"], key=lambda item: item["utilization"])
        values = {
            "required_value": abs(check["signed_demand_kn"]),
            "supplied_value": check["capacity_kn"],
            "unit": "kN",
            "governing_utilization": check["utilization"],
        }
    elif name.startswith("anchorage-") and output.get("checks"):
        check = output["checks"][0]
        values = {
            "required_value": check["required_development_length_mm"],
            "supplied_value": check["available_for_criterion_mm"],
            "unit": "mm",
            "governing_utilization": check["utilization"],
        }
    elif name == "crack" and "calculated_crack_width_mm" in output:
        values = {
            "required_value": output["calculated_crack_width_mm"],
            "supplied_value": output["limit_mm"],
            "unit": "mm",
            "governing_utilization": output["utilization"],
        }
    elif name == "deflection" and "actual_span_depth_ratio" in output:
        actual, limit = (
            output["actual_span_depth_ratio"],
            output["allowable_span_depth_ratio"],
        )
        values = {
            "required_value": actual,
            "supplied_value": limit,
            "unit": "ratio",
            "governing_utilization": actual / limit,
        }
    elif name == "action_basis" and "topology_effective_depth_mm" in output:
        values = {
            "required_value": output["actual_effective_depth_mm"],
            "supplied_value": output["topology_effective_depth_mm"],
            "unit": "mm",
        }
    return b.MemberLeafEvidence.from_result(leaf_id, result, **values)


def _slab_strip(
    profile: str,
    project: b.BeamProject,
    section: b.TSectionGeometry,
    loads: b.TBeamLoadBasis,
) -> b.TFlangeStripRequest:
    """Actual separately owned slab paths and supplied two-span corroboration."""
    span = section.flange_width_physical_mm
    seeds = []
    for y, face in ((35, "top"), (115, "bottom")):
        for index, x in enumerate(range(25, 6951, 150)):
            seeds.append(
                b.BarPathSeed(
                    f"SLAB-M-{face}-{index}",
                    f"SLAB-M-{face}",
                    b.BarPathRole.FLANGE_TRANSVERSE,
                    1,
                    10,
                    415,
                    (
                        b.PathNode("start", b.PathPoint(-125, x, y)),
                        b.PathNode("end", b.PathPoint(2 * span + 125, x, y)),
                    ),
                )
            )
    for y, face in ((49, "top"), (101, "bottom")):
        count = math.floor((span + 126) / 200)
        for index in range(-count, count + 1):
            station = span + 200 * index
            seeds.append(
                b.BarPathSeed(
                    f"SLAB-D-{face}-{index}",
                    f"SLAB-D-{face}",
                    b.BarPathRole.FLANGE_DISTRIBUTION,
                    1,
                    8,
                    415,
                    (
                        b.PathNode("start", b.PathPoint(station, 25, y)),
                        b.PathNode("end", b.PathPoint(station, 6975, y)),
                    ),
                )
            )
    paths = b.BarPathRequest(
        profile,
        project.project_basis_id,
        project.profile.revision_id,
        "SLAB-STRIP",
        "TRANSVERSE-TWO-SPANS",
        "SLAB-LINE-r1",
        "SLAB-M10-150-D8-200-r1",
        b.MemberLocalCoordinateSystem(
            "slab-local",
            "member_station_x",
            "section_x_from_left",
            "section_y_from_top",
        ),
        -150,
        2 * span + 150,
        7000,
        150,
        tuple(seeds),
        (12000,),
    )
    area_g = 150 * 25 / 1000 + loads.superimposed_permanent_load_n_per_mm * 1000 / span
    area_q = loads.imposed_load_n_per_mm * 1000 / span
    line = (
        area_g * loads.permanent_ultimate_factor
        + area_q * loads.imposed_ultimate_factor
    ) * 0.6
    nodes = tuple(
        b.BeamNode(name, x, True, False)
        for name, x in (("LEFT", 0), ("WEB", span), ("RIGHT", 2 * span))
    )
    analysis = b.BeamLineRequest(
        "SLAB-LINE-r1",
        "SLAB-ULS",
        nodes,
        tuple(
            b.BeamElement(
                f"SE-{i}",
                f"SS-{i}",
                a.node_id,
                z.node_id,
                25000,
                600 * 150**3 / 12,
                -line,
            )
            for i, (a, z) in enumerate(zip(nodes, nodes[1:], strict=False))
        ),
        station_intervals=16,
    )
    return b.TFlangeStripRequest(
        "SLAB-STRIP-OWNER",
        section.geometry_revision_id,
        "Supplied ordinary monolithic two-span local slab strip; main direction transverse to T beam; no whole-floor acceptance.",
        20,
        150,
        200,
        35,
        115,
        49,
        101,
        paths,
        analysis,
    )


def run_workflow(
    *,
    case: str = "main",
    probe: str = "adequate",
    omit_checks: tuple[str, ...] = (),
) -> Workflow:
    """Run the frozen supplied profile and named truthful failure/HOLD probes."""
    if case not in ("main", "width-limited"):
        raise ValueError("case must be main or width-limited")
    profile = "LIB-027-E-" + case
    member, detail = "T-B1", (
        "4T8-2T16-L8-150-r1" if probe == "insufficient-bars" else "4T20-2T16-L8-150-r1"
    )
    if probe in ("short-anchor", "short-hook", "shoulder-bar", "end-cover"):
        detail += ":" + probe
    physical_width = 2500 if case == "width-limited" else 1000
    offset = (physical_width - 300) / 2
    section = b.TSectionGeometry(
        "T-SECTION", f"T-{physical_width}-r1", 300, 550, physical_width, 150, offset
    )
    bar_start = 0 if probe == "short-anchor" else -500 if probe == "end-cover" else -450
    bars = tuple(
        b.BarPosition(name, diameter, offset + x, y, face)
        for name, diameter, x, y, face in (
            ("B1", 20, 50, 500, b.Face.BOTTOM),
            ("B2", 20, 350 / 3, 500, b.Face.BOTTOM),
            ("B3", 20, 550 / 3, 500, b.Face.BOTTOM),
            ("B4", 20, 250, 500, b.Face.BOTTOM),
            ("T1", 16, 50, 50, b.Face.TOP),
            ("T2", 16, 250, 50, b.Face.TOP),
        )
    )
    if probe == "shoulder-bar":
        bars = (replace(bars[0], x_from_left_mm=offset - 50),) + bars[1:]
    if probe == "insufficient-bars":
        bars = tuple(
            replace(bar, diameter_mm=8) if bar.face is b.Face.BOTTOM else bar
            for bar in bars
        )
    results: dict[str, b.OperationResult] = {}
    axes = b.LocalAxes(
        "T-axes", b.Vector3(1, 0, 0), b.Vector3(0, 1, 0), b.Vector3(0, 0, 1)
    )
    topology = b.BeamTopologyRequest(
        member,
        axes,
        (
            b.PhysicalSupport("A", 0, -500, 500),
            b.PhysicalSupport("B", 6000, 5500, 6500),
        ),
        (
            b.PhysicalSpan(
                "S1",
                "A",
                "B",
                450 if probe == "depth-conflict" else 500,
                (b.SectionRegion("R1", section.section_id, 0, 6000),),
            ),
        ),
        (b.AnalysisElementMapping("E1", "S1", 0, 6000),),
    )
    results["topology"] = b.define_beam_topology(topology)
    rules = tuple(
        b.DesignCheckRule(
            name,
            operation,
            b.CheckScope.BAR_END if name == "anchorage" else b.CheckScope.MEMBER,
            (
                b.ApplicabilityState.NOT_APPLICABLE
                if name == "seismic"
                else b.ApplicabilityState.APPLICABLE
            ),
            SOURCE,
            name,
        )
        for name, operation, _ in RULES
    )
    results["project"] = b.create_beam_project(
        b.BeamProjectRequest(
            b.BeamProjectDefinition(profile, "Ordinary physical T-beam member", "r1"),
            b.StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
            tuple(
                b.RevisionBinding(name, revision, SOURCE) for name, _, revision in RULES
            ),
            b.BeamDesignProfile(
                profile,
                (
                    "T-profile-service-limit-r1"
                    if probe == "service-fail"
                    else "T-profile-r1"
                ),
                "IS456:2000",
                b.SeismicDesignProfile.ORDINARY_IS456,
                rules,
                (
                    b.DesignCriterion(
                        "beam-cover",
                        25,
                        "mm",
                        "Mild, uncoated OPC M25 beam; separate slab cover20mm",
                    ),
                    b.DesignCriterion(
                        "crack-limit",
                        0.05 if probe == "service-fail" else 0.3,
                        "mm",
                        (
                            "Explicit stricter project-limit negative control"
                            if probe == "service-fail"
                            else "Declared mild, nonharmful cracking code criterion"
                        ),
                    ),
                ),
            ),
        )
    )
    project = results["project"].output_as("project", b.BeamProject)
    seeds = tuple(
        b.BarPathSeed(
            bar.bar_id,
            f"{bar.face.value}-T{bar.diameter_mm:g}",
            (
                b.BarPathRole.BOTTOM_LONGITUDINAL
                if bar.face is b.Face.BOTTOM
                else b.BarPathRole.TOP_LONGITUDINAL
            ),
            1,
            bar.diameter_mm,
            415,
            (
                b.PathNode(
                    "start",
                    b.PathPoint(bar_start, bar.x_from_left_mm, bar.y_from_top_mm),
                ),
                b.PathNode(
                    "end", b.PathPoint(6450, bar.x_from_left_mm, bar.y_from_top_mm)
                ),
            ),
        )
        for bar in bars
    )
    tail = 112 if probe == "short-hook" else 129
    vertices = (
        (0, tail, 29),
        (0, 29, 29),
        (0, 29, 521),
        (10, 271, 521),
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
                    str(i),
                    b.PathPoint(station + dx, offset + x, y),
                    20 if 0 < i < 6 else None,
                    (
                        b.BendKind.HOOK
                        if i in (1, 5)
                        else b.BendKind.STANDARD_BEND if 0 < i < 6 else None
                    ),
                )
                for i, (dx, x, y) in enumerate(vertices)
            ),
        )
        for station in range(75, 5926, 150)
    )
    global_paths = b.BarPathRequest(
        profile,
        project.project_basis_id,
        project.profile.revision_id,
        member,
        "S1",
        results["topology"].result_id,
        detail,
        b.MemberLocalCoordinateSystem(
            "T-global", "member_station_x", "section_x_from_left", "section_y_from_top"
        ),
        -500,
        6500,
        physical_width,
        550,
        seeds,
        (12000,),
    )
    geometry_request = b.TGeometryCheckRequest(
        profile,
        member,
        detail,
        section,
        section.geometry_revision_id,
        25,
        8,
        25,
        bars,
        global_paths,
    )
    results["t_geometry"] = b.check_t_geometry(geometry_request)
    effective = calculate_effective_flange_width(
        bw_mm=300,
        span_mm=6000,
        df_mm=150,
        flange_overhang_left_mm=offset,
        flange_overhang_right_mm=offset,
        beam_type="T",
    )
    capacity_request = b.FlexuralCapacityRequest(
        profile,
        b.SectionKind.T_BEAM,
        300,
        550,
        25,
        415,
        bars,
        b.Face.BOTTOM,
        effective,
        150,
    )
    results["capacity"] = b.flexural_capacity(capacity_request)
    web_geometry = results["t_geometry"].output_as(
        "web_geometry", b.ReinforcementGeometryRequest
    )
    web_paths = results["t_geometry"].output_as("web_paths", b.BarPathRequest)
    results["geometry"] = b.evaluate_geometry(web_geometry)
    results["depth"] = b.effective_depth(web_geometry, b.Face.BOTTOM)
    # A failed x/material layout still retains its conditional section
    # arithmetic and actual draft paths. It cannot qualify the required
    # geometry/depth leaves or issue the member.
    d = float(
        results["depth"].outputs.get(
            "effective_depth_mm", results["capacity"].outputs["effective_depth_mm"]
        )
    )
    loads = b.TBeamLoadBasis(
        25,
        2,
        80 if probe == "overload" else 3,
        1.5,
        1.5,
        28,
        56,
        3650,
        False,
        "Declared demonstration G from28days, finishes56days, assessment3650days; ordinary static Q envelope; complete23.2.1 screening covers conventional long-term effects, no calculated time components.",
    )
    permanent = section.area_mm2 * 25 / 1e6 + loads.superimposed_permanent_load_n_per_mm
    _, _, gross_inertia = gross_t_section(300, physical_width, 150, 550)
    for name, w in (
        ("ULS", 1.5 * (permanent + loads.imposed_load_n_per_mm)),
        ("SLS", permanent + loads.imposed_load_n_per_mm),
        ("PERMANENT", permanent),
    ):
        analysis = b.solve_beam_line(
            b.BeamLineRequest(
                f"T-{name}",
                name,
                (b.BeamNode("A", 0, True, False), b.BeamNode("B", 6000, True, False)),
                (b.BeamElement("E1", "S1", "A", "B", 25000, gross_inertia, -w),),
                station_intervals=12,
            )
        )
        results[f"analysis-{name}"] = analysis
        results[f"actions-{name}"] = b.normalize_action_snapshot(
            b.RawActionSnapshot(
                "public-python-beam-line",
                f"T-{name}",
                analysis.calculation_id,
                analysis.result_id,
                b.ForceUnit.N,
                b.MomentUnit.N_MM,
                b.LengthUnit.MM,
                (axes,),
                tuple(
                    b.RawActionRow(
                        f"{name}-{row['x_mm']:g}",
                        member,
                        "S1",
                        member,
                        "E1",
                        axes.axis_id,
                        row["x_mm"],
                        row["distance_from_start_mm"],
                        name,
                        "static",
                        None,
                        b.ActionConcurrency.STATIC_CONCURRENT,
                        0,
                        row["v2_n"],
                        0,
                        0,
                        0,
                        row["m3_nmm"],
                    )
                    for row in analysis.outputs["stations"]
                ),
            )
        )
    action_request = b.TBeamActionBasisRequest(
        geometry_request,
        None if probe == "missing-support" else topology,
        results["actions-ULS"],
        results["actions-SLS"],
        results["actions-PERMANENT"],
        loads,
    )
    results["action_basis"] = b.check_t_action_basis(action_request)
    flange_request = b.TFlangeParticipationRequest(
        action_request,
        physical_width - 300,
        physical_width - 300,
        True,
        "Monolithic poured web/flange; separately owned contiguous slab strip",
        "perpendicular_to_beam",
        (
            None
            if probe == "missing-flange"
            else _slab_strip(profile, project, section, loads)
        ),
    )
    results["flange_participation"] = b.check_t_flange_participation(flange_request)
    ultimate_rows = results["actions-ULS"].outputs["rows"]
    moment_row = max(ultimate_rows, key=lambda row: row["m3_nmm"])
    results["flexure"] = b.check_flexure(
        b.FlexureCheckRequest(
            capacity_request, positive_design_moment_knm=moment_row["m3_nmm"] / 1e6
        )
    )
    link = b.TransverseLink("L8", 8, 2, 2, 150, 415, True, 242, 492)
    results["shear"] = b.check_shear(
        b.ShearCheckRequest(
            (
                b.ShearCapacityRequest(
                    profile,
                    b.ShearAxis.V2,
                    300,
                    d,
                    25,
                    float(results["capacity"].outputs["tension_steel_area_mm2"]),
                    link,
                ),
            ),
            tuple(
                b.ShearDemand(row["row_id"], b.ShearAxis.V2, abs(row["v2_n"]) / 1000)
                for row in ultimate_rows
            ),
        )
    )
    results["torsion"] = b.check_t_zero_torsion(action_request)
    longitudinal = tuple(
        b.LongitudinalBarPath(
            bar.bar_id,
            f"{bar.face.value}-T{bar.diameter_mm:g}",
            (
                b.ReinforcementRole.BOTTOM_LONGITUDINAL
                if bar.face is b.Face.BOTTOM
                else b.ReinforcementRole.TOP_LONGITUDINAL
            ),
            bar.diameter_mm,
            1,
            bar.x_from_left_mm - offset,
            bar.y_from_top_mm,
            bar_start,
            6450,
            0.87 * 415,
        )
        for bar in bars
    )
    cage = b.LinkCage("L8", 8, 29, 271, 29, 521, 16, True)
    arrangement = b.ReinforcementArrangementCheckRequest(
        profile,
        member,
        "uniform",
        detail,
        300,
        550,
        25,
        20,
        longitudinal,
        (cage,),
        (b.ReinforcementRole.BOTTOM_LONGITUDINAL, b.ReinforcementRole.TOP_LONGITUDINAL),
        1,
    )
    results["arrangement"] = b.check_reinforcement_arrangement(arrangement)
    results["paths"] = b.resolve_bar_paths(global_paths)
    results["hooks"] = b.check_closed_link_detail(
        b.ClosedLinkDetailRequest(web_paths, cage, link, arrangement, 0, 6000)
    )
    results["durability"] = b.check_mild_durability(
        b.MildDurabilityRequest(
            profile, detail, 25, 25, 20, 320, 0.5, "ordinary_portland"
        )
    )
    results["stability"] = b.check_t_lateral_stability(
        b.TLateralStabilityRequest(
            profile,
            member,
            section,
            d,
            0,
            6000,
            (0, 6000),
            "Declared lateral restraints at both physical bearings; conservative web-breadth limit",
        )
    )
    results["seismic"] = b.check_seismic_detailing(
        b.SeismicDetailingCheckRequest(profile, b.SeismicApplicability.ORDINARY_IS456)
    )
    demands = tuple(
        b.StationSteelDemand(
            f"{row['row_id']}-{role.value}",
            row["object_station_mm"],
            role,
            sum(
                math.pi * bar.diameter_mm**2 / 4
                for bar in bars
                if (bar.face is b.Face.BOTTOM)
                == (role is b.ReinforcementRole.BOTTOM_LONGITUDINAL)
            ),
            abs(row["v2_n"]),
            float(results["shear"].outputs["checks"][0]["capacity_kn"]) * 1000,
            row["row_id"],
        )
        for row in ultimate_rows
        if 500 <= row["object_station_mm"] <= 5500
        for role in (
            b.ReinforcementRole.BOTTOM_LONGITUDINAL,
            b.ReinforcementRole.TOP_LONGITUDINAL,
        )
    )
    results["continuity"] = b.check_laps_and_curtailment(
        b.LapCurtailmentCheckRequest(
            profile,
            member,
            "S1",
            results["actions-ULS"].result_id,
            detail,
            500,
            5500,
            d,
            25,
            415,
            b.BarSurface.DEFORMED,
            longitudinal,
            demands,
            (),
            (),
        )
    )
    for side, face, centre, direction in (
        ("left", 500, 0, b.AnchorageDirection.DECREASING_X),
        ("right", 5500, 6000, b.AnchorageDirection.INCREASING_X),
    ):
        for bar in bars:
            results[f"anchorage-{bar.bar_id}-{side}"] = b.check_anchorage(
                b.AnchorageCheckRequest(
                    profile,
                    member,
                    detail,
                    (
                        b.AnchoragePath(
                            bar.bar_id,
                            f"{side}-face",
                            b.AnchorageLocation.DIRECT_SUPPORT,
                            direction,
                            bar_start,
                            6450,
                            face,
                            "A" if side == "left" else "B",
                            face,
                            centre,
                            (),
                            None,
                            b.DevelopmentLengthRequest(
                                profile,
                                bar.diameter_mm,
                                0.87 * 415,
                                415,
                                25,
                                b.BarSurface.DEFORMED,
                                b.StressState.TENSION,
                            ),
                            None,
                        ),
                    ),
                )
            )
    criterion = b.CrackWidthLimitRequest(
        profile,
        b.ExposureClass.MILD,
        False,
        selected_source=(
            b.LimitSource.PROJECT if probe == "service-fail" else b.LimitSource.CODE
        ),
        project_limit_mm=0.05 if probe == "service-fail" else None,
    )
    service_request = b.TServiceabilityRequest(
        flange_request,
        25,
        415,
        200000,
        None if probe == "missing-service" else criterion,
    )
    results["t_serviceability"] = b.check_t_serviceability(service_request)
    for name in ("deflection", "crack"):
        if name in results["t_serviceability"].outputs:
            results[name] = results["t_serviceability"].output_as(
                name, b.OperationResult
            )
    leaf_map = {f"{name}@{member}": name for name, _, _ in RULES if name != "anchorage"}
    leaf_map.update(
        {
            f"anchorage@{bar.bar_id}-{side}": f"anchorage-{bar.bar_id}-{side}"
            for bar in bars
            for side in ("left", "right")
        }
    )
    leaves = tuple(
        _leaf(leaf, name, results[name])
        for leaf, name in leaf_map.items()
        if name in results and name not in omit_checks
    )
    member_request = b.MemberDesignRequest(
        project,
        member,
        results["topology"].result_id,
        results["actions-ULS"].result_id,
        detail,
        "T-member-scope-r1",
        tuple(
            b.MemberScopeInstance(
                f"{bar.bar_id}-{side}", b.CheckScope.BAR_END, "T-member-scope-r1"
            )
            for bar in bars
            for side in ("left", "right")
        ),
        (
            b.EffectiveDepthIteration(
                1,
                detail,
                d,
                tuple(
                    leaf.result_id
                    for leaf in leaves
                    if leaf.leaf_id.split("@", 1)[0] != "seismic"
                ),
                True,
            ),
        ),
        leaves,
    )
    results["member"] = b.design_member(member_request)
    schedule = results["paths"].output_as("reinforcement_schedule", b.BarPathOutput)
    path_binding = r.result_binding(results["paths"], "reinforcement_schedule")
    results["bbs"] = c.create_bbs(
        c.BbsRequest(
            profile,
            project.project_basis_id,
            member,
            detail,
            path_binding.result_id,
            path_binding.output_payload_id,
            schedule,
            c.ShapeConvention("centreline", "r1"),
            c.CuttingStockPolicy("12m", "r1", (12000,), 3, 500),
            7850,
            link_zones=(
                c.LinkPlacementZone("web-links", "L8", 75, 5925, 150, True, True),
            ),
        )
    )
    bbs = results["bbs"].output_as("bbs", c.BbsOutput)
    bbs_binding = r.result_binding(results["bbs"], "bbs")
    results["quantities"] = c.calculate_construction_quantities(
        c.ConstructionQuantityRequest(
            profile,
            project.project_basis_id,
            member,
            detail,
            bbs_binding.result_id,
            bbs_binding.output_payload_id,
            bbs,
            "T-owns-full-prism-support-system-excludes-same-union",
            "exposed-clear-span-soffits-web-sides-no-interface-formwork",
            (
                c.ConcreteNetSegment(
                    "flange",
                    member,
                    "M25",
                    "owned-flange",
                    physical_width * 150,
                    7000,
                    True,
                ),
                c.ConcreteNetSegment(
                    "web-below",
                    member,
                    "M25",
                    "owned-web-below",
                    300 * 400,
                    7000,
                    False,
                ),
            ),
            tuple(
                c.FormworkContactFace(
                    name,
                    member,
                    category,
                    name,
                    area,
                    c.FormworkMeasurementState.INCLUDED,
                )
                for name, category, area in (
                    ("web-soffit", c.FormworkFaceCategory.SOFFIT, 300 * 5000),
                    ("web-left", c.FormworkFaceCategory.SIDE_LEFT, 400 * 5000),
                    ("web-right", c.FormworkFaceCategory.SIDE_RIGHT, 400 * 5000),
                    (
                        "flange-soffits",
                        c.FormworkFaceCategory.SOFFIT,
                        (physical_width - 300) * 5000,
                    ),
                )
            ),
        )
    )
    quantities = results["quantities"].output_as(
        "quantities", c.ConstructionQuantityOutput
    )
    member_output = results["member"].output_as("member_design", b.MemberDesignOutput)
    notes = SOURCE_IDENTITIES + (
        SOURCE,
        "30 frozen obligations:18 member rules plus12 actual bar ends; engineering approval remains unreviewed.",
        "Physical/effective/web widths are distinct. Beam strength does not credit separately owned slab distribution steel; its actual-y effect is audited.",
        "Slab-strip reinforcement paths/provision remain separately owned and excluded from beam steel BBS/quantities; whole-floor and supporting-system approval are outside this packet.",
        "T owns the full7000mm physical flange+web-below union; supporting-system assembly must exclude that owned union. Slab continuation/bearing/internal interfaces are not exposed formwork.",
        "Deflection uses the complete flanged23.2.1 screen, not calculated deflection. Actual T soffit crack envelope retains elastic upper-bound strain and explicit mild exposure.",
    )
    package_request = r.CalculationPackageRequest(
        r.CalculationPackageMetadata(
            profile,
            "Ordinary T-beam member",
            "r1",
            member,
            "r1",
            "python-structural-engineering-v1",
            tuple(x.revision_id for x in project.code_data_revisions),
            "2026-11-07T00:00:00+00:00",
        ),
        r.CalculationPackageProfile(
            profile,
            "r1",
            "ordinary-sagging-T-r1",
            tuple(leaf_map),
            (
                "inputs",
                "calculations",
                "reinforcement",
                "quantities",
                "drawings",
                "signatures",
            ),
        ),
        member_output,
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
                q.evidence.method_revision_id if q.evidence else "MISSING",
                (
                    json.dumps(
                        results[leaf_map[q.expectation.leaf_id]].effective_inputs,
                        sort_keys=True,
                    )
                    if q.evidence
                    else "Required evidence missing from member"
                ),
                q.evidence.required_value if q.evidence else None,
                q.evidence.supplied_value if q.evidence else None,
                q.evidence.selected_value if q.evidence else None,
                q.evidence.unit if q.evidence else None,
                q.evidence.governing_utilization if q.evidence else None,
                q.expectation.leaf_id == member_output.governing_leaf_id,
            )
            for q in member_output.leaf_qualifications
        ),
        (
            r.DrawingView(
                "T-section",
                "physical_section",
                detail,
                tuple(
                    r.DrawingDatum(
                        name, results["t_geometry"].result_id, name, str(value), "mm"
                    )
                    for name, value in (
                        ("bf_physical", physical_width),
                        ("bf_effective", effective),
                        ("bw", 300),
                        ("D", 550),
                        ("Df", 150),
                        ("web_left", offset),
                    )
                ),
            ),
            r.DrawingView(
                "web-paths",
                "bar_schedule",
                detail,
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
    return Workflow(
        results, member_request, package_request, flange_request, service_request, case
    )


def write_artifacts(workflow: Workflow, directory: Path) -> None:
    """Render the actual T outline and unchanged decision/path identities."""
    directory.mkdir(parents=True, exist_ok=True)
    package = workflow.results["package"].outputs["calculation_package"]
    payload = {
        "case": workflow.case,
        "status": workflow.status,
        "member_engineering": workflow.results["member"].engineering.value,
        "member_completeness": workflow.results["member"].completeness.value,
        "results": {
            name: result.to_dict() for name, result in workflow.results.items()
        },
    }
    (directory / "calculation.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    from pydantic import TypeAdapter

    stability_request = TypeAdapter(b.TLateralStabilityRequest).validate_python(
        workflow.results["stability"].effective_inputs["request"]["value"]
    )
    contracts = (
        (
            "t-geometry",
            b.TGeometryCheckRequest,
            workflow.flange_request.action_basis.geometry,
        ),
        ("t-actions", b.TBeamActionBasisRequest, workflow.flange_request.action_basis),
        (
            "t-zero-torsion",
            b.TBeamActionBasisRequest,
            workflow.flange_request.action_basis,
        ),
        ("t-flange", b.TFlangeParticipationRequest, workflow.flange_request),
        ("t-serviceability", b.TServiceabilityRequest, workflow.service_request),
        ("t-stability", b.TLateralStabilityRequest, stability_request),
        ("member", b.MemberDesignRequest, workflow.member_request),
    )
    (directory / "schemas").mkdir(exist_ok=True)
    (directory / "requests").mkdir(exist_ok=True)
    for name, request_type, request in contracts:
        adapter = TypeAdapter(request_type)
        (directory / "schemas" / (name + ".schema.json")).write_text(
            json.dumps(adapter.json_schema(), indent=2) + "\n", encoding="utf-8"
        )
        (directory / "requests" / (name + ".json")).write_bytes(
            adapter.dump_json(request, indent=2)
        )
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
        for path in workflow.package_request.schedule.paths:
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
    geometry = workflow.flange_request.action_basis.geometry
    section = geometry.section
    width = section.flange_width_physical_mm
    points = " ".join(f"{x},{y}" for x, y in section.outline)
    bars_svg = "".join(
        f'<circle class="beam-bar" data-bar-id="{bar.bar_id}" cx="{bar.x_from_left_mm}" cy="{bar.y_from_top_mm}" r="{bar.diameter_mm/2}" fill="#173d6c"/>'
        for bar in geometry.bars
    )
    flange = workflow.results["flange_participation"]
    bars_svg += "".join(
        f'<circle class="slab-distribution" data-bar-id="{html.escape(bar["bar_id"])}" cx="{bar["x_from_left_mm"]}" cy="{bar["y_from_top_mm"]}" r="{bar["diameter_mm"]/2}" fill="#62756b"/>'
        for bar in flange.outputs.get("parallel_slab_bars", ())
    )
    actual_link = next(
        path
        for path in workflow.package_request.schedule.paths
        if path.role is b.BarPathRole.TRANSVERSE_LINK
    )
    cage_points = []
    for segment in actual_link.segments:
        centre, normal = segment.bend_centre, segment.bend_plane_normal
        if centre is None or normal is None:
            cage_points.extend(
                (p.section_x_from_left_mm, p.section_y_from_top_mm)
                for p in (segment.start, segment.end)
            )
        else:
            u = (
                segment.start.station_x_mm - centre.station_x_mm,
                segment.start.section_x_from_left_mm - centre.section_x_from_left_mm,
                segment.start.section_y_from_top_mm - centre.section_y_from_top_mm,
            )
            n = (
                normal.station_component,
                normal.section_horizontal_component,
                normal.section_vertical_component,
            )
            v = (
                n[1] * u[2] - n[2] * u[1],
                n[2] * u[0] - n[0] * u[2],
                n[0] * u[1] - n[1] * u[0],
            )
            for i in range(17):
                t = math.radians(segment.bend_sweep_degrees or 0) * i / 16
                cage_points.append(
                    (
                        centre.section_x_from_left_mm
                        + u[1] * math.cos(t)
                        + v[1] * math.sin(t),
                        centre.section_y_from_top_mm
                        + u[2] * math.cos(t)
                        + v[2] * math.sin(t),
                    )
                )
    cage = (
        f'<polyline class="actual-web-link" data-bar-id="{actual_link.bar_id}" points="'
        + " ".join(f"{x},{y}" for x, y in cage_points)
        + '" fill="none" stroke="#ab4320" stroke-width="8"/>'
    )
    svg = f'<svg aria-label="Actual physical T section and web cage" viewBox="-30 -30 {width+60} 610" style="width:100%;max-height:350px"><polygon points="{points}" fill="#e3e5e8" stroke="#333" stroke-width="3"/>{cage}{bars_svg}</svg>'
    checks = "".join(
        f'<tr><td>{html.escape(q.expectation.leaf_id)}</td><td>{"QUALIFIED" if q.qualified else html.escape(" / ".join(q.reason_codes))}</td><td>{q.evidence.required_value if q.evidence and q.evidence.required_value is not None else "—"}</td><td>{q.evidence.supplied_value if q.evidence and q.evidence.supplied_value is not None else "—"}</td><td>{q.evidence.unit if q.evidence and q.evidence.unit else ""}</td><td>{html.escape(q.evidence.method_revision_id+"; "+q.evidence.code_data_revision_id) if q.evidence else "Required evidence missing"}</td></tr>'
        for q in workflow.package_request.member_result.leaf_qualifications
    )
    steel_rows = "".join(
        f"<tr><td>{bar.bar_id}</td><td>{bar.diameter_mm:g}</td><td>{bar.x_from_left_mm:.6f}</td><td>{bar.x_from_left_mm-section.web_left_from_flange_left_mm:.6f}</td><td>{bar.y_from_top_mm:g}</td></tr>"
        for bar in geometry.bars
    )
    path_rows = "".join(
        f"<tr><td>{html.escape(p.bar_id)}</td><td>{p.diameter_mm:g}</td><td>{p.developed_centreline_length_mm:.9f}</td></tr>"
        for p in workflow.package_request.schedule.paths
    )
    service = workflow.results["t_serviceability"]
    diagnostic_rows = "".join(
        f'<tr><td>{html.escape(name)}</td><td>{html.escape(d.code)}</td><td>{html.escape(d.field_or_location or "")}</td><td>{html.escape(d.message)}</td></tr>'
        for name, result in workflow.results.items()
        for d in result.diagnostics
    )
    hook_rows = "".join(
        f'<tr><td>{html.escape(check["bar_id"])}</td><td>{check["tails_mm"][0]}</td><td>{check["tails_mm"][1]}</td><td>{check["minimum_tail_mm"]}</td><td>{check["passed"]}</td></tr>'
        for check in workflow.results["hooks"].outputs.get("checks", ())
    )
    quantities = workflow.results["quantities"].outputs["quantities"]
    service_html = ""
    if "section_states" in service.outputs:
        states = service.outputs["section_states"]
        service_html = (
            "<h2>T service section</h2><table><tr><th>Model</th><th>NA mm</th><th>Icr mm4</th><th>Steel stress MPa</th><th>Soffit strain</th></tr>"
            + "".join(
                f'<tr><td>{state["model"]}</td><td>{state["neutral_axis_mm"]:.9f}</td><td>{state["cracked_inertia_mm4"]:.6f}</td><td>{state["bottom_steel_stress_nmm2"]:.9f}</td><td>{state["elastic_bottom_surface_strain"]:.12f}</td></tr>'
                for state in states
            )
            + "</table>"
        )
        service_html += f'<p>Deflection screen: {html.escape(json.dumps(service.outputs["deflection"]["outputs"],sort_keys=True))}</p><p>Crack envelope: {html.escape(json.dumps(service.outputs["crack"]["outputs"],sort_keys=True))}</p>'
    report = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Packet E T member</title>
<style>body{{font:15px system-ui;margin:30px;max-width:1100px;color:#17202b}}table{{border-collapse:collapse;width:100%;margin:16px 0}}td,th{{border:1px solid #ccd2da;padding:6px;text-align:left}}p{{overflow-wrap:anywhere}}svg{{display:block}}</style>
<h1>Packet E ordinary T-beam — {workflow.status}</h1><p>Issue state: {package['issue_state']}; engineering approval: unreviewed. Full member engineering: {workflow.results['member'].engineering}; completeness: {workflow.results['member'].completeness}. A known failed required check gives the workflow FAIL summary even when other checks remain HOLD; the original member dimensions remain unchanged.</p>
<p>bf_physical={width:g} mm; bf_effective={workflow.package_request.drawings[0].data[1].value} mm; bw=300 mm. x from physical flange-left; y from flange-top.</p>{svg}
<p>Drawing shows actual T material, the section projection of link {actual_link.bar_id} with its real hooks/tails, blue beam bars and green separately owned parallel slab bars. Slab-strip steel is excluded from beam BBS; its full transverse/distribution paths remain in calculation JSON.</p>
<h2>Declared boundaries</h2>{''.join(f'<p>{html.escape(note)}</p>' for note in workflow.package_request.assumptions)}
<h2>Actual supplied beam steel</h2><table><tr><th>ID</th><th>Diameter mm</th><th>Global x mm</th><th>Web x mm</th><th>Depth mm</th></tr>{steel_rows}</table>
<p>Supplied bottom As={workflow.results['capacity'].outputs['tension_steel_area_mm2']:.9f} mm²; code minimum bottom As={workflow.results['capacity'].outputs['minimum_tension_steel_area_mm2']:.9f} mm². Moment-specific required As is not computed by this supplied-bar check; the actual moment demand/resistance is reported below.</p>
<h2>Required checks</h2><table><tr><th>Obligation</th><th>Result</th><th>Demand/required</th><th>Resistance/available/limit</th><th>Unit</th><th>Method and code-data revisions</th></tr>{checks}</table>{service_html}
<h2>Diagnostics</h2><table><tr><th>Owner</th><th>Code</th><th>Input/location</th><th>Reason</th></tr>{diagnostic_rows}</table>
<h2>Actual ordinary hooks</h2><table><tr><th>Hook path</th><th>Tail 1 mm</th><th>Tail 2 mm</th><th>Minimum mm</th><th>Pass</th></tr>{hook_rows}</table>
<h2>Flange provision</h2><p>State: {flange.engineering}; separate owner: {html.escape(str(flange.outputs.get('strip_owner_id','MISSING')))}; slab/web crossing lower bound: {flange.outputs.get('slab_web_crossing_clearance_lower_bound_mm','HOLD')} mm.</p>
<h2>Owned quantities</h2><p>{html.escape(json.dumps(quantities,sort_keys=True))}</p>
<h2>Actual beam paths</h2><p>Path result: {workflow.results['paths'].result_id}; BBS result: {workflow.results['bbs'].result_id}</p><table><tr><th>ID</th><th>Diameter mm</th><th>Developed length mm</th></tr>{path_rows}</table></html>"""
    (directory / "report.html").write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("main", "width-limited"), default="main")
    parser.add_argument(
        "--probe",
        choices=(
            "adequate",
            "overload",
            "insufficient-bars",
            "service-fail",
            "short-anchor",
            "short-hook",
            "missing-support",
            "missing-flange",
            "missing-service",
            "depth-conflict",
            "shoulder-bar",
            "end-cover",
        ),
        default="adequate",
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    workflow = run_workflow(case=args.case, probe=args.probe)
    if args.output_dir:
        write_artifacts(workflow, args.output_dir)
    member = workflow.results["member"].output_as("member_design", b.MemberDesignOutput)
    print(
        json.dumps(
            {
                "case": args.case,
                "probe": args.probe,
                "status": workflow.status,
                "member_engineering": workflow.results["member"].engineering.value,
                "member_completeness": workflow.results["member"].completeness.value,
                "qualified": sum(q.qualified for q in member.leaf_qualifications),
                "expected": len(member.expected_leaves),
                "issue_state": workflow.results["package"].outputs[
                    "calculation_package"
                ]["issue_state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
