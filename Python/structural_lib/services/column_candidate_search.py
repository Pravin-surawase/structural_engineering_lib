"""Select a short tied rectangular column from a caller's finite catalogue."""

from __future__ import annotations

from dataclasses import dataclass, replace
from html import escape
from itertools import product
from math import pi
from typing import Any

from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.column_tied_member import (
    check_tied_rectangular_member,
    rectangular_section_markup,
)
from structural_lib.services.contracts.column_catalogue import (
    ColumnCatalogueInputV1,
    ColumnCatalogueSizeV1,
    ColumnCatalogueTieV1,
)
from structural_lib.services.contracts.column_member import (
    FourCornerColumnGeometryV1,
    RectangularColumnActionsV1,
    RectangularColumnCageV1,
    TiedRectangularColumnInputV1,
)

_WORKFLOW = "is456.column.catalogue-selection/v1"
_Result = CanonicalFamilyResultV1[dict[str, Any]]


def _input_hash(result: _Result) -> str:
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    return identity.input_hash


@dataclass(frozen=True)
class _Candidate:
    size: ColumnCatalogueSizeV1
    diameter: int
    option: ColumnCatalogueTieV1

    @property
    def identifier(self) -> str:
        return f"{self.size.size_id}/{self.diameter}/{self.option.option_id}"

    @property
    def rank(self) -> tuple[float, float, float, float, int, float, float, str, str]:
        return (
            self.size.b_mm * self.size.D_mm,
            2 * pi * self.diameter**2,
            self.size.b_mm,
            self.size.D_mm,
            self.diameter,
            self.option.tie.diameter_mm,
            -self.option.tie.spacing_mm,
            self.option.option_id,
            self.size.size_id,
        )


def _evaluate(
    request: ColumnCatalogueInputV1, candidate: _Candidate
) -> tuple[dict[str, Any], _Result | None]:
    size, diameter, option = candidate.size, candidate.diameter, candidate.option
    geometry = FourCornerColumnGeometryV1(
        b_mm=size.b_mm, D_mm=size.D_mm, **request.member.model_dump()
    )
    offset = (
        request.detailing.nominal_cover_mm
        + option.tie.diameter_mm
        + diameter / 2
        + request.detailing.corner_inset_mm
    )
    reinforcement = RectangularColumnCageV1(
        layout="eight_bar",
        longitudinal_bar_diameter_mm=diameter,
        bar_center_offset_mm=offset,
        tie=option.tie,
        cross_ties=option.cross_ties,
        **request.detailing.model_dump(exclude={"corner_inset_mm"}),
    )
    combinations: dict[str, dict[str, Any]] = {}
    statuses: set[EngineeringStatus] = set()
    governing: _Result | None = None
    governing_id: str | None = None
    governing_ratio: float | None = None
    for action in sorted(request.actions, key=lambda row: row.combination_id):
        checked = check_tied_rectangular_member(
            TiedRectangularColumnInputV1(
                identity=request.identity.model_copy(
                    update={
                        "case_id": f"{candidate.identifier}:{action.combination_id}"
                    }
                ),
                geometry=geometry,
                materials=request.materials,
                reinforcement=reinforcement,
                actions=RectangularColumnActionsV1(
                    **action.model_dump(exclude={"combination_id"})
                ),
            )
        )
        statuses.add(checked.engineering_status)
        strength = checked.calculation["strength"]
        ratio = strength["governing_ratio"] if strength is not None else None
        combinations[action.combination_id] = {
            "status": checked.engineering_status.value,
            "utilization": ratio,
            "check_station_mm": action.check_station_mm,
            "issue_codes": [issue.code for issue in checked.issues],
            "check_input_hash": _input_hash(checked),
        }
        if ratio is not None and (governing_ratio is None or ratio > governing_ratio):
            governing, governing_id, governing_ratio = (
                checked,
                action.combination_id,
                ratio,
            )

    # One proven failure rules out this option even if another row remains held.
    status = (
        EngineeringStatus.FAIL
        if EngineeringStatus.FAIL in statuses
        else (
            EngineeringStatus.HOLD
            if EngineeringStatus.HOLD in statuses
            else EngineeringStatus.PASS
        )
    )
    return {
        "status": status.value,
        "b_mm": size.b_mm,
        "D_mm": size.D_mm,
        "longitudinal_bar_count": 8,
        "longitudinal_bar_diameter_mm": diameter,
        "bar_center_offset_mm": offset,
        "tie_option_id": option.option_id,
        "tie_diameter_mm": option.tie.diameter_mm,
        "tie_spacing_mm": option.tie.spacing_mm,
        "combinations": combinations,
        "governing_combination_id": governing_id,
        "utilization": governing_ratio,
    }, governing


def _analysis_status(request: ColumnCatalogueInputV1, checked: _Result) -> str:
    basis = request.analysis
    member = checked.request
    assert isinstance(member, TiedRectangularColumnInputV1)
    if basis.analysis_revision != basis.current_analysis_revision:
        return "STALE_ANALYSIS"
    if (
        basis.geometry != member.geometry
        or basis.fck_nmm2 != member.materials.fck_nmm2
        or basis.stiffness_basis != "gross_section"
    ):
        return "ANALYSIS_REFRESH_REQUIRED"
    return "BOUND"


