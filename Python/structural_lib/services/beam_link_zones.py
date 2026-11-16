"""Resolved, non-overlapping placement grids for varied beam-link zones."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

from pydantic import Field

from structural_lib.codes.is456.beam.shear import _minimum_vertical_stirrup_pitch_mm
from structural_lib.codes.is456.column.detailing import (
    calculate_tie_spacing,
    minimum_tie_diameter,
)
from structural_lib.construction.bbs import _zone_stations
from structural_lib.construction.contracts import LinkPlacementZone
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.beam_continuous import (
    BeamContinuousCheckResultV1,
    _shear_sections,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousCheckRequestV1,
    Identifier,
)
from structural_lib.services.contracts.common import StrictPublicModel

_TOLERANCE_MM = 1e-8
_MAX_STATIONS = 251


class BeamLinkZoneV1(StrictPublicModel):
    """One declared part of a beam's longitudinal link-placement grid."""

    zone_id: Identifier
    start_station_mm: float = Field(ge=-1500, le=32000)
    end_station_mm: float = Field(ge=-1500, le=32000)
    spacing_mm: float = Field(gt=0, le=600)
    include_start: bool
    include_end: bool


@dataclass(frozen=True)
class ResolvedBeamLinkZone:
    """A construction placement zone with its owned, enumerated stations."""

    placement: LinkPlacementZone
    stations_mm: tuple[float, ...]


def _placement_issue(path: str, message: str) -> StructuralIssueV1:
    return StructuralIssueV1("BEAM.LINK_ZONE_PLACEMENT_FAIL", path, message)


def resolve_beam_link_zones(
    zones: tuple[BeamLinkZoneV1, ...],
    *,
    mark: str,
    first_station_mm: float,
    last_station_mm: float,
    minimum_grid_separation_mm: float,
) -> tuple[tuple[ResolvedBeamLinkZone, ...], StructuralIssueV1 | None]:
    """Validate and enumerate a single, complete, physically separated link grid."""

    if not zones:
        return (), _placement_issue("link_zones", "Declare at least one link zone.")
    if not math.isfinite(minimum_grid_separation_mm) or minimum_grid_separation_mm <= 0:
        return (), _placement_issue(
            "minimum_grid_separation_mm",
            "The minimum grid separation must be positive.",
        )
    if not math.isfinite(first_station_mm) or not math.isfinite(last_station_mm):
        return (), _placement_issue(
            "link_detail", "Link detail endpoints must be finite."
        )
    if first_station_mm >= last_station_mm:
        return (), _placement_issue(
            "link_detail",
            "The link-detail placement interval must have positive length.",
        )
    if len({zone.zone_id for zone in zones}) != len(zones):
        return (), _placement_issue("link_zones", "Link-zone IDs must be unique.")

    if not math.isclose(
        zones[0].start_station_mm, first_station_mm, rel_tol=0, abs_tol=_TOLERANCE_MM
    ):
        return (), _placement_issue(
            "link_zones[0]",
            "The first zone must start at the link-detail first station.",
        )
    if not math.isclose(
        zones[-1].end_station_mm, last_station_mm, rel_tol=0, abs_tol=_TOLERANCE_MM
    ):
        return (), _placement_issue(
            "link_zones[-1]", "The last zone must end at the link-detail last station."
        )
    if not zones[0].include_start or not zones[-1].include_end:
        return (), _placement_issue(
            "link_zones", "The first and last link-detail stations must be included."
        )

    estimated_station_count = 0
    placements: list[LinkPlacementZone] = []
    for index, zone in enumerate(zones):
        if zone.end_station_mm <= zone.start_station_mm:
            return (), _placement_issue(
                f"link_zones[{index}]", "Each link zone must have positive length."
            )
        span = zone.end_station_mm - zone.start_station_mm
        intervals = span / zone.spacing_mm
        if not math.isfinite(intervals) or intervals > _MAX_STATIONS + 1:
            return (), _placement_issue(
                "link_zones",
                "The resolved link grid may not contain more than 251 stations.",
            )
        rounded_intervals = round(intervals)
        if (
            rounded_intervals < 1
            or abs(span - rounded_intervals * zone.spacing_mm) > _TOLERANCE_MM
        ):
            return (), _placement_issue(
                f"link_zones[{index}]",
                "Zone endpoints must align exactly with the declared pitch.",
            )
        if index:
            previous = zones[index - 1]
            if not math.isclose(
                previous.end_station_mm,
                zone.start_station_mm,
                rel_tol=0,
                abs_tol=_TOLERANCE_MM,
            ):
                return (), _placement_issue(
                    f"link_zones[{index}]",
                    "Link zones must provide contiguous ordered coverage.",
                )
            if previous.include_end == zone.include_start:
                return (), _placement_issue(
                    f"link_zones[{index}]",
                    "Each shared boundary station must have exactly one owning zone.",
                )
        estimated_station_count += (
            rounded_intervals
            + 1
            - int(not zone.include_start)
            - int(not zone.include_end)
        )
        if estimated_station_count > _MAX_STATIONS:
            return (), _placement_issue(
                "link_zones",
                "The resolved link grid may not contain more than 251 stations.",
            )
        placements.append(
            LinkPlacementZone(
                zone.zone_id,
                mark,
                zone.start_station_mm,
                zone.end_station_mm,
                zone.spacing_mm,
                zone.include_start,
                zone.include_end,
            )
        )

    resolved: list[ResolvedBeamLinkZone] = []
    all_stations: list[float] = []
    for index, placement in enumerate(placements):
        stations = _zone_stations(placement, _TOLERANCE_MM)
        if stations is None:
            return (), _placement_issue(
                f"link_zones[{index}]",
                "The declared zone does not resolve to a valid link grid.",
            )
        if any(
            station < placement.start_station_x_mm - _TOLERANCE_MM
            or station > placement.end_station_x_mm + _TOLERANCE_MM
            for station in stations
        ):
            return (), _placement_issue(
                f"link_zones[{index}]",
                "Resolved stations must remain within their owning zone.",
            )
        all_stations.extend(stations)
        resolved.append(ResolvedBeamLinkZone(placement, stations))

    if any(
        right - left < minimum_grid_separation_mm - _TOLERANCE_MM
        for left, right in pairwise(all_stations)
    ):
        return (), _placement_issue(
            "link_zones",
            "Adjacent physical link stations are closer than the required grid separation.",
        )
    return tuple(resolved), None


