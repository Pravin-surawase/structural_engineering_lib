"""Bind short circular section checks to ordinary ring or spiral quantities."""

from __future__ import annotations

import html
import math
from collections.abc import Callable
from dataclasses import asdict, replace
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.codes.is456.beam.shear import _exact_vertical_stirrup_limit_mm
from structural_lib.codes.is456.column.member_detailing import (
    ordinary_column_shear,
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
_SHEAR_SOURCE = "IS 456 Cl. 26.5.1.5–6 and 40, Tables 19–20, with the separately declared circular geometry basis."


class CircularTransversePlacementV1(StrictPublicModel):
    """Body end stations and physical anchorage pitches for a uniform spiral."""

    first_station_mm: float = Field(ge=0, le=50000)
    last_station_mm: float = Field(gt=0, le=50000)
    end_clearance_mm: float = Field(gt=0, le=300)
    start_anchor_pitch_mm: float | None = Field(default=None, gt=0, le=100)
    end_anchor_pitch_mm: float | None = Field(default=None, gt=0, le=100)
    source_reference: str = Field(min_length=1, max_length=240)


class _CircularColumnShearBasisV1(StrictPublicModel):
    """One fixed equivalent-area model with the supplied grade of closed rings."""

    plane: Literal["x", "y"]
    ring_grade_nmm2: float = Field(ge=250, le=600)
    effective_depth_diameter_factor: float = Field(ge=0.8, le=0.8)
    effective_concrete_area_gross_cap_factor: float = Field(ge=0.8, le=0.8)
    credit_closed_ring_legs: Literal[2]


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
    shear_basis: _CircularColumnShearBasisV1 | None = Field(
        default=None, exclude_if=lambda value: value is None
    )

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
    start_clearance = extent_start - steel.diameter_mm / 2
    end_clearance = length - extent_end - steel.diameter_mm / 2
    clearance = min(start_clearance, end_clearance)
    if request.end_detail.end_face_clearance_mm >= placement.end_clearance_mm:
        required_clearance = request.end_detail.end_face_clearance_mm
        clearance_source = "end_detail.end_face_clearance_mm"
    else:
        required_clearance = placement.end_clearance_mm
        clearance_source = "placement.end_clearance_mm"
    if clearance < required_clearance:
        return (
            None,
            EngineeringStatus.FAIL,
            StructuralIssueV1(
                "COLUMN.CIRCULAR_END_PLACEMENT",
                clearance_source,
                f"End-face clearances are {start_clearance:g} mm at the start and "
                f"{end_clearance:g} mm at the end. {clearance_source} requires "
                f"{required_clearance:g} mm at each face.",
            ),
        )
    offset = max(extent_start, length - extent_end)
    if offset > request.end_detail.max_end_hoop_offset_mm:
        return (
            None,
            EngineeringStatus.FAIL,
            StructuralIssueV1(
                "COLUMN.CIRCULAR_END_PLACEMENT",
                "end_detail.max_end_hoop_offset_mm",
                f"End offset {offset:g} mm exceeds the declared "
                f"{request.end_detail.max_end_hoop_offset_mm:g} mm limit.",
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
            "start_face_clearance_mm": start_clearance,
            "end_face_clearance_mm": end_clearance,
            "required_end_clearance_mm": required_clearance,
            "end_clearance_source": clearance_source,
        },
        EngineeringStatus.PASS,
        None,
    )


def _check_circular_shear(
    request: CircularColumnDetailingInputV1,
    transverse: dict[str, Any] | None,
    *,
    evidence_current: bool,
    record: Callable[[str, str, str, EngineeringStatus], None],
) -> tuple[list[dict[str, Any]], str]:
    actions = [row for row in request.actions if row.vx_kn or row.vy_kn]
    if not actions:
        return [], "NOT_APPLICABLE"
    if not evidence_current:
        return [], "HOLD"
    basis, steel = request.shear_basis, request.reinforcement.transverse
    if basis is None:
        record(
            "COLUMN.CIRCULAR_MEMBER_ACTIONS_HELD",
            "actions",
            "Supply the admitted single-plane circular shear basis.",
            EngineeringStatus.HOLD,
        )
        return [], "HOLD"
    if any(row.vx_kn and row.vy_kn for row in actions):
        record(
            "COLUMN.COMBINED_SHEAR",
            "actions",
            "Simultaneous nonzero shears require a two-plane interaction basis.",
            EngineeringStatus.HOLD,
        )
        return [], "HOLD"
    if any(row.vy_kn if basis.plane == "x" else row.vx_kn for row in actions):
        record(
            "COLUMN.CIRCULAR_SHEAR_PLANE_HELD",
            "actions",
            "All nonzero shears must use the declared principal plane.",
            EngineeringStatus.HOLD,
        )
        return [], "HOLD"
    if (
        not isinstance(steel, CircularRingV1)
        or not steel.closed
        or not steel.closure_reference
    ):
        record(
            "COLUMN.CIRCULAR_SHEAR_RING_HELD",
            "reinforcement.transverse",
            "The shear basis requires tied closed rings with documented closure.",
            EngineeringStatus.HOLD,
        )
        return [], "HOLD"
    if transverse is None:
        # Section and placement checks own the disposition when no ring grid is checked.
        return [], "HOLD"
    fck = request.materials.fck_nmm2
    if fck not in (20, 25, 30, 35, 40):
        record(
            "COLUMN.SHEAR_MATERIAL",
            "materials.fck_nmm2",
            "The shear profile uses the M20–M40 tabulated grade columns.",
            EngineeringStatus.HOLD,
        )
        return [], "HOLD"

    diameter = request.geometry.diameter_mm
    depth = basis.effective_depth_diameter_factor * diameter
    gross_area = math.pi * diameter**2 / 4
    effective_area = min(
        diameter * depth, basis.effective_concrete_area_gross_cap_factor * gross_area
    )
    width = effective_area / depth
    link_area = basis.credit_closed_ring_legs * math.pi * steel.diameter_mm**2 / 4
    pitch_limit = _exact_vertical_stirrup_limit_mm(
        width,
        depth,
        link_area,
        basis.ring_grade_nmm2,
        0,
    )
    rows = []
    for index, action in enumerate(request.actions):
        signed_demand = action.vx_kn if basis.plane == "x" else action.vy_kn
        if signed_demand == 0.0:
            continue
        shear = ordinary_column_shear(
            width_mm=width,
            d_mm=depth,
            gross_area_mm2=gross_area,
            pu_kn=action.pu_kn,
            vu_kn=signed_demand,
            fck_nmm2=fck,
            hoop_diameter_mm=steel.diameter_mm,
            hoop_fy_nmm2=basis.ring_grade_nmm2,
            pitch_mm=steel.pitch_mm,
        )
        demand = abs(signed_demand)
        path = f"actions.{index}"
        pitch_ok = steel.pitch_mm <= pitch_limit + 1e-9
        capacity_ok = demand <= shear.capacity_kn + 1e-9
        if not pitch_ok:
            record(
                "COLUMN.SHEAR_LINK_SPACING",
                path,
                f"Ring pitch {steel.pitch_mm:g} mm exceeds the {pitch_limit:.3f} mm shear limit.",
                EngineeringStatus.FAIL,
            )
        if not capacity_ok:
            record(
                (
                    "COLUMN.SHEAR_CRUSHING"
                    if demand > shear.crushing_kn
                    else "COLUMN.SHEAR_CAPACITY"
                ),
                path,
                f"Shear magnitude {demand:g} kN exceeds the {shear.capacity_kn:.3f} kN resistance.",
                EngineeringStatus.FAIL,
            )
        components = asdict(shear)
        components["table_19_tc_nmm2"] = components.pop("base_concrete_stress_nmm2")
        rows.append(
            {
                **components,
                "combination_id": action.combination_id,
                "station_mm": action.check_station_mm,
                "shear_plane": basis.plane,
                "signed_demand_kn": signed_demand,
                "demand_kn": demand,
                "gross_area_mm2": gross_area,
                "effective_shear_area_mm2": effective_area,
                "effective_hoop_area_mm2": link_area,
                "ring_mark": steel.tie_id,
                "credited_legs": basis.credit_closed_ring_legs,
                "margin_kn": shear.capacity_kn - demand,
                "pitch_limit_mm": pitch_limit,
                "status": "PASS" if pitch_ok and capacity_ok else "FAIL",
            }
        )
    return rows, "FAIL" if any(row["status"] == "FAIL" for row in rows) else "PASS"


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
    Short braced circular members with continuous bars. Nonzero shear uses
    one declared principal plane and the supported closed-ring basis.

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
    member_basis_complete = all(
        getattr(request.basis, field)
        for field in (
            "nonseismic_reference",
            "action_source_reference",
            "end_development_reference",
            "placement_reference",
        )
    )
    if not member_basis_complete:
        record(
            "COLUMN.CIRCULAR_MEMBER_BASIS_HELD",
            "basis",
            "Supply the ordinary member and development basis.",
            EngineeringStatus.HOLD,
        )
    if request.laps:
        record(
            "COLUMN.CIRCULAR_MEMBER_ACTIONS_HELD",
            "actions",
            "Circular physical splices require their own verified checks.",
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
    shear_rows, shear_status = _check_circular_shear(
        request,
        transverse,
        evidence_current=member_basis_complete and not stale,
        record=record,
    )
    if shear_status != "NOT_APPLICABLE":
        statuses.append(EngineeringStatus(shear_status))
    governing_shear = min(
        shear_rows,
        key=lambda row: (
            row["status"] != "FAIL",
            -row["utilization"],
            row["combination_id"],
            row["station_mm"],
        ),
        default=None,
    )
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
            **(
                {
                    "shear_rows": shear_rows,
                    "shear_status": shear_status,
                    "governing_shear": governing_shear,
                }
                if request.shear_basis is not None
                else {}
            ),
            "bbs": (
                {
                    "rows": rows,
                    "quantity": sum(row["quantity"] for row in rows),
                    "total_length_mm": math.fsum(
                        row["total_length_mm"] for row in rows
                    ),
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
            "Short braced regular circular cages with continuous straight bars.",
            "Ring closure uses the supplied cut evidence; the spiral is one continuous body and two declared anchorage segments.",
            "Nonzero shear uses one declared principal plane and the closed-ring basis. Splices, spiral shear and seismic checks require separate evidence.",
        ),
        provenance=(
            "IS 456 Clauses 26.2, 26.5.3.2 and 39; checked circular section and actual transverse centreline.",
            *((_SHEAR_SOURCE,) if governing_shear is not None else ()),
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
    governor = result.calculation.get("governing_shear")
    return _schedule_csv(
        bbs["rows"],
        {
            "member_id": request.identity.member_id,
            "analysis_revision": request.basis.analysis_revision,
            "detailing_revision": request.basis.detailing_revision,
            "input_hash": input_hash,
            **(
                {
                    "governing_shear_combination_id": governor["combination_id"],
                    "governing_shear_station_mm": f"{governor['station_mm']:g}",
                }
                if governor is not None
                else {}
            ),
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
            f'<line data-mark="{mark}" data-station-mm="{station:g}" '
            f'x1="70" x2="170" y1="{y(station):.4f}" y2="{y(station):.4f}"/>'
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
    attributes = shear_note = ""
    governor = result.calculation.get("governing_shear")
    if governor is not None:
        combination = html.escape(governor["combination_id"], quote=True)
        station = governor["station_mm"]
        plane = governor["shear_plane"]
        demand = governor["signed_demand_kn"]
        attributes = f' data-governing-shear="{combination}" data-governing-station-mm="{station:g}"'
        shear_note = (
            f'<line x1="173" x2="212" y1="{y(station):.4f}" y2="{y(station):.4f}" stroke="#965515"/>'
            f'<text x="255" y="378" font-size="13">Governing shear {combination} · {station:g} mm</text>'
            f'<text x="255" y="400" font-size="13">V{plane} {demand:+g} kN · {governor["utilization"]:.1%} utilized</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 530 510" role="img"{attributes}>
<title>{html.escape(request.identity.member_id or '')} circular column review elevation</title>
<desc>Input {input_hash}. Analysis {html.escape(request.basis.analysis_revision)}. Detail {html.escape(request.basis.detailing_revision)}.</desc>
<rect x="60" y="{y(length):.4f}" width="120" height="{length*scale:.4f}" fill="#f1f5f9" stroke="#334155"/>
<path d="M 75 50 V 470 M 165 50 V 470" stroke="#172b4d" fill="none"/>
<g stroke="#17616b" stroke-width="1.3">{''.join(marks)}</g>
{section}
<text x="255" y="329" font-size="14">Diameter {diameter:g} mm</text>
<text x="255" y="352" font-size="14">Clear height {length:g} mm</text>{shear_note}</svg>"""


def _shear_report(data: dict[str, Any]) -> str:
    if "shear_status" not in data:
        return ""
    status = data["shear_status"]
    governor = data["governing_shear"]
    if governor is None:
        return f"<h2>Single-plane shear</h2><p>{status}</p>"
    rows = "".join(
        f'<tr><th>{html.escape(row["combination_id"])}</th><td>{row["station_mm"]:g}</td>'
        f'<td>V{row["shear_plane"]} {row["signed_demand_kn"]:+g}</td><td>{row["vc_kn"]:.2f}</td>'
        f'<td>{row["vus_kn"]:.2f}</td><td>{row["capacity_kn"]:.2f}</td>'
        f'<td>{row["utilization"]:.4f}</td><td>{row["status"]}</td></tr>'
        for row in data["shear_rows"]
    )
    return (
        f'<h2>Single-plane shear</h2><p>{status}. Governing shear {html.escape(governor["combination_id"])} '
        f'at {governor["station_mm"]:g} mm. V{governor["shear_plane"]} '
        f'{governor["signed_demand_kn"]:+g} kN. Resistance {governor["capacity_kn"]:.2f} kN.</p>'
        f'<p>Effective shear depth {governor["d_mm"]:g} mm and concrete area '
        f'{governor["effective_shear_area_mm2"]:.2f} mm². Table 20 cap {governor["crushing_kn"]:.2f} kN.</p>'
        f'<p>{html.escape(governor["ring_mark"])}. {governor["credited_legs"]} credited ring legs. '
        f'Pitch {governor["pitch_mm"]:g} mm against {governor["pitch_limit_mm"]:g} mm permitted.</p>'
        f"<table><thead><tr><th>Combination</th><th>Station (mm)</th><th>Signed shear (kN)</th>"
        f"<th>Vc (kN)</th><th>Vus (kN)</th><th>Resistance (kN)</th><th>Utilization</th>"
        f"<th>Status</th></tr></thead><tbody>{rows}</tbody></table>"
    )


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
    for item, supplied in zip(data["sections"], request.actions, strict=False):
        checked = item["checked_section"]
        actions = checked["request"]["actions"]
        status = checked["envelope"]["engineering_status"]
        rows.append(
            f"<tr><th>{html.escape(item['combination_id'])}</th><td>{actions['check_station_mm']:g}</td>"
            f"<td>{actions['pu_kn']:g}</td><td>{actions['mx_knm']:g}</td><td>{actions['my_knm']:g}</td>"
            f"<td>{supplied.vx_kn:g}</td><td>{supplied.vy_kn:g}</td><td>{status}</td></tr>"
        )
    issues = "".join(
        f"<li><code>{html.escape(issue.code)}</code> {html.escape(issue.message)}</li>"
        for issue in result.issues
    )
    limits = "".join(f"<li>{html.escape(limit)}</li>" for limit in result.limitations)
    transverse = data["transverse"]
    clearance = (
        f"<p>End-face clearances {transverse['start_face_clearance_mm']:g} mm at the start "
        f"and {transverse['end_face_clearance_mm']:g} mm at the end. "
        f"Required {transverse['required_end_clearance_mm']:g} mm from "
        f"<code>{html.escape(transverse['end_clearance_source'])}</code>.</p>"
        if transverse is not None
        else ""
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Circular column detailing</title>
<h1>Circular column detailing · {html.escape(request.identity.member_id or '')}</h1>
<p>{result.engineering_status.value} · Qualified review required</p>
<p>Input identity <code>{input_hash}</code>. Analysis revision {html.escape(request.basis.analysis_revision)}.
Detail revision {html.escape(request.basis.detailing_revision)}.</p>
<p>Required straight development {data['end_required_mm']:.2f} mm at each end.</p>{clearance}
<table><thead><tr><th>Combination</th><th>Station (mm)</th><th>P (kN)</th><th>Mx (kN·m)</th>
<th>My (kN·m)</th><th>Vx (kN)</th><th>Vy (kN)</th><th>Section status</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
{_shear_report(data)}{drawing}{schedule_html}<ul>{issues}{limits}</ul></html>"""
