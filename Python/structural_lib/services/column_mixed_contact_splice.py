"""Resolve one Ø16 compression contact group in the mixed rectangular cage."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from itertools import combinations, pairwise
from math import dist, fsum, isclose
from typing import Any

from structural_lib.codes.is456.column.contact_splice import return_link
from structural_lib.codes.is456.column.positioned_biaxial import PositionedColumnBar
from structural_lib.codes.is456.column.positioned_cage import (
    PositionedCrossTie,
    _path_check,
)
from structural_lib.core.geometry import circle_inside_rounded_rectangle
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.column_contact_splice import (
    _EPS,
    _SOURCE,
    ContactSplice,
    _gross_lap_stresses,
    _lap_end_support_ok,
    _lap_support,
    _link_fit,
    _point,
    _split_pieces,
)
from structural_lib.services.contracts.column_member import PositionedColumnCrossTieV1
from structural_lib.services.contracts.column_member_detailing import (
    PositionedColumnMemberDetailingInputV1,
)


@dataclass(frozen=True)
class _MixedContactSplice(ContactSplice):
    transverse_level_clear_mm: float
    transverse_end_cover_mm: float


def _mixed_splice_link(
    request: PositionedColumnMemberDetailingInputV1,
    bars: tuple[PositionedColumnBar, ...],
) -> PositionedColumnCrossTieV1 | None:
    """Find the opposed side link on the admitted twelve-bar cage."""
    steel = request.reinforcement
    if (
        len(request.laps) != 1
        or steel.tie is None
        or len(steel.cross_ties) != 3
        or Counter((bar.row, bar.diameter_mm) for bar in bars)
        != {("outer", 20): 4, ("outer", 16): 6, ("inner", 16): 2}
    ):
        return None
    lap = request.laps[0]
    seats = sorted(
        (bar for bar in bars if bar.bar_id in lap.bar_ids),
        key=lambda bar: bar.x_from_left_mm,
    )
    if len(lap.bar_ids) != 2 or len(seats) != 2:
        return None
    left, right = seats
    inside = steel.nominal_cover_mm + steel.tie.diameter_mm
    if not (
        all(bar.row == "outer" and bar.diameter_mm == 16 for bar in seats)
        and isclose(left.y_from_top_mm, right.y_from_top_mm, rel_tol=0, abs_tol=_EPS)
        and inside - _EPS <= left.x_from_left_mm - 8 <= inside + 2 + _EPS
        and inside - _EPS
        <= request.geometry.b_mm - right.x_from_left_mm - 8
        <= inside + 2 + _EPS
    ):
        return None
    return next(
        (
            link
            for link in steel.cross_ties
            if set(link.restrained_bar_ids) == set(lap.bar_ids)
        ),
        None,
    )


def _side_gaps(
    bars: tuple[PositionedColumnBar, ...], width: float, inside: float
) -> tuple[float, float]:
    faces = [
        sorted(
            bar.y_from_top_mm
            for bar in bars
            if bar.row == "outer"
            and -_EPS <= distance(bar) - bar.diameter_mm / 2 - inside <= 2 + _EPS
        )
        for distance in (
            lambda bar: bar.x_from_left_mm,
            lambda bar: width - bar.x_from_left_mm,
        )
    ]
    return (
        max((b - a for face in faces for a, b in pairwise(face)), default=0),
        max((face[-1] - face[0] for face in faces if face), default=0),
    )


def _check_mixed_contact_splice(
    request: PositionedColumnMemberDetailingInputV1,
    bars: tuple[PositionedColumnBar, ...],
    seat: PositionedColumnCrossTieV1,
    transverse: list[dict[str, Any]],
    required: float,
    record: Callable[..., None],
) -> ContactSplice | None:
    lap = request.laps[0]
    steel, g = request.reinforcement, request.geometry
    hoop = steel.tie
    assert hoop is not None
    path = f"laps.{lap.lap_id}.contact_assembly"
    assembly = lap.contact_assembly
    by_mark = {series["bar_id"]: series for series in transverse}
    ordinary = {bar.bar_id: bar for bar in bars}
    if (
        assembly is None
        or lap.stress_basis != "compression"
        or assembly.corner_link_id is not None
        or assembly.corner_link_offset_mm is not None
    ):
        record(
            "COLUMN.LAP_ASSEMBLY_REQUIRED",
            EngineeringStatus.HOLD,
            path,
            "Supply one physical Ø16 side contact assembly with a compression basis.",
            _SOURCE,
        )
        return None
    if (
        not transverse
        or set(by_mark) != {hoop.tie_id, *(link.tie_id for link in steel.cross_ties)}
        or not all(series["stations_mm"] for series in transverse)
    ):
        record(
            "COLUMN.LAP_ASSEMBLY_REQUIRED",
            EngineeringStatus.HOLD,
            path,
            "Resolve the hoop and all three transverse link paths.",
            _SOURCE,
        )
        return None

    def report(code: str, passed: bool, message: str, **values: Any) -> None:
        record(
            f"COLUMN.{code}",
            EngineeringStatus.PASS if passed else EngineeringStatus.FAIL,
            path,
            message,
            _SOURCE,
            **values,
        )

    start, end = lap.start_mm, lap.end_mm
    left, right = sorted(
        (ordinary[mark] for mark in lap.bar_ids), key=lambda bar: bar.x_from_left_mm
    )
    dia, dt = left.diameter_mm, seat.diameter_mm
    near, far = left.y_from_top_mm, assembly.partner_y_mm
    tangent = isclose(far - near, dia, abs_tol=_EPS, rel_tol=0)
    report(
        "LAP_CONTACT_GEOMETRY",
        tangent,
        "Check the tangency of the lower and shifted upper side bars.",
        actual_separation_mm=far - near,
        required_separation_mm=dia,
    )
    unique_mark = assembly.lap_link_id not in by_mark
    if not unique_mark:
        report("LAP_LINK_MARK", False, "The overlap return needs a distinct mark.")
    if not (tangent and unique_mark):
        return None

    mates = {mark: replace(ordinary[mark], y_from_top_mm=far) for mark in lap.bar_ids}
    upper = tuple(mates.get(bar.bar_id, bar) for bar in bars)
    overlap = (
        *bars,
        *(replace(bar, bar_id=f"{mark}-U") for mark, bar in mates.items()),
    )
    exclusions = {(mark, f"{mark}-U") for mark in mates}
    clear, first_bar, second_bar = min(
        (
            dist(_point(a), _point(b)) - (a.diameter_mm + b.diameter_mm) / 2,
            a.bar_id,
            b.bar_id,
        )
        for a, b in combinations(overlap, 2)
        if (a.bar_id, b.bar_id) not in exclusions
    )
    clear_limit = max(25, steel.aggregate_size_mm + 5)
    report(
        "LAP_CLEAR_SPACING",
        clear >= clear_limit - _EPS,
        "Check the clear space between unrelated longitudinal bars.",
        actual_mm=clear,
        limit_mm=clear_limit,
        limiting_bar_ids=(first_bar, second_bar),
    )
    ratio = fsum(bar.area_mm2 for bar in overlap) / (g.b_mm * g.D_mm)
    report(
        "LAP_STEEL_RATIO",
        ratio <= 0.04,
        "Check the gross longitudinal steel ratio in the overlap.",
        actual=ratio,
        limit=0.04,
    )
    cover = steel.nominal_cover_mm
    inside = cover + hoop.diameter_mm
    encloses = all(
        circle_inside_rounded_rectangle(
            *_point(bar),
            bar.diameter_mm / 2,
            inside,
            g.b_mm - inside,
            inside,
            g.D_mm - inside,
            hoop.internal_bend_radius_mm,
        )
        for bar in overlap
    )
    report("LAP_HOOP_ENCLOSURE", encloses, "Check the hoop enclosure of both partners.")
    gap, span = map(
        max,
        zip(
            *(_side_gaps(layout, g.b_mm, inside) for layout in (bars, upper, overlap)),
            strict=True,
        ),
    )
    span_limit = 48 * min(dt, hoop.diameter_mm)
    # Both partner centres must still lie between the side-face corner centres.
    seated = all(
        any(
            bar.bar_id not in mates
            and bar.y_from_top_mm > far
            and abs(bar.x_from_left_mm - mate.x_from_left_mm) <= 2 + _EPS
            for bar in bars
            if bar.row == "outer"
        )
        for mate in mates.values()
    )
    report(
        "LAP_RESTRAINT_SPAN",
        seated and gap <= 300 and span <= span_limit,
        "Check the spacing of side bars and restrained outer-face span.",
        actual_gap_mm=gap,
        limit_gap_mm=300,
        actual_span_mm=span,
        limit_span_mm=span_limit,
    )

    x_levels = by_mark[seat.tie_id]["stations_mm"]
    before, within, after, distances = _lap_support(x_levels, start, end)
    report(
        "LAP_END_RESTRAINT",
        _lap_end_support_ok(x_levels, before, within, after, distances, dt, dia),
        "Check links inside and outside both lap ends.",
        distances_mm=distances,
        limit_mm=4 * dia,
    )

    radius = seat.internal_bend_radius_mm + dt / 2
    lx = return_link(
        axis="x",
        left_mm=left.x_from_left_mm,
        right_mm=right.x_from_left_mm,
        near_mm=near,
        far_mm=far,
        radius_mm=radius,
        tail_mm=assembly.hook_tail_mm,
    )
    fits, minimum_clear = _link_fit(lx, overlap, g.b_mm, g.D_mm, cover, dt)
    fits &= assembly.hook_tail_mm >= 8 * dt
    sections: dict[str, Any] = {}
    for label, layout in (("lower", bars), ("overlap", overlap), ("upper", upper)):
        axes = dict(ordinary)
        if label == "upper":
            axes.update(mates)
        links = {}
        cuts = {}
        for cross in steel.cross_ties:
            if label == "overlap" and cross.tie_id == seat.tie_id:
                links[assembly.lap_link_id] = asdict(lx)
                cuts[assembly.lap_link_id] = lx.cut_length_mm
                continue
            a, b = (axes[mark] for mark in cross.restrained_bar_ids)
            tie_path, cover_ok, spacing = _path_check(
                b_mm=g.b_mm,
                D_mm=g.D_mm,
                cover_mm=cover,
                bars=layout,
                first=a,
                second=b,
                tie=PositionedCrossTie(**cross.model_dump()),
                horizontal=isclose(
                    a.y_from_top_mm, b.y_from_top_mm, rel_tol=0, abs_tol=_EPS
                ),
            )
            fits &= cover_ok and spacing >= -_EPS
            minimum_clear = min(minimum_clear, spacing)
            links[cross.tie_id] = asdict(tie_path)
            cuts[cross.tie_id] = tie_path.centreline_length_mm
        sections[label] = {
            "bars": [
                {
                    **asdict(bar),
                    "bar_id": f"{bar.bar_id}-{'U' if label == 'upper' else 'L'}",
                }
                if bar.bar_id in mates
                else asdict(bar)
                for bar in layout
            ],
            "links": links,
            "cut_lengths_mm": cuts,
        }
    report(
        "LAP_LINK_FIT",
        fits,
        "Check the ordinary cross-ties and double-return link against all physical bars.",
        minimum_link_clear_mm=minimum_clear,
        minimum_tail_mm=8 * dt,
    )
    transverse = [
        {**series, "stations_mm": [*before, *after]}
        if series["bar_id"] == seat.tie_id
        else series
        for series in transverse
    ] + [
        {
            "bar_id": assembly.lap_link_id,
            "role": "cross_tie",
            "diameter_mm": dt,
            "stations_mm": within,
            "derived_cut_mm": lx.cut_length_mm,
            "cut_source": assembly.fabrication_reference,
        }
    ]
    levels = sorted(
        (z, series["diameter_mm"])
        for series in transverse
        for z in series["stations_mm"]
    )
    level_clear = min(b - a - (da + db) / 2 for (a, da), (b, db) in pairwise(levels))
    end_cover = min(min(z, g.unsupported_length_mm - z) - d / 2 for z, d in levels)
    report(
        "LAP_LINK_LEVELS",
        level_clear >= -_EPS,
        "Check separation of transverse levels.",
        actual_mm=level_clear,
        limit_mm=0,
    )
    report(
        "LAP_LINK_END_COVER",
        end_cover >= request.end_detail.end_face_clearance_mm,
        "Check clear cover from transverse steel to both member ends.",
        actual_mm=end_cover,
        limit_mm=request.end_detail.end_face_clearance_mm,
    )
    stresses = _gross_lap_stresses(request, start, end)
    compression_verified = bool(
        assembly.compression_reference and stresses and min(stresses) > 0
    )
    record(
        "COLUMN.LAP_COMPRESSION_BASIS",
        EngineeringStatus.PASS if compression_verified else EngineeringStatus.HOLD,
        path,
        "Check the supplied interval basis and compression in every supplied overlap row.",
        assembly.compression_reference or _SOURCE,
        minimum_gross_stress_nmm2=min(stresses, default=None),
    )

    return _MixedContactSplice(
        start_mm=start,
        end_mm=end,
        required_lap_mm=required,
        upper=upper,
        pieces=_split_pieces(
            bars,
            mates,
            start,
            end,
            -request.end_detail.start_straight_mm,
            g.unsupported_length_mm + request.end_detail.end_straight_mm,
        ),
        transverse=transverse,
        sections=sections,
        lap_stations_mm=within,
        end_support_distances_mm=distances,
        minimum_unrelated_bar_clear_mm=clear,
        minimum_link_clear_mm=minimum_clear,
        hoop_centreline_radius_mm=hoop.internal_bend_radius_mm + hoop.diameter_mm / 2,
        steel_ratio=ratio,
        fabrication_reference=assembly.fabrication_reference,
        y_plane_setback_mm=None,
        corner_level_clear_mm=None,
        corner_end_cover_mm=None,
        transverse_level_clear_mm=level_clear,
        transverse_end_cover_mm=end_cover,
    )
