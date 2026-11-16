"""Render the checked haunch geometry and signed calculations."""

from __future__ import annotations

import html
from itertools import pairwise
from typing import Any

from structural_lib.services.beam_haunch_geometry import BeamHaunchDetailV1
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousCheckRequestV1,
)


def _outline_depth(outline: list[dict[str, float]], x: float) -> float:
    for left, right in pairwise(outline):
        start, end = left["station_mm"], right["station_mm"]
        if start <= x <= end:
            return left["depth_mm"] + (right["depth_mm"] - left["depth_mm"]) * (
                x - start
            ) / (end - start)
    raise ValueError("The drawing station lies outside the checked haunch outline.")


def render_haunch_svg(
    member: BeamContinuousCheckRequestV1,
    request: BeamHaunchDetailV1,
    data: dict[str, Any],
    *,
    input_hash: str,
    path_id: str,
    bend_radius_mm: float,
) -> str:
    """Project the resolved bottom pieces, regular links and local bend links."""
    outline = data["outline"]
    start, end = outline[0]["station_mm"], outline[-1]["station_mm"]
    depth_max = max(point["depth_mm"] for point in outline)
    soffit = " ".join(
        f"L{point['station_mm']:g} {point['depth_mm']:g}" for point in reversed(outline)
    )
    ext = member.straight_bars
    assert ext is not None
    top_bar_y = next(bar.y_from_top_mm for bar in member.bars if bar.face == "top")
    inset = member.clear_cover_mm + member.link_diameter_mm / 2
    supports = "".join(
        f'<rect x="{support.left_face_mm:g}" y="{_outline_depth(outline, support.centre_mm):g}" '
        f'width="{support.width_mm:g}" height="90" fill="#cbd5e1"/>'
        for support in member.supports
    )
    link_marks = {link.station_mm: link for link in request.links}
    links = "".join(
        f'<line data-link-station="{row["station_mm"]:g}" '
        f'x1="{row["station_mm"]:g}" x2="{row["station_mm"]:g}" '
        f'y1="{inset:g}" y2="{row["bottom_axis_mm"]:g}" '
        f'stroke="{("#7e22ce" if link_marks[row["station_mm"]].purpose == "bend" else "#64748b")}" '
        f'stroke-width="8"><title>{html.escape(link_marks[row["station_mm"]].bar_mark)} at {row["station_mm"]:g} mm</title></line>'
        for row in data["link_checks"]
    )
    bottom_segments = data["bottom_segments"]
    first = bottom_segments[0]["start"]
    bottom_path = [f"M{first[0]:.6f} {first[1]:.6f}"]
    for segment in bottom_segments:
        x, y = segment["end"]
        if "centre" in segment:
            cx, cy = segment["centre"]
            sx, sy = segment["start"]
            sweep = int((sx - cx) * (y - cy) - (sy - cy) * (x - cx) > 0)
            r = segment["radius_mm"]
            bottom_path.append(f"A{r:g} {r:g} 0 0 {sweep} {x:.6f} {y:.6f}")
        else:
            bottom_path.append(f"L{x:.6f} {y:.6f}")
    bend_labels = "".join(
        f'<g data-haunch-bend="{html.escape(bend["node_id"], quote=True)}">'
        f'<line x1="{bend["tangent_x_mm"][0]:.4f}" x2="{bend["tangent_x_mm"][1]:.4f}" '
        f'y1="-60" y2="-60" stroke="#7e22ce" stroke-width="16"/>'
        f'<text x="{sum(bend["tangent_x_mm"]) / 2:.4f}" y="-95" text-anchor="middle" '
        f'font-size="105" fill="#7e22ce">{html.escape(bend["node_id"])}</text></g>'
        for bend in data["bend_checks"]
    )
    outline_path = f"M{start:g} 0 H{end:g} {soffit} Z"
    sections = _section_drawing(member, data, bend_radius_mm, inset)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 654" role="img">
