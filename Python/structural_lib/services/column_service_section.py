"""Result-bound calculation and drawing for a rectangular column service section."""

from __future__ import annotations

import html
from dataclasses import asdict, replace
from typing import Any

from structural_lib.codes.is456.column.positioned_biaxial import PositionedColumnBar
from structural_lib.codes.is456.column.service_section import (
    equilibrate_service_section,
)
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.column_section import ColumnServiceSectionInputV1

WORKFLOW = "is456.column.service-section/v1"


def check_service_section(
    request: ColumnServiceSectionInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Resolve a cracked service section under one signed action row.

    Parameters
    ----------
    request : ColumnServiceSectionInputV1
        Rectangular geometry, positioned bars, elastic moduli and actions.

    Returns
    -------
    CanonicalFamilyResultV1
        Resolved section stresses, strains, properties and equilibrium evidence.

    Raises
    ------
    TypeError
        The request is not a validated service section input.

    Examples
    --------
    >>> callable(check_service_section)
    True

    Limitations
    -----------
    Elastic section calculation for one supplied service action row.
    Concrete tension, tension stiffening and member effects are excluded.

    Provenance
    ----------
    Affine strain compatibility and compression-only linear elasticity.
    """
    require_request_type(request, ColumnServiceSectionInputV1)
    geometry, moduli = request.geometry, request.moduli
    state = equilibrate_service_section(
        width=geometry.b_mm,
        depth=geometry.D_mm,
        bars=tuple(PositionedColumnBar(**bar.model_dump()) for bar in request.bars),
        ec=moduli.ec_nmm2,
        es=moduli.es_nmm2,
        **request.actions.model_dump(),
    )
    issues = []
    if state is None:
        issues.append(
            StructuralIssueV1(
                "COLUMN.SERVICE_EQUILIBRIUM_HELD",
                "actions",
                "No stable equilibrated strain plane was resolved for these actions.",
            )
        )
    else:
        if state.max_concrete_compression_nmm2 > request.concrete_linear_limit_nmm2:
            issues.append(
                StructuralIssueV1(
                    "COLUMN.SERVICE_CONCRETE_RANGE_HELD",
                    "concrete_linear_limit_nmm2",
                    "Calculated concrete stress exceeds the declared linear range.",
                )
            )
        if any(
            abs(bar.steel_stress_nmm2) >= request.materials.fy_nmm2
            for bar in state.bars
        ):
            issues.append(
                StructuralIssueV1(
                    "COLUMN.SERVICE_STEEL_RANGE_HELD",
                    "materials.fy_nmm2",
                    "Calculated steel stress reaches or exceeds the declared yield stress.",
                )
            )
    data = asdict(state) if state else None
    if data is not None:
        for name in (
            "gross_concrete_actions",
            "equilibrated_actions",
            "residual_actions",
        ):
            data[name] = dict(
                zip(("p_kn", "mx_knm", "my_knm"), data[name], strict=True)
            )
    result = canonical_family_result(
        request,
        {
            "section_state": data,
            "coordinate_convention": "x right, y down, from the top-left corner (mm)",
            "action_convention": "compression positive; Mx=sum F*(D/2-y); My=sum F*(b/2-x)",
            "member_acceptance": "NOT_EVALUATED",
            "detailing_acceptance": "NOT_EVALUATED",
        },
        workflow_id=WORKFLOW,
        engineering_status=EngineeringStatus.HOLD if issues else EngineeringStatus.PASS,
        limitations=(
            "PASS confirms equilibrium within the declared elastic section model.",
            "Properties use concrete in compression and concentrated equivalent steel areas at bar centres.",
            "Concrete tension, tension stiffening, creep, cracking limits, and member checks are excluded.",
            "Results beyond the elastic model range are diagnostic.",
        ),
        provenance=(
            "Affine strain compatibility with exact rectangular compression polygon integration.",
            "IS 456:2000 Cl. 6.2.3.1 and Cl. 5.6.3 provide nominal material moduli when applicable.",
        ),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def render_service_section_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render the signed service stresses and section plot from a checked result.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        A calculated service section result.

    Returns
    -------
    str
        A standalone HTML report with a section drawing and signed bar stresses.

    Raises
    ------
    TypeError
        The supplied result belongs to a different workflow.

    Examples
    --------
    >>> callable(render_service_section_html)
    True

    Limitations
    -----------
    Drawing and report use the recorded state and coordinates.

    Provenance
    ----------
    Bound to the input hash and method in the checked result.
    """
    if (
        not isinstance(result, CanonicalFamilyResultV1)
        or result.workflow_id != WORKFLOW
        or not isinstance(result.request, ColumnServiceSectionInputV1)
    ):
        raise TypeError("result must be a column service section result")
    request = result.request
    data = result.calculation
    state = data["section_state"]
    identity = result.envelope.result_identity
    label = html.escape(result.identity.case_id)
    issues = "".join(
        f"<li>{html.escape(issue.message)}</li>" for issue in result.issues
    )
    limits = "".join(f"<li>{html.escape(limit)}</li>" for limit in result.limitations)
    body = (
        _render_state(request, state)
        if state is not None
        else "<p>Section state held.</p>"
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Column service section {label}</title>
<h1>Column service section {label}</h1>
<p>{result.engineering_status.value} · Section calculation · Qualified review required</p>
<p>Input identity <code>{identity.input_hash if identity else ""}</code></p>
<p>{data['coordinate_convention']}. {data['action_convention']}.</p>
<p>Concrete Ec {request.moduli.ec_nmm2:.3f} N/mm², linear limit
{request.concrete_linear_limit_nmm2:.3f} N/mm².
Steel Es {request.moduli.es_nmm2:.3f} N/mm², fy {request.materials.fy_nmm2:.3f} N/mm².</p>
{body}
<h2>Scope and issues</h2><ul>{issues}{limits}</ul></html>"""


def _render_state(request: ColumnServiceSectionInputV1, state: dict[str, Any]) -> str:
    b, depth = request.geometry.b_mm, request.geometry.D_mm
    compression = " ".join(
        f"{x:.5f},{y:.5f}" for x, y in state["compression_polygon_from_top_left_mm"]
    )
    neutral_axis = " ".join(
        f"{x:.5f},{y:.5f}" for x, y in state["neutral_axis_from_top_left_mm"]
    )
    marks, rows = [], []
    for item in state["bars"]:
        bar = item["bar"]
        name = html.escape(bar["bar_id"])
        x, y = bar["x_from_left_mm"], bar["y_from_top_mm"]
        stress = item["steel_stress_nmm2"]
        color = "#b45309" if stress < 0 else "#155e75"
        marks.append(
            f'<circle cx="{x:g}" cy="{y:g}" r="{bar["diameter_mm"]/2:g}" fill="{color}">'
            f"<title>{name}: {stress:.4f} N/mm²</title></circle>"
        )
        rows.append(
            f"<tr><th>{name}</th><td>{x:g}</td><td>{y:g}</td>"
            f"<td>{item['strain']:.8f}</td><td>{stress:.4f}</td>"
            f"<td>{item['net_axial_kn']:.4f}</td></tr>"
        )
    properties = "".join(
        f"<li>{key} = {value:.5g}</li>" for key, value in state["properties"].items()
    )
    actions = []
    for name in ("p_kn", "mx_knm", "my_knm"):
        actions.append(
            f"<tr><th>{name}</th><td>{getattr(request.actions, name):.5f}</td>"
            f"<td>{state['gross_concrete_actions'][name]:.5f}</td>"
            f"<td>{state['equilibrated_actions'][name]:.5f}</td>"
            f"<td>{state['residual_actions'][name]:.3g}</td></tr>"
        )
    angle = state["neutral_axis_angle_deg"]
    axis_label = (
        f"{angle:.3f}°" if angle is not None else "No interior zero-strain line"
    )
    return f"""<h2>Section orientation and strain</h2>
<svg width="360" viewBox="-5 -5 {b+10:g} {depth+10:g}" role="img"
aria-label="Column section, concrete in compression, neutral axis and positioned bars">
<rect width="{b:g}" height="{depth:g}" fill="#f8fafc" stroke="#111827"/>
<polygon points="{compression}" fill="#bfdbfe"/>
<polyline points="{neutral_axis}" fill="none" stroke="#1e40af" stroke-width="2"/>
{''.join(marks)}</svg>
<p>Blue region: concrete in compression. Blue bars: compression. Amber bars: tension.</p>
<p>Neutral axis {axis_label}. Maximum concrete compression
{state['max_concrete_compression_nmm2']:.4f} N/mm².</p>
<p>Centroid strain {state['strain_at_centroid']:.8f}.
Gradients x {state['strain_gradient_x_per_mm']:.5g} and y
{state['strain_gradient_y_per_mm']:.5g} per mm.</p>
<h2>Equilibrium</h2>
<table><thead><tr><th>Action</th><th>Demand</th><th>Gross concrete contribution</th>
<th>Resolved total</th><th>Residual</th></tr></thead><tbody>{''.join(actions)}</tbody></table>
<h2>Bar response</h2><table><thead><tr><th>Bar</th><th>x (mm)</th><th>y (mm)</th>
<th>Strain</th><th>Steel stress (N/mm²)</th><th>Net force (kN)</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2>Transformed active section properties</h2><ul>{properties}</ul>"""
