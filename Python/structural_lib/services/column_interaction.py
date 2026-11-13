"""Bind signed section capacities and properties to the supplied column bars."""

from __future__ import annotations

import html
from dataclasses import asdict, replace
from math import cos, pi, sin
from typing import Any

from structural_lib.codes.is456.column.circular import CircularSection
from structural_lib.codes.is456.column.positioned_biaxial import (
    PositionedColumnBar,
    prepare_positioned_capacity,
    prepare_section_capacity,
)
from structural_lib.codes.is456.column.section_properties import (
    circular_properties,
    rectangular_properties,
    transformed_properties,
)
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.column_section import (
    ColumnInteractionInputV1,
    RectangularInteractionGeometryV1,
)

WORKFLOW = "is456.column.interaction-slice/v1"


def check_interaction_slice(
    request: ColumnInteractionInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Evaluate a signed, fixed-axial section.

    Parameters
    ----------
    request : ColumnInteractionInputV1
        Actual bars, section, compression and direction count.

    Returns
    -------
    CanonicalFamilyResultV1
        Signed equilibrium points and elastic properties.

    Raises
    ------
    TypeError
        The request is not a validated interaction input.

    Examples
    --------
    >>> callable(check_interaction_slice)
    True

    Limitations
    -----------
    One axial compression level. Member and detailing checks are separate.

    Provenance
    ----------
    IS 456 strain compatibility for actual rectangular and circular bars.
    """
    require_request_type(request, ColumnInteractionInputV1)
    geometry, materials = request.geometry, request.materials
    fck, fy = materials.fck_nmm2, materials.fy_nmm2
    bars = tuple(PositionedColumnBar(**item.model_dump()) for item in request.bars)
    steel_area = sum(bar.area_mm2 for bar in bars)
    if isinstance(geometry, RectangularInteractionGeometryV1):
        gross = rectangular_properties(geometry.b_mm, geometry.D_mm)
        capacity = prepare_positioned_capacity(
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            pu_kn=request.pu_kn,
            fck_nmm2=fck,
            fy_nmm2=fy,
            bars=bars,
        )
    else:
        diameter = geometry.diameter_mm
        gross = circular_properties(diameter)
        puz = (
            0.45 * fck * (gross.area_mm2 - steel_area) + 0.75 * fy * steel_area
        ) / 1000
        capacity = prepare_section_capacity(
            CircularSection(diameter, fck, fy, bars), request.pu_kn, steel_area, puz
        )
    points = []
    issues = []
    if capacity is None:
        issues.append(
            StructuralIssueV1(
                "COLUMN.INTERACTION_DOMAIN_HELD",
                "pu_kn",
                "The supplied axial force does not have a resolved fixed-compression slice.",
            )
        )
    else:
        for index in range(request.point_count):
            angle = 2 * pi * index / request.point_count
            direction = 360 * index / request.point_count
            ray = capacity.ray(cos(angle), sin(angle))
            if ray is None:
                issues.append(
                    StructuralIssueV1(
                        "COLUMN.INTERACTION_RAY_HELD",
                        f"rays.{index}",
                        "The supplied direction does not have a unique equilibrated capacity.",
                    )
                )
            points.append(
                {
                    "angle_deg": direction,
                    **(asdict(ray) if ray is not None else {"capacity_knm": None}),
                }
            )
    result = canonical_family_result(
        request,
        {
            "pu_kn": request.pu_kn,
            "steel_area_mm2": steel_area,
            "puz_kn": capacity.puz_kn if capacity else None,
            "gross": asdict(gross),
            "transformed": asdict(
                transformed_properties(gross, bars, request.modular_ratio)
            ),
            "rays": points,
            "member_acceptance": "NOT_EVALUATED",
            "detailing_acceptance": "NOT_EVALUATED",
        },
        workflow_id=WORKFLOW,
        engineering_status=EngineeringStatus.HOLD if issues else EngineeringStatus.PASS,
        limitations=(
            "PASS confirms the declared section slice has resolved signed capacity points.",
            "Elastic properties use the supplied modular ratio and gross uncracked concrete.",
            "Cracked properties, member stability, reinforcement restraint and fabrication require separate checks.",
        ),
        provenance=("IS 456:2000 Cl. 38.1 and 39.6; discrete strain compatibility.",),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def render_interaction_slice_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Show the signed points and property axes of the checked section.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        A checked interaction slice.

    Returns
    -------
    str
        HTML with the input identity, signed points and section properties.

    Raises
    ------
    TypeError
        The result is from a different workflow.

    Examples
    --------
    >>> callable(render_interaction_slice_html)
    True

    Limitations
    -----------
    Rendering uses the supplied result without another calculation.

    Provenance
    ----------
    Bound to the same request identity as the JSON result.
    """
    if (
        not isinstance(result, CanonicalFamilyResultV1)
        or result.workflow_id != WORKFLOW
    ):
        raise TypeError("result must be a column interaction slice")
    data = result.calculation
    rows = []
    for ray in data["rays"]:
        values = (
            ray["angle_deg"],
            ray.get("mx_knm"),
            ray.get("my_knm"),
            ray.get("capacity_knm"),
        )
        rows.append(
            "<tr>"
            + "".join(
                f"<td>{value:.3f}</td>" if value is not None else "<td>Held</td>"
                for value in values
            )
            + "</tr>"
        )
    properties = []
    for name in ("gross", "transformed"):
        fields = "".join(
            f"<li>{key} = {value:.3f}</li>" for key, value in data[name].items()
        )
        properties.append(f"<h2>{name.title()} properties</h2><ul>{fields}</ul>")
    identity = result.envelope.result_identity
    label = html.escape(result.identity.case_id)
    limitations = "".join(
        f"<li>{html.escape(item)}</li>" for item in result.limitations
    )
    issues = "".join(f"<li>{html.escape(item.message)}</li>" for item in result.issues)
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Column interaction {label}</title>
<h1>Column interaction {label}</h1>
<p>Section slice {result.engineering_status.value} · Compression {data['pu_kn']:.3f} kN · Qualified review required</p>
<p>Input identity <code>{identity.input_hash if identity else ""}</code></p>
{''.join(properties)}
<h2>Signed interaction points</h2>
<table><thead><tr><th>Angle (deg)</th><th>Mx (kN·m)</th><th>My (kN·m)</th>
<th>Capacity (kN·m)</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Scope and issues</h2><ul>{limitations}{issues}</ul></html>"""
