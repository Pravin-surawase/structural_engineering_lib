"""Compose the admitted six- and eight-bar tied rectangular member checks."""

from __future__ import annotations

from dataclasses import asdict, replace
from html import escape
from typing import Any, Literal

from structural_lib.codes.is456.column._strain_compatibility import (
    COLUMN_SECTION_METHOD,
)
from structural_lib.codes.is456.column.axial import classify_column, effective_length
from structural_lib.codes.is456.column.four_corner import evaluate_four_corner_cage
from structural_lib.codes.is456.column.midpoint_ties import (
    MidpointCrossTie,
    check_midpoint_ties,
)
from structural_lib.codes.is456.column.positioned import positioned_member_strength
from structural_lib.core.data_types import ColumnClassification, EndCondition
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.column_member import (
    FourCornerColumnGeometryV1,
    RectangularColumnActionsV1,
    TiedRectangularColumnInputV1,
)

_WORKFLOW = "is456.column.tied-rectangular-member-check/v1"
_STRENGTH_SOURCE = "IS 456:2000 Cl. 25.4, 38.1, 39.1, 39.5 and 39.6"
_MIDPOINT_AXES: dict[str, tuple[Literal["x", "y"], ...]] = {
    "eight_bar": ("x", "y"),
    "six_bar_omit_x_face_midpoints": ("y",),
    "six_bar_omit_y_face_midpoints": ("x",),
}


