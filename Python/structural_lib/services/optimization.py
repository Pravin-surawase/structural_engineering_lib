# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Transport-neutral cost optimization for rectangular RC beams."""

from __future__ import annotations

import math
import time
from collections.abc import Iterable
from dataclasses import dataclass, field

from structural_lib.codes.is456.beam import flexure, shear
from structural_lib.core.data_types import FlexureResult, ShearResult
from structural_lib.services.costing import (
    CostBreakdown,
    CostProfile,
    calculate_beam_cost,
    calculate_steel_weight,
)


class OptimizationInfeasibleError(ValueError):
    """Raised when no candidate satisfies the explicit engineering basis."""


@dataclass(frozen=True)
class OptimizationConstraints:
    """Explicit rectangular-section search grid and efficiency threshold."""

    min_width_mm: int
    max_width_mm: int
    min_depth_mm: int
    max_depth_mm: int
    width_step_mm: int
    depth_step_mm: int
    min_flexural_utilization: float

    def validate(self) -> None:
        """Raise ``ValueError`` when the candidate grid is not well formed."""
        integer_values = {
            "min_width_mm": self.min_width_mm,
            "max_width_mm": self.max_width_mm,
            "min_depth_mm": self.min_depth_mm,
            "max_depth_mm": self.max_depth_mm,
            "width_step_mm": self.width_step_mm,
            "depth_step_mm": self.depth_step_mm,
        }
        for name, value in integer_values.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.min_width_mm > self.max_width_mm:
            raise ValueError("min_width_mm must not exceed max_width_mm")
        if self.min_depth_mm > self.max_depth_mm:
            raise ValueError("min_depth_mm must not exceed max_depth_mm")
        if not math.isfinite(self.min_flexural_utilization) or not (
            0.0 <= self.min_flexural_utilization <= 1.0
        ):
            raise ValueError("min_flexural_utilization must be between 0 and 1")


@dataclass
class OptimizationCandidate:
    """A candidate beam design with real flexure, shear, quantity, and cost data."""

    b_mm: int
    D_mm: int
    d_mm: float
    fck_nmm2: int
    fy_nmm2: int
    design_result: FlexureResult | None
    shear_result: ShearResult | None
    cost_breakdown: CostBreakdown | None
    steel_weight_kg: float
    flexural_utilization: float
    shear_utilization: float
    stirrup_utilization: float
    is_valid: bool
    failure_reason: str | None = None
    effective_depth_deduction_mm: float = 0.0
    shear_reinforcement_area_mm2: float = 0.0
    code_edition: str = "IS 456:2000"
    clause_refs: dict[str, str] = field(default_factory=dict)
    quantity_basis: str = (
        "Required longitudinal tension and compression reinforcement over the "
        "supplied span; stirrup mass excluded."
    )


@dataclass
class CostOptimizationResult:
    """Result of cost optimization."""

    optimal_candidate: OptimizationCandidate
    baseline_cost: float
    savings_amount: float
    savings_percent: float
    alternatives: list[OptimizationCandidate]
    candidates_evaluated: int
    candidates_valid: int
    computation_time_sec: float


def optimize_beam_cost(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    cover_mm: float = 40,
    *,
    fck_options: tuple[int, ...] = (25, 30),
    fy_options: tuple[int, ...] = (500,),
    constraints: OptimizationConstraints | None = None,
    asv_mm2: float = 100.53,
    max_alternatives: int = 3,
) -> CostOptimizationResult:
    """Find the lowest-cost singly reinforced section meeting the supplied basis.

    ``cover_mm`` is retained as the compatibility name for the total effective-
    depth deduction ``D - d``. Product transports must calculate and pass that
    deduction explicitly from their clear-cover and bar-size inputs.

    The cost and steel quantity cover required longitudinal reinforcement only.
    The supplied ``asv_mm2`` is used by the maintained IS 456 shear design to
    establish safety and stirrup spacing, but stirrup mass is not included in
    the cost because bar perimeter and anchorage geometry are not inputs here.
    """
    start_time = time.perf_counter()
    profile = cost_profile or CostProfile()
    _validate_optimizer_inputs(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        effective_depth_deduction_mm=cover_mm,
        asv_mm2=asv_mm2,
        fck_options=fck_options,
        fy_options=fy_options,
        max_alternatives=max_alternatives,
        cost_profile=profile,
    )

    if constraints is None:
        width_options = [230, 300, 400]
        depth_min = max(300, int(span_mm / 20))
        depth_max = min(900, int(span_mm / 8))
        depth_options = list(range(depth_min, depth_max + 1, 50))
        minimum_utilization = 0.0
    else:
        constraints.validate()
        width_options = _inclusive_grid(
            constraints.min_width_mm,
            constraints.max_width_mm,
            constraints.width_step_mm,
        )
        depth_options = _inclusive_grid(
            constraints.min_depth_mm,
            constraints.max_depth_mm,
            constraints.depth_step_mm,
        )
        minimum_utilization = constraints.min_flexural_utilization

    candidates: list[OptimizationCandidate] = []
    for b_mm in width_options:
        for D_mm in depth_options:
            d_mm = D_mm - cover_mm
            for fck_nmm2 in fck_options:
                for fy_nmm2 in fy_options:
                    candidates.append(
                        _evaluate_candidate(
                            b_mm=b_mm,
                            D_mm=D_mm,
                            d_mm=d_mm,
                            span_mm=span_mm,
                            mu_knm=mu_knm,
                            vu_kn=vu_kn,
                            fck_nmm2=fck_nmm2,
                            fy_nmm2=fy_nmm2,
                            asv_mm2=asv_mm2,
                            minimum_utilization=minimum_utilization,
                            cost_profile=profile,
                        )
                    )

    valid_candidates = [candidate for candidate in candidates if candidate.is_valid]
    if not valid_candidates:
        raise OptimizationInfeasibleError(
            "No valid designs found for the supplied materials, shear demand, "
            "effective-depth deduction, and search constraints."
        )

    valid_candidates.sort(key=_candidate_cost)
    optimal = valid_candidates[0]
    baseline = _select_conventional_baseline(valid_candidates, span_mm)
    optimal_cost = _candidate_cost(optimal)
    baseline_cost = _candidate_cost(baseline)
    savings = max(0.0, baseline_cost - optimal_cost)
    savings_percent = 100.0 * savings / baseline_cost if baseline_cost > 0 else 0.0

    return CostOptimizationResult(
        optimal_candidate=optimal,
        baseline_cost=baseline_cost,
        savings_amount=round(savings, 2),
        savings_percent=round(savings_percent, 2),
        alternatives=valid_candidates[1 : max_alternatives + 1],
        candidates_evaluated=len(candidates),
        candidates_valid=len(valid_candidates),
        computation_time_sec=round(time.perf_counter() - start_time, 3),
    )