def zone_transition_actions_issue(
    member: BeamContinuousCheckRequestV1,
    zones: tuple[ResolvedBeamLinkZone, ...],
) -> StructuralIssueV1 | None:
    """Require ULS action rows at every varied-link grid transition."""

    uls_combinations = {
        combination.combination_id
        for combination in member.combinations
        if combination.kind == "ULS"
    }
    action_keys = {
        (action.combination_id, action.station_id) for action in member.actions
    }
    for index, left in enumerate(zones[:-1], start=1):
        boundary_mm = left.placement.end_station_x_mm
        station_ids = {
            station.station_id
            for station in member.stations
            if station.side == "CONTINUOUS"
            and math.isclose(
                station.x_mm, boundary_mm, rel_tol=0, abs_tol=_TOLERANCE_MM
            )
        }
        if not station_ids or any(
            not any(
                (combination_id, station_id) in action_keys
                for station_id in station_ids
            )
            for combination_id in uls_combinations
        ):
            return StructuralIssueV1(
                "BEAM.LINK_ZONE_TRANSITION_ACTIONS_HELD",
                f"link_zones[{index}]",
                "Each link-zone transition needs a shared CONTINUOUS station and one supplied row for every ULS combination.",
            )
    return None


def check_varied_link_strength(
    checked: BeamContinuousCheckResultV1,
    zones: tuple[ResolvedBeamLinkZone, ...],
) -> tuple[dict[str, Any], list[StructuralIssueV1]]:
    """Report signed shear evidence across each physical pitch and transition."""
    member = checked.request
    maximum = min(
        calculate_tie_spacing(
            member.width_mm,
            member.depth_mm,
            min(bar.diameter_mm for bar in member.bars),
        ),
        _minimum_vertical_stirrup_pitch_mm(
            member.width_mm,
            math.pi * member.link_diameter_mm**2 / 2,
            member.link_fy_nmm2,
        ),
        *(
            float(leaf.outputs["stirrup_maximum_spacing_mm"])
            for leaf in checked.shear_sections.values()
            if "stirrup_maximum_spacing_mm" in leaf.outputs
        ),
    )
    active = [
        row
        for row in checked.rows
        if row.kind == "ULS" and not row.diagnostic_only and row.shear_face is not None
    ]
    summaries = []
    checks: dict[str, dict[str, dict[str, Any]]] = {}
    issues: list[StructuralIssueV1] = []
    if member.link_diameter_mm < minimum_tie_diameter(
        max(bar.diameter_mm for bar in member.bars)
    ):
        issues.append(
            StructuralIssueV1(
                "BEAM.LINK_ZONE_DIAMETER_FAIL",
                "member.link_diameter_mm",
                "The links are too small to restrain the compression reinforcement.",
            )
        )
    for zone in zones:
        placement = zone.placement
        pitch = placement.spacing_mm
        if pitch > maximum + 1e-9:
            issues.append(
                StructuralIssueV1(
                    "BEAM.LINK_ZONE_PITCH_FAIL",
                    f"link_zones.{placement.zone_id}",
                    f"The {pitch:g} mm pitch exceeds the {maximum:g} mm limit for shear and compression-bar restraint.",
                )
            )
        sections = _shear_sections(member, checked.flexural_sections, pitch)
        zone_checks: dict[str, dict[str, Any]] = {}
        for row in active:
            assert row.shear_face is not None
            if (
                not placement.start_station_x_mm - 1e-8
                <= row.station.x_mm
                <= placement.end_station_x_mm + 1e-8
            ):
                continue
            capacity = float(sections[row.shear_face].outputs["provided_capacity_kn"])
            zone_checks[row.action.row_id] = {
                "zone_id": placement.zone_id,
                "spacing_mm": pitch,
                "capacity_kn": capacity,
                "shear_ratio": abs(row.action.vu_kn) / capacity,
            }
        checks[placement.zone_id] = zone_checks
        summary: dict[str, Any] = {
            "zone_id": placement.zone_id,
            "bar_mark": placement.bar_mark,
            "start_station_mm": placement.start_station_x_mm,
            "end_station_mm": placement.end_station_x_mm,
            "spacing_mm": pitch,
            "include_start": placement.include_start,
            "include_end": placement.include_end,
            "stations_mm": list(zone.stations_mm),
            "quantity": len(zone.stations_mm),
        }
        if zone_checks:
            row = min(
                (row for row in active if row.action.row_id in zone_checks),
                key=lambda row: (
                    -zone_checks[row.action.row_id]["shear_ratio"],
                    row.action.row_id,
                ),
            )
            governing = zone_checks[row.action.row_id]
            summary.update(
                capacity_kn=governing["capacity_kn"],
                governing_row_id=row.action.row_id,
                governing_shear_kn=row.action.vu_kn,
                governing_ratio=governing["shear_ratio"],
            )
        summaries.append(summary)
    transitions = []
    for previous, following in pairwise(zones):
        left, right = previous.placement, following.placement
        boundary = left.end_station_x_mm
        for row in (
            row
            for row in active
            if math.isclose(row.station.x_mm, boundary, rel_tol=0, abs_tol=1e-8)
        ):
            row_id = row.action.row_id
            transitions.append(
                {
                    "station_mm": boundary,
                    "row_id": row_id,
                    "shear_kn": row.action.vu_kn,
                    "owner_zone_id": (
                        left.zone_id if left.include_end else right.zone_id
                    ),
                    "adjacent": [
                        checks[zone.zone_id][row_id] for zone in (left, right)
                    ],
                }
            )
    return {
        "maximum_pitch_mm": maximum,
        "zones": summaries,
        "transitions": transitions,
    }, issues
