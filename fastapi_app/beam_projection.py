"""One compatibility projection for HTTP and WebSocket beam results.

This module converts units and transports an already calculated result. It
does not select engineering inputs, recompute capacities or grant approval.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from structural_lib.services.api import ComplianceCaseResult
from structural_lib.services.evidence import (
    build_beam_evidence_envelope,
    build_beam_result_envelope,
)
from structural_lib.services.serialization import to_transport_value

from fastapi_app.error_utils import sanitize_error_string
from fastapi_app.models.beam import (
    BeamDesignResponse,
    CombinedBeamActions,
    CrackWidthCheckResult,
    DeflectionCheckResult,
    EffectiveDepthResolutionResponse,
    EvidenceEnvelopeResponse,
    FlexureResult,
    IntegratedTorsionResult,
    ShearResult,
)
from fastapi_app.models.response import StructuralResultEnvelopeResponse


def project_beam_design_result(
    result: ComplianceCaseResult, *, evidence_inputs: Mapping[str, Any]
) -> BeamDesignResponse:
    """Project exact calculation status, depth, provenance and quantities.

    ``evidence_inputs`` comes from the validated transport adapter in explicit
    IS456 units. The legacy capped display ratio remains for old consumers;
    ``governing_utilization`` and its unavailable marker carry the actual value.
    """
    payload = to_transport_value(result)
    depth = float(evidence_inputs["d_mm"])
    width = float(evidence_inputs["b_mm"])
    fy = float(evidence_inputs["fy_nmm2"])
    flexure = result.flexure
    shear = result.shear
    evidence = build_beam_evidence_envelope(
        inputs=dict(evidence_inputs),
        is_ok=result.is_ok,
        governing_utilization=result.governing_utilization,
        utilizations=result.utilizations,
    )
    envelope = (
        result.result_envelope
        or build_beam_result_envelope(is_ok=result.is_ok, evidence=evidence).to_dict()
    )

    shear_output = None
    if (result.Vu_kn > 0 or result.Tu_knm > 0) and shear:
        # Vus is kN; the response is Asv/s in mm²/mm, not a bar area in mm².
        asv_per_spacing = (
            shear.Vus * 1000 / (0.87 * fy * depth) if shear.Vus > 0 else 0.0
        )
        spacing = shear.spacing
        if result.torsion is not None:
            asv_per_spacing = result.torsion.Asv_total
            spacing = result.torsion.stirrup_spacing
        shear_output = ShearResult(
            tau_v=shear.tau_v,
            tau_c=shear.tau_c,
            tau_c_max=shear.tau_c_max,
            asv_required=asv_per_spacing,
            stirrup_spacing=spacing,
            sv_max=300.0,
            shear_capacity=(
                shear.tau_c * width * depth / 1000 + shear.Vus
                if shear.Vus > 0
                else result.Vu_kn
            ),
        )

    warnings = []
    if flexure.Asc_required > 0:
        warnings.append(
            "Doubly reinforced design required because moment demand exceeds "
            "the singly reinforced limit"
        )
    if flexure.xu > flexure.xu_max:
        warnings.append("Section is over-reinforced - consider increasing depth")

    combined = None
    torsion_output = None
    if result.torsion is not None:
        torsion = result.torsion
        combined = CombinedBeamActions(
            mu_knm=result.Mu_knm,
            vu_kn=result.Vu_kn,
            tu_knm=result.Tu_knm,
            me_knm=torsion.Me_knm,
            ve_kn=torsion.Ve_kn,
        )
        torsion_output = IntegratedTorsionResult(
            is_safe=torsion.is_safe,
            tau_ve=torsion.tau_ve,
            tau_c=torsion.tau_c,
            tau_c_max=torsion.tau_c_max,
            asv_torsion=torsion.Asv_torsion,
            asv_shear=torsion.Asv_shear,
            asv_total=torsion.Asv_total,
            stirrup_spacing=torsion.stirrup_spacing,
            al_torsion=torsion.Al_torsion,
            me_opposite_knm=torsion.Me_opposite_knm,
            ast_opposite_mm2=torsion.Ast_opposite_mm2,
            requires_closed_stirrups=torsion.requires_closed_stirrups,
            errors=[error.to_dict() for error in torsion.errors],
            clause_refs=torsion.clause_refs,
        )
        if torsion.requires_closed_stirrups:
            warnings.append("Closed stirrups mandatory for torsion (IS 456 Cl 41.4.3)")
        warnings.extend(
            sanitize_error_string(e.message, "beam design") for e in torsion.errors
        )

    return BeamDesignResponse(
        success=result.is_ok,
        message=(
            f"Design complete: Ast = {flexure.Ast_required:.0f} mm²"
            if result.is_ok
            else f"Design failed: {result.remarks}"
        ),
        flexure=FlexureResult(
            ast_required=flexure.Ast_required,
            ast_min=flexure.Ast_min,
            ast_max=flexure.Ast_max,
            xu=flexure.xu,
            xu_max=flexure.xu_max,
            is_under_reinforced=flexure.xu <= flexure.xu_max,
            moment_capacity=flexure.Mu_lim,
            asc_required=flexure.Asc_required,
        ),
        shear=shear_output,
        ast_total=flexure.Ast_required,
        asc_total=flexure.Asc_required,
        utilization_ratio=min(result.governing_utilization, 2.0),
        governing_utilization=payload["governing_utilization"],
        unavailable_utilizations=payload.get("unavailable_utilizations", {}),
        effective_depth_used=depth,
        effective_depth_basis=EffectiveDepthResolutionResponse.model_validate(
            result.effective_depth_resolution
        ),
        result_envelope=StructuralResultEnvelopeResponse.model_validate(envelope),
        deflection_check=(
            DeflectionCheckResult(
                is_ok=result.deflection.is_ok,
                span_depth_actual=result.deflection.computed.get("ld_ratio"),
                span_depth_allowable=result.deflection.computed.get("allowable_ld"),
                remarks=result.deflection.remarks,
            )
            if result.deflection is not None
            else None
        ),
        crack_width_check=(
            CrackWidthCheckResult(
                is_ok=result.crack_width.is_ok,
                crack_width_mm=result.crack_width.computed.get("wcr_mm"),
                crack_width_limit_mm=result.crack_width.computed.get("limit_mm"),
                remarks=result.crack_width.remarks,
            )
            if result.crack_width is not None
            else None
        ),
        combined_actions=combined,
        torsion=torsion_output,
        holds=[],
        warnings=warnings,
        evidence=(
            EvidenceEnvelopeResponse.model_validate(evidence)
            if evidence is not None
            else None
        ),
    )