def _evaluate_candidate(
    *,
    b_mm: int,
    D_mm: int,
    d_mm: float,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck_nmm2: int,
    fy_nmm2: int,
    asv_mm2: float,
    minimum_utilization: float,
    cost_profile: CostProfile,
) -> OptimizationCandidate:
    """Evaluate one exact candidate without transport-specific assumptions."""
    if d_mm <= 0:
        return _failed_candidate(
            b_mm,
            D_mm,
            d_mm,
            fck_nmm2,
            fy_nmm2,
            "Effective depth must be positive after the supplied deduction.",
        )

    design = flexure.design_singly_reinforced(
        b=b_mm,
        d=d_mm,
        d_total=D_mm,
        mu_knm=mu_knm,
        fck=fck_nmm2,
        fy=fy_nmm2,
    )
    flexural_utilization = (
        abs(mu_knm) / design.Mu_lim if design.Mu_lim > 0 else float("inf")
    )
    if not design.is_safe or design.Ast_required <= 0:
        return _failed_candidate(
            b_mm,
            D_mm,
            d_mm,
            fck_nmm2,
            fy_nmm2,
            _result_failure("Flexure design failed", design.errors),
            design_result=design,
            flexural_utilization=flexural_utilization,
        )
    if flexural_utilization < minimum_utilization:
        return _failed_candidate(
            b_mm,
            D_mm,
            d_mm,
            fck_nmm2,
            fy_nmm2,
            (
                f"Flexural utilization {flexural_utilization:.4f} is below "
                f"the requested minimum {minimum_utilization:.4f}."
            ),
            design_result=design,
            flexural_utilization=flexural_utilization,
        )

    shear_design = shear.design_shear(
        vu_kn=vu_kn,
        b=b_mm,
        d=d_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        asv=asv_mm2,
        pt=design.pt_provided,
    )
    shear_utilization = (
        shear_design.tau_v / shear_design.tau_c_max
        if shear_design.tau_c_max > 0
        else float("inf")
    )
    if not shear_design.is_safe:
        return _failed_candidate(
            b_mm,
            D_mm,
            d_mm,
            fck_nmm2,
            fy_nmm2,
            _result_failure("Shear design failed", shear_design.errors),
            design_result=design,
            shear_result=shear_design,
            flexural_utilization=flexural_utilization,
            shear_utilization=shear_utilization,
        )

    provided_stirrup_capacity_kn = (
        0.87 * fy_nmm2 * asv_mm2 * d_mm / (shear_design.spacing * 1000.0)
        if shear_design.spacing > 0
        else 0.0
    )
    stirrup_utilization = (
        shear_design.Vus / provided_stirrup_capacity_kn
        if shear_design.Vus > 0 and provided_stirrup_capacity_kn > 0
        else 0.0
    )
    if stirrup_utilization > 1.0 + 1e-9:
        return _failed_candidate(
            b_mm,
            D_mm,
            d_mm,
            fck_nmm2,
            fy_nmm2,
            (
                "The supplied shear-reinforcement area cannot provide the "
                "required Vus at the maintained minimum practical spacing."
            ),
            design_result=design,
            shear_result=shear_design,
            flexural_utilization=flexural_utilization,
            shear_utilization=shear_utilization,
            stirrup_utilization=stirrup_utilization,
        )

    longitudinal_steel_area_mm2 = design.Ast_required + design.Asc_required
    steel_weight_kg = calculate_steel_weight(longitudinal_steel_area_mm2, span_mm)
    cost = calculate_beam_cost(
        b_mm=b_mm,
        D_mm=D_mm,
        span_mm=span_mm,
        ast_mm2=longitudinal_steel_area_mm2,
        fck_nmm2=fck_nmm2,
        steel_percentage=design.pt_provided,
        cost_profile=cost_profile,
    )
    return OptimizationCandidate(
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        design_result=design,
        shear_result=shear_design,
        cost_breakdown=cost,
        steel_weight_kg=steel_weight_kg,
        flexural_utilization=flexural_utilization,
        shear_utilization=shear_utilization,
        stirrup_utilization=stirrup_utilization,
        is_valid=True,
        effective_depth_deduction_mm=D_mm - d_mm,
        shear_reinforcement_area_mm2=asv_mm2,
        clause_refs={
            **{
                f"flexure.{name}": reference
                for name, reference in design.clause_refs.items()
            },
            **{
                f"shear.{name}": reference
                for name, reference in shear_design.clause_refs.items()
            },
        },
    )


