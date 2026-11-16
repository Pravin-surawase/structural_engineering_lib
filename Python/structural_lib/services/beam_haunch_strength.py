"""Signed row and bend-force checks for the ordinary variable-depth cage."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Any

from structural_lib.beam.bar_paths import PathSegmentKind
from structural_lib.beam.detailing import (
    BarSurface,
    DevelopmentLengthRequest,
    StressState,
    development_length,
)
from structural_lib.beam.reinforcement import Face
from structural_lib.beam.semantics import EngineeringState
from structural_lib.codes.is456.column.detailing import (
    calculate_tie_spacing,
    minimum_tie_diameter,
)
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.beam_continuous import (
    BeamContinuousRowResultV1,
    _bar_positions,
    _centreline_issues,
    _check_row,
    _coverage_issues,
    _governing_rows,
    _row_issues,
    _sections,
    _support_faces,
)
from structural_lib.services.beam_haunch_geometry import (
    BeamHaunchDetailV1,
    HaunchGeometry,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousCheckRequestV1,
)


def check_haunch_station_strength(
    member: BeamContinuousCheckRequestV1,
    haunch: BeamHaunchDetailV1,
    geometry: HaunchGeometry,
) -> tuple[
    dict[str, Any], dict[str, Any], list[StructuralIssueV1], list[StructuralIssueV1]
]:
    """Evaluate the actual section and corrected shear on every signed row."""
    stations = {station.station_id: station for station in member.stations}
    kinds = {
        combination.combination_id: combination.kind
        for combination in member.combinations
    }
    raw_bars = _bar_positions(member)
    faces = _support_faces(member)
    centres = {support.centre_mm for support in member.supports}
    held, service = _coverage_issues(member, stations, require_all_uls_stations=True)
    failed: list[StructuralIssueV1] = []
    diameters = [bar.diameter_mm for bar in member.bars]
    if member.link_spacing_mm > calculate_tie_spacing(
        member.width_mm, min(point.depth_mm for point in haunch.outline), min(diameters)
    ) or member.link_diameter_mm < minimum_tie_diameter(max(diameters)):
        failed.append(
            StructuralIssueV1(
                "BEAM.HAUNCH_LINK_RESTRAINT_FAIL",
                "haunch.links",
                "The regular links do not meet the compression reinforcement pitch or diameter limits.",
            )
        )
    transition_sides = {(station.x_mm, station.side) for station in member.stations}
    if any(
        (point.station_mm, side) not in transition_sides
        for point in haunch.outline[1:-1]
        for side in ("LEFT", "RIGHT")
    ):
        held.append(
            StructuralIssueV1(
                "BEAM.HAUNCH_TRANSITION_ACTIONS_HELD",
                "member.stations",
                "Supply signed action stations on both sides of each soffit transition.",
            )
        )

    sections = {}
    rows = []
    evidence: list[dict[str, Any]] = []
    face_development: dict[str, float] = {}
    required = 0.0
    for action in sorted(
        member.actions,
        key=lambda item: (
            item.combination_id,
            stations[item.station_id].x_mm,
            stations[item.station_id].side,
        ),
    ):
        station = stations[action.station_id]
        x, kind = station.x_mm, kinds[action.combination_id]
        if kind != "ULS":
            rows.append(BeamContinuousRowResultV1(action, station, kind, x in centres))
            continue
        if x not in sections:
            depth, bottom = geometry.depth_at(x), geometry.bottom_axis_at(x)
            local = member.model_copy(update={"depth_mm": depth})
            bars = tuple(
                replace(bar, y_from_top_mm=bottom) if bar.face is Face.BOTTOM else bar
                for bar in raw_bars
            )
            arrangement, flexure, shear = _sections(local, bars)
            sections[x] = (depth, bottom, local, bars, arrangement, flexure, shear)
        depth, bottom, local, bars, arrangement, flexure, shear = sections[x]
        if arrangement.engineering is not EngineeringState.PASS or len(shear) != 2:
            failed.append(
                StructuralIssueV1(
                    "BEAM.HAUNCH_SECTION_FIT_FAIL",
                    f"member.stations.{station.station_id}",
                    "The actual section does not enclose the declared reinforcement.",
                )
            )
            rows.append(
                BeamContinuousRowResultV1(
                    action, station, kind, x in centres, section_status="FAIL"
                )
            )
            continue
        face = Face.TOP if action.mu_knm < 0 else Face.BOTTOM
        shear_face = (
            face
            if action.mu_knm
            else min(
                shear, key=lambda key: float(shear[key].outputs["provided_capacity_kn"])
            )
        )
        d = float(flexure[shear_face].outputs["effective_depth_mm"])
        slope = geometry.slope_at(x, station.side)
        # IS 456 §40.1.1. The moment magnitude grows toward the deeper
        # section when the signs of M, dM/dx (=V) and depth slope agree
        # in product. Only that sense reduces the nominal shear.
        adjustment = abs(action.mu_knm) * abs(slope) * 1000 / d
        if action.mu_knm * action.vu_kn * slope > 0:
            adjustment = -adjustment
        demand = abs(abs(action.vu_kn) + adjustment)
        support_face = faces.get(x)
        bottom_extents = None
        if support_face is not None and face is Face.BOTTOM:
            straight = next(
                (
                    segment
                    for segment in geometry.bottom_path
                    if segment.kind is PathSegmentKind.TANGENT_STRAIGHT
                    and segment.start.station_x_mm <= x <= segment.end.station_x_mm
                ),
                None,
            )
            if straight is None:
                held.append(
                    StructuralIssueV1(
                        "BEAM.HAUNCH_ANCHORAGE_HELD",
                        f"member.stations.{station.station_id}",
                        "Verify tension development from the support face along the actual curved bar.",
                    )
                )
                support_face = None
            else:
                bottom_extents = {
                    bar.bar_id: (straight.start.station_x_mm, straight.end.station_x_mm)
                    for bar in bars
                    if bar.face is Face.BOTTOM
                }
        row = _check_row(
            local,
            bars,
            action,
            station,
            kind,
            x in centres,
            support_face,
            flexure,
            shear,
            shear_demand_kn=demand,
            bar_extents=bottom_extents,
        )
        rows.append(row)
        if x in centres:
            continue
        evidence.append(
            {
                "row_id": action.row_id,
                "station_mm": x,
                "side": station.side,
                "depth_mm": depth,
                "bottom_axis_mm": bottom,
                "soffit_slope": slope,
                "moment_knm": action.mu_knm,
                "concurrent_shear_kn": action.vu_kn,
                "shear_adjustment_kn": adjustment,
                "shear_demand_kn": demand,
                "effective_depth_mm": d,
                "tension_face": face.value,
                "moment_capacity_knm": float(flexure[face].outputs["capacity_knm"]),
                "shear_capacity_kn": float(
                    shear[shear_face].outputs["provided_capacity_kn"]
                ),
                "nominal_shear_nmm2": demand * 1000 / (member.width_mm * d),
                "flexure_utilization": row.flexure_utilization,
                "shear_utilization": row.shear_utilization,
            }
        )
        if row.anchorage is not None:
            for anchor in row.anchorage.outputs.get("checks", ()):
                key = station.station_id
                length = anchor["available_straight_length_mm"]
                face_development[key] = min(length, face_development.get(key, math.inf))
                required = max(required, anchor["required_development_length_mm"])
    all_rows = tuple(rows)
    held.extend(_centreline_issues(member, all_rows))
    strength_failed, strength_held = _row_issues(all_rows, faces)
    failed.extend(strength_failed)
    held.extend(strength_held)
    status = "FAIL" if failed else "HOLD" if held else "PASS"
    strength = {
        "rows": [row.to_dict() for row in all_rows],
        "governing_rows": _governing_rows(all_rows),
        "ultimate_status": status,
        "serviceability_status": "HOLD" if service else "NOT_EVALUATED",
    }
    details = {
        "rows": evidence,
        "support_development_mm": face_development,
        "required_tension_development_mm": required,
    }
    return strength, details, failed, [*held, *service]


def check_haunch_bend_restraint(
    member: BeamContinuousCheckRequestV1,
    haunch: BeamHaunchDetailV1,
    geometry: HaunchGeometry,
) -> tuple[list[dict[str, Any]], list[StructuralIssueV1]]:
    """Check separately scheduled restraint, local bearing and projected development."""
    bottom_bars = [bar for bar in member.bars if bar.face == "bottom"]
    diameter = bottom_bars[0].diameter_mm
    bar_force = 0.87 * member.fy_nmm2 * math.pi * diameter**2 / 4
    leg_force = (
        0.87 * min(member.link_fy_nmm2, 415) * math.pi * member.link_diameter_mm**2 / 4
    )
    developed = development_length(
        DevelopmentLengthRequest(
            member.schema_version,
            diameter,
            0.87 * member.fy_nmm2,
            member.fy_nmm2,
            member.fck_nmm2,
            BarSurface.DEFORMED,
            StressState.COMPRESSION,
        )
    )
    if developed.engineering is not EngineeringState.PASS:
        return [], [
            StructuralIssueV1(
                "BEAM.HAUNCH_BASIS_HELD",
                "member.bars",
                "Supply a supported compression development basis for the rounded bars.",
            )
        ]
    required = float(developed.outputs["required_development_length_mm"])
    end = member.straight_bars
    assert end is not None
    bend_nodes = haunch.bottom_bar_path[1:-1]
    bends = [segment for segment in geometry.bottom_segments if "centre" in segment]
    reserve = {link.station_mm for link in haunch.links if link.purpose == "bend"}
    groups = haunch.bend_restraint or ()
    by_node = {group.node_id: group.link_stations_mm for group in groups}
    group_stations = [x for group in groups for x in group.link_stations_mm]
    if (
        {node.node_id for node in bend_nodes} != by_node.keys()
        or len(groups) != len(by_node)
        or len(group_stations) != len(set(group_stations))
        or set(group_stations) != reserve
        or len(bends) != len(bend_nodes)
    ):
        return [], [
            StructuralIssueV1(
                "BEAM.HAUNCH_BASIS_HELD",
                "haunch.bend_restraint",
                "Bind each actual bend and dedicated link exactly once in the restraint schedule.",
            )
        ]
    side_axis = min(
        min(bar.x_from_left_mm, member.width_mm - bar.x_from_left_mm)
        for bar in bottom_bars
    )
    cover = min(side_axis - diameter / 2, geometry.bottom_bar_soffit_cover_bound_mm)
    bearing_limit = 1.5 * member.fck_nmm2 / (1 + 2 * diameter / (cover + diameter))
    checks = []
    issues = []
    for node, bend in zip(bend_nodes, bends, strict=True):
        stations = by_node[node.node_id]
        tangent = [bend["start"][0], bend["end"][0]]
        radius = bend["radius_mm"]
        turn = bend["length_mm"] / radius
        demand = 2 * bar_force * math.sin(turn / 2) / 1000
        capacity = len(stations) * leg_force / 1000
        bearing = bar_force / ((radius - diameter / 2) * diameter)
        available = min(tangent[0] - end.start_mm, end.end_mm - tangent[1])
        brackets_bend = (
            len(stations) == 2
            and stations[0] < tangent[0] < tangent[1] < stations[1]
            and stations[1] - stations[0] <= member.link_spacing_mm
        )
        if (
            not brackets_bend
            or capacity < demand
            or bearing > bearing_limit
            or available < required
        ):
            issues.append(
                StructuralIssueV1(
                    "BEAM.HAUNCH_BEND_RESTRAINT_FAIL",
                    f"haunch.bend_restraint.{node.node_id}",
                    "The rounded bar bend fails its dedicated local restraint, bearing or development check.",
                )
            )
        checks.append(
            {
                "node_id": node.node_id,
                "link_stations_mm": list(stations),
                "tangent_x_mm": tangent,
                "demand_per_bar_kn": demand,
                "resistance_per_bar_kn": capacity,
                "bearing_nmm2": bearing,
                "bearing_limit_nmm2": bearing_limit,
                "minimum_projected_development_mm": available,
                "required_compression_development_mm": required,
            }
        )
    return checks, issues