def select_column_from_catalogue(request: ColumnCatalogueInputV1) -> _Result:
    """Check every required row of each visited option and select only after complete evaluation."""
    require_request_type(request, ColumnCatalogueInputV1)
    catalogue = sorted(
        (
            _Candidate(*entry)
            for entry in product(
                request.sizes, request.longitudinal_diameters_mm, request.tie_options
            )
        ),
        key=lambda candidate: candidate.rank,
    )
    evaluated: dict[str, dict[str, Any]] = {}
    eligible: list[str] = []
    first_eligible: _Result | None = None
    for candidate in catalogue[: request.evaluation_limit]:
        summary, governing = _evaluate(request, candidate)
        evaluated[candidate.identifier] = summary
        if summary["status"] == "PASS":
            eligible.append(candidate.identifier)
            if first_eligible is None:
                first_eligible = governing

    complete = len(evaluated) == len(catalogue)
    selected_id = None
    selected = None
    analysis_status = None
    issues: tuple[StructuralIssueV1, ...] = ()
    status = EngineeringStatus.HOLD
    if not complete:
        terminal = "INCOMPLETE_BUDGET"
        issues = (
            StructuralIssueV1(
                "COLUMN.CATALOGUE_BUDGET",
                "evaluation_limit",
                "The supplied budget stopped evaluation before the full catalogue was checked.",
            ),
        )
    elif any(row["status"] == "HOLD" for row in evaluated.values()):
        terminal = "BLOCKED_MANDATORY_CHECK"
        issues = (
            StructuralIssueV1(
                "COLUMN.CATALOGUE_CHECKS_HELD",
                "calculation.evaluated",
                "One or more candidates still require a mandatory check.",
            ),
        )
    elif not eligible:
        terminal = "COMPLETE_INFEASIBLE"
        status = EngineeringStatus.FAIL
        issues = (
            StructuralIssueV1(
                "COLUMN.CATALOGUE_INFEASIBLE",
                "calculation.evaluated",
                "Every candidate failed a mandatory check for the supplied actions.",
            ),
        )
    else:
        assert first_eligible is not None
        terminal = "COMPLETE_FEASIBLE"
        selected_id = eligible[0]
        selected = {
            "candidate_id": selected_id,
            "checked_member": first_eligible.to_dict(),
        }
        analysis_status = _analysis_status(request, first_eligible)
        if analysis_status == "BOUND":
            status = EngineeringStatus.PASS
        else:
            message = (
                "The supplied analysis revision is not the current revision."
                if analysis_status == "STALE_ANALYSIS"
                else "Refresh actions for the selected geometry and stiffness basis before accepting the member."
            )
            issues = (
                StructuralIssueV1(f"COLUMN.{analysis_status}", "analysis", message),
            )

    result = canonical_family_result(
        request,
        {
            "terminal_state": terminal,
            "catalogue_count": len(catalogue),
            "evaluated_count": len(evaluated),
            "enumeration_complete": complete,
            "eligible_ids": eligible,
            "selected_id": selected_id,
            "selected": selected,
            "analysis_status": analysis_status,
            "evaluated": evaluated,
        },
        workflow_id=_WORKFLOW,
        engineering_status=status,
        assumptions=(
            "The catalogue and analysis basis are supplied by the caller.",
            "Positive Mx compresses the top face; positive My compresses the left face.",
            "Each signed action triplet is checked at its declared station.",
        ),
        limitations=(
            "Only supplied combinations and stations are checked. Their completeness is not established.",
            "Short braced rectangles with eight equal bars and ordinary ties only.",
            "Selection is based on the documented rank, not cost or fabrication optimisation.",
            "Member shear, laps, anchorage, seismic checks and fabrication schedules require separate evidence.",
        ),
        provenance=(
            "COL06 finite-catalogue ranking; docs/verification/library-029-col06-column-catalogue.json",
            "Local strength and restraint: is456.column.tied-rectangular-member-check/v1",
        ),
    )
    return replace(result, envelope=replace(result.envelope, issues=issues))


def _require_result(result: _Result) -> ColumnCatalogueInputV1:
    if result.workflow_id != _WORKFLOW or not isinstance(
        result.request, ColumnCatalogueInputV1
    ):
        raise TypeError("A column catalogue selection result is required")
    return result.request


