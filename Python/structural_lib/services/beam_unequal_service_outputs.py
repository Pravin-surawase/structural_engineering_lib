"""HTML output for the bounded unequal-span finite service history."""

from __future__ import annotations

import html
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

from structural_lib.services.canonical_family import CanonicalFamilyResultV1

if TYPE_CHECKING:
    from structural_lib.services.beam_service_history import BeamServiceHistoryInputV1


def _text(value: object) -> str:
    """Escape a report value without treating engineering input as markup."""
    return html.escape(str(value))


def _number(value: object, digits: int = 3) -> str:
    """Render a numeric result compactly while retaining a visible HOLD value."""
    if value is None:
        return "HOLD"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return _text(value)


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _items(value: object) -> Sequence[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(_mapping(item) for item in value)


def _table(headers: Sequence[str], body: Sequence[Sequence[str]]) -> str:
    """Return a small escaped table, or an explicit unavailable marker."""
    if not body:
        return "<p>Not available.</p>"
    header_cells = "".join(f"<th>{_text(label)}</th>" for label in headers)
    rows = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"
        for cells in body
    )
    return f"<table><thead><tr>{header_cells}</tr></thead><tbody>{rows}</tbody></table>"


def _stage_table(history: Mapping[str, Any]) -> str:
    rows: list[list[str]] = []
    for name, label in (
        ("initial", "Initial"),
        ("at_finishes", "At finishes"),
        ("at_assessment", "At assessment"),
    ):
        stage = _mapping(history.get(name))
        rows.append(
            [
                label,
                _number(stage.get("age_days"), 0),
                _number(stage.get("concrete_modulus_nmm2"), 1),
                _number(stage.get("neutral_axis_mm")),
                _number(stage.get("cracked_inertia_mm4"), 0),
                _number(stage.get("cracking_moment_knm")),
            ]
        )
    return _table(
        ("Stage", "Age (days)", "Ec (N/mm²)", "x (mm)", "Icr (mm⁴)", "Mcr (kN·m)"), rows
    )


def _issue_list(result: CanonicalFamilyResultV1[dict[str, Any]]) -> str:
    entries = [
        f"<li><code>{_text(issue.code)}</code> — {_text(issue.message)}</li>"
        for issue in result.issues
    ]
    entries.extend(f"<li>{_text(item)}</li>" for item in result.limitations)
    return "<ul>" + "".join(entries) + "</ul>" if entries else "<p>None recorded.</p>"


