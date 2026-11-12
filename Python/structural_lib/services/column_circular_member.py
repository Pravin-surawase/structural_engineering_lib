"""Compose circular section strength, restraint and result-bound outputs."""

from __future__ import annotations

from dataclasses import asdict, replace
from html import escape
from typing import Any

from structural_lib.codes.is456.column._common import calculate_puz_for_area
from structural_lib.codes.is456.column._strain_compatibility import (
    COLUMN_SECTION_METHOD,
)
from structural_lib.codes.is456.column.axial import (
    classify_column,
    effective_length,
    min_eccentricity,
    short_axial_capacity,
)
from structural_lib.codes.is456.column.circular import CircularSection
from structural_lib.codes.is456.column.circular_cage import (
    CircularCage,
    CircularRing,
    CircularSpiral,
    check_circular_cage,
)
from structural_lib.codes.is456.column.helical import _HELICAL_ENHANCEMENT_FACTOR
from structural_lib.codes.is456.column.positioned_biaxial import (
    prepare_section_capacity,
)
from structural_lib.core.data_types import ColumnClassification, EndCondition
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.column_circular import (
    CircularColumnInputV1,
    CircularRingV1,
)

_WORKFLOW = "is456.column.circular-member-check/v1"
_SCOPE = "IS 456:2000 Cl. 25, 38.1 and 39.1–39.6"
_PASS, _FAIL, _HOLD = (
    EngineeringStatus.PASS,
    EngineeringStatus.FAIL,
    EngineeringStatus.HOLD,
)
_Result = CanonicalFamilyResultV1[dict[str, Any]]


def _strength(
    request: CircularColumnInputV1, cage: CircularCage, eccentricity: float, puz: float
) -> dict[str, Any] | None:
    """Use the short axial branch or a fixed-compression signed section."""
    actions, geo, material = request.actions, request.geometry, request.materials
    pu, mx, my = actions.pu_kn, actions.mx_knm, actions.my_knm
    if mx == my == 0 and eccentricity <= 0.05 * geo.diameter_mm:
        tied = short_axial_capacity(
            material.fck_nmm2,
            material.fy_nmm2,
            cage.gross_area_mm2,
            cage.steel_area_mm2,
        ).Pu_kN
        factor = (
            _HELICAL_ENHANCEMENT_FACTOR if cage.spiral_enhancement_eligible else 1.0
        )
        return {
            "method": "short_axial",
            "tied_axial_capacity_kn": tied,
            "axial_capacity_kn": tied * factor,
            "enhancement_factor": factor,
            "governing_ratio": pu / (tied * factor),
        }
    section = CircularSection(
        geo.diameter_mm, material.fck_nmm2, material.fy_nmm2, cage.bars
    )
    prepared = prepare_section_capacity(section, pu, cage.steel_area_mm2, puz)
    if prepared is None:
        return None
    length = geo.unsupported_length_mm
    checked = prepared.check(mx, my, length, length)
    if checked is None:
        return None
    return {**asdict(checked), "method": "fixed_compression", "enhancement_factor": 1.0}


