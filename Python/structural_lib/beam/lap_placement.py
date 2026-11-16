"""Pure section geometry for a nested closed-link lap cage.

This module deliberately consumes the already checked link and reinforcement
arrangements.  It does not re-run their design checks or attach result
semantics; callers decide how a placement outcome participates in a larger
member check.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from itertools import pairwise
from typing import Any

from .bar_paths import BarPathRole
from .detailing import LinkCage, LongitudinalBarPath, ReinforcementRole
from .physical_torsion import ClosedLinkDetailRequest


@dataclass(frozen=True)
class LapPlacementEnvelope:
    """Declared fabrication and placing bounds for one straight web cage."""

    source_reference: str
    bar_axis_tolerance_mm: float
    bar_end_tolerance_mm: float
    cage_location_tolerance_mm: float
    link_station_tolerance_mm: float
    internal_bend_radius_tolerance_mm: float
    hook_plane_tolerance_mm: float
    hook_vertex_leg_tolerance_mm: float
    longitudinal_diameter_allowance_mm: float
    link_diameter_allowance_mm: float
    required_cover_mm: float
    concrete_placement_access_diameter_mm: float


def _number(value: object, *, positive: bool = False) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    return math.isfinite(value) and (value > 0 if positive else value >= 0)


def _finite(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _failure(
    *, issue: str = "placement_interference", **evidence: Any
) -> dict[str, Any]:
    return {"status": "FAIL", "issue": issue, **evidence}


def _seat_candidates(cage: LinkCage) -> list[tuple[float, float, bool, bool]]:
    """Return (x, y, is_left, is_top) centres of a cage's four return seats."""
    centre_radius = cage.internal_bend_radius_mm + cage.diameter_mm / 2
    return [
        (
            cage.left_centre_x_mm + centre_radius,
            cage.top_centre_y_mm + centre_radius,
            True,
            True,
        ),
        (
            cage.right_centre_x_mm - centre_radius,
            cage.top_centre_y_mm + centre_radius,
            False,
            True,
        ),
        (
            cage.left_centre_x_mm + centre_radius,
            cage.bottom_centre_y_mm - centre_radius,
            True,
            False,
        ),
        (
            cage.right_centre_x_mm - centre_radius,
            cage.bottom_centre_y_mm - centre_radius,
            False,
            False,
        ),
    ]


