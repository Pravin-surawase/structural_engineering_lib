"""Checked continuous bar and ordinary link schedules for two-span beams."""

from __future__ import annotations

import csv
import html
import io
import math
from collections.abc import Iterable
from dataclasses import replace
from itertools import pairwise, product
from typing import Annotated, Any, Literal, Self

from pydantic import Field, field_validator, model_validator

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
from structural_lib.beam.lap_placement import (
    LapPlacementEnvelope,
    check_nested_lap_placement,
)
from structural_lib.beam.physical_torsion import (
    ClosedLinkDetailRequest,
    check_closed_link_detail,
)
from structural_lib.beam.reinforcement import BarPosition, Face
from structural_lib.beam.semantics import (
    EngineeringState,
    ExecutionState,
    OperationResult,
    semantic_hash,
)
from structural_lib.beam.shear_torsion import TransverseLink
from structural_lib.codes.is456.column.detailing import (
    calculate_tie_spacing,
    minimum_tie_diameter,
)
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
    BeamContinuousRowResultV1,
    _bar_positions,
    _check_row,
    _check_station_beam,
    _positive_support_web_capacity,
    _row_issues,
    _sections,
    _support_faces,
    check_continuous_beam,
)
from structural_lib.services.beam_haunch_geometry import (
    BeamHaunchDetailV1,
    resolve_haunch_geometry,
)
from structural_lib.services.beam_haunch_outputs import (
    render_haunch_report,
    render_haunch_svg,
)
from structural_lib.services.beam_haunch_strength import (
    check_haunch_bend_restraint,
    check_haunch_station_strength,
)
from structural_lib.services.beam_layered_edit_checks import (
    BeamLayeredEditServiceV1,
    check_layered_edit_actions,
)
from structural_lib.services.beam_layered_edit_outputs import (
    project_centre_cross_tie,
    render_layered_cage_report,
)
from structural_lib.services.beam_layered_edit_paths import centre_cross_tie_paths
from structural_lib.services.beam_layered_edit_placement import (
    BeamCentreCrossTieV1,
    BeamLayeredCagePlacementV1,
    check_layered_cage_placement,
)
from structural_lib.services.beam_link_zones import (
    BeamLinkZoneV1,
    ResolvedBeamLinkZone,
    check_varied_link_strength,
    resolve_beam_link_zones,
    zone_transition_actions_issue,
)
from structural_lib.services.beam_physical_flange_geometry import (
    BeamPhysicalFlangeDetailV1,
    flange_issue,
    resolve_physical_flange_geometry,
)
from structural_lib.services.beam_physical_flange_outputs import (
    render_physical_flange_report,
    render_physical_flange_svg,
)
from structural_lib.services.beam_physical_flange_strength import (
    bind_physical_flange_actions,
    check_physical_flange_anchorage,
    check_physical_flange_strength,
)
from structural_lib.services.beam_physical_flange_strip import (
    check_physical_flange_strip,
)
from structural_lib.services.beam_support_lap import check_support_lap_continuity
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


class BeamRestraintLinkV1(StrictPublicModel):
    """A narrower closed link on a staggered grid within the web cage."""

    left_centre_x_mm: float = Field(gt=0)
    right_centre_x_mm: float = Field(gt=0)
    station_offset_mm: float = Field(gt=0)


class BeamOrdinaryLinkDetailV1(StrictPublicModel):
    """Actual placement interval and fabricated hook geometry for web links."""

    first_station_mm: float = Field(ge=-1500, le=30000)
    last_station_mm: float = Field(ge=0, le=32000)
    internal_bend_radius_mm: float = Field(gt=0, le=100)
    hook_vertex_leg_mm: float = Field(gt=0, le=300)
    hook_plane_offset_mm: float = Field(gt=0, le=100)
    source_reference: Reference
    restraint_link: BeamRestraintLinkV1 | None = None


class BeamBottomCutoffV1(StrictPublicModel):
    """One straight bottom bar with a theoretical and physical termination."""

    bar_id: Identifier
    theoretical_station_id: Identifier
    termination_station_id: Identifier


class BeamBarEditV1(StrictPublicModel):
    """An explicit diameter change and optional transverse centre change."""

    bar_id: Identifier
    diameter_mm: float = Field(ge=8, le=40)
    x_from_left_mm: float | None = Field(default=None, gt=0)


class BeamSeparatedBottomLapV1(StrictPublicModel):
    """One equal-diameter separated tension splice in a supported lap window."""

    bar_id: Identifier
    partner_bar_id: Identifier
    partner_x_from_left_mm: float = Field(gt=0)
    start_station_id: Identifier
    middle_station_id: Identifier
    end_station_id: Identifier
    placement_reference: Reference


class BeamLapPlacementEnvelopeV1(StrictPublicModel):
    """Declared tolerances for an unobstructed web cage with two link grids."""

    source_reference: Reference
    bar_axis_tolerance_mm: float = Field(ge=0, le=30)
    bar_end_tolerance_mm: float = Field(ge=0, le=100)
    cage_location_tolerance_mm: float = Field(ge=0, le=30)
    link_station_tolerance_mm: float = Field(ge=0, le=50)
    internal_bend_radius_tolerance_mm: float = Field(ge=0, le=20)
    hook_plane_tolerance_mm: float = Field(ge=0, le=20)
    hook_vertex_leg_tolerance_mm: float = Field(ge=0, le=30)
    longitudinal_diameter_allowance_mm: float = Field(ge=0, le=10)
    link_diameter_allowance_mm: float = Field(ge=0, le=5)
    required_cover_mm: float = Field(gt=0, le=100)
    concrete_placement_access_diameter_mm: float = Field(gt=0, le=200)


class BeamLayeredCageDetailV1(StrictPublicModel):
    """Placement and service evidence for an ordinary two-layer rectangular cage."""

    placement: BeamLayeredCagePlacementV1 | None = None
    cross_tie: BeamCentreCrossTieV1 | None = None
    service: BeamLayeredEditServiceV1 | None = None


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
    placement_envelope: BeamLapPlacementEnvelopeV1 | Literal["not_requested"] | None = (
        Field(
            default="not_requested",
            exclude_if=lambda value: value == "not_requested",
        )
    )
    link_zones: (
        Annotated[tuple[BeamLinkZoneV1, ...], Field(min_length=2, max_length=12)]
        | Literal["not_requested"]
        | None
    ) = Field(
        default="not_requested", exclude_if=lambda value: value == "not_requested"
    )

    haunch: BeamHaunchDetailV1 | Literal["not_requested"] | None = Field(
        default="not_requested", exclude_if=lambda value: value == "not_requested"
    )
    physical_flange: BeamPhysicalFlangeDetailV1 | Literal["not_requested"] | None = (
        Field(
            default="not_requested", exclude_if=lambda value: value == "not_requested"
        )
    )
    layered_cage: BeamLayeredCageDetailV1 | Literal["not_requested"] = Field(
        default="not_requested", exclude_if=lambda value: value == "not_requested"
    )

    @field_validator("link_zones", mode="before")
    @classmethod
    def accept_link_zone_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.identity.member_id != self.member.member_id:
            raise ValueError("Member and detailing identities must agree.")
        return self