def render_unequal_service_history_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render the checked unequal-span service history, without recalculation.

    The report intentionally works from the recorded ``history`` evidence only.
    A ``None`` history remains a useful HOLD report rather than a partial result.
    """
    if not isinstance(result, CanonicalFamilyResultV1):
        raise TypeError("result must be a canonical unequal-span service result")

    calculation = _mapping(result.calculation)
    history_value = calculation.get("history")
    history = _mapping(history_value)
    identity = result.envelope.result_identity
    request = cast("BeamServiceHistoryInputV1", result.request)
    basis = request.unequal_span_basis
    assert basis is not None
    status = result.engineering_status.value

    header = (
        f"<h1>Beam finite service history · unequal spans · {_text(result.identity.case_id)}</h1>"
        f"<p><strong>{_text(status)}</strong> · input hash "
        f"<code>{_text(identity.input_hash if identity else '')}</code></p>"
        "<p>Positive moment is sagging. Shear follows the increasing-station convention. "
        "Positive deflection is downward and negative deflection is upward.</p>"
        f"<p>Axial restraint {_text(basis.axial_restraint)}. "
        f"Shrinkage profile {_text(basis.shrinkage_profile.replace('_', ' '))}. "
        f"{_text(basis.source_reference)}</p>"
    )

    if history_value is None:
        content = "<h2>History held.</h2>"
    else:
        spans = _items(history.get("span_deflections"))
        extrema = _items(history.get("deflection_extrema"))
        cracks = _items(history.get("crack_sections"))
        action_rows = _items(history.get("signed_rows"))
        governing_deflection = history.get("governing_deflection_station_id", "HOLD")
        governing_after = history.get("governing_after_finishes_station_id", "HOLD")
        governing_crack = history.get("governing_crack_station_id", "HOLD")
        material_history, total_load = request.history, request.service_load
        assert (
            material_history is not None
            and material_history.sustained_load is not None
            and total_load is not None
        )
        sustained_load = material_history.sustained_load

        span_rows = [
            [
                _text(item.get("span_id", "")),
                _number(item.get("span_mm"), 0),
                _text(item.get("station_id", "")),
                _number(item.get("x_mm")),
                _number(item.get("initial_total_mm")),
                _number(item.get("at_finishes_mm")),
                _number(item.get("at_assessment_mm")),
                _number(item.get("after_finishes_mm")),
                _number(item.get("total_limit_mm")),
                _number(item.get("after_finishes_limit_mm")),
            ]
            for item in spans
        ]
        extrema_rows = [
            [
                _text(item.get("span_id", "")),
                _text(item.get("station_id", "")),
                _number(item.get("x_mm")),
                _number(item.get("at_assessment_mm")),
                _number(item.get("after_finishes_mm")),
                _number(item.get("shrinkage_deflection_mm")),
            ]
            for item in extrema
        ]
        crack_rows = [
            [
                _text(item.get("station_id", "")),
                _number(item.get("x_mm")),
                _text(item.get("tension_face", "")),
                "yes" if item.get("cracked") else "no",
                _number(item.get("width_mm")),
                _text(item.get("assessment_row_id", "")),
                _text(item.get("sustained_row_id", "")),
                _number(item.get("tensile_steel_stress_nmm2")),
            ]
            for item in cracks
        ]
        current_stations = {
            station.station_id: station for station in request.member.stations
        }
        signed_rows = [
            [
                _text(item.get("row_id", "")),
                _text(item.get("station_id", "")),
                _number(current_stations[item["station_id"]].x_mm),
                _text(current_stations[item["station_id"]].side),
                _number(item.get("mu_knm")),
                _number(item.get("vu_kn")),
                _number(item.get("tu_knm")),
            ]
            for item in action_rows
        ]
        governing_width = next(
            item["width_mm"] for item in cracks if item["station_id"] == governing_crack
        )
        content = f"""
<p>Each span carries {_number(sustained_load.uniform_load_kn_per_m)} kN/m from day {_number(material_history.loading_age_days, 0)} and {_number(total_load.uniform_load_kn_per_m)} kN/m at assessment.</p>
<h2>Section stages</h2>{_stage_table(history)}
<p>Uniform shrinkage curvature is <strong>{_number(history.get('uniform_shrinkage_curvature_per_mm'), 8)} /mm</strong>.</p>
<h2>Governing checks</h2>
<p>Deflection governs at {_text(governing_deflection)} at assessment and at {_text(governing_after)} after finishes.</p>
<p>Crack width governs at {_text(governing_crack)}. Calculated {_number(governing_width, 5)} mm against the {_number(request.crack_width_limit_mm)} mm limit.</p>
<h2>Per-span staged deflection</h2>{_table(('Span', 'Length (mm)', 'Station', 'x (mm)', 'Initial (mm)', 'Finishes (mm)', 'Assessment (mm)', 'After finishes (mm)', 'Total limit (mm)', 'After finishes limit (mm)'), span_rows)}
<h2>Deflection extrema</h2>{_table(('Span', 'Station', 'x (mm)', 'Assessment (mm)', 'After finishes (mm)', 'Shrinkage (mm)'), extrema_rows)}
<h2>Assessment crack sections</h2>{_table(('Station', 'x (mm)', 'Tension face', 'Cracked', 'Width (mm)', 'Assessment action', 'Sustained action', 'Steel stress (N/mm²)'), crack_rows)}
<h2>Signed service action rows</h2>{_table(('Row', 'Station', 'x (mm)', 'Side', 'M (kN·m)', 'V (kN)', 'T (kN·m)'), signed_rows)}
"""

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Unequal-span service history</title>
<style>body{{font:14px/1.4 system-ui,sans-serif;margin:24px;color:#17202a}} table{{border-collapse:collapse;margin:8px 0 20px;max-width:100%}} th,td{{border:1px solid #aeb6bf;padding:4px 7px;text-align:right;white-space:nowrap}} th:first-child,td:first-child{{text-align:left}} h2{{margin-top:24px}} code{{font-size:.9em}}</style></head><body>
{header}{content}<h2>Diagnostics and limitations</h2>{_issue_list(result)}</body></html>"""
