"""Draw and report the same resolved beam and slab pieces used by the BBS."""

from __future__ import annotations

import html
from collections import defaultdict
from typing import Any

from structural_lib.services.canonical_family import CanonicalFamilyResultV1

_Result = CanonicalFamilyResultV1[dict[str, Any]]
_COLOURS = {"web": "#1d4ed8", "flange": "#7e22ce", "slab": "#15803d"}


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _colour(piece: dict[str, Any]) -> str:
    return _COLOURS[piece["role"].split("_", 1)[0]]


def _path(piece: dict[str, Any], horizontal: int, vertical: int) -> str:
    points = " L".join(
        f"{p[horizontal]:.4f} {p[vertical]:.4f}" for p in piece["points_mm"]
    )
    return (
        f'<path data-piece-id="{_escape(piece["bar_id"])}" data-role="{_escape(piece["role"])}" '
        f'd="M{points}" fill="none" stroke="{_colour(piece)}" '
        f'stroke-width="{piece["diameter_mm"]:g}" stroke-linecap="round">'
        f'<title>{_escape(piece["bar_id"])} · {_escape(piece["mark"])}</title></path>'
    )


def _support_projection(pieces: list[dict[str, Any]], middle: float) -> tuple[str, str]:
    representative: dict[str, dict[str, Any]] = {}
    section = []
    for piece in pieces:
        points = piece["points_mm"]
        if (
            piece["role"].endswith("longitudinal")
            or piece["role"] == "slab_distribution"
        ):
            if points[0][0] <= middle <= points[-1][0]:
                _, x, y = points[0]
                section.append(
                    f'<circle data-piece-id="{_escape(piece["bar_id"])}" cx="{x:g}" cy="{y:g}" '
                    f'r="{piece["diameter_mm"] / 2:g}" fill="{_colour(piece)}">'
                    f'<title>{_escape(piece["mark"])} · {_escape(piece["bar_id"])}</title></circle>'
                )
        else:
            mark = piece["mark"]
            current = representative.get(mark)
            if current is None or abs(points[0][0] - middle) < abs(
                current["points_mm"][0][0] - middle
            ):
                representative[mark] = piece
    paths = "".join(_path(piece, 1, 2) for piece in representative.values())
    stations = " · ".join(
        f"{_escape(mark)} at {piece['points_mm'][0][0]:g} mm"
        for mark, piece in representative.items()
    )
    return paths + "".join(section), stations


def render_physical_flange_svg(result: _Result) -> str:
    """Project resolved centreline coordinates at the local support and along the beam."""
    assembly = result.calculation["physical_flange"]
    request, pieces = assembly["request"], assembly["pieces"]
    beam = request["beam"]
    flange, supports = beam["flange"], request["supports"]
    width, depth = beam["width_mm"], beam["depth_mm"]
    left, right, thickness = (
        flange["left_overhang_mm"],
        flange["right_overhang_mm"],
        flange["thickness_mm"],
    )
    start = supports[0]["centre_mm"] - supports[0]["width_mm"] / 2
    end = supports[-1]["centre_mm"] + supports[-1]["width_mm"] / 2
    middle = supports[1]["centre_mm"]
    min_x, max_x = request["slab_edge_x_mm"]
    section, stations = _support_projection(pieces, middle)
    elevation = "".join(_path(piece, 0, 2) for piece in pieces)
    supporting = "".join(
        f'<rect x="{s["centre_mm"] - s["width_mm"] / 2:g}" y="{depth:g}" '
        f'width="{s["width_mm"]:g}" height="95" fill="#cbd5e1"/>'
        for s in supports
    )
    plan_paths = "".join(
        _path(piece, 0, 1)
        for piece in pieces
        if not piece["role"].endswith("longitudinal")
        and (
            piece["role"] == "slab_distribution"
            or abs(piece["points_mm"][0][0] - middle) < 255
        )
    )
    geometry = assembly["engineering"]["geometry"]
    stamp = result.envelope.result_identity
    assert stamp is not None
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 752" role="img">
<title>{_escape(result.identity.member_id)} checked T-flange reinforcement</title>
<desc>Input {_escape(stamp.input_hash)}. Paths {_escape(result.calculation["paths"]["result_id"])}.</desc>
<text x="20" y="28" font-size="22">{_escape(result.identity.member_id)} · beam and slab reinforcement</text>
<text x="20" y="58" font-size="16">Elevation · beam station in mm</text>
<svg data-view="elevation" x="20" y="70" width="1160" height="216" viewBox="{start - 100:g} -60 {end - start + 200:g} {depth + 200:g}" preserveAspectRatio="none">
<rect x="{start:g}" y="0" width="{end - start:g}" height="{depth:g}" fill="#f8fafc" stroke="#475569" stroke-width="4"/>
{supporting}{elevation}
</svg>
<text x="20" y="315" font-size="17">Support assembly projection at {middle:g} mm · flange detail</text>
<text x="615" y="315" font-size="17">Support plan · staggered grids</text>
<svg data-view="support-section" x="20" y="332" width="555" height="338" viewBox="{-left - 40:g} -50 {width + left + right + 80:g} {depth + 100:g}">
<path d="M{min_x:g} 0 H{max_x:g} V{thickness:g} H{width:g} V{depth:g} H0 V{thickness:g} H{min_x:g} Z"
 fill="#f8fafc" stroke="#475569" stroke-width="4"/>
