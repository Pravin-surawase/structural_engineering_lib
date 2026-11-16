"""Checked continuous bar and ordinary link schedules for two-span beams."""

from __future__ import annotations

import csv
import html
import io
import math
from dataclasses import replace
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.beam.bar_paths import (
    BarPathOutput,
    BarPathRequest,
    BarPathRole,
    BarPathSeed,
    BendKind,
    MemberLocalCoordinateSystem,
    PathNode,
    PathPoint,
    resolve_bar_paths,
)
from structural_lib.beam.detailing import (
    AnchorageCheckRequest,
    AnchorageDirection,
    AnchorageLocation,
    AnchoragePath,
    BarSurface,
    DevelopmentLengthRequest,
    LapCurtailmentCheckRequest,
    LinkCage,
    LongitudinalBarPath,
    ReinforcementArrangementCheckRequest,
    ReinforcementRole,
    SpliceDetail,
    SpliceKind,
    StationSteelDemand,
    StressState,
    check_anchorage,
    check_laps_and_curtailment,
    check_reinforcement_arrangement,
)
from structural_lib.beam.physical_torsion import (
    ClosedLinkDetailRequest,
    check_closed_link_detail,
)
from structural_lib.beam.reinforcement import Face
from structural_lib.beam.semantics import (
    EngineeringState,
    ExecutionState,
    OperationResult,
    semantic_hash,
)
from structural_lib.beam.shear_torsion import TransverseLink
from structural_lib.construction import (
    BbsRequest,
    CuttingStockPolicy,
    LinkPlacementZone,
    ShapeConvention,
    SpliceRecord,
    create_bbs,
)
from structural_lib.construction import (
    SpliceKind as ScheduleSpliceKind,
)
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import (
    EngineeringStatus,
    FreshnessStatus,
    StructuralIssueV1,
)
from structural_lib.reporting.calculation_package import result_binding
from structural_lib.services.beam_continuous import (
    BeamContinuousCheckResultV1,
    _bar_positions,
    _check_row,
    _positive_support_web_capacity,
    _row_issues,
    _sections,
    _support_faces,
    check_continuous_beam,
)
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    _input_hash,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousCheckRequestV1,
    BeamLayeredContinuousCheckRequestV1,
    BeamSectionBarV1,
    Identifier,
    Reference,
)
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    model_validate_or_error,
)

WORKFLOW = "is456.beam.continuous-detailing/v1"


class BeamOrdinaryLinkDetailV1(StrictPublicModel):
    """Actual placement interval and fabricated hook geometry for one link mark."""

    first_station_mm: float = Field(ge=-1500, le=30000)
    last_station_mm: float = Field(ge=0, le=32000)
    internal_bend_radius_mm: float = Field(gt=0, le=100)
    hook_vertex_leg_mm: float = Field(gt=0, le=300)
    hook_plane_offset_mm: float = Field(gt=0, le=100)
    source_reference: Reference


class BeamBottomCutoffV1(StrictPublicModel):
    """One straight bottom bar terminating in the first clear span."""

    bar_id: Identifier
    theoretical_station_id: Identifier
    termination_station_id: Identifier


class BeamBarEditV1(StrictPublicModel):
    """An explicit diameter change and optional transverse centre change."""

    bar_id: Identifier
    diameter_mm: float = Field(ge=8, le=40)
    x_from_left_mm: float | None = Field(default=None, gt=0)


class BeamSeparatedBottomLapV1(StrictPublicModel):
    """One equal-diameter separated bottom bar splice within the first span."""

    bar_id: Identifier
    partner_bar_id: Identifier
    partner_x_from_left_mm: float = Field(gt=0)
    start_station_id: Identifier
    middle_station_id: Identifier
    end_station_id: Identifier
    placement_reference: Reference


class BeamContinuousDetailingInputV1(StrictPublicModel):
    """Two-span action and reinforcement check with a current ordinary link detail."""

    schema_version: Literal["is456-beam-continuous-detailing-input/v1"] = (
        "is456-beam-continuous-detailing-input/v1"
    )
    identity: FamilyIdentityV1
    member: BeamContinuousCheckRequestV1 | BeamLayeredContinuousCheckRequestV1
    link_detail: BeamOrdinaryLinkDetailV1 | None = None
    stock_length_mm: float = Field(gt=0, le=18000)
    cutoff: BeamBottomCutoffV1 | None = None
    lap: BeamSeparatedBottomLapV1 | None = None

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.identity.member_id != self.member.member_id:
            raise ValueError("Member and detailing identities must agree.")
        return self


def _physical_paths(
    request: BeamContinuousDetailingInputV1,
    source_hash: str,
    cutoff_end_mm: float | None,
    lap_bounds: tuple[float, float] | None,
) -> tuple[BarPathRequest, ClosedLinkDetailRequest] | None:
    member, detail = request.member, request.link_detail
    extent = member.straight_bars
    if detail is None or extent is None:
        return None
    spacing = member.link_spacing_mm
    intervals = (detail.last_station_mm - detail.first_station_mm) / spacing
    left, _, right = member.supports
    if (
        not 1 <= round(intervals) <= 250
        or not math.isclose(intervals, round(intervals), rel_tol=0, abs_tol=1e-8)
        or detail.first_station_mm > left.right_face_mm
        or detail.last_station_mm < right.left_face_mm
    ):
        return None
    diameter = member.link_diameter_mm
    mark = f"{member.member_id}-L{diameter:g}"
    inset = member.clear_cover_mm + diameter / 2
    x1, x2 = inset, member.width_mm - inset
    y1, y2 = inset, member.depth_mm - inset
    radius = detail.internal_bend_radius_mm + diameter / 2
    tail = detail.hook_vertex_leg_mm
    if not (
        left.left_face_mm + inset <= detail.first_station_mm
        and detail.last_station_mm + detail.hook_plane_offset_mm
        <= right.right_face_mm - inset
        and tail < min(x2 - x1, y2 - y1)
    ):
        return None
    bars = tuple(
        LongitudinalBarPath(
            bar.bar_id,
            f"{member.member_id}-{bar.face}"
            + (f"-L{bar.layer}" if isinstance(bar, BeamSectionBarV1) else "")
            + f"-D{bar.diameter_mm:g}"
            + (
                "-cutoff"
                if request.cutoff and bar.bar_id == request.cutoff.bar_id
                else ""
            ),
            ReinforcementRole(f"{bar.face}_longitudinal"),
            bar.diameter_mm,
            bar.layer if isinstance(bar, BeamSectionBarV1) else 1,
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            extent.start_mm,
            (
                cutoff_end_mm
                if cutoff_end_mm is not None
                and request.cutoff
                and bar.bar_id == request.cutoff.bar_id
                else extent.end_mm
            ),
            0.87 * member.fy_nmm2,
        )
        for bar in member.bars
    )
    if request.lap is not None and lap_bounds is not None:
        lap = request.lap
        start, end = lap_bounds
        original = next(bar for bar in bars if bar.bar_id == lap.bar_id)
        bars = (
            *(bar for bar in bars if bar.bar_id != lap.bar_id),
            replace(
                original, bar_mark=f"{original.bar_mark}-lap-I", end_station_mm=end
            ),
            replace(
                original,
                bar_id=lap.partner_bar_id,
                bar_mark=f"{original.bar_mark}-lap-J",
                start_station_mm=start,
                x_from_left_mm=lap.partner_x_from_left_mm,
            ),
        )
    seeds = [
        BarPathSeed(
            bar.bar_id,
            bar.bar_mark,
            BarPathRole(bar.role.value),
            bar.layer,
            bar.diameter_mm,
            member.fy_nmm2,
            (
                PathNode(
                    "start",
                    PathPoint(
                        bar.start_station_mm, bar.x_from_left_mm, bar.y_from_top_mm
                    ),
                ),
                PathNode(
                    "end",
                    PathPoint(
                        bar.end_station_mm, bar.x_from_left_mm, bar.y_from_top_mm
                    ),
                ),
            ),
            splice_ids=(
                ("bottom-lap",)
                if request.lap
                and bar.bar_id in (request.lap.bar_id, request.lap.partner_bar_id)
                else ()
            ),
        )
        for bar in bars
    ]
    shift = detail.hook_plane_offset_mm
    vertices = (
        (0, x1 + tail, y1),
        (0, x1, y1),
        (0, x1, y2),
        (shift, x2, y2),
        (shift, x2, y1),
        (shift, x1, y1),
        (shift, x1, y1 + tail),
    )
    used_ids = {bar.bar_id for bar in bars}
    for index in range(round(intervals) + 1):
        station = detail.first_station_mm + index * spacing
        bar_id = f"{mark}-{index + 1}"
        while bar_id in used_ids:
            bar_id += "-link"
        used_ids.add(bar_id)
        seeds.append(
            BarPathSeed(
                bar_id,
                mark,
                BarPathRole.TRANSVERSE_LINK,
                1,
                diameter,
                member.link_fy_nmm2,
                tuple(
                    PathNode(
                        str(i),
                        PathPoint(station + offset, x, y),
                        radius if 0 < i < 6 else None,
                        (
                            BendKind.HOOK
                            if i in (1, 5)
                            else BendKind.STANDARD_BEND if 0 < i < 6 else None
                        ),
                    )
                    for i, (offset, x, y) in enumerate(vertices)
                ),
            )
        )
    paths = BarPathRequest(
        WORKFLOW,
        member.source_reference,
        WORKFLOW,
        member.member_id,
        "both-spans",
        source_hash,
        member.reinforcement_revision,
        MemberLocalCoordinateSystem(
            "beam-local",
            "member_station_x",
            "section_x_from_left",
            "section_y_from_top",
        ),
        left.left_face_mm,
        right.right_face_mm,
        member.width_mm,
        member.depth_mm,
        tuple(seeds),
        (request.stock_length_mm,),
    )
    cage = LinkCage(
        mark, diameter, x1, x2, y1, y2, detail.internal_bend_radius_mm, True
    )
    link = TransverseLink(
        mark, diameter, 2, 2, spacing, member.link_fy_nmm2, True, x2 - x1, y2 - y1
    )
    arrangement = ReinforcementArrangementCheckRequest(
        WORKFLOW,
        member.member_id,
        "both-spans",
        member.reinforcement_revision,
        member.width_mm,
        member.depth_mm,
        member.clear_cover_mm,
        member.aggregate_size_mm,
        bars,
        (cage,),
        (ReinforcementRole.TOP_LONGITUDINAL, ReinforcementRole.BOTTOM_LONGITUDINAL),
        1e-6,
    )
    return paths, ClosedLinkDetailRequest(
        paths, cage, link, arrangement, left.right_face_mm, right.left_face_mm
    )