def _physical_paths(
    request: BeamContinuousDetailingInputV1,
    source_hash: str,
    cutoff_bounds: tuple[float, float] | None,
    lap_pieces: tuple[LongitudinalBarPath, LongitudinalBarPath] | None,
    zones: tuple[ResolvedBeamLinkZone, ...] = (),
) -> tuple[BarPathRequest, tuple[ClosedLinkDetailRequest, ...]] | None:
    member, detail = request.member, request.link_detail
    extent = member.straight_bars
    if detail is None or extent is None:
        return None
    spacing = member.link_spacing_mm
    intervals = (detail.last_station_mm - detail.first_station_mm) / spacing
    left, _, right = member.supports
    if (
        detail.first_station_mm > left.right_face_mm
        or detail.last_station_mm < right.left_face_mm
    ):
        return None
    if zones:
        stations = tuple(x for zone in zones for x in zone.stations_mm)
    else:
        if not 1 <= round(intervals) <= 250 or not math.isclose(
            intervals, round(intervals), rel_tol=0, abs_tol=1e-8
        ):
            return None
        stations = tuple(
            detail.first_station_mm + index * spacing
            for index in range(round(intervals) + 1)
        )
    diameter = member.link_diameter_mm
    mark = f"{member.member_id}-L{diameter:g}"
    inset = member.clear_cover_mm + diameter / 2
    x1, x2 = inset, member.width_mm - inset
    y1, y2 = inset, member.depth_mm - inset
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
            *(
                cutoff_bounds
                if cutoff_bounds is not None
                and request.cutoff
                and bar.bar_id == request.cutoff.bar_id
                else (extent.start_mm, extent.end_mm)
            ),
            0.87 * member.fy_nmm2,
        )
        for bar in member.bars
    )
    if lap_pieces is not None:
        original, partner = lap_pieces
        lap_mark = next(bar.bar_mark for bar in bars if bar.bar_id == original.bar_id)
        bars = (
            *(bar for bar in bars if bar.bar_id != original.bar_id),
            replace(original, bar_mark=f"{lap_mark}-{original.bar_mark}"),
            replace(partner, bar_mark=f"{lap_mark}-{partner.bar_mark}"),
        )
    longitudinal = [
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
                (
                    (
                        "top-lap"
                        if bar.role is ReinforcementRole.TOP_LONGITUDINAL
                        else "bottom-lap"
                    ),
                )
                if request.lap
                and bar.bar_id in (request.lap.bar_id, request.lap.partner_bar_id)
                else ()
            ),
        )
        for bar in bars
    ]
    outer_links = _link_grid(
        member, detail, mark, x1, x2, stations, {bar.bar_id for bar in bars}
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
        (*longitudinal, *outer_links),
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
    outer = ClosedLinkDetailRequest(
        paths, cage, link, arrangement, left.right_face_mm, right.left_face_mm
    )
    if zones:
        # Each neighbour verifies the single physical link at the shared
        # boundary. Only the combined path list and BBS own that link.
        by_station = dict(zip(stations, outer_links, strict=True))
        return paths, tuple(
            replace(
                outer,
                paths=replace(
                    paths,
                    paths=(
                        *longitudinal,
                        *(
                            seed
                            for x, seed in by_station.items()
                            if zone.placement.start_station_x_mm - 1e-8
                            <= x
                            <= zone.placement.end_station_x_mm + 1e-8
                        ),
                    ),
                ),
                link=replace(link, spacing_mm=zone.placement.spacing_mm),
                required_start_mm=zone.placement.start_station_x_mm,
                required_end_mm=zone.placement.end_station_x_mm,
            )
            for zone in zones
        )
    if detail.restraint_link is None:
        return paths, (outer,)
    extra = _restraint_link_request(request, outer, round(intervals))
    if extra is None:
        return None
    extra_links = (
        seed for seed in extra.paths.paths if seed.role is BarPathRole.TRANSVERSE_LINK
    )
    combined = replace(paths, paths=(*paths.paths, *extra_links))
    return combined, (outer, extra)


def _link_grid(
    member: BeamContinuousCheckRequestV1 | BeamLayeredContinuousCheckRequestV1,
    detail: BeamOrdinaryLinkDetailV1,
    mark: str,
    x1: float,
    x2: float,
    stations: tuple[float, ...],
    used_ids: set[str],
) -> tuple[BarPathSeed, ...]:
    diameter = member.link_diameter_mm
    inset = member.clear_cover_mm + diameter / 2
    y1, y2 = inset, member.depth_mm - inset
    radius = detail.internal_bend_radius_mm + diameter / 2
    tail, shift = detail.hook_vertex_leg_mm, detail.hook_plane_offset_mm
    vertices = (
        (0, x1 + tail, y1),
        (0, x1, y1),
        (0, x1, y2),
        (shift, x2, y2),
        (shift, x2, y1),
        (shift, x1, y1),
        (shift, x1, y1 + tail),
    )
    seeds = []
    for index, station in enumerate(stations, 1):
        bar_id = f"{mark}-{index}"
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
    return tuple(seeds)


def _restraint_link_request(
    request: BeamContinuousDetailingInputV1,
    outer: ClosedLinkDetailRequest,
    intervals: int,
) -> ClosedLinkDetailRequest | None:
    member, detail = request.member, request.link_detail
    assert detail is not None and detail.restraint_link is not None
    inner = detail.restraint_link
    x1, x2 = inner.left_centre_x_mm, inner.right_centre_x_mm
    offset = inner.station_offset_mm
    diameter = outer.link.diameter_mm
    gap = _restraint_grid_clearance(member, detail, offset)
    if not (
        request.lap is not None
        and isinstance(member, BeamLayeredContinuousCheckRequestV1)
        and (member.flange is not None or request.placement_envelope != "not_requested")
        and outer.cage.left_centre_x_mm < x1 < x2 < outer.cage.right_centre_x_mm
        and x2 - x1 > detail.hook_vertex_leg_mm
        and gap >= member.aggregate_size_mm + 5
        and detail.last_station_mm + offset + detail.hook_plane_offset_mm
        <= outer.paths.member_end_x_mm - member.clear_cover_mm - diameter / 2
    ):
        return None
    bars = tuple(bar for bar in outer.arrangement.bars if x1 < bar.x_from_left_mm < x2)
    bound_ids = {bar.bar_id for bar in bars}
    # A bar outside the supplementary cage must also clear its side legs.
    if any(
        min(abs(bar.x_from_left_mm - x) for x in (x1, x2))
        < (bar.diameter_mm + diameter) / 2
        for bar in outer.arrangement.bars
        if bar.bar_id not in bound_ids
    ):
        return None
    mark = f"{outer.link.link_id}-restraint"
    seeds = _link_grid(
        member,
        detail,
        mark,
        x1,
        x2,
        tuple(
            (detail.first_station_mm + index * member.link_spacing_mm) + offset
            for index in range(intervals + 1)
        ),
        {seed.bar_id for seed in outer.paths.paths},
    )
    paths = replace(
        outer.paths,
        paths=(
            *(seed for seed in outer.paths.paths if seed.bar_id in bound_ids),
            *seeds,
        ),
    )
    cage = replace(outer.cage, link_id=mark, left_centre_x_mm=x1, right_centre_x_mm=x2)
    return replace(
        outer,
        paths=paths,
        cage=cage,
        link=replace(outer.link, link_id=mark, centre_width_mm=x2 - x1),
        arrangement=replace(outer.arrangement, bars=bars, links=(cage,)),
    )


def _restraint_grid_clearance(
    member: BeamContinuousCheckRequestV1 | BeamLayeredContinuousCheckRequestV1,
    detail: BeamOrdinaryLinkDetailV1,
    offset: float,
) -> float:
    return (
        min(offset, member.link_spacing_mm - offset)
        - detail.hook_plane_offset_mm
        - member.link_diameter_mm
    )


def _schedule(
    request: BeamContinuousDetailingInputV1,
    paths: OperationResult,
    details: tuple[ClosedLinkDetailRequest, ...],
    splice: SpliceRecord | None,
    resolved_zones: tuple[ResolvedBeamLinkZone, ...] = (),
) -> OperationResult:
    link = request.link_detail
    assert link is not None
    zones = [
        LinkPlacementZone(
            "both-spans",
            details[0].link.link_id,
            link.first_station_mm,
            link.last_station_mm,
            details[0].link.spacing_mm,
            True,
            True,
        )
    ]
    if link.restraint_link is not None:
        offset = link.restraint_link.station_offset_mm
        zones.append(
            replace(
                zones[0],
                zone_id="restraint-links",
                bar_mark=details[1].link.link_id,
                start_station_x_mm=link.first_station_mm + offset,
                end_station_x_mm=link.last_station_mm + offset,
            )
        )
    cage = request.layered_cage
    if isinstance(cage, BeamLayeredCageDetailV1) and cage.cross_tie is not None:
        tie = cage.cross_tie
        zones.append(
            replace(
                zones[0],
                zone_id="centre-cross-ties",
                bar_mark=f"{request.member.member_id}-CT{tie.diameter_mm:g}",
                start_station_x_mm=link.first_station_mm + tie.station_offset_mm,
                end_station_x_mm=link.last_station_mm + tie.station_offset_mm,
            )
        )
    return _create_bound_bbs(
        request,
        paths,
        (
            tuple(zone.placement for zone in resolved_zones)
            if resolved_zones
            else tuple(zones)
        ),
        splice,
    )


def _create_bound_bbs(
    request: BeamContinuousDetailingInputV1,
    paths: OperationResult,
    zones: tuple[LinkPlacementZone, ...],
    splice: SpliceRecord | None = None,
) -> OperationResult:
    data = paths.output_as("reinforcement_schedule", BarPathOutput)
    binding = result_binding(paths, "reinforcement_schedule")
    return create_bbs(
        BbsRequest(
            data.profile_id,
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
            link_zones=zones,
        )
    )


def _check_bottom_cutoff(
    request: BeamContinuousDetailingInputV1,
    checked: BeamContinuousCheckResultV1,
) -> tuple[
    tuple[float, float] | None,
    dict[str, Any],
    list[StructuralIssueV1],
    EngineeringStatus,
]:
    member, cutoff = request.member, request.cutoff
    assert cutoff is not None
    stations = {station.station_id: station for station in member.stations}
    theoretical = stations.get(cutoff.theoretical_station_id)
    end = stations.get(cutoff.termination_station_id)
    bar = next((bar for bar in member.bars if bar.bar_id == cutoff.bar_id), None)
    extent = member.straight_bars
    layered = isinstance(member, BeamLayeredContinuousCheckRequestV1)
    left, middle, right = member.supports
    if not (
        extent
        and theoretical
        and end
        and bar
        and bar.face == "bottom"
        and (not isinstance(bar, BeamSectionBarV1) or bar.layer == 1)
        and theoretical.side == end.side == "CONTINUOUS"
        and (
            left.right_face_mm < theoretical.x_mm < end.x_mm < middle.left_face_mm
            or (
                isinstance(member, BeamLayeredContinuousCheckRequestV1)
                and member.flange is None
                and middle.right_face_mm
                < end.x_mm
                < theoretical.x_mm
                < right.left_face_mm
            )
        )
    ):
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_BASIS_HELD",
            "cutoff",
            "Identify an outer-layer bottom bar and ordered cutoff stations toward the interior support. The second clear span requires a layered rectangular cage.",
        )
        return None, {}, [issue], EngineeringStatus.HOLD

    reverse = end.x_mm < theoretical.x_mm
    direction = (
        AnchorageDirection.DECREASING_X if reverse else AnchorageDirection.INCREASING_X
    )
    retained_extent = (
        (end.x_mm, extent.end_mm) if reverse else (extent.start_mm, end.x_mm)
    )
    affected_side = -1 if reverse else 1

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
        if row.kind == "ULS"
        and affected_side * (row.station.x_mm - theoretical.x_mm) >= 0
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
    extension = abs(end.x_mm - theoretical.x_mm)
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
                    direction,
                    *retained_extent,
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
        retained_extent,
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
            **({"cutoff_direction": direction.value} if reverse else {}),
        },
        failed + held,
        (
            EngineeringStatus.FAIL
            if failed
            else EngineeringStatus.HOLD if held else EngineeringStatus.PASS
        ),
    )


