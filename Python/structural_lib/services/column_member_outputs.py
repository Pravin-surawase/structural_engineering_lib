"""Project COL07 report, elevation and BBS from the same checked member."""

from __future__ import annotations

import csv
from html import escape
from io import StringIO
from math import dist
from typing import Any

from structural_lib.services.column_member_detailing import (
    WORKFLOW,
    DetailingRequest,
    Result,
)
from structural_lib.services.column_tied_member import rectangular_section_markup
from structural_lib.services.contracts.column_member_detailing import (
    ColumnMemberDetailingInputV1,
    PositionedColumnMemberDetailingInputV1,
    SlenderColumnMemberDetailingInputV1,
)


def _metadata(result: Result) -> tuple[DetailingRequest, str]:
    request = result.request
    if result.workflow_id != WORKFLOW or not isinstance(
        request,
        (
            ColumnMemberDetailingInputV1,
            PositionedColumnMemberDetailingInputV1,
            SlenderColumnMemberDetailingInputV1,
        ),
    ):
        raise TypeError("A COL07 member detailing result is required")
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    return request, identity.input_hash


def render_column_member_bbs_csv(result: Result) -> str | None:
    """Return the issued schedule, carrying the calculation and revision identity."""
    request, input_hash = _metadata(result)
    bbs = result.calculation["bbs"]
    if bbs is None:
        return None
    return _schedule_csv(
        bbs["rows"],
        {
            "member_id": request.identity.member_id,
            "analysis_revision": request.basis.analysis_revision,
            "detailing_revision": request.basis.detailing_revision,
            "input_hash": input_hash,
        },
    )


def _schedule_csv(rows: list[dict[str, Any]], metadata: dict[str, str | None]) -> str:
    out = StringIO()
    fields = (
        "bar_id",
        "role",
        "diameter_mm",
        "quantity",
        "cut_length_mm",
        "total_length_mm",
        "total_weight_kg",
        "source",
    )
    writer = csv.DictWriter(out, fieldnames=[*metadata, *fields], lineterminator="\n")
    writer.writeheader()
    for row in rows:
        values = {**metadata, **row}
        writer.writerow(
            {
                key: (
                    "'" + value
                    if isinstance(value, str)
                    and value.lstrip().startswith(("=", "+", "-", "@"))
                    else value
                )
                for key, value in values.items()
            }
        )
    return out.getvalue()


def _splice_sections(
    splice: dict[str, Any], cage: dict[str, Any], width: float, depth: float
) -> str:
    """Draw the three checked transverse layouts with their real bend paths."""
    scale = 152 / max(width, depth)
    sections = []
    for label, caption, left in (
        ("lower", "Below lap", 300),
        ("overlap", "Within lap", 475),
        ("upper", "Above lap", 650),
    ):
        section = splice["sections"][label]
        hoop_width = cage["tie_centreline_width_mm"]
        hoop_depth = cage["tie_centreline_depth_mm"]
        geometry = [
            f'<rect width="{width}" height="{depth}" fill="#f3f6f8" stroke="#172b4d"/>',
            f'<rect x="{(width-hoop_width)/2}" y="{(depth-hoop_depth)/2}" width="{hoop_width}" height="{hoop_depth}"'
            f' rx="{splice["hoop_centreline_radius_mm"]}" fill="none" stroke="#17706d"/>',
        ]
        for mark, link in section["links"].items():
            paths = []
            for segment in link["segments"]:
                x, y = segment["start_mm"]
                ex, ey = segment["end_mm"]
                centre = segment["centre_mm"]
                if centre is None:
                    command = f"L {ex:g} {ey:g}"
                else:
                    cx, cy = centre
                    radius = dist((x, y), centre)
                    sweep = int((x - cx) * (ey - cy) > (y - cy) * (ex - cx))
                    command = f"A {radius:g} {radius:g} 0 0 {sweep} {ex:g} {ey:g}"
                paths.append(f'<path d="M {x:g} {y:g} {command}"/>')
            geometry.append(
                f'<g data-link-mark="{escape(mark, quote=True)}" fill="none" stroke="#17706d" stroke-width="2.3">'
                f'<title>{escape(mark)} return link</title>{"".join(paths)}</g>'
            )
        for bar in section["bars"]:
            mark = escape(bar["bar_id"], quote=True)
            color = "#bd6421" if bar["bar_id"].endswith("-U") else "#172b4d"
            geometry.append(
                f'<circle cx="{bar["x_from_left_mm"]:g}" cy="{bar["y_from_top_mm"]:g}" r="{bar["diameter_mm"]/2:g}"'
                f' fill="{color}" data-piece-mark="{mark}"><title>{mark}</title></circle>'
            )
        sections.append(
            f'<text x="{left}" y="85" font-size="11">{caption}</text>'
            f'<g data-section="{label}" transform="translate({left} 100) scale({scale})">{"".join(geometry)}</g>'
        )
    return "".join(sections)


