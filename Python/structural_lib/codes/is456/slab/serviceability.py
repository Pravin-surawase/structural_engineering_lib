# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Explicit span/depth serviceability boundary for supported solid slabs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "SlabServiceabilityInput",
    "SlabServiceabilityResult",
    "SlabServiceabilityStatus",
    "check_slab_span_depth_serviceability",
]


class SlabServiceabilityStatus(StrEnum):
    SATISFIED_WITH_REVIEWED_LIMIT = "satisfied_with_reviewed_limit"
    LIMIT_EXCEEDED = "limit_exceeded"


def _positive(value: float, name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise SlabContractError(f"{name} must be finite and positive in {unit}")
    return normalized


@dataclass(frozen=True)
class SlabServiceabilityInput:
    effective_span_mm: float
    effective_depth_mm: float
    reviewed_base_span_depth_limit: float
    reviewed_aggregate_modification_factor: float
    limit_source_reference: str
    limit_source_is_approved: bool
    qualified_acceptance_reference: str
    qualified_acceptance_acknowledged: bool

    def __post_init__(self) -> None:
        for name, unit in (
            ("effective_span_mm", "mm"),
            ("effective_depth_mm", "mm"),
            ("reviewed_base_span_depth_limit", "ratio"),
            ("reviewed_aggregate_modification_factor", "ratio"),
        ):
            object.__setattr__(self, name, _positive(getattr(self, name), name, unit))
        for name in ("limit_source_reference", "qualified_acceptance_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise SlabContractError(f"{name} must be a non-blank string")
            object.__setattr__(self, name, value.strip())
        if self.limit_source_is_approved is not True:
            raise SlabContractError("limit_source_is_approved must be explicitly True")
        if self.qualified_acceptance_acknowledged is not True:
            raise SlabContractError(
                "qualified_acceptance_acknowledged must be explicitly True"
            )


@dataclass(frozen=True)
class SlabServiceabilityResult:
    actual_span_depth_ratio: float
    reviewed_modified_span_depth_limit: float
    utilization: float
    status: SlabServiceabilityStatus
    direct_deflection_status: str
    crack_width_status: str
    source_reference: str
    qualified_acceptance_reference: str
    verified_by_library: bool

    @property
    def is_satisfied(self) -> bool:
        return self.status is SlabServiceabilityStatus.SATISFIED_WITH_REVIEWED_LIMIT


@clause("23.2.1", "24.1")
def check_slab_span_depth_serviceability(
    design_input: SlabServiceabilityInput,
) -> SlabServiceabilityResult:
    """Compare L/d only against explicit reviewed limit carriers."""
    if not isinstance(design_input, SlabServiceabilityInput):
        raise SlabContractError("design_input must be a SlabServiceabilityInput")
    actual = design_input.effective_span_mm / design_input.effective_depth_mm
    limit = (
        design_input.reviewed_base_span_depth_limit
        * design_input.reviewed_aggregate_modification_factor
    )
    status = (
        SlabServiceabilityStatus.SATISFIED_WITH_REVIEWED_LIMIT
        if actual <= limit
        else SlabServiceabilityStatus.LIMIT_EXCEEDED
    )
    return SlabServiceabilityResult(
        actual_span_depth_ratio=actual,
        reviewed_modified_span_depth_limit=limit,
        utilization=actual / limit,
        status=status,
        direct_deflection_status=(
            "held_requires_slab_specific_service_actions_load_duration_"
            "reinforcement_and_effective_inertia_validation"
        ),
        crack_width_status=(
            "held_requires_explicit_bar_geometry_cover_neutral_axis_and_"
            "service_stress_or_strain_validation"
        ),
        source_reference=design_input.limit_source_reference,
        qualified_acceptance_reference=(design_input.qualified_acceptance_reference),
        verified_by_library=False,
    )
