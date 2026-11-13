"""Bind short circular section checks to ordinary ring or spiral quantities."""

from __future__ import annotations

import html
import math
from dataclasses import replace
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.codes.is456.column.member_detailing import (
    straight_column_bond_lengths,
)
from structural_lib.core.result_contract import (
    EngineeringStatus,
    FreshnessStatus,
    StructuralIssueV1,
)
from structural_lib.services.bbs import calculate_bar_weight
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.column_circular_member import (
    check_circular_member,
    render_circular_member_svg,
)
from structural_lib.services.column_member_outputs import _schedule_csv
from structural_lib.services.contracts.column_circular import (
    CircularColumnCageV1,
    CircularColumnGeometryV1,
    CircularColumnInputV1,
    CircularRingV1,
)
from structural_lib.services.contracts.column_member import RectangularColumnActionsV1
from structural_lib.services.contracts.column_member_detailing import (
    ColumnCompressionLapV1,
    ColumnDetailingActionV1,
    ColumnDetailingBasisV1,
    ColumnStraightEndDetailV1,
    ColumnTransverseCutScheduleV1,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1

WORKFLOW = "is456.column.circular-member-detailing/v1"
Result = CanonicalFamilyResultV1[dict[str, Any]]


class CircularTransversePlacementV1(StrictPublicModel):
    """Body end stations and physical anchorage pitches for a uniform spiral."""

    first_station_mm: float = Field(ge=0, le=50000)
    last_station_mm: float = Field(gt=0, le=50000)
    end_clearance_mm: float = Field(gt=0, le=300)
    start_anchor_pitch_mm: float | None = Field(default=None, gt=0, le=100)
    end_anchor_pitch_mm: float | None = Field(default=None, gt=0, le=100)
    source_reference: str = Field(min_length=1, max_length=240)


class CircularColumnDetailingInputV1(StrictPublicModel):
    """Short circular column, current concurrent station rows and actual cage detail."""

    schema_version: Literal["column-circular-member-detailing-input/v1"] = (
        "column-circular-member-detailing-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: CircularColumnGeometryV1
    materials: ColumnMaterialsV1
    reinforcement: CircularColumnCageV1
    basis: ColumnDetailingBasisV1
    end_detail: ColumnStraightEndDetailV1
    actions: tuple[ColumnDetailingActionV1, ...] = Field(min_length=1, max_length=48)
    placement: CircularTransversePlacementV1 | None = None
    transverse_cut_schedule: ColumnTransverseCutScheduleV1 | None = None
    laps: tuple[ColumnCompressionLapV1, ...] = Field(default=(), max_length=8)

    @field_validator("actions", "laps", mode="before")
    @classmethod
    def accept_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def validate_actions(self) -> Self:
        if self.identity.member_id is None:
            raise ValueError("The schedule needs a physical member ID.")
        keys = {(row.combination_id, row.check_station_mm) for row in self.actions}
        if len(keys) != len(self.actions):
            raise ValueError("Each combination and station pair must be unique.")
        if any(
            row.check_station_mm > self.geometry.unsupported_length_mm
            for row in self.actions
        ):
            raise ValueError("Every action station must lie within the member.")
        _circular_section(self, self.actions[0])
        return self


def _circular_section(
    request: CircularColumnDetailingInputV1, action: ColumnDetailingActionV1
) -> CircularColumnInputV1:
    return CircularColumnInputV1(
        identity=request.identity,
        geometry=request.geometry,
        materials=request.materials,
        reinforcement=request.reinforcement,
        actions=RectangularColumnActionsV1.model_validate(
            action.model_dump(exclude={"combination_id", "vx_kn", "vy_kn"})
        ),
    )


def _schedule_transverse(
    request: CircularColumnDetailingInputV1,
    section: Result,
) -> tuple[dict[str, Any] | None, EngineeringStatus, StructuralIssueV1 | None]:
    placement, steel = request.placement, request.reinforcement.transverse
    cut = request.transverse_cut_schedule
    if placement is None or steel is None:
        return (
            None,
            EngineeringStatus.HOLD,
            StructuralIssueV1(
                "COLUMN.CIRCULAR_PLACEMENT_HELD",
                "placement",
                "Supply the current ring or spiral member placement.",
            ),
        )
    first, last, pitch = (
        placement.first_station_mm,
        placement.last_station_mm,
        steel.pitch_mm,
    )
    body = (last - first) / pitch
    length = request.geometry.unsupported_length_mm
    if not 1 <= round(body) <= 500 or not math.isclose(
        body, round(body), rel_tol=0, abs_tol=1e-8
    ):
        return (
            None,
            EngineeringStatus.FAIL,
            StructuralIssueV1(
                "COLUMN.CIRCULAR_GRID",
                "placement",
                "The body interval must contain a whole, bounded number of pitches.",
            ),
        )
    centreline = section.calculation["detail"]["transverse_centreline_diameter_mm"]
    circumference = math.pi * centreline
    extent_start, extent_end = first, last
    if isinstance(steel, CircularRingV1):
        if (
            cut is None
            or cut.detailing_revision != request.basis.detailing_revision
            or set(cut.cut_lengths_mm) != {steel.tie_id}
        ):
            return (
                None,
                EngineeringStatus.HOLD,
                StructuralIssueV1(
                    "COLUMN.CIRCULAR_RING_CUT_HELD",
                    "transverse_cut_schedule",
                    "Supply the current cut and closure register for the actual ring mark.",
                ),
            )
        count, length_each = round(body) + 1, cut.cut_lengths_mm[steel.tie_id]
        if length_each < circumference:
            return (
                None,
                EngineeringStatus.FAIL,
                StructuralIssueV1(
                    "COLUMN.CIRCULAR_RING_CUT",
                    "transverse_cut_schedule",
                    "The declared closed-ring cut is shorter than the centreline circumference.",
                ),
            )
        source = cut.reference
        stages: tuple[tuple[float, float, float, float], ...] = ()
    else:
        end_pitches = placement.start_anchor_pitch_mm, placement.end_anchor_pitch_mm
        turns = steel.start_extra_turns, steel.end_extra_turns
        if any(value is None for value in (*end_pitches, *turns)) or cut is not None:
            return (
                None,
                EngineeringStatus.HOLD,
                StructuralIssueV1(
                    "COLUMN.CIRCULAR_SPIRAL_ENDS_HELD",
                    "placement",
                    "Supply both actual end pitches and turns for the derived spiral cut.",
                ),
            )
        start_pitch, end_pitch = end_pitches
        start_turns, end_turns = turns
        assert (
            start_pitch is not None
            and end_pitch is not None
            and start_turns is not None
            and end_turns is not None
        )
        if any(
            p / math.hypot(1, p / (2 * centreline)) < steel.diameter_mm or p > pitch
            for p in end_pitches
            if p is not None
        ):
            return (
                None,
                EngineeringStatus.FAIL,
                StructuralIssueV1(
                    "COLUMN.CIRCULAR_SPIRAL_END_PITCH",
                    "placement",
                    "Adjacent end turns require physical separation and pitch at most the body pitch.",
                ),
            )
        extent_start -= start_turns * start_pitch
        extent_end += end_turns * end_pitch
        stages = (
            (extent_start, first, start_pitch, start_turns),
            (first, last, pitch, round(body)),
            (last, extent_end, end_pitch, end_turns),
        )
        length_each = math.fsum(
            turn_count * math.hypot(circumference, p) for _, _, p, turn_count in stages
        )
        count, source = 1, placement.source_reference
    clearance = min(extent_start, length - extent_end) - steel.diameter_mm / 2
    offset = max(extent_start, length - extent_end)
    if (
        clearance < placement.end_clearance_mm
        or offset > request.end_detail.max_end_hoop_offset_mm
    ):
        return (
            None,
            EngineeringStatus.FAIL,
            StructuralIssueV1(
                "COLUMN.CIRCULAR_END_PLACEMENT",
                "placement",
                "Check the first and last transverse steel against the declared face clearance and end offset.",
            ),
        )
    if any(
        not extent_start <= row.check_station_mm <= extent_end
        for row in request.actions
    ):
        return (
            None,
            EngineeringStatus.HOLD,
            StructuralIssueV1(
                "COLUMN.CIRCULAR_STATION_OUTSIDE_GRID",
                "actions",
                "A supplied check station is outside the placed transverse member detail.",
            ),
        )
    return (
        {
            "bar_id": steel.tie_id,
            "role": steel.kind,
            "diameter_mm": steel.diameter_mm,
            "quantity": count,
            "cut_length_mm": length_each,
            "source": source,
            "stations_mm": [first + i * pitch for i in range(round(body) + 1)],
            "spiral_stages": stages,
            "transverse_end_clearance_mm": clearance,
        },
        EngineeringStatus.PASS,
        None,
    )


def check_circular_column_detailing(request: CircularColumnDetailingInputV1) -> Result:
    """Check circular longitudinal development, transverse placement and BBS.

    Parameters
    ----------
    request : CircularColumnDetailingInputV1
        Actual cage, supplied current station rows and ring or spiral placement.

    Returns
    -------
    CanonicalFamilyResultV1
        Checked sections, end development, transverse quantities and schedule.

    Raises
    ------
    InputContractError
        The request is not a validated circular detailing input.

    Examples
    --------
    See the circular column member detailing worked example.

    Limitations
    -----------
    Short braced circular members with zero supplied shear and continuous bars.

    Provenance
    ----------
    Uses the checked COL05 cage, IS 456 straight development and actual transverse geometry.
    """
    require_request_type(request, CircularColumnDetailingInputV1)
    steel, mat = request.reinforcement, request.materials
    issues = []
    statuses = []

    def record(code: str, path: str, message: str, status: EngineeringStatus) -> None:
        issues.append(StructuralIssueV1(code, path, message))
        statuses.append(status)

    stale = request.basis.analysis_revision != request.basis.current_analysis_revision
    if stale:
        record(
            "COLUMN.STALE_ANALYSIS",
            "basis",
            "Supply current analysis rows.",
            EngineeringStatus.HOLD,
        )
    if any(
        not getattr(request.basis, field)
        for field in (
            "nonseismic_reference",
            "action_source_reference",
            "end_development_reference",
            "placement_reference",
        )
    ):
        record(
            "COLUMN.CIRCULAR_MEMBER_BASIS_HELD",
            "basis",
            "Supply the ordinary member and development basis.",
            EngineeringStatus.HOLD,
        )
    if any(row.vx_kn or row.vy_kn for row in request.actions) or request.laps:
        record(
            "COLUMN.CIRCULAR_MEMBER_ACTIONS_HELD",
            "actions",
            "Circular shear and physical splices require their own verified checks.",
            EngineeringStatus.HOLD,
        )

    sections = (
        [
            check_circular_member(_circular_section(request, row))
            for row in request.actions
        ]
        if not stale
        else []
    )
    for section in sections:
        statuses.append(section.engineering_status)
        issues.extend(section.issues)
    end_required, _ = straight_column_bond_lengths(
        steel.bar_diameter_mm, mat.fck_nmm2, mat.fy_nmm2
    )
    ends = request.end_detail
    if min(ends.start_straight_mm, ends.end_straight_mm) < end_required:
        record(
            "COLUMN.END_DEVELOPMENT",
            "end_detail",
            "The straight bar projection is shorter than the full-tension development.",
            EngineeringStatus.FAIL,
        )
    transverse = None
    if sections and all(
        item.engineering_status is EngineeringStatus.PASS for item in sections
    ):
        transverse, status, issue = _schedule_transverse(request, sections[0])
        statuses.append(status)
        if issue is not None:
            issues.append(issue)
    status = (
        EngineeringStatus.FAIL
        if EngineeringStatus.FAIL in statuses
        else (
            EngineeringStatus.HOLD
            if EngineeringStatus.HOLD in statuses
            else EngineeringStatus.PASS
        )
    )
    rows = []
    if status is EngineeringStatus.PASS and transverse is not None:
        rows = [
            {
                "bar_id": bar["bar_id"],
                "role": "longitudinal",
                "diameter_mm": bar["diameter_mm"],
                "quantity": 1,
                "cut_length_mm": request.geometry.unsupported_length_mm
                + ends.start_straight_mm
                + ends.end_straight_mm,
                "source": request.basis.end_development_reference,
            }
            for bar in sections[0].calculation["bars"]
        ]
        if transverse["bar_id"] in {row["bar_id"] for row in rows}:
            status = EngineeringStatus.FAIL
            issues.append(
                StructuralIssueV1(
                    "COLUMN.BAR_MARK_CONFLICT",
                    "reinforcement",
                    "The transverse and longitudinal marks must be distinct.",
                )
            )
            rows = []
        else:
            rows.append(
                {
                    key: transverse[key]
                    for key in (
                        "bar_id",
                        "role",
                        "diameter_mm",
                        "quantity",
                        "cut_length_mm",
                        "source",
                    )
                }
            )
    for row in rows:
        row["total_length_mm"] = row["quantity"] * row["cut_length_mm"]
        row["total_weight_kg"] = calculate_bar_weight(
            row["diameter_mm"], row["total_length_mm"], round_weight=False
        )
    result = canonical_family_result(
        request,
        {
            "sections": [
                {
                    "combination_id": action.combination_id,
                    "checked_section": section.to_dict(),
                }
                for action, section in zip(request.actions, sections, strict=not stale)
            ],
            "section_svg": (
                render_circular_member_svg(sections[0]) if sections else None
            ),
            "transverse": transverse,
            "end_required_mm": end_required,
            "bbs": (
                {
                    "rows": rows,
                    "total_weight_kg": math.fsum(
                        row["total_weight_kg"] for row in rows
                    ),
                }
                if rows
                else None
            ),
        },
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Short braced regular circular cages with continuous straight bars and zero supplied shear.",
            "Ring closure uses the supplied cut evidence; the spiral is one continuous body and two declared anchorage segments.",
            "Circular shear, splices, seismic checks, and professional approval require separate evidence.",
        ),
        provenance=(
            "IS 456 Clauses 26.2, 26.5.3.2 and 39; checked circular section and actual transverse centreline.",
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


def _metadata(result: Result) -> tuple[CircularColumnDetailingInputV1, str]:
    request, identity = result.request, result.envelope.result_identity
    if (
        result.workflow_id != WORKFLOW
        or not isinstance(request, CircularColumnDetailingInputV1)
        or identity is None
        or identity.input_hash is None
    ):
        raise TypeError("A checked circular column detailing result is required.")
    return request, identity.input_hash


def render_circular_detailing_bbs_csv(result: Result) -> str | None:
    """Render the circular member's checked bar schedule.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked circular detailing result.

    Returns
    -------
    str or None
        The result-bound CSV if the schedule is eligible.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See the circular member worked example.

    Limitations
    -----------
    Uses the recorded ring or spiral cut and straight longitudinal bars.

    Provenance
    ----------
    Carries the same member, analysis, detail and input identities as the report.
    """
    request, input_hash = _metadata(result)
    bbs = result.calculation["bbs"]
    if bbs is None:
        return None
    return _schedule_csv(
        bbs["rows"],
        {
            "member_id": request.identity.member_id,
            "analysis_revision": request.basis.analysis_revision,
            "detailing_revision": request.basis.detailing_revision,
            "input_hash": input_hash,
        },
    )


def render_circular_detailing_svg(result: Result) -> str | None:
    """Draw a circular section and the checked member elevation.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked circular detailing result.

    Returns
    -------
    str or None
        The review SVG if the member schedule is eligible.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See the circular member worked example.

    Limitations
    -----------
    The spiral is shown as a projected centreline.

    Provenance
    ----------
    Uses the checked section and exact transverse end and body stations.
    """
    request, input_hash = _metadata(result)
    if result.calculation["bbs"] is None:
        return None
    transverse = result.calculation["transverse"]
    length = request.geometry.unsupported_length_mm
    diameter = request.geometry.diameter_mm
    ends = request.end_detail
    scale = 420 / (length + ends.start_straight_mm + ends.end_straight_mm)

    def y(station: float) -> float:
        return 470 - (station + ends.start_straight_mm) * scale

    section = result.calculation["section_svg"].replace(
        'width="320"', 'width="220" height="220" x="255" y="75"', 1
    )
    mark = html.escape(transverse["bar_id"], quote=True)
    marks: list[str] = []
    if transverse["role"] == "tied":
        marks.extend(
            f'<line data-mark="{mark}" x1="70" x2="170" y1="{y(station):.4f}" y2="{y(station):.4f}"/>'
            for station in transverse["stations_mm"]
        )
    else:
        points = []
        phase = 0.0
        for start, _, pitch, turns in transverse["spiral_stages"]:
            steps = max(1, math.ceil(turns * 24))
            for index in range(steps + 1):
                turn = turns * index / steps
                points.append(
                    f"{120+50*math.cos(2*math.pi*(phase+turn)):.3f},{y(start+pitch*turn):.4f}"
                )
            phase += turns
        marks.append(
            f'<polyline data-mark="{mark}" points="{" ".join(points)}" fill="none"/>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 530 510" role="img">
<title>{html.escape(request.identity.member_id or '')} circular column review elevation</title>
<desc>Input {input_hash}. Detail {html.escape(request.basis.detailing_revision)}.</desc>
<rect x="60" y="{y(length):.4f}" width="120" height="{length*scale:.4f}" fill="#f1f5f9" stroke="#334155"/>
<path d="M 75 50 V 470 M 165 50 V 470" stroke="#172b4d" fill="none"/>
<g stroke="#17616b" stroke-width="1.3">{''.join(marks)}</g>
{section}
<text x="255" y="329" font-size="14">Diameter {diameter:g} mm</text>
<text x="255" y="352" font-size="14">Clear height {length:g} mm</text></svg>"""


def render_circular_detailing_html(result: Result) -> str:
    """Render current circular member checks and fabrication quantities.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The checked circular detailing result.

    Returns
    -------
    str
        Standalone result-bound HTML.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See the circular member worked example.

    Limitations
    -----------
    Reuses the recorded results and withholds unqualified schedule outputs.

    Provenance
    ----------
    Preserves the same station, combination and bar evidence as JSON.
    """
    request, input_hash = _metadata(result)
    data = result.calculation
    drawing = render_circular_detailing_svg(result) or ""
    schedule = render_circular_detailing_bbs_csv(result)
    schedule_html = (
        f"<pre>{html.escape(schedule)}</pre>" if schedule else "<p>BBS held.</p>"
    )
    rows = []
    for item in data["sections"]:
        checked = item["checked_section"]
        actions = checked["request"]["actions"]
        status = checked["envelope"]["engineering_status"]
        rows.append(
            f"<tr><th>{html.escape(item['combination_id'])}</th><td>{actions['check_station_mm']:g}</td>"
            f"<td>{actions['pu_kn']:g}</td><td>{actions['mx_knm']:g}</td><td>{actions['my_knm']:g}</td>"
            f"<td>{status}</td></tr>"
        )
    issues = "".join(
        f"<li>{html.escape(issue.message)}</li>" for issue in result.issues
    )
    limits = "".join(f"<li>{html.escape(limit)}</li>" for limit in result.limitations)
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Circular column detailing</title>
<h1>Circular column detailing · {html.escape(request.identity.member_id or '')}</h1>
<p>{result.engineering_status.value} · Qualified review required</p>
<p>Input identity <code>{input_hash}</code>. Detail revision {html.escape(request.basis.detailing_revision)}.</p>
<p>Required straight development {data['end_required_mm']:.2f} mm at each end.</p>
<table><thead><tr><th>Combination</th><th>Station (mm)</th><th>P (kN)</th><th>Mx (kN·m)</th>
<th>My (kN·m)</th><th>Section status</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
{drawing}{schedule_html}<ul>{issues}{limits}</ul></html>"""