def render_column_catalogue_svg(result: _Result) -> str | None:
    """Draw the same local cage that was checked for the governing combination."""
    _require_result(result)
    selected = result.calculation["selected"]
    if selected is None:
        return None
    checked = selected["checked_member"]
    geometry = checked["request"]["geometry"]
    width, depth = geometry["b_mm"], geometry["D_mm"]
    local = checked["calculation"]
    section, _ = rectangular_section_markup(
        local["cage"], local["cross_ties"], width, depth
    )
    basis = _input_hash(result)
    child_hash = checked["envelope"]["result_identity"]["input_hash"]
    identifier = escape(selected["candidate_id"])
    title = f"{result.engineering_status.value} · {identifier} · local section"
    hoop = checked["request"]["reinforcement"]["tie"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -28 {width + 10:g} {depth + 33:g}" role="img" aria-labelledby="column-section-title">'
        f'<title id="column-section-title">{title}</title>'
        f"<desc>Catalogue input {basis}; governing check input {child_hash}. Section only, not a fabrication drawing.</desc>"
        f'<text x="0" y="-16" font-size="10">{result.engineering_status.value} · local section</text>'
        f'<text x="0" y="-4" font-size="9">{width:g} × {depth:g} mm · 8Ø{checked["request"]["reinforcement"]["longitudinal_bar_diameter_mm"]:g}'
        f' · Ø{hoop["diameter_mm"]:g} @ {hoop["spacing_mm"]:g} mm</text>'
        f'<rect x="0" y="0" width="{width:g}" height="{depth:g}" fill="#f5f7fa" stroke="#172b4d"/>'
        f'{"".join(section)}</svg>'
    )


def render_column_catalogue_html(result: _Result) -> str:
    """Report the search outcome, the signed checks and the checked section."""
    request = _require_result(result)
    calc = result.calculation
    actions = {row.combination_id: row for row in request.actions}
    rows = []
    for identifier, option in calc["evaluated"].items():
        for combination_id, check in option["combinations"].items():
            row = actions[combination_id]
            ratio = check["utilization"]
            ratio_text = f"{ratio:.4f}" if ratio is not None else "—"
            rows.append(
                f'<tr><td>{escape(identifier)}</td><td>{option["status"]}</td><td>{escape(combination_id)}</td>'
                f"<td>{row.check_station_mm:g}</td><td>{row.pu_kn:g} / {row.mx_knm:g} / {row.my_knm:g}</td>"
                f'<td>{check["status"]}</td><td>{ratio_text}</td><td>{escape(", ".join(check["issue_codes"]))}</td></tr>'
            )
    issues = "".join(f"<li>{escape(issue.message)}</li>" for issue in result.issues)
    limits = "".join(f"<li>{escape(limit)}</li>" for limit in result.limitations)
    selection = "<p>No candidate selected.</p>"
    identifier = calc["selected_id"]
    if identifier is not None:
        option = calc["evaluated"][identifier]
        governing = option["governing_combination_id"]
        check_hash = option["combinations"][governing]["check_input_hash"]
        checked = calc["selected"]["checked_member"]
        hoop = checked["request"]["reinforcement"]["tie"]
        links = "".join(
            f"<li>{escape(link['tie_id'])} · {escape(', '.join(link['restrained_bar_ids']))}"
            f" · {link['station_offset_mm']:g} mm from hoop level</li>"
            for link in checked["calculation"]["cross_ties"]
        )
        sources = "".join(
            f"<li>{escape(source)}</li>" for source in checked["provenance"]
        )
        selection = (
            f"<p>Selected: {escape(identifier)} · governing combination {escape(governing)} "
            f'· utilization {option["utilization"]:.4f} · analysis {calc["analysis_status"]}.</p>'
            f"<p>Governing check input: <code>{check_hash}</code></p>"
            f"{render_column_catalogue_svg(result)}"
            f"<p>Hoop {escape(hoop['tie_id'])} · Ø{hoop['diameter_mm']:g} at {hoop['spacing_mm']:g} mm"
            f" · {hoop['internal_bend_radius_mm']:g} mm inside bend radius.</p>"
            f"<ul>{links}</ul><details><summary>Governing check sources</summary><ul>{sources}</ul></details>"
        )
    input_hash = _input_hash(result)
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Column catalogue selection</title>'
        "<style>body{font:16px system-ui;margin:2rem;max-width:80rem}table{border-collapse:collapse}"
        "th,td{padding:.4rem;border:1px solid #cdd5df;text-align:left}svg{width:min(100%,26rem);display:block}</style>"
        f"<h1>Column catalogue selection · {result.engineering_status.value}</h1>"
        f'<p>{calc["terminal_state"]} · {calc["evaluated_count"]} of {calc["catalogue_count"]} candidates checked.</p>'
        f"<p>Analysis revision: {escape(request.analysis.analysis_revision)}; current revision: "
        f"{escape(request.analysis.current_analysis_revision)}. Qualified review required.</p>"
        f"<p>Catalogue input: <code>{input_hash}</code></p><ul>{issues}</ul>{selection}"
        "<h2>Checks in catalogue rank order</h2><table><thead><tr><th>Candidate</th><th>Candidate status</th>"
        "<th>Combination</th><th>Station (mm)</th><th>Pu / Mx / My (kN / kNm / kNm)</th>"
        f'<th>Check status</th><th>Utilization</th><th>Issues</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
        f"<h2>Scope</h2><ul>{limits}</ul></html>"
    )
