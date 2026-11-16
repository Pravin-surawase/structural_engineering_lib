"""Fit, restraint and placement checks for a two-layer rectangular beam cage."""

from __future__ import annotations

import math
from itertools import pairwise
from typing import Any, Literal

from pydantic import Field, field_validator

from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
    BeamSectionBarV1,
    Identifier,
    Reference,
)
from structural_lib.services.contracts.common import StrictPublicModel


class BeamLayeredCagePlacementV1(StrictPublicModel):
    """Declared tolerances and open-form access for one assembled cage."""

    source_reference: Reference
    form_opening_width_mm: float = Field(gt=0, le=3000)
    form_opening_height_mm: float = Field(gt=0, le=3000)
    required_cover_mm: float = Field(gt=0, le=100)
    consolidation_access_diameter_mm: float = Field(gt=0, le=200)
    bar_axis_tolerance_mm: float = Field(ge=0, le=30)
    bar_end_tolerance_mm: float = Field(ge=0, le=100)
    cage_location_tolerance_mm: float = Field(ge=0, le=30)
    link_bound_tolerance_mm: float = Field(ge=0, le=30)
    link_station_tolerance_mm: float = Field(ge=0, le=50)
    bend_radius_tolerance_mm: float = Field(ge=0, le=20)
    bar_diameter_allowance_mm: float = Field(ge=0, le=10)
    link_diameter_allowance_mm: float = Field(ge=0, le=5)
    closed_hook_plane_offset_tolerance_mm: float = Field(ge=0, le=20)
    cross_tie_hook_tail_tolerance_mm: float = Field(ge=0, le=30)
    cross_tie_maximum_hook_angle_deg: float = Field(ge=135, lt=180)


class BeamCentreCrossTieV1(StrictPublicModel):
    """One open cross-tie seated on a vertically aligned pair of outer bars."""

    restrained_bar_ids: tuple[Identifier, Identifier]
    diameter_mm: float = Field(gt=0, le=20)
    station_offset_mm: float = Field(gt=0, le=3000)
    internal_bend_radius_mm: float = Field(gt=0, le=100)
    hook_angle_deg: Literal[135]
    hook_tail_mm: float = Field(gt=0, le=300)
    straight_leg_side: Literal["left", "right"]
    source_reference: Reference

    @field_validator("restrained_bar_ids", mode="before")
    @classmethod
    def accept_bar_id_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


def _bar_rows(
    member: BeamLayeredContinuousCheckRequestV1,
) -> tuple[tuple[BeamSectionBarV1, ...], ...]:
    return tuple(
        tuple(
            sorted(
                (bar for bar in member.bars if bar.face == face and bar.layer == layer),
                key=lambda bar: bar.x_from_left_mm,
            )
        )
        for face, layer in (("top", 1), ("bottom", 1), ("bottom", 2))
    )


def _clear(
    a: BeamSectionBarV1,
    b: BeamSectionBarV1,
    distance: float,
    limits: BeamLayeredCagePlacementV1,
) -> float:
    return (
        distance
        - (a.diameter_mm + b.diameter_mm) / 2
        - 2 * limits.bar_axis_tolerance_mm
        - limits.bar_diameter_allowance_mm
    )


def _corner_checks(
    outer_top: tuple[BeamSectionBarV1, ...],
    outer_bottom: tuple[BeamSectionBarV1, ...],
    bounds: tuple[float, float, float, float],
    radius: float,
    link_diameter: float,
    limits: BeamLayeredCagePlacementV1,
) -> dict[str, Any]:
    x1, y1, x2, y2 = bounds
    centre_offset = radius + link_diameter / 2
    checked = {}
    for bar, side_x, side_y in (
        (outer_top[0], -1, -1),
        (outer_top[-1], 1, -1),
        (outer_bottom[0], -1, 1),
        (outer_bottom[-1], 1, 1),
    ):
        x, y = bar.x_from_left_mm, bar.y_from_top_mm
        cx = (x1 if side_x < 0 else x2) - side_x * centre_offset
        cy = (y1 if side_y < 0 else y2) - side_y * centre_offset
        dx, dy = (x - cx) * side_x, (y - cy) * side_y
        tolerance = limits.bar_axis_tolerance_mm
        radial_clearance = (
            radius
            - limits.bend_radius_tolerance_mm
            - (bar.diameter_mm + limits.bar_diameter_allowance_mm) / 2
            - math.hypot(max(0.0, dx + tolerance), max(0.0, dy + tolerance))
        )
        checked[bar.bar_id] = {
            "axis_mm": [x, y],
            "bend_centre_mm": [cx, cy],
            "min_radial_clearance_mm": radial_clearance,
            "seated_through_tolerance": min(dx, dy) > tolerance
            and radial_clearance >= 0,
        }
    return checked


