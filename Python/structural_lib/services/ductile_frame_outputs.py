"""Render the same checked PROJECT03 frame geometry and source identity."""

from __future__ import annotations

import csv
from html import escape
from io import StringIO
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from structural_lib.services.contracts.ductile_frame import DuctileFrameRequestV1
    from structural_lib.services.ductile_frame import DuctileFrameResultV1


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def render_frame_html(result: DuctileFrameResultV1) -> str:
    """Render a report for both passing and refused frame cuts.

    Parameters
    ----------
    result : DuctileFrameResultV1
        Captured source, checks and diagnostic evidence.
    Returns
    -------
    str
        HTML report bound to the checked revision and geometry.
    Raises
    ------
    AttributeError
        An invalid result object was supplied.
    Examples
    --------
    See Python/examples/ductile_frame_cut.py.
    Limitations
    -----------
    Reports the bounded structural cut and construction evidence status.
    Provenance
    ----------
    PROJECT03 DUCT01 and DUCT02 plus the common member checks.
    """
    req, data = result.request, result.calculation
    name = _text(req.project_id)
    errors = "".join(
        f"<li>{_text(issue.code)} · {_text(issue.message)}</li>"
        for issue in result.issues
    )
    source = data.get("source_balances", {})
    action_rows = "".join(
        f"<tr><td>{_text(combo)}</td><td>{_text(req.actions[combo].direction)}</td>"
        f"<td>{req.actions[combo].beams['BX12'].vertical_reactions_kn[0]:.3f}</td>"
        f"<td>{req.actions[combo].beams['BX12'].vertical_reactions_kn[1]:.3f}</td>"
        f"<td>{'PASS' if record['pass'] else 'FAIL'}</td></tr>"
        for combo, record in source.items()
    )
    member_rows = ""
    shared = data.get("shared_beam", {})
    if "strength" in shared:
        governing = shared["strength"]["governing"]
        for family in ("flexure", "shear"):
            control = governing[family]
            member_rows += (
                f"<tr><td>BX12 {family}</td><td>{_text(control['combination_id'])}</td>"
                f"<td>{_text(control['station'])}</td><td>{control[f'{family}_utilization']:.3f}</td></tr>"
            )
    for member, column in data.get("column_legs", {}).items():
        for family in ("flexure", "shear"):
            control = column[f"governing_{family}"]
            demand = (
                control["conservative_linear_biaxial_utilization"]
                if family == "flexure"
                else control["shear_utilization"]
            )
            member_rows += (
                f"<tr><td>{_text(member)} {family}</td><td>{_text(control['combination_id'])}</td>"
                f"<td>{_text(control.get('end', 'leg'))}</td><td>{demand:.3f}</td></tr>"
            )
    joint_rows = "".join(
        f"<li>{_text(name)} · {_text(joint['status'])} · signed joint shear "
        f"{_text(joint.get('governing', {}).get('joint_shear', {}).get('direction', 'pending'))}</li>"
        for name, joint in data.get("joints", {}).items()
    )
    accounting = data.get("artifact_reconciliation", {})
    artifacts = ""
    if accounting and result.status == "PASS":
        links = shared["links"]
        artifacts = (
            "<h2>Checked reinforcement</h2>"
            f"<p>{accounting['unique_cut_piece_count']} resolved cuts, "
            f"{accounting['cut_weight_kg']:.2f} kg. "
            f"Compaction opening {links['compaction_diameter_mm']:.2f} mm. "
            f"Minimum hoop-to-longitudinal clearance {links['hoop_to_longitudinal']['adverse_clearance_mm']:.2f} mm.</p>"
        )
    admission = (
        "<p>Design review scope. Site insertion, temporary supports and the boundary "
        "anchorage cage require construction evidence. The five cut boundary beams "
        "contribute actions and remain outside member design and scheduling.</p>"
    )
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{name} frame check</title></head>'
        f"<body><h1>{name} ductile frame cut</h1><p>{result.status} · "
        f"action revision {_text(req.action_revision)} · <code>{result.input_hash}</code></p>"
        + admission
        + (f"<h2>Issues</h2><ul>{errors}</ul>" if errors else "")
        + (
            f"<p>{_text(data['cage_diagnostic'])}</p>"
            if "cage_diagnostic" in data
            else ""
        )
        + (
            "<h2>Source equilibrium</h2><table><tr><th>Combination</th><th>Direction</th>"
            "<th>J1 reaction (kN)</th><th>J2 reaction (kN)</th><th>Balance</th></tr>"
            f"{action_rows}</table>"
            if action_rows
            else ""
        )
        + (f"<h2>Joint checks</h2><ul>{joint_rows}</ul>" if joint_rows else "")
        + (
            "<h2>Governing member checks</h2><table><tr><th>Member</th><th>Combination</th>"
            "<th>Location</th><th>Utilization</th></tr>"
            f"{member_rows}</table>"
            if member_rows
            else ""
        )
        + artifacts
        + "</body></html>"
    )