def check_tied_rectangular_member(
    request: TiedRectangularColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Check the supplied signed load pair and fully identified cage."""
    require_request_type(request, TiedRectangularColumnInputV1)
    geometry, actions = request.geometry, request.actions
    steel, materials = request.reinforcement, request.materials
    checks: list[dict[str, Any]] = []
    issues: list[StructuralIssueV1] = []

    def record(
        code: str, status: EngineeringStatus, path: str, message: str, **values: Any
    ) -> None:
        checks.append(
            {"code": code, "status": status, "path": path, "message": message, **values}
        )
        if status is not EngineeringStatus.PASS:
            issues.append(StructuralIssueV1(code, path, message))

    le = effective_length(
        geometry.unsupported_length_mm, EndCondition[geometry.end_condition]
    )
    short = all(
        classify_column(le, dimension) is ColumnClassification.SHORT
        for dimension in (geometry.D_mm, geometry.b_mm)
    )
    record(
        "COLUMN.SHORT_PROFILE",
        EngineeringStatus.PASS if short else EngineeringStatus.HOLD,
        "geometry",
        "This profile requires both effective-length ratios below 12.",
        effective_length_mm=le,
        slenderness_x=le / geometry.D_mm,
        slenderness_y=le / geometry.b_mm,
        source_reference="IS 456:2000 Cl. 25.1.2 and Cl. 25.2 Table 28",
    )
    supported_materials = materials.fck_nmm2 <= 60
    if not supported_materials:
        record(
            "COLUMN.CONCRETE_PROFILE",
            EngineeringStatus.HOLD,
            "materials.fck_nmm2",
            "The tied rectangular profile is bounded to concrete grades up to M60.",
        )

    calculation: dict[str, Any] = {
        "scope": "Short braced tied rectangle at one supplied station",
        "layout": steel.layout,
        "check_station_mm": actions.check_station_mm,
        "effective_length_mm": le,
        "cage": None,
        "cross_ties": (),
        "strength": None,
        "checks": checks,
    }
    tie = steel.tie
    if tie is None:
        record(
            "COLUMN.TIE_REQUIRED",
            EngineeringStatus.HOLD,
            "reinforcement.tie",
            "The perimeter tie and its shared open cross-tie schedule are required.",
        )
    else:
        inset = (
            steel.bar_center_offset_mm
            - steel.nominal_cover_mm
            - tie.diameter_mm
            - steel.longitudinal_bar_diameter_mm / 2
        )
        # This profile only admits the checked near-perimeter placement.
        # A large gap between the corner bars and link would leave them
        # inside the hoop without establishing lateral restraint.
        inset_supported = -1e-9 <= inset <= 2 + 1e-9
        record(
            "COLUMN.PERIMETER_RESTRAINT_INSET",
            EngineeringStatus.PASS if inset_supported else EngineeringStatus.FAIL,
            "reinforcement.bar_center_offset_mm",
            "The supported corner inset beyond the inside tie face and bar radius is 0–2 mm.",
            actual=inset,
            limit=2,
            source_reference="Bounded COL02 perimeter restraint profile",
        )
        cage = evaluate_four_corner_cage(
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            bar_diameter_mm=steel.longitudinal_bar_diameter_mm,
            nominal_cover_mm=steel.nominal_cover_mm,
            corner_inset_mm=inset,
            aggregate_size_mm=steel.aggregate_size_mm,
            project_required_cover_mm=steel.project_required_cover_mm,
            project_required_bend_radius_mm=steel.project_required_bend_radius_mm,
            tie_diameter_mm=tie.diameter_mm,
            tie_spacing_mm=tie.spacing_mm,
            tie_internal_bend_radius_mm=tie.internal_bend_radius_mm,
            tie_closed=tie.closed,
            tie_hook_angle_deg=tie.hook_angle_deg,
            tie_hook_tail_mm=tie.hook_tail_mm,
            midpoint_axes=_MIDPOINT_AXES[steel.layout],
        )
        calculation["cage"] = asdict(cage)
        for check in cage.checks:
            record(
                check.code,
                EngineeringStatus.PASS if check.passed else EngineeringStatus.FAIL,
                "reinforcement",
                check.code.removeprefix("COLUMN.").replace("_", " ").lower(),
                actual=check.actual,
                limit=check.limit,
                source_reference=check.source_reference,
            )

        if inset_supported and all(check.passed for check in cage.checks):
            restraint = check_midpoint_ties(
                cage=cage,
                b_mm=geometry.b_mm,
                D_mm=geometry.D_mm,
                nominal_cover_mm=steel.nominal_cover_mm,
                tie_id=tie.tie_id,
                diameter_mm=tie.diameter_mm,
                pitch_mm=tie.spacing_mm,
                bend_radius_mm=tie.internal_bend_radius_mm,
                hook_angle_deg=tie.hook_angle_deg,
                hook_tail_mm=tie.hook_tail_mm,
                cross_ties=tuple(
                    MidpointCrossTie(
                        item.tie_id, item.restrained_bar_ids, item.station_offset_mm
                    )
                    for item in steel.cross_ties
                ),
            )
            calculation["cross_ties"] = tuple(asdict(path) for path in restraint.paths)
            for check in restraint.checks:
                record(
                    check.code,
                    EngineeringStatus.PASS if check.passed else EngineeringStatus.FAIL,
                    "reinforcement.cross_ties",
                    check.code.removeprefix("COLUMN.").replace("_", " ").lower(),
                    actual=check.actual,
                    limit=check.limit,
                    source_reference=check.source_reference,
                )
            if restraint.missing_pairs:
                record(
                    "COLUMN.MIDPOINT_TIE_REQUIRED",
                    EngineeringStatus.HOLD,
                    "reinforcement.cross_ties",
                    "Each retained face-midpoint pair requires its own open cross-tie.",
                    missing_pairs=restraint.missing_pairs,
                )

            if not issues:
                strength = positioned_member_strength(
                    b_mm=geometry.b_mm,
                    D_mm=geometry.D_mm,
                    unsupported_length_mm=geometry.unsupported_length_mm,
                    pu_kn=actions.pu_kn,
                    mx_knm=actions.mx_knm,
                    my_knm=actions.my_knm,
                    fck_nmm2=materials.fck_nmm2,
                    fy_nmm2=materials.fy_nmm2,
                    cage=cage,
                )
                calculation["strength"] = asdict(strength)
                if actions.pu_kn >= strength.puz_kn:
                    record(
                        "COLUMN.AXIAL_LIMIT",
                        EngineeringStatus.FAIL,
                        "actions.pu_kn",
                        "The compression reaches or exceeds the Cl. 39.6 axial limit.",
                        actual=actions.pu_kn,
                        limit=strength.puz_kn,
                        source_reference=_STRENGTH_SOURCE,
                    )
                elif strength.governing_ratio is None:
                    record(
                        "COLUMN.PM_BASIS",
                        EngineeringStatus.HOLD,
                        "actions",
                        "The supplied compression did not give a converged partial-compression capacity on both axes.",
                        source_reference=_STRENGTH_SOURCE,
                    )
                else:
                    record(
                        "COLUMN.PM_STRENGTH",
                        (
                            EngineeringStatus.PASS
                            if strength.governing_ratio <= 1
                            else EngineeringStatus.FAIL
                        ),
                        "actions",
                        "The supplied pair and separate minimum-eccentricity checks must pass.",
                        actual=strength.governing_ratio,
                        limit=1,
                        governing_basis=strength.governing_basis,
                        source_reference=_STRENGTH_SOURCE,
                    )

    statuses = {item["status"] for item in checks}
    status = (
        EngineeringStatus.FAIL
        if EngineeringStatus.FAIL in statuses
        else (
            EngineeringStatus.HOLD
            if EngineeringStatus.HOLD in statuses
            else EngineeringStatus.PASS
        )
    )
    result = canonical_family_result(
        request,
        calculation,
        workflow_id=_WORKFLOW,
        engineering_status=status,
        assumptions=(
            "Positive Mx compresses the top face and positive My compresses the left face.",
            "Open midpoint links repeat with the perimeter tie pitch and share its diameter, bend and hook schedule.",
            "The supplied project cover and bend reference apply to this station.",
        ),
        limitations=(
            "Covers the three symmetric equal-bar layouts and partial-compression strength at one station.",
            "The section schematic identifies restraint paths. Joint and splice detailing, fabrication lengths and member-wide scheduling require separate evidence.",
            "Slender and seismic members, general P–M–M and automatic design require separate checks.",
        ),
        provenance=(
            COLUMN_SECTION_METHOD,
            _STRENGTH_SOURCE,
            "IS 456:2000 Cl. 26.2.2.4(b), 26.3.2, 26.4 and 26.5.3.2(b)(2) Fig. 9",
        ),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def render_tied_rectangular_member_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render a result-bound section schematic and the actual check statuses."""
    if result.workflow_id != _WORKFLOW or not isinstance(
        result.request, TiedRectangularColumnInputV1
    ):
        raise TypeError("A tied rectangular column member result is required")

    return _render_rectangular_section(
        result, result.request.geometry, result.request.actions
    )


def _render_rectangular_section(
    result: CanonicalFamilyResultV1[dict[str, Any]],
    geometry: FourCornerColumnGeometryV1,
    actions: RectangularColumnActionsV1,
    *,
    capacity_keys: tuple[str, str] = ("x", "y"),
) -> str:
    """Render either checked local section without recalculating the result."""
    payload = result.to_dict()
    calculation = payload["calculation"]
    width, depth = geometry.b_mm, geometry.D_mm
    status = result.engineering_status.value
    input_hash = payload["envelope"]["result_identity"]["input_hash"]
    cage = calculation["cage"]
    section = []
    bars = []
    if cage is not None:
        tie_width = cage["tie_centreline_width_mm"]
        tie_depth = cage["tie_centreline_depth_mm"]
        if min(tie_width, tie_depth) > 0:
            bend = cage.get("tie_centreline_bend_radius_mm")
            radius = f' rx="{bend}"' if bend is not None else ""
            section.append(
                f'<rect x="{(width - tie_width) / 2}" y="{(depth - tie_depth) / 2}" '
                f'width="{tie_width}" height="{tie_depth}"{radius} fill="none" stroke="#17616b"/>'
            )
        for path in calculation["cross_ties"]:
            x1, y1 = path["start_mm"]
            x2, y2 = path["end_mm"]
            section.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#17616b">'
                f"<title>{escape(path['tie_id'])}</title></line>"
            )
            for hook in path.get("hooks", ()):
                cx, cy = hook["centre_mm"]
                sx, sy = hook["tangent_mm"]
                ex, ey = hook["bend_end_mm"]
                tx, ty = hook["tail_end_mm"]
                radius = hook["radius_mm"]
                sweep = int((sx - cx) * (ey - cy) > (sy - cy) * (ex - cx))
                section.append(
                    f'<path d="M {sx} {sy} A {radius} {radius} 0 0 {sweep} '
                    f'{ex} {ey} L {tx} {ty}" fill="none" stroke="#17616b"/>'
                )
        for bar in cage["bars"]:
            x, y = bar["x_from_left_mm"], bar["y_from_top_mm"]
            bar_id = escape(bar["bar_id"])
            section.append(
                f'<circle cx="{x}" cy="{y}" r="{bar["diameter_mm"] / 2}" fill="#172b4d">'
                f"<title>{bar_id}</title></circle>"
            )
            bars.append(f"<li>{bar_id} · x {x:g} mm · y {y:g} mm</li>")

    rows = "".join(
        f"<tr><td>{escape(check['code'])}</td><td>{escape(check['status'])}</td>"
        f"<td>{escape(check['message'])}</td></tr>"
        for check in calculation["checks"]
    )
    tie_rows = "".join(
        f"<li>{escape(tie['tie_id'])} · {escape(', '.join(tie['restrained_bar_ids']))}"
        f" · axial offset {tie['station_offset_mm']:g} mm</li>"
        for tie in calculation["cross_ties"]
    )
    limits = "".join(f"<li>{escape(limit)}</li>" for limit in result.limitations)
    sources = "".join(f"<li>{escape(source)}</li>" for source in result.provenance)
    strength = calculation["strength"]
    strength_html = "<p>Strength check unavailable.</p>"
    if strength is not None and strength["governing_ratio"] is not None:
        strength_html = (
            f"<p>Mx capacity {strength['axes'][capacity_keys[0]]['capacity_knm']:.3f} kNm · "
            f"My capacity {strength['axes'][capacity_keys[1]]['capacity_knm']:.3f} kNm · "
            f"Governing ratio {strength['governing_ratio']:.5f}</p>"
        )
    title = "Tied rectangular column member check"
    page_title = "Tied rectangular column check"
    check_status = ""
    if "restraint_status" in calculation:
        title = page_title = "Positioned rectangular column member check"
        check_status = (
            f"<p>Section strength {calculation['strength_status']} · "
            f"Local restraint {calculation['restraint_status']}</p>\n"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{page_title}</title>
<style>body{{font:16px system-ui,sans-serif;margin:2rem;color:#162238}}
table{{border-collapse:collapse}}td,th{{border:1px solid #c4ceda;padding:.45rem}}
svg{{max-width:100%;height:auto}}code{{overflow-wrap:anywhere}}</style></head>
<body><h1>{title}</h1>
<p>Case {escape(result.identity.case_id)} · Station {actions.check_station_mm:g} mm</p>
<p><strong>Engineering status {status}</strong> · {result.envelope.review_status.value}</p>
{check_status}<p>Input SHA-256 <code>{input_hash}</code></p>
<p>Pu {actions.pu_kn:g} kN · Mx {actions.mx_knm:g} kNm · My {actions.my_knm:g} kNm</p>
<h2>Section and restraint schematic</h2>
<svg viewBox="0 0 {width} {depth}" width="300" role="img" aria-label="Column section and restraint paths">
<rect x="0" y="0" width="{width}" height="{depth}" fill="#f4f7fa" stroke="#172b4d"/>
{''.join(section)}</svg>
<ul>{''.join(bars)}{tie_rows}</ul>
<h2>Checks</h2><table><tr><th>Check</th><th>Status</th><th>Meaning</th></tr>{rows}</table>
<h2>Strength</h2>{strength_html}
<h2>Sources and scope</h2><ul>{sources}{limits}</ul></body></html>
"""