def _cross_tie_fit(
    member: BeamLayeredContinuousCheckRequestV1,
    tie: BeamCentreCrossTieV1,
    limits: BeamLayeredCagePlacementV1,
    top: BeamSectionBarV1,
    bottom: BeamSectionBarV1,
    outer_bottom: tuple[BeamSectionBarV1, ...],
    maximum_hoop_diameter: float,
    closed_hook_shift: float,
) -> dict[str, Any]:
    axis_tolerance = limits.bar_axis_tolerance_mm
    diameter = tie.diameter_mm + limits.link_diameter_allowance_mm
    max_radius = (
        tie.internal_bend_radius_mm + limits.bend_radius_tolerance_mm + diameter / 2
    )
    min_radius = tie.internal_bend_radius_mm - limits.bend_radius_tolerance_mm
    max_tail = tie.hook_tail_mm + limits.cross_tie_hook_tail_tolerance_mm
    angle = math.radians(limits.cross_tie_maximum_hook_angle_deg)
    inward_tail = -max_tail * math.cos(angle) - (
        min_radius + tie.diameter_mm / 2
    ) * math.sin(angle)
    width, depth = member.width_mm, member.depth_mm
    reflected = tie.straight_leg_side == "left"

    def x_axis(bar: BeamSectionBarV1) -> float:
        x = bar.x_from_left_mm
        return width - x if reflected else x

    x = x_axis(top)
    other_bars = [
        bar for bar in member.bars if bar.bar_id not in tie.restrained_bar_ids
    ]
    steel_clearance = (
        diameter
        + max(bar.diameter_mm for bar in member.bars)
        + limits.bar_diameter_allowance_mm
    ) / 2 + 2 * axis_tolerance
    # Both 135 degree tails return to the side opposite the straight leg.
    # Bound the swept hook and tail steel against each unengaged bar.
    clearances = []
    for bar in other_bars:
        offset = x_axis(bar) - x
        y = bar.y_from_top_mm
        if offset > 0:
            gap = offset - max_radius
        elif y in (top.y_from_top_mm, bottom.y_from_top_mm):
            gap = -offset / math.sqrt(2) - max_radius
        else:
            gap = min(
                min_radius + tie.diameter_mm / 2 - offset,
                y - top.y_from_top_mm - inward_tail,
                bottom.y_from_top_mm - y - inward_tail,
            )
        clearances.append(gap - steel_clearance)
    # A clear vertical consolidation line passes between the middle bars
    # and the next side bars, between the tie plane and the next hoop.
    lane_left = max(
        x_axis(bar) + (bar.diameter_mm + limits.bar_diameter_allowance_mm) / 2
        for bar in member.bars
        if x_axis(bar) <= x
    )
    lane_right = min(
        x_axis(bar) - (bar.diameter_mm + limits.bar_diameter_allowance_mm) / 2
        for bar in member.bars
        if x_axis(bar) > x
    )
    lane_width = lane_right - lane_left - 2 * axis_tolerance
    tail_reach = -max_radius * math.cos(angle) + max_tail / math.sqrt(2)
    cover = (
        min(
            top.y_from_top_mm - max_radius,
            depth - bottom.y_from_top_mm - max_radius,
            x - max(max_radius, tail_reach),
            width - x - max_radius,
        )
        - diameter / 2
        - axis_tolerance
        - limits.cage_location_tolerance_mm
    )
    station_allowance = (
        2 * limits.link_station_tolerance_mm + (maximum_hoop_diameter + diameter) / 2
    )
    lane_length = member.link_spacing_mm - tie.station_offset_mm - station_allowance
    return {
        "restraint_corner_span_mm": outer_bottom[-1].x_from_left_mm
        - outer_bottom[0].x_from_left_mm,
        "restraint_span_limit_mm": 48 * min(tie.diameter_mm, member.link_diameter_mm),
        "maximum_untied_spacing_each_side_mm": 75,
        "middle_bar_spacing_each_side_mm": [
            b.x_from_left_mm - a.x_from_left_mm for a, b in pairwise(outer_bottom)
        ],
        "hook_min_clearance_to_engaged_steel_mm": min_radius
        - (max(top.diameter_mm, bottom.diameter_mm) + limits.bar_diameter_allowance_mm)
        / 2
        - math.sqrt(2) * axis_tolerance,
        "envelope_clearance_to_other_bars_mm": min(clearances),
        "minimum_cover_mm": cover,
        "minimum_tail_mm": tie.hook_tail_mm - limits.cross_tie_hook_tail_tolerance_mm,
        "minimum_grid_clearance_mm": min(
            tie.station_offset_mm - closed_hook_shift - station_allowance,
            lane_length,
        ),
        "consolidation_lane_width_mm": lane_width,
        "consolidation_lane_length_mm": lane_length,
        "consolidation_opening_mm": min(lane_width, lane_length),
    }