def _schedule(
    request: BeamContinuousDetailingInputV1,
    paths: OperationResult,
    detail: ClosedLinkDetailRequest,
    splice: SpliceRecord | None,
) -> OperationResult:
    data = paths.output_as("reinforcement_schedule", BarPathOutput)
    binding = result_binding(paths, "reinforcement_schedule")
    link = request.link_detail
    assert link is not None
    return create_bbs(
        BbsRequest(
            WORKFLOW,
            data.project_basis_id,
            data.member_id,
            data.detail_revision_id,
            binding.result_id,
            binding.output_payload_id,
            data,
            ShapeConvention("resolved-centreline", "v1"),
            CuttingStockPolicy(
                "declared-stock", "v1", (request.stock_length_mm,), 3, 500
            ),
            7850,
            splice_records=(splice,) if splice else (),
            link_zones=(
                LinkPlacementZone(
                    "both-spans",
                    detail.link.link_id,
                    link.first_station_mm,
                    link.last_station_mm,
                    detail.link.spacing_mm,
                    True,
                    True,
                ),
            ),
        )
    )


def _check_bottom_cutoff(
    request: BeamContinuousDetailingInputV1,
    checked: BeamContinuousCheckResultV1,
) -> tuple[float | None, dict[str, Any], list[StructuralIssueV1], EngineeringStatus]:
    member, cutoff = request.member, request.cutoff
    assert cutoff is not None
    stations = {station.station_id: station for station in member.stations}
    theoretical = stations.get(cutoff.theoretical_station_id)
    end = stations.get(cutoff.termination_station_id)
    bar = next((bar for bar in member.bars if bar.bar_id == cutoff.bar_id), None)
    extent = member.straight_bars
    layered = isinstance(member, BeamLayeredContinuousCheckRequestV1)
    left, middle, _ = member.supports
    if not (
        extent
        and theoretical
        and end
        and bar
        and bar.face == "bottom"
        and (not isinstance(bar, BeamSectionBarV1) or bar.layer == 1)
        and theoretical.side == end.side == "CONTINUOUS"
        and left.right_face_mm < theoretical.x_mm < end.x_mm < middle.left_face_mm
    ):
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_BASIS_HELD",
            "cutoff",
            "Identify an outer-layer bottom bar and two ordered continuous stations in the first clear span.",
        )
        return None, {}, [issue], EngineeringStatus.HOLD

    expected = {
        (combo.combination_id, station.station_id)
        for combo in member.combinations
        if combo.kind == "ULS"
        for station in (theoretical, end)
    }
    actual = {
        (row.action.combination_id, row.station.station_id) for row in checked.rows
    }
    missing = sorted(expected - actual)
    if missing:
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_ACTIONS_HELD",
            "cutoff",
            "Supply each declared ULS combination at both cutoff stations.",
        )
        return None, {"missing_cutoff_rows": missing}, [issue], EngineeringStatus.HOLD

    bars = tuple(item for item in _bar_positions(member) if item.bar_id != bar.bar_id)
    if sum(item.face == Face.BOTTOM and item.layer == 1 for item in bars) < 2:
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_BASIS_HELD",
            "cutoff",
            "Keep at least two outer-layer bottom bars continuous through both spans.",
        )
        return None, {}, [issue], EngineeringStatus.HOLD

    geometry, flexure, shear = _sections(member, bars)
    section_states = {
        result.engineering for result in (geometry, *flexure.values(), *shear.values())
    }
    if section_states != {EngineeringState.PASS}:
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_SECTION_UNAVAILABLE",
            "cutoff",
            "A passing reduced section check is required for the remaining bars and links.",
        )
        status = (
            EngineeringStatus.FAIL
            if EngineeringState.FAIL in section_states
            else EngineeringStatus.HOLD
        )
        return None, {}, [issue], status

    faces = _support_faces(member)
    web_capacity = (
        _positive_support_web_capacity(member, bars)
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else None
    )
    reduced_rows = tuple(
        _check_row(
            member,
            bars,
            row.action,
            row.station,
            row.kind,
            row.diagnostic_only,
            faces.get(row.station.x_mm),
            flexure,
            shear,
            web_capacity,
        )
        for row in checked.rows
        if row.kind == "ULS" and row.station.x_mm >= theoretical.x_mm
    )
    failed, held = _row_issues(reduced_rows, faces, layered=layered)
    bottom = flexure[Face.BOTTOM].outputs
    full_bottom = checked.flexural_sections[Face.BOTTOM].outputs
    d = max(
        float(full_bottom["effective_depth_mm"]), float(bottom["effective_depth_mm"])
    )
    continuing_area = float(bottom["tension_steel_area_mm2"])
    if continuing_area + 1e-9 < float(full_bottom["tension_steel_area_mm2"]) / 4:
        failed.append(
            StructuralIssueV1(
                "BEAM.CUTOFF_CONTINUITY_FAIL",
                "cutoff",
                "At least one quarter of the positive reinforcement must continue into the supports.",
            )
        )
    capacity_kn = float(shear[Face.BOTTOM].outputs["provided_capacity_kn"])
    # Use the weaker of both reduced shear faces at each physical termination.
    termination_limit = (
        2
        / 3
        * min(
            float(result.outputs["provided_capacity_kn"]) for result in shear.values()
        )
    )
    cutoff_rows = [
        row for row in reduced_rows if row.station.station_id == end.station_id
    ]
    shear_rows = [
        {
            "row_id": row.action.row_id,
            "shear_kn": row.action.vu_kn,
            "passes_two_thirds": abs(row.action.vu_kn) <= termination_limit + 1e-9,
        }
        for row in cutoff_rows
    ]
    if any(not row["passes_two_thirds"] for row in shear_rows):
        failed.append(
            StructuralIssueV1(
                "BEAM.CUTOFF_SHEAR_FAIL",
                "cutoff",
                "The termination shear exceeds two-thirds of the permitted reduced-section resistance.",
            )
        )
    extension = end.x_mm - theoretical.x_mm
    required_extension = max(d, 12 * bar.diameter_mm)
    anchor = check_anchorage(
        AnchorageCheckRequest(
            WORKFLOW,
            member.member_id,
            member.reinforcement_revision,
            (
                AnchoragePath(
                    bar.bar_id,
                    theoretical.station_id,
                    AnchorageLocation.DISCONTINUITY,
                    AnchorageDirection.INCREASING_X,
                    extent.start_mm,
                    end.x_mm,
                    theoretical.x_mm,
                    None,
                    None,
                    None,
                    (),
                    None,
                    DevelopmentLengthRequest(
                        WORKFLOW,
                        bar.diameter_mm,
                        0.87 * member.fy_nmm2,
                        member.fy_nmm2,
                        member.fck_nmm2,
                        BarSurface.DEFORMED,
                        StressState.TENSION,
                    ),
                ),
            ),
        )
    )
    if (
        extension + 1e-9 < required_extension
        or anchor.engineering is EngineeringState.FAIL
    ):
        failed.append(
            StructuralIssueV1(
                "BEAM.CUTOFF_EXTENSION_FAIL",
                "cutoff",
                "The actual straight extension fails the cutoff length or development check.",
            )
        )
    elif anchor.engineering is not EngineeringState.PASS:
        held.append(
            StructuralIssueV1(
                "BEAM.CUTOFF_ANCHORAGE_HELD",
                "cutoff",
                "The cutoff needs a current straight development check.",
            )
        )
    return (
        end.x_mm,
        {
            "bar_id": bar.bar_id,
            "theoretical_station_mm": theoretical.x_mm,
            "termination_station_mm": end.x_mm,
            "actual_extension_mm": extension,
            "required_extension_mm": required_extension,
            "continuing_bottom_mm2": continuing_area,
            "continuing_bar_ids": [item.bar_id for item in bars],
            "continuing_shear_capacity_kn": capacity_kn,
            "reduced_moment_knm": {
                face.value: flexure[face].outputs["capacity_knm"] for face in Face
            },
            "reduced_shear_kn": {
                face.value: shear[face].outputs["provided_capacity_kn"] for face in Face
            },
            "termination_shear_limit_kn": termination_limit,
            "termination_rows": shear_rows,
            "reduced_section_rows": [row.to_dict() for row in reduced_rows],
            "anchorage": anchor.to_dict(),
        },
        failed + held,
        (
            EngineeringStatus.FAIL
            if failed
            else EngineeringStatus.HOLD if held else EngineeringStatus.PASS
        ),
    )