def _frame_view(data: dict[str, Any]) -> str:
    left = data["joint_action_requests"]["J1"]
    w = left["column_width_mm"]
    d = left["joint_depth_mm"]
    span = left["beam_clear_spans_mm"]["X"]["plus"]
    bars = data["shared_beam"]["longitudinal"]["bars"]
    west = min(bar["west_end_project_x_mm"] for bar in bars)
    east = span + w
    scale = 820 / float(east - west)
    x0 = 70 - float(west) * scale
    y0 = 192

    def x(position: float) -> float:
        return x0 + position * scale

    def column(face: float, joint: str) -> str:
        heights = data["joint_action_requests"][joint]["column_clear_heights_mm"]
        graph_height = 95
        return (
            f'<rect data-joint="{joint}" x="{x(face):g}" y="{y0 - graph_height:g}" width="{w * scale:g}" '
            f'height="{d * scale + 2 * graph_height:g}" fill="#eff2f6" stroke="#42586b"/>'
            f'<text x="{x(face):g}" y="{y0 - 110:g}">{joint}</text>'
            f'<text x="{x(face):g}" y="{y0 - 97:g}">{heights["upper"]:g}/{heights["lower"]:g} mm legs</text>'
        )

    elements = [
        column(-w, "J1"),
        column(span, "J2"),
        f'<rect data-member="BX12" x="{x(0):g}" y="{y0:g}" '
        f'width="{span * scale:g}" height="{d * scale:g}" fill="#e4f0ef" stroke="#42586b"/>',
        f'<rect x="{x(west):g}" y="{y0:g}" width="{(-w - west) * scale:g}" height="{d * scale:g}" '
        'fill="none" stroke="#9aaab8" stroke-dasharray="5 3"/>',
        f'<text x="{x(0):g}" y="{y0 - 14:g}">BX12 · clear span {span:g} mm</text>',
        f'<text x="{x(west):g}" y="{y0 - 14:g}">West development and boundary continuation</text>',
    ]
    for bar in bars:
        depth = bar["depth_mm"]
        zbar = y0 + depth * scale
        bottom = bar["east_tail_end_z_mm"] < depth
        sweep = 0 if bottom else 1
        radius = bar["east_bend_end_x_mm"] - bar["east_tangent_x_mm"]
        z_tangent = y0 + (depth + (-radius if bottom else radius)) * scale
        elements.append(
            f'<path data-bar-id="{_text(bar["bar_id"])}" data-cut-mm="{bar["cut_mm"]:.9f}" '
            f'data-interior-path="{_text(bar["interior_joint_path_id"])}" '
            f'data-exterior-path="{_text(bar["exterior_joint_path_id"])}" '
            f'd="M{x(bar["west_end_project_x_mm"]):g},{zbar:g} L{x(bar["east_tangent_x_mm"]):g},{zbar:g} '
            f'A{radius * scale:g},{radius * scale:g} 0 0 {sweep} {x(bar["east_bend_end_x_mm"]):g},{z_tangent:g} '
            f'V{y0 + bar["east_tail_end_z_mm"] * scale:g}" fill="none" stroke="#b36826" stroke-width="2"/>'
        )
    return "".join(elements)


