# SPDX-License-Identifier: MIT
"""Bind generated reinforcement geometry to the depths used for strength."""

from __future__ import annotations

import math
from typing import Any, Literal

from structural_lib.codes.is456.beam.detailing import BeamDetailingResult
from structural_lib.core.errors import InputContractError, InputIssueV1


def _require_matching_design_inputs(
    params: dict[str, Any], inputs: dict[str, Any]
) -> None:
    """Keep serialized geometry and materials tied to the consumed design basis."""
    issues = []
    for name, source in (
        ("b", "b_mm"),
        ("D", "D_mm"),
        ("d", "d_mm"),
        ("fck", "fck_nmm2"),
        ("fy", "fy_nmm2"),
    ):
        expected = inputs.get(source)
        if (
            not isinstance(expected, (int, float))
            or isinstance(expected, bool)
            or not math.isfinite(expected)
            or not math.isclose(params[name], expected, rel_tol=1e-9, abs_tol=1e-6)
        ):
            issues.append(
                InputIssueV1(
                    code="DETAILING_DESIGN_BASIS_MISMATCH",
                    path=f"design_inputs.{source}",
                    message=f"Detailing {source} must match the original strength input.",
                    received=params[name],
                    suggestion="Use the original geometry/materials or rerun strength design for the revised member.",
                )
            )
    if issues:
        raise InputContractError(issues)


def _serialized_detailing_basis(
    beam: dict[str, Any], params: dict[str, Any]
) -> tuple[dict[str, Any], float] | None:
    """Admit a design-derived schedule, or identify a standalone steel-only input.

    A steel-only drafting request has no source design outcome. Once design
    evidence is present, missing basis or rejected checks cannot become defaults.
    """
    if not any(
        key in beam for key in ("design_inputs", "shear", "is_ok", "result_envelope")
    ):
        return None

    envelope = beam.get("result_envelope") or {}
    shear = beam.get("shear") or {}
    if (
        beam.get("is_ok") is not True
        or shear.get("is_safe") is not True
        or beam.get("flexure", {}).get("is_safe") is not True
        or envelope.get("engineering_status") != "PASS"
    ):
        raise InputContractError(
            (
                InputIssueV1(
                    code="CONSUMER_RESULT_NOT_ACCEPTED",
                    path="beam.is_ok",
                    message="Generated detailing requires a passing source design.",
                    suggestion="Resolve the failed design checks before generating a schedule; reports remain available for diagnosis.",
                ),
            )
        )

    inputs = beam.get("design_inputs")
    if not isinstance(inputs, dict) or not inputs:
        raise InputContractError(
            (
                InputIssueV1(
                    code="DETAILING_DESIGN_BASIS_MISSING",
                    path="design_inputs",
                    message="The original strength inputs are required for generated detailing.",
                    suggestion="Regenerate legacy design results with the current design API or CLI.",
                ),
            )
        )
    _require_matching_design_inputs(params, inputs)
    deflection = inputs.get("deflection_params") or {}
    bar_dependent_serviceability = inputs.get("crack_width_params") is not None or any(
        deflection.get(name) not in (None, 1.0)
        for name in ("mf_tension_steel", "mf_compression_steel", "mf_flanged")
    )
    if inputs.get("tu_knm", 0) != 0 or bar_dependent_serviceability:
        raise InputContractError(
            (
                InputIssueV1(
                    code="DETAILING_DESIGN_SCOPE_UNSUPPORTED",
                    path="design_inputs",
                    message="This serialized drafting route cannot bind torsion, supplied crack strains or reinforcement-dependent serviceability factors to newly generated bars.",
                    suggestion="Use the canonical beam facade within its documented detailing scope.",
                ),
            )
        )
    # The existing unmodified span/depth screen needs geometry, not bar-revision
    # evidence. Preserve that CLI journey only for the same checked span/depth.
    if deflection and any(
        not math.isclose(value, params[target], rel_tol=1e-9, abs_tol=1e-6)
        for value, target in (
            (deflection["span_mm"], "span"),
            (deflection["d_mm"], "d"),
        )
    ):
        raise InputContractError(
            (
                InputIssueV1(
                    code="DETAILING_DESIGN_BASIS_MISMATCH",
                    path="design_inputs.deflection_params",
                    message="Detailing must use the span and depth evaluated by the span/depth screen.",
                    suggestion="Rerun the design with the intended geometry.",
                ),
            )
        )
    spacing = shear.get("spacing", shear.get("sv_required_mm"))
    issues = []
    for path, value in (
        ("design_inputs.asv_mm2", inputs.get("asv_mm2")),
        ("design_inputs.d_dash_mm", inputs.get("d_dash_mm")),
        ("shear.spacing", spacing),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value <= 0
        ):
            issues.append(
                InputIssueV1(
                    code="DETAILING_DESIGN_BASIS_MISSING",
                    path=path,
                    message="A positive finite strength-basis value is required.",
                    received=value,
                    suggestion="Regenerate the complete result with the current design API or CLI.",
                )
            )
    if issues:
        raise InputContractError(issues)
    return inputs, float(spacing)


