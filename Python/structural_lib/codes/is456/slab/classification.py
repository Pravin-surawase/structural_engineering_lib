# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Solid rectangular slab classification without design calculations."""

from __future__ import annotations

from structural_lib.codes.is456.slab.models import (
    SlabClassification,
    SlabClassificationResult,
    SlabContractError,
    SlabScopeStatus,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.traceability import clause

__all__ = ["classify_solid_rectangular_slab"]


_SOURCE_REFS: tuple[str, ...] = (
    "IS 456:2000 (consolidated through Amd. 5), Cl. 24.1",
    "IS 456:2000 (consolidated through Amd. 5), Cl. 24.3",
)


@clause("24.1", "24.3")
def classify_solid_rectangular_slab(
    geometry: SolidRectangularSlabGeometry,
) -> SlabClassificationResult:
    """Classify a supported solid rectangular slab from effective spans.

    The supplied effective spans are normalized to ``Lx`` (short) and ``Ly``
    (long).  A ratio ``Ly/Lx`` greater than 2 is one-way; a ratio less than or
    equal to 2 is two-way.  This function deliberately does not infer a
    support condition or produce a design path, coefficients, loads, moments,
    or reinforcement.

    Args:
        geometry: Positive finite, caller-supplied effective spans and slab
            thickness in mm.  An optional strip width in mm is retained for a
            later supported design slice but does not affect classification.

    Returns:
        A typed classification result with ratio, assumptions, source IDs, and
        P6 scope status.

    Raises:
        SlabContractError: If ``geometry`` is not the supported geometry type.
    """
    if not isinstance(geometry, SolidRectangularSlabGeometry):
        raise SlabContractError(
            "geometry must be a SolidRectangularSlabGeometry with effective spans in mm"
        )

    short_span_mm = geometry.short_effective_span_mm
    long_span_mm = geometry.long_effective_span_mm
    span_ratio_ly_lx = long_span_mm / short_span_mm
    classification = (
        SlabClassification.ONE_WAY
        if span_ratio_ly_lx > 2.0
        else SlabClassification.TWO_WAY
    )

    ordering_assumption = (
        "Input effective spans were normalized to Lx (short) and Ly (long)."
        if geometry.span_order_was_normalized
        else "Input effective spans already map to Lx (short) and Ly (long)."
    )
    return SlabClassificationResult(
        geometry=geometry,
        classification=classification,
        span_ratio_ly_lx=span_ratio_ly_lx,
        scope_status=SlabScopeStatus.SUPPORTED,
        assumptions=(
            ordering_assumption,
            "Effective spans are supplied by the caller in mm; their derivation is outside this contract.",
            "No support condition, restraint, load case, or design path is inferred.",
        ),
        source_refs=_SOURCE_REFS,
    )