def render_column_member_detailing_svg(result: Result) -> str:
    """Draw the checked section and the supplied full-length reinforcement schedule."""
    request, input_hash = _metadata(result)
    data = result.calculation
    geometry, ends = request.geometry, request.end_detail
    length, width, depth = geometry.unsupported_length_mm, geometry.b_mm, geometry.D_mm
    status = result.engineering_status.value
    revisions = f"analysis {request.basis.analysis_revision} · detailing {request.basis.detailing_revision}"
    title = f"{status} · {request.identity.member_id or request.identity.case_id}"
    section, _ = rectangular_section_markup(
        data["cage"], data["cross_ties"], width, depth
    )
    top, bottom, left, right = 65, 480, 45, 135
    total = length + ends.start_straight_mm + ends.end_straight_mm

    def y(station: float) -> float:
        return bottom - (bottom - top) * (station + ends.start_straight_mm) / total

    body_top, body_bottom = y(length), y(0)
    projection = [
        f'<rect x="{left}" y="{body_top}" width="{right-left}" height="{body_bottom-body_top}" fill="#f3f6f8" stroke="#172b4d"/>'
    ]
    cage = data["cage"]
    splice = data.get("contact_splice")
    if splice is not None:
        corner_splice = splice.get("y_plane_setback_mm") is not None
        pieces = splice["pieces"]
        if corner_splice:
            # Paint the bars on the back face first in the front projection.
            pieces = sorted(pieces, key=lambda piece: piece["y_mm"], reverse=True)
        for piece in pieces:
            mark = escape(piece["bar_id"], quote=True)
            fraction = piece["x_mm"] / width if corner_splice else piece["y_mm"] / depth
            x = left + (right - left) * fraction
            lo, hi = piece["start_mm"], piece["end_mm"]
            color = "#bd6421" if piece["bar_id"].endswith("-U") else "#2a3d5c"
            projection.append(
                f'<line x1="{x}" x2="{x}" y1="{y(lo)}" y2="{y(hi)}" stroke="{color}" '
                f'data-piece-id="{mark}" data-start-mm="{lo:g}" data-end-mm="{hi:g}">'
                f"<title>{mark} · {lo:g} to {hi:g} mm</title></line>"
            )
    elif cage is not None:
        dashed = ' stroke-dasharray="3 2"' if data["laps"] else ""
        for bar in cage["bars"]:
            x = left + (right - left) * bar["x_from_left_mm"] / width
            projection.append(
                f'<line x1="{x}" x2="{x}" y1="{top}" y2="{bottom}" stroke="#2a3d5c"{dashed}>'
                f'<title>{escape(bar["bar_id"])} longitudinal axis</title></line>'
            )
    for series in data["transverse"]:
        for station in series["stations_mm"]:
            position = y(station)
            projection.append(
                f'<line x1="{left+10}" x2="{right-10}" y1="{position}" y2="{position}" stroke="#17706d" '
                f'data-bar-id="{escape(series["bar_id"], quote=True)}" data-station-mm="{station:g}">'
                f'<title>{escape(series["bar_id"])} at {station:g} mm</title></line>'
            )
    for zone in data["tie_zones"]:
        start, end = zone["start_mm"], zone["end_mm"]
        pos = (y(start) + y(end)) / 2
        projection.append(
            f'<path d="M {right+5} {y(start)} h 5 V {y(end)} h -5" stroke="#64748b" fill="none"/>'
            f'<text x="{right+14}" y="{pos}" font-size="10">{escape(zone["zone_id"])} @ {zone["pitch_mm"]:g} mm</text>'
        )
    for lap in data["laps"]:
        start, end = lap["start_mm"], lap["end_mm"]
        projection.append(
            f'<rect x="{left-11}" y="{y(end)}" width="6" height="{y(start)-y(end)}" fill="#be640d">'
            f'<title>{"Contact lap" if splice else "Proposed lap"} {escape(lap["lap_id"])} · {start:g} to {end:g} mm</title></rect>'
        )
    scale = 170 / max(width, depth)
    if splice is not None:
        section_markup = _splice_sections(splice, cage, width, depth)
        splice_note = (
            f'<text x="310" y="353" font-size="11">{splice["end_mm"] - splice["start_mm"]:g} mm contact lap'
            f' · {len(splice["lap_stations_mm"])} overlap links</text>'
            '<text x="310" y="372" font-size="11" fill="#bd6421">Orange bars are upper splice pieces</text>'
        )
        if corner_splice:
            splice_note += (
                '<text x="40" y="500" font-size="10">Front elevation · x across width</text>'
                '<text x="310" y="391" font-size="11">The section cuts show the partner offset along the side faces.</text>'
            )
        view_width = 840
    else:
        section_markup = (
            f'<text x="310" y="85" font-size="11">{width:g} × {depth:g} mm section</text>'
            f'<g transform="translate(310 100) scale({scale})">'
            f'<rect width="{width}" height="{depth}" fill="#f3f6f8" stroke="#172b4d"/>{"".join(section)}</g>'
        )
        splice_note = (
            '<text x="310" y="353" font-size="11">Dashed axes show proposed splice scope</text>'
            if data["laps"]
            else ""
        )
        view_width = 560
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} 520" role="img" aria-labelledby="member-title">'
        f'<title id="member-title">{escape(title)}</title>'
        f"<desc>Input {input_hash}. {escape(revisions)}. Projections of the supplied schedule.</desc>"
        f'<text x="25" y="25" font-size="16" font-family="sans-serif">{escape(title)}</text>'
        f'<text x="25" y="44" font-size="11" font-family="sans-serif">{escape(revisions)}</text>'
        f'<g font-family="sans-serif">{section_markup}</g>'
        f'<g font-family="sans-serif">{"".join(projection)}</g>'
        f'<text x="310" y="296" font-size="11">Clear member length {length:g} mm</text>'
        f'<text x="310" y="315" font-size="11">Straight projections {ends.start_straight_mm:g} / {ends.end_straight_mm:g} mm</text>'
        f'<text x="310" y="334" font-size="11">{len(data["hoop_stations_mm"])} hoop levels</text>'
        f"{splice_note}</svg>"
    )


