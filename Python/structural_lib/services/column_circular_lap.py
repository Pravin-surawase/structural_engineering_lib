"""Check one straight perimeter contact lap and its tied circular assembly."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import asdict, replace
from itertools import combinations, pairwise
from typing import Any, Protocol

from structural_lib.codes.is456.column.axial import min_eccentricity
from structural_lib.codes.is456.column.circular import (
    CircularSection,
    check_circular_fixed_compression,
    circular_bars,
)
from structural_lib.codes.is456.column.positioned_biaxial import PositionedColumnBar
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.contracts.column_circular import (
    CircularColumnCageV1,
    CircularColumnGeometryV1,
    CircularContactLapV1,
    CircularDetailingActionV1,
    CircularRingV1,
)
from structural_lib.services.contracts.column_member_detailing import (
    ColumnDetailingBasisV1,
    ColumnStraightEndDetailV1,
)
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1

_PASS, _FAIL, _HOLD = (
    EngineeringStatus.PASS,
    EngineeringStatus.FAIL,
    EngineeringStatus.HOLD,
)
_TOL_MM = 1e-6
LapRecord = Callable[[str, str, str, EngineeringStatus], None]


class _LapRequest(Protocol):
    geometry: CircularColumnGeometryV1
    materials: ColumnMaterialsV1
    reinforcement: CircularColumnCageV1
    basis: ColumnDetailingBasisV1
    end_detail: ColumnStraightEndDetailV1
    actions: tuple[CircularDetailingActionV1, ...]


def admits_circular_contact_lap(
    request: _LapRequest, lap: CircularContactLapV1
) -> bool:
    """Require one bounded same-load tied perimeter profile at the checked cuts."""
    steel = request.reinforcement
    length = request.geometry.unsupported_length_mm
    ids = {action.station_id for action in request.actions}
    stations = {action.check_station_mm for action in request.actions}
    concurrent = {
        (action.combination_id, action.pu_kn, action.mx_knm, action.my_knm)
        for action in request.actions
    }
    return (
        isinstance(steel.transverse, CircularRingV1)
        and steel.bar_count == 8
        and steel.bar_diameter_mm == 20
        and lap.bar_id == "B1"
        and 0 < lap.start_mm < lap.end_mm < length
        and not any(action.vx_kn or action.vy_kn for action in request.actions)
        and len(concurrent) == 1
        and all(action.station_id is not None for action in request.actions)
        and len(ids) == len(request.actions)
        and {0.0, length} <= stations
        and any(lap.start_mm < station < lap.end_mm for station in stations)
    )


def _projected_closure_clearance(
    angles: list[float],
    bar_radius: float,
    bar_diameter: float,
    ring_diameter: float,
    lap: CircularContactLapV1,
) -> float:
    """Bound the closest bar surface to the supplied closure sector."""
    low, high = lap.closure_clear_sector_deg
    minimum_radius, maximum_radius = lap.closure_centreline_radial_envelope_mm
    separation = min(
        0.0 if low <= angle <= high else min((low - angle) % 360, (angle - high) % 360)
        for angle in angles
    )
    gap = math.radians(separation)
    closest_radius = min(
        maximum_radius, max(minimum_radius, bar_radius * math.cos(gap))
    )
    centre_distance = math.hypot(
        closest_radius - bar_radius * math.cos(gap), bar_radius * math.sin(gap)
    )
    return centre_distance - (bar_diameter + ring_diameter) / 2


def _ring_placement(
    request: _LapRequest,
    lap: CircularContactLapV1,
    transverse: dict[str, Any],
    path: str,
    record: LapRecord,
) -> dict[str, Any]:
    grid = sorted([*transverse["stations_mm"], *lap.additional_ring_stations_mm])
    ring_diameter = transverse["diameter_mm"]
    length = request.geometry.unsupported_length_mm
    start, end = lap.start_mm, lap.end_mm
    inner = [z for z in grid if start < z < end]
    before = max((z for z in grid if z < start), default=None)
    after = min((z for z in grid if z > end), default=None)
    pitch_min = min(b - a for a, b in pairwise(grid))
    offsets = [grid[0], length - grid[-1]]
    clear = pitch_min - ring_diameter
    results = {
        "ring_stations_mm": grid,
        "rings_inside_lap_mm": inner,
        "end_clearances_mm": offsets,
        "minimum_ring_clear_spacing_mm": clear,
        "actual_maximum_field_pitch_mm": max(b - a for a, b in pairwise(grid)),
    }
    if (
        grid[0] != transverse["stations_mm"][0]
        or grid[-1] != transverse["stations_mm"][-1]
        or clear < request.reinforcement.aggregate_size_mm + 5
        or min(offsets) < request.end_detail.end_hoop_offset_mm
    ):
        record(
            "COLUMN.CIRCULAR_LAP_RING_PLACEMENT",
            path,
            "Keep supplemental rings inside the placed member with clear space between levels.",
            _FAIL,
        )
    if before is None or after is None or not inner:
        record(
            "COLUMN.LAP_END_RESTRAINT",
            path,
            "Supply rings inside the lap and on each side of its two ends.",
            _FAIL,
        )
        return results
    brackets = [before, inner[0], inner[-1], after]
    distances = [start - before, inner[0] - start, end - inner[-1], after - end]
    if (
        start in grid
        or end in grid
        or min(distances) < ring_diameter / 2
        or max(distances) > lap.maximum_lap_end_ring_distance_mm
    ):
        record(
            "COLUMN.LAP_END_RESTRAINT",
            path,
            "Check the placement clearances and limiting ring distances on both sides of each lap end.",
            _FAIL,
        )
    lap_pitch = max(b - a for a, b in pairwise([before, *inner, after]))
    if lap_pitch > lap.maximum_lap_ring_pitch_mm:
        record(
            "COLUMN.CIRCULAR_LAP_RING_PITCH",
            path,
            f"Lap and bracketing ring pitch {lap_pitch:g} mm exceeds {lap.maximum_lap_ring_pitch_mm:g} mm.",
            _FAIL,
        )
    return {
        **results,
        "lap_end_bracket_stations_mm": brackets,
        "lap_end_bracket_distances_mm": distances,
        "maximum_lap_pitch_mm": lap_pitch,
    }


def _phase_strength(
    request: _LapRequest,
    bars: tuple[PositionedColumnBar, ...],
    puz: float,
    eccentricity: float,
) -> dict[str, Any] | None:
    action = request.actions[0]
    geometry, material = request.geometry, request.materials
    steel_area = sum(bar.area_mm2 for bar in bars)
    checked = check_circular_fixed_compression(
        CircularSection(
            geometry.diameter_mm, material.fck_nmm2, material.fy_nmm2, bars
        ),
        pu_kn=action.pu_kn,
        mx_knm=action.mx_knm,
        my_knm=action.my_knm,
        unsupported_length_mm=geometry.unsupported_length_mm,
        steel_area_mm2=steel_area,
        puz_kn=puz,
    )
    if checked is None:
        return None
    ratios = {
        "contour": checked.contour_ratio,
        "direct_ray": checked.direct_ratio,
        **{
            f"minimum_eccentricity_{axis}": ratio
            for axis, ratio in checked.minimum_eccentricity_ratios.items()
        },
    }
    return {
        "capacity_bar_ids": [bar.bar_id for bar in bars],
        "puz_kn": puz,
        "alpha_n": checked.alpha_n,
        "axis_capacities_knm": {
            axis: ray.capacity_knm for axis, ray in checked.axes.items()
        },
        "demand_ray": asdict(checked.demand) if checked.demand is not None else None,
        "minimum_eccentricity_mm": eccentricity,
        "ratios": ratios,
        "governing_check": max(ratios, key=ratios.__getitem__),
        "utilization": checked.governing_ratio,
        "status": (_PASS if checked.governing_ratio <= 1 else _FAIL).value,
    }


def check_circular_contact_lap(
    request: _LapRequest,
    lap: CircularContactLapV1,
    transverse: dict[str, Any],
    regular_section: dict[str, Any],
    end_required_mm: float,
    record: LapRecord,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Check a supported assembly and return exact cuts and phased strength evidence."""
    path = f"laps.{lap.lap_id}"
    steel, ends, geometry = request.reinforcement, request.end_detail, request.geometry
    ring = steel.transverse
    assert isinstance(ring, CircularRingV1)
    diameter, radius = steel.bar_diameter_mm, geometry.diameter_mm / 2
    ring_radius = steel.ring_radius_mm
    lower = tuple(
        replace(bar, bar_id=f"B{idx + 1}" if idx else f"{lap.bar_id}-L")
        for idx, bar in enumerate(
            circular_bars(
                geometry.diameter_mm,
                steel.bar_count,
                diameter,
                ring_radius,
                steel.first_bar_angle_deg,
            )
        )
    )
    upper_angle = math.radians(lap.upper_bar_angle_deg)
    partner = replace(
        lower[0],
        bar_id=f"{lap.bar_id}-U",
        x_from_left_mm=radius + ring_radius * math.cos(upper_angle),
        y_from_top_mm=radius + ring_radius * math.sin(upper_angle),
    )
    upper = (*lower[1:], partner)
    physical = (*lower, partner)
    centres = {
        bar.bar_id: (bar.x_from_left_mm - radius, bar.y_from_top_mm - radius)
        for bar in physical
    }
    pair = {lower[0].bar_id, partner.bar_id}
    contact = math.dist(centres[lower[0].bar_id], centres[partner.bar_id])
    unrelated = min(
        math.dist(first, second) - diameter
        for (first_id, first), (second_id, second) in combinations(centres.items(), 2)
        if {first_id, second_id} != pair
    )
    clear_required = regular_section["detail"]["minimum_clear_spacing_mm"]
    start, end = lap.start_mm, lap.end_mm
    compression_ld = end_required_mm / 1.25
    lap_required = max(1.10 * compression_ld, 24 * diameter)
    hoop_radius = regular_section["detail"]["transverse_centreline_diameter_mm"] / 2
    gaps = {
        mark: hoop_radius - (ring.diameter_mm + diameter) / 2 - math.hypot(*point)
        for mark, point in centres.items()
    }
    angles = {
        mark: math.degrees(math.atan2(point[1], point[0])) % 360
        for mark, point in centres.items()
    }
    closure_clearance = _projected_closure_clearance(
        list(angles.values()),
        ring_radius,
        diameter,
        ring.diameter_mm,
        lap,
    )
    max_periphery_spacing = regular_section["detail"]["periphery_spacing_mm"]
    upper_angles = sorted(angles[bar.bar_id] for bar in upper)
    max_periphery_spacing = max(
        max_periphery_spacing,
        radius
        * math.radians(
            max(b - a for a, b in pairwise([*upper_angles, upper_angles[0] + 360]))
        ),
    )
    gross = regular_section["gross_area_mm2"]
    overlap_ratio = sum(bar.area_mm2 for bar in physical) / gross
    action = request.actions[0]
    minimum_stress = (
        1000 * action.pu_kn / gross
        - 1e6
        * math.hypot(action.mx_knm, action.my_knm)
        * radius
        / regular_section["gross_inertia_mm4"]
    )
    details = {
        "lap_id": lap.lap_id,
        "bar_id": lap.bar_id,
        "compression_reference": lap.compression_reference,
        "lap_action_continuity_reference": request.basis.lap_action_continuity_reference,
        "lap_provided_mm": end - start,
        "lap_required_mm": lap_required,
        "contact_centre_distance_mm": contact,
        "overlap_bounds_mm": [start, end],
        "overlap_centres_from_column_centre_mm": centres,
        "overlap_radial_gaps_to_ring_mm": gaps,
        "minimum_unrelated_clearance_mm": unrelated,
        "minimum_required_unrelated_clearance_mm": clear_required,
        "minimum_gross_stress_nmm2": minimum_stress,
        "ring_centreline_radius_mm": hoop_radius,
        "ring_outer_cover_mm": steel.nominal_cover_mm,
        "closure_sector_projected_clearance_mm": closure_clearance,
        "longitudinal_maximum_periphery_spacing_mm": max_periphery_spacing,
        "ordinary_steel_ratio": regular_section["steel_ratio"],
        "overlap_physical_steel_ratio": overlap_ratio,
        "spliced_bar_fraction": 1 / steel.bar_count,
        "unsupported_length_over_diameter": geometry.unsupported_length_mm
        / geometry.diameter_mm,
        "ordinary_ring_pitch_limit_mm": regular_section["detail"][
            "ordinary_pitch_limit_mm"
        ],
        "end_tension_development_mm": end_required_mm,
        "unmodified_compression_development_mm": compression_ld,
        "maximum_lap_ring_pitch_limit_mm": lap.maximum_lap_ring_pitch_mm,
        "maximum_lap_end_ring_distance_mm": lap.maximum_lap_end_ring_distance_mm,
        **_ring_placement(request, lap, transverse, path, record),
    }
    if end - start < lap_required:
        record(
            "COLUMN.LAP_LENGTH",
            path,
            f"Lap {end - start:g} mm is shorter than {lap_required:g} mm.",
            _FAIL,
        )
    if not math.isclose(contact, diameter, rel_tol=0, abs_tol=_TOL_MM):
        record(
            "COLUMN.LAP_CONTACT_GEOMETRY",
            path,
            f"Equal bars require {diameter:g} mm contact spacing. The submitted centres are {contact:g} mm apart.",
            _FAIL,
        )
    if (
        unrelated < clear_required
        or any(abs(gap) > _TOL_MM for gap in gaps.values())
        or max_periphery_spacing > 300
        or overlap_ratio > 0.04
    ):
        record(
            "COLUMN.CIRCULAR_LAP_CAGE_FIT",
            path,
            "Check the unrelated bar clearance, individual ring contact, peripheral spacing and physical overlap steel.",
            _FAIL,
        )
    if (
        lap.closure_centreline_radial_envelope_mm[1] > hoop_radius
        or closure_clearance < clear_required
    ):
        record(
            "COLUMN.CIRCULAR_LAP_CLOSURE_FIT",
            path,
            "Keep the declared ring closure inside the hoop cover and clear of all longitudinal bars.",
            _FAIL,
        )
    if (
        not lap.compression_reference
        or not request.basis.lap_action_continuity_reference
        or minimum_stress <= 0
    ):
        record(
            "COLUMN.LAP_COMPRESSION_BASIS",
            path,
            "Supply interval compression evidence and keep the supplied signed action inside the circular gross-section kern.",
            _HOLD,
        )

    z0, z1 = (
        -ends.start_straight_mm,
        geometry.unsupported_length_mm + ends.end_straight_mm,
    )
    details["pieces"] = [
        {
            "bar_id": mark,
            "diameter_mm": diameter,
            "x_mm": x,
            "y_mm": y,
            "start_mm": start if mark == partner.bar_id else z0,
            "end_mm": end if mark == lower[0].bar_id else z1,
        }
        for mark, (x, y) in centres.items()
    ]
    phases: list[dict[str, Any]] = []
    eccentricity = min_eccentricity(
        geometry.unsupported_length_mm, geometry.diameter_mm
    )
    puz = regular_section["puz_kn"]
    for label, bars in (("LOWER", lower), ("UPPER", upper)):
        strength = _phase_strength(request, bars, puz, eccentricity)
        if strength is None:
            record(
                "COLUMN.PM_BASIS",
                path,
                f"The {label.lower()} transfer layout lacks signed section equilibrium.",
                _HOLD,
            )
            continue
        if strength["status"] == _FAIL.value:
            record(
                "COLUMN.LAP_SECTION_STRENGTH",
                path,
                f"The {label.lower()} transfer layout exceeds its signed section capacity.",
                _FAIL,
            )
        for row in request.actions:
            z = row.check_station_mm
            inside = start <= z <= end
            if inside or (z < start if label == "LOWER" else z > end):
                phases.append(
                    {
                        "station_id": row.station_id,
                        "station_mm": z,
                        "combination_id": row.combination_id,
                        "pu_kn": row.pu_kn,
                        "mx_knm": row.mx_knm,
                        "my_knm": row.my_knm,
                        "phase": f"OVERLAP_{label}" if inside else f"{label}_ONLY",
                        **strength,
                    }
                )
    phases.sort(key=lambda row: (row["station_mm"], row["phase"]))
    governing = max((row["utilization"] for row in phases), default=-math.inf)
    return (
        details,
        phases,
        [
            row
            for row in phases
            if math.isclose(row["utilization"], governing, rel_tol=0, abs_tol=1e-9)
        ],
    )
