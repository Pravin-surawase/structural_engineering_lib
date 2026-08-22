# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Ordinary one-way shear check for beam/wall-supported solid slab strips."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456 import tables
from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "SlabShearInput",
    "SlabShearResult",
    "SlabShearStatus",
    "check_solid_slab_one_way_shear",
    "slab_depth_shear_factor",
]


class SlabShearStatus(StrEnum):
    CONCRETE_CAPACITY_SATISFIED = "concrete_capacity_satisfied"
    INCREASE_DEPTH_OR_ENGINEER_REINFORCEMENT = (
        "increase_depth_or_engineer_reinforcement"
    )
    EXCEEDS_MAXIMUM_SHEAR_STRESS = "exceeds_maximum_shear_stress"


def _positive(value: float, name: str, unit: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{name} must be a real value in {unit}")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise SlabContractError(f"{name} must be finite and positive in {unit}")
    return normalized


def slab_depth_shear_factor(overall_depth_mm: float) -> float:
    """Return the Cl. 40.2.1.1 solid-slab depth factor, linearly interpolated."""
    depth = _positive(overall_depth_mm, "overall_depth_mm", "mm")
    return max(1.0, min(1.3, 1.6 - depth / 500.0))


@dataclass(frozen=True)
class SlabShearInput:
    factored_shear_kn: float
    strip_width_mm: float
    effective_depth_mm: float
    overall_depth_mm: float
    fck_n_per_mm2: float
    tension_reinforcement_mm2: float
    uniformly_distributed_load_only: bool
    beam_or_wall_supported: bool

    def __post_init__(self) -> None:
        for name, unit in (
            ("factored_shear_kn", "kN"),
            ("strip_width_mm", "mm"),
            ("effective_depth_mm", "mm"),
            ("overall_depth_mm", "mm"),
            ("fck_n_per_mm2", "N/mm2"),
            ("tension_reinforcement_mm2", "mm2"),
        ):
            object.__setattr__(self, name, _positive(getattr(self, name), name, unit))
        if self.effective_depth_mm >= self.overall_depth_mm:
            raise SlabContractError(
                "effective_depth_mm must be less than overall_depth_mm"
            )
        if not 15.0 <= self.fck_n_per_mm2 <= 40.0:
            raise SlabContractError(
                "slab shear Table 19/20 lookup supports fck_n_per_mm2 from 15 to 40"
            )
        if self.uniformly_distributed_load_only is not True:
            raise SlabContractError(
                "ordinary slab shear supports uniformly distributed load only"
            )
        if self.beam_or_wall_supported is not True:
            raise SlabContractError(
                "ordinary slab shear supports beam- or wall-supported panels only"
            )


@dataclass(frozen=True)
class SlabShearResult:
    tau_v_n_per_mm2: float
    tension_steel_percentage: float
    base_tau_c_n_per_mm2: float
    slab_depth_factor: float
    design_tau_c_n_per_mm2: float
    tau_c_max_n_per_mm2: float
    status: SlabShearStatus
    punching_shear_disposition: str
    shear_reinforcement_design_status: str
    source_refs: tuple[str, ...]

    @property
    def is_safe_without_shear_reinforcement(self) -> bool:
        return self.status is SlabShearStatus.CONCRETE_CAPACITY_SATISFIED


@clause("40.1", "40.2")
def check_solid_slab_one_way_shear(design_input: SlabShearInput) -> SlabShearResult:
    """Check concrete shear capacity; never auto-design slab stirrups."""
    if not isinstance(design_input, SlabShearInput):
        raise SlabContractError("design_input must be a SlabShearInput")
    tau_v = (
        design_input.factored_shear_kn
        * 1000.0
        / (design_input.strip_width_mm * design_input.effective_depth_mm)
    )
    pt = (
        100.0
        * design_input.tension_reinforcement_mm2
        / (design_input.strip_width_mm * design_input.effective_depth_mm)
    )
    base_tau_c = tables._get_tc_value_for_derived_reinforcement(
        design_input.fck_n_per_mm2, pt
    )
    depth_factor = slab_depth_shear_factor(design_input.overall_depth_mm)
    design_tau_c = base_tau_c * depth_factor
    tau_c_max = tables.get_tc_max_value(design_input.fck_n_per_mm2)
    if tau_v > tau_c_max:
        status = SlabShearStatus.EXCEEDS_MAXIMUM_SHEAR_STRESS
    elif tau_v > design_tau_c:
        status = SlabShearStatus.INCREASE_DEPTH_OR_ENGINEER_REINFORCEMENT
    else:
        status = SlabShearStatus.CONCRETE_CAPACITY_SATISFIED
    return SlabShearResult(
        tau_v_n_per_mm2=tau_v,
        tension_steel_percentage=pt,
        base_tau_c_n_per_mm2=base_tau_c,
        slab_depth_factor=depth_factor,
        design_tau_c_n_per_mm2=design_tau_c,
        tau_c_max_n_per_mm2=tau_c_max,
        status=status,
        punching_shear_disposition=(
            "not_applicable_to_supported_beam_or_wall_supported_udl_panel"
        ),
        shear_reinforcement_design_status="not_automatically_designed",
        source_refs=(
            "IS 456:2000 Cl. 40.1 and 40.2.1.1",
            "IS 456:2000 Table 19 and Table 20",
            "IIT Kharagpur/NPTEL Module 8 Lesson 18 pp. 6 and 15",
        ),
    )
