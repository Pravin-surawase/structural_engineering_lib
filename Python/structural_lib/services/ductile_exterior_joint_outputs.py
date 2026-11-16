"""Projection-only checked outputs for the DUCT02 exterior joint.

Eligibility is deliberately owned by the public renderer.  These functions
only turn its already-admitted calculation evidence into local fabrication
views; they never infer a whole-member cut length.
"""

from __future__ import annotations

import csv
from collections.abc import Mapping
from html import escape
from io import StringIO
from typing import TYPE_CHECKING, Any

from structural_lib.services.bbs import calculate_bar_weight

if TYPE_CHECKING:
    from structural_lib.services.ductile_joint import DuctileJointResultV1


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _polyline(points: list[list[float]]) -> str:
    """Project checked local xyz samples into their plan x/y polyline."""
    return " ".join(f"{point[0]:g},{point[1]:g}" for point in points)


def _request(result: DuctileJointResultV1) -> Mapping[str, Any]:
    """Use the detached checked request, never a duplicated calculation field."""
    return result.request.model_dump(mode="json")


def render_exterior_joint_report_html(result: DuctileJointResultV1) -> str:
    """Return a complete diagnostic document for every exterior-joint result."""
    data = result.calculation
    request = _request(result)
    issues = (
        "".join(
            f"<li><code>{_text(issue.code)}</code> {_text(issue.message)}</li>"
            for issue in result.issues
        )
        or "<li>None recorded</li>"
    )
    heading = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>DUCT02 exterior joint {_text(request['joint_id'])}</title></head><body>"
        f"<h1>DUCT02 exterior joint · {_text(request['joint_id'])}</h1>"
        f"<p>Status <strong>{_text(result.status)}</strong> · input <code>{_text(result.input_hash)}</code> · "
        f"action <code>{_text(request['action_revision'])}</code> · cage <code>{_text(request['cage_action_revision'])}</code>.</p>"
    )
    if result.status != "PASS":
        checks = (
            "".join(
                f"<li>{_text(name)}: {_text(value)}</li>"
                for name, value in data.get("checks", {}).items()
            )
            or "<li>Not evaluated</li>"
        )
        return (
            heading
            + f"<p>Fabrication evidence withheld: {_text(data.get('reason', 'a required check did not pass'))}.</p>"
            + f"<h2>Issues</h2><ul>{issues}</ul><h2>Diagnostic checks</h2><ul>{checks}</ul></body></html>"
        )
    governing, placement, anchorage = (
        data["governing"],
        data["placement"],
        data["anchorage"],
    )
    joint, terminated = governing["joint_shear"], anchorage["terminated_X"]
    fit_rows = "".join(
        f"<li>{_text(name)}: {item['adverse_clearance_mm']:g} mm ({_text(' / '.join(item['parts']))})</li>"
        for name, item in placement["pair_clearances"].items()
    )
    return (
        heading
        + "<h2>Governing signed directions</h2>"
        + f"<p>Joint shear {_text(joint['direction'])}: V<sub>j</sub>={joint['signed_joint_shear_kn']:g} kN; compatible column V="
        f"{joint['signed_compatible_column_shear_kn']:g} kN; u={joint['utilization']:.4f}. SCWB {_text(governing['scwb']['direction'])}; "
        f"beam capacity shear {_text(governing['beam_capacity_shear']['combination_id'])} / {_text(governing['beam_capacity_shear']['side'])}.</p>"
        + "<h2>Governing capacity/stress values</h2>"
        + f"<ul><li>Beam shear: {governing['beam_capacity_shear']['demand_kn']:g} / {governing['beam_capacity_shear']['accepted_capacity_kn']:g} kN</li>"
        f"<li>Column shear: {governing['column_capacity_shear']['demand_kn']:g} / {governing['column_capacity_shear']['accepted_capacity_kn']:g} kN</li>"
        f"<li>Joint stress: {joint['stress_mpa']:.3f} / {joint['strength_mpa']:.3f} MPa</li>"
        f"<li>SCWB: {governing['scwb']['available_column_capacity_knm']:.3f} / {governing['scwb']['required_column_capacity_knm']:.3f} kNm</li></ul>"
        + "<h2>Anchorage, fit and compaction</h2>"
        + f"<p>Top/bottom adverse straight: {terminated['TOP']['adverse_straight_length_mm']:g} / {terminated['BOTTOM']['adverse_straight_length_mm']:g} mm; "
        f"required development {terminated['TOP']['required_mm']:g} mm; continuous-Y each side {anchorage['continuous_Y']['adverse_development_each_side_mm']:g} mm.</p>"
        + f"<p>Compaction corridor {placement['compaction_diameter_mm']:g} mm against a {request['compaction_head_mm']:g} mm head. Closure separation {placement['closure_adverse_separation_mm']:g} mm; "
        f"opposed-tail clearance {placement['opposed_parallel_tail_clear_mm']:g} mm against {placement['required_parallel_tail_clear_mm']:g} mm required.</p><ul>{fit_rows}</ul>"
        + f"<h2>Assembly and pending project evidence</h2><p>{_text(request.get('assembly') or 'Assembly evidence missing.')}</p>"
        + "<p>Scope: local exterior-joint cage, through-Y continuations, and X geometry beyond face only; not a whole-member cutting list. "
        "Pending: compatible project-frame actions, global seismic-system acceptance, and member fabrication beyond this local joint.</p></body></html>"
    )


