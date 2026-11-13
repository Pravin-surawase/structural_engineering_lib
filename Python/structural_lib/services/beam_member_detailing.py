"""Checked continuous bar and ordinary link schedules for a two-span rectangle."""

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
    LinkCage,
    LongitudinalBarPath,
    ReinforcementArrangementCheckRequest,
    ReinforcementRole,
    StressState,
    check_anchorage,
    check_reinforcement_arrangement,
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
from structural_lib.construction import (
    BbsRequest,
    CuttingStockPolicy,
    LinkPlacementZone,
    ShapeConvention,
    create_bbs,
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
    _check_row,
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


class BeamContinuousDetailingInputV1(StrictPublicModel):
    """Two-span action and reinforcement check with a current ordinary link detail."""

    schema_version: Literal["is456-beam-continuous-detailing-input/v1"] = (
        "is456-beam-continuous-detailing-input/v1"
    )
    identity: FamilyIdentityV1
    member: BeamContinuousCheckRequestV1
    link_detail: BeamOrdinaryLinkDetailV1 | None = None
    stock_length_mm: float = Field(gt=0, le=18000)
    cutoff: BeamBottomCutoffV1 | None = None

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.identity.member_id != self.member.member_id:
            raise ValueError("Member and detailing identities must agree.")
        return self


def _physical_paths(
    request: BeamContinuousDetailingInputV1,
    source_hash: str,
    cutoff_end_mm: float | None,
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
            f"{member.member_id}-{bar.face}-D{bar.diameter_mm:g}"
            + (
                "-cutoff"
                if request.cutoff and bar.bar_id == request.cutoff.bar_id
                else ""
            ),
            ReinforcementRole(f"{bar.face}_longitudinal"),
            bar.diameter_mm,
            1,
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
    left, middle, _ = member.supports
    if not (
        extent
        and theoretical
        and end
        and bar
        and bar.face == "bottom"
        and theoretical.side == end.side == "CONTINUOUS"
        and left.right_face_mm < theoretical.x_mm < end.x_mm < middle.left_face_mm
    ):
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_BASIS_HELD",
            "cutoff",
            "Identify a bottom bar and two ordered continuous stations in the first clear span.",
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

    bars = tuple(
        BarPosition(
            item.bar_id,
            item.diameter_mm,
            item.x_from_left_mm,
            item.y_from_top_mm,
            Face(item.face),
            1,
        )
        for item in member.bars
        if item.bar_id != bar.bar_id
    )
    if sum(item.face == Face.BOTTOM for item in bars) < 2:
        issue = StructuralIssueV1(
            "BEAM.CUTOFF_BASIS_HELD",
            "cutoff",
            "Keep at least two bottom bars continuous through both spans.",
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
        )
        for row in checked.rows
        if row.kind == "ULS" and row.station.x_mm >= theoretical.x_mm
    )
    failed, held = _row_issues(reduced_rows, faces)
    bottom = flexure[Face.BOTTOM].outputs
    d = float(bottom["effective_depth_mm"])
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
            "continuing_bottom_mm2": bottom["tension_steel_area_mm2"],
            "continuing_shear_capacity_kn": capacity_kn,
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
    Straight longitudinal bars, one optional first-span bottom cutoff,
    and a single ordinary link mark.

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
    source_hash = identity.input_hash
    if status is EngineeringStatus.PASS and request.cutoff is not None:
        cutoff_end, cutoff, cutoff_issues, status = _check_bottom_cutoff(
            request, checked
        )
        data["cutoff"] = cutoff
        issues.extend(cutoff_issues)
        source_hash = semantic_hash(
            "beam_detailing_source",
            {
                "strength": identity.input_hash,
                "cutoff": request.cutoff.model_dump(mode="json"),
                "link": (
                    request.link_detail.model_dump(mode="json")
                    if request.link_detail
                    else None
                ),
            },
        )
    if status is EngineeringStatus.PASS:
        inputs = _physical_paths(request, source_hash, cutoff_end)
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
                schedule = _schedule(request, paths, link_request)
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
    elif checked.ultimate_status != "PASS":
        issues.extend(checked.result_envelope.issues)
    result = canonical_family_result(
        request,
        data,
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Only the supplied strength and anchorage rows and the declared physical layout are checked.",
            "Ordinary straight bars, one optional bottom-bar cutoff, and one uniform two-hook link mark.",
            "Unreported demand between stations, splices, member serviceability, support connections and fabrication approval require separate evidence.",
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
    One straight bar in the two-span rectangular detailing profile.

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
    proposed["member"].update(bars=new_bars, reinforcement_revision=revision)
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
    """Project the checked member bars and link levels onto a review elevation.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked physical member detail.
    current : BeamContinuousDetailingInputV1 or None
        Current input required by a caller exporting from an editable session.

    Returns
    -------
    str or None
        Identified SVG elevation when the schedule is eligible.

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
    The review elevation is a projection of the resolved schedule.

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
    bars = []
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
        bars.append(
            f'<line data-bar-id="{path_id}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="8"/>'
        )
    identity = result.envelope.result_identity
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{start - 40:g} -40 {end - start + 80:g} {depth + 180:g}" role="img">
<title>{html.escape(member.member_id)} checked continuous beam elevation</title>
<desc>Input {identity.input_hash if identity else ""}. Path {data["paths"]["result_id"]}. Review drawing.</desc>
<rect x="{start:g}" width="{end - start:g}" height="{depth:g}" fill="#f1f5f9" stroke="#0f172a"/>
{support_lines}{"".join(bars)}</svg>"""


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
    cutoff = result.calculation.get("cutoff", {})
    cutoff_html = ""
    if "bar_id" in cutoff:
        rows = "".join(
            f"<li>{html.escape(row['row_id'])} · {row['shear_kn']:g} kN · "
            f"{'PASS' if row['passes_two_thirds'] else 'FAIL'}</li>"
            for row in cutoff["termination_rows"]
        )
        cutoff_html = (
            f"<h2>Bottom bar cutoff</h2><p>{html.escape(cutoff['bar_id'])} ends at "
            f"{cutoff['termination_station_mm']:g} mm. Straight extension "
            f"{cutoff['actual_extension_mm']:g} mm. Continuing bottom steel "
            f"{cutoff['continuing_bottom_mm2']:.3f} mm².</p>"
            f"<p>Termination shear limit {cutoff['termination_shear_limit_kn']:.3f} kN.</p>"
            f"<ul>{rows}</ul>"
        )
    issues = "".join(f"<li>{html.escape(item.message)}</li>" for item in result.issues)
    limits = "".join(f"<li>{html.escape(item)}</li>" for item in result.limitations)
    status = result.engineering_status.value if current_match else "HOLD · stale result"
    if not current_match:
        strength = {"ultimate_status": "HOLD", "serviceability_status": "HOLD"}
        governance, cutoff_html = "", ""
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
{edit_html}{cutoff_html}{svg}{report_bbs}<ul>{issues}{limits}</ul></html>"""
