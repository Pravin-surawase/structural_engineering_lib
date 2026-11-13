"""Check supplied short tied column actions and project one physical schedule."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, replace
from itertools import pairwise
from math import fsum, isclose, pi
from typing import Any, TypeVar

from structural_lib.codes.is456.column.member_detailing import (
    ordinary_column_shear,
    straight_column_bond_lengths,
)
from structural_lib.codes.is456.column.positioned import positioned_member_strength
from structural_lib.codes.is456.column.positioned_biaxial import PositionedColumnBar
from structural_lib.core.result_contract import (
    EngineeringStatus,
    FreshnessStatus,
    StructuralIssueV1,
)
from structural_lib.services.bbs import calculate_bar_weight
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.column_contact_splice import (
    ContactSplice,
    check_contact_splice,
)
from structural_lib.services.column_positioned_member import (
    check_positioned_rectangular_member,
    evaluate_positioned_rectangular_cage,
)
from structural_lib.services.column_tied_member import (
    check_tied_rectangular_member,
    evaluate_tied_rectangular_cage,
)
from structural_lib.services.contracts.column_member import (
    PositionedColumnCageV1,
    PositionedRectangularColumnInputV1,
    RectangularColumnActionsV1,
    RectangularColumnCageV1,
    TiedRectangularColumnInputV1,
)
from structural_lib.services.contracts.column_member_detailing import (
    ColumnMemberDetailingInputV1,
    ColumnTieZoneV1,
    PositionedColumnMemberDetailingInputV1,
)

WORKFLOW = "is456.column.member-detailing/v1"
Result = CanonicalFamilyResultV1[dict[str, Any]]
DetailingRequest = ColumnMemberDetailingInputV1 | PositionedColumnMemberDetailingInputV1
PositionedBars = tuple[PositionedColumnBar, ...]
_Record = Callable[..., None]
_PASS = EngineeringStatus.PASS
_FAIL = EngineeringStatus.FAIL
_HOLD = EngineeringStatus.HOLD
_BOND = "IS 456:2000 Cl. 26.2.1 and 26.2.5.1"
_TIE = "IS 456:2000 Cl. 26.5.3.2 and declared project tie placement"
_SHEAR = "IS 456:2000 Cl. 40.1–40.4 and Tables 19–20"


_Cage = TypeVar("_Cage", RectangularColumnCageV1, PositionedColumnCageV1)


def _zone_cage(steel: _Cage, zone: ColumnTieZoneV1) -> _Cage:
    if steel.tie is None:
        return steel
    return steel.model_copy(
        update={"tie": steel.tie.model_copy(update={"spacing_mm": zone.pitch_mm})}
    )


def _hoop_grid(
    request: DetailingRequest, zones: list[ColumnTieZoneV1], record: _Record
) -> list[float]:
    ends = request.end_detail
    length = request.geometry.unsupported_length_mm
    offset = ends.end_hoop_offset_mm
    if not (
        isclose(zones[0].start_mm, offset, rel_tol=0, abs_tol=1e-7)
        and isclose(zones[-1].end_mm, length - offset, rel_tol=0, abs_tol=1e-7)
        and all(
            isclose(left.end_mm, right.start_mm, rel_tol=0, abs_tol=1e-7)
            for left, right in pairwise(zones)
        )
    ):
        record(
            "COLUMN.TIE_ZONE_COVERAGE",
            _FAIL,
            "tie_zones",
            "Zones must meet without gaps or overlaps from the first to last declared hoop level.",
            _TIE,
        )
        return []
    positions: list[float] = []
    for zone in zones:
        intervals = (zone.end_mm - zone.start_mm) / zone.pitch_mm
        count = round(intervals)
        if count < 1 or not isclose(intervals, count, rel_tol=0, abs_tol=1e-7):
            record(
                "COLUMN.TIE_ZONE_GRID",
                _FAIL,
                "tie_zones",
                f"Pitch does not place hoops at both ends of {zone.zone_id}.",
                _TIE,
            )
            return []
        # The next zone supplies the shared boundary level.
        positions.extend(zone.start_mm + i * zone.pitch_mm for i in range(count))
    positions.append(zones[-1].end_mm)

    tie = request.reinforcement.tie
    if tie is not None:
        link_offset = max(
            (link.station_offset_mm for link in request.reinforcement.cross_ties),
            default=0.0,
        )
        if isinstance(request, PositionedColumnMemberDetailingInputV1):
            clearance = offset - max(
                [tie.diameter_mm / 2]
                + [
                    link.station_offset_mm + link.diameter_mm / 2
                    for link in request.reinforcement.cross_ties
                ]
            )
        else:
            clearance = offset - link_offset - tie.diameter_mm / 2
        passed = (
            offset <= ends.max_end_hoop_offset_mm
            and clearance >= ends.end_face_clearance_mm
        )
        record(
            "COLUMN.TIE_END_PLACEMENT",
            _PASS if passed else _FAIL,
            "end_detail",
            "Check the first hoop and the last link against the supplied end placement limits.",
            _TIE,
            actual_min_clearance_mm=clearance,
            required_clearance_mm=ends.end_face_clearance_mm,
            end_hoop_offset_mm=offset,
            maximum_end_hoop_offset_mm=ends.max_end_hoop_offset_mm,
        )
    return positions


def _check_laps(
    request: ColumnMemberDetailingInputV1,
    zones: list[ColumnTieZoneV1],
    bar_ids: set[str],
    required_mm: float,
    record: _Record,
) -> list[dict[str, Any]]:
    if not request.laps:
        return []
    window = request.approved_lap_zone
    diameter = request.reinforcement.longitudinal_bar_diameter_mm
    laps = sorted(request.laps, key=lambda row: (row.start_mm + row.end_mm, row.lap_id))
    seen: set[str] = set()
    details = []
    for lap in laps:
        path = f"laps.{lap.lap_id}"
        ids = set(lap.bar_ids)
        if ids - bar_ids or seen & ids:
            record(
                "COLUMN.LAP_BAR_ID",
                _FAIL,
                path,
                "Each lap must refer to existing bars, each spliced at most once.",
                _BOND,
            )
        seen.update(ids)
        if diameter > 32 or lap.stress_basis != "compression":
            record(
                "COLUMN.LAP_SCOPE",
                _HOLD,
                path,
                "This check admits only declared equal-bar compression laps up to 32 mm.",
                _BOND,
            )
        else:
            length = lap.end_mm - lap.start_mm
            record(
                "COLUMN.LAP_LENGTH",
                _PASS if length >= required_mm else _FAIL,
                path,
                "Check the supplied overlap against the unrounded compression lap length.",
                _BOND,
                actual_mm=length,
                required_mm=required_mm,
            )
        if window is None:
            record(
                "COLUMN.LAP_ZONE_REQUIRED",
                _HOLD,
                path,
                "Supply the project-approved splice window and tie limit.",
                _BOND,
            )
        elif not (window.start_mm <= lap.start_mm < lap.end_mm <= window.end_mm):
            record(
                "COLUMN.LAP_LOCATION",
                _FAIL,
                path,
                "The lap extends outside the approved splice window.",
                window.reference,
            )
        else:
            pitches = [
                zone.pitch_mm
                for zone in zones
                if zone.start_mm <= lap.end_mm and zone.end_mm >= lap.start_mm
            ]
            if (
                not pitches
                or lap.start_mm < zones[0].start_mm
                or lap.end_mm > zones[-1].end_mm
            ):
                record(
                    "COLUMN.LAP_TIE_PITCH",
                    _FAIL,
                    path,
                    "The tie grid must cover the whole lap.",
                    _TIE,
                )
            else:
                pitch = max(pitches)
                record(
                    "COLUMN.LAP_TIE_PITCH",
                    _PASS if pitch <= window.max_tie_pitch_mm else _FAIL,
                    path,
                    "The whole splice uses the supplied lap-zone pitch limit.",
                    window.reference,
                    actual_mm=pitch,
                    limit_mm=window.max_tie_pitch_mm,
                )
        details.append(
            {
                **lap.model_dump(),
                "provided_mm": lap.end_mm - lap.start_mm,
                "required_mm": required_mm,
            }
        )
    for left, right in pairwise(laps):
        distance = (right.start_mm + right.end_mm - left.start_mm - left.end_mm) / 2
        if distance < 1.3 * required_mm:
            record(
                "COLUMN.LAP_STAGGER",
                _FAIL,
                f"laps.{right.lap_id}",
                "Lap group centres need at least 1.3 times the required lap length.",
                _BOND,
                actual_mm=distance,
                required_mm=1.3 * required_mm,
            )
    max_count = max(
        sum(
            len(lap.bar_ids)
            for lap in laps
            if lap.start_mm <= row.start_mm <= lap.end_mm
        )
        for row in laps
    )
    if max_count > len(bar_ids) / 2:
        record(
            "COLUMN.LAP_BAR_FRACTION",
            _FAIL,
            "laps",
            "This profile limits simultaneous splices to half the bars.",
            _BOND,
            simultaneous_bars=max_count,
            total_bars=len(bar_ids),
        )
    return details


def _check_actions(
    request: DetailingRequest,
    zones: list[ColumnTieZoneV1],
    grid: list[float],
    valid_zones: set[str],
    record: _Record,
    splice: ContactSplice | None = None,
) -> list[dict[str, Any]]:
    geometry, steel, materials = (
        request.geometry,
        request.reinforcement,
        request.materials,
    )
    tie = steel.tie
    rows = []
    for i, action in enumerate(request.actions):
        station = action.check_station_mm
        path = f"actions.{i}"
        matching = [zone for zone in zones if zone.start_mm <= station <= zone.end_mm]
        summary: dict[str, Any] = {
            "combination_id": action.combination_id,
            "station_mm": station,
            "action": action.model_dump(),
            "section": None,
            "shear": None,
        }
        rows.append(summary)
        if not grid or not matching:
            record(
                "COLUMN.SHEAR_ZONE_REQUIRED",
                _HOLD,
                path,
                "The station needs a resolved tie interval within the grid.",
                _TIE,
            )
            continue
        zone = max(matching, key=lambda item: item.pitch_mm)
        summary["zone_id"] = zone.zone_id
        actions = RectangularColumnActionsV1.model_validate(
            action.model_dump(exclude={"combination_id", "vx_kn", "vy_kn"})
        )
        if isinstance(request, PositionedColumnMemberDetailingInputV1):
            local = check_positioned_rectangular_member(
                PositionedRectangularColumnInputV1(
                    identity=request.identity,
                    geometry=request.geometry,
                    materials=materials,
                    reinforcement=_zone_cage(request.reinforcement, zone),
                    actions=actions,
                )
            )
        else:
            local = check_tied_rectangular_member(
                TiedRectangularColumnInputV1(
                    identity=request.identity,
                    geometry=request.geometry,
                    materials=materials,
                    reinforcement=_zone_cage(request.reinforcement, zone),
                    actions=actions,
                )
            )
        identity = local.envelope.result_identity
        assert identity is not None
        strength = local.calculation["strength"]
        summary["section"] = {
            "status": local.engineering_status.value,
            "input_hash": identity.input_hash,
            "utilization": strength["governing_ratio"] if strength else None,
        }
        if splice is not None and strength is not None:
            layouts = {}
            if station <= splice.end_mm:
                layouts["lower"] = strength
            if station >= splice.start_mm:
                layouts["upper"] = asdict(
                    positioned_member_strength(
                        b_mm=geometry.b_mm,
                        D_mm=geometry.D_mm,
                        unsupported_length_mm=geometry.unsupported_length_mm,
                        pu_kn=action.pu_kn,
                        mx_knm=action.mx_knm,
                        my_knm=action.my_knm,
                        fck_nmm2=materials.fck_nmm2,
                        fy_nmm2=materials.fy_nmm2,
                        cage=splice.upper,
                    )
                )
            ratios = [layout["governing_ratio"] for layout in layouts.values()]
            utilization = max(
                (ratio for ratio in ratios if ratio is not None), default=None
            )
            if action.pu_kn >= strength["puz_kn"] or (
                utilization is not None and utilization > 1
            ):
                status = _FAIL
            elif any(ratio is None for ratio in ratios):
                status = _HOLD
            else:
                status = _PASS
            summary["section"] = {
                "status": status.value,
                "input_hash": None,
                "utilization": utilization,
                "splice_layouts": layouts,
            }
            record(
                "COLUMN.LAP_SECTION_STRENGTH",
                status,
                path,
                "Check the applicable eight-bar transfer layouts without crediting both partners.",
                "IS 456:2000 Cl. 39.6 and checked contact assembly",
            )
        elif local.engineering_status is not _PASS:
            for issue in local.issues:
                record(
                    issue.code,
                    local.engineering_status,
                    path,
                    issue.message,
                    "Physical tied rectangular member check",
                )
        if tie is None or any(item.zone_id not in valid_zones for item in matching):
            continue
        if action.vx_kn and action.vy_kn:
            record(
                "COLUMN.COMBINED_SHEAR",
                _HOLD,
                path,
                "Simultaneous nonzero shears need a verified two-plane interaction basis.",
                _SHEAR,
            )
            continue
        if materials.fck_nmm2 not in (20, 25, 30, 35, 40):
            record(
                "COLUMN.SHEAR_MATERIAL",
                _HOLD,
                path,
                "The shear profile uses the M20–M40 tabulated grade columns.",
                _SHEAR,
            )
            continue
        direction = "x" if action.vx_kn else "y"
        if direction == "x":
            width, depth, demand = geometry.D_mm, geometry.b_mm, action.vx_kn
        else:
            width, depth, demand = geometry.b_mm, geometry.D_mm, action.vy_kn
        if isinstance(steel, PositionedColumnCageV1):
            coords = [
                bar.x_from_left_mm if direction == "x" else bar.y_from_top_mm
                for bar in steel.bars
                if bar.row == "outer"
            ]
            if not coords:
                record(
                    "COLUMN.SHEAR_SETBACK_HELD",
                    _HOLD,
                    path,
                    "Outer bars are required for the effective shear depth.",
                    _SHEAR,
                )
                continue
            setback = max(min(coords), depth - max(coords))
        else:
            setback = steel.bar_center_offset_mm
        if direction == "y" and splice is not None and station >= splice.start_mm:
            if splice.y_plane_setback_mm is not None:
                setback = max(setback, splice.y_plane_setback_mm)
        shear = ordinary_column_shear(
            width_mm=width,
            d_mm=depth - setback,
            gross_area_mm2=geometry.b_mm * geometry.D_mm,
            pu_kn=action.pu_kn,
            vu_kn=demand,
            fck_nmm2=materials.fck_nmm2,
            hoop_diameter_mm=tie.diameter_mm,
            hoop_fy_nmm2=request.tie_fy_nmm2,
            pitch_mm=zone.pitch_mm,
        )
        spacing_ok = zone.pitch_mm <= 0.75 * shear.d_mm
        if not spacing_ok:
            record(
                "COLUMN.SHEAR_LINK_SPACING",
                _FAIL,
                path,
                "The spacing exceeds the 0.75d limit of the admitted vertical shear transfer model.",
                _SHEAR,
            )
        if abs(demand) > shear.crushing_kn:
            code = "COLUMN.SHEAR_CRUSHING"
        else:
            code = "COLUMN.SHEAR_CAPACITY"
        status = _PASS if shear.utilization <= 1 else _FAIL
        record(
            code,
            status,
            path,
            "Check signed shear magnitude against the two closed hoop legs and concrete.",
            _SHEAR,
        )
        summary["shear"] = {
            "direction": direction,
            "demand_kn": demand,
            "status": (status if spacing_ok else _FAIL).value,
            "credited_hoop_id": tie.tie_id,
            "credited_legs": 2,
            **asdict(shear),
        }
    return rows


def _bar_schedule(
    request: DetailingRequest,
    bars: list[dict[str, Any]],
    transverse: list[dict[str, Any]],
    record: _Record,
    splice: ContactSplice | None = None,
) -> dict[str, Any] | None:
    cut = request.transverse_cut_schedule
    marks = {item["bar_id"] for item in transverse}
    supplied_marks = {
        item["bar_id"] for item in transverse if "derived_cut_mm" not in item
    }
    if (
        cut is None
        or cut.detailing_revision != request.basis.detailing_revision
        or set(cut.cut_lengths_mm) != supplied_marks
    ):
        record(
            "COLUMN.TRANSVERSE_CUT_BASIS",
            _HOLD,
            "transverse_cut_schedule",
            "Supply the approved cut register for exactly these transverse marks and detailing revision.",
            "Supplied cut register",
        )
        return None
    piece_marks = [bar["bar_id"] for bar in (splice.pieces if splice else bars)]
    if (
        marks & set(piece_marks)
        or len(marks) != len(transverse)
        or len(set(piece_marks)) != len(piece_marks)
    ):
        record(
            "COLUMN.BAR_MARK_CONFLICT",
            _FAIL,
            "reinforcement",
            "Longitudinal and transverse bar marks must be distinct.",
            "Checked bar schedule",
        )
        return None
    if any(
        cut.cut_lengths_mm[item["bar_id"]] < item["minimum_path_mm"]
        for item in transverse
        if item["bar_id"] in supplied_marks
    ):
        record(
            "COLUMN.TRANSVERSE_CUT_LENGTH",
            _FAIL,
            "transverse_cut_schedule",
            "A supplied cut is shorter than its checked centreline projection.",
            cut.reference,
        )
        return None
    length = (
        request.geometry.unsupported_length_mm
        + request.end_detail.start_straight_mm
        + request.end_detail.end_straight_mm
    )
    rows = [
        {
            "bar_id": bar["bar_id"],
            "role": "longitudinal",
            "diameter_mm": bar["diameter_mm"],
            "quantity": 1,
            "cut_length_mm": bar.get("cut_length_mm", length),
            "source": "Checked straight bar path and supplied end projections",
        }
        for bar in (splice.pieces if splice else bars)
    ]
    rows.extend(
        {
            "bar_id": item["bar_id"],
            "role": item["role"],
            "diameter_mm": item["diameter_mm"],
            "quantity": len(item["stations_mm"]),
            "cut_length_mm": (
                item["derived_cut_mm"]
                if "derived_cut_mm" in item
                else cut.cut_lengths_mm[item["bar_id"]]
            ),
            "source": item.get("cut_source", cut.reference),
        }
        for item in transverse
    )
    for row in rows:
        row["total_length_mm"] = row["quantity"] * row["cut_length_mm"]
        row["total_weight_kg"] = calculate_bar_weight(
            row["diameter_mm"], row["total_length_mm"], round_weight=False
        )
    return {
        "rows": rows,
        "quantity": sum(row["quantity"] for row in rows),
        "total_length_mm": sum(row["total_length_mm"] for row in rows),
        "total_weight_kg": sum(row["total_weight_kg"] for row in rows),
    }


def check_column_member_detailing(request: DetailingRequest) -> Result:
    """Combine the supplied station and physical detailing checks."""
    if not isinstance(request, PositionedColumnMemberDetailingInputV1):
        require_request_type(request, ColumnMemberDetailingInputV1)
    checks: list[dict[str, Any]] = []
    issues = []

    def record(
        code: str,
        status: EngineeringStatus,
        path: str,
        message: str,
        source: str,
        **values: Any,
    ) -> None:
        checks.append(
            {
                "code": code,
                "status": status.value,
                "path": path,
                "message": message,
                "source_reference": source,
                **values,
            }
        )
        if status is not _PASS:
            issues.append(StructuralIssueV1(code, path, message))

    basis = request.basis
    if basis.analysis_revision != basis.current_analysis_revision:
        record(
            "COLUMN.STALE_ANALYSIS",
            _HOLD,
            "basis",
            "Supplied action revision is stale.",
            "Declared analysis revision",
        )
    for field in (
        "nonseismic_reference",
        "action_source_reference",
        "end_development_reference",
        "placement_reference",
    ):
        if getattr(basis, field) is None:
            record(
                "COLUMN.MEMBER_BASIS_REQUIRED",
                _HOLD,
                f"basis.{field}",
                "Supply the project basis for this check.",
                "Declared member basis",
            )

    geometry, steel, materials = (
        request.geometry,
        request.reinforcement,
        request.materials,
    )
    if request.identity.member_id is None:
        record(
            "COLUMN.MEMBER_ID_REQUIRED",
            _HOLD,
            "identity.member_id",
            "The schedule requires a member identifier.",
            "Schedule identity",
        )
    zones = sorted(request.tie_zones, key=lambda zone: zone.start_mm)
    grid = _hoop_grid(request, zones, record)
    cage: dict[str, Any] | None = None
    cross_ties: tuple[dict[str, Any], ...] = ()
    tied_cage = None
    valid_zones = set()
    positioned = isinstance(request, PositionedColumnMemberDetailingInputV1)
    bars_positioned = (
        tuple(PositionedColumnBar(**bar.model_dump()) for bar in steel.bars)
        if isinstance(steel, PositionedColumnCageV1)
        else ()
    )
    for zone in zones:
        first = len(checks)

        def record_zone(
            code: str,
            status: EngineeringStatus,
            path: str,
            message: str,
            *,
            zone_id: str = zone.zone_id,
            **values: Any,
        ) -> None:
            source = values.pop("source_reference", _TIE)
            record(
                code, status, f"tie_zones.{zone_id}.{path}", message, source, **values
            )

        if isinstance(steel, PositionedColumnCageV1):
            cage, positioned_links = evaluate_positioned_rectangular_cage(
                b_mm=geometry.b_mm,
                D_mm=geometry.D_mm,
                steel=_zone_cage(steel, zone),
                bars=bars_positioned,
                ratio=fsum(bar.area_mm2 for bar in bars_positioned)
                / (geometry.b_mm * geometry.D_mm),
                record=record_zone,
            )
            cross_ties = tuple(asdict(link) for link in positioned_links)
        else:
            tied_cage, cross_ties = evaluate_tied_rectangular_cage(
                b_mm=geometry.b_mm,
                D_mm=geometry.D_mm,
                steel=_zone_cage(steel, zone),
                record=record_zone,
            )
            cage = asdict(tied_cage) if tied_cage is not None else None
        if all(check["status"] == _PASS.value for check in checks[first:]):
            valid_zones.add(zone.zone_id)

    bars = list(cage["bars"]) if cage is not None else []
    transverse = []
    if cage is not None and steel.tie is not None:
        hoop = steel.tie
        perimeter = 2 * (
            cage["tie_centreline_width_mm"] + cage["tie_centreline_depth_mm"]
        )
        radius = hoop.internal_bend_radius_mm + hoop.diameter_mm / 2
        transverse = [
            {
                "bar_id": hoop.tie_id,
                "role": "hoop",
                "diameter_mm": hoop.diameter_mm,
                "stations_mm": grid,
                "minimum_path_mm": perimeter + (2 * pi - 8) * radius,
            }
        ]
        for item in cross_ties:
            link = {
                "bar_id": item["tie_id"],
                "role": "cross_tie",
                "diameter_mm": item.get("diameter_mm", hoop.diameter_mm),
                "stations_mm": [
                    station + item["station_offset_mm"] for station in grid
                ],
                "minimum_path_mm": max(
                    abs(a - b)
                    for a, b in zip(item["start_mm"], item["end_mm"], strict=True)
                ),
            }
            if positioned:
                link.update(
                    derived_cut_mm=item["centreline_length_mm"],
                    cut_source="Checked positioned cross-tie centreline",
                )
            transverse.append(link)

    diameters = (
        {bar.diameter_mm for bar in bars_positioned}
        if isinstance(steel, PositionedColumnCageV1)
        else {steel.longitudinal_bar_diameter_mm}
    )
    bond = {
        diameter: straight_column_bond_lengths(
            diameter, materials.fck_nmm2, materials.fy_nmm2
        )
        for diameter in sorted(diameters)
    }
    end_required = max(item[0] for item in bond.values())
    lap_required = max(item[1] for item in bond.values())
    for end in ("start", "end"):
        length = getattr(request.end_detail, f"{end}_straight_mm")
        record(
            "COLUMN.END_DEVELOPMENT",
            _PASS if length >= end_required else _FAIL,
            f"end_detail.{end}_straight_mm",
            "Check straight deformed bar development from the member face at full design tension stress.",
            _BOND,
            actual_mm=length,
            required_mm=end_required,
            required_by_diameter_mm={dia: value[0] for dia, value in bond.items()},
        )
    splice = None
    if isinstance(request, PositionedColumnMemberDetailingInputV1):
        laps = [
            {
                **lap.model_dump(),
                "provided_mm": lap.end_mm - lap.start_mm,
                "required_mm": None,
            }
            for lap in request.laps
        ]
        if laps:
            record(
                "COLUMN.POSITIONED_SPLICE_HELD",
                _HOLD,
                "laps",
                "The positioned mixed-cage schedule requires continuous bars; supply a qualified physical splice profile.",
                _BOND,
            )
    else:
        laps = _check_laps(
            request, zones, {bar["bar_id"] for bar in bars}, lap_required, record
        )
        splice = check_contact_splice(
            request, tied_cage, transverse, end_required, record
        )
        if splice is not None:
            transverse = splice.transverse
            laps[0]["required_mm"] = splice.required_lap_mm
    actions = _check_actions(request, zones, grid, valid_zones, record, splice)
    if grid and cage is not None:
        schedule = _bar_schedule(request, bars, transverse, record, splice)
    else:
        schedule = None
    statuses = {item["status"] for item in checks}
    status = (
        _FAIL
        if _FAIL.value in statuses
        else _HOLD if _HOLD.value in statuses else _PASS
    )
    if status is not _PASS:
        schedule = None
    shear_rows = [row for row in actions if row["shear"] is not None]
    governing = max(
        shear_rows, key=lambda row: row["shear"]["utilization"], default=None
    )
    result = canonical_family_result(
        request,
        {
            "checks": checks,
            "actions": actions,
            "governing_shear": governing,
            "end_required_mm": end_required,
            "lap_required_mm": lap_required,
            "laps": laps,
            "contact_splice": splice.to_dict() if splice else None,
            "hoop_stations_mm": grid,
            "tie_zones": [zone.model_dump() for zone in zones],
            "cage": cage,
            "transverse": transverse,
            "cross_ties": cross_ties,
            "bbs": schedule,
        },
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Checks only the supplied stations and combinations for ordinary short tied six- and eight-bar rectangles and continuous positioned mixed cages.",
            "Shear uses the lowest Table 19 row and the two closed hoop legs in one local plane. Cross-ties receive no shear credit.",
            "Straight end projections require separately checked adjoining concrete. An eight-bar physical contact splice supports one side-midpoint or C1/C2 group with straight bars.",
            "The schedule uses approved cut data for the closed hoop. Admitted contact links use their checked centreline lengths.",
        ),
        assumptions=(
            "Positive Mx compresses the top face; positive My compresses the left face. Vy uses D and Vx uses b as overall depth.",
            "The stated tie grade, nonseismic application, project end clearances and straight development basis apply to this member.",
        ),
        provenance=(_SHEAR, _TIE, _BOND),
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=tuple(issues),
            freshness_status=(
                FreshnessStatus.CURRENT
                if basis.analysis_revision == basis.current_analysis_revision
                else FreshnessStatus.STALE
            ),
        ),
    )