def render_column_member_detailing_html(result: Result) -> str:
    """Report the signed demands, independent checks and checked schedule."""
    request, input_hash = _metadata(result)
    data = result.calculation
    status = result.engineering_status.value
    action_rows = []
    for row in data["actions"]:
        a = row["action"]
        section = row["section"]
        section_status = section["status"] if section else "—"
        section_hash = section["input_hash"] if section else ""
        shear = row["shear"]
        if shear is None:
            shear_text = "<td colspan='5'>Unavailable</td>"
        else:
            shear_text = (
                f'<td>{shear["status"]} · {shear["direction"]}</td><td>{shear["pitch_mm"]:g}</td>'
                f'<td>{shear["d_mm"]:g}</td><td>{shear["vc_kn"]:.2f} / {shear["vus_kn"]:.2f}</td><td>{shear["utilization"]:.4f}</td>'
            )
        action_rows.append(
            f'<tr><td>{escape(row["combination_id"])}</td><td>{row["station_mm"]:g}</td>'
            f'<td>{a["pu_kn"]:g} / {a["mx_knm"]:g} / {a["my_knm"]:g}</td>'
            f'<td>{a["vx_kn"]:g} / {a["vy_kn"]:g}</td>'
            f'<td title="{section_hash}">{section_status}</td><td>{escape(row.get("zone_id","—"))}</td>'
            f"{shear_text}</tr>"
        )
    checks = "".join(
        f'<tr><td>{escape(c["code"])}</td><td>{escape(c["path"])}</td><td>{c["status"]}</td>'
        f'<td>{escape(c["message"])}<br><small>{escape(c["source_reference"])}</small></td></tr>'
        for c in data["checks"]
    )
    bbs = data["bbs"]
    if bbs is None:
        schedule = "<p>BBS withheld while a mandatory check is held or failed.</p>"
    else:
        rows = "".join(
            f'<tr><td>{escape(row["bar_id"])}</td><td>{row["diameter_mm"]:g}</td>'
            f'<td>{row["quantity"]}</td><td>{row["cut_length_mm"]:g}</td><td>{row["total_weight_kg"]:.3f}</td></tr>'
            for row in bbs["rows"]
        )
        schedule = (
            f'<p>{bbs["quantity"]} pieces · {bbs["total_length_mm"]/1000:.3f} m · {bbs["total_weight_kg"]:.3f} kg.</p>'
            "<table><thead><tr><th>Mark</th><th>Ø (mm)</th><th>Quantity</th><th>Cut (mm)</th><th>Mass (kg)</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )
    lap_table = ""
    if data["laps"]:
        lap_rows = ""
    for lap in data["laps"]:
        required = lap["required_mm"]
        required_text = f"{required:.2f}" if required is not None else "HOLD"
        lap_rows += (
            f'<tr><td>{escape(lap["lap_id"])}</td><td>{escape(", ".join(lap["bar_ids"]))}</td>'
            f'<td>{lap["start_mm"]:g}–{lap["end_mm"]:g}</td><td>{lap["provided_mm"]:g}</td>'
            f"<td>{required_text}</td></tr>"
        )
    splice = data.get("contact_splice")
    splice_details = ""
    if splice is not None:
        distances = ", ".join(
            f"{value:g}" for value in splice["end_support_distances_mm"]
        )
        splice_details = (
            f'<p>Unrelated longitudinal clearance {splice["minimum_unrelated_bar_clear_mm"]:.2f} mm. '
            f'Minimum link-to-bar clearance {splice["minimum_link_clear_mm"]:.2f} mm. '
            f'End support distances {distances or "unresolved"} mm.</p>'
        )
        if splice.get("corner_level_clear_mm") is not None:
            splice_details += (
                f'<p>Supplemental corner link level clearance {splice["corner_level_clear_mm"]:.2f} mm. '
                f'End face cover after adding corner links {splice["corner_end_cover_mm"]:.2f} mm.</p>'
            )
    governing = data["governing_shear"]
    governing_text = (
        f'<p>Governing supplied shear: {escape(governing["combination_id"])} at '
        f'{governing["station_mm"]:g} mm, utilization {governing["shear"]["utilization"]:.4f}.</p>'
        if governing
        else ""
    )
    limits = "".join(f"<li>{escape(item)}</li>" for item in result.limitations)
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Column member detailing</title>'
        "<style>body{font:16px system-ui;margin:2rem;max-width:80rem}table{border-collapse:collapse}"
        "td,th{padding:.35rem;border:1px solid #d0d8df;text-align:left}svg{width:min(100%,40rem);display:block}</style>"
        f"<h1>Column member detailing · {status}</h1><p>Member {escape(request.identity.member_id or request.identity.case_id)}. Qualified review required.</p>"
        f"<p>Analysis revision {escape(request.basis.analysis_revision)} · detailing revision {escape(request.basis.detailing_revision)}.</p>"
        f"<p>Input <code>{input_hash}</code>.</p>"
        f"{render_column_member_detailing_svg(result)}"
        f'<p>Straight end development required {data["end_required_mm"]:.2f} mm. '
        f"Provided {request.end_detail.start_straight_mm:g} mm at the start and "
        f"{request.end_detail.end_straight_mm:g} mm at the end. "
        f'Base compression lap requirement {data["lap_required_mm"]:.2f} mm.</p>'
        f"{governing_text}<h2>Supplied concurrent actions</h2><table><thead><tr>"
        "<th>Combination</th><th>Station (mm)</th><th>Pu / Mx / My (kN / kNm / kNm)</th><th>Vx / Vy (kN)</th>"
        "<th>Section</th><th>Zone</th><th>Shear</th><th>Pitch (mm)</th><th>d (mm)</th><th>Vc / Vus (kN)</th><th>Utilization</th>"
        f'</tr></thead><tbody>{"".join(action_rows)}</tbody></table>'
        f"{lap_table}{splice_details}<h2>Bar bending schedule</h2>{schedule}<h2>Checks</h2>"
        f"<table><thead><tr><th>Code</th><th>Input</th><th>Status</th><th>Basis</th></tr></thead><tbody>{checks}</tbody></table>"
        f"<h2>Scope</h2><ul>{limits}</ul></html>"
    )