def _check_bottom_lap(
    request: BeamContinuousDetailingInputV1,
    checked: BeamContinuousCheckResultV1,
) -> tuple[
    tuple[float, float] | None,
    dict[str, Any],
    list[StructuralIssueV1],
    EngineeringStatus,
]:
    member, lap = request.member, request.lap
    assert lap is not None
    layered = isinstance(member, BeamLayeredContinuousCheckRequestV1)
    stations = {item.station_id: item for item in member.stations}
    start = stations.get(lap.start_station_id)
    middle = stations.get(lap.middle_station_id)
    end = stations.get(lap.end_station_id)
    left, support, _ = member.supports
    extent = member.straight_bars
    bar = next((item for item in member.bars if item.bar_id == lap.bar_id), None)
    if not (
        extent
        and bar
        and bar.face == "bottom"
        and (not isinstance(bar, BeamSectionBarV1) or bar.layer == 1)
        and bar.diameter_mm <= 32
        and lap.partner_bar_id not in {item.bar_id for item in member.bars}
        and start
        and middle
        and end
        and start.side == middle.side == end.side == "CONTINUOUS"
        and left.right_face_mm
        < start.x_mm
        < middle.x_mm
        < end.x_mm
        < support.left_face_mm
        and lap.partner_x_from_left_mm < member.width_mm
    ):
        issue = StructuralIssueV1(
            "BEAM.LAP_BASIS_HELD",
            "lap",
            "Identify an outer-layer bottom bar up to Ø32, a distinct partner and three ordered stations in the first clear span.",
        )
        return None, {}, [issue], EngineeringStatus.HOLD

    combos = {
        combo.combination_id for combo in member.combinations if combo.kind == "ULS"
    }
    lap_ids = {start.station_id, middle.station_id, end.station_id}
    inventory = {
        (row.action.combination_id, row.station.station_id) for row in checked.rows
    }
    missing = sorted({(cid, sid) for cid in combos for sid in lap_ids} - inventory)
    if missing:
        issue = StructuralIssueV1(
            "BEAM.LAP_ACTIONS_HELD",
            "lap",
            "Supply every declared ULS combination at the start, interior and end of the overlap.",
        )
        return None, {"missing_lap_rows": missing}, [issue], EngineeringStatus.HOLD

    positions = _bar_positions(member)
    splice_rows = [
        row
        for row in checked.rows
        if row.kind == "ULS" and start.x_mm <= row.station.x_mm <= end.x_mm
    ]
    if layered:
        diameter = bar.diameter_mm
        cover = (
            min(
                bar.x_from_left_mm,
                member.width_mm - bar.x_from_left_mm,
                lap.partner_x_from_left_mm,
                member.width_mm - lap.partner_x_from_left_mm,
                bar.y_from_top_mm,
                member.depth_mm - bar.y_from_top_mm,
            )
            - diameter / 2
        )
        if cover < 2 * diameter or any(row.action.mu_knm <= 0 for row in splice_rows):
            issue = StructuralIssueV1(
                "BEAM.LAP_TENSION_BASIS_HELD",
                "lap",
                "The layered lap requires sagging in every supplied overlap row and clear concrete cover of at least two bar diameters at both pieces.",
            )
            return None, {}, [issue], EngineeringStatus.HOLD

        # The lapped outer bar changes axis. Every inner bar must stay aligned
        # over an uninterrupted outer bar before, through and after the lap.
        outer_axes = [
            item.x_from_left_mm
            for item in positions
            if item.face == Face.BOTTOM
            and item.layer == 1
            and item.bar_id != bar.bar_id
        ]
        unaligned = [
            item.bar_id
            for item in positions
            if item.face == Face.BOTTOM
            and item.layer > 1
            and not any(abs(item.x_from_left_mm - axis) <= 1e-6 for axis in outer_axes)
        ]
        if unaligned:
            issue = StructuralIssueV1(
                "BEAM.LAP_LAYER_ALIGNMENT_FAIL",
                "lap",
                "Inner bottom bars must align with uninterrupted outer bars: "
                + ", ".join(unaligned)
                + ".",
            )
            return (
                None,
                {"unaligned_inner_bar_ids": unaligned},
                [issue],
                EngineeringStatus.FAIL,
            )

    partner_positions = tuple(
        (
            replace(
                item,
                bar_id=lap.partner_bar_id,
                x_from_left_mm=lap.partner_x_from_left_mm,
            )
            if item.bar_id == lap.bar_id
            else item
        )
        for item in positions
    )
    geometry, flexure, shear = _sections(member, partner_positions)
    if geometry.engineering is not EngineeringState.PASS:
        issue = StructuralIssueV1(
            "BEAM.LAP_PARTNER_GEOMETRY",
            "lap",
            "The downstream bar layout fails geometry, spacing or cover.",
        )
        status = (
            EngineeringStatus.FAIL
            if geometry.engineering is EngineeringState.FAIL
            else EngineeringStatus.HOLD
        )
        return None, {"partner_geometry": geometry.to_dict()}, [issue], status
    faces = _support_faces(member)
    web_capacity = (
        _positive_support_web_capacity(member, partner_positions)
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else None
    )
    partner_rows = tuple(
        _check_row(
            member,
            partner_positions,
            row.action,
            row.station,
            row.kind,
            row.diagnostic_only,
            faces.get(row.station.x_mm),
            flexure,
            shear,
            web_capacity,
        )
        for row in checked.rows
        if row.kind == "ULS" and row.station.x_mm >= start.x_mm
    )
    failed, held = _row_issues(partner_rows, faces, layered=layered)
    full_bottom = checked.flexural_sections[Face.BOTTOM].outputs
    d = float(full_bottom["effective_depth_mm"])
    demands = []
    stress_rows = []
    for row in splice_rows:
        face = Face.TOP if row.action.mu_knm < 0 else Face.BOTTOM
        capacity = min(
            float(checked.flexural_sections[face].outputs["capacity_knm"]),
            float(flexure[face].outputs["capacity_knm"]),
        )
        stress_rows.append(
            {
                "row_id": row.action.row_id,
                "moment_knm": row.action.mu_knm,
                "shear_kn": row.action.vu_kn,
                "half_capacity_knm": 0.5 * capacity,
            }
        )
        if abs(row.action.mu_knm) > 0.5 * capacity + 1e-9:
            failed.append(
                StructuralIssueV1(
                    "BEAM.LAP_MOMENT_LIMIT",
                    f"actions.{row.action.row_id}",
                    "A supplied splice-zone moment exceeds half the signed section resistance.",
                )
            )
        demands.append(
            StationSteelDemand(
                row.action.row_id,
                row.station.x_mm,
                ReinforcementRole.BOTTOM_LONGITUDINAL,
                float(full_bottom["minimum_tension_steel_area_mm2"]),
                abs(row.action.vu_kn) * 1000,
                float(shear[Face.BOTTOM].outputs["provided_capacity_kn"]) * 1000,
                row.action.row_id,
            )
        )
    original = LongitudinalBarPath(
        bar.bar_id,
        "lap-I",
        ReinforcementRole.BOTTOM_LONGITUDINAL,
        bar.diameter_mm,
        bar.layer if isinstance(bar, BeamSectionBarV1) else 1,
        bar.x_from_left_mm,
        bar.y_from_top_mm,
        extent.start_mm,
        end.x_mm,
        0.87 * member.fy_nmm2,
    )
    partner = replace(
        original,
        bar_id=lap.partner_bar_id,
        bar_mark="lap-J",
        x_from_left_mm=lap.partner_x_from_left_mm,
        start_station_mm=start.x_mm,
        end_station_mm=extent.end_mm,
    )
    checked_lap = check_laps_and_curtailment(
        LapCurtailmentCheckRequest(
            WORKFLOW,
            member.member_id,
            "first-span",
            member.analysis_revision,
            member.reinforcement_revision,
            left.left_face_mm,
            support.right_face_mm,
            d,
            member.fck_nmm2,
            member.fy_nmm2,
            BarSurface.DEFORMED,
            (original, partner),
            tuple(demands),
            (
                SpliceDetail(
                    "bottom-lap",
                    SpliceKind.LAP,
                    (original.bar_id, partner.bar_id),
                    start.x_mm,
                    end.x_mm,
                    StressState.TENSION,
                    False,
                    100 / sum(item.face == "bottom" for item in member.bars),
                    "single-group",
                ),
            ),
            (),
        )
    )
    diagnostic_issues = [
        StructuralIssueV1(
            issue.code,
            issue.field_or_location or "lap",
            issue.message,
        )
        for issue in checked_lap.diagnostics
    ]
    if checked_lap.engineering is EngineeringState.FAIL:
        failed.extend(diagnostic_issues)
    elif checked_lap.engineering is not EngineeringState.PASS:
        held.extend(diagnostic_issues)
    status = (
        EngineeringStatus.FAIL
        if failed
        else EngineeringStatus.HOLD if held else EngineeringStatus.PASS
    )
    return (
        (start.x_mm, end.x_mm),
        {
            "bar_id": bar.bar_id,
            "partner_bar_id": lap.partner_bar_id,
            "overlap_mm": end.x_mm - start.x_mm,
            "start_station_mm": start.x_mm,
            "middle_station_mm": middle.x_mm,
            "end_station_mm": end.x_mm,
            "lap_result": checked_lap.to_dict(),
            "stress_rows": stress_rows,
            "partner_rows": [row.to_dict() for row in partner_rows],
            **(
                {"web_only_anchor_moment_knm": web_capacity}
                if isinstance(member, BeamLayeredContinuousCheckRequestV1)
                and member.flange is not None
                and member.flange.kind == "t_beam"
                else {}
            ),
        },
        failed + held,
        status,
    )


