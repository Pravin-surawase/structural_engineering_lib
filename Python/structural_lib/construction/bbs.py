"""AO19: BBS and deterministic cutting data from resolved physical paths."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

from structural_lib.beam.bar_paths import BarPathRole, PathSegmentKind
from structural_lib.beam.semantics import (
    Diagnostic,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
    semantic_hash,
)

from .contracts import (
    BbsOutput,
    BbsRequest,
    BbsRow,
    CouplerItem,
    PlacedLinkZone,
    ShapeDimension,
    SpliceKind,
    StockCut,
    StockPiece,
)

CREATE_BBS_OPERATION = "structural.bbs.create/v1"
BBS_METHOD_REVISION = "structural-bbs-cutting-wp07-v1"


@dataclass
class _OpenStock:
    diameter_mm: float
    steel_grade_n_per_mm2: float
    stock_length_mm: float
    cuts: list[StockCut] = field(default_factory=list)


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _provenance() -> Provenance:
    return Provenance(
        "construction-data-wp07-v1",
        BBS_METHOD_REVISION,
        (
            "PF5 AO19 resolved-path BBS contract",
            "PF7 AR19 schedule, stock, kerf, offcut, and waste reconciliation",
        ),
    )


def _error(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        CREATE_BBS_OPERATION,
        field,
        "construction-bbs",
        remediation,
    )


def _reject(
    inputs: dict[str, dict[str, object]],
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> OperationResult:
    return rejected_result(
        CREATE_BBS_OPERATION,
        inputs,
        (_error(code, message, field, remediation),),
        provenance=_provenance(),
    )


def _zone_stations(zone: object, tolerance: float) -> tuple[float, ...]:
    start = zone.start_station_x_mm  # type: ignore[attr-defined]
    end = zone.end_station_x_mm  # type: ignore[attr-defined]
    spacing = zone.spacing_mm  # type: ignore[attr-defined]
    stations: list[float] = []
    index = 0
    while start + index * spacing <= end + tolerance:
        station = start + index * spacing
        if station <= end + tolerance:
            stations.append(min(station, end))
        index += 1
    if stations and not zone.include_start and abs(stations[0] - start) <= tolerance:  # type: ignore[attr-defined]
        stations.pop(0)
    if stations and not zone.include_end and abs(stations[-1] - end) <= tolerance:  # type: ignore[attr-defined]
        stations.pop()
    return tuple(stations)


def _stock_plan(request: BbsRequest, rows: tuple[BbsRow, ...]) -> tuple[StockPiece, ...] | None:
    policy = request.stock_policy
    stock_lengths = tuple(sorted(policy.stock_lengths_mm))
    cuts: list[tuple[float, str, float, float, str]] = []
    for row in rows:
        for index in range(1, row.scheduled_bar_count + 1):
            cuts.append(
                (
                    row.fabrication_cut_length_each_mm,
                    row.bar_mark,
                    row.diameter_mm,
                    row.steel_grade_n_per_mm2,
                    f"{row.bar_mark}:{index:04d}",
                )
            )
    cuts.sort(key=lambda item: (-item[0], item[1], item[4]))
    opened: list[_OpenStock] = []
    for length, mark, diameter, grade, cut_id in cuts:
        selected: _OpenStock | None = None
        for piece in opened:
            if (
                piece.diameter_mm != diameter
                or piece.steel_grade_n_per_mm2 != grade
            ):
                continue
            used = sum(item.length_mm for item in piece.cuts)
            kerf = len(piece.cuts) * policy.kerf_mm
            if (
                used + kerf + length + policy.kerf_mm
                <= piece.stock_length_mm + 1e-9
            ):
                selected = piece
                break
        if selected is None:
            stock = next(
                (
                    value
                    for value in stock_lengths
                    if length + policy.kerf_mm <= value + 1e-9
                ),
                None,
            )
            if stock is None:
                return None
            selected = _OpenStock(diameter, grade, stock)
            opened.append(selected)
        selected.cuts.append(StockCut(cut_id, mark, length))

    pieces: list[StockPiece] = []
    for index, piece in enumerate(opened, start=1):
        piece_cuts: tuple[StockCut, ...] = tuple(piece.cuts)
        stock = piece.stock_length_mm
        kerf = len(piece_cuts) * policy.kerf_mm
        remainder = stock - math.fsum(cut.length_mm for cut in piece_cuts) - kerf
        reusable = remainder if remainder + 1e-9 >= policy.reusable_offcut_min_mm else 0.0
        waste = 0.0 if reusable else remainder
        pieces.append(
            StockPiece(
                f"STOCK-{index:04d}",
                piece.diameter_mm,
                piece.steel_grade_n_per_mm2,
                stock,
                piece_cuts,
                kerf,
                reusable,
                waste,
            )
        )
    return tuple(pieces)


def _schedule_reconciles(request: BbsRequest) -> bool:
    schedule = request.schedule
    path_ids = [item.bar_id for item in schedule.paths]
    mark_names = [item.bar_mark for item in schedule.marks]
    if (
        not schedule.paths
        or not schedule.marks
        or len(path_ids) != len(set(path_ids))
        or len(mark_names) != len(set(mark_names))
    ):
        return False
    tolerance = request.station_tolerance_mm
    for summary in schedule.marks:
        paths = [item for item in schedule.paths if item.bar_mark == summary.bar_mark]
        if (
            not paths
            or summary.count != len(paths)
            or set(summary.bar_ids) != {item.bar_id for item in paths}
            or len(summary.bar_ids) != len(set(summary.bar_ids))
        ):
            return False
        first = paths[0]
        if (
            summary.role is not first.role
            or abs(summary.diameter_mm - first.diameter_mm) > tolerance
            or abs(summary.steel_grade_n_per_mm2 - first.steel_grade_n_per_mm2)
            > tolerance
            or summary.bundle_size != first.bundle_size
            or summary.closed != first.closed
            or abs(
                summary.developed_centreline_length_mm
                - first.developed_centreline_length_mm
            )
            > tolerance
        ):
            return False
        for path in paths:
            if (
                path.role is not summary.role
                or abs(path.diameter_mm - summary.diameter_mm) > tolerance
                or abs(path.steel_grade_n_per_mm2 - summary.steel_grade_n_per_mm2)
                > tolerance
                or path.bundle_size != summary.bundle_size
                or path.closed != summary.closed
                or abs(
                    math.fsum(item.centreline_length_mm for item in path.segments)
                    - path.developed_centreline_length_mm
                )
                > tolerance
                or len(path.segments) != len(first.segments)
            ):
                return False
            for left, right in zip(path.segments, first.segments, strict=True):
                if (
                    left.kind is not right.kind
                    or abs(left.centreline_length_mm - right.centreline_length_mm)
                    > tolerance
                    or left.bend_kind is not right.bend_kind
                    or left.bend_radius_mm != right.bend_radius_mm
                    or left.bend_angle_degrees != right.bend_angle_degrees
                ):
                    return False
    return {item.bar_mark for item in schedule.paths} == set(mark_names)


def create_bbs(request: BbsRequest) -> OperationResult:
    """Create fabrication rows and a deterministic, explicitly heuristic cut plan."""

    inputs = effective_inputs(request=request)
    schedule = request.schedule
    policy = request.stock_policy
    convention = request.shape_convention
    identities = (
        request.profile_id,
        request.project_basis_id,
        request.member_id,
        request.detail_revision_id,
        request.schedule_result_id,
        request.schedule_output_payload_id,
        convention.convention_id,
        convention.revision_id,
        policy.policy_id,
        policy.revision_id,
    )
    if not all(_text(value) for value in identities):
        return _reject(inputs, "BBS.IDENTITY", "Complete schedule and policy identities are required.", "request", "Supply every current identity.")
    if (
        schedule.profile_id != request.profile_id
        or schedule.project_basis_id != request.project_basis_id
        or schedule.member_id != request.member_id
        or schedule.detail_revision_id != request.detail_revision_id
        or not schedule.passed
    ):
        return _reject(inputs, "BBS.SCHEDULE_STALE", "The BBS request must bind the current passing resolved schedule.", "schedule", "Re-resolve reinforcement paths for the active detail revision.")
    if request.schedule_output_payload_id != semantic_hash(
        "output_payload_id", schedule
    ):
        return _reject(inputs, "BBS.SCHEDULE_BINDING", "The schedule payload does not match its canonical output identity.", "schedule_output_payload_id", "Bind the unchanged AO18 output payload.")
    if not _schedule_reconciles(request):
        return _reject(inputs, "BBS.SCHEDULE_RECONCILIATION", "Resolved paths, mark summaries, counts, materials, and developed lengths must reconcile exactly.", "schedule", "Use the unchanged passing AO18 output.")
    if convention.length_basis != "resolved_centreline_v1":
        return _reject(inputs, "BBS.CONVENTION", "WP07 accepts the resolved-centreline fabrication convention only.", "shape_convention.length_basis", "Use the versioned resolved centreline basis.")
    if (
        not math.isfinite(request.steel_density_kg_per_m3)
        or request.steel_density_kg_per_m3 <= 0
        or policy.allocation_method != "first_fit_decreasing_v1"
        or not policy.stock_lengths_mm
        or len(policy.stock_lengths_mm) != len(set(policy.stock_lengths_mm))
        or any(not math.isfinite(value) or value <= 0 for value in policy.stock_lengths_mm)
        or not math.isfinite(policy.kerf_mm)
        or policy.kerf_mm < 0
        or not math.isfinite(policy.reusable_offcut_min_mm)
        or policy.reusable_offcut_min_mm < 0
        or not math.isfinite(request.station_tolerance_mm)
        or request.station_tolerance_mm <= 0
    ):
        return _reject(inputs, "BBS.POLICY", "Density, stock lengths, kerf, offcut threshold, tolerance, and allocation method must be valid.", "stock_policy", "Correct the explicit fabrication policy.")

    splice_ids = [item.splice_id for item in request.splice_records]
    referenced_splices = sorted({item for path in schedule.paths for item in path.splice_ids})
    if (
        len(splice_ids) != len(set(splice_ids))
        or sorted(splice_ids) != referenced_splices
        or any(
            not _text(item.splice_id)
            or not isinstance(item.kind, SpliceKind)
            or not math.isfinite(item.station_x_mm)
            or not _text(item.qualification_reference)
            or (item.kind is SpliceKind.LAP and item.coupler_count != 0)
            or (item.kind is SpliceKind.COUPLER and item.coupler_count <= 0)
            for item in request.splice_records
        )
    ):
        return _reject(inputs, "BBS.SPLICE", "Every path splice must have exactly one qualified lap or coupler record.", "splice_records", "Bind each referenced splice; model lap length in the physical path and couplers as hardware.")

    zone_ids = [item.zone_id for item in request.link_zones]
    if len(zone_ids) != len(set(zone_ids)) or any(
        not _text(item.zone_id)
        or not _text(item.bar_mark)
        or not all(math.isfinite(value) for value in (item.start_station_x_mm, item.end_station_x_mm, item.spacing_mm))
        or item.start_station_x_mm > item.end_station_x_mm
        or item.spacing_mm <= 0
        or abs(
            (item.end_station_x_mm - item.start_station_x_mm) / item.spacing_mm
            - round(
                (item.end_station_x_mm - item.start_station_x_mm)
                / item.spacing_mm
            )
        )
        > request.station_tolerance_mm
        for item in request.link_zones
    ):
        return _reject(inputs, "BBS.LINK_ZONE", "Link zones require unique identities, ordered bounds, and positive spacing.", "link_zones", "Correct the explicit first/last placement convention.")

    placed_zones: list[PlacedLinkZone] = []
    expected_by_mark: dict[str, list[float]] = defaultdict(list)
    for zone in sorted(request.link_zones, key=lambda item: (item.bar_mark, item.start_station_x_mm, item.zone_id)):
        stations = _zone_stations(zone, request.station_tolerance_mm)
        for station in stations:
            if any(abs(station - prior) <= request.station_tolerance_mm for prior in expected_by_mark[zone.bar_mark]):
                return _reject(inputs, "BBS.LINK_BOUNDARY_DUPLICATE", "Adjacent link zones assign the same physical station more than once.", f"link_zones[{zone.zone_id}]", "Give the shared boundary to exactly one zone.")
            expected_by_mark[zone.bar_mark].append(station)
        placed_zones.append(PlacedLinkZone(zone.zone_id, zone.bar_mark, stations, len(stations)))
    transverse_marks = {
        path.bar_mark
        for path in schedule.paths
        if path.role is BarPathRole.TRANSVERSE_LINK
    }
    if transverse_marks != set(expected_by_mark):
        return _reject(inputs, "BBS.LINK_ZONE_REQUIRED", "Every resolved transverse-link mark requires explicit placement-zone ownership, with no unused zone mark.", "link_zones", "Supply boundary conventions for every physical link mark.")
    for mark_name, expected in expected_by_mark.items():
        actual = sorted(
            path.segments[0].start.station_x_mm
            for path in schedule.paths
            if path.bar_mark == mark_name
            and path.role is BarPathRole.TRANSVERSE_LINK
        )
        expected_sorted = sorted(expected)
        if len(actual) != len(expected_sorted) or any(
            abs(left - right) > request.station_tolerance_mm
            for left, right in zip(actual, expected_sorted, strict=True)
        ):
            return _reject(inputs, "BBS.LINK_PATH_MISMATCH", "Link-zone stations must match the resolved physical link paths exactly.", f"link_zones[mark={mark_name}]", "Resolve one link path at every owned placement station.")

    paths_by_mark = {mark.bar_mark: [path for path in schedule.paths if path.bar_mark == mark.bar_mark] for mark in schedule.marks}
    rows: list[BbsRow] = []
    for summary in sorted(schedule.marks, key=lambda item: item.bar_mark):
        paths = paths_by_mark[summary.bar_mark]
        exemplar = paths[0]
        scheduled_count = summary.count * summary.bundle_size
        cut_each = summary.developed_centreline_length_mm
        total_cut = cut_each * scheduled_count
        mass = math.pi / 4 * summary.diameter_mm**2 * total_cut / 1e9 * request.steel_density_kg_per_m3
        dimensions = tuple(
            ShapeDimension(
                segment.segment_id.split(":")[-1],
                segment.kind.value,
                segment.centreline_length_mm,
                segment.bend_radius_mm,
                segment.bend_angle_degrees,
            )
            for segment in exemplar.segments
        )
        rows.append(
            BbsRow(
                summary.bar_mark,
                summary.role,
                summary.diameter_mm,
                summary.steel_grade_n_per_mm2,
                summary.bundle_size,
                summary.count,
                scheduled_count,
                "-".join("B" if item.kind is PathSegmentKind.BEND_ARC else "S" for item in exemplar.segments),
                dimensions,
                summary.developed_centreline_length_mm,
                cut_each,
                total_cut,
                mass,
                tuple(path.bar_id for path in paths),
                tuple(sorted({item for path in paths for item in path.splice_ids})),
            )
        )
    row_items = tuple(rows)
    stock_pieces = _stock_plan(request, row_items)
    if stock_pieces is None:
        return _reject(inputs, "BBS.STOCK_LENGTH", "At least one scheduled cut plus its required kerf exceeds every stock length.", "stock_policy.stock_lengths_mm", "Provide a compatible stock length or a qualified explicit splice.")

    scheduled_length = math.fsum(item.scheduled_cut_length_mm for item in row_items)
    stock_length = math.fsum(item.stock_length_mm for item in stock_pieces)
    kerf_length = math.fsum(item.kerf_length_mm for item in stock_pieces)
    reusable = math.fsum(item.reusable_offcut_length_mm for item in stock_pieces)
    waste = math.fsum(item.waste_length_mm for item in stock_pieces)
    if abs(stock_length - scheduled_length - kerf_length - reusable - waste) > 1e-6:
        return _reject(inputs, "BBS.RECONCILIATION", "Stock length does not reconcile to cuts, kerf, reusable offcuts, and waste.", "stock_pieces", "Correct the cutting allocation.")
    purchased_mass = math.fsum(
        math.pi / 4 * item.diameter_mm**2 * item.stock_length_mm / 1e9 * request.steel_density_kg_per_m3
        for item in stock_pieces
    )
    couplers = tuple(
        CouplerItem(item.splice_id, item.station_x_mm, item.coupler_count, item.qualification_reference)
        for item in sorted(request.splice_records, key=lambda value: value.splice_id)
        if item.kind is SpliceKind.COUPLER
    )
    output = BbsOutput(
        request.profile_id,
        request.project_basis_id,
        request.member_id,
        request.detail_revision_id,
        request.schedule_result_id,
        convention.revision_id,
        policy.revision_id,
        row_items,
        tuple(placed_zones),
        stock_pieces,
        couplers,
        scheduled_length,
        stock_length,
        kerf_length,
        reusable,
        waste,
        math.fsum(item.theoretical_mass_kg for item in row_items),
        purchased_mass,
        "heuristic_first_fit_decreasing",
        True,
    )
    return completed_result(
        CREATE_BBS_OPERATION,
        inputs,
        {"bbs": output},
        provenance=_provenance(),
    )
