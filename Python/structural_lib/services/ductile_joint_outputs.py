"""Checked fabrication views for regular interior and exterior joints.

This module only projects facts already checked by :mod:`ductile_joint`.  In
particular a calculation from another request is useful diagnostic evidence,
but is never drawing or schedule authority.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Mapping
from html import escape
from io import StringIO
from typing import TYPE_CHECKING, Any

from structural_lib.services.bbs import calculate_bar_weight
from structural_lib.services.contracts.ductile_joint import (
    DuctileExteriorJointRequestV1,
)
from structural_lib.services.ductile_exterior_joint_outputs import (
    render_exterior_joint_bbs_csv,
    render_exterior_joint_report_html,
    render_exterior_joint_svg,
)

if TYPE_CHECKING:
    from .ductile_joint import DuctileJointResultV1, JointRequest


def _request(result: DuctileJointResultV1) -> dict[str, Any]:
    return result.request.model_dump(mode="json")


def _checked(result: DuctileJointResultV1, current: JointRequest | None) -> bool:
    return (
        result.status == "PASS"
        and current is not None
        and result.artifacts_match(current)
    )


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _g(data: Mapping[str, Any], key: str, default: str = "—") -> str:
    value = data.get(key)
    return (
        default
        if value is None
        else f"{value:g}" if isinstance(value, (int, float)) else _text(value)
    )


def _tie_path(mark: str, tie: Mapping[str, Any]) -> str:
    """Return an actual plan path for a C-TX/C-TY open cross-tie."""
    stems = tie["stem_xy_mm"]
    centres = tie["bend_centres_xy_mm"]
    ends = tie["arc_end_xy_mm"]
    tails = tie["tail_end_xy_mm"]
    (sx, sy), (ex, ey) = stems
    (c1x, c1y), (c2x, c2y) = centres
    (a1x, a1y), (a2x, a2y) = ends
    (t1x, t1y), (t2x, t2y) = tails
    # The checked geometry supplies the actual tangent/end points.  Radius is
    # the distance from each bend centre to its arc end.
    r1 = ((a1x - c1x) ** 2 + (a1y - c1y) ** 2) ** 0.5
    r2 = ((a2x - c2x) ** 2 + (a2y - c2y) ** 2) ** 0.5
    return (
        f'<path data-bar-mark="{_text(mark)}" data-plane-offset-mm="{tie["plane_offset_mm"]:g}" '
        f'd="M {t1x:g} {t1y:g} L {a1x:g} {a1y:g} A {r1:g} {r1:g} 0 0 1 {sx:g} {sy:g} '
        f'L {ex:g} {ey:g} A {r2:g} {r2:g} 0 0 1 {a2x:g} {a2y:g} L {t2x:g} {t2y:g}" '
        'fill="none" stroke="#7e22ce" stroke-width="3"><title>'
        f"{_text(mark)} checked open cross-tie</title></path>"
    )


def render_joint_svg(
    result: DuctileJointResultV1, *, current: JointRequest | None = None
) -> str | None:
    """Render the checked local joint plan and both principal sections.

    Parameters
    ----------
    result : DuctileJointResultV1
        Captured joint calculation.
    current : DuctileJointRequestV1 or None
        Explicit current request used to verify the drawing identity.
    Returns
    -------
    str or None
        SVG for a current passing joint. Other dispositions yield None.
    Raises
    ------
    AttributeError
        The supplied result lacks the public joint result attributes.
    Examples
    --------
    See Python/examples/ductile_interior_joint.py.
    Limitations
    -----------
    Draws the joint cage and the checked local beam continuations.
    Provenance
    ----------
    DUCT01 checked cage and action revision.
    """
    if not _checked(result, current):
        return None
    if isinstance(current, DuctileExteriorJointRequestV1):
        return render_exterior_joint_svg(result)
    request, data = _request(result), result.calculation
    placement = data["placement"]
    marks = placement["column_transverse_joint_marks"]
    width = request["column_width_mm"]
    joint_depth = request["joint_depth_mm"]
    axes = placement["column_longitudinal_axes_xy_mm"]
    hoop_lo, hoop_hi = placement["column_hoop_axis_bounds_mm"]
    hoop_corner = placement["column_hoop_corner_centre_axes_mm"]
    hoop_rise = placement["column_hoop_closure_rise_mm"]
    member = request["joint_id"]
    identity = f"input {result.input_hash} · action {request['action_revision']} · cage {request['cage_action_revision']}"

    bar_radius = request["column_bar_mm"] / 2.0
    bars = "".join(
        f'<g data-bar-id="C-{index}" data-x-mm="{x:g}" data-y-mm="{y:g}" '
        f'data-radius-mm="{bar_radius:g}"><title>C-{index}: ({x:g}, {y:g}) mm; Ø{2 * bar_radius:g}</title>'
        f'<circle cx="{x:g}" cy="{y:g}" r="{bar_radius:g}" fill="#172b4d"/>'
        f'<path d="M {x - bar_radius:g} {y:g} H {x + bar_radius:g} M {x:g} {y - bar_radius:g} '
        f'V {y + bar_radius:g}" stroke="#f3f6f8" stroke-width="2"/></g>'
        for index, (x, y) in enumerate(axes, start=1)
    )
    bend_radius = request["column_link_centre_radius_mm"]
    hook_tail = request["column_hook_tail_mm"]
    hook_ramp = request["column_hook_ramp_length_mm"]
    # The three plain bends form the body. Both closure ends turn southeast
    # around the same NW corner bar in distinct vertical planes.
    c, h = hoop_corner
    tangent = bend_radius / math.sqrt(2)
    tail_run = hook_tail / math.sqrt(2)
    hoop = (
        f'<path data-bar-mark="C-H" data-shape="hoop-body" '
        f'd="M {c:g} {hoop_lo:g} H {h:g} A {bend_radius:g} {bend_radius:g} 0 0 1 '
        f"{hoop_hi:g} {c:g} V {h:g} A {bend_radius:g} {bend_radius:g} 0 0 1 "
        f"{h:g} {hoop_hi:g} H {c:g} A {bend_radius:g} {bend_radius:g} 0 0 1 "
        f'{hoop_lo:g} {h:g} V {c:g}" fill="none" stroke="#17706d" stroke-width="3"/>'
        f'<path data-bar-mark="C-H" data-hook-angle-deg="135" data-hook="raised" '
        f'data-bend-radius-mm="{bend_radius:g}" data-hook-tail-mm="{hook_tail:g}" '
        f'data-hook-ramp-mm="{hook_ramp:g}" data-hook-rise-mm="{hoop_rise:g}" data-plane-rise-mm="{hoop_rise:g}" '
        f'd="M {c:g} {hoop_lo:g} A {bend_radius:g} {bend_radius:g} 0 0 0 '
        f"{c - tangent:g} {c + tangent:g} L "
        f'{c - tangent + tail_run:g} {c + tangent + tail_run:g}" '
        f'fill="none" stroke="#17706d" stroke-width="3" stroke-dasharray="6 3"><title>'
        f"C-H raised return · 135° · tail {hook_tail:g} mm</title></path>"
        f'<path data-bar-mark="C-H" data-hook-angle-deg="135" data-hook="base" '
        f'data-bend-radius-mm="{bend_radius:g}" data-hook-tail-mm="{hook_tail:g}" '
        f'data-hook-ramp-mm="{hook_ramp:g}" data-hook-rise-mm="{hoop_rise:g}" data-plane-rise-mm="0" '
        f'd="M {hoop_lo:g} {c:g} A {bend_radius:g} {bend_radius:g} 0 0 1 '
        f"{c + tangent:g} {c - tangent:g} L "
        f'{c + tangent + tail_run:g} {c - tangent + tail_run:g}" '
        f'fill="none" stroke="#17706d" stroke-width="3"><title>C-H base return · 135° · tail {hook_tail:g} mm</title></path>'
        f'<line x1="{c:g}" x2="{c + hook_ramp:g}" y1="{hoop_lo:g}" y2="{hoop_lo:g}" '
        f'data-closure-ramp-mm="{hook_ramp:g}" stroke="#17706d" stroke-width="5" stroke-dasharray="3 3">'
        f"<title>C-H closure ramp · rise {hoop_rise:g} mm over {hook_ramp:g} mm</title></line>"
    )
    ties = _tie_path("C-TX", marks["C-TX"]) + _tie_path("C-TY", marks["C-TY"])
    x_hoop, y_hoop = (
        placement["beam_hoop_sections"]["X"],
        placement["beam_hoop_sections"]["Y"],
    )
    x_across = x_hoop["outer_across_axis_bounds_mm"]
    y_across = y_hoop["outer_across_axis_bounds_mm"]
    seats = "".join(
        (
            f'<line data-seat="X-minus" x1="0" x2="0" y1="{x_across[0]:g}" y2="{x_across[1]:g}"/>',
            f'<line data-seat="X-plus" x1="{width:g}" x2="{width:g}" y1="{x_across[0]:g}" y2="{x_across[1]:g}"/>',
            f'<line data-seat="Y-minus" x1="{y_across[0]:g}" x2="{y_across[1]:g}" y1="0" y2="0"/>',
            f'<line data-seat="Y-plus" x1="{y_across[0]:g}" x2="{y_across[1]:g}" y1="{width:g}" y2="{width:g}"/>',
        )
    )
    corridors = "".join(
        f'<path d="M 0 {axis:g} H {width:g} M {axis:g} 0 V {width:g}" stroke="#bd6421" '
        'stroke-width="1" stroke-dasharray="4 5" fill="none"/>'
        for axis in request["beam_axis_across_column_mm"]
    )
    plan = (
        f'<g data-view="plan" transform="translate(35 75) scale({520 / width:g})"><rect width="{width:g}" height="{width:g}" '
        'fill="#f3f6f8" stroke="#172b4d"/><g stroke="#bd6421" stroke-width="5">'
        + seats
        + "</g><g>"
        + corridors
        + hoop
        + ties
        + bars
        + "</g>"
        f'<text x="0" y="-18">Plan · {width:g} × {width:g} mm · 8 column bars</text>'
        f'<text x="0" y="{width + 22:g}" font-size="11">Four beam-link seats; C-H / C-TX / C-TY planes: 0 / '
        f'{marks["C-TX"]["plane_offset_mm"]:g} / {marks["C-TY"]["plane_offset_mm"]:g} mm</text></g>'
    )
    section_x, section_w, section_h = 600, 460, 245
    section_levels = {"X": 86, "Y": 397}
    continuation = request["beam_uninterrupted_development_mm"]
    scale_x = section_w / (2 * continuation + width)
    joint_x = section_x + continuation * scale_x
    joint_w = width * scale_x
    pieces: list[str] = []
    for mark, tie in marks.items():
        for ordinal, station in enumerate(tie["stations_mm"], start=1):
            y = section_levels["X"] + section_h * station / joint_depth
            pieces.append(
                f'<line x1="{joint_x:g}" x2="{joint_x + joint_w:g}" y1="{y:g}" y2="{y:g}" '
                f'stroke="#17706d" data-bar-mark="{_text(mark)}" data-station-mm="{station:g}" '
                f'data-piece="{ordinal}"><title>{_text(mark)} piece {ordinal} at {station:g} mm</title></line>'
            )
    beam_levels: dict[str, list[str]] = {"X": [], "Y": []}
    for plane, paths in placement["beam_bar_paths"].items():
        section_y = section_levels[plane]
        for bar in paths:
            level = bar["depth_mm"]
            start, end = bar["joint_relative_axial_interval_mm"]
            y = section_y + section_h * level / joint_depth
            beam_levels[plane].append(
                f'<line x1="{section_x + (start + continuation) * scale_x:g}" x2="{section_x + (end + continuation) * scale_x:g}" y1="{y:g}" y2="{y:g}" '
                f'stroke="#bd6421" stroke-dasharray="4 2" data-beam-plane="{_text(plane)}" '
                f'data-section-plane="{_text(plane)}" data-bar-id="{_text(bar["bar_id"])}" '
                f'data-path-start-mm="{start:g}" data-path-end-mm="{end:g}" '
                f'data-across-mm="{bar["across_axis_mm"]:g}" data-relative-level-mm="{level:g}"/>'
            )
    row_depths = {
        plane: " / ".join(
            f"{level:g}" for level in sorted({bar["depth_mm"] for bar in paths})
        )
        for plane, paths in placement["beam_bar_paths"].items()
    }
    transverse_piece_count = sum(len(tie["stations_mm"]) for tie in marks.values())
    elevations = "".join(
        f'<g data-view="elevation" data-section-plane="{plane}">'
        f'<text x="{section_x:g}" y="{section_y - 12:g}">{plane} section · bars at {row_depths[plane]} mm from top</text>'
        f'<rect x="{section_x:g}" y="{section_y:g}" width="{section_w:g}" height="{section_h:g}" '
        'fill="#f3f6f8" stroke="#172b4d"/>'
        f'<rect x="{joint_x:g}" y="{section_y:g}" width="{joint_w:g}" height="{section_h:g}" fill="#e3eceb" stroke="#172b4d"/>'
        + "".join(beam_levels[plane])
        + ("".join(pieces) if plane == "X" else "")
        + f'<text x="{section_x:g}" y="{section_y + section_h + 22:g}" font-size="11">'
        f"{continuation:g} mm continuation each side · {joint_depth:g} mm joint depth"
        + (f" · {transverse_piece_count} transverse pieces" if plane == "X" else "")
        + "</text></g>"
        for plane, section_y in section_levels.items()
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1095 680" role="img" aria-labelledby="joint-title">'
        f'<title id="joint-title">Checked DUCT01 joint { _text(member) }</title>'
        f"<desc>{_text(identity)}. Local beam continuation axes are evidence only, not full-span cuts.</desc>"
        f'<text x="25" y="28" font-family="sans-serif" font-size="16">{_text(member)} · checked joint fabrication</text>'
        f'<text x="25" y="48" font-family="sans-serif" font-size="11">{_text(identity)}</text>'
        f'<g font-family="sans-serif" font-size="12">{plan}{elevations}</g></svg>'
    )


def render_joint_bbs_csv(
    result: DuctileJointResultV1, *, current: JointRequest | None = None
) -> str | None:
    """Render the checked joint hoop and cross-ties as CSV.

    Parameters
    ----------
    result : DuctileJointResultV1
        Captured joint calculation.
    current : DuctileJointRequestV1 or None
        Explicit current request used to verify the schedule identity.
    Returns
    -------
    str or None
        Schedule in mm and kg for a current passing joint.
    Raises
    ------
    AttributeError
        The supplied result lacks the public joint result attributes.
    Examples
    --------
    See Python/examples/ductile_interior_joint.py.
    Limitations
    -----------
    Schedules the checked local joint hoop and two cross-tie marks.
    Provenance
    ----------
    DUCT01 checked cage and action revision.
    """
    if not _checked(result, current):
        return None
    if isinstance(current, DuctileExteriorJointRequestV1):
        return render_exterior_joint_bbs_csv(result)
    request, marks = (
        _request(result),
        result.calculation["placement"]["column_transverse_joint_marks"],
    )
    out = StringIO()
    fields = (
        "joint_id",
        "action_revision",
        "cage_action_revision",
        "input_hash",
        "bar_mark",
        "diameter_mm",
        "quantity",
        "shape",
        "bend_radius_mm",
        "hook_tail_mm",
        "hook_ramp_mm",
        "hook_rise_mm",
        "girth_mm",
        "cut_length_mm",
        "total_length_mm",
        "total_weight_kg",
        "units",
    )
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    dia = request["column_link_mm"]
    for mark in ("C-H", "C-TX", "C-TY"):
        item = marks[mark]
        total = item["quantity"] * item["cut_mm"]
        writer.writerow(
            {
                "joint_id": request["joint_id"],
                "action_revision": request["action_revision"],
                "cage_action_revision": request["cage_action_revision"],
                "input_hash": result.input_hash,
                "bar_mark": mark,
                "diameter_mm": dia,
                "quantity": item["quantity"],
                "shape": (
                    "closed_hoop_2x135_hooks"
                    if mark == "C-H"
                    else "open_cross_tie_2x135_hooks"
                ),
                "bend_radius_mm": request["column_link_centre_radius_mm"],
                "hook_tail_mm": request["column_hook_tail_mm"],
                "hook_ramp_mm": (
                    request["column_hook_ramp_length_mm"] if mark == "C-H" else ""
                ),
                "hook_rise_mm": request["column_hook_rise_mm"] if mark == "C-H" else "",
                "girth_mm": item["cut_mm"],
                "cut_length_mm": item["cut_mm"],
                "total_length_mm": total,
                "total_weight_kg": calculate_bar_weight(dia, total, round_weight=False),
                "units": "mm, kg",
            }
        )
    return out.getvalue()


def render_joint_html(
    result: DuctileJointResultV1, *, current: JointRequest | None = None
) -> str:
    """Render the joint's governing checks and diagnostics.

    Parameters
    ----------
    result : DuctileJointResultV1
        Captured joint calculation.
    current : DuctileJointRequestV1 or None
        Explicit current request used to verify eligibility for the embedded SVG.
    Returns
    -------
    str
        HTML with the governing checks, issues and eligible drawing.
    Raises
    ------
    AttributeError
        The supplied result lacks the public joint result attributes.
    Examples
    --------
    See Python/examples/ductile_interior_joint.py.
    Limitations
    -----------
    Reports the evaluated joint and the supplied action basis.
    Provenance
    ----------
    DUCT01 checked result, including the recorded IS 13920 amendment chain.
    """
    request, data = _request(result), result.calculation
    if request["schema_version"] == "ductile-exterior-joint/v1":
        return render_exterior_joint_report_html(result)
    governing = data.get("governing", {})
    anchor = data.get("anchorage", {})
    placement = data.get("placement", {})
    confinement = placement.get("confinement", {})
    clearances = placement.get("minimum_clearances_mm", {})
    governing_rows = []
    for check, label, demand, resistance, unit in (
        (
            "beam_capacity_shear",
            "Beam capacity shear",
            "demand_kn",
            "accepted_capacity_kn",
            "kN",
        ),
        (
            "column_capacity_shear",
            "Column capacity shear",
            "demand_kn",
            "accepted_capacity_kn",
            "kN",
        ),
        (
            "scwb",
            "Strong-column weak-beam",
            "required_column_capacity_knm",
            "available_column_capacity_knm",
            "kN·m",
        ),
        ("joint_shear", "Joint shear stress", "stress_mpa", "strength_mpa", "MPa"),
    ):
        row = governing.get(check)
        if row is not None:
            governing_rows.append(
                f'<tr data-check="{check}"><th>{label}</th><td>{_g(row, "direction")}</td>'
                f'<td>{_g(row, "combination_id")} {_g(row, "side", "")}</td>'
                f"<td>{_g(row, demand)} {unit}</td><td>{_g(row, resistance)} {unit}</td>"
                f'<td>{100 * row["utilization"]:.2f}%</td></tr>'
            )
    checks_table = (
        "<table><thead><tr><th>Check</th><th>Direction</th><th>Combination and end</th>"
        "<th>Demand</th><th>Capacity</th><th>Utilization</th></tr></thead>"
        f'<tbody>{"".join(governing_rows)}</tbody></table>'
        if governing_rows
        else "<p>Strength results are unavailable.</p>"
    )
    issues = (
        "".join(
            f"<li><code>{_text(issue.code)}</code> {_text(issue.message)}</li>"
            for issue in result.issues
        )
        or "<li>None</li>"
    )
    signed = (
        "".join(
            f"<li>{_text(direction)}: joint V={_g(row, 'signed_joint_shear_kn')} kN; compatible column V="
            f"{_g(row, 'signed_compatible_column_shear_kn')} kN; u={_g(row, 'utilization')}</li>"
            for direction, item in data.get("directions", {}).items()
            for row in [item.get("joint_shear", {})]
        )
        or "<li>Unavailable</li>"
    )
    drawing = render_joint_svg(result, current=current)
    evidence = (
        drawing
        if drawing is not None
        else "<p>Drawing and BBS require a current passing check.</p>"
    )
    clearance_rows = (
        "".join(
            f'<li>{_text(label.replace("_", " "))} {_g(clearances, label)} mm</li>'
            for label in clearances
        )
        or "<li>Unavailable</li>"
    )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Interior joint check</title><main>'
        f"<h1>DUCT01 interior joint · {_text(request.get('joint_id', 'unidentified'))}</h1>"
        f"<p>Status <strong>{_text(result.status)}</strong> · input <code>{_text(result.input_hash)}</code> · "
        f"action revision <code>{_text(request.get('action_revision', '—'))}</code> · cage revision "
        f"<code>{_text(request.get('cage_action_revision', '—'))}</code>.</p>"
        f"<p>IS 13920:2016 with Amendments 1 and 2. {_text(request.get('applicability_reference') or '')}</p>"
        f"<h2>Governing checks</h2>{checks_table}"
        f"<h2>Signed directions</h2><ul>{signed}</ul>"
        f"<h2>Anchorage and confinement</h2><p>Development {_g(anchor, 'adjacent_member_development_provided_mm_each_side')} / "
        f"{_g(anchor, 'adjacent_member_development_required_mm')} mm each side; joint length "
        f"{_g(anchor, 'joint_length_in_each_plane_mm')} / {_g(anchor, 'joint_width_required_mm')} mm. "
        f"Confinement pitch {_g(confinement, 'joint_pitch_mm')} / {_g(confinement, 'joint_pitch_limit_mm')} mm. "
        f"Leg area {_g(confinement, 'ash_provided_per_leg_mm2')} / {_g(confinement, 'joint_ash_required_mm2')} mm².</p>"
        f"<h2>Clearances</h2><ul>{clearance_rows}</ul><h2>Issues</h2><ul>{issues}</ul>{evidence}</main></html>"
    )