def render_exterior_joint_svg(result: DuctileJointResultV1) -> str:
    """Render local plan, X hook section, Y paths, and tie stations faithfully."""
    data, request = result.calculation, _request(result)
    placement, marks = data["placement"], data["placement"]["joint_tie_marks"]
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    plan_scale = 380 / width
    scale = min(375 / width, 445 / depth)
    identity = f"input {result.input_hash} · action {request['action_revision']}"
    colours = {"C-W": "#17706d", "C-E": "#3461a0", "C-TX": "#924677"}
    ties = "".join(
        f'<polyline data-bar-mark="{_text(mark)}" data-quantity="{tie["quantity"]}" '
        f'data-stations-mm="{_text(",".join(f"{station:g}" for station in tie["stations_mm"]))}" '
        f'data-closure-offset-bends-deg="{_text(",".join(f"{bend:g}" for bend in tie["closure_offset_bends_deg"]))}" '
        f'data-closure-plane-offset-mm="{tie["closure_plane_offset_mm"]:g}" '
        f'data-closure-coordinates-xyz-mm="{_text(str(tie["local_centreline_polyline_mm"]))}" '
        f'points="{_polyline(tie["local_centreline_polyline_mm"])}" fill="none" stroke="{colours[mark]}" '
        f'stroke-width="{tie["diameter_mm"]:g}"><title>{_text(mark)} · local checked centreline</title></polyline>'
        for mark, tie in marks.items()
    )
    bars = "".join(
        f'<circle data-bar-id="C-{index}" cx="{x:g}" cy="{y:g}" r="{request["column_bar_mm"] / 2:g}" fill="#172b4d"/>'
        for index, (x, y) in enumerate(placement["column_axes_xy_mm"], start=1)
    )
    plan = (
        f'<text x="35" y="77">Plan · +X exterior face · x→, y↓ · {width:g} × {width:g} mm</text>'
        f'<g data-view="plan" transform="translate(35 90) scale({plan_scale:g})">'
        f'<rect width="{width:g}" height="{width:g}" fill="#f3f6f8" stroke="#172b4d"/>'
        + ties
        + bars
        + "</g>"
    )
    tie_legend = "".join(
        f'<text x="{35 + index * 128}" y="497" fill="{colours[mark]}">'
        f'{_text(mark)} · Ø{tie["diameter_mm"]:g} · {tie["quantity"]} pieces</text>'
        for index, (mark, tie) in enumerate(marks.items())
    )
    sx, sy = 475, 90

    def project_xz(xyz: list[float]) -> tuple[float, float]:
        return sx + xyz[0] * scale, sy + xyz[2] * scale

    x_paths: list[str] = []
    for hook in placement["x_hook_paths"]:
        start, bend_start = (
            hook["start_at_inner_face_xyz_mm"],
            hook["bend_start_xyz_mm"],
        )
        bend_end, tail, centre = (
            hook["bend_end_xyz_mm"],
            hook["tail_end_xyz_mm"],
            hook["bend_centre_xyz_mm"],
        )
        radius, sweep = hook["bend_centreline_radius_mm"], int("TOP" in hook["bar_id"])
        a, b, c, d = (
            project_xz(start),
            project_xz(bend_start),
            project_xz(bend_end),
            project_xz(tail),
        )
        x_paths.append(
            f'<path data-bar-id="{_text(hook["bar_id"])}" data-local-beyond-face="true" data-bend-radius-mm="{radius:g}" '
            f'data-bend-centre-xyz-mm="{_text(str(centre))}" data-tail-end-xyz-mm="{_text(str(tail))}" '
            f'd="M {a[0]:g} {a[1]:g} L {b[0]:g} {b[1]:g} A {radius * scale:g} {radius * scale:g} 0 0 {sweep} {c[0]:g} {c[1]:g} L {d[0]:g} {d[1]:g}" '
            f'fill="none" stroke="#bd6421" stroke-width="3"><title>{_text(hook["bar_id"])} local hook</title></path>'
        )
    x_section = (
        f'<g data-view="x-section"><rect x="{sx:g}" y="{sy:g}" width="{width * scale:g}" height="{depth * scale:g}" fill="#f3f6f8" stroke="#172b4d"/>'
        + "".join(x_paths)
        + f'<text x="{sx:g}" y="77">X section · +X exterior face · top/soffit z↓</text></g>'
    )
    x_caption = (
        f'<text x="{sx:g}" y="{sy + depth * scale + 19:g}">4 Ø'
        f'{request["beam_bar_mm"]["X"]:g} each face · 90° radius '
        f'{request["x_hook_radius_mm"]:g} mm</text>'
    )
    yx, yy = 35, 590
    extension = request["y_straight_each_side_mm"]
    ys = 815 / (width + 2 * extension)
    depth_scale = 275 / depth
    near_face = yx + extension * ys
    far_face = near_face + width * ys
    y_paths = "".join(
        f'<line data-bar-id="{_text(path["bar_id"])}" data-path-start-xyz-mm="{_text(str(path["points_mm"][0]))}" '
        f'data-path-end-xyz-mm="{_text(str(path["points_mm"][1]))}" data-level-z-mm="{path["points_mm"][0][2]:g}" '
        f'x1="{yx + (path["points_mm"][0][1] + extension) * ys:g}" x2="{yx + (path["points_mm"][1][1] + extension) * ys:g}" '
        f'y1="{yy + path["points_mm"][0][2] * depth_scale:g}" y2="{yy + path["points_mm"][1][2] * depth_scale:g}" stroke="#172b4d" stroke-width="3"/>'
        for path in placement["y_through_paths"]
    )
    y_section = (
        f'<g data-view="y-elevation"><text x="{yx:g}" y="573">Y through bars · 4 Ø{request["beam_bar_mm"]["Y"]:g} each face · y→ · z↓</text>'
        f'<rect x="{near_face:g}" y="{yy:g}" width="{far_face - near_face:g}" height="275" '
        f'fill="#f3f6f8" stroke="#172b4d"/>{y_paths}</g>'
    )
    tx, ty = 915, sy
    tie_stations = "".join(
        f'<line data-bar-mark="{_text(mark)}" data-station-mm="{station:g}" x1="{tx:g}" x2="{tx + 105:g}" '
        f'y1="{ty + station * scale:g}" y2="{ty + station * scale:g}" stroke="{colours[mark]}"/>'
        f'<text x="{tx + 55:g}" y="{ty + station * scale - 2:g}" font-size="8" '
        f'fill="{colours[mark]}">{_text(mark)} {station:g}</text>'
        for mark, tie in marks.items()
        for station in tie["stations_mm"]
    )
    piece_count = sum(mark["quantity"] for mark in marks.values())
    tie_elevation = (
        f'<g data-view="tie-elevation"><text x="{tx:g}" y="77">{piece_count} joint ties · z↓</text>'
        f"{tie_stations}</g>"
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1070 895" role="img" aria-labelledby="duct02-title">'
        f'<title id="duct02-title">Checked DUCT02 exterior joint {_text(request["joint_id"])}</title>'
        f"<desc>{_text(identity)}. +X exterior face; x and y horizontal axes, z increases from top to soffit.</desc>"
        f'<text x="25" y="30" font-family="sans-serif" font-size="16">{_text(request["joint_id"])} · exterior +X · local checked steel</text>'
        f'<text x="25" y="50" font-family="sans-serif" font-size="11">{_text(identity)} · no whole-member lengths</text>'
        f'<g font-family="sans-serif" font-size="12">{plan}{tie_legend}{x_section}{x_caption}{y_section}{tie_elevation}</g></svg>'
    )


