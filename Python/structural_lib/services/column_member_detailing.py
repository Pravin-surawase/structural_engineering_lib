"""Check supplied short tied column actions and project one physical schedule."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, replace
from itertools import pairwise
from math import isclose, pi
from typing import Any

from structural_lib.codes.is456.column.member_detailing import (
    ordinary_column_shear,
    straight_column_bond_lengths,
)
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.bbs import calculate_bar_weight
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.column_tied_member import (
    check_tied_rectangular_member,
    evaluate_tied_rectangular_cage,
)
from structural_lib.services.contracts.column_member import (
    RectangularColumnActionsV1,
    RectangularColumnCageV1,
    TiedRectangularColumnInputV1,
)
from structural_lib.services.contracts.column_member_detailing import (
    ColumnMemberDetailingInputV1,
    ColumnTieZoneV1,
)

WORKFLOW = "is456.column.member-detailing/v1"
Result = CanonicalFamilyResultV1[dict[str, Any]]
_Record = Callable[..., None]
_PASS = EngineeringStatus.PASS
_FAIL = EngineeringStatus.FAIL
_HOLD = EngineeringStatus.HOLD
_BOND = "IS 456:2000 Cl. 26.2.1 and 26.2.5.1"
_TIE = "IS 456:2000 Cl. 26.5.3.2 and declared project tie placement"
_SHEAR = "IS 456:2000 Cl. 40.1–40.4 and Tables 19–20"


def _zone_cage(
    request: ColumnMemberDetailingInputV1, zone: ColumnTieZoneV1
) -> RectangularColumnCageV1:
    steel = request.reinforcement
    if steel.tie is None:
        return steel
    return steel.model_copy(
        update={"tie": steel.tie.model_copy(update={"spacing_mm": zone.pitch_mm})}
    )


def _hoop_grid(
    request: ColumnMemberDetailingInputV1, zones: list[ColumnTieZoneV1], record: _Record
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
    record(
        "COLUMN.LAP_ASSEMBLY_REQUIRED",
        _HOLD,
        "laps",
        "Check splice partner paths, transition geometry, local restraint and congestion before issuing a spliced member schedule.",
        _BOND,
    )
    return details


def _check_actions(
    request: ColumnMemberDetailingInputV1,
    zones: list[ColumnTieZoneV1],
    grid: list[float],
    valid_zones: set[str],
    record: _Record,
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
        local = check_tied_rectangular_member(
            TiedRectangularColumnInputV1(
                identity=request.identity,
                geometry=geometry,
                materials=materials,
                reinforcement=_zone_cage(request, zone),
                actions=RectangularColumnActionsV1.model_validate(
                    action.model_dump(exclude={"combination_id", "vx_kn", "vy_kn"})
                ),
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
        if local.engineering_status is not _PASS:
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
        shear = ordinary_column_shear(
            width_mm=width,
            d_mm=depth - steel.bar_center_offset_mm,
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
    request: ColumnMemberDetailingInputV1,
    bars: list[dict[str, Any]],
    transverse: list[dict[str, Any]],
    record: _Record,
) -> dict[str, Any] | None:
    cut = request.transverse_cut_schedule
    marks = {item["bar_id"] for item in transverse}
    if (
        cut is None
        or cut.detailing_revision != request.basis.detailing_revision
        or set(cut.cut_lengths_mm) != marks
    ):
        record(
            "COLUMN.TRANSVERSE_CUT_BASIS",
            _HOLD,
            "transverse_cut_schedule",
            "Supply the approved cut register for exactly these transverse marks and detailing revision.",
            "Supplied cut register",
        )
        return None
    if marks & {bar["bar_id"] for bar in bars} or len(marks) != len(transverse):
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
            "cut_length_mm": length,
            "source": "Straight bar from supplied end projections",
        }
        for bar in bars
    ]
    rows.extend(
        {
            "bar_id": item["bar_id"],
            "role": item["role"],
            "diameter_mm": item["diameter_mm"],
            "quantity": len(item["stations_mm"]),
            "cut_length_mm": cut.cut_lengths_mm[item["bar_id"]],
            "source": cut.reference,
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


def check_column_member_detailing(request: ColumnMemberDetailingInputV1) -> Result:
    """Combine the supplied station and physical detailing checks."""
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
    if steel.layout != "eight_bar":
        record(
            "COLUMN.MEMBER_CAGE_SCOPE",
            _HOLD,
            "reinforcement.layout",
            "The member workflow is qualified for the symmetric eight-bar cage.",
            _TIE,
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
    cage = None
    cross_ties: tuple[dict[str, Any], ...] = ()
    valid_zones = set()
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

        cage, cross_ties = evaluate_tied_rectangular_cage(
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            steel=_zone_cage(request, zone),
            record=record_zone,
        )
        if all(check["status"] == _PASS.value for check in checks[first:]):
            valid_zones.add(zone.zone_id)
    bars = [asdict(bar) for bar in cage.bars] if cage is not None else []
    transverse = []
    if cage is not None and steel.tie is not None:
        hoop = steel.tie
        perimeter = 2 * (cage.tie_centreline_width_mm + cage.tie_centreline_depth_mm)
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
        transverse.extend(
            {
                "bar_id": item["tie_id"],
                "role": "cross_tie",
                "diameter_mm": hoop.diameter_mm,
                "stations_mm": [
                    station + item["station_offset_mm"] for station in grid
                ],
                "minimum_path_mm": max(
                    abs(a - b)
                    for a, b in zip(item["start_mm"], item["end_mm"], strict=True)
                ),
            }
            for item in cross_ties
        )
    end_required, lap_required = straight_column_bond_lengths(
        steel.longitudinal_bar_diameter_mm, materials.fck_nmm2, materials.fy_nmm2
    )
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
        )
    laps = _check_laps(
        request, zones, {bar["bar_id"] for bar in bars}, lap_required, record
    )
    actions = _check_actions(request, zones, grid, valid_zones, record)
    if grid and cage is not None:
        schedule = _bar_schedule(request, bars, transverse, record)
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
            "hoop_stations_mm": grid,
            "tie_zones": [zone.model_dump() for zone in zones],
            "cage": asdict(cage) if cage is not None else None,
            "transverse": transverse,
            "cross_ties": cross_ties,
            "bbs": schedule,
        },
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Checks only the supplied stations and combinations for an ordinary short tied eight-bar rectangle.",
            "Shear uses the lowest Table 19 row and the two closed hoop legs in one local plane. Cross-ties receive no shear credit.",
            "Straight end projections require separately checked adjoining concrete. Compression lap checks do not resolve the physical splice assembly.",
            "The continuous-bar schedule uses the supplied approved transverse cut lengths.",
        ),
        assumptions=(
            "Positive Mx compresses the top face; positive My compresses the left face. Vy uses D and Vx uses b as overall depth.",
            "The stated tie grade, nonseismic application, project end clearances and straight development basis apply to this member.",
        ),
        provenance=(_SHEAR, _TIE, _BOND),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))