<path d="M{-left:g} -15 V{thickness:g} M{width + right:g} -15 V{thickness:g}" stroke="#94a3b8" stroke-dasharray="12 10" stroke-width="4"/>
{section}
</svg>
<svg data-view="support-plan" x="615" y="332" width="555" height="338" viewBox="{middle - 235:g} {min_x - 30:g} 470 {max_x - min_x + 60:g}" preserveAspectRatio="none">
<rect x="{middle - 235:g}" y="{min_x:g}" width="470" height="{max_x - min_x:g}" fill="#f8fafc"/>
<rect x="{middle - 235:g}" y="0" width="470" height="{width:g}" fill="#e2e8f0"/>
{plan_paths}
</svg>
<text x="20" y="685" font-size="15">{stations}</text>
<text x="20" y="712" font-size="15">
<tspan fill="#1d4ed8">Web cage</tspan> · <tspan fill="#7e22ce">Flange bars and links</tspan> · <tspan fill="#15803d">Slab-owned bars</tspan>
</text>
<text x="620" y="712" font-size="15">Local clear opening {geometry["axial_access_mm"]:.1f} × {geometry["transverse_access_mm"]:.1f} mm after placement</text>
<text x="20" y="738" font-size="13" fill="#475569">Section projects staggered pieces from the listed stations. Joint steel and site obstructions require project checks.</text>
</svg>"""


def _check_rows(strength: dict[str, Any]) -> str:
    rows = []
    for row in strength["rows"]:
        action = row["action"]
        moment_ratio, shear_ratio = row["flexure_utilization"], row["shear_utilization"]
        if moment_ratio is None or shear_ratio is None:
            continue
        rows.append(
            f'<tr><th>{_escape(action["row_id"])}</th><td>{action["mu_knm"]:.3f}</td>'
            f'<td>{action["vu_kn"]:.3f}</td><td>{moment_ratio:.4f}</td>'
            f'<td>{shear_ratio:.4f}</td><td>{_escape(row["section_status"])}</td></tr>'
        )
    return (
        "<h2>Signed beam actions and adverse utilization</h2><table><thead><tr><th>Row</th>"
        "<th>M (kN·m)</th><th>V (kN)</th><th>Moment ratio</th><th>Shear ratio</th>"
        f"<th>Status</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
        if rows
        else ""
    )


def render_physical_flange_report(
    result: _Result,
    *,
    drawing: str = "",
    schedule: str | None = None,
    current: bool = True,
) -> str:
    """Report placement, development and actual strip actions from the checked result."""
    assembly = result.calculation["physical_flange"]
    details = assembly["engineering"]
    basis, geometry, strip, strength = (
        details.get(key, {}) for key in ("basis", "geometry", "strip", "strength")
    )
    issues = "".join(
        f"<li>{_escape(i.code)} · {_escape(i.message)}</li>"
        for i in result.envelope.issues
    )
    stamp = result.envelope.result_identity
    assert stamp is not None
    anchored = "".join(
        f'<tr><th>{_escape(row["bar_id"])}</th><td>{row["available_after_tolerance_mm"]:.3f}</td>'
        f'<td>{row["required_development_mm"]:.3f}</td><td>{row["beyond_zero_moment_mm"]:.3f}</td></tr>'
        for row in details.get("anchorage", {}).get("bars", ())
    )
    strip_rows = "".join(
        f'<tr><th>{_escape(row["combination_id"])}</th>'
        f'<td>{row["interior_support_moment_knm"]:.3f}</td>'
        f'<td>{row["same_span_positive_peak_knm"]:.3f}</td>'
        f'<td>{row["support_shear_magnitude_kn"]:.3f}</td>'
        f'<td>{row["adverse_tau_v_nmm2"]:.4f}</td>'
        f'<td>{row["adverse_tau_c_nmm2"]:.4f}</td></tr>'
        for row in strip.get("strip_checks", ())
    )
    cover_rows = "".join(
        f"<li>{_escape(key)} · {value:.3f} mm</li>"
        for key, value in geometry.get("minimum_cover_after_tolerance_mm", {}).items()
    )
    groups: dict[str, list[str]] = defaultdict(list)
    for piece in assembly["pieces"]:
        groups[piece["mark"]].append(piece["bar_id"])
    schedule_rows = ""
    if schedule is not None:
        for item in result.calculation["bbs"]["outputs"]["bbs"]["rows"]:
            mark = item["bar_mark"]
            schedule_rows += (
                f'<tr data-mark="{_escape(mark)}"><th>{_escape(mark)}</th>'
                f'<td>{_escape(assembly["owners_by_mark"][mark])}</td><td>{item["diameter_mm"]:g}</td>'
                f'<td>{item["scheduled_bar_count"]}</td>'
                f'<td>{item["fabrication_cut_length_each_mm"]:.3f}</td><td>{item["theoretical_mass_kg"]:.3f}</td>'
                f'<td>{", ".join(_escape(b) for b in groups[mark])}</td></tr>'
            )
    top = (
        f'<p>Hogging capacity {strength["adverse_capacity_knm"]["top"]:.3f} kN·m under adverse placement. '
        f'Web shear capacity {strength["adverse_web_shear_capacity_kn"]["top"]:.3f} kN at hogging. '
        f'Hogging row {_escape(strength["governing_rows"].get("hogging", ""))}. '
        f'Shear row {_escape(strength["governing_rows"].get("shear", ""))}.</p>'
        if strength
        else ""
    )
    band = (
        f'<p>Effective sagging flange width {basis["effective_width_mm"]:g} mm. '
        f'Hogging distribution width {basis["hogging_distribution_width_mm"]:g} mm.</p>'
        if basis
        else ""
    )
    fit = (
        f'<h2>Placement</h2><p>Clear axial opening {geometry["axial_access_mm"]:.3f} mm. '
        f'Clear transverse opening {geometry["transverse_access_mm"]:.3f} mm. '
        "Minimum cover after tolerance</p>"
        f"<ul>{cover_rows}</ul>"
        if geometry
        else ""
    )
    anchorage = (
        f"<h2>Beam flange development</h2><table><tr><th>Bar</th><th>Available (mm)</th>"
        f"<th>Required (mm)</th><th>Past zero moment (mm)</th></tr>{anchored}</table>"
        if anchored
        else ""
    )
    slab = (
        f"<h2>Perpendicular slab strip</h2><p>Straight development "
        f'{strip["available_main_development_mm"]:.3f} mm available, '
        f'{strip["required_main_development_mm"]:.3f} mm required.</p>'
        f"<table><tr><th>ULS</th><th>M at support (kN·m)</th><th>Peak sagging (kN·m)</th>"
        f"<th>V (kN)</th><th>Adverse τv (MPa)</th><th>Adverse τc (MPa)</th></tr>{strip_rows}</table>"
        if strip_rows
        else ""
    )
    cut_list = (
        f'<p>Path result <code>{_escape(result.calculation["paths"]["result_id"])}</code></p>'
        f"<table><tr><th>Mark</th><th>Owner</th><th>Ø mm</th><th>Pieces</th><th>Cut (mm)</th>"
        f"<th>Mass (kg)</th><th>Piece IDs</th></tr>{schedule_rows}</table>"
        if schedule_rows
        else "<p>Checked schedule withheld.</p>"
    )
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Physical T-flange review</title>
<style>body{{font:16px system-ui;margin:2rem;color:#172033}} table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{padding:.4rem .65rem;border-bottom:1px solid #d4dbe6;text-align:left}} svg{{width:100%;max-width:1200px}}</style>
<h1>Physical T-flange review · {_escape(result.identity.member_id)}</h1>
<p>{_escape(result.envelope.engineering_status.value) if current else "STALE"} · Input <code>{_escape(stamp.input_hash)}</code></p>
<ul>{issues}</ul>{band}{top}{_check_rows(result.calculation["strength"])}{anchorage}{slab}{fit}
{drawing}<h2>Bar bending schedule</h2>{cut_list}</html>"""
