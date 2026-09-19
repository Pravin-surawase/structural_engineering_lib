# SPDX-License-Identifier: MIT
"""Bind generated reinforcement geometry to the depths used for strength."""

from __future__ import annotations

import math
from typing import Literal

from structural_lib.codes.is456.beam.detailing import BeamDetailingResult
from structural_lib.core.errors import InputContractError, InputIssueV1


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
