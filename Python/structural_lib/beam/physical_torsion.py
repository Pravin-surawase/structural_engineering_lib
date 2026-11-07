"""Physical evidence operations for the ordinary rectangular torsion profile.

Support transfer stops at the receiving crosshead's section-strength boundary.
It does not design that crosshead's end supports, bearings or foundation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.beam.detailing import (
    check_min_spacing,
    mild_exposure_limits,
    ordinary_link_anchorage_limits,
)

from .analysis import (
    ACTION_NORMALIZE_OPERATION,
    BeamLineRequest,
    BeamTopologyRequest,
    define_beam_topology,
    solve_beam_line,
)
from .bar_paths import (
    BarPathOutput,
    BarPathRequest,
    BarPathRole,
    BendKind,
    PathSegmentKind,
    ResolvedBarPath,
    resolve_bar_paths,
)
from .detailing import (
    LinkCage,
    ReinforcementArrangementCheckRequest,
    check_reinforcement_arrangement,
)
from .flexure import (
    FlexuralCapacityRequest,
    FlexureCheckRequest,
    SectionKind,
    check_flexure,
)
from .reinforcement import ReinforcementGeometryRequest, evaluate_geometry
from .semantics import (
    CompletenessState,
    Diagnostic,
    EngineeringState,
    ExecutionState,
    FreshnessState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_applicable_result,
    not_evaluated_result,
    rejected_result,
)
from .shear_torsion import (
    ShearAxis,
    ShearCapacityRequest,
    ShearCheckRequest,
    ShearDemand,
    TransverseLink,
    check_shear,
)

LINK_DETAIL_OPERATION = "is456.beam.closed_link_detail.check/v1"
DURABILITY_OPERATION = "is456.beam.mild_durability.check/v1"
TRANSFER_OPERATION = "structural.beam.torsion_support_transfer.check/v1"
CODE_REVISION = "is456-physical-torsion-d2-v1"


@dataclass(frozen=True)
class MildDurabilityRequest:
    profile_id: str
    reinforcement_revision_id: str
    concrete_grade_nmm2: float
    nominal_cover_mm: float
    largest_bar_diameter_mm: float
    cement_content_kg_per_m3: float
    water_cement_ratio: float
    cement_type: str
    maximum_aggregate_size_mm: float = 20
    exposure: str = "mild"


@dataclass(frozen=True)
class ClosedLinkDetailRequest:
    paths: BarPathRequest
    cage: LinkCage
    link: TransverseLink
    arrangement: ReinforcementArrangementCheckRequest
    required_start_mm: float
    required_end_mm: float


@dataclass(frozen=True)
class BearingReactionLine:
    line_id: str
    receiver_station_mm: float
    upward_reaction_kn: float


@dataclass(frozen=True)
class TorqueSupportDetail:
    support_id: str
    source_row_id: str
    source_station_mm: float
    vertical_reaction_kn: float
    external_torque_reaction_knm: float
    receiver_topology: BeamTopologyRequest
    receiver_analysis: BeamLineRequest
    receiver_section: FlexuralCapacityRequest
    receiver_links: TransverseLink
    receiver_nominal_cover_mm: float
    receiver_unit_weight_kn_per_m3: float
    receiver_self_weight_factor: float
    receiver_maximum_aggregate_size_mm: float
    bearing_lines: tuple[BearingReactionLine, ...]
    torque_reference_station_mm: float
    load_path_reference: str


@dataclass(frozen=True)
class TorsionSupportTransferRequest:
    profile_id: str
    member_id: str
    reinforcement_revision_id: str
    action_snapshot: OperationResult
    primary_topology: BeamTopologyRequest
    primary_section: FlexuralCapacityRequest
    primary_paths: BarPathRequest
    applied_vertical_load_kn: float
    applied_torque_knm: float
    supports: tuple[TorqueSupportDetail, ...]


def _diag(operation: str, code: str, field: str, message: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        operation,
        field,
        "physical-torsion-d2",
        "Resolve the named physical evidence and rerun the dependent member checks.",
    )


def _provenance(operation: str) -> Provenance:
    return Provenance(
        CODE_REVISION,
        operation.replace("/v1", "-d2-v1"),
        (
            "IS 456:2000 through Amendment 6; Cl. 26.2.2.4(b), 26.4.1-26.4.2, 41; Tables 5 and 16",
            "Right-handed force and torque equilibrium; receiving section flexure/shear",
            "IS 456 Amendment 6:2024 Cl. 8.2.4.2 and Table 5 cement-specific provisions",
        ),
    )


def _positive(value: float) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def _passed(result: OperationResult) -> bool:
    return (
        result.execution is ExecutionState.COMPLETED
        and result.engineering is EngineeringState.PASS
    )


def _crossing_clearance_mm(
    x: float, y: float, diameter: float, path: ResolvedBarPath
) -> float | None:
    """Conservative surface clearance to a transverse receiver bar axis.

    Project primary segments onto member-station/depth coordinates. Straight
    projection distance is exact for an extended transverse axis; a projected
    arc lies inside its centre/radius disk, giving a conservative lower bound.
    """
    gaps = []
    for segment in path.segments:
        if segment.kind is PathSegmentKind.BEND_ARC:
            centre, radius = segment.bend_centre, segment.bend_radius_mm
            if centre is None or radius is None:
                return None
            distance = max(
                0.0,
                math.hypot(x - centre.station_x_mm, y - centre.section_y_from_top_mm)
                - radius,
            )
        else:
            start, end = segment.start, segment.end
            dx = end.station_x_mm - start.station_x_mm
            dy = end.section_y_from_top_mm - start.section_y_from_top_mm
            length2 = dx * dx + dy * dy
            fraction = (
                max(
                    0.0,
                    min(
                        1.0,
                        (
                            (x - start.station_x_mm) * dx
                            + (y - start.section_y_from_top_mm) * dy
                        )
                        / length2,
                    ),
                )
                if length2
                else 0.0
            )
            distance = math.hypot(
                x - start.station_x_mm - fraction * dx,
                y - start.section_y_from_top_mm - fraction * dy,
            )
        gaps.append(distance - (diameter + path.diameter_mm) / 2)
    return min(gaps) if gaps else None


def check_mild_durability(request: MildDurabilityRequest) -> OperationResult:
    """Check supplied mix/cover against the named mild, 20 mm aggregate profile."""
    op = DURABILITY_OPERATION
    inputs, provenance = effective_inputs(request=request), _provenance(op)
    if (
        request.exposure != "mild"
        or request.maximum_aggregate_size_mm != 20
        or request.cement_type
        not in ("ordinary_portland", "portland_calcined_clay_limestone")
    ):
        return not_applicable_result(
            op,
            inputs,
            _diag(
                op,
                "PROFILE.UNSUPPORTED",
                "exposure,aggregate",
                "This operation qualifies mild exposure, 20 mm aggregate and explicitly named ordinary Portland or calcined-clay-limestone cement.",
            ),
            provenance=provenance,
        )
    if (
        not request.profile_id
        or not request.reinforcement_revision_id
        or not all(
            _positive(v)
            for v in (
                request.concrete_grade_nmm2,
                request.nominal_cover_mm,
                request.largest_bar_diameter_mm,
                request.cement_content_kg_per_m3,
                request.water_cement_ratio,
            )
        )
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "INPUT.INVALID",
                    "request",
                    "Finite positive values and current identities are required.",
                ),
            ),
            provenance=provenance,
        )
    limits = mild_exposure_limits(request.largest_bar_diameter_mm, request.cement_type)
    checks = {
        "cover_pass": request.nominal_cover_mm >= limits["minimum_cover_mm"],
        "grade_pass": request.concrete_grade_nmm2 >= limits["minimum_grade_nmm2"],
        "cement_pass": limits["minimum_cement_kg_per_m3"]
        <= request.cement_content_kg_per_m3
        <= limits["maximum_cement_without_special_consideration_kg_per_m3"],
        "water_cement_pass": request.water_cement_ratio
        <= limits["maximum_water_cement_ratio"],
    }
    return completed_result(
        op,
        inputs,
        {**limits, **checks},
        engineering=(
            EngineeringState.PASS if all(checks.values()) else EngineeringState.FAIL
        ),
        diagnostics=tuple(
            _diag(
                op,
                "DURABILITY." + k.upper(),
                k,
                "Supplied mix or cover fails the applicable requirement.",
            )
            for k, v in checks.items()
            if not v
        ),
        provenance=provenance,
    )


def check_closed_link_detail(request: ClosedLinkDetailRequest) -> OperationResult:
    """Check actual two-90-degree-hook link paths against their declared cage.

    The admitted fabrication shape has five tangent bends and two separated
    hook planes. Other shapes need their own geometry qualification.
    """
    op = LINK_DETAIL_OPERATION
    inputs, provenance = effective_inputs(request=request), _provenance(op)
    result = resolve_bar_paths(request.paths)
    if not _passed(result):
        return not_evaluated_result(
            op,
            inputs,
            _diag(
                op,
                "PATHS.REQUIRED",
                "paths",
                "Current valid physical paths are required.",
            ),
            provenance=provenance,
        )
    link, cage = request.link, request.cage
    if (
        not all(_positive(v) for v in (link.diameter_mm, link.spacing_mm))
        or not request.required_start_mm < request.required_end_mm
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "INPUT.INVALID",
                    "link,range",
                    "Positive link size/pitch and an ordered scope are required.",
                ),
            ),
            provenance=provenance,
        )
    schedule = result.output_as("reinforcement_schedule", BarPathOutput)
    actual = {p.bar_id: p for p in schedule.paths}
    seeds = [p for p in request.paths.paths if p.role is BarPathRole.TRANSVERSE_LINK]
    if not seeds:
        return not_evaluated_result(
            op,
            inputs,
            _diag(
                op, "LINKS.REQUIRED", "paths", "Actual fabricated links are required."
            ),
            provenance=provenance,
        )
    diagnostics: list[Diagnostic] = []
    arrangement = request.arrangement
    main_seeds = {
        p.bar_id: p
        for p in request.paths.paths
        if p.role in (BarPathRole.TOP_LONGITUDINAL, BarPathRole.BOTTOM_LONGITUDINAL)
    }
    path_binding = (
        arrangement.member_id == request.paths.member_id
        and arrangement.reinforcement_revision_id == request.paths.detail_revision_id
        and arrangement.section_width_mm == request.paths.section_width_mm
        and arrangement.section_depth_mm == request.paths.section_depth_mm
        and arrangement.links == (cage,)
        and len(main_seeds) == len(arrangement.bars) == 4
        and _passed(check_reinforcement_arrangement(arrangement))
    )
    for bar in arrangement.bars:
        seed = main_seeds.get(bar.bar_id)
        path_binding = path_binding and seed is not None
        if seed is None:
            continue
        path_binding = (
            path_binding
            and len(seed.nodes) == 2
            and seed.diameter_mm == bar.diameter_mm
            and seed.bar_mark == bar.bar_mark
        )
        path_binding = path_binding and all(
            n.point.section_x_from_left_mm == bar.x_from_left_mm
            and n.point.section_y_from_top_mm == bar.y_from_top_mm
            for n in seed.nodes
        )
        path_binding = (
            path_binding
            and seed.nodes[0].point.station_x_mm == bar.start_station_mm
            and seed.nodes[-1].point.station_x_mm == bar.end_station_mm
        )
    if not path_binding:
        diagnostics.append(
            _diag(
                op,
                "LINK.LONGITUDINAL_PATH_BINDING",
                "paths,arrangement",
                "Four actual continuous bar paths must match the checked cage arrangement and revision.",
            )
        )
    expected = (
        (cage.left_centre_x_mm, cage.top_centre_y_mm),
        (cage.left_centre_x_mm, cage.bottom_centre_y_mm),
        (cage.right_centre_x_mm, cage.bottom_centre_y_mm),
        (cage.right_centre_x_mm, cage.top_centre_y_mm),
        (cage.left_centre_x_mm, cage.top_centre_y_mm),
    )
    binding = (
        cage.closed
        and link.closed
        and link.link_id == cage.link_id
        and link.diameter_mm == cage.diameter_mm
        and link.legs_v2 == 2
        and link.legs_v3 == 2
        and math.isclose(
            link.centre_width_mm,
            cage.right_centre_x_mm - cage.left_centre_x_mm,
            abs_tol=1e-9,
        )
        and math.isclose(
            link.centre_depth_mm,
            cage.bottom_centre_y_mm - cage.top_centre_y_mm,
            abs_tol=1e-9,
        )
    )
    if not binding:
        diagnostics.append(
            _diag(
                op,
                "LINK.CAGE_BINDING",
                "cage,link",
                "Strength link and physical cage must identify the same closed two-leg link.",
            )
        )
    checks: list[dict[str, object]] = []
    stations: list[float] = []
    for seed in seeds:
        path = actual[seed.bar_id]
        corners = seed.nodes[1:-1]
        shape = (
            len(seed.nodes) == 7
            and not seed.closed
            and seed.diameter_mm == link.diameter_mm
            and seed.steel_grade_n_per_mm2 == link.steel_yield_strength_n_per_mm2
        )
        shape = shape and all(
            math.isclose(n.point.section_x_from_left_mm, x, abs_tol=1e-9)
            and math.isclose(n.point.section_y_from_top_mm, y, abs_tol=1e-9)
            for n, (x, y) in zip(corners, expected, strict=True)
        )
        arcs = [s for s in path.segments if s.kind is PathSegmentKind.BEND_ARC]
        hooks = [s for s in arcs if s.bend_kind is BendKind.HOOK]
        shape = (
            shape
            and len(arcs) == 5
            and len(hooks) == 2
            and hooks[0] == arcs[0]
            and hooks[-1] == arcs[-1]
        )
        if not shape:
            diagnostics.append(
                _diag(
                    op,
                    "LINK.SHAPE",
                    seed.bar_id,
                    "The physical path does not match the admitted closed-cage fabrication shape.",
                )
            )
            continue
        minimum_tail, minimum_radius = ordinary_link_anchorage_limits(
            link.diameter_mm, 90
        )
        tails = (
            path.segments[0].centreline_length_mm,
            path.segments[-1].centreline_length_mm,
        )
        radius_ok = all(
            s.bend_radius_mm is not None
            and s.bend_radius_mm - link.diameter_mm / 2 >= minimum_radius - 1e-9
            for s in arcs
        )
        radius_ok = radius_ok and all(
            math.isclose(
                (s.bend_radius_mm or 0) - link.diameter_mm / 2,
                cage.internal_bend_radius_mm,
                abs_tol=1e-9,
            )
            for s in arcs
        )
        angle_ok = all(
            math.isclose(s.bend_angle_degrees or 0, 90, abs_tol=1e-8) for s in hooks
        )
        planes_ok = (
            abs(corners[0].point.station_x_mm - corners[-1].point.station_x_mm)
            >= link.diameter_mm
        )
        passed = (
            min(tails) >= minimum_tail - 1e-9 and radius_ok and angle_ok and planes_ok
        )
        if not passed:
            diagnostics.append(
                _diag(
                    op,
                    "LINK.HOOK_DETAIL",
                    seed.bar_id,
                    "Actual tangent tails, bend radius or hook-plane clearance fail the declared ordinary detail.",
                )
            )
        stations.append(corners[0].point.station_x_mm)
        checks.append(
            {
                "bar_id": seed.bar_id,
                "tails_mm": tails,
                "minimum_tail_mm": minimum_tail,
                "minimum_internal_radius_mm": minimum_radius,
                "passed": passed,
            }
        )
    stations.sort()
    placement = (
        bool(stations)
        and stations[0] <= request.required_start_mm + link.spacing_mm / 2 + 1e-9
        and stations[-1] >= request.required_end_mm - link.spacing_mm / 2 - 1e-9
        and all(
            math.isclose(b - a, link.spacing_mm, rel_tol=0, abs_tol=1e-9)
            for a, b in zip(stations, stations[1:], strict=False)
        )
    )
    if not placement:
        diagnostics.append(
            _diag(
                op,
                "LINK.PLACEMENT",
                "paths",
                "Actual link stations do not cover the required interval at the checked pitch.",
            )
        )
    return completed_result(
        op,
        inputs,
        {
            "path_result_id": result.result_id,
            "detail_revision_id": schedule.detail_revision_id,
            "checks": checks,
            "placement_pass": placement,
        },
        engineering=EngineeringState.FAIL if diagnostics else EngineeringState.PASS,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def check_torsion_support_transfer(
    request: TorsionSupportTransferRequest,
) -> OperationResult:
    """Verify signed couples and their receiving crosshead section strength.

    Right-handed e1 along primary member, e2 vertically up, e3 transverse:
    external primary torque is minus sum(upward reaction * transverse arm).
    The receiver takes the opposite downward loads. Its own end reactions
    are this operation's supporting-system boundary. Primary and receiver
    section depths share the same physical top datum in this profile.
    """
    op = TRANSFER_OPERATION
    inputs, provenance = effective_inputs(request=request), _provenance(op)
    snapshot = request.action_snapshot
    if (
        not _passed(snapshot)
        or snapshot.operation_semantic_id != ACTION_NORMALIZE_OPERATION
        or snapshot.freshness is not FreshnessState.CURRENT
        or snapshot.completeness is not CompletenessState.COMPLETE_FOR_SCOPE
        or not request.supports
    ):
        return not_evaluated_result(
            op,
            inputs,
            _diag(
                op,
                "SUPPORT.EVIDENCE_REQUIRED",
                "supports,actions",
                "Current source actions and actual torsion-transfer details are required.",
            ),
            provenance=provenance,
        )
    rows = {r["source_row_id"]: r for r in snapshot.outputs.get("rows", ())}
    primary = request.primary_topology
    primary_path_result = resolve_bar_paths(request.primary_paths)
    path_request = request.primary_paths
    if (
        not _passed(primary_path_result)
        or path_request.member_id != request.member_id
        or path_request.profile_id != request.profile_id
        or path_request.detail_revision_id != request.reinforcement_revision_id
        or path_request.section_width_mm != request.primary_section.web_width_mm
        or path_request.section_depth_mm != request.primary_section.depth_mm
        or path_request.topology_revision_id != define_beam_topology(primary).result_id
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "SUPPORT.PATH_BINDING",
                    "primary_paths",
                    "Receiver clearance requires the same current primary physical paths and topology.",
                ),
            ),
            provenance=provenance,
        )
    primary_schedule = primary_path_result.output_as(
        "reinforcement_schedule", BarPathOutput
    )
    main_seeds = {
        p.bar_id: p
        for p in path_request.paths
        if p.role in (BarPathRole.TOP_LONGITUDINAL, BarPathRole.BOTTOM_LONGITUDINAL)
    }
    section_binding = set(main_seeds) == {
        bar.bar_id for bar in request.primary_section.bars
    }
    for bar in request.primary_section.bars:
        seed = main_seeds.get(bar.bar_id)
        section_binding = section_binding and seed is not None
        if seed is not None:
            section_binding = (
                section_binding
                and seed.diameter_mm == bar.diameter_mm
                and all(
                    node.point.section_x_from_left_mm == bar.x_from_left_mm
                    and node.point.section_y_from_top_mm == bar.y_from_top_mm
                    for node in seed.nodes
                )
            )
    if not section_binding:
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "SUPPORT.PRIMARY_SECTION_BINDING",
                    "primary_paths,primary_section",
                    "Receiver clearance must use all actual primary section bars at their checked coordinates.",
                ),
            ),
            provenance=provenance,
        )
    if (
        not _passed(define_beam_topology(primary))
        or primary.member_id != request.member_id
        or len(primary.supports) != 2
        or {s.support_id for s in primary.supports}
        != {s.support_id for s in request.supports}
        or len({r["load_case_id"] for r in rows.values()}) != 1
        or request.primary_section.profile_id != request.profile_id
        or request.primary_section.section_kind is not SectionKind.RECTANGULAR
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "SUPPORT.TOPOLOGY_BINDING",
                    "topology",
                    "The two physical primary supports and one source load case must bind the transfer scope.",
                ),
            ),
            provenance=provenance,
        )
    if not _positive(request.applied_vertical_load_kn) or not math.isfinite(
        request.applied_torque_knm
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "INPUT.INVALID",
                    "loads",
                    "Declared applied loads must be finite with a positive vertical resultant.",
                ),
            ),
            provenance=provenance,
        )
    if len(request.supports) != 2 or len({s.support_id for s in request.supports}) != 2:
        return rejected_result(
            op,
            inputs,
            (
                _diag(
                    op,
                    "SUPPORT.IDENTITY",
                    "supports",
                    "This profile requires two distinct end supports.",
                ),
            ),
            provenance=provenance,
        )
    diagnostics: list[Diagnostic] = []
    checks: list[dict[str, object]] = []
    couples: list[float] = []
    reactions: list[float] = []
    for index, support in enumerate(
        sorted(request.supports, key=lambda s: s.source_station_mm)
    ):
        row = rows.get(support.source_row_id)
        physical = next(
            s for s in primary.supports if s.support_id == support.support_id
        )
        if (
            row is None
            or row["member_id"] != request.member_id
            or row["axis_id"] != primary.local_axes.axis_id
            or row["concurrency"] != "static_concurrent"
            or not math.isclose(
                row["object_station_mm"], support.source_station_mm, abs_tol=1e-9
            )
            or not math.isclose(
                support.source_station_mm, physical.centre_x_mm, abs_tol=1e-9
            )
            or not support.load_path_reference
        ):
            return rejected_result(
                op,
                inputs,
                (
                    _diag(
                        op,
                        "SUPPORT.ACTION_BINDING",
                        support.support_id,
                        "Support forces must bind the same member, station and concurrent source row.",
                    ),
                ),
                provenance=provenance,
            )
        lines = support.bearing_lines
        if (
            len(lines) != 2
            or len({line.line_id for line in lines}) != 2
            or not all(
                _positive(line.upward_reaction_kn)
                and math.isfinite(line.receiver_station_mm)
                for line in lines
            )
            or lines[0].receiver_station_mm == lines[1].receiver_station_mm
        ):
            return rejected_result(
                op,
                inputs,
                (
                    _diag(
                        op,
                        "SUPPORT.REACTION_LINES",
                        support.support_id,
                        "Two distinct compression-only bearing lines with positive reactions are required.",
                    ),
                ),
                provenance=provenance,
            )
        if any(
            abs(line.receiver_station_mm - support.torque_reference_station_mm)
            > request.primary_section.web_width_mm / 2
            for line in lines
        ):
            return rejected_result(
                op,
                inputs,
                (
                    _diag(
                        op,
                        "SUPPORT.BEARING_FOOTPRINT",
                        support.support_id,
                        "The bearing reaction lines must lie under the primary beam footprint.",
                    ),
                ),
                provenance=provenance,
            )
        couple = (
            -sum(
                line.upward_reaction_kn
                * (line.receiver_station_mm - support.torque_reference_station_mm)
                for line in lines
            )
            / 1000
        )
        force = sum(line.upward_reaction_kn for line in lines)
        expected_torque = (-1 if index == 0 else 1) * row["t_nmm"] / 1e6
        balance = (
            math.isclose(force, support.vertical_reaction_kn, abs_tol=1e-8)
            and math.isclose(force, abs(row["v2_n"]) / 1000, abs_tol=1e-8)
            and math.isclose(couple, support.external_torque_reaction_knm, abs_tol=1e-8)
            and math.isclose(couple, expected_torque, abs_tol=1e-8)
        )
        if not balance:
            diagnostics.append(
                _diag(
                    op,
                    "SUPPORT.COUPLE_EQUILIBRIUM",
                    support.support_id,
                    "The actual bearing forces do not reproduce the signed source end actions.",
                )
            )
        analysis = support.receiver_analysis
        # The pair loads must be the actual loads solved for this receiver.
        point_rows = sorted(
            (p.distance_from_start_mm, p.vertical_force_n) for p in analysis.point_loads
        )
        expected_loads = sorted(
            (p.receiver_station_mm, -p.upward_reaction_kn * 1000) for p in lines
        )
        topology = define_beam_topology(support.receiver_topology)
        self_weight = (
            support.receiver_section.web_width_mm
            * support.receiver_section.depth_mm
            * support.receiver_unit_weight_kn_per_m3
            * support.receiver_self_weight_factor
            / 1e6
        )
        receiver_positions = sorted(
            s.centre_x_mm for s in support.receiver_topology.supports
        )
        valid_receiver = (
            _passed(topology)
            and len(analysis.elements) == 1
            and len(analysis.nodes) == 2
            and _positive(support.receiver_unit_weight_kn_per_m3)
            and _positive(support.receiver_self_weight_factor)
            and _positive(support.receiver_maximum_aggregate_size_mm)
            and math.isclose(
                analysis.elements[0].uniform_load_n_per_mm,
                -self_weight,
                rel_tol=0,
                abs_tol=1e-9,
            )
            and all(
                n.nodal_force_n == 0
                and n.nodal_moment_nmm == 0
                and n.vertical_restraint
                and not n.rotation_restraint
                for n in analysis.nodes
            )
            and point_rows == expected_loads
        )
        valid_receiver = (
            valid_receiver
            and receiver_positions == sorted(n.x_mm for n in analysis.nodes)
            and receiver_positions[0] == 0
            and analysis.load_case_id == row["load_case_id"]
            and support.receiver_section.web_width_mm
            >= physical.right_face_x_mm - physical.left_face_x_mm
        )
        valid_receiver = (
            valid_receiver
            and analysis.model_id == support.receiver_topology.member_id
            and support.receiver_section.profile_id == request.profile_id
        )
        receiver_axes = support.receiver_topology.local_axes
        valid_receiver = (
            valid_receiver
            and receiver_axes.e1 == primary.local_axes.e3
            and receiver_axes.e2 == primary.local_axes.e2
        )
        valid_receiver = (
            valid_receiver
            and receiver_positions[-1] - receiver_positions[0]
            >= 2 * support.receiver_section.depth_mm
            and support.receiver_section.section_kind is SectionKind.RECTANGULAR
        )
        if valid_receiver:
            mapping = support.receiver_topology.analysis_elements
            element = analysis.elements[0]
            valid_receiver = (
                len(mapping) == 1
                and element.analysis_element_id == mapping[0].analysis_element_id
                and element.physical_span_id == mapping[0].physical_span_id
            )
            nodes = {n.node_id: n for n in analysis.nodes}
            valid_receiver = (
                valid_receiver
                and element.start_node_id in nodes
                and element.end_node_id in nodes
            )
            if valid_receiver:
                valid_receiver = (
                    nodes[element.start_node_id].x_mm == mapping[0].start_x_mm
                    and nodes[element.end_node_id].x_mm == mapping[0].end_x_mm
                )
            valid_receiver = (
                valid_receiver
                and support.receiver_links.closed
                and 0
                < support.receiver_links.centre_width_mm
                < support.receiver_section.web_width_mm
                and 0
                < support.receiver_links.centre_depth_mm
                < support.receiver_section.depth_mm
            )
        if not valid_receiver:
            return rejected_result(
                op,
                inputs,
                (
                    _diag(
                        op,
                        "SUPPORT.RECEIVER_BINDING",
                        support.support_id,
                        "Receiver topology and actual point loads must describe the supplied bearing pair.",
                    ),
                ),
                provenance=provenance,
            )
        solved = solve_beam_line(analysis)
        if (
            solved.execution is not ExecutionState.COMPLETED
            or "stations" not in solved.outputs
        ):
            return not_evaluated_result(
                op,
                inputs,
                _diag(
                    op,
                    "SUPPORT.RECEIVER_REQUIRED",
                    support.support_id,
                    "Receiver analysis must complete before transfer can qualify.",
                ),
                provenance=provenance,
            )
        stations = solved.outputs["stations"]
        moment = max(abs(r["m3_nmm"]) for r in stations) / 1e6
        shear = max(abs(r["v2_n"]) for r in stations) / 1000
        section = support.receiver_section
        geometry = evaluate_geometry(
            ReinforcementGeometryRequest(
                request.profile_id,
                section.web_width_mm,
                section.depth_mm,
                support.receiver_nominal_cover_mm,
                support.receiver_links.diameter_mm,
                max(25, max((p.diameter_mm for p in section.bars), default=25)),
                section.bars,
            )
        )
        gaps = []
        crossing_pass = True
        for bar in section.bars:
            for path in primary_schedule.paths:
                gap = _crossing_clearance_mm(
                    physical.left_face_x_mm + bar.x_from_left_mm,
                    bar.y_from_top_mm,
                    bar.diameter_mm,
                    path,
                )
                if gap is None:
                    crossing_pass = False
                    continue
                gaps.append(gap)
                diameter = max(bar.diameter_mm, path.diameter_mm)
                passed, _ = check_min_spacing(
                    gap + diameter, diameter, support.receiver_maximum_aggregate_size_mm
                )
                crossing_pass = crossing_pass and passed
        if not crossing_pass:
            diagnostics.append(
                _diag(
                    op,
                    "SUPPORT.RECEIVER_BAR_CLEARANCE",
                    support.support_id,
                    "Receiver bars do not meet the conservative crossing-clearance criterion against actual primary paths.",
                )
            )
        flexure = check_flexure(
            FlexureCheckRequest(section, positive_design_moment_knm=moment)
        )
        area = sum(
            math.pi * p.diameter_mm**2 / 4
            for p in section.bars
            if p.face.value == "bottom"
        )
        depth = (
            sum(
                math.pi * p.diameter_mm**2 / 4 * p.y_from_top_mm
                for p in section.bars
                if p.face.value == "bottom"
            )
            / area
            if area
            else 0
        )
        shear_result = check_shear(
            ShearCheckRequest(
                (
                    ShearCapacityRequest(
                        request.profile_id,
                        ShearAxis.V2,
                        section.web_width_mm,
                        depth,
                        section.concrete_strength_n_per_mm2,
                        area,
                        support.receiver_links,
                    ),
                ),
                (ShearDemand(support.support_id, ShearAxis.V2, shear),),
            )
        )
        if not _passed(geometry) or not _passed(flexure) or not _passed(shear_result):
            diagnostics.append(
                _diag(
                    op,
                    "SUPPORT.RECEIVER_STRENGTH",
                    support.support_id,
                    "The actual receiving crosshead fails section flexure or shear qualification.",
                )
            )
        couples.append(couple)
        reactions.append(force)
        checks.append(
            {
                "support_id": support.support_id,
                "source_row_id": support.source_row_id,
                "source_row_identity": row["row_id"],
                "force_kn": force,
                "external_torque_knm": couple,
                "couple_pass": balance,
                "receiver_topology_result_id": topology.result_id,
                "receiver_geometry": geometry.to_dict(),
                "receiver_analysis": solved.to_dict(),
                "receiver_flexure": flexure.to_dict(),
                "receiver_shear": shear_result.to_dict(),
                "receiver_moment_knm": moment,
                "receiver_shear_kn": shear,
                "receiver_factored_self_weight_n_per_mm": self_weight,
                "minimum_receiver_primary_bar_clearance_mm": (
                    min(gaps) if gaps else None
                ),
                "receiver_bar_crossing_pass": crossing_pass,
                "primary_path_result_id": primary_path_result.result_id,
            }
        )
    equilibrium = math.isclose(
        sum(couples) + request.applied_torque_knm, 0, abs_tol=1e-8
    ) and math.isclose(sum(reactions), request.applied_vertical_load_kn, abs_tol=1e-8)
    if not equilibrium:
        diagnostics.append(
            _diag(
                op,
                "SUPPORT.GLOBAL_EQUILIBRIUM",
                "supports",
                "Support resultants do not balance the declared total applied forces and torque.",
            )
        )
    return completed_result(
        op,
        inputs,
        {
            "action_snapshot_id": snapshot.result_id,
            "checks": checks,
            "global_equilibrium_pass": equilibrium,
            "boundary": "Receiving crosshead section flexure/shear; receiver end-support, bearing/contact and foundation design are separate supporting-system checks.",
        },
        engineering=EngineeringState.FAIL if diagnostics else EngineeringState.PASS,
        diagnostics=diagnostics,
        provenance=provenance,
    )