def _grid_view(data: dict[str, Any]) -> str:
    """Elevation station strips and physical section shapes for all cut marks."""
    schedules = data["artifact_reconciliation"]["checked_tie_and_beam_cut_marks"]
    sections = data["artifact_reconciliation"]["column_tie_sections"]
    parts = []
    for index, member in enumerate(("BX12", "J1", "J2", *data["column_legs"])):
        marks = [
            (name, mark)
            for name, mark in schedules.items()
            if name.startswith(member + ":")
            or (member == "BX12" and name in ("BX12-O", "BX12-M"))
        ]
        y = 358 + 74 * index
        span = max(station for _, mark in marks for station in mark["stations_mm"])
        parts.append(
            f'<text x="40" y="{y - 13}">{_text(member)} · station strip in mm</text>'
        )
        for j, (name, mark) in enumerate(marks):
            lane = y + j * 13
            parts.append(
                f'<g data-mark="{_text(name)}" data-quantity="{mark["quantity"]}" '
                f'data-cut-mm="{mark["cut_mm"]:.9f}">'
                f'<text x="40" y="{lane + 4}">{_text(name)} · {mark["quantity"]} × Ø{mark["diameter_mm"]:g}</text>'
                f'<line x1="270" y1="{lane}" x2="935" y2="{lane}" stroke="#d5dce3"/>'
            )
            for station in mark["stations_mm"]:
                station_x = 270 + station * 665 / span
                parts.append(
                    f'<line data-station-mm="{station:g}" x1="{station_x:g}" x2="{station_x:g}" '
                    f'y1="{lane-4}" y2="{lane+4}" stroke="#2b7e77"/>'
                )
            parts.append("</g>")

    joint_calcs = data["joints"]
    for index, (name, joint) in enumerate(joint_calcs.items()):
        x0, y0 = 65 + 320 * index, 910
        scale = 192 / data["joint_action_requests"][name]["column_width_mm"]
        placement = joint["placement"]
        if name == "J1":
            path_lookup = {
                mark: geometry["local_centreline_xyz_mm"]
                for mark, geometry in sections["J1"].items()
            }
            axes = placement["column_longitudinal_axes_xy_mm"]
        else:
            path_lookup = {
                mark: geometry["local_centreline_polyline_mm"]
                for mark, geometry in placement["joint_tie_marks"].items()
            }
            axes = placement["column_axes_xy_mm"]
        parts.append(
            f'<text x="{x0}" y="{y0-12}">{_text(name)} actual joint link plan</text>'
        )
        for mark, path in path_lookup.items():
            coords = " ".join(f"{x0+scale*a:g},{y0+scale*b:g}" for a, b, _ in path)
            parts.append(
                f'<polyline data-plan-mark="{name}:{_text(mark)}" points="{coords}" '
                'fill="none" stroke="#2b7e77" stroke-width="2"/>'
            )
        parts.extend(
            f'<circle data-column-seat="{name}-{i}" cx="{x0+scale*a:g}" cy="{y0+scale*b:g}" '
            'r="4" fill="#33455a"/>'
            for i, (a, b) in enumerate(axes, 1)
        )
    x0, y0 = 710, 910
    left = data["joint_action_requests"]["J1"]
    scale = min(195 / left["column_width_mm"], 210 / left["joint_depth_mm"])
    parts.append(
        f'<text x="{x0}" y="{y0 - 12}">BX12 shared beam section · link return paths</text>'
    )
    for index, (mark, row) in enumerate(data["shared_beam"]["links"]["marks"].items()):
        shape = row["shape"]
        coords = " ".join(
            f"{x0 + scale * a:g},{y0 + scale * b:g}"
            for a, b, _ in shape["local_centreline_xyz_mm"]
        )
        colour = ("#2b7e77", "#9d6587")[index]
        parts.append(
            f'<polyline data-section-mark="{mark}" data-closure="{_text(shape["closure_corner"])}" '
            f'data-closure-rise-mm="{shape["closure_rise_left_mm"]:g}" points="{coords}" '
            f'fill="none" stroke="{colour}" stroke-width="2"><title>{mark}</title></polyline>'
        )
    for bar in data["shared_beam"]["longitudinal"]["bars"]:
        parts.append(
            f'<circle data-section-bar="{_text(bar["bar_id"])}" cx="{x0 + scale * bar["across_mm"]:g}" '
            f'cy="{y0 + scale * bar["depth_mm"]:g}" r="{0.5 * scale * bar["diameter_mm"]:g}" fill="#33455a"/>'
        )
    return "".join(parts)


