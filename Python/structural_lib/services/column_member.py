"""Compose one physical four-corner column check and its HTML report."""

from __future__ import annotations

from dataclasses import asdict, replace
from html import escape
from typing import Any

from structural_lib.codes.is456.column.axial import classify_column, effective_length
from structural_lib.codes.is456.column.four_corner import evaluate_four_corner_cage
from structural_lib.codes.is456.column.uniaxial import design_short_column_uniaxial
from structural_lib.core.data_types import ColumnClassification, EndCondition
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.column_member import FourCornerColumnInputV1

_WORKFLOW = "is456.column.four-corner-member-check/v1"


def check_four_corner_member(
    request: FourCornerColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Compose physical cage checks and the existing principal-axis P–M owner."""
    require_request_type(request, FourCornerColumnInputV1)
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
        for dimension in (geometry.b_mm, geometry.D_mm)
    )
    record(
        "COLUMN.SHORT_PROFILE",
        EngineeringStatus.PASS if short else EngineeringStatus.HOLD,
        "geometry",
        "Both effective-length ratios must be below 12 for this profile.",
        effective_length_mm=le,
        slenderness_x=le / geometry.D_mm,
        slenderness_y=le / geometry.b_mm,
        source_reference="IS 456:2000 Cl. 25.1.2, Cl. 25.2 Table 28",
    )
    calculation: dict[str, Any] = {
        "scope": "short braced column, one principal bending axis and ordinary four-corner cage",
        "bending_axis": actions.bending_axis,
        "effective_length_mm": le,
        "cage": None,
        "strength": None,
        "checks": checks,
    }
    tie = steel.tie
    if tie is None:
        record(
            "COLUMN.TIE_REQUIRED",
            EngineeringStatus.HOLD,
            "reinforcement.tie",
            "Physical member checking requires the actual tie dimensions, spacing, bend, closure and hook.",
        )
    else:
        cage = evaluate_four_corner_cage(
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            bar_diameter_mm=steel.longitudinal_bar_diameter_mm,
            nominal_cover_mm=steel.nominal_cover_mm,
            corner_inset_mm=steel.corner_inset_mm,
            aggregate_size_mm=steel.aggregate_size_mm,
            project_required_cover_mm=steel.project_required_cover_mm,
            project_required_bend_radius_mm=steel.project_required_bend_radius_mm,
            tie_diameter_mm=tie.diameter_mm,
            tie_spacing_mm=tie.spacing_mm,
            tie_internal_bend_radius_mm=tie.internal_bend_radius_mm,
            tie_closed=tie.closed,
            tie_hook_angle_deg=tie.hook_angle_deg,
            tie_hook_tail_mm=tie.hook_tail_mm,
        )
        calculation["cage"] = asdict(cage)
        for check in cage.checks:
            record(
                check.code,
                EngineeringStatus.PASS if check.passed else EngineeringStatus.FAIL,
                "reinforcement",
                check.code.replace("COLUMN.", "").replace("_", " ").lower(),
                actual=check.actual,
                limit=check.limit,
                source_reference=check.source_reference,
            )
        offset = cage.bar_centroid_offset_mm
        capacity_basis_valid = (
            short
            and 0.008 <= cage.steel_ratio <= 0.04
            and 0 < offset < min(geometry.b_mm, geometry.D_mm) / 2
        )
        if capacity_basis_valid:
            width, depth = geometry.b_mm, geometry.D_mm
            if actions.bending_axis == "y":
                width, depth = depth, width
            strength = design_short_column_uniaxial(
                Pu_kN=actions.pu_kn,
                Mu_kNm=actions.moment_knm,
                b_mm=width,
                D_mm=depth,
                le_mm=le,
                fck=materials.fck_nmm2,
                fy=materials.fy_nmm2,
                Asc_mm2=cage.supplied_steel_area_mm2,
                d_prime_mm=offset,
                l_unsupported_mm=geometry.unsupported_length_mm,
            )
            calculation["strength"] = asdict(strength)
            calculation["strength"]["classification"] = strength.classification.name
            record(
                "COLUMN.PM_STRENGTH",
                EngineeringStatus.PASS if strength.is_safe else EngineeringStatus.FAIL,
                "actions",
                "The applied compression and design moment must lie inside the P–M envelope.",
                actual=strength.utilization_ratio,
                limit=1,
                equivalent_width_mm=width,
                equivalent_depth_mm=depth,
                source_reference=f"IS 456:2000 Cl. 25.4 and Cl. 39.5; {strength.method}",
            )
        else:
            record(
                "COLUMN.PM_BASIS",
                EngineeringStatus.HOLD,
                "reinforcement",
                "The short-column P–M owner requires ordered bar centres and 0.8–4% steel.",
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
        limitations=(
            "The selected action is compression plus a moment magnitude about one principal axis.",
            "Project cover and internal bend-radius requirements are supplied with a detailing reference.",
            "Joint anchorage, splices, serviceability, fire assessment and seismic confinement require their own evidence.",
        ),
        assumptions=(
            "Four equal bars are placed at the explicit inset inside one rectangular tie family.",
            "The two pairs are equivalent to equal opposite-face steel for the selected principal axis.",
            "The supplied project cover accounts for exposure and fire requirements.",
        ),
        provenance=(
            "structural_lib.codes.is456.column.four_corner.evaluate_four_corner_cage",
            "structural_lib.codes.is456.column.uniaxial.design_short_column_uniaxial",
            "IS 456:2000 Cl. 25, Cl. 26.2.2.4(b), Cl. 26.3.2, Cl. 26.4 and Cl. 26.5.3",
        ),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def render_four_corner_member_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render the checked inputs, physical cage, checks and identities."""
    if result.workflow_id != _WORKFLOW or not isinstance(
        result.request, FourCornerColumnInputV1
    ):
        raise TypeError("A physical four-corner column member result is required")

    def text(value: Any) -> str:
        return escape(str(value))

    request = result.request
    status = result.engineering_status.value
    payload = result.to_dict()
    identity = payload["envelope"]["result_identity"]
    check_rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{text(check.get(key, ''))}</td>"
            for key in (
                "code",
                "status",
                "actual",
                "limit",
                "message",
                "source_reference",
            )
        )
        + "</tr>"
        for check in payload["calculation"]["checks"]
    )
    cage = payload["calculation"]["cage"]
    bar_rows = ""
    if cage is not None:
        bar_rows = "".join(
            "<tr>"
            + "".join(
                f"<td>{text(bar[key])}</td>"
                for key in (
                    "bar_id",
                    "diameter_mm",
                    "area_mm2",
                    "x_from_left_mm",
                    "y_from_top_mm",
                )
            )
            + "</tr>"
            for bar in cage["bars"]
        )
    tie = request.reinforcement.tie
    tie_rows = "<tr><td>Actual tie</td><td>Missing</td></tr>"
    if tie is not None:
        tie_rows = "".join(
            f"<tr><td>{text(key)}</td><td>{text(value)}</td></tr>"
            for key, value in tie.model_dump().items()
        )
    input_rows = "".join(
        f"<tr><td>{text(group)}.{text(key)}</td><td>{text(value)}</td></tr>"
        for group in ("geometry", "actions", "materials", "reinforcement")
        for key, value in request.model_dump(mode="json")[group].items()
        if key != "tie"
    )
    strength_rows = "".join(
        f"<tr><td>{text(key)}</td><td>{text(value)}</td></tr>"
        for key, value in (payload["calculation"]["strength"] or {}).items()
    )
    references = "".join(f"<li>{text(value)}</li>" for value in result.provenance)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Four-corner column check</title>