<title>{html.escape(member.member_id)} checked variable-depth beam</title>
<desc>Input {html.escape(input_hash)}. Path {html.escape(path_id)}. Nominal haunch review drawing.</desc>
<text x="18" y="27" font-size="22">Haunch elevation</text>
<text x="700" y="27" font-size="17" fill="#7e22ce">Purple links restrain the bottom bar bends</text>
<svg data-view="haunch-elevation" x="0" y="44" width="1200" height="229"
 viewBox="{start - 40:g} -145 {end - start + 80:g} {depth_max + 275:g}">
{supports}
<path d="{outline_path}" fill="#f1f5f9" stroke="#0f172a" stroke-width="4"/>
{links}
<path d="M{ext.start_mm:g} {top_bar_y:g} H{ext.end_mm:g}" stroke="#1e40af" stroke-width="12"/>
<path d="{' '.join(bottom_path)}" fill="none" stroke="#1e40af" stroke-width="13"/>
{bend_labels}
</svg>
<text x="18" y="280" font-size="18">Sections at checked link stations</text>
<svg data-view="haunch-section" x="0" y="292" width="1200" height="352" viewBox="0 0 1200 352">{sections}</svg>
</svg>"""


def _section_drawing(
    member: BeamContinuousCheckRequestV1,
    data: dict[str, Any],
    bend_radius_mm: float,
    inset: float,
) -> str:
    chosen = []
    for first, last in pairwise(data["outline"]):
        a, b = first["station_mm"], last["station_mm"]
        candidates = [row for row in data["link_checks"] if a <= row["station_mm"] <= b]
        if not candidates:
            continue
        row = min(candidates, key=lambda item: abs(item["station_mm"] - (a + b) / 2))
        depth = _outline_depth(data["outline"], row["station_mm"])
        chosen.append((row, depth))
    panels = []
    if not chosen:
        return ""
    panel = 1200 / len(chosen)
    width = member.width_mm
    depth_max = max(point["depth_mm"] for point in data["outline"])
    for i, (row, depth) in enumerate(chosen):
        circles = "".join(
            f'<circle data-bar-id="{html.escape(bar.bar_id, quote=True)}" cx="{bar.x_from_left_mm:g}" '
            f'cy="{(row["bottom_axes_mm"][0] if bar.face == "bottom" else bar.y_from_top_mm):.6f}" '
            f'r="{bar.diameter_mm / 2:g}" fill="#1e40af"/>'
            for bar in member.bars
        )
        panels.append(
            f'<text x="{i * panel + panel / 2:g}" y="23" text-anchor="middle" font-size="16">'
            f'{row["station_mm"]:g} mm · D{depth:.1f}</text>'
            f'<svg x="{i * panel:g}" y="36" width="{panel:g}" height="310" '
            f'viewBox="-22 -22 {width + 44:g} {depth_max + 44:g}">'
            f'<rect width="{width:g}" height="{depth:g}" fill="#f1f5f9" stroke="#0f172a" stroke-width="3"/>'
            f'<rect x="{inset:g}" y="{inset:g}" width="{width - 2 * inset:g}" '
            f'height="{row["bottom_axis_mm"] - inset:g}" rx="{bend_radius_mm:g}" '
            f'fill="none" stroke="#64748b" stroke-width="{member.link_diameter_mm:g}"/>{circles}</svg>'
        )
    return "".join(panels)


def render_haunch_report(data: dict[str, Any]) -> str:
    """Disclose the signed adjustment and usable local link resistance."""
    rows = "".join(
        f"<tr><th>{html.escape(row['row_id'])}</th><td>{row['station_mm']:g}</td>"
        f"<td>{row['depth_mm']:.3f}</td><td>{row['moment_knm']:.3f}</td>"
        f"<td>{row['concurrent_shear_kn']:.3f}</td><td>{row['shear_adjustment_kn']:.3f}</td>"
        f"<td>{row['shear_demand_kn']:.3f}</td><td>{row['shear_capacity_kn']:.3f}</td></tr>"
        for row in data.get("rows", ())
    )
    bends = "".join(
        f"<tr><th>{html.escape(row['node_id'])}</th>"
        f"<td>{', '.join(format(x, 'g') for x in row['link_stations_mm'])}</td>"
        f"<td>{row['demand_per_bar_kn']:.3f}</td><td>{row['resistance_per_bar_kn']:.3f}</td>"
        f"<td>{row['bearing_nmm2']:.3f} / {row['bearing_limit_nmm2']:.3f}</td>"
        f"<td>{row['minimum_projected_development_mm']:.3f} / {row['required_compression_development_mm']:.3f}</td></tr>"
        for row in data.get("bend_checks", ())
    )
    result = "<h2>Variable-depth haunch</h2>"
    if "minimum_link_cover_mm" in data:
        result += (
            f"<p>Minimum nominal link cover {data['minimum_link_cover_mm']:.3f} mm. "
            f"Axial opening {data['minimum_axial_opening_mm']:.3f} mm. "
            f"Bottom bar cover bound {data['bottom_bar_soffit_cover_bound_mm']:.3f} mm.</p>"
        )
    if data.get("support_development_mm"):
        result += "<h3>Support development</h3><ul>"
        result += "".join(
            f"<li>{html.escape(face)} · {length:g} mm available · "
            f"{data['required_tension_development_mm']:g} mm required</li>"
            for face, length in data["support_development_mm"].items()
        )
        result += "</ul>"
    if rows:
        result += (
            "<h3>Signed varying-depth shear</h3><table><thead><tr><th>Row</th><th>Station (mm)</th>"
            "<th>Depth (mm)</th><th>Moment (kN·m)</th><th>Concurrent shear (kN)</th>"
            "<th>Correction (kN)</th><th>Demand (kN)</th><th>Resistance (kN)</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )
    if bends:
        result += (
            "<h3>Dedicated links at the bottom bar bends</h3><table><thead><tr><th>Bend</th>"
            "<th>Link stations (mm)</th><th>Demand per bar (kN)</th><th>Resistance per side (kN)</th>"
            "<th>Bearing used / limit (N/mm²)</th><th>Development available / required (mm)</th>"
            f"</tr></thead><tbody>{bends}</tbody></table>"
        )
    return result
