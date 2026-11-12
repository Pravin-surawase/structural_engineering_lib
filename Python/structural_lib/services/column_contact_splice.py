"""Resolve the bounded straight compression lap and its physical bar schedule."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from itertools import combinations
from math import dist, isclose, pi
from typing import Any

from structural_lib.codes.is456.column.contact_splice import ReturnLink, return_link
from structural_lib.codes.is456.column.four_corner import FourCornerBar, FourCornerCage
from structural_lib.core.geometry import circle_inside_rounded_rectangle
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.contracts.column_member_detailing import (
    ColumnMemberDetailingInputV1,
)

_SOURCE = "IS 456:2000 Cl. 26.1.1, 26.2.1.2, 26.2.2.4(b), 26.2.5 and 26.5.3"
_PAIR = ("M_LEFT", "M_RIGHT")
_ORTHOGONAL = ("M_TOP", "M_BOTTOM")
_PASS = EngineeringStatus.PASS
_FAIL = EngineeringStatus.FAIL
_HOLD = EngineeringStatus.HOLD
_EPS = 1e-8


@dataclass(frozen=True)
class ContactSplice:
    """Checked physical pieces, section layouts and repeated transverse marks."""

    start_mm: float
    end_mm: float
    required_lap_mm: float
    upper: FourCornerCage
    pieces: list[dict[str, Any]]
    transverse: list[dict[str, Any]]
    sections: dict[str, Any]
    lap_stations_mm: list[float]
    end_support_distances_mm: list[float]
    minimum_unrelated_bar_clear_mm: float
    minimum_link_clear_mm: float
    hoop_centreline_radius_mm: float
    steel_ratio: float
    fabrication_reference: str

    def to_dict(self) -> dict[str, Any]:
        """Project the physical data, with the section strengths checked separately."""
        return {key: value for key, value in vars(self).items() if key != "upper"}


def _point(bar: FourCornerBar) -> tuple[float, float]:
    return bar.x_from_left_mm, bar.y_from_top_mm


def _link_fit(
    link: ReturnLink,
    bars: tuple[FourCornerBar, ...],
    width: float,
    depth: float,
    cover: float,
    diameter: float,
) -> tuple[bool, float]:
    margin = cover + diameter / 2
    # All extrema of an axis-aligned quadrant arc are its ends.
    inside = all(
        margin - _EPS <= x <= width - margin + _EPS
        and margin - _EPS <= y <= depth - margin + _EPS
        for segment in link.segments
        for x, y in (segment.start_mm, segment.end_mm)
    )
    clearance = min(
        segment.distance_to(_point(bar)) - (bar.diameter_mm + diameter) / 2
        for bar in bars
        for segment in link.segments
    )
    return (
        inside and link.tail_gap_mm >= diameter - _EPS and clearance >= -_EPS,
        clearance,
    )


def check_contact_splice(
    request: ColumnMemberDetailingInputV1,
    cage: FourCornerCage | None,
    transverse: list[dict[str, Any]],
    end_required_mm: float,
    record: Callable[..., None],
) -> ContactSplice | None:
    """Check straight contact geometry and retain HOLD outside the admitted topology."""
    if not request.laps:
        return None
    if len(request.laps) != 1 or request.laps[0].contact_assembly is None:
        record(
            "COLUMN.LAP_ASSEMBLY_REQUIRED",
            _HOLD,
            "laps",
            "Provide one supported physical contact splice assembly.",
            _SOURCE,
        )
        return None
    lap = request.laps[0]
    assembly = lap.contact_assembly
    assert assembly is not None
    steel, g = request.reinforcement, request.geometry
    hoop = steel.tie
    dia = steel.longitudinal_bar_diameter_mm
    path = f"laps.{lap.lap_id}.contact_assembly"

    def report(code: str, condition: bool, message: str, **values: Any) -> None:
        record(
            f"COLUMN.{code}",
            _PASS if condition else _FAIL,
            path,
            message,
            _SOURCE,
            **values,
        )

    if (
        steel.layout != "eight_bar"
        or set(lap.bar_ids) != set(_PAIR)
        or lap.stress_basis != "compression"
        or dia > 25
        or cage is None
        or hoop is None
        or len(transverse) != 3
        or not transverse[0]["stations_mm"]
    ):
        record(
            "COLUMN.LAP_ASSEMBLY_REQUIRED",
            _HOLD,
            path,
            "This assembly requires one equal-bar compression group up to Ø25 on the opposing left and right midpoint lines, with a resolved hoop and two links.",
            _SOURCE,
        )
        return None

    start, end = lap.start_mm, lap.end_mm
    ordinary = {bar.bar_id: bar for bar in cage.bars}
    near, far = ordinary[_PAIR[0]].y_from_top_mm, assembly.partner_y_mm
    if not isclose(far - near, dia, rel_tol=0, abs_tol=_EPS):
        report(
            "LAP_CONTACT_GEOMETRY",
            False,
            "Each upper partner must lie exactly one diameter towards the bottom face from its lower bar.",
            actual_separation_mm=far - near,
            required_separation_mm=dia,
        )
        return None
    report(
        "LAP_CONTACT_GEOMETRY",
        True,
        "The two matched pairs are tangent with unchanged section width.",
        actual_separation_mm=dia,
    )
    # Retain the contact-pair allowance of Cl. 26.2.1.2 throughout the lap.
    required = max(1.1 * end_required_mm / 1.25, 24 * dia)
    report(
        "LAP_LENGTH",
        end - start >= required,
        "Check the compression lap including the contact-pair allowance.",
        actual_mm=end - start,
        required_mm=required,
    )

    mates = {mark: replace(ordinary[mark], y_from_top_mm=far) for mark in _PAIR}
    upper = replace(cage, bars=tuple(mates.get(bar.bar_id, bar) for bar in cage.bars))
    overlap = (
        *cage.bars,
        *(replace(mates[mark], bar_id=f"{mark}-U") for mark in _PAIR),
    )
    pairs = {frozenset((mark, f"{mark}-U")) for mark in _PAIR}
    clear = min(
        dist(_point(first), _point(second)) - dia
        for first, second in combinations(overlap, 2)
        if frozenset((first.bar_id, second.bar_id)) not in pairs
    )
    clear_limit = max(25, dia, steel.aggregate_size_mm + 5)
    report(
        "LAP_CLEAR_SPACING",
        clear >= clear_limit - _EPS,
        "Check the minimum clear distance between unrelated longitudinal bars.",
        actual_mm=clear,
        limit_mm=clear_limit,
    )
    lap_ratio = len(overlap) * pi * dia**2 / 4 / (g.b_mm * g.D_mm)
    report(
        "LAP_STEEL_RATIO",
        lap_ratio <= 0.04,
        "Check the bounded 4% gross longitudinal steel limit through the overlap.",
        actual=lap_ratio,
        limit=0.04,
    )

    inside_face = steel.nominal_cover_mm + hoop.diameter_mm
    enclosure_ok = all(
        circle_inside_rounded_rectangle(
            *_point(bar),
            dia / 2,
            inside_face,
            g.b_mm - inside_face,
            inside_face,
            g.D_mm - inside_face,
            hoop.internal_bend_radius_mm,
        )
        for bar in overlap
    )
    report(
        "LAP_HOOP_ENCLOSURE",
        enclosure_ok,
        "All longitudinal bar circles must fit inside the closed hoop.",
    )
    offset = cage.bar_centroid_offset_mm
    face_span = max(g.b_mm, g.D_mm) - 2 * offset
    spacing_ok = max(far - offset, g.D_mm - offset - near) <= 300
    report(
        "LAP_RESTRAINT_SPAN",
        face_span <= 48 * hoop.diameter_mm and spacing_ok,
        "Check the permitted restrained face span and maximum spacing across the two straight layouts.",
    )

    transverse_by_pair = {
        frozenset(link.restrained_bar_ids): link for link in steel.cross_ties
    }
    x_mark = transverse_by_pair[frozenset(_PAIR)].tie_id
    y_mark = transverse_by_pair[frozenset(_ORTHOGONAL)].tie_id
    by_mark = {item["bar_id"]: item for item in transverse}
    x_levels = by_mark[x_mark]["stations_mm"]
    before = [s for s in x_levels if s < start]
    within = [s for s in x_levels if start < s < end]
    after = [s for s in x_levels if s > end]
    distances = (
        [start - before[-1], within[0] - start, end - within[-1], after[0] - end]
        if before and within and after
        else []
    )
    dt = hoop.diameter_mm
    report(
        "LAP_END_RESTRAINT",
        len(within) >= 2
        and len(before) + len(within) + len(after) == len(x_levels)
        and bool(distances)
        and min(distances) >= dt / 2 - _EPS
        and max(distances) <= 4 * dia + _EPS,
        "Each lap end needs an adjacent inner and outer link within four bar diameters, clear of the bar end.",
        distances_mm=distances,
        limit_mm=4 * dia,
    )

    r = hoop.internal_bend_radius_mm + dt / 2
    tail = assembly.hook_tail_mm
    fitted: dict[str, dict[str, Any]] = {}
    minimum_link = float("inf")
    fits = dia / 2 <= hoop.internal_bend_radius_mm <= dia / 2 + 2 and tail >= 8 * dt
    for label, low, high, bars in (
        ("lower", near, near, cage.bars),
        ("overlap", near, far, overlap),
        ("upper", far, far, upper.bars),
    ):
        links = {
            assembly.lap_link_id if label == "overlap" else x_mark: return_link(
                axis="x",
                left_mm=offset,
                right_mm=g.b_mm - offset,
                near_mm=low,
                far_mm=high,
                radius_mm=r,
                tail_mm=tail,
            ),
            y_mark: return_link(
                axis="y",
                left_mm=offset,
                right_mm=g.D_mm - offset,
                near_mm=g.b_mm / 2,
                far_mm=g.b_mm / 2,
                radius_mm=r,
                tail_mm=tail,
            ),
        }
        for link in links.values():
            link_fits, link_clearance = _link_fit(
                link, bars, g.b_mm, g.D_mm, steel.nominal_cover_mm, dt
            )
            minimum_link = min(minimum_link, link_clearance)
            fits &= link_fits
        fitted[label] = {
            "bars": [
                {
                    **asdict(bar),
                    "bar_id": (
                        f"{bar.bar_id}-{'U' if label == 'upper' else 'L'}"
                        if bar.bar_id in _PAIR
                        else bar.bar_id
                    ),
                }
                for bar in bars
            ],
            "links": {mark: asdict(link) for mark, link in links.items()},
            "cut_lengths_mm": {
                mark: link.cut_length_mm for mark, link in links.items()
            },
        }
    report(
        "LAP_LINK_FIT",
        fits,
        "Check the 90° anchorage tails, cover, tail separation and swept links against all longitudinal steel.",
        minimum_link_clear_mm=minimum_link,
        minimum_tail_mm=8 * dt,
    )

    if assembly.lap_link_id in by_mark:
        report(
            "LAP_LINK_MARK", False, "The overlap link needs a unique fabrication mark."
        )
        return None

    # Compression remains a declared interval basis. The supplied in-lap
    # rows must also stay strictly inside the gross-section elastic kern.
    actions = [row for row in request.actions if start <= row.check_station_mm <= end]
    stresses = [
        1000 * row.pu_kn / (g.b_mm * g.D_mm)
        - 6e6 * abs(row.mx_knm) / (g.b_mm * g.D_mm**2)
        - 6e6 * abs(row.my_knm) / (g.D_mm * g.b_mm**2)
        for row in actions
    ]
    if not assembly.compression_reference or not stresses or min(stresses) <= 0:
        record(
            "COLUMN.LAP_COMPRESSION_BASIS",
            _HOLD,
            path,
            "Supply an interval compression reference and an in-lap action row inside the gross-section kern, with all supplied in-lap rows in compression.",
            _SOURCE,
            minimum_gross_stress_nmm2=min(stresses, default=None),
        )

    pieces: list[dict[str, Any]] = []
    z_start = -request.end_detail.start_straight_mm
    z_end = g.unsupported_length_mm + request.end_detail.end_straight_mm
    for bar in cage.bars:
        segments: tuple[tuple[str, FourCornerBar, float, float], ...]
        if bar.bar_id in mates:
            segments = (
                (f"{bar.bar_id}-L", bar, z_start, end),
                (f"{bar.bar_id}-U", mates[bar.bar_id], start, z_end),
            )
        else:
            segments = ((bar.bar_id, bar, z_start, z_end),)
        pieces.extend(
            {
                "bar_id": mark,
                "parent_bar_id": bar.bar_id,
                "diameter_mm": dia,
                "x_mm": piece.x_from_left_mm,
                "y_mm": piece.y_from_top_mm,
                "start_mm": low,
                "end_mm": high,
                "cut_length_mm": high - low,
            }
            for mark, piece, low, high in segments
        )
    resolved = [transverse[0]]
    for mark, label, levels in (
        (x_mark, "lower", [*before, *after]),
        (y_mark, "lower", by_mark[y_mark]["stations_mm"]),
        (assembly.lap_link_id, "overlap", within),
    ):
        resolved.append(
            {
                "bar_id": mark,
                "role": "cross_tie",
                "diameter_mm": dt,
                "stations_mm": levels,
                "derived_cut_mm": fitted[label]["cut_lengths_mm"][mark],
                "cut_source": assembly.fabrication_reference,
            }
        )
    return ContactSplice(
        start,
        end,
        required,
        upper,
        pieces,
        resolved,
        fitted,
        within,
        distances,
        clear,
        minimum_link,
        r,
        lap_ratio,
        assembly.fabrication_reference,
    )