def check_nested_lap_placement(
    outer: ClosedLinkDetailRequest,
    inner: ClosedLinkDetailRequest,
    envelope: LapPlacementEnvelope,
    *,
    hook_plane_offset_mm: float,
    hook_vertex_leg_mm: float,
    restraint_station_offset_mm: float,
) -> dict[str, Any]:
    """Check physical fit of all outer-layer longitudinal pieces in two cages.

    A seat is a particular rounded corner of either actual cage.  Assignment is
    geometric and one-to-one, so a lap replacement can occupy a different seat
    even when it shares a layout row with its discontinued counterpart.
    """
    try:
        values = (
            *asdict(envelope).values(),
            hook_plane_offset_mm,
            hook_vertex_leg_mm,
            restraint_station_offset_mm,
        )
    except (TypeError, ValueError):
        return _failure(prerequisites_valid=False)
    if (
        not envelope.source_reference
        or not all(_number(value) for value in values[1:])
        or min(values[-5:]) <= 0
    ):
        return _failure(prerequisites_valid=False)

    arrangement = outer.arrangement
    member = outer.paths
    cages = (outer.cage, inner.cage)
    links = (outer.link, inner.link)
    numeric = (
        arrangement.section_width_mm,
        arrangement.section_depth_mm,
        arrangement.nominal_cover_mm,
        arrangement.maximum_aggregate_size_mm,
        *(
            value
            for cage in cages
            for value in (
                cage.diameter_mm,
                cage.left_centre_x_mm,
                cage.right_centre_x_mm,
                cage.top_centre_y_mm,
                cage.bottom_centre_y_mm,
                cage.internal_bend_radius_mm,
            )
        ),
        *(value for link in links for value in (link.diameter_mm, link.spacing_mm)),
    )
    if (
        not all(_number(value, positive=True) for value in numeric)
        or not _finite(member.member_start_x_mm)
        or not _finite(member.member_end_x_mm)
        or member.member_start_x_mm >= member.member_end_x_mm
        or not all(cage.closed for cage in cages)
        or not all(link.closed for link in links)
        or outer.cage.left_centre_x_mm >= outer.cage.right_centre_x_mm
        or inner.cage.left_centre_x_mm >= inner.cage.right_centre_x_mm
        or outer.cage.top_centre_y_mm >= outer.cage.bottom_centre_y_mm
        or inner.cage.top_centre_y_mm >= inner.cage.bottom_centre_y_mm
    ):
        return _failure(prerequisites_valid=False)

    bars = tuple(arrangement.bars)
    if not bars or len({bar.bar_id for bar in bars}) != len(bars):
        return _failure(prerequisites_valid=False)
    if not all(
        bar.bar_id
        and isinstance(bar.role, ReinforcementRole)
        and isinstance(bar.layer, int)
        and bar.layer >= 1
        and all(
            _number(value, positive=True)
            for value in (
                bar.diameter_mm,
                bar.x_from_left_mm,
                bar.y_from_top_mm,
            )
        )
        and _finite(bar.start_station_mm)
        and _finite(bar.end_station_mm)
        and bar.start_station_mm <= bar.end_station_mm
        for bar in bars
    ):
        return _failure(prerequisites_valid=False)

    # The exterior row is explicitly layer one; deeper layers are still used
    # for clear-gap and access evidence but have no rounded-return seat.
    seated = tuple(
        bar
        for bar in bars
        if bar.layer == 1
        and bar.role
        in (ReinforcementRole.TOP_LONGITUDINAL, ReinforcementRole.BOTTOM_LONGITUDINAL)
    )
    seats = [seat for cage in cages for seat in _seat_candidates(cage)]
    if len(seated) != len(seats):
        return _failure(
            prerequisites_valid=False,
            occupied_seat_count=len(seated),
            available_seat_count=len(seats),
        )

    inner_ids = {bar.bar_id for bar in inner.arrangement.bars}
    assigned = []
    for is_inner in (False, True):
        for role in (
            ReinforcementRole.TOP_LONGITUDINAL,
            ReinforcementRole.BOTTOM_LONGITUDINAL,
        ):
            row = sorted(
                (
                    bar
                    for bar in seated
                    if (bar.bar_id in inner_ids) is is_inner and bar.role is role
                ),
                key=lambda bar: bar.x_from_left_mm,
            )
            if len(row) != 2:
                return _failure(
                    issue="restraint_sector_unresolved",
                    status="HOLD",
                    prerequisites_valid=False,
                )
            assigned.extend(row)

    axis_tolerance = envelope.bar_axis_tolerance_mm
    allowance = envelope.longitudinal_diameter_allowance_mm
    returns: dict[str, dict[str, Any]] = {}
    for index, bar in enumerate(assigned):
        x, y, left, top = seats[index]
        dx = (x - bar.x_from_left_mm) * (1 if left else -1)
        dy = (y - bar.y_from_top_mm) * (1 if top else -1)
        cage = cages[index // 4]
        radial = math.hypot(abs(dx) + axis_tolerance, abs(dy) + axis_tolerance)
        minimum_radius = (
            cage.internal_bend_radius_mm - envelope.internal_bend_radius_tolerance_mm
        )
        clearance = minimum_radius - (bar.diameter_mm + allowance) / 2 - radial
        returns[bar.bar_id] = {
            "min_clearance_mm": clearance,
            "outward_offsets_mm": [dx, dy],
            "stays_inside_bend_sector": min(dx, dy) > axis_tolerance,
        }

    rows: dict[tuple[ReinforcementRole, int], list[LongitudinalBarPath]] = {}
    for bar in bars:
        if bar.role in (
            ReinforcementRole.TOP_LONGITUDINAL,
            ReinforcementRole.BOTTOM_LONGITUDINAL,
        ):
            rows.setdefault((bar.role, bar.layer), []).append(bar)
    horizontal: dict[str, list[float]] = {}
    for (role, layer), row in rows.items():
        ordered = sorted(row, key=lambda bar: bar.x_from_left_mm)
        name = (
            "top" if role is ReinforcementRole.TOP_LONGITUDINAL else "bottom"
        ) + f"-{layer}"
        horizontal[name] = [
            second.x_from_left_mm
            - first.x_from_left_mm
            - 2 * axis_tolerance
            - (first.diameter_mm + second.diameter_mm) / 2
            - allowance
            for first, second in pairwise(ordered)
        ]
    gaps = [gap for row in horizontal.values() for gap in row]
    if not gaps:
        return _failure(prerequisites_valid=False)

    vertical_gaps: list[float] = []
    for role in (
        ReinforcementRole.TOP_LONGITUDINAL,
        ReinforcementRole.BOTTOM_LONGITUDINAL,
    ):
        layer_rows = sorted(
            (layer, row) for (row_role, layer), row in rows.items() if row_role is role
        )
        for (_, nearer), (_, deeper) in pairwise(layer_rows):
            if role is ReinforcementRole.TOP_LONGITUDINAL:
                separation = min(bar.y_from_top_mm for bar in deeper) - max(
                    bar.y_from_top_mm for bar in nearer
                )
            else:
                separation = min(bar.y_from_top_mm for bar in nearer) - max(
                    bar.y_from_top_mm for bar in deeper
                )
            vertical_gaps.append(
                separation
                - 2 * axis_tolerance
                - max(bar.diameter_mm for bar in (*nearer, *deeper))
                - allowance
            )
    if not vertical_gaps:
        return _failure(prerequisites_valid=False)
    vertical = min(vertical_gaps)

    max_link = (
        max(link.diameter_mm for link in links) + envelope.link_diameter_allowance_mm
    )
    maximum_shift = hook_plane_offset_mm + envelope.hook_plane_tolerance_mm
    grid_pitch = min(
        restraint_station_offset_mm, outer.link.spacing_mm - restraint_station_offset_mm
    )
    grid = (
        grid_pitch - 2 * envelope.link_station_tolerance_mm - maximum_shift - max_link
    )
    centre = arrangement.section_width_mm / 2
    left_bars = [bar for bar in bars if bar.x_from_left_mm < centre]
    right_bars = [bar for bar in bars if bar.x_from_left_mm >= centre]
    if not left_bars or not right_bars:
        return _failure(prerequisites_valid=False)
    left_edge = max(
        bar.x_from_left_mm + (bar.diameter_mm + allowance) / 2 + axis_tolerance
        for bar in left_bars
    )
    right_edge = min(
        bar.x_from_left_mm - (bar.diameter_mm + allowance) / 2 - axis_tolerance
        for bar in right_bars
    )
    nominal_opening = outer.link.spacing_mm - restraint_station_offset_mm
    access = [
        right_edge - left_edge,
        nominal_opening
        - 2 * envelope.link_station_tolerance_mm
        - maximum_shift
        - max_link,
    ]
    max_radius = (
        inner.cage.internal_bend_radius_mm + envelope.internal_bend_radius_tolerance_mm
    )
    hook_tail = (
        hook_vertex_leg_mm
        - envelope.hook_vertex_leg_tolerance_mm
        - max_radius
        - max_link / 2
    )
    hook_shift = hook_plane_offset_mm - envelope.hook_plane_tolerance_mm
    inner_width = inner.cage.right_centre_x_mm - inner.cage.left_centre_x_mm
    steel_cover = (
        arrangement.nominal_cover_mm
        - envelope.cage_location_tolerance_mm
        - envelope.link_diameter_allowance_mm / 2
    )
    end_cover = (
        min(
            min(bar.start_station_mm - member.member_start_x_mm for bar in bars),
            min(member.member_end_x_mm - bar.end_station_mm for bar in bars),
        )
        - envelope.bar_end_tolerance_mm
    )
    main_diameter = max(bar.diameter_mm for bar in bars)
    required_gap = max(main_diameter, arrangement.maximum_aggregate_size_mm + 5)
    side_clearances = [
        min(
            abs(bar.x_from_left_mm - x)
            for x in (inner.cage.left_centre_x_mm, inner.cage.right_centre_x_mm)
        )
        - (bar.diameter_mm + allowance + max_link) / 2
        - 2 * axis_tolerance
        - envelope.internal_bend_radius_tolerance_mm
        for bar in bars
        if bar.bar_id not in inner_ids
    ]
    link_stations = [
        node.point.station_x_mm
        for detail in (outer, inner)
        for seed in detail.paths.paths
        if seed.role is BarPathRole.TRANSVERSE_LINK
        for node in seed.nodes
    ]
    if not link_stations:
        return _failure(prerequisites_valid=False)
    link_end_cover = (
        min(
            min(link_stations) - member.member_start_x_mm,
            member.member_end_x_mm - max(link_stations),
        )
        - envelope.link_station_tolerance_mm
        - envelope.hook_plane_tolerance_mm
        - max_link / 2
    )
    interference = (
        min(item["min_clearance_mm"] for item in returns.values()) < 0
        or min(gaps) < required_gap
        or vertical
        < max(15, main_diameter, 2 * arrangement.maximum_aggregate_size_mm / 3)
        or grid < required_gap
        or min(access) < envelope.concrete_placement_access_diameter_mm
        or hook_tail < 8 * max(link.diameter_mm for link in links)
        or hook_shift < max_link
        or hook_vertex_leg_mm + envelope.hook_vertex_leg_tolerance_mm >= inner_width
        or steel_cover < envelope.required_cover_mm
        or end_cover < envelope.required_cover_mm
        or link_end_cover < envelope.required_cover_mm
        or min(side_clearances, default=0) < 0
    )
    sector = all(item["stays_inside_bend_sector"] for item in returns.values())
    status, issue = (
        ("FAIL", "placement_interference")
        if interference
        else (("PASS", None) if sector else ("HOLD", "restraint_sector_unresolved"))
    )
    by_grid: dict[str, list[str]] = {"outer": [], "restraint": []}
    for index, bar in enumerate(assigned):
        by_grid["outer" if index < 4 else "restraint"].append(bar.bar_id)
    return {
        "status": status,
        "issue": issue,
        "returns": returns,
        "minimum_steel_cover_mm": steel_cover,
        "minimum_main_bar_end_cover_mm": end_cover,
        "minimum_horizontal_clearances_mm": horizontal,
        "minimum_vertical_clearance_mm": vertical,
        "minimum_grid_clearance_mm": grid,
        "maximum_perimeter_pitch_mm": outer.link.spacing_mm
        + 2 * envelope.link_station_tolerance_mm,
        "minimum_hook_tail_mm": hook_tail,
        "minimum_hook_plane_shift_mm": hook_shift,
        "minimum_clear_concrete_access_mm": access,
        # A passed result is also the unambiguous installation record.  Do not
        # present a provisional assignment as supported when geometry holds or
        # fails.
        "corner_bar_ids_by_grid": (
            {name: sorted(ids) for name, ids in by_grid.items()}
            if status == "PASS"
            else None
        ),
    }