def check_continuous_detailing(
    request: BeamContinuousDetailingInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Check and schedule continuous straight bars and ordinary closed links.

    Parameters
    ----------
    request : BeamContinuousDetailingInputV1
        Physical two-span member, supplied actions and link detail.

    Returns
    -------
    CanonicalFamilyResultV1
        Checked strength, anchorage, cage, actual paths and eligible schedule.

    Raises
    ------
    InputContractError
        The request is not a validated two-span detailing input.

    Examples
    --------
    >>> callable(check_continuous_detailing)
    True

    Limitations
    -----------
    Straight longitudinal bars and a uniform ordinary web link mark. One
    first-span outer-layer bottom cutoff is supported. Rectangular and
    symmetric T sections admit one separated straight outer-bottom tension lap.

    Provenance
    ----------
    Uses the checked supplied station actions, physical path and BBS owners.
    """
    require_request_type(request, BeamContinuousDetailingInputV1)
    checked = check_continuous_beam(request.member)
    identity = checked.result_envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    data: dict[str, Any] = {"strength": checked.to_dict(), "paths": None, "bbs": None}
    issues = []
    status = EngineeringStatus(checked.ultimate_status)
    cutoff_end = None
    lap_bounds = None
    source_hash = identity.input_hash
    layered = isinstance(request.member, BeamLayeredContinuousCheckRequestV1)
    flange = (
        request.member.flange
        if isinstance(request.member, BeamLayeredContinuousCheckRequestV1)
        else None
    )
    if (
        request.lap
        and flange is not None
        and (
            flange.kind != "t_beam"
            or not math.isclose(
                flange.left_overhang_mm,
                flange.right_overhang_mm,
                rel_tol=0,
                abs_tol=1e-6,
            )
        )
    ):
        issues.append(
            StructuralIssueV1(
                "BEAM.LAYERED_BAR_DETAIL_HELD",
                "lap",
                "The layered lap profile covers rectangles and symmetric T web cages.",
            )
        )
        if status is EngineeringStatus.PASS:
            status = EngineeringStatus.HOLD
    elif status is EngineeringStatus.PASS and request.cutoff and request.lap:
        status = EngineeringStatus.HOLD
        issues.append(
            StructuralIssueV1(
                "BEAM.COMBINED_BAR_DETAIL_HELD",
                "cutoff,lap",
                "The cutoff and separated lap have individually checked profiles.",
            )
        )
    elif status is EngineeringStatus.PASS and request.cutoff is not None:
        cutoff_end, cutoff, cutoff_issues, status = _check_bottom_cutoff(
            request, checked
        )
        data["cutoff"] = cutoff
        issues.extend(cutoff_issues)
    elif status is EngineeringStatus.PASS and request.lap is not None:
        lap_bounds, lap, lap_issues, status = _check_bottom_lap(request, checked)
        data["lap"] = lap
        issues.extend(lap_issues)
    if request.cutoff or request.lap:
        source_hash = semantic_hash(
            "beam_detailing_source",
            {
                "strength": identity.input_hash,
                "cutoff": (
                    request.cutoff.model_dump(mode="json") if request.cutoff else None
                ),
                "lap": request.lap.model_dump(mode="json") if request.lap else None,
                "link": (
                    request.link_detail.model_dump(mode="json")
                    if request.link_detail
                    else None
                ),
            },
        )
    if status is EngineeringStatus.PASS:
        inputs = _physical_paths(request, source_hash, cutoff_end, lap_bounds)
        if inputs is None:
            status = EngineeringStatus.HOLD
            issues.append(
                StructuralIssueV1(
                    "BEAM.DETAIL_LINK_BASIS_HELD",
                    "link_detail",
                    "Supply a current link shape and full member placement grid.",
                )
            )
        else:
            paths_request, link_request = inputs
            fit = check_reinforcement_arrangement(link_request.arrangement)
            paths = resolve_bar_paths(paths_request)
            links = check_closed_link_detail(link_request)
            data.update(
                arrangement=fit.to_dict(),
                paths=paths.to_dict(),
                link_check=links.to_dict(),
            )
            for leaf in (fit, paths, links):
                if (
                    leaf.execution is ExecutionState.COMPLETED
                    and leaf.engineering is EngineeringState.FAIL
                ):
                    status = EngineeringStatus.FAIL
                elif (
                    status is EngineeringStatus.PASS
                    and leaf.engineering is not EngineeringState.PASS
                ):
                    status = EngineeringStatus.HOLD
                issues.extend(
                    StructuralIssueV1(
                        item.code, item.field_or_location or "detail", item.message
                    )
                    for item in leaf.diagnostics
                )
            if status is EngineeringStatus.PASS:
                splice = None
                if lap_bounds is not None and request.lap is not None:
                    splice = SpliceRecord(
                        "bottom-lap",
                        ScheduleSpliceKind.LAP,
                        sum(lap_bounds) / 2,
                        data["lap"]["lap_result"]["result_id"],
                    )
                schedule = _schedule(request, paths, link_request, splice)
                if schedule.engineering is EngineeringState.PASS:
                    data["bbs"] = schedule.to_dict()
                else:
                    status = EngineeringStatus.HOLD
                    issues.extend(
                        StructuralIssueV1(
                            item.code, item.field_or_location or "bbs", item.message
                        )
                        for item in schedule.diagnostics
                    )
    if checked.ultimate_status != "PASS":
        issues.extend(checked.result_envelope.issues)
    result = canonical_family_result(
        request,
        data,
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Only the supplied strength and anchorage rows and the declared physical layout are checked.",
            (
                "Prismatic web cage with straight layers, one optional outer-layer bottom cutoff and one uniform two-hook web link. Rectangular and symmetric T cages admit one separated straight outer-bottom tension lap. Slab reinforcement and equilibrium torsion need separate evidence."
                if layered
                else "Ordinary straight bars, one optional first-span bottom cutoff or separated bottom lap, and one uniform two-hook link mark."
            ),
            "Unreported demand between stations, other splices, member serviceability, support connections and fabrication approval require separate evidence.",
        ),
        provenance=(
            "IS 456 ordinary anchorage and reinforcement geometry with actual resolved cut paths.",
        ),
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=tuple(issues),
            freshness_status=checked.result_envelope.freshness_status,
        ),
    )


def _required_result(result: CanonicalFamilyResultV1[dict[str, Any]]) -> None:
    if (
        not isinstance(result, CanonicalFamilyResultV1)
        or result.workflow_id != WORKFLOW
    ):
        raise TypeError("result must be a checked continuous beam detailing result")


def _matches_current(
    result: CanonicalFamilyResultV1[dict[str, Any]],
    current: BeamContinuousDetailingInputV1 | None,
) -> bool:
    if current is None:
        return result.envelope.freshness_status is FreshnessStatus.CURRENT
    require_request_type(current, BeamContinuousDetailingInputV1)
    identity = result.envelope.result_identity
    return (
        result.envelope.freshness_status is FreshnessStatus.CURRENT
        and identity is not None
        and identity.input_hash == _input_hash(current)
    )


def recheck_continuous_bar_edit(
    current: BeamContinuousDetailingInputV1,
    previous: CanonicalFamilyResultV1[dict[str, Any]],
    edit: BeamBarEditV1,
    *,
    analysis_basis: Literal[
        "fixed_supplied_actions", "reinforcement_dependent_stiffness"
    ],
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Apply and check one physical bar edit against the current result.

    Parameters
    ----------
    current : BeamContinuousDetailingInputV1
        Current member and source action revisions.
    previous : CanonicalFamilyResultV1
        Previously checked detailing result on which the edit is based.
    edit : BeamBarEditV1
        Identified bar diameter and optional lateral centre, in mm.
    analysis_basis : str
        Whether the supplied actions depend on the reinforcement stiffness.

    Returns
    -------
    CanonicalFamilyResultV1
        Result bound to the edited physical member, or HOLD on a stale basis.

    Raises
    ------
    InputContractError
        The edit, analysis basis or resulting input is invalid.
    TypeError
        The previous result belongs to another workflow.

    Examples
    --------
    >>> callable(recheck_continuous_bar_edit)
    True

    Limitations
    -----------
    One straight bar in the checked two-span cage.

    Provenance
    ----------
    Replays the same strength, placement, path and schedule owners on the
    edited bar geometry.
    """
    require_request_type(current, BeamContinuousDetailingInputV1)
    require_request_type(edit, BeamBarEditV1)
    _required_result(previous)
    bar = next((bar for bar in current.member.bars if bar.bar_id == edit.bar_id), None)
    if bar is None or analysis_basis not in (
        "fixed_supplied_actions",
        "reinforcement_dependent_stiffness",
    ):
        raise InputContractError(
            (
                InputIssueV1(
                    code="INPUT_CONTRACT_INVALID",
                    path="edit",
                    message="Identify an existing bar and declare the analysis stiffness basis.",
                ),
            )
        )
    edited_bar = bar.model_copy(
        update={
            "diameter_mm": edit.diameter_mm,
            "x_from_left_mm": (
                edit.x_from_left_mm
                if edit.x_from_left_mm is not None
                else bar.x_from_left_mm
            ),
        }
    )
    new_bars = tuple(
        edited_bar if item.bar_id == edit.bar_id else item
        for item in current.member.bars
    )
    revision = (
        "edit-"
        + semantic_hash(
            "beam_bars",
            {
                "parent": current.member.reinforcement_revision,
                "bars": tuple(item.model_dump(mode="json") for item in new_bars),
            },
        ).rsplit(":", 1)[-1]
    )
    proposed = current.model_dump(mode="python")
    proposed["member"].update(
        bars=tuple(item.model_dump(mode="python") for item in new_bars),
        reinforcement_revision=revision,
    )
    request = model_validate_or_error(BeamContinuousDetailingInputV1, proposed)
    source = previous.envelope.result_identity
    current_hash = _input_hash(current)
    stale = not _matches_current(previous, current)
    result: CanonicalFamilyResultV1[dict[str, Any]]
    if stale or analysis_basis == "reinforcement_dependent_stiffness":
        result = canonical_family_result(
            request,
            {
                "strength": {
                    "ultimate_status": "HOLD",
                    "serviceability_status": "HOLD",
                    "governing_rows": {},
                },
                "paths": None,
                "bbs": None,
            },
            workflow_id=WORKFLOW,
            engineering_status=EngineeringStatus.HOLD,
        )
        issue = StructuralIssueV1(
            (
                "BEAM.EDIT_STALE_RESULT"
                if stale
                else "BEAM.EDIT_ANALYSIS_REFRESH_REQUIRED"
            ),
            "member",
            "The edit requires a current base result and actions compatible with the edited stiffness.",
        )
        result = replace(
            result,
            envelope=replace(
                result.envelope,
                issues=(issue,),
                freshness_status=FreshnessStatus.STALE,
            ),
        )
    else:
        result = check_continuous_detailing(request)
    return replace(
        result,
        calculation={
            **result.calculation,
            "bar_edit": {
                "bar_id": edit.bar_id,
                "previous_diameter_mm": bar.diameter_mm,
                "edited_diameter_mm": edited_bar.diameter_mm,
                "base_input_hash": source.input_hash if source else None,
                "current_input_hash": current_hash,
                "reinforcement_revision": revision,
                "analysis_basis": analysis_basis,
            },
        },
    )


def render_continuous_detailing_svg(
    result: CanonicalFamilyResultV1[dict[str, Any]],
    *,
    current: BeamContinuousDetailingInputV1 | None = None,
) -> str | None:
    """Project checked bars and link levels onto a review drawing.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked physical member detail.
    current : BeamContinuousDetailingInputV1 or None
        Current input required by a caller exporting from an editable session.

    Returns
    -------
    str or None
        Identified SVG drawing when the schedule is eligible.

    Raises
    ------
    TypeError
        The result belongs to a different workflow.

    Examples
    --------
    >>> callable(render_continuous_detailing_svg)
    True

    Limitations
    -----------
    The drawing shows the resolved elevation and, for the layered profile,
    the physical web cage and optional flange cross-section.

    Provenance
    ----------
    Retains the same input and path result identities as the schedule.
    """
    _required_result(result)
    data = result.calculation
    if data["bbs"] is None or not _matches_current(result, current):
        return None
    request = result.request
    assert isinstance(request, BeamContinuousDetailingInputV1)
    member = request.member
    geometry = data["paths"]["outputs"]["reinforcement_schedule"]
    left, _, right = member.supports
    start, end = left.left_face_mm, right.right_face_mm
    depth = member.depth_mm
    support_lines = "".join(
        f'<rect x="{item.left_face_mm:g}" y="{depth:g}" width="{item.width_mm:g}" height="100" fill="#cbd5e1"/>'
        for item in member.supports
    )
    cutoff = (
        data.get("cutoff", {})
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else {}
    )
    lap = (
        data.get("lap", {})
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else {}
    )
    lap_colors = (
        {lap["bar_id"]: "#92400e", lap["partner_bar_id"]: "#0f766e"}
        if "web_only_anchor_moment_knm" in lap
        else {}
    )
    lap_lines = []
    bars = []
    termination = ""
    for item in geometry["paths"]:
        path_id = html.escape(item["bar_id"], quote=True)
        segments = item["segments"]
        x1 = segments[0]["start"]["station_x_mm"]
        if item["role"] == "transverse_link":
            x2, y1, y2 = x1, member.clear_cover_mm, depth - member.clear_cover_mm
            color = "#64748b"
        else:
            x2 = segments[-1]["end"]["station_x_mm"]
            y1 = y2 = segments[0]["start"]["section_y_from_top_mm"]
            color = "#1e40af"
        line = (
            f'<line data-bar-id="{path_id}" data-layer="{item["layer"]}" '
            f'x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
        )
        if item["bar_id"] == cutoff.get("bar_id"):
            # Bars in the same layer overlap in elevation. Draw the cut bar last.
            termination = (
                line + 'stroke="#b45309" stroke-width="14"/>'
                f'<path d="M{x2:g} -35 V{y2:g}" stroke="#b45309" stroke-width="7" stroke-dasharray="24 15"/>'
                f'<circle cx="{x2:g}" cy="{y2:g}" r="23" fill="#b45309"/>'
                f'<text x="{x2:g}" y="-68" text-anchor="middle" font-size="112" '
                f'fill="#92400e">{path_id} ends at {x2:g} mm</text>'
            )
        elif item["bar_id"] in lap_colors:
            color = lap_colors[item["bar_id"]]
            first = item["bar_id"] == lap["bar_id"]
            dash = "" if first else ' stroke-dasharray="42 22"'
            lap_lines.append(
                line + f'stroke="{color}" stroke-width="14"{dash}/>'
                f'<circle cx="{x2 if first else x1:g}" cy="{y1:g}" r="18" fill="{color}"/>'
            )
        else:
            bars.append(line + f'stroke="{color}" stroke-width="8"/>')
    identity = result.envelope.result_identity
    lap_band = ""
    if lap:
        lap_start, lap_end = lap["start_station_mm"], lap["end_station_mm"]
        lap_band = (
            f'<rect data-view="lap-overlap" x="{lap_start:g}" y="0" width="{lap_end - lap_start:g}" '
            f'height="{depth:g}" fill="#fde68a" opacity="0.6"/>'
            f'<text x="{(lap_start + lap_end) / 2:g}" y="-68" text-anchor="middle" font-size="112" '
            f'fill="#92400e">Overlap {lap_start:g} to {lap_end:g} mm</text>'
        )
    top = 180 if cutoff or lap else 40
    elevation_view = (
        f"{start - 40:g} {-top:g} {end - start + 80:g} {depth + 140 + top:g}"
    )
    elevation = (
        f'<rect x="{start:g}" width="{end - start:g}" height="{depth:g}" fill="#f1f5f9" stroke="#0f172a"/>'
        + support_lines
        + lap_band
        + "".join(bars)
        + termination
        + "".join(lap_lines)
    )
    drawing_label = "elevation"
    if isinstance(member, BeamLayeredContinuousCheckRequestV1):
        drawing_label = "drawing"
        drawing_view = "0 0 1200 650"
        lap_legend = (
            '<text x="334" y="28" font-size="17" fill="#92400e">Lap-I · original</text>'
            '<text x="500" y="28" font-size="17" fill="#0f766e">Lap-J · partner</text>'
            if lap_colors
            else ""
        )
        panels = (
            '<text x="18" y="28" font-size="22">Member elevation</text>'
            f"{lap_legend}"
            f'<svg x="0" y="44" width="1200" height="230" viewBox="{elevation_view}">'
            f"{elevation}</svg>"
        )
        if cutoff:
            before, after = (
                cutoff["theoretical_station_mm"],
                cutoff["termination_station_mm"],
            )
            panels += _section_panel(
                member,
                request.link_detail,
                geometry["paths"],
                station_mm=before,
                panel_width=600,
                label=f"Section at {before:g} mm · before termination",
            )
            panels += _section_panel(
                member,
                request.link_detail,
                geometry["paths"],
                station_mm=after,
                panel_x=600,
                panel_width=600,
                label=f"Section just after {after:g} mm · continuing cage",
            )
        elif lap:
            views = (
                ((left.right_face_mm + lap["start_station_mm"]) / 2, "before lap"),
                (lap["middle_station_mm"], "lap overlap"),
                (lap["end_station_mm"], "after lap"),
            )
            for index, (station, label) in enumerate(views):
                panels += _section_panel(
                    member,
                    request.link_detail,
                    geometry["paths"],
                    station_mm=station,
                    panel_x=400 * index,
                    panel_width=400,
                    label=f"Section at {station:g} mm · {label}",
                    lap_colors=lap_colors,
                )
        else:
            panels += _section_panel(member, request.link_detail, geometry["paths"])
    else:
        drawing_view, panels = elevation_view, elevation
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{drawing_view}" role="img">
<title>{html.escape(member.member_id)} checked continuous beam {drawing_label}</title>
<desc>Input {identity.input_hash if identity else ""}. Path {data["paths"]["result_id"]}. Review drawing.</desc>
{panels}</svg>"""


def _section_panel(
    member: BeamLayeredContinuousCheckRequestV1,
    link: BeamOrdinaryLinkDetailV1 | None,
    paths: list[dict[str, Any]],
    *,
    station_mm: float | None = None,
    panel_x: int = 0,
    panel_width: int = 1200,
    label: str = "Physical cross-section · web cage",
    lap_colors: dict[str, str] | None = None,
) -> str:
    """Draw the web cage immediately to the right of the section station."""
    assert link is not None
    flange = member.flange
    width, depth = member.width_mm, member.depth_mm
    left = flange.left_overhang_mm if flange else 0.0
    right = flange.right_overhang_mm if flange else 0.0
    flange_depth = flange.thickness_mm if flange else 0.0
    flange_left = 0.0 - left
    if flange:
        outline = (
            f"M{flange_left:g} 0 H{width + right:g} V{flange_depth:g} H{width:g} "
            f"V{depth:g} H0 V{flange_depth:g} H{flange_left:g} Z"
        )
    else:
        outline = f"M0 0 H{width:g} V{depth:g} H0 Z"
    inset = member.clear_cover_mm + member.link_diameter_mm / 2
    radius = link.internal_bend_radius_mm + member.link_diameter_mm / 2
    circles = []
    for path in paths:
        if path["role"] == "transverse_link":
            continue
        segments = path["segments"]
        point = segments[0]["start"]
        if station_mm is not None and not (
            point["station_x_mm"] <= station_mm < segments[-1]["end"]["station_x_mm"]
        ):
            continue
        bar_id = html.escape(path["bar_id"], quote=True)
        mark = html.escape(path["bar_mark"])
        color = (lap_colors or {}).get(path["bar_id"], "#1e40af")
        circles.append(
            f'<circle data-bar-id="{bar_id}" data-layer="{path["layer"]}" '
            f'cx="{point["section_x_from_left_mm"]:g}" cy="{point["section_y_from_top_mm"]:g}" '
            f'r="{path["diameter_mm"] / 2:g}" fill="{color}"><title>{mark}</title></circle>'
        )
    station = f' data-station-mm="{station_mm:g}"' if station_mm is not None else ""
    return f"""<text x="{panel_x + 18}" y="302" font-size="22">{html.escape(label)}</text>
<svg data-view="section"{station} x="{panel_x}" y="318" width="{panel_width}" height="320"
 viewBox="{-left - 35:g} -35 {width + left + right + 70:g} {depth + 70:g}">
<path data-outline="concrete" d="{outline}" fill="#f1f5f9" stroke="#0f172a" stroke-width="3"/>
<rect data-outline="web-link" x="{inset:g}" y="{inset:g}" width="{width - 2 * inset:g}"
 height="{depth - 2 * inset:g}" rx="{radius:g}" fill="none" stroke="#64748b" stroke-width="{member.link_diameter_mm:g}"/>
{"".join(circles)}</svg>"""


def render_continuous_detailing_bbs_csv(
    result: CanonicalFamilyResultV1[dict[str, Any]],
    *,
    current: BeamContinuousDetailingInputV1 | None = None,
) -> str | None:
    """Serialize the checked BBS and preserve its input and path identities.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked physical member detail.
    current : BeamContinuousDetailingInputV1 or None
        Current input required by a caller exporting from an editable session.

    Returns
    -------
    str or None
        CSV for an eligible schedule, or None for FAIL or HOLD.

    Raises
    ------
    TypeError
        The result belongs to a different workflow.

    Examples
    --------
    >>> callable(render_continuous_detailing_bbs_csv)
    True

    Limitations
    -----------
    The schedule is a digital review output.

    Provenance
    ----------
    The checked WP07 schedule supplies every count, length and mass.
    """
    _required_result(result)
    bbs = result.calculation["bbs"]
    if bbs is None or not _matches_current(result, current):
        return None
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(
        (
            "member_id",
            "input_hash",
            "path_result_id",
            "bar_mark",
            "role",
            "diameter_mm",
            "quantity",
            "cut_mm",
            "total_mm",
            "mass_kg",
        )
    )
    identity = result.envelope.result_identity
    for row in bbs["outputs"]["bbs"]["rows"]:
        writer.writerow(
            (
                result.identity.member_id,
                identity.input_hash if identity else "",
                result.calculation["paths"]["result_id"],
                row["bar_mark"],
                row["role"],
                row["diameter_mm"],
                row["scheduled_bar_count"],
                row["fabrication_cut_length_each_mm"],
                row["scheduled_cut_length_mm"],
                row["theoretical_mass_kg"],
            )
        )
    return out.getvalue()


def render_continuous_detailing_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
    *,
    current: BeamContinuousDetailingInputV1 | None = None,
) -> str:
    """Render the checked continuous detail and schedule.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked two-span member detail.
    current : BeamContinuousDetailingInputV1 or None
        Current input required by a caller exporting from an editable session.

    Returns
    -------
    str
        A result-bound HTML report and eligible review elevation and schedule.

    Raises
    ------
    TypeError
        The result belongs to a different workflow.

    Examples
    --------
    >>> callable(render_continuous_detailing_html)
    True

    Limitations
    -----------
    The report renders the supplied result without recalculation.

    Provenance
    ----------
    Shows the same action, path and BBS identities as the JSON output.
    """
    _required_result(result)
    identity = result.envelope.result_identity
    current_match = _matches_current(result, current)
    svg = render_continuous_detailing_svg(result, current=current) or ""
    bbs = render_continuous_detailing_bbs_csv(result, current=current)
    strength = result.calculation["strength"]
    governance = "".join(
        f"<li>{html.escape(check)} · {html.escape(row)}</li>"
        for check, row in strength["governing_rows"].items()
    )
    report_bbs = (
        f"<pre>{html.escape(bbs)}</pre>" if bbs is not None else "<p>BBS held.</p>"
    )
    section_html = ""
    request = result.request
    cutoff = result.calculation.get("cutoff", {})
    lap = result.calculation.get("lap", {})
    if (
        current_match
        and isinstance(request, BeamContinuousDetailingInputV1)
        and isinstance(request.member, BeamLayeredContinuousCheckRequestV1)
    ):
        section_html = _layered_section_report(strength, cutoff, lap)
    cutoff_html = ""
    if "bar_id" in cutoff:
        rows = "".join(
            f"<li>{html.escape(row['row_id'])} · {row['shear_kn']:g} kN · "
            f"{'PASS' if row['passes_two_thirds'] else 'FAIL'}</li>"
            for row in cutoff["termination_rows"]
        )
        development = cutoff["anchorage"]["outputs"].get("checks", ())
        development_html = (
            f"<p>Required straight development "
            f"{development[0]['required_development_length_mm']:.3f} mm.</p>"
            if development
            else ""
        )
        cutoff_html = (
            f"<h2>Bottom bar cutoff</h2><p>{html.escape(cutoff['bar_id'])} ends at "
            f"{cutoff['termination_station_mm']:g} mm. Straight extension "
            f"{cutoff['actual_extension_mm']:g} mm. Continuing bottom steel "
            f"{cutoff['continuing_bottom_mm2']:.3f} mm².</p>"
            f"{development_html}"
            f"<p>Termination shear limit {cutoff['termination_shear_limit_kn']:.3f} kN.</p>"
            f"<ul>{rows}</ul>"
        )
        if isinstance(request, BeamContinuousDetailingInputV1) and isinstance(
            request.member, BeamLayeredContinuousCheckRequestV1
        ):
            cutoff_html += (
                f"<p>Analysis revision <code>{html.escape(request.member.analysis_revision)}</code>. "
                f"Reinforcement revision <code>{html.escape(request.member.reinforcement_revision)}</code>.</p>"
                + _cutoff_section_report(cutoff)
            )
    lap_html = ""
    if "lap_result" in lap:
        checks = lap["lap_result"]["outputs"].get("splice_checks", ())
        if checks:
            lap_html = (
                f"<h2>Separated bottom lap</h2><p>{html.escape(lap['bar_id'])} and "
                f"{html.escape(lap['partner_bar_id'])}. Overlap {lap['overlap_mm']:g} mm. "
                f"Required length {checks[0]['required_length_mm']:.3f} mm.</p>"
            )
            if isinstance(request, BeamContinuousDetailingInputV1) and isinstance(
                request.member, BeamLayeredContinuousCheckRequestV1
            ):
                lap_html += (
                    f"<p>Analysis revision <code>{html.escape(request.member.analysis_revision)}</code>. "
                    f"Reinforcement revision <code>{html.escape(request.member.reinforcement_revision)}</code>.</p>"
                    + _layered_lap_report(
                        lap, result.calculation.get("arrangement", {})
                    )
                )
    issues = "".join(f"<li>{html.escape(item.message)}</li>" for item in result.issues)
    limits = "".join(f"<li>{html.escape(item)}</li>" for item in result.limitations)
    status = result.engineering_status.value if current_match else "HOLD · stale result"
    if not current_match:
        strength = {"ultimate_status": "HOLD", "serviceability_status": "HOLD"}
        governance, cutoff_html, lap_html = "", "", ""
    bar_edit = result.calculation.get("bar_edit")
    edit_html = ""
    if bar_edit:
        edit_html = (
            f"<h2>Bar edit</h2><p>{html.escape(bar_edit['bar_id'])} diameter "
            f"{bar_edit['previous_diameter_mm']:g} → {bar_edit['edited_diameter_mm']:g} mm.</p>"
        )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Continuous beam detailing</title>
<h1>Continuous beam detailing · {html.escape(result.identity.member_id or "")}</h1>
<p>{status} · Qualified review required</p>
<p>Input identity <code>{identity.input_hash if identity else ""}</code></p>
<p>Supplied strength {strength["ultimate_status"]} · Serviceability {strength["serviceability_status"]}</p>
<h2>Governing baseline action rows</h2><ul>{governance}</ul>
{edit_html}{cutoff_html}{lap_html}{section_html}{svg}{report_bbs}<ul>{issues}{limits}</ul></html>"""


def _cutoff_section_report(cutoff: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><th>{html.escape(row['action']['row_id'])}</th>"
        f"<td>{row['station']['x_mm']:g}</td>"
        f"<td>{row['action']['mu_knm']:g}</td>"
        f"<td>{row['action']['vu_kn']:g}</td>"
        f"<td>{row['flexure_utilization']:.3f}</td>"
        f"<td>{row['shear_utilization']:.3f}</td>"
        f"<td>{row['section_status']}</td></tr>"
        for row in cutoff["reduced_section_rows"]
        if not row["diagnostic_only"]
    )
    return (
        "<h3>Continuing cage from the theoretical cutoff</h3>"
        f"<p>Sagging resistance {cutoff['reduced_moment_knm']['bottom']:.3f} kN·m. "
        f"Hogging resistance {cutoff['reduced_moment_knm']['top']:.3f} kN·m.</p>"
        "<table><thead><tr><th>Row ID</th><th>Station (mm)</th><th>Moment (kN·m)</th>"
        "<th>Shear (kN)</th><th>Flexure utilization</th><th>Shear utilization</th>"
        f"<th>Section check</th></tr></thead><tbody>{rows}</tbody></table>"
    )


def _layered_lap_report(lap: dict[str, Any], arrangement: dict[str, Any]) -> str:
    bars = {lap["bar_id"], lap["partner_bar_id"]}
    clearances = [
        pair
        for pair in arrangement.get("outputs", {}).get(
            "horizontal_clearance_checks", ()
        )
        if {pair["first_bar_id"], pair["second_bar_id"]} == bars
    ]
    spacing = "".join(
        f"<p>Clear distance between lap pieces {pair['actual_clear_mm']:g} mm. "
        f"Required {pair['required_clear_mm']:g} mm.</p>"
        for pair in clearances
    )
    stress_rows = lap["stress_rows"]
    rows = "".join(
        f"<tr><th>{html.escape(row['row_id'])}</th>"
        f"<td>{row['moment_knm']:g}</td><td>{row['shear_kn']:g}</td>"
        f"<td>{row['half_capacity_knm']:.3f}</td></tr>"
        for row in stress_rows
    )
    basis = ""
    if "web_only_anchor_moment_knm" in lap and stress_rows:
        governor = min(
            stress_rows,
            key=lambda row: (
                -abs(row["moment_knm"]) / row["half_capacity_knm"],
                row["row_id"],
            ),
        )
        basis = (
            f"<p>Governing lap moment {html.escape(governor['row_id'])} · "
            f"{governor['moment_knm']:.3f} kN·m against "
            f"{governor['half_capacity_knm']:.3f} kN·m.</p>"
            "<p>Each transfer layout credits one lap piece. Sagging uses the compression flange. "
            "Hogging and shear use the web.</p>"
        )
        web_capacity = lap["web_only_anchor_moment_knm"]
        if web_capacity is not None:
            basis += (
                f"<p>Web-only moment resistance for positive support anchorage "
                f"{web_capacity:.3f} kN·m.</p>"
            )
    return (
        f"<p>Overlap from {lap['start_station_mm']:g} to {lap['end_station_mm']:g} mm.</p>"
        f"{spacing}{basis}<h3>Concurrent ULS actions within the lap</h3>"
        "<table><thead><tr><th>Row ID</th><th>Moment (kN·m)</th>"
        "<th>Shear (kN)</th><th>Half section resistance (kN·m)</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _layered_section_report(
    strength: dict[str, Any], cutoff: dict[str, Any], lap: dict[str, Any]
) -> str:
    flexure = strength.get("flexural_sections", {})
    shear = strength.get("shear_sections", {})
    if not flexure or not shear:
        return ""
    rows = []
    for face, label in (("bottom", "Sagging"), ("top", "Hogging")):
        flex = flexure[face]["outputs"]
        web_shear = shear.get(face, {}).get("outputs", {})
        if "capacity_knm" in flex and "provided_capacity_kn" in web_shear:
            rows.append(
                f"<tr><th>{label}</th><td>{flex['capacity_knm']:.3f}</td>"
                f"<td>{web_shear['provided_capacity_kn']:.3f}</td></tr>"
            )
    flange_width = flexure["bottom"]["effective_inputs"]["flange_width_mm"]["value"]
    flange_html = (
        f"<p>Effective sagging flange width {flange_width:g} mm.</p>"
        if flange_width is not None
        else ""
    )
    revised_rows = {
        row["action"]["row_id"]: row
        for row in cutoff.get("reduced_section_rows", lap.get("partner_rows", ()))
    }
    checked_rows = [
        revised_rows.get(row["action"]["row_id"], row) for row in strength["rows"]
    ]
    actions = "".join(
        f"<tr><th>{html.escape(row['action']['row_id'])}</th>"
        f"<td>{row['station']['x_mm']:g}</td>"
        f"<td>{row['action']['mu_knm']:g}</td>"
        f"<td>{row['action']['vu_kn']:g}</td>"
        f"<td>{row['action']['tu_knm']:g}</td>"
        f"<td>{row['section_status']}</td></tr>"
        for row in checked_rows
        if row["kind"] == "ULS" and not row["diagnostic_only"]
    )
    anchors = "".join(
        f"<tr><th>{html.escape(row['action']['row_id'])}</th>"
        f"<td>{html.escape(check['bar_id'])}</td>"
        f"<td>{html.escape(check['criterion'].replace('_', ' '))}</td>"
        f"<td>{check['required_development_length_mm']:.3f}</td>"
        f"<td>{check['available_for_criterion_mm']:.3f}</td>"
        f"<td>{'PASS' if check['passed'] else 'FAIL'}</td></tr>"
        for row in checked_rows
        for anchor in (row["anchorage"], row.get("positive_support_anchorage"))
        if anchor
        for check in anchor["outputs"].get("checks", ())
    )
    heading = (
        "Uncurtailed section resistance"
        if cutoff.get("reduced_section_rows")
        else "Section resistance"
    )
    return (
        f"<h2>{heading}</h2>{flange_html}"
        "<table><thead><tr><th>Flexure direction</th><th>Moment (kN·m)</th>"
        f"<th>Web shear (kN)</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
        "<h2>Supplied concurrent ULS actions at physical stations</h2>"
        "<table><thead><tr><th>Row ID</th><th>Station (mm)</th><th>Moment (kN·m)</th>"
        "<th>Shear (kN)</th><th>Torsion (kN·m)</th><th>Section check</th></tr></thead>"
        f"<tbody>{actions}</tbody></table>"
        "<h2>Straight support anchorage</h2>"
        "<table><thead><tr><th>Row ID</th><th>Bar ID</th><th>Criterion</th><th>Required (mm)</th>"
        "<th>Available (mm)</th><th>Check</th></tr></thead>"
        f"<tbody>{anchors}</tbody></table>"
    )