def _check_lap(
    request: BeamContinuousDetailingInputV1,
    checked: BeamContinuousCheckResultV1,
) -> tuple[
    tuple[LongitudinalBarPath, LongitudinalBarPath] | None,
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
    left, support, right = member.supports
    extent = member.straight_bars
    bar = next((item for item in member.bars if item.bar_id == lap.bar_id), None)
    top_lap = (
        bar is not None
        and bar.face == "top"
        and isinstance(member, BeamLayeredContinuousCheckRequestV1)
        and member.flange is None
        and request.placement_envelope != "not_requested"
        and request.link_detail is not None
        and request.link_detail.restraint_link is not None
    )
    if not (
        extent
        and bar
        and (bar.face == "bottom" or top_lap)
        and (not isinstance(bar, BeamSectionBarV1) or bar.layer == 1)
        and bar.diameter_mm <= 32
        and lap.partner_bar_id not in {item.bar_id for item in member.bars}
        and start
        and middle
        and end
        and start.side == middle.side == end.side == "CONTINUOUS"
        and start.x_mm < middle.x_mm < end.x_mm
        and (
            (left.right_face_mm < start.x_mm and end.x_mm < support.left_face_mm)
            or (
                isinstance(member, BeamLayeredContinuousCheckRequestV1)
                and not top_lap
                and member.flange is None
                and support.right_face_mm < start.x_mm
                and end.x_mm < right.left_face_mm
            )
        )
        and lap.partner_x_from_left_mm < member.width_mm
    ):
        issue = StructuralIssueV1(
            "BEAM.LAP_BASIS_HELD",
            "lap",
            (
                "Supply an outer-layer top bar up to Ø32 and a distinct partner with three ordered stations in the first clear span of a layered rectangle with a nested restraint link and a requested placement check."
                if bar is not None and bar.face == "top"
                else "Identify an outer-layer bottom bar up to Ø32, a distinct partner and three ordered stations in one clear span. The second clear span requires a layered rectangular cage."
            ),
        )
        return None, {}, [issue], EngineeringStatus.HOLD

    reverse = start.x_mm > support.right_face_mm
    tension_face = Face.TOP if top_lap else Face.BOTTOM
    role = (
        ReinforcementRole.TOP_LONGITUDINAL
        if top_lap
        else ReinforcementRole.BOTTOM_LONGITUDINAL
    )

    combos = {
        combo.combination_id for combo in member.combinations if combo.kind == "ULS"
    }
    lap_ids = {start.station_id, middle.station_id, end.station_id}
    expanded_start, expanded_end = start.x_mm, end.x_mm
    if top_lap and isinstance(request.placement_envelope, BeamLapPlacementEnvelopeV1):
        tolerance = request.placement_envelope.bar_end_tolerance_mm
        expanded_start -= tolerance
        expanded_end += tolerance
        limits = {expanded_start, expanded_end}
        boundary_stations = {
            site.x_mm: site.station_id
            for site in member.stations
            if site.side == "CONTINUOUS" and site.x_mm in limits
        }
        if (
            boundary_stations.keys() != limits
            or expanded_start <= left.right_face_mm
            or expanded_end >= support.left_face_mm
        ):
            return (
                None,
                {},
                [
                    StructuralIssueV1(
                        "BEAM.LAP_ACTIONS_HELD",
                        "lap",
                        "Supply stations at both tolerance-adjusted lap ends within the first clear span.",
                    )
                ],
                EngineeringStatus.HOLD,
            )
        lap_ids.update(boundary_stations.values())
    inventory = {
        (row.action.combination_id, row.station.station_id) for row in checked.rows
    }
    missing = sorted({(cid, sid) for cid in combos for sid in lap_ids} - inventory)
    if missing:
        issue = StructuralIssueV1(
            "BEAM.LAP_ACTIONS_HELD",
            "lap",
            (
                "Supply every declared ULS combination at the required top lap stations."
                if top_lap
                else "Supply every declared ULS combination at the start, interior and end of the overlap."
            ),
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
        sign_rows = (
            tuple(
                row
                for row in checked.rows
                if row.kind == "ULS"
                and expanded_start <= row.station.x_mm <= expanded_end
            )
            if top_lap
            else splice_rows
        )
        wrong_sign = any(
            row.action.mu_knm >= 0 if top_lap else row.action.mu_knm <= 0
            for row in sign_rows
        )
        if cover < 2 * diameter or wrong_sign:
            issue = StructuralIssueV1(
                "BEAM.LAP_TENSION_BASIS_HELD",
                "lap",
                (
                    "The top lap needs hogging across the supplied placement window and clear concrete cover of at least two bar diameters."
                    if top_lap
                    else "The layered lap requires sagging in every supplied overlap row and clear concrete cover of at least two bar diameters at both pieces."
                ),
            )
            return None, {}, [issue], EngineeringStatus.HOLD

        # The lapped outer bar changes axis. Every inner bar must stay aligned
        # over an uninterrupted outer bar before, through and after the lap.
        outer_axes = [
            item.x_from_left_mm
            for item in positions
            if item.face is tension_face
            and item.layer == 1
            and item.bar_id != bar.bar_id
        ]
        unaligned = [
            item.bar_id
            for item in positions
            if item.face is tension_face
            and item.layer > 1
            and not any(abs(item.x_from_left_mm - axis) <= 1e-6 for axis in outer_axes)
        ]
        if unaligned:
            issue = StructuralIssueV1(
                "BEAM.LAP_LAYER_ALIGNMENT_FAIL",
                "lap",
                f"Inner {tension_face.value} bars must align with uninterrupted outer bars: "
                + ", ".join(unaligned)
                + ".",
            )
            return (
                None,
                {"unaligned_inner_bar_ids": unaligned},
                [issue],
                EngineeringStatus.FAIL,
            )

    partner_positions = _lap_partner_positions(positions, lap)
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
    original = LongitudinalBarPath(
        bar.bar_id,
        "lap-I",
        role,
        bar.diameter_mm,
        bar.layer if isinstance(bar, BeamSectionBarV1) else 1,
        bar.x_from_left_mm,
        bar.y_from_top_mm,
        start.x_mm if reverse else extent.start_mm,
        extent.end_mm if reverse else end.x_mm,
        0.87 * member.fy_nmm2,
    )
    partner = replace(
        original,
        bar_id=lap.partner_bar_id,
        bar_mark="lap-J",
        x_from_left_mm=lap.partner_x_from_left_mm,
        start_station_mm=extent.start_mm if reverse else start.x_mm,
        end_station_mm=end.x_mm if reverse else extent.end_mm,
    )
    faces = _support_faces(member)
    web_capacity = (
        _positive_support_web_capacity(member, partner_positions)
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else None
    )
    transfer_extents = None
    if top_lap:
        transfer_extents = {
            item.bar_id: (extent.start_mm, extent.end_mm) for item in partner_positions
        }
        transfer_extents[partner.bar_id] = (
            partner.start_station_mm,
            partner.end_station_mm,
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
            bar_extents=transfer_extents,
        )
        for row in checked.rows
        if row.kind == "ULS"
        and (
            row.station.x_mm <= end.x_mm if reverse else row.station.x_mm >= start.x_mm
        )
    )
    failed, held = _row_issues(partner_rows, faces, layered=layered)
    full_tension = checked.flexural_sections[tension_face].outputs
    d = float(full_tension["effective_depth_mm"])
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
                role,
                float(full_tension["minimum_tension_steel_area_mm2"]),
                abs(row.action.vu_kn) * 1000,
                float(shear[tension_face].outputs["provided_capacity_kn"]) * 1000,
                row.action.row_id,
            )
        )
    checked_lap = check_laps_and_curtailment(
        LapCurtailmentCheckRequest(
            WORKFLOW,
            member.member_id,
            "second-span" if reverse else "first-span",
            member.analysis_revision,
            member.reinforcement_revision,
            support.left_face_mm if reverse else left.left_face_mm,
            right.right_face_mm if reverse else support.right_face_mm,
            d,
            member.fck_nmm2,
            member.fy_nmm2,
            BarSurface.DEFORMED,
            (original, partner),
            tuple(demands),
            (
                SpliceDetail(
                    "top-lap" if top_lap else "bottom-lap",
                    SpliceKind.LAP,
                    (original.bar_id, partner.bar_id),
                    start.x_mm,
                    end.x_mm,
                    StressState.TENSION,
                    False,
                    100 / sum(item.face == tension_face.value for item in member.bars),
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
    restraint = None
    if status is EngineeringStatus.PASS and layered and request.link_detail is not None:
        original_rows = tuple(
            row
            for row in checked.rows
            if original.start_station_mm <= row.station.x_mm <= original.end_station_mm
        )
        restraint = _lap_compression_restraint(
            request,
            (
                ("upstream", checked.flexural_sections, original_rows),
                ("downstream", flexure, partner_rows),
            ),
            (original, partner),
        )
    return (
        (original, partner),
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
            **({"tension_face": "top"} if top_lap else {}),
            **({"compression_restraint": restraint} if restraint is not None else {}),
            **(
                {"lap_direction": AnchorageDirection.DECREASING_X.value}
                if reverse
                else {}
            ),
            **(
                {"web_only_anchor_moment_knm": web_capacity}
                if isinstance(member, BeamLayeredContinuousCheckRequestV1)
                and member.flange is not None
                else {}
            ),
        },
        failed + held,
        status,
    )


def _lap_partner_positions(
    positions: tuple[BarPosition, ...], lap: BeamSeparatedBottomLapV1
) -> tuple[BarPosition, ...]:
    return tuple(
        (
            replace(
                bar,
                bar_id=lap.partner_bar_id,
                x_from_left_mm=lap.partner_x_from_left_mm,
            )
            if bar.bar_id == lap.bar_id
            else bar
        )
        for bar in positions
    )


def _lap_compression_restraint(
    request: BeamContinuousDetailingInputV1,
    layouts: tuple[
        tuple[str, dict[Face, OperationResult], tuple[BeamContinuousRowResultV1, ...]],
        ...,
    ],
    lap_pieces: tuple[LongitudinalBarPath, LongitudinalBarPath],
    *,
    placement_seats: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    """Verify compression restraint for the ordinary closed web link."""
    member, link = request.member, request.link_detail
    assert isinstance(member, BeamLayeredContinuousCheckRequestV1) and link is not None
    original, partner = lap_pieces
    existing = {bar.bar_id: bar for bar in member.bars}
    existing[partner.bar_id] = existing[original.bar_id].model_copy(
        update={"bar_id": partner.bar_id, "x_from_left_mm": partner.x_from_left_mm}
    )
    source = "IS 456:2000 clauses 26.5.1.2 and 26.5.3.2, including Amendment No. 1"
    link_dia = member.link_diameter_mm
    bend_radius = link.internal_bend_radius_mm
    # The bend centre is one link diameter plus the inner radius from cover.
    bend_inset = member.clear_cover_mm + link_dia + bend_radius
    pitch = member.link_spacing_mm
    depth_shift = 0.0
    if placement_seats is not None:
        seat_ids = placement_seats
        basis = request.placement_envelope
        assert isinstance(basis, BeamLapPlacementEnvelopeV1)
        pitch += 2 * basis.link_station_tolerance_mm
        depth_shift = basis.cage_location_tolerance_mm + basis.bar_axis_tolerance_mm
    elif link.restraint_link is not None:
        inset = member.clear_cover_mm + link_dia / 2
        bend_axis_radius = bend_radius + link_dia / 2
        corner_sets = {
            "outer": (inset, member.width_mm - inset),
            "restraint": (
                link.restraint_link.left_centre_x_mm,
                link.restraint_link.right_centre_x_mm,
            ),
        }
        seat_ids = {
            name: _rounded_link_seats(
                existing.values(),
                left,
                right,
                bend_inset,
                member.depth_mm,
                bend_axis_radius,
                bend_radius,
            )
            for name, (left, right) in corner_sets.items()
        }
    else:
        seat_ids = {}
    layouts_checked = []
    for layout, capacities, rows in layouts:
        for tension_face in (Face.BOTTOM, Face.TOP):
            row_ids = [
                row.action.row_id
                for row in rows
                if row.kind == "ULS"
                and not row.diagnostic_only
                and row.tension_face == tension_face.value
            ]
            if not row_ids:
                continue
            responses = capacities[tension_face].outputs["bar_responses"]
            credited = sorted(
                row["bar_id"] for row in responses if row["net_force_n"] > 0
            )
            if not credited:
                continue
            face = Face.TOP if tension_face is Face.BOTTOM else Face.BOTTOM
            cage = [existing[row["bar_id"]] for row in responses if row["face"] == face]
            outer = sorted(
                (bar for bar in cage if bar.layer == 1),
                key=lambda bar: bar.x_from_left_mm,
            )
            bend_y = bend_inset if face is Face.TOP else member.depth_mm - bend_inset
            # At both ends of the outer row, use bars seated in the nominal
            # 90-degree link bends as positive proof of two-direction restraint.
            corners = [
                bar.bar_id
                for x in (bend_inset, member.width_mm - bend_inset)
                for bar in outer
                if math.isclose(bar.x_from_left_mm, x, rel_tol=0, abs_tol=1e-6)
                and math.isclose(bar.y_from_top_mm, bend_y, rel_tol=0, abs_tol=1e-6)
                and math.isclose(
                    bar.diameter_mm / 2, bend_radius, rel_tol=0, abs_tol=1e-6
                )
            ]
            gaps = (
                [
                    right.x_from_left_mm - left.x_from_left_mm
                    for left, right in pairwise(outer)
                ]
                if len(outer) > 2
                else []
            )
            outer_supported = (
                2 <= len(outer) <= 3
                and corners == [outer[0].bar_id, outer[-1].bar_id]
                and all(
                    math.isclose(bar.y_from_top_mm, bend_y, rel_tol=0, abs_tol=1e-6)
                    for bar in outer
                )
                and all(gap <= 75 for gap in gaps)
            )
            if seat_ids:
                seated = seat_ids["outer"] | seat_ids["restraint"]
                corners = [bar.bar_id for bar in outer if bar.bar_id in seated]
                outer_supported = bool(outer) and len(corners) == len(outer)
            inner = [bar for bar in cage if bar.layer > 1]
            maximum_inner_dia = max((bar.diameter_mm for bar in inner), default=0)
            inner_supported = all(
                (
                    bar.y_from_top_mm
                    if face is Face.TOP
                    else member.depth_mm - bar.y_from_top_mm
                )
                >= 3 * maximum_inner_dia + depth_shift
                for bar in inner
            )
            active_diameters = [
                existing[row["bar_id"]].diameter_mm for row in responses
            ]
            tie_pitch_limit = calculate_tie_spacing(
                member.width_mm,
                member.depth_mm,
                min(active_diameters),
            )
            tie_diameter_limit = minimum_tie_diameter(max(active_diameters))
            verified = (
                outer_supported
                and inner_supported
                and set(credited) <= {bar.bar_id for bar in cage}
                and pitch <= tie_pitch_limit
                and link_dia >= tie_diameter_limit
            )
            layouts_checked.append(
                {
                    "layout": layout,
                    "compression_face": face.value,
                    "row_ids": row_ids,
                    "corner_bar_ids": corners,
                    "compressed_bar_ids": credited,
                    "intermediate_centre_gaps_mm": gaps,
                    "unresolved_bar_ids": [] if verified else credited,
                    "maximum_tie_pitch_mm": tie_pitch_limit,
                    "minimum_tie_diameter_mm": tie_diameter_limit,
                    "verified": verified,
                }
            )
    return {
        "source": source,
        "layouts": layouts_checked,
        "verified": all(layout["verified"] for layout in layouts_checked),
        **(
            {
                "corner_bar_ids_by_grid": {
                    name: sorted(ids) for name, ids in seat_ids.items()
                },
                "minimum_between_link_grids_mm": _restraint_grid_clearance(
                    member, link, link.restraint_link.station_offset_mm
                ),
            }
            if link.restraint_link is not None
            else {}
        ),
    }


def _rounded_link_seats(
    bars: Iterable[BeamSectionBarV1],
    left_mm: float,
    right_mm: float,
    bend_inset_mm: float,
    depth_mm: float,
    bend_axis_radius_mm: float,
    internal_radius_mm: float,
) -> set[str]:
    # A seat in this bounded double-link profile lies inside the bend sector
    # with no more than 1 mm radial play, independent of the straight-leg gap.
    seated = set()
    for bar in bars:
        centre_y = bend_inset_mm if bar.face == "top" else depth_mm - bend_inset_mm
        dy = (bar.y_from_top_mm - centre_y) * (1 if bar.face == "top" else -1)
        if bar.layer != 1 or dy > 0:
            continue
        for leg_x, side in ((left_mm, 1), (right_mm, -1)):
            centre_x = leg_x + side * bend_axis_radius_mm
            dx = (bar.x_from_left_mm - centre_x) * side
            clearance = internal_radius_mm - bar.diameter_mm / 2 - math.hypot(dx, dy)
            if dx < 0 and dy < 0 and -1e-6 <= clearance <= 1:
                seated.add(bar.bar_id)
    return seated


def _check_lap_placement(
    request: BeamContinuousDetailingInputV1,
    checked: BeamContinuousCheckResultV1,
    lap_pieces: tuple[LongitudinalBarPath, LongitudinalBarPath] | None,
    lap: dict[str, Any],
    link_requests: tuple[ClosedLinkDetailRequest, ...],
) -> tuple[dict[str, Any], dict[str, Any] | None, list[StructuralIssueV1]]:
    member, detail = request.member, request.link_detail
    basis = request.placement_envelope
    roles = {
        (bar.face, bar.layer)
        for bar in member.bars
        if isinstance(bar, BeamSectionBarV1)
    }
    if not (
        isinstance(basis, BeamLapPlacementEnvelopeV1)
        and isinstance(member, BeamLayeredContinuousCheckRequestV1)
        and roles == {("top", 1), ("bottom", 1), ("bottom", 2)}
        and detail is not None
        and detail.restraint_link is not None
        and lap_pieces is not None
        and len(link_requests) == 2
    ):
        return (
            {"status": "HOLD", "issue": "placement_basis_missing"},
            None,
            [
                StructuralIssueV1(
                    "BEAM.LAP_PLACEMENT_EVIDENCE_HELD",
                    "placement_envelope",
                    "Supply placement limits for the layered lap with two checked link grids, one top row and two bottom rows.",
                )
            ],
        )
    outer, inner = link_requests
    output = check_nested_lap_placement(
        outer,
        inner,
        LapPlacementEnvelope(**basis.model_dump()),
        hook_plane_offset_mm=detail.hook_plane_offset_mm,
        hook_vertex_leg_mm=detail.hook_vertex_leg_mm,
        restraint_station_offset_mm=detail.restraint_link.station_offset_mm,
    )
    output["source_reference"] = basis.source_reference
    if output["status"] != "PASS":
        interference = output["status"] == "FAIL"
        return (
            output,
            None,
            [
                StructuralIssueV1(
                    (
                        "BEAM.LAP_PLACEMENT_INTERFERENCE"
                        if interference
                        else "BEAM.LAP_RESTRAINT_SECTOR_HELD"
                    ),
                    "placement_envelope",
                    (
                        "The declared tolerance crosses a fit, cover, hook or access limit."
                        if interference
                        else "The declared bar positions do not establish a supported bend seat throughout the placement range."
                    ),
                )
            ],
        )
    end_move = basis.bar_end_tolerance_mm
    overlap = lap["overlap_mm"] - 2 * end_move
    output["minimum_overlap_mm"] = overlap
    location_move = basis.bar_axis_tolerance_mm + basis.cage_location_tolerance_mm
    lap_cover = min(
        min(
            piece.x_from_left_mm,
            member.width_mm - piece.x_from_left_mm,
            piece.y_from_top_mm,
            member.depth_mm - piece.y_from_top_mm,
        )
        - location_move
        - (piece.diameter_mm + basis.longitudinal_diameter_allowance_mm) / 2
        for piece in lap_pieces
    )
    output["minimum_lap_cover_mm"] = lap_cover
    if lap_cover < 2 * lap_pieces[0].diameter_mm:
        output.update(status="FAIL", issue="placement_lap_cover")
        return (
            output,
            None,
            [
                StructuralIssueV1(
                    "BEAM.LAP_PLACEMENT_COVER_FAIL",
                    "placement_envelope",
                    "The declared placement range can reduce lap cover below two bar diameters.",
                )
            ],
        )
    required = lap["lap_result"]["outputs"]["splice_checks"][0]["required_length_mm"]
    if overlap < required:
        output.update(status="FAIL", issue="placement_overlap_short")
        return (
            output,
            None,
            [
                StructuralIssueV1(
                    "BEAM.LAP_PLACEMENT_LENGTH_FAIL",
                    "placement_envelope.bar_end_tolerance_mm",
                    "The minimum lap over the declared bar-end range is shorter than required.",
                )
            ],
        )
    top_lap = lap.get("tension_face") == "top"
    if top_lap:
        continuity, continuity_issue = check_support_lap_continuity(
            member,
            checked.rows,
            outer.arrangement.bars,
            end_tolerance_mm=end_move,
            depth_tolerance_mm=location_move,
        )
        if continuity_issue is not None:
            output.update(
                status=(
                    "FAIL"
                    if continuity_issue.code == "BEAM.LAP_CONTINUITY_FAIL"
                    else "HOLD"
                ),
                issue="top_lap_continuity_unresolved",
            )
            return output, None, [continuity_issue]
        output["negative_steel_continuity"] = continuity
    seats = {name: set(ids) for name, ids in output["corner_bar_ids_by_grid"].items()}
    worst, minimum_development, restraint, retained_anchors, status, issues = (
        _check_placement_strength(
            request,
            member,
            basis,
            checked.rows,
            lap_pieces,
            outer.arrangement.bars,
            seats,
        )
    )
    output.update(
        worst_strength=worst,
        minimum_straight_support_development_mm=minimum_development,
        status=status.value,
        issue="placement_strength_unresolved" if issues else None,
    )
    if top_lap:
        output["retained_support_anchorage"] = retained_anchors
    return output, restraint, issues


def _check_placement_strength(
    request: BeamContinuousDetailingInputV1,
    member: BeamLayeredContinuousCheckRequestV1,
    basis: BeamLapPlacementEnvelopeV1,
    rows: tuple[BeamContinuousRowResultV1, ...],
    lap_pieces: tuple[LongitudinalBarPath, LongitudinalBarPath],
    bars: tuple[LongitudinalBarPath, ...],
    seats: dict[str, set[str]],
) -> tuple[
    dict[str, Any],
    float | None,
    dict[str, Any] | None,
    dict[str, Any],
    EngineeringStatus,
    list[StructuralIssueV1],
]:
    lap = request.lap
    assert lap is not None
    end_move = basis.bar_end_tolerance_mm
    depth_move = basis.cage_location_tolerance_mm + basis.bar_axis_tolerance_mm
    extents = {
        bar.bar_id: (bar.start_station_mm + end_move, bar.end_station_mm - end_move)
        for bar in bars
    }
    overlap_start = max(part.start_station_mm for part in lap_pieces) - end_move
    overlap_end = min(part.end_station_mm for part in lap_pieces) + end_move
    tension_face = (
        Face.TOP
        if lap_pieces[0].role is ReinforcementRole.TOP_LONGITUDINAL
        else Face.BOTTOM
    )
    member = member.model_copy(
        update={
            "link_spacing_mm": member.link_spacing_mm
            + 2 * basis.link_station_tolerance_mm
        }
    )
    positions = _bar_positions(member)
    faces = _support_faces(member)
    worst: dict[str, Any] = {}
    development: list[float] = []
    restraint = None
    retained_anchors: dict[str, Any] = {}
    failed: list[StructuralIssueV1] = []
    held: list[StructuralIssueV1] = []
    for changes in product((-depth_move, depth_move), repeat=3):
        shifts = dict(zip(("top-1", "bottom-1", "bottom-2"), changes, strict=True))
        upstream = tuple(
            replace(
                bar,
                y_from_top_mm=bar.y_from_top_mm
                + shifts[f"{bar.face.value}-{bar.layer}"],
            )
            for bar in positions
        )
        downstream = _lap_partner_positions(upstream, lap)
        layouts = []
        for name, cage, piece in zip(
            ("upstream", "downstream"), (upstream, downstream), lap_pieces, strict=True
        ):
            geometry, flexure, shear = _sections(member, cage)
            if geometry.engineering is not EngineeringState.PASS:
                issue = StructuralIssueV1(
                    "BEAM.LAP_PLACEMENT_SECTION_FAIL",
                    "placement_envelope",
                    "The supplied section fails the adverse placement geometry check.",
                )
                return worst, None, None, {}, EngineeringStatus.FAIL, [issue]
            web = _positive_support_web_capacity(member, cage)
            # Check both layouts at a row within the range of either piece's end.
            # Anchorage always uses the shorter physical extent of each bar.
            trial_rows = tuple(
                _check_row(
                    member,
                    cage,
                    row.action,
                    row.station,
                    row.kind,
                    row.diagnostic_only,
                    faces.get(row.station.x_mm),
                    flexure,
                    shear,
                    web,
                    bar_extents=extents,
                )
                for row in rows
                if (
                    row.kind == "ULS"
                    and piece.start_station_mm - end_move
                    <= row.station.x_mm
                    <= piece.end_station_mm + end_move
                )
            )
            row_failed, row_held = _row_issues(trial_rows, faces, layered=True)
            failed.extend(row_failed)
            held.extend(row_held)
            actual_rows = [row for row in trial_rows if not row.diagnostic_only]
            if tension_face is Face.TOP and name == "downstream":
                support_evidence, support_issue = _retained_top_lap_development(
                    member, actual_rows, piece.bar_id
                )
                retained_anchors.update(support_evidence)
                if support_issue is not None:
                    held.append(support_issue)
            for row in actual_rows:
                if row.anchorage is not None:
                    development.extend(
                        float(check["available_straight_length_mm"])
                        for check in row.anchorage.outputs.get("checks", ())
                    )
                if overlap_start <= row.station.x_mm <= overlap_end and (
                    row.tension_face is not tension_face
                    or row.flexure_utilization is None
                    or row.flexure_utilization > 0.5 + 1e-12
                ):
                    failed.append(
                        StructuralIssueV1(
                            "BEAM.LAP_PLACEMENT_MOMENT_FAIL",
                            f"actions.{row.action.row_id}",
                            "The expanded lap region exceeds the tension-lap moment screen under the declared placement ranges.",
                        )
                    )
            layouts.append((name, flexure, trial_rows))
            _record_placement_strength(worst, shifts, actual_rows, flexure, shear)
        trial_restraint = _lap_compression_restraint(
            request, tuple(layouts), lap_pieces, placement_seats=seats
        )
        if not trial_restraint["verified"]:
            held.append(
                StructuralIssueV1(
                    "BEAM.LAP_RESTRAINT_SECTOR_HELD",
                    "placement_envelope",
                    "The adverse placement case lacks restraint for a bar credited in compression.",
                )
            )
        if restraint is None:
            restraint = trial_restraint
    if not development or set(worst) != {"top", "bottom"}:
        held.append(
            StructuralIssueV1(
                "BEAM.LAP_PLACEMENT_ACTIONS_HELD",
                "placement_envelope",
                "The placement check requires signed rows in both bending directions and checked support development.",
            )
        )
    status = (
        EngineeringStatus.FAIL
        if failed
        else EngineeringStatus.HOLD if held else EngineeringStatus.PASS
    )
    unique_issues = list(dict.fromkeys(failed + held))
    if restraint is not None:
        restraint["verified"] = status is EngineeringStatus.PASS
        restraint["minimum_between_link_grids_mm"] -= (
            2 * basis.link_station_tolerance_mm
            + basis.hook_plane_tolerance_mm
            + basis.link_diameter_allowance_mm
        )
        restraint["placement_envelope_verified"] = status is EngineeringStatus.PASS
    return (
        worst,
        min(development, default=None),
        restraint,
        retained_anchors,
        status,
        unique_issues,
    )


def _retained_top_lap_development(
    member: BeamLayeredContinuousCheckRequestV1,
    rows: list[BeamContinuousRowResultV1],
    partner_id: str,
) -> tuple[dict[str, Any], StructuralIssueV1 | None]:
    support = member.supports[1]
    directions = {
        support.left_face_mm: AnchorageDirection.INCREASING_X,
        support.right_face_mm: AnchorageDirection.DECREASING_X,
    }
    required = {
        (combination.combination_id, face_station)
        for combination in member.combinations
        if combination.kind == "ULS"
        for face_station in directions
    }
    checked = set()
    evidence = {}
    for row in rows:
        station = row.station.x_mm
        if (
            station not in directions
            or row.tension_face is not Face.TOP
            or row.anchorage is None
            or row.anchorage.engineering is not EngineeringState.PASS
        ):
            continue
        for anchor in row.anchorage.outputs.get("checks", ()):
            if anchor["bar_id"] != partner_id:
                continue
            checked.add((row.action.combination_id, station))
            evidence[row.action.row_id] = {
                "bar_id": partner_id,
                "direction": directions[station].value,
                "straight_available_mm": anchor["available_straight_length_mm"],
                "development_required_mm": anchor["required_development_length_mm"],
            }
    issue = None
    if not required <= checked:
        issue = StructuralIssueV1(
            "BEAM.LAP_SUPPORT_DEVELOPMENT_HELD",
            "lap",
            "Supply checked hogging rows with the retained top lap bar developed at both interior support faces.",
        )
    return evidence, issue


def _record_placement_strength(
    worst: dict[str, Any],
    shifts: dict[str, float],
    rows: list[BeamContinuousRowResultV1],
    flexure: dict[Face, OperationResult],
    shear: dict[Face, OperationResult],
) -> None:
    for face in Face:
        active = [row for row in rows if row.tension_face is face]
        if not active:
            continue
        moment = float(flexure[face].outputs["capacity_knm"])
        force = float(shear[face].outputs["provided_capacity_kn"])
        summary = worst.setdefault(face.value, {})
        moment_row = min(
            active, key=lambda row: (-abs(row.action.mu_knm), row.action.row_id)
        )
        shear_row = min(
            active, key=lambda row: (-abs(row.action.vu_kn), row.action.row_id)
        )
        if abs(moment_row.action.mu_knm) > summary.get("moment_demand_knm", -1):
            summary.update(
                moment_demand_knm=abs(moment_row.action.mu_knm),
                moment_row_id=moment_row.action.row_id,
            )
        if abs(shear_row.action.vu_kn) > summary.get("shear_demand_kn", -1):
            summary.update(
                shear_demand_kn=abs(shear_row.action.vu_kn),
                shear_row_id=shear_row.action.row_id,
            )
        if moment < summary.get("capacity_knm", math.inf):
            summary.update(capacity_knm=moment, flexure_row_shifts_mm=shifts)
        if force < summary.get("shear_capacity_kn", math.inf):
            summary.update(shear_capacity_kn=force, shear_row_shifts_mm=shifts)
        summary["flexure_utilization"] = (
            summary["moment_demand_knm"] / summary["capacity_knm"]
            if summary["capacity_knm"]
            else None
        )
        summary["shear_utilization"] = (
            summary["shear_demand_kn"] / summary["shear_capacity_kn"]
            if summary["shear_capacity_kn"]
            else None
        )


def _varied_link_basis(
    request: BeamContinuousDetailingInputV1,
) -> tuple[tuple[ResolvedBeamLinkZone, ...], StructuralIssueV1 | None]:
    member, detail = request.member, request.link_detail
    if (
        not isinstance(request.link_zones, tuple)
        or not isinstance(member, BeamContinuousCheckRequestV1)
        or len(member.bars) != 4
        or member.depth_mm > 750
        or detail is None
        or detail.restraint_link is not None
        or request.lap is not None
        or request.cutoff is not None
        or request.placement_envelope != "not_requested"
    ):
        return (), StructuralIssueV1(
            "BEAM.LINK_ZONE_BASIS_HELD",
            "link_zones",
            "Varied links require the complete zone schedule for one ordinary rectangular cage with four uninterrupted corner bars and one closed link shape.",
        )
    # Verify the seated geometry of each bar at the rounded inside corner.
    # A bar with the bend's inside radius can sit at its exact arc centre.
    corner = (
        member.clear_cover_mm + member.link_diameter_mm + detail.internal_bend_radius_mm
    )
    occupied = set()
    for bar in member.bars:
        left = bar.x_from_left_mm < member.width_mm / 2
        top = bar.face == "top"
        x = bar.x_from_left_mm if left else member.width_mm - bar.x_from_left_mm
        y = bar.y_from_top_mm if top else member.depth_mm - bar.y_from_top_mm
        clearance = (
            detail.internal_bend_radius_mm
            - bar.diameter_mm / 2
            - math.hypot(corner - x, corner - y)
        )
        if x <= corner + 1e-9 and y <= corner + 1e-9 and -1e-9 <= clearance <= 1:
            occupied.add((left, top))
    if len(occupied) != 4:
        return (), StructuralIssueV1(
            "BEAM.LINK_ZONE_BASIS_HELD",
            "member.bars",
            "Verify one continuous longitudinal bar in each outside link bend.",
        )
    return resolve_beam_link_zones(
        request.link_zones,
        mark=f"{member.member_id}-L{member.link_diameter_mm:g}",
        first_station_mm=detail.first_station_mm,
        last_station_mm=detail.last_station_mm,
        minimum_grid_separation_mm=(
            detail.hook_plane_offset_mm + member.link_diameter_mm
        ),
    )


def _check_haunch_detailing(
    request: BeamContinuousDetailingInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    member, detail, haunch = request.member, request.link_detail, request.haunch
    status = EngineeringStatus.HOLD
    stale = member.analysis_revision != member.current_analysis_revision
    data: dict[str, Any] = {
        "strength": {
            "rows": [],
            "governing_rows": {},
            "ultimate_status": "HOLD",
            "serviceability_status": "NOT_EVALUATED",
        },
        "paths": None,
        "bbs": None,
        "haunch": {},
    }
    issues: list[StructuralIssueV1] = []
    if stale:
        issues.append(
            StructuralIssueV1(
                "BEAM_ANALYSIS_STALE",
                "member.analysis_revision",
                "Supply the signed actions from the current analysis revision.",
            )
        )
    elif (
        not isinstance(member, BeamContinuousCheckRequestV1)
        or not isinstance(haunch, BeamHaunchDetailV1)
        or haunch.bend_restraint is None
        or len(member.bars) != 4
        or len({bar.diameter_mm for bar in member.bars}) != 1
        or member.straight_bars is None
        or detail is None
        or detail.restraint_link is not None
        or request.cutoff is not None
        or request.lap is not None
        or request.link_zones != "not_requested"
        or request.placement_envelope != "not_requested"
    ):
        issues.append(
            StructuralIssueV1(
                "BEAM.HAUNCH_BASIS_HELD",
                "haunch",
                "Supply the ordinary haunch outline, four uninterrupted corner bars, closed links and dedicated bend restraint.",
            )
        )
    else:
        geometry, fit_issues = resolve_haunch_geometry(
            member,
            haunch,
            first_station_mm=detail.first_station_mm,
            last_station_mm=detail.last_station_mm,
            internal_bend_radius_mm=detail.internal_bend_radius_mm,
            hook_vertex_leg_mm=detail.hook_vertex_leg_mm,
            hook_plane_offset_mm=detail.hook_plane_offset_mm,
            source_hash=_input_hash(request),
            stock_length_mm=request.stock_length_mm,
        )
        issues.extend(fit_issues)
        if geometry is not None:
            data["paths"] = geometry.paths.to_dict()
            data["haunch"].update(
                bottom_segments=geometry.bottom_segments,
                link_checks=geometry.link_checks,
                minimum_link_cover_mm=geometry.minimum_link_cover_mm,
                bottom_bar_soffit_cover_bound_mm=geometry.bottom_bar_soffit_cover_bound_mm,
                minimum_axial_opening_mm=geometry.minimum_axial_opening_mm,
                face_bar_clear_spacing_mm=min(
                    max(bar.x_from_left_mm for bar in member.bars if bar.face == face)
                    - min(bar.x_from_left_mm for bar in member.bars if bar.face == face)
                    for face in ("top", "bottom")
                )
                - member.bars[0].diameter_mm,
                outline=[point.model_dump(mode="json") for point in haunch.outline],
            )
        if fit_issues:
            if any(not issue.code.endswith("_HELD") for issue in fit_issues):
                status = EngineeringStatus.FAIL
        elif geometry is not None:
            strength, receipts, failed, held = check_haunch_station_strength(
                member, haunch, geometry
            )
            bend_checks, bend_issues = check_haunch_bend_restraint(
                member, haunch, geometry
            )
            data["strength"] = strength
            data["haunch"].update(receipts, bend_checks=bend_checks)
            issues.extend([*failed, *held, *bend_issues])
            status = EngineeringStatus(strength["ultimate_status"])
            if any(issue.code.endswith("_FAIL") for issue in bend_issues):
                status = EngineeringStatus.FAIL
            elif bend_issues and status is EngineeringStatus.PASS:
                status = EngineeringStatus.HOLD
            if status is EngineeringStatus.PASS:
                zones = tuple(
                    LinkPlacementZone(
                        f"link-{index}",
                        link.bar_mark,
                        link.station_mm,
                        link.station_mm,
                        member.link_spacing_mm,
                        True,
                        True,
                    )
                    for index, link in enumerate(haunch.links, 1)
                )
                schedule = _create_bound_bbs(request, geometry.paths, zones)
                if schedule.engineering is EngineeringState.PASS:
                    data["bbs"] = schedule.to_dict()
                else:
                    status = EngineeringStatus.HOLD
                    issues.extend(
                        StructuralIssueV1(
                            issue.code, issue.field_or_location or "bbs", issue.message
                        )
                        for issue in schedule.diagnostics
                    )
    result = canonical_family_result(
        request,
        data,
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Ordinary constant-width haunch with continuous corner bars and nominal placement checks.",
            "Checks supplied station actions. Joint obstructions and field tolerances require project evidence.",
        ),
        provenance=(
            "IS 456:2000 §§26.2.1–4, 26.5.1–3 and 40.1.1–40.4.",
            "SP 34 §§8.10.2 and 8.11, vertical individual closed links.",
        ),
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=tuple(issues),
            freshness_status=(
                FreshnessStatus.STALE if stale else FreshnessStatus.CURRENT
            ),
        ),
    )


def _check_physical_flange_detailing(
    request: BeamContinuousDetailingInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    member, web, detail = request.member, request.link_detail, request.physical_flange
    status = EngineeringStatus.HOLD
    stale = member.analysis_revision != member.current_analysis_revision
    engineering: dict[str, Any] = {}
    assembly: dict[str, Any] = {
        "request": {
            "member_id": member.member_id,
            "beam": {
                "width_mm": member.width_mm,
                "depth_mm": member.depth_mm,
                "flange": (
                    member.flange.model_dump(mode="json")
                    if isinstance(member, BeamLayeredContinuousCheckRequestV1)
                    and member.flange
                    else None
                ),
            },
            "supports": [
                support.model_dump(mode="json") for support in member.supports
            ],
        },
        "engineering": engineering,
        "pieces": [],
        "owners_by_mark": {},
    }
    data: dict[str, Any] = {
        "strength": {
            "rows": [],
            "governing_rows": {},
            "ultimate_status": "HOLD",
            "serviceability_status": "NOT_EVALUATED",
        },
        "paths": None,
        "bbs": None,
        "physical_flange": assembly,
    }
    issues: list[StructuralIssueV1] = []
    if stale:
        issues.append(
            StructuralIssueV1(
                "BEAM_ANALYSIS_STALE",
                "member.analysis_revision",
                "Supply the current signed beam actions.",
            )
        )
    elif not (
        isinstance(member, BeamLayeredContinuousCheckRequestV1)
        and member.flange is not None
        and member.flange.kind == "t_beam"
        and member.flange.monolithic
        and math.isclose(
            member.flange.left_overhang_mm,
            member.flange.right_overhang_mm,
            rel_tol=0,
            abs_tol=1e-8,
        )
        and member.fck_nmm2 == 25
        and member.fy_nmm2 == member.link_fy_nmm2 == 415
        and member.depth_mm <= 750
        and member.straight_bars is not None
        and isinstance(detail, BeamPhysicalFlangeDetailV1)
        and web is not None
        and web.restraint_link is None
        and request.cutoff is None
        and request.lap is None
        and request.haunch == "not_requested"
        and request.link_zones == "not_requested"
        and request.placement_envelope == "not_requested"
    ):
        issues.append(
            flange_issue(
                "BASIS_HELD",
                "member",
                "Supply the ordinary M25 and Fe415 monolithic T beam, complete web cage and separate physical flange evidence.",
            )
        )
    elif detail.slab_strip is None:
        issues.append(
            flange_issue(
                "STRIP_ACTIONS_HELD",
                "slab_strip",
                "Supply the current physical transverse slab strip and its signed load basis.",
            )
        )
    elif (
        detail.analysis_revision != member.analysis_revision
        or detail.reinforcement_revision != member.reinforcement_revision
        or detail.slab_strip.geometry_revision != detail.geometry_revision
    ):
        stale = True
        issues.append(
            flange_issue(
                "STRIP_REVISION_HELD",
                "slab_strip.geometry_revision",
                "The beam, reinforcement and slab strip must bind to the current geometry and analysis.",
            )
        )
    else:
        basis, basis_issues = bind_physical_flange_actions(member, detail)
        engineering["basis"] = basis
        issues.extend(basis_issues)
        if not issues:
            slot = detail.placement.maximum_assembly_translation_per_axis_mm
            strip, strip_issues = check_physical_flange_strip(
                detail.slab_strip,
                member,
                placement_tolerance_mm=slot,
            )
            anchorage, anchor_issues = check_physical_flange_anchorage(
                member, detail, basis
            )
            engineering.update(strip=strip, anchorage=anchorage)
            issues.extend((*strip_issues, *anchor_issues))
        if not issues:
            geometry, placement_issues = resolve_physical_flange_geometry(
                member,
                detail,
                web_first=web.first_station_mm,
                web_last=web.last_station_mm,
                web_internal_radius=web.internal_bend_radius_mm,
                web_tail=web.hook_vertex_leg_mm,
                web_hook_shift=web.hook_plane_offset_mm,
                source_hash=_input_hash(request),
                stock_length_mm=request.stock_length_mm,
            )
            issues.extend(placement_issues)
            if geometry is not None:
                data["paths"] = geometry.paths.to_dict()
                engineering["geometry"] = geometry.placement
                assembly["pieces"] = geometry.pieces
                assembly["request"][
                    "slab_edge_x_mm"
                ] = detail.slab_strip.transverse_edge_x_mm
                assembly["owners_by_mark"] = {
                    p["mark"]: p["owner"] for p in geometry.pieces
                }
                if not issues:
                    strength, summary, strength_issues = check_physical_flange_strength(
                        member, detail
                    )
                    engineering["strength"] = summary
                    issues.extend(strength_issues)
                    if strength:
                        data["strength"] = strength
                        if strength["ultimate_status"] == "FAIL":
                            status = EngineeringStatus.FAIL
                    if not issues:
                        schedule = _create_bound_bbs(
                            request, geometry.paths, geometry.zones
                        )
                        if schedule.engineering is EngineeringState.PASS:
                            data["bbs"] = schedule.to_dict()
                            status = EngineeringStatus.PASS
                        else:
                            issues.extend(
                                StructuralIssueV1(
                                    item.code,
                                    item.field_or_location or "bbs",
                                    item.message,
                                )
                                for item in schedule.diagnostics
                            )
        if any(issue.code.endswith("_FAIL") for issue in issues):
            status = EngineeringStatus.FAIL
    result = canonical_family_result(
        request,
        data,
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Ordinary monolithic symmetric T beam, two equal pinned-end spans and a perpendicular two-span slab strip.",
            "Local placement opening covers the submitted beam and slab assembly. Joint reinforcement and field obstructions require project evidence.",
            "Member serviceability and torsion are outside this supplied ULS profile.",
        ),
        provenance=("IS 456:2000 §§23.1.1–2, 26.2–5, 38 and 40, including Table 19.",),
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=tuple(issues),
            freshness_status=(
                FreshnessStatus.STALE if stale else FreshnessStatus.CURRENT
            ),
        ),
    )


def _check_layered_cage(
    request: BeamContinuousDetailingInputV1,
    checked: BeamContinuousCheckResultV1,
    cage: BeamLayeredCageDetailV1,
) -> tuple[dict[str, Any], EngineeringStatus, tuple[StructuralIssueV1, ...]]:
    member, link = request.member, request.link_detail
    if (
        not isinstance(member, BeamLayeredContinuousCheckRequestV1)
        or member.flange is not None
        or member.straight_bars is None
        or link is None
        or link.restraint_link is not None
        or request.cutoff is not None
        or request.lap is not None
        or request.link_zones != "not_requested"
        or request.placement_envelope != "not_requested"
        or request.haunch != "not_requested"
        or request.physical_flange != "not_requested"
    ):
        return (
            {},
            EngineeringStatus.HOLD,
            (
                StructuralIssueV1(
                    "BEAM.EDIT_CAGE_SCOPE_HELD",
                    "layered_cage",
                    "The placement edit needs an ordinary two-layer rectangular cage with uninterrupted bars and one uniform outer hoop grid.",
                ),
            ),
        )
    if cage.placement is None:
        return (
            {},
            EngineeringStatus.HOLD,
            (
                StructuralIssueV1(
                    "BEAM.EDIT_PLACEMENT_HELD",
                    "layered_cage.placement",
                    "Supply cover, form opening, placement tolerances and concrete consolidation access.",
                ),
            ),
        )
    inset = member.clear_cover_mm + member.link_diameter_mm / 2
    bounds = (inset, inset, member.width_mm - inset, member.depth_mm - inset)
    placement, issues = check_layered_cage_placement(
        member,
        link_bounds_mm=bounds,
        internal_bend_radius_mm=link.internal_bend_radius_mm,
        hook_vertex_leg_mm=link.hook_vertex_leg_mm,
        hook_plane_offset_mm=link.hook_plane_offset_mm,
        placement=cage.placement,
        cross_tie=cage.cross_tie,
    )
    evidence = {"placement": placement}
    if issues:
        status = (
            EngineeringStatus.HOLD
            if any(issue.code == "BEAM.EDIT_CAGE_SCOPE_HELD" for issue in issues)
            else EngineeringStatus.FAIL
        )
        return evidence, status, issues
    if checked.ultimate_status != "PASS":
        return evidence, EngineeringStatus(checked.ultimate_status), ()
    hoop_edge = (
        member.link_diameter_mm + cage.placement.link_diameter_allowance_mm
    ) / 2 + cage.placement.link_station_tolerance_mm
    first = link.first_station_mm - hoop_edge
    last = (
        link.last_station_mm
        + link.hook_plane_offset_mm
        + cage.placement.closed_hook_plane_offset_tolerance_mm
        + hoop_edge
    )
    if cage.cross_tie is not None:
        tie = cage.cross_tie
        tie_edge = (
            tie.diameter_mm + cage.placement.link_diameter_allowance_mm
        ) / 2 + cage.placement.link_station_tolerance_mm
        first = min(first, link.first_station_mm + tie.station_offset_mm - tie_edge)
        last = max(last, link.last_station_mm + tie.station_offset_mm + tie_edge)
    left, _, right = member.supports
    if (
        min(first - left.left_face_mm, right.right_face_mm - last)
        < cage.placement.required_cover_mm
    ):
        return (
            evidence,
            EngineeringStatus.FAIL,
            (
                StructuralIssueV1(
                    "BEAM.EDIT_LINK_END_COVER",
                    "link_detail",
                    "The hoop and cross-tie grids require end cover under the declared station tolerances.",
                ),
            ),
        )
    actions, status, issue = check_layered_edit_actions(
        member,
        checked,
        cage.placement,
        placement["max_pitch_under_tolerance_mm"],
        cage.service,
    )
    if cage.cross_tie is not None:
        evidence["cross_tie_mark"] = (
            f"{member.member_id}-CT{cage.cross_tie.diameter_mm:g}"
        )
    return {**evidence, **actions}, status, (issue,) if issue is not None else ()


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
    first-span outer-layer bottom cutoff is supported. Layered rectangular
    cages also admit a second-span cutoff toward the interior support.
    Rectangular, symmetric T and right-flanged L sections admit one
    separated straight outer-bottom tension lap. A layered rectangle can
    use the second clear span with transfer toward decreasing x.
    The ordinary layered rectangle with two checked link grids and declared
    placement limits also supports one first-span top tension lap near the
    interior support.
    One straight rectangular four-corner cage can use declared link pitch
    zones with a single ordinary closed link shape and signed transition rows.
    The ordinary four-corner haunch uses resolved bottom bends, individual
    link depths and the signed varying-depth shear check.
    A layered rectangular cage with declared construction limits checks
    the outer seats, supported middle cross-ties and form placement.

    Provenance
    ----------
    Uses the checked supplied station actions, physical path and BBS owners.
    """
    require_request_type(request, BeamContinuousDetailingInputV1)
    cage = request.layered_cage
    if cage == "not_requested":
        if request.physical_flange != "not_requested":
            return _check_physical_flange_detailing(request)
        if request.haunch != "not_requested":
            return _check_haunch_detailing(request)
    member = request.member
    varied_requested = request.link_zones != "not_requested"
    zones: tuple[ResolvedBeamLinkZone, ...] = ()
    basis_issue = None
    if (
        varied_requested
        and member.analysis_revision == member.current_analysis_revision
    ):
        zones, basis_issue = _varied_link_basis(request)
    if zones:
        # At a shared station the larger adjacent pitch is the exact
        # governing shear resistance for the same link shape and cage.
        pitches = {
            station.x_mm: max(
                (
                    zone.placement.spacing_mm
                    for zone in zones
                    if zone.placement.start_station_x_mm - 1e-8
                    <= station.x_mm
                    <= zone.placement.end_station_x_mm + 1e-8
                ),
                default=member.link_spacing_mm,
            )
            for station in member.stations
        }
        checked = _check_station_beam(member, link_spacing_by_station=pitches)
    else:
        checked = check_continuous_beam(member)
    identity = checked.result_envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    data: dict[str, Any] = {"strength": checked.to_dict(), "paths": None, "bbs": None}
    issues = []
    status = EngineeringStatus(checked.ultimate_status)
    if basis_issue is not None:
        issues.append(basis_issue)
        status = (
            EngineeringStatus.FAIL
            if basis_issue.code == "BEAM.LINK_ZONE_PLACEMENT_FAIL"
            else EngineeringStatus.HOLD
        )
    if zones:
        assert isinstance(member, BeamContinuousCheckRequestV1)
        data["link_zones"], pitch_issues = check_varied_link_strength(checked, zones)
        # No uniform shear capacities apply to the zoned member as a whole.
        data["strength"]["shear_sections"] = {}
        issues.extend(pitch_issues)
        if pitch_issues:
            status = EngineeringStatus.FAIL
        transition_issue = zone_transition_actions_issue(member, zones)
        if transition_issue is not None:
            issues.append(transition_issue)
            if status is EngineeringStatus.PASS:
                status = EngineeringStatus.HOLD
    cutoff_bounds = None
    lap_pieces = None
    source_hash = identity.input_hash
    placement_requested = request.placement_envelope != "not_requested"
    layered = isinstance(request.member, BeamLayeredContinuousCheckRequestV1)
    flange = (
        request.member.flange
        if isinstance(request.member, BeamLayeredContinuousCheckRequestV1)
        else None
    )
    if isinstance(cage, BeamLayeredCageDetailV1):
        source_hash = _input_hash(request)
        if checked.result_envelope.freshness_status is FreshnessStatus.CURRENT:
            evidence, cage_status, cage_issues = _check_layered_cage(
                request, checked, cage
            )
            if status is not EngineeringStatus.FAIL:
                status = cage_status
            data["layered_cage"] = evidence
            issues.extend(cage_issues)
    elif (
        request.lap
        and flange is not None
        and (
            (flange.kind == "l_beam" and flange.left_overhang_mm > 0)
            or (
                flange.kind == "t_beam"
                and not math.isclose(
                    flange.left_overhang_mm,
                    flange.right_overhang_mm,
                    rel_tol=0,
                    abs_tol=1e-6,
                )
            )
        )
    ):
        issues.append(
            StructuralIssueV1(
                "BEAM.LAYERED_BAR_DETAIL_HELD",
                "lap",
                "The layered lap profile covers rectangles, symmetric T cages and right-flanged L cages.",
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
        cutoff_bounds, cutoff, cutoff_issues, status = _check_bottom_cutoff(
            request, checked
        )
        data["cutoff"] = cutoff
        issues.extend(cutoff_issues)
    elif status is EngineeringStatus.PASS and request.lap is not None:
        lap_pieces, lap, lap_issues, status = _check_lap(request, checked)
        data["lap"] = lap
        issues.extend(lap_issues)
    if cage == "not_requested" and (
        request.cutoff or request.lap or placement_requested or varied_requested
    ):
        source_hash = semantic_hash(
            "beam_detailing_source",
            {
                "strength": identity.input_hash,
                "cutoff": (
                    request.cutoff.model_dump(mode="json") if request.cutoff else None
                ),
                "lap": request.lap.model_dump(mode="json") if request.lap else None,
                "link": (
                    request.link_detail.model_dump(mode="json", exclude_none=True)
                    if request.link_detail
                    else None
                ),
                **(
                    {
                        "placement_envelope": (
                            request.placement_envelope.model_dump(mode="json")
                            if isinstance(
                                request.placement_envelope, BeamLapPlacementEnvelopeV1
                            )
                            else None
                        )
                    }
                    if placement_requested
                    else {}
                ),
                **(
                    {
                        "link_zones": [
                            zone.model_dump(mode="json") for zone in request.link_zones
                        ]
                    }
                    if isinstance(request.link_zones, tuple)
                    else {}
                ),
            },
        )
    if status is EngineeringStatus.PASS:
        restraint = data.get("lap", {}).get("compression_restraint")
        inputs = _physical_paths(request, source_hash, cutoff_bounds, lap_pieces, zones)
        if inputs is None:
            status = EngineeringStatus.HOLD
            if restraint is not None:
                restraint["verified"] = False
            issues.append(
                StructuralIssueV1(
                    "BEAM.DETAIL_LINK_BASIS_HELD",
                    "link_detail",
                    "Supply a current link shape and full member placement grid.",
                )
            )
        else:
            paths_request, link_requests = inputs
            if isinstance(cage, BeamLayeredCageDetailV1) and cage.cross_tie is not None:
                assert isinstance(member, BeamLayeredContinuousCheckRequestV1)
                stations = tuple(
                    path.nodes[0].point.station_x_mm
                    for path in paths_request.paths
                    if path.role is BarPathRole.TRANSVERSE_LINK
                )
                cross_ties = centre_cross_tie_paths(member, cage.cross_tie, stations)
                paths_request = replace(
                    paths_request, paths=(*paths_request.paths, *cross_ties)
                )
            fit = check_reinforcement_arrangement(link_requests[0].arrangement)
            paths = resolve_bar_paths(paths_request)
            links = tuple(check_closed_link_detail(detail) for detail in link_requests)
            data.update(
                arrangement=fit.to_dict(),
                paths=paths.to_dict(),
                link_check=links[0].to_dict(),
            )
            if zones:
                data["link_zones"]["shape_checks"] = {
                    zone.placement.zone_id: leaf.to_dict()
                    for zone, leaf in zip(zones, links, strict=True)
                }
            elif len(links) == 2:
                data["restraint_link_check"] = links[1].to_dict()
            for leaf in (fit, paths, *links):
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
            if placement_requested and status is EngineeringStatus.PASS:
                placement, placed_restraint, placement_issues = _check_lap_placement(
                    request,
                    checked,
                    lap_pieces,
                    data.get("lap", {}),
                    link_requests,
                )
                data["placement"] = placement
                status = EngineeringStatus(placement["status"])
                issues.extend(placement_issues)
                if placed_restraint is not None:
                    restraint = placed_restraint
                    data["lap"]["compression_restraint"] = restraint
            if restraint is not None and status is not EngineeringStatus.PASS:
                restraint["verified"] = False
            if (
                status is EngineeringStatus.PASS
                and restraint is not None
                and not restraint["verified"]
            ):
                status = EngineeringStatus.HOLD
                issues.append(
                    StructuralIssueV1(
                        "BEAM.LAP_COMPRESSION_RESTRAINT_HELD",
                        "lap",
                        "The closed link has not demonstrated effective lateral restraint for the credited compression bars in both transfer layouts.",
                    )
                )
            if status is EngineeringStatus.PASS:
                splice = None
                if lap_pieces is not None:
                    splice = SpliceRecord(
                        "top-lap" if lap.get("tension_face") == "top" else "bottom-lap",
                        ScheduleSpliceKind.LAP,
                        (lap["start_station_mm"] + lap["end_station_mm"]) / 2,
                        data["lap"]["lap_result"]["result_id"],
                    )
                schedule = _schedule(request, paths, link_requests, splice, zones)
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
    lap_scope = (
        "The layered rectangular top lap uses signed hogging and checked placement limits."
        if data.get("lap", {}).get("tension_face") == "top"
        else (
            "Right-flanged L cages admit one separated straight outer-bottom tension lap."
            if request.lap and flange is not None and flange.kind == "l_beam"
            else "Rectangular and symmetric T cages admit one separated straight outer-bottom tension lap."
        )
    )
    result = canonical_family_result(
        request,
        data,
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Only the supplied strength and anchorage rows and the declared physical layout are checked.",
            (
                "Prismatic web cage with straight layers and one optional outer-layer bottom cutoff or lap. "
                f"{lap_scope} Slab reinforcement and equilibrium torsion need separate evidence."
                if layered and cage == "not_requested"
                else (
                    "Seated outer corner bars, supported middle bars and a two-layer section with the declared placement limits."
                    if isinstance(cage, BeamLayeredCageDetailV1)
                    else (
                        "Ordinary uninterrupted corner bars with one two-hook link mark on declared pitch zones."
                        if varied_requested
                        else "Ordinary straight bars, one optional first-span bottom cutoff or separated bottom lap, and one uniform two-hook link mark."
                    )
                )
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
    if "physical_flange" in data:
        return render_physical_flange_svg(result)
    request = result.request
    assert isinstance(request, BeamContinuousDetailingInputV1)
    member = request.member
    if isinstance(request.haunch, BeamHaunchDetailV1):
        identity = result.envelope.result_identity
        detail = request.link_detail
        assert isinstance(member, BeamContinuousCheckRequestV1) and detail is not None
        return render_haunch_svg(
            member,
            request.haunch,
            data["haunch"],
            input_hash=identity.input_hash if identity and identity.input_hash else "",
            path_id=data["paths"]["result_id"],
            bend_radius_mm=detail.internal_bend_radius_mm + member.link_diameter_mm / 2,
        )
    geometry = data["paths"]["outputs"]["reinforcement_schedule"]
    link_zones = data.get("link_zones", {}).get("zones", ())
    left, support, right = member.supports
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
    reverse_cutoff = cutoff.get("cutoff_direction") == AnchorageDirection.DECREASING_X
    lap = (
        data.get("lap", {})
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else {}
    )
    reverse_lap = lap.get("lap_direction") == AnchorageDirection.DECREASING_X
    lap_colors = (
        {lap["bar_id"]: "#92400e", lap["partner_bar_id"]: "#0f766e"}
        if reverse_lap or "web_only_anchor_moment_knm" in lap or "placement" in data
        else {}
    )
    lap_lines = []
    bars = []
    termination = ""
    restraint_mark = (
        f"{member.member_id}-L{member.link_diameter_mm:g}-restraint"
        if request.link_detail and request.link_detail.restraint_link
        else None
    )
    centre_cross_mark = data.get("layered_cage", {}).get("cross_tie_mark")
    section_note = ""
    if restraint_mark is not None:
        detail = request.link_detail
        assert detail is not None and detail.restraint_link is not None
        section_note = (
            '<text x="18" y="273" font-size="17" fill="#334155">'
            f"Links @ {member.link_spacing_mm:g} mm · outer in grey · "
            f"restraint in purple at +{detail.restraint_link.station_offset_mm:g} mm</text>"
            '<text x="18" y="295" font-size="17" fill="#334155">'
            "Link shapes are projected onto each bar section. See elevation for placement.</text>"
        )
    if centre_cross_mark is not None:
        assert isinstance(request.layered_cage, BeamLayeredCageDetailV1)
        tie = request.layered_cage.cross_tie
        assert tie is not None
        section_note = (
            '<text x="18" y="273" font-size="17" fill="#334155">'
            f"Outer hoops @ {member.link_spacing_mm:g} mm · "
            f"centre cross-ties @ {member.link_spacing_mm:g} mm, +{tie.station_offset_mm:g} mm</text>"
            '<text x="18" y="295" font-size="17" fill="#334155">'
            "Purple shows the cross-tie projected onto the web section.</text>"
        )
    for item in geometry["paths"]:
        path_id = html.escape(item["bar_id"], quote=True)
        segments = item["segments"]
        x1 = segments[0]["start"]["station_x_mm"]
        mark_attribute = ""
        if item["role"] == "transverse_link":
            x2, y1, y2 = x1, member.clear_cover_mm, depth - member.clear_cover_mm
            color = (
                "#7e22ce"
                if item["bar_mark"] in (restraint_mark, centre_cross_mark)
                else "#64748b"
            )
            if item["bar_mark"] == centre_cross_mark:
                hook_limits = tuple(
                    (
                        segment["bend_centre"]["section_y_from_top_mm"],
                        segment["bend_radius_mm"],
                    )
                    for segment in segments
                    if segment["bend_centre"] is not None
                )
                y1 = min(centre - radius for centre, radius in hook_limits)
                y2 = max(centre + radius for centre, radius in hook_limits)
                mark_attribute = (
                    f' data-cross-tie="{html.escape(centre_cross_mark, quote=True)}"'
                )
        else:
            x2 = segments[-1]["end"]["station_x_mm"]
            y1 = y2 = segments[0]["start"]["section_y_from_top_mm"]
            color = "#1e40af"
        line = (
            f'<line data-bar-id="{path_id}" data-layer="{item["layer"]}"{mark_attribute} '
            f'x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
        )
        if item["bar_id"] == cutoff.get("bar_id"):
            # Bars in the same layer overlap in elevation. Draw the cut bar last.
            cut_x = x1 if reverse_cutoff else x2
            termination = (
                line + 'stroke="#b45309" stroke-width="14"/>'
                f'<path d="M{cut_x:g} -35 V{y2:g}" stroke="#b45309" stroke-width="7" stroke-dasharray="24 15"/>'
                f'<circle cx="{cut_x:g}" cy="{y2:g}" r="23" fill="#b45309"/>'
                f'<text x="{cut_x:g}" y="-68" text-anchor="middle" font-size="112" '
                f'fill="#92400e">{path_id} ends at {cut_x:g} mm</text>'
            )
        elif item["bar_id"] in lap_colors:
            color = lap_colors[item["bar_id"]]
            first = item["bar_id"] == lap["bar_id"]
            dash = "" if first else ' stroke-dasharray="42 22"'
            lap_tip_x = x2 if first != reverse_lap else x1
            lap_lines.append(
                line + f'stroke="{color}" stroke-width="14"{dash}/>'
                f'<circle cx="{lap_tip_x:g}" cy="{y1:g}" r="18" fill="{color}"/>'
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
    elevation_depth = depth + (300 if link_zones else 140)
    elevation_view = (
        f"{start - 40:g} {-top:g} {end - start + 80:g} {elevation_depth + top:g}"
    )
    zone_lines = []
    for zone in link_zones:
        x1, x2 = zone["start_station_mm"], zone["end_station_mm"]
        pitch = zone["spacing_mm"]
        name = html.escape(zone["zone_id"], quote=True)
        first, last = (
            "inclusive" if zone[key] else "exclusive"
            for key in ("include_start", "include_end")
        )
        font_size = min(112, (x2 - x1) / 14)
        interval = f"{'[' if zone['include_start'] else '('}{x1:g}, {x2:g}{']' if zone['include_end'] else ')'}"
        zone_lines.append(
            f'<g data-link-zone="{name}" data-start-mm="{x1:g}" data-end-mm="{x2:g}" '
            f'data-spacing-mm="{pitch:g}" data-start="{first}" data-end="{last}">'
            f'<path d="M{x1:g} {depth + 130:g} v65 H{x2:g} v-65" '
            'fill="none" stroke="#475569" stroke-width="6"/>'
            f'<text x="{(x1 + x2) / 2:g}" y="{depth + 275:g}" text-anchor="middle" '
            f'font-size="{font_size:g}" fill="#334155">{interval} mm · Ø{member.link_diameter_mm:g} @ {pitch:g} mm</text></g>'
        )
    elevation = (
        f'<rect x="{start:g}" width="{end - start:g}" height="{depth:g}" fill="#f1f5f9" stroke="#0f172a"/>'
        + support_lines
        + lap_band
        + "".join(bars)
        + termination
        + "".join(lap_lines)
        + "".join(zone_lines)
    )
    drawing_label = "elevation"
    if isinstance(member, BeamLayeredContinuousCheckRequestV1) or link_zones:
        drawing_label = "drawing"
        drawing_view = f"0 0 1200 {692 if section_note else 650}"
        lap_legend = (
            '<text x="334" y="28" font-size="17" fill="#92400e">Lap-I · original</text>'
            '<text x="500" y="28" font-size="17" fill="#0f766e">Lap-J · partner</text>'
            if lap_colors
            else ""
        )
        link_legend = (
            '<text x="500" y="28" font-size="17" fill="#334155">'
            f'{html.escape(link_zones[0]["bar_mark"])} · one closed link shape</text>'
            if link_zones
            else ""
        )
        panels = (
            '<text x="18" y="28" font-size="22">Member elevation</text>'
            f"{lap_legend}{link_legend}"
            f'<svg x="0" y="44" width="1200" height="230" viewBox="{elevation_view}">'
            f"{elevation}</svg>{section_note}"
        )
        if cutoff:
            theoretical, cut_at = (
                cutoff["theoretical_station_mm"],
                cutoff["termination_station_mm"],
            )
            cut_side = "before" if reverse_cutoff else "after"
            panels += _section_panel(
                member,
                request.link_detail,
                geometry["paths"],
                station_mm=theoretical,
                panel_width=600,
                label=f"Section at {theoretical:g} mm · before termination",
            )
            panels += _section_panel(
                member,
                request.link_detail,
                geometry["paths"],
                station_mm=cut_at,
                at_left_limit=reverse_cutoff,
                panel_x=600,
                panel_width=600,
                label=f"Section just {cut_side} {cut_at:g} mm · continuing cage",
            )
        elif lap:
            entering_face = support.right_face_mm if reverse_lap else left.right_face_mm
            views = (
                ((entering_face + lap["start_station_mm"]) / 2, "before lap"),
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
        elif link_zones:
            panels += _section_panel(
                member,
                request.link_detail,
                geometry["paths"],
                label=(
                    f"Cross-section · {member.width_mm:g} × {member.depth_mm:g} mm"
                    f" · {member.clear_cover_mm:g} mm cover to links"
                ),
            )
        else:
            panels += _section_panel(
                member,
                request.link_detail,
                geometry["paths"],
                centre_cross_mark=centre_cross_mark,
            )
    else:
        drawing_view, panels = elevation_view, elevation
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{drawing_view}" role="img">
<title>{html.escape(member.member_id)} checked continuous beam {drawing_label}</title>
<desc>Input {identity.input_hash if identity else ""}. Path {data["paths"]["result_id"]}. Review drawing.</desc>
{panels}</svg>"""


def _section_panel(
    member: BeamContinuousCheckRequestV1 | BeamLayeredContinuousCheckRequestV1,
    link: BeamOrdinaryLinkDetailV1 | None,
    paths: list[dict[str, Any]],
    *,
    station_mm: float | None = None,
    at_left_limit: bool = False,
    panel_x: int = 0,
    panel_width: int = 1200,
    label: str = "Physical cross-section · web cage",
    lap_colors: dict[str, str] | None = None,
    centre_cross_mark: str | None = None,
) -> str:
    """Draw the web cage at the selected side of the section station."""
    assert link is not None
    flange = (
        member.flange
        if isinstance(member, BeamLayeredContinuousCheckRequestV1)
        else None
    )
    width, depth = member.width_mm, member.depth_mm
    left = flange.left_overhang_mm if flange else 0.0
    right = flange.right_overhang_mm if flange else 0.0
    flange_depth = flange.thickness_mm if flange else 0.0
    flange_left = 0.0 - left
    if flange:
        outline = (
            f"M{flange_left:g} 0 H{width + right:g} V{flange_depth:g} H{width:g} "
            f"V{depth:g} H0"
        )
        if left > 0:
            outline += f" V{flange_depth:g} H{flange_left:g}"
        outline += " Z"
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
        if station_mm is not None:
            start_mm = point["station_x_mm"]
            end_mm = segments[-1]["end"]["station_x_mm"]
            present = (
                start_mm < station_mm <= end_mm
                if at_left_limit
                else start_mm <= station_mm < end_mm
            )
            if not present:
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
    inner_shape = ""
    section_offset = 0
    projection = ""
    if link.restraint_link is not None:
        inner = link.restraint_link
        section_offset = 42
        projection = ' data-link-display="projected"'
        inner_shape = (
            f'<rect data-outline="restraint-link"{projection} x="{inner.left_centre_x_mm:g}" '
            f'y="{inset:g}" width="{inner.right_centre_x_mm - inner.left_centre_x_mm:g}" '
            f'height="{depth - 2 * inset:g}" rx="{radius:g}" fill="none" '
            f'stroke="#7e22ce" stroke-width="{member.link_diameter_mm:g}"/>'
        )
    if centre_cross_mark is not None:
        path = next(item for item in paths if item["bar_mark"] == centre_cross_mark)
        inner_shape += project_centre_cross_tie(path)
        section_offset = 42
    return f"""<text x="{panel_x + 18}" y="{302 + section_offset}" font-size="22">{html.escape(label)}</text>
<svg data-view="section"{station} x="{panel_x}" y="{318 + section_offset}" width="{panel_width}" height="320"
 viewBox="{-left - 35:g} -35 {width + left + right + 70:g} {depth + 70:g}">
<path data-outline="concrete" d="{outline}" fill="#f1f5f9" stroke="#0f172a" stroke-width="3"/>
<rect data-outline="web-link"{projection} x="{inset:g}" y="{inset:g}" width="{width - 2 * inset:g}"
 height="{depth - 2 * inset:g}" rx="{radius:g}" fill="none" stroke="#64748b" stroke-width="{member.link_diameter_mm:g}"/>{inner_shape}
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
    owners = result.calculation.get("physical_flange", {}).get("owners_by_mark", {})
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
            *(("owner",) if owners else ()),
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
                *((owners[row["bar_mark"]],) if owners else ()),
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
    if "physical_flange" in result.calculation:
        return render_physical_flange_report(
            result, drawing=svg, schedule=bbs, current=current_match
        )
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
        if cutoff.get("cutoff_direction") == AnchorageDirection.DECREASING_X:
            cutoff_html += (
                f"<p>Development from {cutoff['theoretical_station_mm']:g} mm "
                "toward decreasing x.</p>"
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
                f"<h2>Separated {lap.get('tension_face', 'bottom')} lap</h2><p>{html.escape(lap['bar_id'])} and "
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
                flange = request.member.flange
                if flange is not None and flange.kind == "l_beam":
                    width = request.member.width_mm + flange.right_overhang_mm
                    lap_html += (
                        f"<p>L beam with a {flange.right_overhang_mm:g} mm right overhang "
                        f"and a {flange.thickness_mm:g} mm flange. Physical width {width:g} mm.</p>"
                    )
    issues = "".join(f"<li>{html.escape(item.message)}</li>" for item in result.issues)
    limits = "".join(f"<li>{html.escape(item)}</li>" for item in result.limitations)
    status = result.engineering_status.value if current_match else "HOLD · stale result"
    if not current_match:
        strength = {"ultimate_status": "HOLD", "serviceability_status": "HOLD"}
        governance, cutoff_html, lap_html = "", "", ""
    bar_edit = result.calculation.get("bar_edit")
    placement = result.calculation.get("placement") if current_match else None
    placement_html = _lap_placement_report(placement) if placement else ""
    zones = result.calculation.get("link_zones") if current_match else None
    zone_html = _varied_link_report(zones) if zones else ""
    haunch = result.calculation.get("haunch") if current_match else None
    haunch_html = render_haunch_report(haunch) if haunch is not None else ""
    layered_cage = result.calculation.get("layered_cage") if current_match else None
    cage_html = (
        render_layered_cage_report(
            layered_cage,
            analysis_revision=request.member.analysis_revision,
            reinforcement_revision=request.member.reinforcement_revision,
        )
        if layered_cage and isinstance(request, BeamContinuousDetailingInputV1)
        else ""
    )
    governing_title = (
        "Governing action rows"
        if zones or haunch is not None
        else "Governing baseline action rows"
    )
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
<h2>{governing_title}</h2><ul>{governance}</ul>
{edit_html}{cutoff_html}{lap_html}{section_html}{placement_html}{zone_html}{haunch_html}{cage_html}{svg}{report_bbs}<ul>{issues}{limits}</ul></html>"""


def _varied_link_report(data: dict[str, Any]) -> str:
    rows = []
    for zone in data["zones"]:
        limits = (
            f"{'[' if zone['include_start'] else '('}{zone['start_station_mm']:g}, "
            f"{zone['end_station_mm']:g}{']' if zone['include_end'] else ')'}"
        )
        evidence = ""
        if "governing_row_id" in zone:
            evidence = (
                f"{html.escape(zone['governing_row_id'])} · "
                f"{zone['governing_shear_kn']:.3f} kN / {zone['capacity_kn']:.3f} kN"
            )
        rows.append(
            f"<tr><th>{html.escape(zone['zone_id'])}</th><td>{limits}</td>"
            f"<td>{zone['spacing_mm']:g}</td><td>{zone['quantity']}</td>"
            f"<td>{html.escape(zone['bar_mark'])}</td><td>{evidence}</td></tr>"
        )
    transitions = "".join(
        f"<tr><th>{html.escape(row['row_id'])}</th><td>{row['station_mm']:g}</td>"
        f"<td>{row['shear_kn']:.3f}</td><td>{html.escape(row['owner_zone_id'])}</td>"
        f"<td>{html.escape(side['zone_id'])}</td><td>{side['spacing_mm']:g}</td>"
        f"<td>{side['capacity_kn']:.3f}</td><td>{side['shear_ratio']:.3f}</td></tr>"
        for row in data["transitions"]
        for side in row["adjacent"]
    )
    return (
        "<h2>Varied link zones</h2>"
        f"<p>Maximum pitch {data['maximum_pitch_mm']:g} mm for shear and compression-bar restraint.</p>"
        "<table><thead><tr><th>Zone</th><th>Owned interval (mm)</th>"
        "<th>Pitch (mm)</th><th>Quantity</th><th>Bar mark</th><th>Governing shear</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        "<h3>Checks at both sides of each transition</h3>"
        "<table><thead><tr><th>Row ID</th><th>Station (mm)</th><th>Shear (kN)</th>"
        "<th>Link owner</th><th>Checked zone</th><th>Pitch (mm)</th>"
        "<th>Resistance (kN)</th><th>Utilization</th></tr></thead>"
        f"<tbody>{transitions}</tbody></table>"
    )


def _lap_placement_report(placement: dict[str, Any]) -> str:
    details = f"<h2>Placement envelope</h2><p>Placement {html.escape(placement['status'])}.</p>"
    if "source_reference" in placement:
        details += f"<p>{html.escape(placement['source_reference'])}</p>"
    if "returns" in placement:
        gap = min(
            min(row)
            for row in placement["minimum_horizontal_clearances_mm"].values()
            if row
        )
        across, along = placement["minimum_clear_concrete_access_mm"]
        clearance = min(
            row["min_clearance_mm"] for row in placement["returns"].values()
        )
        details += (
            f"<p>Minimum bend clearance {clearance:.3f} mm. "
            f"Minimum horizontal bar clearance {gap:g} mm. "
            f"Minimum vertical bar clearance {placement['minimum_vertical_clearance_mm']:g} mm.</p>"
            f"<p>Minimum link-grid clearance {placement['minimum_grid_clearance_mm']:g} mm. "
            f"Maximum perimeter pitch {placement['maximum_perimeter_pitch_mm']:g} mm. "
            f"Minimum hook tail {placement['minimum_hook_tail_mm']:g} mm.</p>"
            f"<p>Minimum link cover {placement['minimum_steel_cover_mm']:g} mm. "
            f"Clear concrete access through the web cage {across:g} × {along:g} mm.</p>"
        )
    if placement["status"] == "PASS":
        details += (
            f"<p>Minimum lap {placement['minimum_overlap_mm']:g} mm. "
            f"Minimum lap cover {placement['minimum_lap_cover_mm']:g} mm. "
            f"Minimum straight support development {placement['minimum_straight_support_development_mm']:g} mm.</p>"
            "<p>Assemble the link grids and straight bars on a jig. Check bar fit at the returns "
            "and maintain the cover and layer clearances with cover blocks and spacers. "
            "Check any support and flange obstructions against project geometry.</p>"
            "<h3>Adverse placement capacities</h3><ul>"
        )
        for face, row in placement["worst_strength"].items():
            details += (
                f"<li>{html.escape(face)} tension · {row['capacity_knm']:.3f} kN·m at "
                f"{html.escape(row['moment_row_id'])} · {row['shear_capacity_kn']:.3f} kN at "
                f"{html.escape(row['shear_row_id'])}</li>"
            )
        details += "</ul>"
        if continuity := placement.get("negative_steel_continuity"):
            locations = " and ".join(
                f"{x:g}" for x in continuity["inflection_stations_mm"]
            )
            details += (
                f"<p>Continuous top steel extends {continuity['minimum_extension_mm']:g} mm "
                f"past both inflections at {locations} mm. "
                f"Required extension {continuity['required_extension_mm']:g} mm. "
                f"Continuous area {continuity['area_fraction']:.1%} of the top steel.</p>"
            )
        if support := placement.get("retained_support_anchorage"):
            details += "<h3>Retained top bar development</h3><ul>"
            for row, trace in support.items():
                details += (
                    f"<li>{html.escape(row)} · {html.escape(trace['bar_id'])} · "
                    f"{html.escape(trace['direction'].replace('_', ' '))} · "
                    f"{trace['straight_available_mm']:g} mm available against "
                    f"{trace['development_required_mm']:g} mm required</li>"
                )
            details += "</ul>"
    return details


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
    reverse = lap.get("lap_direction") == AnchorageDirection.DECREASING_X
    has_flange_basis = "web_only_anchor_moment_knm" in lap
    if (reverse or has_flange_basis) and stress_rows:
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
        )
    if reverse:
        basis += "<p>Lap transfer toward decreasing x. Each transfer layout credits one lap piece.</p>"
    if has_flange_basis and stress_rows:
        basis += (
            "<p>Each transfer layout credits one lap piece. Sagging uses the compression flange. "
            "Hogging and shear use the web.</p>"
        )
        web_capacity = lap["web_only_anchor_moment_knm"]
        if web_capacity is not None:
            basis += (
                f"<p>Web-only moment resistance for positive support anchorage "
                f"{web_capacity:.3f} kN·m.</p>"
            )
    restraint = lap.get("compression_restraint")
    if restraint is not None:
        state = "PASS" if restraint["verified"] else "HOLD"
        basis += (
            f"<p>Compression-bar restraint {state} for the signed transfer layouts. "
            f"{html.escape(restraint['source'])}.</p>"
        )
        if restraint.get("corner_bar_ids_by_grid"):
            basis += (
                f"<p>Clear spacing between link grids "
                f"{restraint['minimum_between_link_grids_mm']:g} mm.</p>"
                + (
                    "<p>Checked with the declared placement limits.</p>"
                    if restraint.get("placement_envelope_verified")
                    else "<p>Checked on nominal dimensions. Verify the assembly and placement tolerances for the project.</p>"
                )
                + "<p>Closed link bend seats by grid.</p><ul>"
            )
            for name, bar_ids in restraint["corner_bar_ids_by_grid"].items():
                basis += f"<li>{html.escape(name)} link · {html.escape(', '.join(bar_ids))}</li>"
            basis += "</ul>"
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
