"""Check direct deflection and flexural cracking of the positioned slab strip."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import replace
from itertools import pairwise
from typing import Any

from structural_lib.codes.is456.beam.serviceability import (
    _elastic_deflection,
    _sls_section,
    calculate_cracking_moment,
    calculate_shrinkage_curvature,
    calculate_shrinkage_deflection,
    check_crack_width,
)
from structural_lib.codes.is456.slab.detailing import (
    ProvidedSlabBars,
    check_slab_reinforcement_region,
)
from structural_lib.core.data_types import SupportCondition
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    FreshnessStatus,
    IntakeStatus,
    StructuralIssueV1,
)
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.slab_direct_service import (
    SlabDirectServiceInputV1,
    SlabServiceAgeV1,
    SlabServiceSectionV1,
)

WORKFLOW = "is456.slab.direct-service/v1"
_ES_NMM2 = 200_000.0
_SOURCE = "IS 456:2000 Clauses 23.2, 24.1, 26.3 and 26.5.2; Annexes C and F"


def load_direct_service(
    value: Mapping[str, object] | SlabDirectServiceInputV1,
) -> SlabDirectServiceInputV1:
    """Load one positioned one-way slab service request.

    Parameters
    ----------
    value : Mapping[str, object] or SlabDirectServiceInputV1
        Decoded request with explicit bar axes, service actions and history.

    Returns
    -------
    SlabDirectServiceInputV1
        Immutable input for :func:`check_direct_service`.

    Raises
    ------
    InputContractError
        The input has an invalid shape, type or value.

    Limitations
    -----------
    The input describes one metre of an interior tributary strip. The check
    evaluates whether its supplied support and history evidence are usable.

    Examples
    --------
    See the frozen B01 request in the direct slab service cookbook.

    Provenance
    ----------
    The request carries caller-owned source references and revision IDs.
    """
    if isinstance(value, SlabDirectServiceInputV1):
        return value
    return model_validate_or_error(SlabDirectServiceInputV1, value)


def _result(
    request: SlabDirectServiceInputV1,
    calculation: dict[str, Any],
    status: EngineeringStatus,
    issues: tuple[StructuralIssueV1, ...] = (),
    *,
    evaluated: bool = True,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    result = canonical_family_result(
        request,
        calculation,
        workflow_id=WORKFLOW,
        engineering_status=status,
        assumptions=(
            "Two simple support lines and a repeated one-metre tributary strip.",
            "One uniform sustained gravity load and one assessment-only transient increment.",
            "Prescribed creep and uniform free shrinkage; no tension stiffening reduction for crack width.",
        ),
        limitations=(
            "Direct service checks for a mild-exposure strip with one bottom main layer, orthogonal distribution steel and no axial restraint.",
            "Elastic bending only. Strength, support anchorage, fire cover and project placement tolerances require their own evidence.",
        ),
        provenance=(_SOURCE,),
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            intake_status=IntakeStatus.VALID if evaluated else IntakeStatus.PARTIAL,
            calculation_status=(
                CalculationStatus.COMPLETED
                if evaluated
                else CalculationStatus.NOT_EVALUATED
            ),
            freshness_status=(
                FreshnessStatus.STALE
                if any(issue.code == "SLAB.SERVICE_REVISION_STALE" for issue in issues)
                else FreshnessStatus.CURRENT
            ),
            issues=issues,
        ),
    )


def _actions(span_mm: float, area_load_kn_per_m2: float) -> tuple[float, float]:
    # One metre strip: kN/m² converts numerically to N/mm.
    return area_load_kn_per_m2 * span_mm**2 / 8e6, area_load_kn_per_m2 * span_mm / 2000


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-7)


def _evidence_issue(request: SlabDirectServiceInputV1) -> StructuralIssueV1 | None:
    edges = request.support_edges
    if (
        edges is None
        or (edges.x_min, edges.x_max, edges.y_min, edges.y_max)
        != ("simple", "simple", "free", "free")
        or request.transverse_panel_span_mm < request.section.strip_width_mm
    ):
        return StructuralIssueV1(
            "SLAB.SERVICE_SUPPORT_HELD",
            "support_edges",
            "Identify two simple support lines and two free edges for the one-metre strip.",
        )
    history = request.history
    if history is None or not (
        history.loading_age_days
        < history.finishes.age_days
        < history.assessment.age_days
        and history.finishes.creep_coefficient <= history.assessment.creep_coefficient
        and history.finishes.shrinkage_strain <= history.assessment.shrinkage_strain
        and history.finish_added_load_kn_per_m2 == 0
        and history.axial_restraint == "free_shortening"
        and history.shrinkage_basis == "uniform_through_depth"
    ):
        return StructuralIssueV1(
            "SLAB.SERVICE_HISTORY_HELD",
            "history",
            "Supply ordered ages and cumulative effects for free, uniform shrinkage with no load added at finishes.",
        )
    loads = request.service_loads
    if loads is None:
        return StructuralIssueV1(
            "SLAB.SERVICE_ACTIONS_HELD",
            "service_loads",
            "Supply total and sustained service action rows.",
        )
    rows = (loads.total, loads.sustained)
    if any(
        row.analysis_revision != request.analysis_revision
        or row.reinforcement_revision != request.reinforcement_revision
        for row in rows
    ):
        return StructuralIssueV1(
            "SLAB.SERVICE_REVISION_STALE",
            "service_loads",
            "The action rows must bind the current analysis and reinforcement revisions.",
        )
    if (
        loads.total.uniform_area_load_kn_per_m2 <= 0
        or loads.sustained.uniform_area_load_kn_per_m2
        > loads.total.uniform_area_load_kn_per_m2
        or loads.total.action_row_id == loads.sustained.action_row_id
        or any(
            not all(
                _close(supplied, expected)
                for supplied, expected in zip(
                    (row.midspan_moment_knm, row.support_shear_kn),
                    _actions(
                        request.effective_span_mm, row.uniform_area_load_kn_per_m2
                    ),
                    strict=True,
                )
            )
            for row in rows
        )
    ):
        return StructuralIssueV1(
            "SLAB.SERVICE_ACTIONS_HELD",
            "service_loads",
            "Provide distinct, concurrent action rows consistent with the verified gravity UDL and span.",
        )
    return None


def _section_issue(section: SlabServiceSectionV1) -> StructuralIssueV1 | None:
    main = sorted(section.main_bars, key=lambda bar: bar.x_from_left_mm)
    first = main[0]
    pitch = section.main_pitch_mm
    if (
        len({bar.bar_id for bar in main}) != len(main)
        or not _close(len(main) * pitch, section.strip_width_mm)
        or any(
            not _close(bar.x_from_left_mm, (i + 0.5) * pitch)
            or not _close(bar.diameter_mm, first.diameter_mm)
            or not _close(bar.y_from_top_mm, first.y_from_top_mm)
            for i, bar in enumerate(main)
        )
    ):
        return StructuralIssueV1(
            "SLAB.SERVICE_LAYOUT_HELD",
            "section.main_bars",
            "Supply the actual equal-diameter single layer on its centred periodic pitch.",
        )
    distribution = section.distribution
    cover = section.thickness_mm - first.y_from_top_mm - first.diameter_mm / 2
    clear_horizontal = min(
        pitch - first.diameter_mm, distribution.pitch_mm - distribution.diameter_mm
    )
    bars_fit = (
        cover >= max(section.nominal_cover_mm, 20, first.diameter_mm)
        and distribution.y_from_top_mm - distribution.diameter_mm / 2
        >= max(section.nominal_cover_mm, 20, distribution.diameter_mm)
        and distribution.y_from_top_mm + distribution.diameter_mm / 2
        <= first.y_from_top_mm - first.diameter_mm / 2
        and clear_horizontal >= section.maximum_aggregate_mm + 5
        and pitch - first.diameter_mm >= first.diameter_mm
        and distribution.pitch_mm - distribution.diameter_mm >= distribution.diameter_mm
    )
    detailing_pass = all(
        check_slab_reinforcement_region(
            region_id=role,
            required_for_moment_mm2_per_m=0,
            bars=bars,
            overall_depth_mm=section.thickness_mm,
            effective_depth_mm=first.y_from_top_mm,
            fy_n_per_mm2=section.fy_nmm2,
            distribution_only=role == "distribution",
        ).is_adequate
        for role, bars in (
            ("main", ProvidedSlabBars(first.diameter_mm, pitch)),
            (
                "distribution",
                ProvidedSlabBars(distribution.diameter_mm, distribution.pitch_mm),
            ),
        )
    )
    if not (bars_fit and detailing_pass):
        return StructuralIssueV1(
            "SLAB.SERVICE_LAYOUT_FAIL",
            "section",
            "The supplied cage fails minimum steel, bar size, pitch, clear spacing, cover or crossing fit.",
        )
    return None


def _section_state(raw: dict[str, float], cracked: bool) -> dict[str, float | bool]:
    return {
        "concrete_modulus_nmm2": raw["ec_nmm2"],
        "neutral_axis_mm": raw["x_mm"],
        "cracked_inertia_mm4": raw["icr_mm4"],
        "effective_inertia_mm4": raw["ieff_mm4"],
        "cracked": cracked,
    }


def _curvature(moment_knm: float, state: dict[str, float]) -> float:
    return moment_knm * 1e6 / (state["ec_nmm2"] * state["icr_mm4"])


def _crack(
    request: SlabDirectServiceInputV1,
    total_knm: float,
    sustained_knm: float,
    initial: dict[str, float],
    long_term: dict[str, float],
    cracked: bool,
) -> dict[str, Any]:
    limit = request.crack_width_limit_mm
    if not cracked:
        return {
            "status": "PASS",
            "method": "uncracked_flexure",
            "width_mm": 0.0,
            "crack_limit_mm": limit,
        }

    section = request.section
    depth = section.thickness_mm
    d = section.main_bars[0].y_from_top_mm
    sustained_k = _curvature(sustained_knm, long_term)
    transient_k = _curvature(total_knm - sustained_knm, initial)
    curvature = sustained_k + transient_k
    x = (sustained_k * long_term["x_mm"] + transient_k * initial["x_mm"]) / curvature
    steel_strain = curvature * (d - x)
    initial_stress = _ES_NMM2 * _curvature(total_knm, initial) * (d - initial["x_mm"])
    stress_limit = 0.8 * section.fy_nmm2
    trace = {
        "crack_limit_mm": limit,
        "initial_elastic_steel_stress_nmm2": initial_stress,
        "assessment_elastic_steel_stress_nmm2": steel_strain * _ES_NMM2,
        "assessment_elastic_steel_strain": steel_strain,
        "annex_f_strain_limit": stress_limit / _ES_NMM2,
    }
    if (
        max(initial_stress, trace["assessment_elastic_steel_stress_nmm2"])
        > stress_limit
    ):
        return {
            **trace,
            "status": "HOLD",
            "method": "annex_f_strain_limit_exceeded",
            "width_mm": None,
        }

    centres = sorted(bar.x_from_left_mm for bar in section.main_bars)
    points = (
        0.0,
        float(section.strip_width_mm),
        *((left + right) / 2 for left, right in pairwise(centres)),
    )
    point = max(points, key=lambda x_mm: min(abs(x_mm - centre) for centre in centres))
    radius = section.main_bars[0].diameter_mm / 2
    acr = min(math.hypot(point - centre, depth - d) - radius for centre in centres)
    cover = depth - d - radius
    surface_strain = curvature * (depth - x)
    width = check_crack_width(
        exposure_class="mild",
        limit_mm=limit,
        acr_mm=acr,
        cmin_mm=cover,
        h_mm=depth,
        x_mm=x,
        epsilon_m=surface_strain,
    )
    return {
        **trace,
        "status": "PASS" if width.is_ok else "FAIL",
        "method": "annex_f_one_way_flexure",
        "width_mm": width.computed["wcr_mm"],
        "governing_strip_position_mm": point,
        "surface_strain": surface_strain,
        "neutral_axis_mm": x,
        "nearest_steel_mm": acr,
        "main_bar_cover_mm": cover,
    }


def _calculate(request: SlabDirectServiceInputV1) -> dict[str, Any]:
    section = request.section
    history, loads = request.history, request.service_loads
    assert history is not None and loads is not None
    span = request.effective_span_mm
    width, depth = section.strip_width_mm, section.thickness_mm
    d = section.main_bars[0].y_from_top_mm
    area = math.fsum(math.pi * bar.diameter_mm**2 / 4 for bar in section.main_bars)
    fck = section.fck_nmm2
    ec = 5_000 * math.sqrt(fck)
    mcr = calculate_cracking_moment(b_mm=width, D_mm=depth, fck_nmm2=fck)
    total, sustained = loads.total, loads.sustained
    m_total, m_g = total.midspan_moment_knm, sustained.midspan_moment_knm

    def state(modulus: float, moment: float) -> dict[str, float]:
        return _sls_section(width, depth, d, area, modulus, _ES_NMM2, mcr, moment)

    def deflection(moment: float, stiffness: dict[str, float]) -> float:
        return _elastic_deflection(
            moment,
            span,
            stiffness["ec_nmm2"],
            stiffness["ieff_mm4"],
            SupportCondition.SIMPLY_SUPPORTED,
        )

    def stage(age: SlabServiceAgeV1) -> tuple[dict[str, float], dict[str, Any]]:
        stiffness = state(ec / (1 + age.creep_coefficient), m_g)
        shrinkage = calculate_shrinkage_curvature(
            eps_cs=age.shrinkage_strain,
            b_mm=width,
            d_mm=d,
            ast_mm2=area,
            D_mm=depth,
        )
        return stiffness, {
            **_section_state(stiffness, m_g > mcr),
            "sustained_deflection_mm": deflection(m_g, stiffness),
            "shrinkage_curvature_per_mm": shrinkage,
            "shrinkage_deflection_mm": calculate_shrinkage_deflection(
                phi_sh=shrinkage, span_mm=span
            ),
        }

    initial, initial_g = state(ec, m_total), state(ec, m_g)
    cracked = m_total > mcr
    immediate_total = deflection(m_total, initial)
    immediate_sustained = deflection(m_g, initial_g)
    actions = {
        "assessment_moment_knm": m_total,
        "sustained_moment_knm": m_g,
        "assessment_support_shear_kn": total.support_shear_kn,
        "sustained_support_shear_kn": sustained.support_shear_kn,
    }
    section_result = {
        "gross_inertia_mm4": initial["igross_mm4"],
        "cracking_moment_knm": mcr,
        "main_steel_area_mm2": area,
        "cracked_at_assessment": cracked,
        "effective_depth_mm": d,
        "main_bar_bottom_cover_mm": depth - d - section.main_bars[0].diameter_mm / 2,
    }
    final_limit, finishes_limit = span / 250, min(span / 350, 20)
    check: dict[str, Any] = {
        "limit_final_mm": final_limit,
        "limit_after_finishes_mm": finishes_limit,
        "midspan_mm": span / 2,
    }

    if m_g > mcr:
        x_mm = initial_g["x_mm"]
        sustained_section_modulus_mm3 = 0.5 * width * x_mm * (d - x_mm / 3)
    else:
        sustained_section_modulus_mm3 = initial_g["igross_mm4"] / (depth / 2)
    initial_sustained_concrete_stress = m_g * 1e6 / sustained_section_modulus_mm3
    creep_stress_limit = fck / 3
    # The fck/3 boundary is inclusive. Cover only binary64 rounding in
    # the supplied actions and section calculation.
    creep_stress_tolerance = 8 * math.ulp(creep_stress_limit)
    if initial_sustained_concrete_stress > creep_stress_limit + creep_stress_tolerance:
        check.update(
            status="HOLD",
            method="creep_stress_domain_exceeded",
            initial_total_mm=immediate_total,
            initial_sustained_mm=immediate_sustained,
            final_deflection_mm=None,
            initial_sustained_concrete_stress_nmm2=initial_sustained_concrete_stress,
            creep_stress_limit_nmm2=creep_stress_limit,
            creep_stress_margin_nmm2=(
                creep_stress_limit - initial_sustained_concrete_stress
            ),
        )
        return {
            "actions": {
                **actions,
                "total_action_row_id": total.action_row_id,
                "sustained_action_row_id": sustained.action_row_id,
                "analysis_revision": request.analysis_revision,
                "reinforcement_revision": request.reinforcement_revision,
            },
            "section": section_result,
            "deflection": check,
            "crack": {
                "status": "HOLD",
                "method": "creep_stress_domain_exceeded",
                "width_mm": None,
                "crack_limit_mm": request.crack_width_limit_mm,
            },
        }

    _, at_finishes = stage(history.finishes)
    long_term, at_assessment = stage(history.assessment)
    crack = _crack(request, m_total, m_g, initial, long_term, cracked)
    if (
        cracked
        and max(
            crack["initial_elastic_steel_stress_nmm2"],
            crack["assessment_elastic_steel_stress_nmm2"],
        )
        >= section.fy_nmm2
    ):
        check.update(
            status="HOLD", method="outside_elastic_profile", final_deflection_mm=None
        )
        witness = request.elastic_witness_load_kn_per_m2
        if (
            witness is not None
            and sustained.uniform_area_load_kn_per_m2
            < witness
            < total.uniform_area_load_kn_per_m2
        ):
            moment, shear = _actions(span, witness)
            trial = state(ec, moment)
            stress = _ES_NMM2 * _curvature(moment, trial) * (d - trial["x_mm"])
            displacement = deflection(moment, trial)
            if mcr < moment and stress < section.fy_nmm2 and displacement > final_limit:
                check.update(
                    status="FAIL",
                    method="elastic_lower_load_exceeds_final_limit",
                    elastic_witness={
                        "load_kn_per_m2": witness,
                        "midspan_moment_knm": moment,
                        "support_shear_kn": shear,
                        "tension_steel_stress_nmm2": stress,
                        "instantaneous_deflection_mm": displacement,
                        "effective_inertia_mm4": trial["ieff_mm4"],
                    },
                )
    else:
        initial_delta, initial_sustained = immediate_total, immediate_sustained
        finishes_total = (
            at_finishes["sustained_deflection_mm"]
            + at_finishes["shrinkage_deflection_mm"]
        )
        # The transient increment uses the change from the initial
        # sustained-load response to the initial full-load response.
        final_total = (
            at_assessment["sustained_deflection_mm"]
            + at_assessment["shrinkage_deflection_mm"]
            + initial_delta
            - initial_sustained
        )
        increment = final_total - finishes_total
        check.update(
            status=(
                "PASS"
                if final_total <= final_limit and increment <= finishes_limit
                else "FAIL"
            ),
            method="annex_c_2_3_4",
            initial_total_mm=initial_delta,
            initial_sustained_mm=initial_sustained,
            at_finishes={**at_finishes, "total_deflection_mm": finishes_total},
            at_assessment={**at_assessment, "total_deflection_mm": final_total},
            after_finishes_mm=increment,
        )
    return {
        "actions": actions,
        "section": section_result,
        "deflection": check,
        "crack": crack,
    }


def check_direct_service(
    request: SlabDirectServiceInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Check finite-age deflection and flexural crack width for a one-way strip.

    Parameters
    ----------
    request : SlabDirectServiceInputV1
        Validated positioned cage, support edges, UDL rows and age history.

    Returns
    -------
    CanonicalFamilyResultV1
        Bound input, independent deflection and crack dispositions, and
        calculated values where the supported models apply.

    Raises
    ------
    InputContractError
        The input is not a validated direct slab service request.

    Limitations
    -----------
    Elastic gravity flexure, one bottom main layer, free axial shortening,
    mild exposure and two simple support lines. Decisions on strength,
    anchorage, fire cover and project tolerances require separate checks.

    Examples
    --------
    See the frozen B01 request and controls in the direct slab service cookbook.

    Provenance
    ----------
    IS 456 Annex C-2 through C-4, Annex F and the Clause 23.2 limits.
    """
    require_request_type(request, SlabDirectServiceInputV1)
    evidence = _evidence_issue(request)
    if evidence is not None:
        return _result(
            request, {}, EngineeringStatus.HOLD, (evidence,), evaluated=False
        )
    section = _section_issue(request.section)
    if section is not None:
        failed = section.code == "SLAB.SERVICE_LAYOUT_FAIL"
        return _result(
            request,
            {},
            EngineeringStatus.FAIL if failed else EngineeringStatus.HOLD,
            (section,),
            evaluated=failed,
        )
    try:
        calculation = _calculate(request)
    except ValueError as error:
        issue = StructuralIssueV1(
            "SLAB.SERVICE_DOMAIN_HELD", "section/history", str(error)
        )
        return _result(request, {}, EngineeringStatus.HOLD, (issue,), evaluated=False)

    dispositions = {
        "deflection": calculation["deflection"]["status"],
        "crack": calculation["crack"]["status"],
    }
    issues = tuple(
        StructuralIssueV1(
            f"SLAB.SERVICE_{name.upper()}_{status}", name, calculation[name]["method"]
        )
        for name, status in dispositions.items()
        if status != "PASS"
    )
    status = next(
        (
            state
            for state in (EngineeringStatus.FAIL, EngineeringStatus.HOLD)
            if state.value in dispositions.values()
        ),
        EngineeringStatus.PASS,
    )
    return _result(request, calculation, status, issues)
