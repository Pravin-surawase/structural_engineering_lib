"""Qualified T-specific screening and actual-bar flexural crack evidence."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.beam.flanged_serviceability import (
    cracked_t_section,
    gross_t_section,
)

from .reinforcement import BarPosition, Face
from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_evaluated_result,
    partial_result,
)
from .serviceability import (
    CrackWidthCheckRequest,
    CrackWidthLimitRequest,
    DeflectionCheckRequest,
    DeflectionMethod,
    DeflectionScreeningBasis,
    SupportCondition,
    check_crack_width,
    check_deflection,
)
from .t_flange import TFlangeParticipationRequest, check_t_flange_participation
from .t_member_basis import _passed, check_t_action_basis

T_SERVICEABILITY_OPERATION = "is456.beam.t_serviceability.check/v1"
T_SERVICEABILITY_REVISION = "is456-t-screen-actual-section-e-v1"


@dataclass(frozen=True)
class TServiceabilityRequest:
    flange: TFlangeParticipationRequest
    concrete_grade_nmm2: float
    steel_yield_strength_nmm2: float
    steel_modulus_nmm2: float
    crack_limit: CrackWidthLimitRequest | None


def check_t_serviceability(request: TServiceabilityRequest) -> OperationResult:
    """Complete source-bounded flanged screen, not Annex-C deflection values.

    The actual-y eligible slab distribution steel is audited, with no beam
    strength credit. The larger of its actual crack result and the web-only
    result governs; loss of the source screening envelope retains HOLD.
    """
    return _check_t_serviceability(request, flange=None)


def _check_t_flange_and_serviceability(
    request: TServiceabilityRequest,
) -> tuple[OperationResult, OperationResult]:
    """Compute both results using the flange evidence from this request."""
    flange = check_t_flange_participation(request.flange)
    return flange, _check_t_serviceability(request, flange=flange)


def _check_t_serviceability(
    request: TServiceabilityRequest, *, flange: OperationResult | None
) -> OperationResult:
    op, inputs = T_SERVICEABILITY_OPERATION, effective_inputs(request=request)
    provenance = Provenance(
        T_SERVICEABILITY_REVISION,
        T_SERVICEABILITY_REVISION,
        (
            "IS456:2000 through Amendment6;23.2.1(a,c,d,e),Figs4-6; complete flanged span/depth screening",
            "Fig4 conservative factor1 for pt<=0.4% and actual service fs<=145MPa; Fig5 no compression enhancement; Fig6 factor0.8 on bw/bf 0..0.3",
            "AnnexF fully cracked actual-T elastic strain, no tension-stiffening reduction; actual eligible parallel slab steel separately audited",
        ),
    )

    def hold(code: str, message: str) -> OperationResult:
        return not_evaluated_result(
            op,
            inputs,
            Diagnostic(
                code,
                "error",
                message,
                op,
                "service_basis",
                "T-serviceability",
                "Supply the same complete current T flange/actions and a source-qualified service method.",
            ),
            provenance=provenance,
        )

    if (
        request.concrete_grade_nmm2 != 25
        or request.steel_yield_strength_nmm2 != 415
        or request.steel_modulus_nmm2 != 200000
    ):
        return hold(
            "T_SLS.MATERIAL_PROFILE",
            "The frozen complete profile is M25/uncoated Fe415 with explicit Es=200000N/mm²; other material profiles need their own qualification.",
        )
    if request.crack_limit is None:
        return hold(
            "T_SLS.CRACK_BASIS",
            "Exposure, harmful-cracking applicability and the selected crack limit are required.",
        )
    if flange is None:
        flange = check_t_flange_participation(request.flange)
    action = check_t_action_basis(request.flange.action_basis)
    if not _passed(flange) or not _passed(action):
        return hold(
            "T_SLS.CURRENT_BASIS",
            "Actual T geometry, slab-strip participation and separate current physical ULS/SLS/permanent actions must qualify first.",
        )
    geometry = request.flange.action_basis.geometry
    section = geometry.section
    if request.crack_limit.profile_id != geometry.profile_id:
        return hold(
            "T_SLS.PROFILE_IDENTITY",
            "The crack criterion belongs to another member profile.",
        )
    bf = float(flange.outputs["effective_flange_width_mm"])
    d = float(action.outputs["effective_depth_mm"])
    ec, es = 5000 * math.sqrt(request.concrete_grade_nmm2), request.steel_modulus_nmm2
    moment = float(action.outputs["service_moment_knm"]) * 1e6
    beam_bars = geometry.bars
    eligible = tuple(
        BarPosition(
            str(bar["bar_id"]),
            float(bar["diameter_mm"]),
            float(bar["x_from_left_mm"]),
            float(bar["y_from_top_mm"]),
            Face(bar["face"]),
            int(bar["layer"]),
        )
        for bar in flange.outputs["eligible_parallel_slab_bars"]
    )
    # Keep both the no-credit design model and the actual-y supplemental
    # model inspectable. Their source/bar identities are in the flange result.
    states = []
    service_stresses: list[float] = []
    web_bars = tuple(
        BarPosition(
            bar.bar_id,
            bar.diameter_mm,
            bar.x_from_left_mm - section.web_left_from_flange_left_mm,
            bar.y_from_top_mm,
            bar.face,
            bar.layer,
        )
        for bar in beam_bars
    )
    bottom = sorted(
        (bar for bar in web_bars if bar.face is Face.BOTTOM),
        key=lambda bar: bar.x_from_left_mm,
    )
    if not bottom:
        return hold(
            "T_SLS.TENSION_BARS", "Actual positioned web tension bars are required."
        )
    surface_points = sorted(
        {
            0.0,
            section.web_width_mm,
            *(bar.x_from_left_mm for bar in bottom),
            *(
                (a.x_from_left_mm + b.x_from_left_mm) / 2
                for a, b in zip(bottom, bottom[1:], strict=False)
            ),
        }
    )
    # For the admitted single-diameter, single-depth row these Voronoi
    # boundaries/endpoints give the complete bottom-soffit crack envelope.
    if (
        len({bar.diameter_mm for bar in bottom}) != 1
        or len({bar.y_from_top_mm for bar in bottom}) != 1
    ):
        return hold(
            "T_SLS.SOFFIT_ENVELOPE",
            "The frozen soffit envelope admits one actual bottom row/diameter; another layout needs a qualified surface envelope.",
        )
    cracks = []
    for label, bars in (
        ("web_only_no_slab_credit", beam_bars),
        ("actual_eligible_parallel_steel", beam_bars + eligible),
    ):
        layers = tuple(
            (bar.y_from_top_mm, math.pi * bar.diameter_mm**2 / 4) for bar in bars
        )
        axis, inertia = cracked_t_section(
            section.web_width_mm,
            bf,
            section.flange_thickness_mm,
            section.depth_mm,
            layers,
            ec,
            es,
        )
        curvature = moment / (ec * inertia)
        stress = es * curvature * (d - axis)
        service_stresses.append(stress)
        surface_strain = curvature * (section.depth_mm - axis)
        state_cracks = tuple(
            check_crack_width(
                CrackWidthCheckRequest(
                    geometry.profile_id,
                    geometry.member_id,
                    "SLS-midspan",
                    str(action.outputs["governing_service_row_id"]),
                    geometry.reinforcement_revision_id,
                    section.web_width_mm,
                    section.depth_mm,
                    axis,
                    Face.BOTTOM,
                    web_bars,
                    x,
                    stress,
                    request.steel_yield_strength_nmm2,
                    es,
                    surface_strain,
                    request.crack_limit,
                )
            )
            for x in surface_points
        )
        if any(
            r.execution != "completed" or "calculated_crack_width_mm" not in r.outputs
            for r in state_cracks
        ):
            return hold(
                "T_SLS.CRACK_DOMAIN",
                "The actual service stress/strain or physical crack criterion is outside the qualified AnnexF owner.",
            )
        worst = max(
            state_cracks, key=lambda r: float(r.outputs["calculated_crack_width_mm"])
        )
        cracks.append(worst)
        states.append(
            {
                "model": label,
                "neutral_axis_mm": axis,
                "cracked_inertia_mm4": inertia,
                "curvature_per_mm": curvature,
                "bottom_steel_stress_nmm2": stress,
                "elastic_bottom_surface_strain": surface_strain,
                "bar_responses": tuple(
                    {
                        "bar_id": bar.bar_id,
                        "strain": curvature * (bar.y_from_top_mm - axis),
                        "steel_stress_nmm2": es
                        * curvature
                        * (bar.y_from_top_mm - axis),
                    }
                    for bar in bars
                ),
                "soffit_surface_points_web_x_mm": surface_points,
                "crack_envelope": worst,
            }
        )
    selected_crack = max(
        cracks, key=lambda r: float(r.outputs["calculated_crack_width_mm"])
    )
    ast = math.fsum(math.pi * bar.diameter_mm**2 / 4 for bar in bottom)
    pt = 100 * ast / (bf * d)
    pc = (
        100
        * math.fsum(
            math.pi * bar.diameter_mm**2 / 4
            for bar in beam_bars
            if bar.face is Face.TOP
        )
        / (bf * d)
    )
    fs = max(service_stresses)
    ratio = section.web_width_mm / bf
    domain = (
        0 < pt <= 0.4
        and 0 <= pc <= 3
        and fs <= 145
        and 0 < ratio <= 0.3 + 1e-12
        and float(action.outputs["code_effective_span_mm"]) <= 10000
    )
    if domain:
        deflection = check_deflection(
            DeflectionCheckRequest(
                geometry.profile_id,
                DeflectionMethod.SPAN_DEPTH_SCREENING,
                screening=DeflectionScreeningBasis(
                    float(action.outputs["code_effective_span_mm"]),
                    d,
                    SupportCondition.SIMPLY_SUPPORTED,
                    1,
                    1,
                    0.8,
                    str(action.outputs["topology_result_id"]),
                    "Controlled IS456 PDF39-40 Figs4-6; normalized conservative envelope, bf_effective*d percentages; actual T fs and explicit no enhancement",
                ),
            )
        )
    else:
        deflection = not_evaluated_result(
            "is456.beam.deflection.check/v1",
            effective_inputs(request=request),
            Diagnostic(
                "T_SLS.SCREENING_DOMAIN",
                "error",
                "Actual pt/fs/bw:bf/span leaves the frozen source envelope; select a newly qualified screen or actual-T AnnexC calculation.",
                "is456.beam.deflection.check/v1",
                "screening",
                "IS45623.2.1",
                "Retain HOLD; do not extrapolate or omit Fig6.",
            ),
            provenance=Provenance(
                "is456-wp04-v1", T_SERVICEABILITY_REVISION, provenance.source_references
            ),
        )
    gross_area, centroid, gross_inertia = gross_t_section(
        section.web_width_mm, bf, section.flange_thickness_mm, section.depth_mm
    )
    outputs = {
        "section_id": section.section_id,
        "geometry_revision_id": section.geometry_revision_id,
        "reinforcement_revision_id": geometry.reinforcement_revision_id,
        "flange_participation_result_id": flange.result_id,
        "action_basis_result_id": action.result_id,
        "physical_flange_width_mm": section.flange_width_physical_mm,
        "effective_flange_width_mm": bf,
        "web_width_mm": section.web_width_mm,
        "effective_service_gross_area_mm2": gross_area,
        "effective_service_gross_centroid_mm": centroid,
        "effective_service_gross_inertia_mm4": gross_inertia,
        "service_moment_knm": moment / 1e6,
        "section_states": states,
        "tension_percentage_on_effective_flange": pt,
        "compression_percentage_on_effective_flange": pc,
        "screening_domain_qualified": domain,
        "screening_factors": {"tension": 1, "compression": 1, "flange": 0.8},
        "screening_reinforcement_model": "Actual beam bars with no slab strength/stiffness credit; eligible parallel slab steel retains its separate actual-y section audit",
        "deflection": deflection,
        "crack": selected_crack,
        "result_kind": "flanged_span_depth_screen_and_T_soffit_crack_envelope",
        "calculated_deflection_mm": None,
        "annex_c_time_components_computed": False,
    }
    if not domain:
        return partial_result(
            op,
            inputs,
            outputs,
            (
                Diagnostic(
                    "T_SLS.SCREENING_DOMAIN",
                    "error",
                    "The required flanged deflection screen has no qualified source factor for these inputs.",
                    op,
                    "screening",
                    "IS45623.2.1",
                    "Retain HOLD and supply another qualified source/method.",
                ),
            ),
            provenance=provenance,
        )
    failed = deflection.engineering == "fail" or selected_crack.engineering == "fail"
    return completed_result(
        op,
        inputs,
        outputs,
        engineering=EngineeringState.FAIL if failed else EngineeringState.PASS,
        diagnostics=deflection.diagnostics + selected_crack.diagnostics,
        provenance=provenance,
    )