def render_frame_svg(
    result: DuctileFrameResultV1, *, current: DuctileFrameRequestV1 | None = None
) -> str | None:
    """Render the current accepted frame cut and its checked reinforcement.

    Parameters
    ----------
    result : DuctileFrameResultV1
        Captured frame result.
    current : DuctileFrameRequestV1 or None
        Explicit current request that must match the checked identity.
    Returns
    -------
    str or None
        SVG for a passing current result.
    Raises
    ------
    AttributeError
        An invalid result object was supplied.
    Examples
    --------
    See Python/examples/ductile_frame_cut.py.
    Limitations
    -----------
    Design review drawing with explicitly labeled local scopes.
    Provenance
    ----------
    Same checked bar axes, marks and signed revision as the frame BBS.
    """
    if not result.artifacts_match(current):
        return None
    data = result.calculation
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1150" role="img" '
        'aria-labelledby="frame-title"><g font-family="sans-serif" font-size="11">'
        f'<title id="frame-title">{_text(result.request.project_id)} checked ductile frame cut</title>'
        f'<text x="40" y="26">{_text(result.request.project_id)} · design review · '
        f"{_text(result.request.action_revision)}</text>"
        f'<text x="40" y="47">Checked input {result.input_hash} · assembly evidence pending</text>'
        + _frame_view(data)
        + _grid_view(data)
        + "</g></svg>"
    )


def render_frame_bbs_csv(
    result: DuctileFrameResultV1, *, current: DuctileFrameRequestV1 | None = None
) -> str | None:
    """Return the reconciled local design schedule for a current frame result.

    Parameters
    ----------
    result : DuctileFrameResultV1
        Captured frame result.
    current : DuctileFrameRequestV1 or None
        Explicit current request that must match the checked identity.
    Returns
    -------
    str or None
        CSV with unique checked marks and local quantities.
    Raises
    ------
    AttributeError
        An invalid result object was supplied.
    Examples
    --------
    See Python/examples/ductile_frame_cut.py.
    Limitations
    -----------
    Design review quantities. Continuous column segments are listed with
    lengths in the report result and require boundary anchorage evidence.
    Provenance
    ----------
    Same resolved shapes and marks as the frame drawing.
    """
    if not result.artifacts_match(current):
        return None
    request = result.request
    output = StringIO()
    fields = (
        "project_id",
        "action_revision",
        "input_hash",
        "scope",
        "bar_mark",
        "quantity",
        "diameter_mm",
        "cut_length_mm",
        "total_length_mm",
        "total_mass_kg",
        "stations_mm",
        "bar_ids",
        "shape_evidence",
    )
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for name, row in result.calculation["artifact_reconciliation"][
        "checked_tie_and_beam_cut_marks"
    ].items():
        writer.writerow(
            {
                "project_id": request.project_id,
                "action_revision": request.action_revision,
                "input_hash": result.input_hash,
                "scope": "DESIGN_REVIEW",
                "bar_mark": name,
                "quantity": row["quantity"],
                "diameter_mm": row["diameter_mm"],
                "cut_length_mm": row["cut_mm"],
                "total_length_mm": row["total_length_mm"],
                "total_mass_kg": row["mass_kg"],
                "stations_mm": " ".join(
                    f"{station:g}" for station in row.get("stations_mm", [])
                ),
                "bar_ids": " ".join(row.get("bar_ids", [])),
                "shape_evidence": row["shape"].get(
                    "source", row["shape"].get("scope", name)
                ),
            }
        )
    return output.getvalue()
