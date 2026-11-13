"""Compose signed slender-column actions with the actual checked cage."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import asdict, replace
from html import escape
from typing import Any

from structural_lib.codes.is456.column._common import _calculate_puz
from structural_lib.codes.is456.column._strain_compatibility import (
    COLUMN_SECTION_METHOD,
)
from structural_lib.codes.is456.column.detailing import check_longitudinal_limits
from structural_lib.codes.is456.column.positioned_biaxial import (
    PositionedColumnBar,
    prepare_positioned_capacity,
)
from structural_lib.codes.is456.column.slender_positioned import (
    equivalent_slender_pairs,
    slender_plane_demand,
)
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.column_positioned_member import (
    evaluate_positioned_rectangular_cage,
)
from structural_lib.services.column_tied_member import (
    evaluate_tied_rectangular_cage,
    rectangular_section_markup,
)
from structural_lib.services.contracts.column_member import RectangularColumnCageV1
from structural_lib.services.contracts.column_slender import (
    FirstOrderColumnActionsV1,
    SlenderRectangularColumnInputV1,
)

_WORKFLOW = "is456.column.slender-rectangular-member-check/v1"
_SOURCE = "IS 456:2000 Cl. 25.1–25.4, 38.1 and 39.1–39.7"
_CAGE_SOURCE = "IS 456:2000 Cl. 26.3, 26.4 and 26.5.3.2"
_Result = CanonicalFamilyResultV1[dict[str, Any]]
_PASS, _FAIL, _HOLD = (
    EngineeringStatus.PASS,
    EngineeringStatus.FAIL,
    EngineeringStatus.HOLD,
)


def _combined(*statuses: EngineeringStatus) -> EngineeringStatus:
    if _FAIL in statuses:
        return _FAIL
    return _HOLD if _HOLD in statuses else _PASS


def _cage(
    request: SlenderRectangularColumnInputV1, record: Callable[..., None]
) -> tuple[
    tuple[PositionedColumnBar, ...], dict[str, Any] | None, tuple[dict[str, Any], ...]
]:
    geometry, steel = request.geometry, request.reinforcement
    if isinstance(steel, RectangularColumnCageV1):
        tied, paths = evaluate_tied_rectangular_cage(
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            steel=steel,
            record=record,
        )
        if tied is None:
            return (), None, paths
        bars = tuple(
            PositionedColumnBar(
                bar.bar_id,
                bar.x_from_left_mm,
                bar.y_from_top_mm,
                bar.diameter_mm,
                "outer",
            )
            for bar in tied.bars
        )
        return bars, asdict(tied), paths

    bars = tuple(PositionedColumnBar(**bar.model_dump()) for bar in steel.bars)
    ratio, minimum_ok, maximum_ok, _ = check_longitudinal_limits(
        geometry.b_mm * geometry.D_mm, sum(bar.area_mm2 for bar in bars)
    )
    record(
        "COLUMN.LONGITUDINAL_RATIO",
        _PASS if minimum_ok and maximum_ok else _FAIL,
        "reinforcement.bars",
        "Check the admitted 0.8–4% longitudinal steel range.",
        actual=ratio,
        source_reference=_CAGE_SOURCE,
    )
    cage, link_paths = evaluate_positioned_rectangular_cage(
        b_mm=geometry.b_mm,
        D_mm=geometry.D_mm,
        steel=steel,
        bars=bars,
        ratio=ratio,
        record=record,
    )
    return bars, cage, tuple(asdict(path) for path in link_paths)


def _strength(
    request: SlenderRectangularColumnInputV1,
    bars: tuple[PositionedColumnBar, ...],
    rows: dict[str, dict[str, Any]],
    record: Callable[..., None],
) -> tuple[EngineeringStatus, dict[str, Any] | None]:
    geometry, actions, mat = request.geometry, request.actions, request.materials
    puz = _calculate_puz(
        geometry.b_mm,
        geometry.D_mm,
        mat.fck_nmm2,
        mat.fy_nmm2,
        sum(bar.area_mm2 for bar in bars),
    )
    if actions.pu_kn >= puz:
        record(
            "COLUMN.AXIAL_LIMIT",
            _FAIL,
            "actions.pu_kn",
            "Compression reaches the Cl. 39.6 axial limit.",
            actual=actions.pu_kn,
            limit=puz,
        )
        return _FAIL, None
    section = prepare_positioned_capacity(
        b_mm=geometry.b_mm,
        D_mm=geometry.D_mm,
        pu_kn=actions.pu_kn,
        fck_nmm2=mat.fck_nmm2,
        fy_nmm2=mat.fy_nmm2,
        bars=bars,
    )
    evaluated: dict[str, dict[str, Any]] = {}
    minimum: dict[str, float] = {}
    if section is not None:
        for identifier, row in rows.items():
            checked = section.check(
                row["mx_knm"],
                row["my_knm"],
                geometry.x.unsupported_length_mm,
                geometry.y.unsupported_length_mm,
            )
            if checked is None:
                break
            minimum = checked.minimum_eccentricity_ratios
            evaluated[identifier] = {
                **row,
                "contour_ratio": checked.contour_ratio,
                "direct_ratio": checked.direct_ratio,
                "ratio": max(checked.contour_ratio, checked.direct_ratio),
                "demand": (
                    asdict(checked.demand) if checked.demand is not None else None
                ),
            }
    if section is None or len(evaluated) != len(rows):
        record(
            "COLUMN.PM_BASIS",
            _HOLD,
            "actions",
            "A signed section equilibrium could not be established for every row.",
        )
        return _HOLD, None

    ratios = {
        **{name: row["ratio"] for name, row in evaluated.items()},
        **{f"MIN-ECC-{axis.upper()}": ratio for axis, ratio in minimum.items()},
    }
    utilization = max(ratios.values())
    governing = min(
        name for name, ratio in ratios.items() if utilization - ratio < 1e-8
    )
    status = _PASS if utilization <= 1 else _FAIL
    record(
        "COLUMN.PM_STRENGTH",
        status,
        "actions",
        "Check the signed interaction contour, demand rays and separate minimum eccentricities.",
        actual=utilization,
        limit=1,
        governing_id=governing,
        source_reference=_SOURCE,
    )
    return status, {
        "axes": {name: asdict(ray) for name, ray in section.axes.items()},
        "puz_kn": puz,
        "alpha_n": section.alpha_n,
        "evaluated": evaluated,
        "minimum_eccentricity_ratios": minimum,
        "governing_id": governing,
        "governing_ratio": utilization,
    }


def check_slender_rectangular_member(
    request: SlenderRectangularColumnInputV1,
) -> _Result:
    """Check supplied actions and independent local restraint on the actual bars."""
    require_request_type(request, SlenderRectangularColumnInputV1)
    geometry, actions = request.geometry, request.actions
    checks: list[dict[str, Any]] = []
    issues: list[StructuralIssueV1] = []

    def record(
        code: str, status: EngineeringStatus, path: str, message: str, **values: Any
    ) -> None:
        checks.append(
            {"code": code, "status": status, "path": path, "message": message, **values}
        )
        if status is not _PASS:
            issues.append(StructuralIssueV1(code, path, message))

    bars, cage, links = _cage(request, record)
    restraint_status = _combined(*(check["status"] for check in checks))
    first_order = isinstance(actions, FirstOrderColumnActionsV1)
    planes = {}
    for axis, restraint, dimension in (
        ("x", geometry.x, geometry.D_mm),
        ("y", geometry.y, geometry.b_mm),
    ):
        ends = None
        if isinstance(actions, FirstOrderColumnActionsV1):
            key = f"m{axis}_knm"
            ends = (getattr(actions.end_a, key), getattr(actions.end_b, key))
        planes[axis] = slender_plane_demand(
            dimension_mm=dimension,
            unsupported_mm=restraint.unsupported_length_mm,
            effective_mm=restraint.effective_length_mm,
            pu_kn=actions.pu_kn,
            end_moments_knm=ends,
        )
        limit = 60 * min(geometry.b_mm, geometry.D_mm)
        record(
            "COLUMN.UNSUPPORTED_LENGTH",
            _PASS if restraint.unsupported_length_mm <= limit else _FAIL,
            f"geometry.{axis}.unsupported_length_mm",
            "Check the unsupported length against Cl. 25.3.1.",
            actual=restraint.unsupported_length_mm,
            limit=limit,
            source_reference=_SOURCE,
        )
        if planes[axis].slenderness > 60:
            record(
                "COLUMN.EFFECTIVE_LENGTH_PROFILE",
                _HOLD,
                f"geometry.{axis}.effective_length_mm",
                "This member profile admits an effective slenderness ratio at most 60.",
            )

    rows: dict[str, dict[str, Any]] = {}
    if isinstance(actions, FirstOrderColumnActionsV1):
        for identifier, station, pair in (
            ("A", 0, actions.end_a),
            ("B", geometry.length_mm, actions.end_b),
        ):
            rows[identifier] = {
                **pair.model_dump(),
                "station_mm": station,
                "kind": "supplied_end",
            }
        if actions.has_transverse_member_load is not False:
            record(
                "COLUMN.FIRST_ORDER_PROFILE",
                _HOLD,
                "actions.has_transverse_member_load",
                "The braced first-order method requires confirmation of no transverse member load.",
            )
        for identifier, mx, my in equivalent_slender_pairs(planes["x"], planes["y"]):
            rows[identifier] = {
                "mx_knm": mx,
                "my_knm": my,
                "station_mm": None,
                "kind": "equivalent_design_pair",
            }
    else:
        for row in actions.stations:
            rows[row.station_id] = {
                "mx_knm": row.mx_knm,
                "my_knm": row.my_knm,
                "station_mm": row.station_mm,
                "kind": "supplied_second_order",
            }
        if (
            not actions.member_deflection_basis
            or not actions.member_deflection_basis.strip()
        ):
            record(
                "COLUMN.MEMBER_DEFLECTION_BASIS",
                _HOLD,
                "actions.member_deflection_basis",
                "Identify the analysis that included local deflection effects and critical stations.",
            )
        required = set(actions.required_station_ids)
        missing = sorted(required - rows.keys())
        coverage = {rows[key]["station_mm"] for key in required & rows.keys()}
        if missing or not {0, geometry.length_mm} <= coverage:
            record(
                "COLUMN.REQUIRED_STATIONS",
                _HOLD,
                "actions.stations",
                "Supply the declared critical stations including both member ends.",
                missing_ids=missing,
            )
    if request.analysis_revision != request.current_analysis_revision:
        record(
            "COLUMN.STALE_ANALYSIS",
            _HOLD,
            "analysis_revision",
            "Refresh the actions to match the current analysis revision.",
        )
    if request.materials.fck_nmm2 > 60:
        record(
            "COLUMN.CONCRETE_PROFILE",
            _HOLD,
            "materials.fck_nmm2",
            "This profile admits concrete through M60.",
        )

    action_status = _combined(
        *(
            check["status"]
            for check in checks
            if not check["path"].startswith("reinforcement")
        )
    )
    strength_status, strength = _HOLD, None
    if bars and restraint_status is not _FAIL and action_status is _PASS:
        strength_status, strength = _strength(request, bars, rows, record)

    result = canonical_family_result(
        request,
        {
            "scope": "Actual rectangular cage and braced slender-member action check",
            "basis": actions.basis,
            "combination_id": actions.combination_id,
            "analysis_revision": request.analysis_revision,
            "current_analysis_revision": request.current_analysis_revision,
            "member_deflection_basis": (
                None
                if isinstance(actions, FirstOrderColumnActionsV1)
                else actions.member_deflection_basis
            ),
            "axes": {
                name: {
                    **asdict(values),
                    "restraint_basis": getattr(geometry, name).restraint_basis,
                }
                for name, values in planes.items()
            },
            "action_rows": rows,
            "strength": strength,
            "strength_status": strength_status,
            "restraint_status": restraint_status,
            "cage": cage,
            "cross_ties": links,
            "section_quantities": {
                "longitudinal_count_by_diameter_mm": dict(
                    Counter(f"{bar.diameter_mm:g}" for bar in bars)
                ),
                "perimeter_count_per_pitch": int(request.reinforcement.tie is not None),
                "cross_tie_count_per_pitch": len(request.reinforcement.cross_ties),
            },
            "checks": checks,
        },
        workflow_id=_WORKFLOW,
        engineering_status=_combined(restraint_status, action_status, strength_status),
        assumptions=(
            "Compression is positive. Positive Mx compresses the top and positive My compresses the left.",
            "Each check uses one concurrent combination with the same axial force at the supplied stations.",
            (
                "First-order additions are unreduced. Signed component bounds form conservative equivalent pairs."
                if first_order
                else "Supplied station moments already include the declared local deflection effects."
            ),
        ),
        limitations=(
            "Prismatic braced members with independently declared axis restraint and effective lengths.",
            "The supplied analysis and its station inventory must cover the required member actions.",
            "Local cage geometry and quantities cover the checked cross section. Member shear, splices, joints, global sway and fabrication require separate checks.",
        ),
        provenance=(COLUMN_SECTION_METHOD, _SOURCE, _CAGE_SOURCE),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def _checked_result(result: _Result) -> tuple[SlenderRectangularColumnInputV1, str]:
    request = result.request
    identity = result.envelope.result_identity
    if (
        result.workflow_id != _WORKFLOW
        or not isinstance(request, SlenderRectangularColumnInputV1)
        or identity is None
        or identity.input_hash is None
    ):
        raise TypeError("A slender rectangular column member result is required")
    return request, identity.input_hash


def render_slender_rectangular_member_svg(result: _Result) -> str:
    """Draw the checked cross section and carry the same result identity."""
    request, input_hash = _checked_result(result)
    width, depth = request.geometry.b_mm, request.geometry.D_mm
    calculation = result.calculation
    section, _ = rectangular_section_markup(
        calculation["cage"], calculation["cross_ties"], width, depth
    )
    case = escape(request.identity.case_id)
    hoop = request.reinforcement.tie
    hoop_label = escape(hoop.tie_id) if hoop is not None else "not supplied"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {depth}" width="320" role="img" aria-labelledby="title">
<title id="title">{case} checked column section · {result.engineering_status.value}</title>
<desc>{width:g} × {depth:g} mm · Hoop {hoop_label} · Input SHA-256 {input_hash} · Local restraint {calculation['restraint_status']}</desc>
<rect x="0" y="0" width="{width}" height="{depth}" fill="#f4f7fa" stroke="#172b4d"/>
{''.join(section)}
</svg>
"""