def check_layered_cage_placement(
    member: BeamLayeredContinuousCheckRequestV1,
    *,
    link_bounds_mm: tuple[float, float, float, float],
    internal_bend_radius_mm: float,
    hook_vertex_leg_mm: float,
    hook_plane_offset_mm: float,
    placement: BeamLayeredCagePlacementV1,
    cross_tie: BeamCentreCrossTieV1 | None,
) -> tuple[dict[str, Any], tuple[StructuralIssueV1, ...]]:
    """Check the rounded-hoop seats, middle-bar tie and trial form clearances."""
    top, bottom, inner = _bar_rows(member)
    if (
        tuple(map(len, (top, bottom, inner))) != (3, 3, 2)
        or len(member.bars) != 8
        or any(
            len({bar.y_from_top_mm for bar in row}) != 1 for row in (top, bottom, inner)
        )
    ):
        return {}, (
            StructuralIssueV1(
                "BEAM.EDIT_CAGE_SCOPE_HELD",
                "member.bars",
                "Supply three coplanar outer bars per face and one pair of inner bottom bars for this placement profile.",
            ),
        )
    limits = placement
    issues: list[StructuralIssueV1] = []

    def require(passed: bool, code: str, field: str, message: str) -> None:
        if not passed:
            issues.append(StructuralIssueV1(code, field, message))

    corners = _corner_checks(
        top,
        bottom,
        link_bounds_mm,
        internal_bend_radius_mm,
        member.link_diameter_mm,
        limits,
    )
    require(
        all(item["seated_through_tolerance"] for item in corners.values()),
        "BEAM.EDIT_CORNER_RESTRAINT",
        "member.bars",
        "Each rounded hoop corner must remain occupied by its outer bar throughout the placement tolerance.",
    )
    horizontal: dict[str, list[float]] = {}
    for label, row in zip(
        ("top-1", "bottom-1", "bottom-2"), (top, bottom, inner), strict=True
    ):
        horizontal[label] = []
        for a, b in pairwise(row):
            gap = _clear(a, b, b.x_from_left_mm - a.x_from_left_mm, limits)
            horizontal[label].append(gap)
            require(
                gap
                >= max(
                    max(a.diameter_mm, b.diameter_mm)
                    + limits.bar_diameter_allowance_mm,
                    member.aggregate_size_mm + 5,
                ),
                "BEAM.EDIT_SPACING",
                f"member.bars.{label}",
                "Horizontal steel clearance falls below the aggregate and bar requirement.",
            )
    outer_edges = (bottom[0], bottom[-1])
    vertical = []
    for outer, bar in zip(outer_edges, inner, strict=True):
        gap = _clear(outer, bar, outer.y_from_top_mm - bar.y_from_top_mm, limits)
        vertical.append(gap)
        require(
            gap
            >= max(
                15,
                max(outer.diameter_mm, bar.diameter_mm)
                + limits.bar_diameter_allowance_mm,
                2 * member.aggregate_size_mm / 3,
            )
            and math.isclose(
                outer.x_from_left_mm, bar.x_from_left_mm, rel_tol=0, abs_tol=1e-6
            ),
            "BEAM.EDIT_SPACING",
            "member.bars.bottom-2",
            "The inner bars require alignment behind their outer bars and sufficient vertical clear spacing.",
        )
    depth, width = member.depth_mm, member.width_mm
    inner_depth = min(
        depth
        - bar.y_from_top_mm
        - (bar.diameter_mm + limits.bar_diameter_allowance_mm) / 2
        - limits.bar_axis_tolerance_mm
        - limits.cage_location_tolerance_mm
        for bar in inner
    )
    required_depth = 3 * (
        max(bar.diameter_mm for bar in inner) + limits.bar_diameter_allowance_mm
    )
    require(
        inner_depth >= required_depth,
        "BEAM.EDIT_INTERMEDIATE_RESTRAINT",
        "member.bars.bottom-2",
        "The inner row is too close to the compression face for restraint by the outer row.",
    )
    x1, y1, x2, y2 = link_bounds_mm
    hoop_diameter = member.link_diameter_mm
    max_hoop_dia = hoop_diameter + limits.link_diameter_allowance_mm
    cage_shift = limits.cage_location_tolerance_mm + limits.link_bound_tolerance_mm
    cover = min(x1, y1, width - x2, depth - y2) - max_hoop_dia / 2 - cage_shift
    lift_width = x2 - x1 + max_hoop_dia + 2 * cage_shift
    lift_height = y2 - y1 + max_hoop_dia + 2 * cage_shift
    max_pitch = member.link_spacing_mm + 2 * limits.link_station_tolerance_mm
    pitch_limit = min(
        width, depth, 16 * min(bar.diameter_mm for bar in member.bars), 300
    )
    finished_tail = hook_vertex_leg_mm - internal_bend_radius_mm - hoop_diameter / 2
    require(
        cover >= limits.required_cover_mm,
        "BEAM.EDIT_COVER",
        "layered_cage.placement.required_cover_mm",
        "The outer hoop falls below the required placed cover.",
    )
    require(
        limits.form_opening_width_mm >= lift_width
        and limits.form_opening_height_mm >= lift_height,
        "BEAM.EDIT_FORM_OPENING",
        "layered_cage.placement",
        "The form opening is smaller than the tolerated cage lift envelope.",
    )
    maximum_longitudinal = max(bar.diameter_mm for bar in member.bars)
    require(
        max_pitch <= pitch_limit
        and hoop_diameter >= max(6, maximum_longitudinal / 4)
        and hook_vertex_leg_mm
        - internal_bend_radius_mm
        - limits.bend_radius_tolerance_mm
        - max_hoop_dia / 2
        >= 8 * hoop_diameter,
        "BEAM.EDIT_HOOP_RESTRAINT",
        "link_detail",
        "The outer hoop pitch, size and finished returns must restrain the outer cage.",
    )
    cross_data = {}
    top_middle, bottom_middle = top[1], bottom[1]
    if (
        cross_tie is not None
        and cross_tie.restrained_bar_ids == (top_middle.bar_id, bottom_middle.bar_id)
        and all(
            row[0].x_from_left_mm < row[1].x_from_left_mm < row[2].x_from_left_mm
            for row in (top, bottom)
        )
        and math.isclose(
            top_middle.x_from_left_mm,
            bottom_middle.x_from_left_mm,
            rel_tol=0,
            abs_tol=1e-9,
        )
    ):
        cross_data = _cross_tie_fit(
            member,
            cross_tie,
            limits,
            top_middle,
            bottom_middle,
            bottom,
            max_hoop_dia,
            hook_plane_offset_mm + limits.closed_hook_plane_offset_tolerance_mm,
        )
        max_face_span = (
            max(row[-1].x_from_left_mm - row[0].x_from_left_mm for row in (top, bottom))
            + 2 * limits.bar_axis_tolerance_mm
        )
        require(
            max_face_span <= cross_data["restraint_span_limit_mm"]
            and cross_tie.diameter_mm >= max(6, maximum_longitudinal / 4)
            and cross_data["minimum_tail_mm"] >= 6 * cross_tie.diameter_mm
            and cross_data["minimum_cover_mm"] >= limits.required_cover_mm
            and cross_data["hook_min_clearance_to_engaged_steel_mm"] >= 0
            and cross_data["envelope_clearance_to_other_bars_mm"] >= 0,
            "BEAM.EDIT_INTERMEDIATE_RESTRAINT",
            "layered_cage.cross_tie",
            "The centre tie cannot seat and restrain its middle pair with the declared hooks and tolerances.",
        )
        require(
            cross_data["minimum_grid_clearance_mm"] >= member.aggregate_size_mm + 5
            and cross_data["consolidation_opening_mm"]
            >= limits.consolidation_access_diameter_mm,
            "BEAM.EDIT_CONSOLIDATION",
            "layered_cage.placement",
            "The staggered steel obstructs the declared consolidation opening.",
        )
    else:
        require(
            False,
            "BEAM.EDIT_INTERMEDIATE_RESTRAINT",
            "layered_cage.cross_tie",
            "Supply the physical cross-tie around the aligned middle bars of the two outer faces.",
        )
    result = {
        "outer_corner_checks": corners,
        "worst_horizontal_clearance_mm": horizontal,
        "worst_vertical_clearance_mm": min(vertical),
        "inner_bottom_depth_to_steel_mm": inner_depth,
        "inner_bottom_required_depth_mm": required_depth,
        "worst_outer_hoop_cover_mm": cover,
        "max_pitch_under_tolerance_mm": max_pitch,
        "restraint_pitch_limit_mm": pitch_limit,
        "hoop_finished_straight_tail_mm": finished_tail,
        "lift_envelope_width_mm": lift_width,
        "lift_envelope_height_mm": lift_height,
        "form_opening_width_mm": limits.form_opening_width_mm,
        "form_opening_height_mm": limits.form_opening_height_mm,
        "consolidation_access_diameter_mm": limits.consolidation_access_diameter_mm,
        "required_cover_mm": limits.required_cover_mm,
        "cross_tie": cross_data,
    }
    return result, tuple(issues)