def render_exterior_joint_bbs_csv(result: DuctileJointResultV1) -> str:
    """Schedule the in-core ties and separately label local X hook geometry."""
    data = result.calculation
    request = _request(result)
    placement = data["placement"]
    out = StringIO()
    fields = (
        "joint_id",
        "action_revision",
        "cage_action_revision",
        "input_hash",
        "schedule_scope",
        "bar_mark",
        "diameter_mm",
        "quantity",
        "shape",
        "cut_length_mm",
        "total_length_mm",
        "total_weight_kg",
        "units",
        "local_beyond_face_length_mm",
        "bend_centreline_radius_mm",
        "hook_tail_mm",
        "closure_run_mm",
        "closure_rise_mm",
        "closure_bends_deg",
        "stations_mm",
        "plan_xy_extent_mm",
    )
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    identity = {
        "joint_id": request["joint_id"],
        "action_revision": request["action_revision"],
        "cage_action_revision": request["cage_action_revision"],
        "input_hash": result.input_hash,
        "units": "mm, kg",
    }
    for mark, tie in placement["joint_tie_marks"].items():
        cut = tie["nominal_cut_length_mm"]
        total = cut * tie["quantity"]
        xs, ys, _ = zip(*tie["local_centreline_polyline_mm"], strict=True)
        writer.writerow(
            {
                **identity,
                "schedule_scope": "in_core_order",
                "bar_mark": mark,
                "diameter_mm": tie["diameter_mm"],
                "quantity": tie["quantity"],
                "shape": f"hooks_{'-'.join(f'{angle:g}' for angle in tie['hook_angles_deg'])}",
                "cut_length_mm": cut,
                "total_length_mm": total,
                "total_weight_kg": calculate_bar_weight(
                    tie["diameter_mm"], total, round_weight=False
                ),
                "local_beyond_face_length_mm": "",
                "bend_centreline_radius_mm": tie["bend_centreline_radius_mm"],
                "hook_tail_mm": tie["hook_tail_mm"],
                "closure_run_mm": tie["closure_offset_run_mm"],
                "closure_rise_mm": tie["closure_plane_offset_mm"],
                "closure_bends_deg": " ".join(
                    map(str, tie["closure_offset_bends_deg"])
                ),
                "stations_mm": " ".join(map(str, tie["stations_mm"])),
                "plan_xy_extent_mm": f"{min(xs):g} {max(xs):g} {min(ys):g} {max(ys):g}",
            }
        )
    for hook in placement["x_hook_paths"]:
        writer.writerow(
            {
                **identity,
                "schedule_scope": "local_beyond_face_geometry_not_order_total",
                "bar_mark": hook["bar_id"],
                "diameter_mm": hook["diameter_mm"],
                "quantity": 1,
                "shape": f"hook_{hook['bend_angle_deg']:g}",
                "cut_length_mm": "",
                "total_length_mm": "",
                "total_weight_kg": "",
                "local_beyond_face_length_mm": hook["centreline_length_beyond_face_mm"],
                "bend_centreline_radius_mm": hook["bend_centreline_radius_mm"],
                "hook_tail_mm": hook["straight_tail_mm"],
            }
        )
    return out.getvalue()