def check_circular_member(request: CircularColumnInputV1) -> _Result:
    """Check one circular section, its signed strength and local restraint."""
    require_request_type(request, CircularColumnInputV1)
    geo, steel, actions, mat = (
        request.geometry,
        request.reinforcement,
        request.actions,
        request.materials,
    )
    submitted = steel.transverse
    transverse: CircularRing | CircularSpiral | None = None
    if isinstance(submitted, CircularRingV1):
        transverse = CircularRing(**submitted.model_dump(exclude={"kind"}))
    elif submitted is not None:
        transverse = CircularSpiral(**submitted.model_dump(exclude={"kind"}))
    cage = check_circular_cage(
        diameter_mm=geo.diameter_mm,
        count=steel.bar_count,
        bar_diameter_mm=steel.bar_diameter_mm,
        ring_radius_mm=steel.ring_radius_mm,
        first_angle_deg=steel.first_bar_angle_deg,
        aggregate_size_mm=steel.aggregate_size_mm,
        nominal_cover_mm=steel.nominal_cover_mm,
        project_cover_mm=steel.project_required_cover_mm,
        fck=mat.fck_nmm2,
        transverse=transverse,
    )
    checks: list[dict[str, Any]] = []
    issues: list[StructuralIssueV1] = []

    def record(
        code: str, status: EngineeringStatus, path: str, message: str, **values: Any
    ) -> None:
        checks.append(
            {"code": code, "status": status, "path": path, "message": message, **values}
        )
        if status is not _PASS:
            issues.append(StructuralIssueV1(code, path, message))

    for check in cage.checks:
        record(
            check.code,
            _PASS if check.passed else _FAIL,
            "reinforcement",
            check.code.removeprefix("COLUMN.").replace("_", " ").lower(),
            actual=check.actual,
            limit=check.limit,
            source_reference=check.source_reference,
        )
    for code, message in cage.missing_evidence:
        record(code, _HOLD, "reinforcement.transverse", message)
    restraint = (
        _FAIL
        if any(not check.passed for check in cage.checks)
        else _HOLD if cage.missing_evidence else _PASS
    )
    le = effective_length(geo.unsupported_length_mm, EndCondition[geo.end_condition])
    short = classify_column(le, geo.diameter_mm) is ColumnClassification.SHORT
    record(
        "COLUMN.SHORT_PROFILE",
        _PASS if short else _HOLD,
        "geometry",
        "This circular profile covers effective-length ratios below 12.",
        actual=le / geo.diameter_mm,
        limit=12,
        source_reference=_SCOPE,
    )
    if mat.fck_nmm2 > 60:
        record(
            "COLUMN.CONCRETE_PROFILE",
            _HOLD,
            "materials.fck_nmm2",
            "This profile admits concrete through M60.",
        )
    eccentricity = min_eccentricity(geo.unsupported_length_mm, geo.diameter_mm)
    puz = (
        calculate_puz_for_area(
            cage.gross_area_mm2, mat.fck_nmm2, mat.fy_nmm2, cage.steel_area_mm2
        )
        if cage.steel_area_mm2 < cage.gross_area_mm2
        else None
    )
    strength_status, strength = _HOLD, None
    if short and mat.fck_nmm2 <= 60 and cage.section_admitted and puz is not None:
        if actions.pu_kn >= puz:
            strength_status = _FAIL
            record(
                "COLUMN.AXIAL_LIMIT",
                _FAIL,
                "actions.pu_kn",
                "Compression reaches the Cl. 39.6 axial limit.",
                actual=actions.pu_kn,
                limit=puz,
                source_reference=_SCOPE,
            )
        else:
            strength = _strength(request, cage, eccentricity, puz)
            if strength is None:
                record(
                    "COLUMN.PM_BASIS",
                    _HOLD,
                    "actions",
                    "A signed section equilibrium could not be established.",
                    source_reference=_SCOPE,
                )
            else:
                strength_status = _PASS if strength["governing_ratio"] <= 1 else _FAIL
                record(
                    "COLUMN.CIRCULAR_STRENGTH",
                    strength_status,
                    "actions",
                    "Check the admitted short axial capacity or signed fixed-compression interaction.",
                    actual=strength["governing_ratio"],
                    limit=1,
                    source_reference=_SCOPE,
                )

    statuses = (strength_status, restraint)
    result = canonical_family_result(
        request,
        {
            "scope": "Short braced circular column at one supplied station",
            "check_station_mm": actions.check_station_mm,
            "effective_length_mm": le,
            "slenderness": le / geo.diameter_mm,
            "gross_area_mm2": cage.gross_area_mm2,
            "steel_area_mm2": cage.steel_area_mm2,
            "gross_inertia_mm4": cage.gross_inertia_mm4,
            "steel_ratio": cage.steel_ratio,
            "minimum_eccentricity_mm": eccentricity,
            "puz_kn": puz,
            "bars": tuple(asdict(bar) for bar in cage.bars),
            "transverse": submitted.model_dump() if submitted is not None else None,
            "detail": cage.detail,
            "checks": checks,
            "restraint_status": restraint,
            "strength_status": strength_status,
            "spiral_enhancement_eligible": cage.spiral_enhancement_eligible,
            "strength": strength,
        },
        workflow_id=_WORKFLOW,
        engineering_status=(
            _FAIL if _FAIL in statuses else _HOLD if _HOLD in statuses else _PASS
        ),
        assumptions=(
            "Positive Mx compresses the top and positive My compresses the left.",
            "Bar angles increase clockwise from the right, using top-left section coordinates.",
            "The signed interaction uses the tied section basis. The qualified spiral factor applies to the short axial method.",
        ),
        limitations=(
            "One regular ring of equal longitudinal bars in a short braced circular member.",
            "The transverse drawing is a cross-section projection. Ring closure details and spiral terminations use the supplied evidence.",
            "Member shear, splices, joints, seismic confinement and fabrication schedules require separate checks.",
        ),
        provenance=(
            COLUMN_SECTION_METHOD,
            _SCOPE,
            "IS 456:2000 Cl. 26.2.2.4(b), 26.3, 26.4 and 26.5.3",
        ),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def _checked_result(result: _Result) -> tuple[CircularColumnInputV1, str]:
    request, identity = result.request, result.envelope.result_identity
    if (
        result.workflow_id != _WORKFLOW
        or not isinstance(request, CircularColumnInputV1)
        or identity is None
        or identity.input_hash is None
    ):
        raise TypeError("A circular column member result is required")
    return request, identity.input_hash


def render_circular_member_svg(result: _Result) -> str:
    """Draw the checked cage at the same input identity."""
    request, input_hash = _checked_result(result)
    diameter = request.geometry.diameter_mm
    centre = diameter / 2
    calc = result.calculation
    transverse = calc["transverse"]
    ring = ""
    if transverse is not None:
        radius = calc["detail"]["transverse_centreline_diameter_mm"] / 2
        ring = (
            f'<circle cx="{centre}" cy="{centre}" r="{radius}" fill="none" '
            f'stroke="#17616b" stroke-width="{transverse["diameter_mm"]}">'
            f'<title>{escape(transverse["tie_id"])} · {transverse["kind"]} projection</title></circle>'
        )
    bars = "".join(
        f'<circle cx="{bar["x_from_left_mm"]}" cy="{bar["y_from_top_mm"]}" '
        f'r="{bar["diameter_mm"] / 2}" fill="#172b4d"><title>{escape(bar["bar_id"])}</title></circle>'
        for bar in calc["bars"]
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {diameter} {diameter}" width="320" role="img" aria-labelledby="title">
<title id="title">{escape(result.identity.case_id)} circular column section · {result.engineering_status.value}</title>
<desc>Diameter {diameter:g} mm · Input SHA-256 {input_hash} · Local restraint {calc['restraint_status']}</desc>
<circle cx="{centre}" cy="{centre}" r="{centre}" fill="#f4f7fa" stroke="#172b4d"/>
{ring}{bars}</svg>
"""


def render_circular_member_html(result: _Result) -> str:
    """Report the same checked actions, restraint and local section drawing."""
    request, input_hash = _checked_result(result)
    calc = result.calculation
    actions = request.actions
    strength = calc["strength"]
    summary = "<p>Strength capacity unavailable for this case.</p>"
    if strength is not None:
        factor = strength["enhancement_factor"]
        summary = f"<p>Governing utilization {strength['governing_ratio']:.5f} · Applied spiral factor {factor:g}</p>"
        if strength["method"] == "short_axial":
            summary += f"<p>Short axial capacity {strength['axial_capacity_kn']:.3f} kN · Tied basis {strength['tied_axial_capacity_kn']:.3f} kN</p>"
        else:
            axes = strength["axes"]
            capacities = " · ".join(
                f"{label} {axes[key]['capacity_knm']:.3f}"
                for label, key in (
                    ("+Mx", "x_positive"),
                    ("−Mx", "x_negative"),
                    ("+My", "y_positive"),
                    ("−My", "y_negative"),
                )
            )
            summary += f"<p>Signed capacity magnitudes (kNm) · {capacities}</p>"
    if calc["puz_kn"] is not None:
        summary += (
            f"<p>Cl. 39.6 axial limit on the tied basis {calc['puz_kn']:.3f} kN</p>"
        )
    transverse = calc["transverse"]
    schedule = "<p>Transverse reinforcement evidence is missing.</p>"
    if transverse:
        schedule = (
            f"<p>{escape(transverse['tie_id'])} · {transverse['kind']} · "
            f"Ø{transverse['diameter_mm']:g} at {transverse['pitch_mm']:g} mm</p>"
            f"<p>Outside core diameter {calc['detail']['core_outside_mm']:g} mm · "
            f"Centreline length per pitch {calc['detail']['centreline_length_per_pitch_mm']:.3f} mm</p>"
        )
        if transverse["kind"] == "spiral":
            detail = calc["detail"]
            schedule += (
                f"<p>Spiral volume ratio {detail['spiral_ratio_provided']:.6f} · "
                f"Minimum for enhancement {detail['spiral_ratio_required']:.6f} · "
                f"Enhancement eligible {calc['spiral_enhancement_eligible']}</p>"
                f"<p>Enhancement pitch window {detail['enhanced_min_pitch_mm']:g}"
                f"–{detail['enhanced_max_pitch_mm']:.3f} mm</p>"
            )
        elif transverse["closure_reference"]:
            schedule += f"<p>Ring closure evidence {escape(transverse['closure_reference'])}</p>"
    checks = []
    for check in calc["checks"]:
        values = (
            f" · Actual {check['actual']:.6g} · Limit {check['limit']:.6g}"
            if "actual" in check
            else ""
        )
        checks.append(
            f"<li>{escape(check['code'])} · {check['status']} · {escape(check['message'])}{values}</li>"
        )
    bars = "".join(
        f"<li>{escape(bar['bar_id'])} · Ø{bar['diameter_mm']:g} · "
        f"x {bar['x_from_left_mm']:.2f} mm · y {bar['y_from_top_mm']:.2f} mm</li>"
        for bar in calc["bars"]
    )
    sources = "".join(
        f"<li>{escape(item)}</li>" for item in (*result.provenance, *result.limitations)
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Circular column check</title>
<style>body{{font:16px system-ui;margin:2rem;color:#172b4d}}svg{{max-width:100%;height:auto}}code{{overflow-wrap:anywhere}}</style>
<h1>Circular column check</h1>
<p>Case {escape(result.identity.case_id)} · Station {actions.check_station_mm:g} mm</p>
<p><strong>Engineering status {result.engineering_status.value}</strong> · {result.envelope.review_status.value}</p>
<p>Section strength {calc['strength_status']} · Local restraint {calc['restraint_status']}</p>
<p>Input SHA-256 <code>{input_hash}</code></p>
<p>Pu {actions.pu_kn:g} kN · Mx {actions.mx_knm:g} kNm · My {actions.my_knm:g} kNm</p>
<p>Slenderness {calc['slenderness']:.4f} · Minimum eccentricity {calc['minimum_eccentricity_mm']:.3f} mm</p>
<h2>Strength</h2>{summary}
<h2>Checked local section</h2>{render_circular_member_svg(result)}{schedule}<ul>{bars}</ul>
<h2>Checks</h2><ul>{''.join(checks)}</ul><h2>Sources and scope</h2><ul>{sources}</ul></html>
"""
