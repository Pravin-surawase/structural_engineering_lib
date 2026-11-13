"""Restraint checks for the admitted open midpoint cross-tie arrangement."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from .four_corner import ColumnCageCheck, FourCornerCage

_SOURCE = "IS 456:2000 Cl. 26.5.3.2(b)(2), Fig. 9 and Cl. 26.2.2.4(b)"
_PAIRS = (("M_LEFT", "M_RIGHT"), ("M_TOP", "M_BOTTOM"))


@dataclass(frozen=True)
class MidpointCrossTie:
    """One repeated open link between the named midpoint bars."""

    tie_id: str
    restrained_bar_ids: tuple[str, str]
    station_offset_mm: float


@dataclass(frozen=True)
class MidpointTiePath:
    """Restraint schematic between two hooked bars at one offset in the pitch."""

    tie_id: str
    restrained_bar_ids: tuple[str, str]
    station_offset_mm: float
    start_mm: tuple[float, float]
    end_mm: tuple[float, float]
    diameter_mm: float
    pitch_mm: float
    internal_bend_radius_mm: float
    hook_angle_deg: float
    hook_tail_mm: float


@dataclass(frozen=True)
class MidpointTieChecks:
    """Physical restraint checks and explicit missing evidence."""

    paths: tuple[MidpointTiePath, ...]
    checks: tuple[ColumnCageCheck, ...]
    missing_pairs: tuple[tuple[str, str], ...]


def check_midpoint_ties(
    *,
    cage: FourCornerCage,
    b_mm: float,
    D_mm: float,
    nominal_cover_mm: float,
    tie_id: str,
    diameter_mm: float,
    pitch_mm: float,
    bend_radius_mm: float,
    hook_angle_deg: float,
    hook_tail_mm: float,
    cross_ties: tuple[MidpointCrossTie, ...],
) -> MidpointTieChecks:
    """Check open links that share the checked perimeter tie's bend schedule."""
    bars = {bar.bar_id: bar for bar in cage.bars}
    pairs = {frozenset(pair): pair for pair in _PAIRS if pair[0] in bars}
    remaining = dict(pairs)
    paths: list[MidpointTiePath] = []
    checks: list[ColumnCageCheck] = []
    ids = {tie_id}
    offset = cage.bar_centroid_offset_mm

    for tie in cross_ties:
        key = frozenset(tie.restrained_bar_ids)
        valid_pair = key in remaining and tie.tie_id not in ids
        checks.append(
            ColumnCageCheck(
                "COLUMN.MIDPOINT_TIE_PAIR", valid_pair, valid_pair, True, _SOURCE
            )
        )
        if not valid_pair:
            continue
        ids.add(tie.tie_id)
        pair = remaining.pop(key)
        first, second = (bars[bar_id] for bar_id in pair)
        left_right = pair == _PAIRS[0]
        face_span = (D_mm if left_right else b_mm) - 2 * offset
        link_span = (b_mm if left_right else D_mm) - 2 * offset
        checks.append(
            ColumnCageCheck(
                "COLUMN.MIDPOINT_RESTRAINT_SPAN",
                face_span <= 48 * diameter_mm,
                face_span,
                48 * diameter_mm,
                _SOURCE,
            )
        )

        # Bound the outer bend at the cover line and reserve the full
        # bend-plus-tail reach between each midpoint and the nearest corner.
        bend_extent = bend_radius_mm + diameter_mm
        bar_radius = first.diameter_mm / 2
        hook_fits = (
            bend_radius_mm >= bar_radius
            and offset - bend_extent >= nominal_cover_mm
            and 2 * bend_extent <= link_span
            and bend_extent + hook_tail_mm <= face_span / 2 - bar_radius
        )
        checks.append(
            ColumnCageCheck(
                "COLUMN.MIDPOINT_TIE_HOOK_FIT", hook_fits, hook_fits, True, _SOURCE
            )
        )
        paths.append(
            MidpointTiePath(
                tie.tie_id,
                pair,
                tie.station_offset_mm,
                (first.x_from_left_mm, first.y_from_top_mm),
                (second.x_from_left_mm, second.y_from_top_mm),
                diameter_mm,
                pitch_mm,
                bend_radius_mm,
                hook_angle_deg,
                hook_tail_mm,
            )
        )

    if paths:
        offsets = (0.0, *sorted(path.station_offset_mm for path in paths), pitch_mm)
        minimum_gap = min(end - start for start, end in pairwise(offsets))
        checks.append(
            ColumnCageCheck(
                "COLUMN.MIDPOINT_TIE_LEVELS",
                minimum_gap >= diameter_mm,
                minimum_gap,
                diameter_mm,
                "Separate transverse steel levels within the repeated tie pitch",
            )
        )
    return MidpointTieChecks(tuple(paths), tuple(checks), tuple(remaining.values()))
