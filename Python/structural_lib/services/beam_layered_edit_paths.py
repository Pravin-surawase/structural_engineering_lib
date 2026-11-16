"""Physical open centre-cross-tie paths for the bounded FLOW03 edit profile."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING

from structural_lib.beam.bar_paths import (
    BarPathRole,
    BarPathSeed,
    BendKind,
    PathNode,
    PathPoint,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
)

if TYPE_CHECKING:
    from structural_lib.services.beam_layered_edit_placement import BeamCentreCrossTieV1


def centre_cross_tie_paths(
    member: BeamLayeredContinuousCheckRequestV1,
    cross_tie: BeamCentreCrossTieV1,
    stations_mm: tuple[float, ...],
) -> tuple[BarPathSeed, ...]:
    """Return one two-hook open cross-tie seed at each outer-hoop station.

    The open tie runs beside the declared, vertically aligned restrained pair.
    Its internal bend radius is converted to the centreline radius required by
    :func:`resolve_bar_paths`; the end tails remain explicit straight segments.
    """
    by_id = {bar.bar_id: bar for bar in member.bars}
    top_id, bottom_id = cross_tie.restrained_bar_ids
    top, bottom = by_id[top_id], by_id[bottom_id]
    if not math.isclose(top.x_from_left_mm, bottom.x_from_left_mm, abs_tol=1e-9):
        raise ValueError(
            "Centre cross-tie restrained bars must share one vertical axis."
        )
    if top.y_from_top_mm >= bottom.y_from_top_mm:
        raise ValueError(
            "Centre cross-tie restrained bars must be ordered top to bottom."
        )

    diameter = cross_tie.diameter_mm
    radius = cross_tie.internal_bend_radius_mm + diameter / 2
    angle = math.radians(cross_tie.hook_angle_deg)
    tail = cross_tie.hook_tail_mm
    tangent_offset = radius * math.tan(angle / 2)
    side = 1.0 if cross_tie.straight_leg_side == "right" else -1.0
    axis = top.x_from_left_mm
    straight_x = axis + side * radius

    # These endpoints and tangent points deliberately reproduce the independent
    # fixture's two 135-degree inward tails and vertical straight leg.
    top_tail = PathPoint(
        0.0,
        axis + side * (radius * math.cos(angle) - tail * math.sin(angle)),
        top.y_from_top_mm - radius * math.sin(angle) - tail * math.cos(angle),
    )
    top_vertex = PathPoint(0.0, straight_x, top.y_from_top_mm - tangent_offset)
    bottom_vertex = PathPoint(0.0, straight_x, bottom.y_from_top_mm + tangent_offset)
    bottom_tail = PathPoint(
        0.0,
        axis + side * (radius * math.cos(angle) - tail * math.sin(angle)),
        bottom.y_from_top_mm + radius * math.sin(angle) + tail * math.cos(angle),
    )

    mark = f"{member.member_id}-CT{diameter:g}"
    nodes = (
        PathNode("tail-top", top_tail),
        PathNode("hook-top", top_vertex, radius, BendKind.HOOK),
        PathNode("hook-bottom", bottom_vertex, radius, BendKind.HOOK),
        PathNode("tail-bottom", bottom_tail),
    )
    seeds = []
    used_ids = set(by_id)
    for index, station in enumerate(stations_mm, start=1):
        plane = station + cross_tie.station_offset_mm
        path_id = f"{mark}-{index:03d}"
        while path_id in used_ids:
            path_id += "-tie"
        used_ids.add(path_id)

        seeds.append(
            BarPathSeed(
                path_id,
                mark,
                BarPathRole.TRANSVERSE_LINK,
                1,
                diameter,
                member.link_fy_nmm2,
                tuple(
                    replace(node, point=replace(node.point, station_x_mm=plane))
                    for node in nodes
                ),
            )
        )
    return tuple(seeds)