def _require_generated_detailing_depth(
    detailing: BeamDetailingResult,
    *,
    d_mm: float,
    d_dash_mm: float,
    compression_required_mm2: float,
    primary_tension_face: Literal["TOP", "BOTTOM"] = "BOTTOM",
) -> None:
    """Reject a passing joint result whose generated bars cannot prove its depths.

    The legacy arrangement records a layer count without row positions. Only
    single-layer strength-bearing faces have a recoverable centroid. Nominal
    opposite-face steel does not determine d_dash when no compression is used.
    This check does not change the supplied depths or redesign the member.
    """
    primary = "top_bars" if primary_tension_face == "TOP" else "bottom_bars"
    opposite = "bottom_bars" if primary_tension_face == "TOP" else "top_bars"
    faces = [(primary, "d_mm", d_mm)]
    if compression_required_mm2 > 0:
        faces.append((opposite, "d_dash_mm", d_dash_mm))

    issues: list[InputIssueV1] = []
    for face, depth_name, design_depth in faces:
        for index, (bars, stirrups) in enumerate(
            zip(getattr(detailing, face), detailing.stirrups, strict=True)
        ):
            path = f"detailing.{face}[{index}]"
            if bars.layers != 1:
                issues.append(
                    InputIssueV1(
                        code="DETAILING_EFFECTIVE_DEPTH_UNVERIFIED",
                        path=path,
                        message="Generated multiple-layer bars have no row positions to verify the strength depth.",
                        received=bars.layers,
                        suggestion="Use a compatible single-layer layout or the supplied-reinforcement route with explicit layer positions.",
                    )
                )
                continue
            centroid_cover = detailing.cover + stirrups.diameter + bars.diameter / 2
            physical_depth = (
                detailing.D - centroid_cover if depth_name == "d_mm" else centroid_cover
            )
            if not math.isclose(
                design_depth, physical_depth, rel_tol=1e-9, abs_tol=1e-6
            ):
                issues.append(
                    InputIssueV1(
                        code="DETAILING_EFFECTIVE_DEPTH_MISMATCH",
                        path=f"{path}.{depth_name}",
                        message=f"Strength {depth_name}={design_depth:g} mm does not match the generated bar centroid ({physical_depth:g} mm).",
                        received=design_depth,
                        constraint=f"{depth_name} must equal {physical_depth:g} mm for this generated layout",
                        suggestion="Reconcile the section depth, clear cover, link and longitudinal bar sizes, then rerun design and detailing.",
                    )
                )
    if issues:
        raise InputContractError(issues)


def _require_generated_detailing_shear(
    detailing: BeamDetailingResult,
    *,
    assumed_asv_mm2: float,
    maximum_spacing_mm: float,
) -> None:
    """Bind generated stirrups to the accepted shear-design basis.

    The shear owner has already calculated the permitted spacing from its
    assumed stirrup-leg area. This validator verifies the generated schedule
    uses at least that area and does not widen any generated zone beyond the
    calculated limit. It does not redesign the member or alter the schedule.
    """
    issues: list[InputIssueV1] = []
    for index, stirrup in enumerate(detailing.stirrups):
        path = f"detailing.stirrups[{index}]"
        actual_asv_mm2 = stirrup.legs * math.pi * stirrup.diameter**2 / 4
        if actual_asv_mm2 + 1e-6 < assumed_asv_mm2:
            issues.append(
                InputIssueV1(
                    code="DETAILING_SHEAR_AREA_MISMATCH",
                    path=f"{path}.area_mm2",
                    message=(
                        f"Generated stirrup area={actual_asv_mm2:g} mm² is below "
                        f"the shear-design basis Asv={assumed_asv_mm2:g} mm²."
                    ),
                    received=actual_asv_mm2,
                    constraint=f"area_mm2 must be at least {assumed_asv_mm2:g} mm²",
                    suggestion=(
                        "Rerun strength design with the generated stirrup area or select "
                        "stirrups that provide the assumed Asv."
                    ),
                )
            )
        if stirrup.spacing > maximum_spacing_mm + 1e-6:
            issues.append(
                InputIssueV1(
                    code="DETAILING_SHEAR_SPACING_EXCEEDED",
                    path=f"{path}.spacing_mm",
                    message=(
                        f"Generated stirrup spacing={stirrup.spacing:g} mm exceeds "
                        f"the shear-design limit={maximum_spacing_mm:g} mm."
                    ),
                    received=stirrup.spacing,
                    constraint=(
                        f"spacing_mm must not exceed {maximum_spacing_mm:g} mm"
                    ),
                    suggestion=(
                        "Use spacing at or below the calculated shear limit, then rerun "
                        "design and detailing."
                    ),
                )
            )
    if issues:
        raise InputContractError(issues)