<style>body{{font:16px system-ui,sans-serif;margin:2rem;color:#162238}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}td,th{{border:1px solid #c4ceda;padding:.45rem;text-align:left}}
th{{background:#eef3f8}}code{{overflow-wrap:anywhere}}h1,h2{{color:#183f65}}</style></head>
<body><h1>Four-corner column member check</h1>
<p>Member {text(request.identity.member_id)} · Case {text(request.identity.case_id)}</p>
<p><strong>Engineering status {text(status)}</strong> · {text(result.envelope.review_status.value)}</p>
<p>{text(payload["calculation"]["scope"])}</p>
<p>Input SHA-256 <code>{text(identity["input_hash"])}</code></p>
<p>Workflow <code>{text(result.workflow_id)}</code> · Library {text(identity["library_version"])}</p>
<h2>Checked inputs</h2><table><tr><th>Field and unit</th><th>Value</th></tr>{input_rows}</table>
<h2>Actual tie</h2><table><tr><th>Field and unit</th><th>Value</th></tr>{tie_rows}</table>
<h2>Resolved longitudinal bars</h2><p>Coordinates are mm from the left and top concrete faces.</p>
<table><tr><th>Bar</th><th>Diameter mm</th><th>Area mm²</th><th>x mm</th><th>y mm</th></tr>{bar_rows}</table>
<h2>Checks</h2><table><tr><th>Check</th><th>Status</th><th>Actual</th><th>Limit</th><th>Meaning</th><th>Source</th></tr>{check_rows}</table>
<h2>Principal-axis strength</h2><table><tr><th>Quantity and unit</th><th>Value</th></tr>{strength_rows}</table>
<h2>Calculation sources</h2><ul>{references}</ul>
<h2>Scope</h2><ul>{"".join(f"<li>{text(value)}</li>" for value in result.limitations)}</ul>
</body></html>"""