def _failed_candidate(
    b_mm: int,
    D_mm: int,
    d_mm: float,
    fck_nmm2: int,
    fy_nmm2: int,
    reason: str,
    *,
    design_result: FlexureResult | None = None,
    shear_result: ShearResult | None = None,
    flexural_utilization: float = 0.0,
    shear_utilization: float = 0.0,
    stirrup_utilization: float = 0.0,
) -> OptimizationCandidate:
    return OptimizationCandidate(
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        design_result=design_result,
        shear_result=shear_result,
        cost_breakdown=None,
        steel_weight_kg=0.0,
        flexural_utilization=flexural_utilization,
        shear_utilization=shear_utilization,
        stirrup_utilization=stirrup_utilization,
        is_valid=False,
        failure_reason=reason,
    )


def _validate_optimizer_inputs(
    *,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    effective_depth_deduction_mm: float,
    asv_mm2: float,
    fck_options: tuple[int, ...],
    fy_options: tuple[int, ...],
    max_alternatives: int,
    cost_profile: CostProfile,
) -> None:
    numeric_inputs = {
        "span_mm": span_mm,
        "mu_knm": mu_knm,
        "vu_kn": vu_kn,
        "effective_depth_deduction_mm": effective_depth_deduction_mm,
        "asv_mm2": asv_mm2,
    }
    for name, value in numeric_inputs.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite real number")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite real number")
    if span_mm <= 0:
        raise ValueError("span_mm must be positive")
    if mu_knm < 0 or vu_kn < 0:
        raise ValueError("mu_knm and vu_kn must be non-negative factored actions")
    if effective_depth_deduction_mm <= 0:
        raise ValueError("effective_depth_deduction_mm must be positive")
    if asv_mm2 <= 0:
        raise ValueError("asv_mm2 must be positive")
    if not fck_options or any(
        isinstance(value, bool) or not isinstance(value, int) or not 15 <= value <= 40
        for value in fck_options
    ):
        raise ValueError("fck_options must contain integer grades from 15 to 40")
    if not fy_options or any(
        isinstance(value, bool) or not isinstance(value, int) or not 250 <= value <= 550
        for value in fy_options
    ):
        raise ValueError("fy_options must contain integer grades from 250 to 550")
    missing_rates = sorted(set(fck_options) - set(cost_profile.concrete_costs))
    if missing_rates:
        raise ValueError(
            "cost_profile is missing concrete rates for grades: "
            + ", ".join(str(grade) for grade in missing_rates)
        )
    if (
        isinstance(max_alternatives, bool)
        or not isinstance(max_alternatives, int)
        or max_alternatives < 0
    ):
        raise ValueError("max_alternatives must be a non-negative integer")


def _inclusive_grid(minimum: int, maximum: int, step: int) -> list[int]:
    """Return the explicit stepped grid; ``maximum`` remains an upper bound."""
    return list(range(minimum, maximum + 1, step))


def _candidate_cost(candidate: OptimizationCandidate) -> float:
    if candidate.cost_breakdown is None:
        return float("inf")
    return candidate.cost_breakdown.total_cost


def _select_conventional_baseline(
    valid_candidates: list[OptimizationCandidate], span_mm: float
) -> OptimizationCandidate:
    """Pick the valid candidate nearest the conventional 300 mm, span/12 basis."""
    target_depth_mm = span_mm / 12.0
    return min(
        valid_candidates,
        key=lambda candidate: (
            abs(candidate.b_mm - 300),
            abs(candidate.D_mm - target_depth_mm),
            _candidate_cost(candidate),
        ),
    )


def _result_failure(prefix: str, errors: Iterable[object]) -> str:
    messages = [getattr(error, "message", str(error)) for error in errors]
    return f"{prefix}: {'; '.join(messages)}" if messages else prefix
