"""Project the resolved cross-tie and render the checked construction evidence."""

from __future__ import annotations

import html
from typing import Any


def _section_xy(point: dict[str, float]) -> tuple[float, float]:
    return point["section_x_from_left_mm"], point["section_y_from_top_mm"]


def project_centre_cross_tie(path: dict[str, Any]) -> str:
    """Draw the open tie using the resolved segment endpoints and bend centres."""
    segments = path["segments"]
    x, y = _section_xy(segments[0]["start"])
    commands = [f"M{x:g} {y:g}"]
    for segment in segments:
        next_x, next_y = _section_xy(segment["end"])
        if segment["kind"] == "bend_arc":
            centre_x, centre_y = _section_xy(segment["bend_centre"])
            cross = (x - centre_x) * (next_y - centre_y) - (y - centre_y) * (
                next_x - centre_x
            )
            radius = segment["bend_radius_mm"]
            commands.append(
                f"A{radius:g} {radius:g} 0 0 {int(cross > 0)} {next_x:g} {next_y:g}"
            )
        else:
            commands.append(f"L{next_x:g} {next_y:g}")
        x, y = next_x, next_y
    mark = html.escape(path["bar_mark"], quote=True)
    station = segments[0]["start"]["station_x_mm"]
    return (
        f'<path data-outline="centre-cross-tie" data-link-display="projected" '
        f'data-bar-mark="{mark}" data-station-mm="{station:g}" d="{" ".join(commands)}" '
        f'fill="none" stroke="#7e22ce" stroke-width="{path["diameter_mm"]:g}">'
        f"<title>{mark} · projected from station {station:g} mm</title></path>"
    )


def render_layered_cage_report(
    evidence: dict[str, Any], *, analysis_revision: str, reinforcement_revision: str
) -> str:
    """Report the measured construction checks and the checked revision."""
    placement = evidence.get("placement")
    if not placement:
        return ""
    corners = "".join(
        f'<li>{html.escape(bar_id)} · {"seated" if check["seated_through_tolerance"] else "seat fails"}'
        f' · bend clearance {check["min_radial_clearance_mm"]:.3f} mm</li>'
        for bar_id, check in placement["outer_corner_checks"].items()
    )
    governing = ""
    if evidence.get("governing_flexure_row_id"):
        governing = (
            f'<p>Governing signed flexure row <code>{html.escape(evidence["governing_flexure_row_id"])}</code>. '
            f'Governing acceptance shear row <code>{html.escape(evidence["governing_acceptance_shear_row_id"] or "")}</code>.</p>'
        )
    service = evidence.get("service")
    service_html = ""
    if service and service["status"] == "PASS":
        service_html = (
            "<h3>Instantaneous service</h3>"
            f'<p>Sagging effective depth {service["sagging_effective_depth_mm"]:.3f} mm. '
            f'Unfactored UDL {service["unfactored_udl_kn_per_m_per_span"]:g} kN/m per span. '
            f'Calculated instantaneous deflection {service["maximum_instantaneous_deflection_mm"]:.3f} mm. '
            f'Calculated flexural crack width {service["flexural_crack_width_mm"]:.3f} mm.</p>'
        )
    cross = placement.get("cross_tie")
    cross_html = ""
    if cross:
        cross_html = (
            f'<p>Concrete consolidation opening {cross["consolidation_opening_mm"]:g} mm. '
            f'Required opening {placement["consolidation_access_diameter_mm"]:g} mm. '
            f'Cross-tie and hoop axial clearance {cross["minimum_grid_clearance_mm"]:g} mm.</p>'
        )
    return (
        "<h2>Two-layer cage placement</h2>"
        f"<p>Analysis revision <code>{html.escape(analysis_revision)}</code>. "
        f"Reinforcement revision <code>{html.escape(reinforcement_revision)}</code>.</p>"
        f'<p>Lift envelope {placement["lift_envelope_width_mm"]:g} × {placement["lift_envelope_height_mm"]:g} mm. '
        f'Form opening {placement["form_opening_width_mm"]:g} × {placement["form_opening_height_mm"]:g} mm. '
        f'Minimum outer hoop cover {placement["worst_outer_hoop_cover_mm"]:g} mm against '
        f'{placement["required_cover_mm"]:g} mm required.</p>'
        f"<ul>{corners}</ul>{cross_html}{governing}{service_html}"
    )