def render_slender_rectangular_member_html(result: _Result) -> str:
    """Render member actions, governing check and the same checked section."""
    request, input_hash = _checked_result(result)
    calc = result.calculation
    strength = calc["strength"]
    evaluated = strength["evaluated"] if strength else {}
    axis_rows = "".join(
        f"<tr><td>{axis.upper()}</td><td>{row['unsupported_length_mm']:g}</td>"
        f"<td>{row['effective_length_mm']:g}</td><td>{row['slenderness']:.4f}</td>"
        f"<td>{row['classification']}</td><td>{row['minimum_eccentricity_mm']:.3f}</td>"
        f"<td>{row['additional_moment_knm']:.3f}</td><td>{escape(row['restraint_basis'])}</td></tr>"
        for axis, row in calc["axes"].items()
    )
    action_rows = []
    for identifier, row in calc["action_rows"].items():
        station = row["station_mm"]
        station_text = f"{station:g}" if station is not None else "Equivalent pair"
        ratio = (
            f"{evaluated[identifier]['ratio']:.5f}" if identifier in evaluated else "—"
        )
        action_rows.append(
            f"<tr><td>{escape(identifier)}</td><td>{station_text}</td>"
            f"<td>{row['mx_knm']:.3f}</td><td>{row['my_knm']:.3f}</td><td>{ratio}</td></tr>"
        )
    governing = "<p>Strength evaluation unavailable for the supplied basis.</p>"
    if strength:
        minimum = strength["minimum_eccentricity_ratios"]
        capacities = strength["axes"]
        governing = (
            f"<p>Governing check <strong>{escape(strength['governing_id'])}</strong>"
            f" · Utilization {strength['governing_ratio']:.5f}</p>"
            f"<p>Minimum-eccentricity utilization · X {minimum['x']:.5f} · Y {minimum['y']:.5f}</p>"
            f"<p>Signed capacity magnitudes (kNm) · +Mx {capacities['x_positive']['capacity_knm']:.3f}"
            f" · −Mx {capacities['x_negative']['capacity_knm']:.3f}"
            f" · +My {capacities['y_positive']['capacity_knm']:.3f}"
            f" · −My {capacities['y_negative']['capacity_knm']:.3f}</p>"
        )
    details = "".join(
        f"<li>{escape(check['code'])} · {check['status']} · {escape(check['message'])}</li>"
        for check in calc["checks"]
    )
    sources = "".join(
        f"<li>{escape(item)}</li>"
        for item in (*result.provenance, *result.assumptions, *result.limitations)
    )
    deflection_basis = calc["member_deflection_basis"]
    analysis_basis = (
        f"<p>Member deflection basis {escape(deflection_basis)}</p>"
        if deflection_basis
        else ""
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Slender rectangular column check</title>
<style>body{{font:16px system-ui;margin:2rem;color:#172b4d}}table{{border-collapse:collapse}}
th,td{{padding:.45rem;border:1px solid #c4ceda}}svg{{max-width:100%;height:auto}}code{{overflow-wrap:anywhere}}</style>
<h1>Slender rectangular column check</h1>
<p>Case {escape(request.identity.case_id)} · Combination {escape(calc['combination_id'])} · Pu {request.actions.pu_kn:g} kN</p>
<p>Analysis revision {escape(calc['analysis_revision'])} · Current revision {escape(calc['current_analysis_revision'])} · Basis {escape(calc['basis'])}</p>
{analysis_basis}
<p><strong>Engineering status {result.engineering_status.value}</strong> · {result.envelope.review_status.value}</p>
<p>Section strength {calc['strength_status']} · Local restraint {calc['restraint_status']}</p>
<p>Input SHA-256 <code>{input_hash}</code></p>
<h2>Member restraint and additions</h2><table>
<tr><th>Axis</th><th>Unsupported length (mm)</th><th>Effective length (mm)</th><th>Slenderness</th>
<th>Class</th><th>Minimum eccentricity (mm)</th><th>Additional moment (kNm)</th><th>Restraint basis</th></tr>
{axis_rows}</table>
<h2>Signed action checks</h2><table>
<tr><th>ID</th><th>Station (mm)</th><th>Mx (kNm)</th><th>My (kNm)</th><th>Utilization</th></tr>
{''.join(action_rows)}</table>{governing}
<h2>Checked local section</h2>{render_slender_rectangular_member_svg(result)}
<h2>Checks</h2><ul>{details}</ul>
<h2>Sources and scope</h2><ul>{sources}</ul></html>
"""
