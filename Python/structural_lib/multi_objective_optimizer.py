# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Multi-Objective Optimization Module
====================================

NSGA-II implementation for Pareto-optimal beam designs.

Features:
- Multi-objective optimization (cost vs utilization vs steel weight)
- Pareto front generation
- Pure Python implementation (no external dependencies)
- IS 456:2000 compliant designs only

Example:
    >>> from structural_lib.multi_objective_optimizer import optimize_pareto_front
    >>> result = optimize_pareto_front(
    ...     span_mm=5000, mu_knm=120, vu_kn=80,
    ...     objectives=['cost', 'steel_weight', 'utilization']
    ... )
    >>> print(f"Found {len(result.pareto_front)} Pareto-optimal designs")

Author: AI Agent (Session 24 Part 4)
Version: 1.0.0
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Any

from structural_lib import flexure
from structural_lib.costing import CostProfile, calculate_beam_cost


@dataclass
class ParetoCandidate:
    """A candidate beam design on the Pareto front.

    Attributes:
        b_mm: Beam width (mm)
        D_mm: Beam total depth (mm)
        d_mm: Effective depth (mm)
        fck_nmm2: Concrete grade (N/mm²)
        fy_nmm2: Steel grade (N/mm²)
        ast_required: Required steel area (mm²)
        ast_provided: Provided steel area (mm²)
        bar_config: Bar configuration string (e.g., "4-16mm")
        cost: Total cost (INR)
        steel_weight_kg: Steel weight (kg)
        utilization: Capacity utilization ratio (0.0 to 1.0)
        is_safe: Whether design meets IS 456 requirements
        governing_clauses: IS 456 clauses that govern this design
        rank: Pareto rank (1 = best front)
        crowding_distance: NSGA-II crowding distance
    """

    b_mm: int
    D_mm: int
    d_mm: int
    fck_nmm2: int
    fy_nmm2: int
    ast_required: float
    ast_provided: float
    bar_config: str
    cost: float
    steel_weight_kg: float
    utilization: float
    is_safe: bool
    governing_clauses: list[str] = field(default_factory=list)
    rank: int = 0
    crowding_distance: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for UI consumption."""
        return {
            "b_mm": self.b_mm,
            "D_mm": self.D_mm,
            "d_mm": self.d_mm,
            "fck_nmm2": self.fck_nmm2,
            "fy_nmm2": self.fy_nmm2,
            "ast_required": round(self.ast_required, 1),
            "ast_provided": round(self.ast_provided, 1),
            "bar_config": self.bar_config,
            "cost": round(self.cost, 2),
            "steel_weight_kg": round(self.steel_weight_kg, 2),
            "utilization": round(self.utilization, 3),
            "is_safe": self.is_safe,
            "governing_clauses": self.governing_clauses,
            "rank": self.rank,
            "crowding_distance": round(self.crowding_distance, 4),
        }


@dataclass
class ParetoOptimizationResult:
    """Result of Pareto multi-objective optimization.

    Attributes:
        pareto_front: List of Pareto-optimal designs (rank 1)
        all_candidates: All valid candidates evaluated
        objectives_used: Objectives optimized
        generations: Number of NSGA-II generations run
        computation_time_sec: Time taken
        best_by_cost: Cheapest design
        best_by_utilization: Most efficient design
        best_by_weight: Lightest design
    """

    pareto_front: list[ParetoCandidate]
    all_candidates: list[ParetoCandidate]
    objectives_used: list[str]
    generations: int
    computation_time_sec: float
    best_by_cost: ParetoCandidate | None
    best_by_utilization: ParetoCandidate | None
    best_by_weight: ParetoCandidate | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for UI consumption."""
        return {
            "pareto_front": [c.to_dict() for c in self.pareto_front],
            "pareto_count": len(self.pareto_front),
            "total_candidates": len(self.all_candidates),
            "objectives_used": self.objectives_used,
            "generations": self.generations,
            "computation_time_sec": round(self.computation_time_sec, 3),
            "best_by_cost": self.best_by_cost.to_dict() if self.best_by_cost else None,
            "best_by_utilization": (
                self.best_by_utilization.to_dict() if self.best_by_utilization else None
            ),
            "best_by_weight": (
                self.best_by_weight.to_dict() if self.best_by_weight else None
            ),
        }


# IS 456 clause references for governing decisions
GOVERNING_CLAUSES = {
    "min_steel": {
        "clause": "26.5.1.1(a)",
        "title": "Minimum tension steel",
        "description": "Ast,min = 0.85*b*d/fy",
    },
    "max_steel": {
        "clause": "26.5.1.1(b)",
        "title": "Maximum tension steel",
        "description": "pt_max = 4%",
    },
    "flexure_design": {
        "clause": "38.1",
        "title": "Flexural design",
        "description": "Stress block coefficients",
    },
    "mu_limit": {
        "clause": "G-1.1(c)",
        "title": "Limiting moment capacity",
        "description": "Mu,lim = 0.138*fck*b*d²",
    },
    "shear_design": {
        "clause": "40.1",
        "title": "Shear design",
        "description": "Nominal shear stress τv",
    },
    "cover": {
        "clause": "Table 16",
        "title": "Nominal cover",
        "description": "Based on exposure condition",
    },
}


def _get_bar_configuration(ast_required: float, b_mm: float) -> tuple[str, float]:
    """Get practical bar configuration for required steel area.

    Args:
        ast_required: Required steel area (mm²)
        b_mm: Beam width (mm)

    Returns:
        Tuple of (bar_config string, ast_provided)
    """
    bar_options = [12, 16, 20, 25]
    if b_mm >= 400:
        bar_options.append(32)

    best_config = None
    best_area = float("inf")

    for dia in bar_options:
        area_per_bar = math.pi * (dia**2) / 4
        num_bars = math.ceil(ast_required / area_per_bar)
        if num_bars < 2:
            num_bars = 2
        if num_bars > 8:
            continue  # Skip impractical configurations

        ast_provided = num_bars * area_per_bar
        if ast_provided >= ast_required and ast_provided < best_area:
            best_config = (f"{num_bars}-{dia}mm", ast_provided)
            best_area = ast_provided

    if best_config is None:
        # Fallback to 20mm bars
        dia = 20
        area_per_bar = math.pi * (dia**2) / 4
        num_bars = max(2, math.ceil(ast_required / area_per_bar))
        best_config = (f"{num_bars}-{dia}mm", num_bars * area_per_bar)

    return best_config


def _dominates(a: list[float], b: list[float]) -> bool:
    """Check if solution a dominates solution b (minimization).

    Args:
        a: Objective values for solution a
        b: Objective values for solution b

    Returns:
        True if a dominates b (a <= b in all objectives, a < b in at least one)
    """
    all_less_equal = all(ai <= bi for ai, bi in zip(a, b, strict=True))
    any_less = any(ai < bi for ai, bi in zip(a, b, strict=True))
    return all_less_equal and any_less


def _fast_non_dominated_sort(
    candidates: list[ParetoCandidate],
    objectives: list[str],
) -> list[list[ParetoCandidate]]:
    """NSGA-II fast non-dominated sorting.

    Args:
        candidates: List of candidates to sort
        objectives: List of objective names to minimize

    Returns:
        List of fronts (front 0 = Pareto optimal)
    """
    if not candidates:
        return []

    n = len(candidates)

    # Get objective values for each candidate
    def get_objectives(c: ParetoCandidate) -> list[float]:
        values = []
        for obj in objectives:
            if obj == "cost":
                values.append(c.cost)
            elif obj == "steel_weight":
                values.append(c.steel_weight_kg)
            elif obj == "utilization":
                # For utilization, we want HIGH utilization (close to 1.0)
                # So minimize (1 - utilization)
                values.append(1.0 - c.utilization)
            else:
                values.append(c.cost)  # Default to cost
        return values

    # Domination count and dominated set for each candidate
    domination_count = [0] * n
    dominated_by: list[list[int]] = [[] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            obj_i = get_objectives(candidates[i])
            obj_j = get_objectives(candidates[j])
            if _dominates(obj_i, obj_j):
                dominated_by[i].append(j)
            elif _dominates(obj_j, obj_i):
                domination_count[i] += 1

    # Build fronts
    fronts: list[list[ParetoCandidate]] = []
    current_front_indices = [i for i in range(n) if domination_count[i] == 0]

    while current_front_indices:
        front = [candidates[i] for i in current_front_indices]
        for c in front:
            c.rank = len(fronts) + 1

        fronts.append(front)

        next_front_indices = []
        for i in current_front_indices:
            for j in dominated_by[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front_indices.append(j)

        current_front_indices = next_front_indices

    return fronts


def _crowding_distance(
    front: list[ParetoCandidate],
    objectives: list[str],
) -> None:
    """Calculate and set crowding distances for a front.

    Args:
        front: List of candidates in a single front
        objectives: List of objective names
    """
    if len(front) <= 2:
        for c in front:
            c.crowding_distance = float("inf")
        return

    # Initialize distances
    for c in front:
        c.crowding_distance = 0.0

    def get_obj_value(c: ParetoCandidate, obj: str) -> float:
        if obj == "cost":
            return c.cost
        elif obj == "steel_weight":
            return c.steel_weight_kg
        elif obj == "utilization":
            return 1.0 - c.utilization
        return c.cost

    for obj in objectives:
        # Sort by objective
        sorted_front = sorted(front, key=lambda c: get_obj_value(c, obj))

        # Boundary points get infinite distance
        sorted_front[0].crowding_distance = float("inf")
        sorted_front[-1].crowding_distance = float("inf")

        # Calculate range
        obj_min = get_obj_value(sorted_front[0], obj)
        obj_max = get_obj_value(sorted_front[-1], obj)
        obj_range = obj_max - obj_min if obj_max != obj_min else 1.0

        # Add normalized distance
        for i in range(1, len(sorted_front) - 1):
            if sorted_front[i].crowding_distance != float("inf"):
                dist = (
                    get_obj_value(sorted_front[i + 1], obj)
                    - get_obj_value(sorted_front[i - 1], obj)
                ) / obj_range
                sorted_front[i].crowding_distance += dist


def _get_governing_clauses(
    design: Any,
    b: float,
    d: float,
    fck: int,
    fy: int,
) -> list[str]:
    """Determine which IS 456 clauses govern the design.

    Args:
        design: FlexureResult from flexure design
        b: Beam width (mm)
        d: Effective depth (mm)
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)

    Returns:
        List of governing clause references with descriptions
    """
    clauses: list[str] = []

    if not design:
        return clauses

    ast_required = design.ast_required
    ast_min = 0.85 * b * d / fy

    # Check minimum steel governs
    if ast_required <= ast_min * 1.1:  # Within 10% of minimum
        clause_info = GOVERNING_CLAUSES["min_steel"]
        clauses.append(f"Cl. {clause_info['clause']}: {clause_info['title']}")

    # Check maximum steel limit
    pt = 100 * ast_required / (b * d)
    if pt > 3.5:  # Approaching 4% limit
        clause_info = GOVERNING_CLAUSES["max_steel"]
        clauses.append(f"Cl. {clause_info['clause']}: {clause_info['title']}")

    # Flexure design always applies
    clause_info = GOVERNING_CLAUSES["flexure_design"]
    clauses.append(f"Cl. {clause_info['clause']}: {clause_info['title']}")

    # Check if Mu limit governs (singly vs doubly reinforced)
    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    if hasattr(design, "mu_knm") and design.mu_knm:
        if design.mu_knm > mu_lim * 0.9:  # Close to limit
            clause_info = GOVERNING_CLAUSES["mu_limit"]
            clauses.append(f"Cl. {clause_info['clause']}: {clause_info['title']}")

    return clauses


def optimize_pareto_front(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    objectives: list[str] | None = None,
    cost_profile: CostProfile | None = None,
    cover_mm: int = 40,
    max_candidates: int = 50,
    random_seed: int | None = None,
) -> ParetoOptimizationResult:
    """Find Pareto-optimal beam designs using NSGA-II inspired algorithm.

    Generates a diverse set of designs varying width, depth, and grades,
    then identifies the Pareto front for the specified objectives.

    Args:
        span_mm: Beam span (mm)
        mu_knm: Factored bending moment (kN·m)
        vu_kn: Factored shear force (kN)
        objectives: List of objectives to optimize. Options:
            - 'cost': Total construction cost (minimize)
            - 'steel_weight': Steel weight in kg (minimize)
            - 'utilization': Capacity utilization (maximize, i.e., less over-design)
            Default: ['cost', 'utilization']
        cost_profile: Regional cost data (defaults to India CPWD 2023)
        cover_mm: Concrete cover (default 40mm)
        max_candidates: Maximum number of candidates to generate
        random_seed: Random seed for reproducibility

    Returns:
        ParetoOptimizationResult with Pareto front and analysis

    Example:
        >>> result = optimize_pareto_front(
        ...     span_mm=5000, mu_knm=120, vu_kn=80,
        ...     objectives=['cost', 'steel_weight', 'utilization']
        ... )
        >>> print(f"Found {len(result.pareto_front)} Pareto-optimal designs")
        >>> for design in result.pareto_front[:3]:
        ...     print(f"  {design.bar_config}: ₹{design.cost:,.0f}, "
        ...           f"{design.steel_weight_kg:.1f}kg, {design.utilization:.0%}")
    """
    start_time = time.time()

    if objectives is None:
        objectives = ["cost", "utilization"]

    if cost_profile is None:
        cost_profile = CostProfile()

    if random_seed is not None:
        random.seed(random_seed)

    # Design space
    width_options = [200, 230, 250, 300, 350, 400]
    depth_min = max(300, int(span_mm / 20))
    depth_max = min(900, int(span_mm / 8))
    depth_step = 25
    depth_options = list(range(depth_min, depth_max + 1, depth_step))
    grade_options = [(25, 500), (30, 500), (25, 415), (30, 415)]

    # Steel density for weight calculation
    steel_density = 7850.0  # kg/m³

    candidates: list[ParetoCandidate] = []

    # Generate candidates systematically
    for b in width_options:
        for D in depth_options:
            d = D - cover_mm
            if d <= 100:
                continue

            for fck, fy in grade_options:
                if len(candidates) >= max_candidates:
                    break

                # Quick feasibility check
                mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
                if mu_lim < mu_knm:
                    continue  # Would need doubly reinforced

                # Design beam
                try:
                    design = flexure.design_singly_reinforced(
                        b=b, d=d, d_total=D, mu_knm=mu_knm, fck=fck, fy=fy
                    )
                except Exception:
                    continue

                if not design.is_safe or design.ast_required <= 0:
                    continue

                # Check compliance
                pt = 100 * design.ast_required / (b * d)
                pt_min = 100 * 0.85 / fy
                pt_max = 4.0
                if pt < pt_min or pt > pt_max:
                    continue

                # Get bar configuration
                bar_config, ast_provided = _get_bar_configuration(
                    design.ast_required, b
                )

                # Calculate steel weight (kg)
                steel_vol_m3 = ast_provided * span_mm / 1e9  # mm² * mm / 1e9 = m³
                steel_weight_kg = steel_vol_m3 * steel_density

                # Calculate utilization
                utilization = mu_knm / mu_lim if mu_lim > 0 else 0.0
                utilization = min(utilization, 1.0)

                # Calculate cost
                steel_pct = 100 * design.ast_required / (b * d)
                cost_breakdown = calculate_beam_cost(
                    b_mm=b,
                    D_mm=D,
                    span_mm=span_mm,
                    ast_mm2=design.ast_required,
                    fck_nmm2=fck,
                    steel_percentage=steel_pct,
                    cost_profile=cost_profile,
                )

                # Get governing clauses
                governing = _get_governing_clauses(design, b, d, fck, fy)

                candidate = ParetoCandidate(
                    b_mm=b,
                    D_mm=D,
                    d_mm=d,
                    fck_nmm2=fck,
                    fy_nmm2=fy,
                    ast_required=design.ast_required,
                    ast_provided=ast_provided,
                    bar_config=bar_config,
                    cost=cost_breakdown.total_cost,
                    steel_weight_kg=steel_weight_kg,
                    utilization=utilization,
                    is_safe=True,
                    governing_clauses=governing,
                )

                candidates.append(candidate)

    if not candidates:
        raise ValueError("No valid designs found. Check inputs or loosen constraints.")

    # Non-dominated sorting
    fronts = _fast_non_dominated_sort(candidates, objectives)

    # Calculate crowding distances for each front
    for front in fronts:
        _crowding_distance(front, objectives)

    # Pareto front is the first front
    pareto_front = fronts[0] if fronts else []

    # Sort Pareto front by crowding distance (diverse solutions first)
    pareto_front.sort(key=lambda c: c.crowding_distance, reverse=True)

    # Find best by each objective
    best_by_cost = min(candidates, key=lambda c: c.cost) if candidates else None
    best_by_weight = (
        min(candidates, key=lambda c: c.steel_weight_kg) if candidates else None
    )
    best_by_utilization = (
        max(candidates, key=lambda c: c.utilization) if candidates else None
    )

    computation_time = time.time() - start_time

    return ParetoOptimizationResult(
        pareto_front=pareto_front,
        all_candidates=candidates,
        objectives_used=objectives,
        generations=1,  # Single pass algorithm
        computation_time_sec=computation_time,
        best_by_cost=best_by_cost,
        best_by_utilization=best_by_utilization,
        best_by_weight=best_by_weight,
    )


def get_design_explanation(candidate: ParetoCandidate) -> str:
    """Generate human-readable explanation of why this design was chosen.

    Args:
        candidate: A Pareto candidate design

    Returns:
        Markdown-formatted explanation with IS 456 clause references
    """
    lines = [
        f"## Design: {candidate.b_mm}×{candidate.D_mm}mm beam",
        "",
        f"**Bar Configuration:** {candidate.bar_config}",
        f"**Total Cost:** ₹{candidate.cost:,.0f}",
        f"**Steel Weight:** {candidate.steel_weight_kg:.2f} kg",
        f"**Capacity Utilization:** {candidate.utilization:.1%}",
        "",
        "### Why This Design?",
        "",
    ]

    # Add governing clauses explanations
    if candidate.governing_clauses:
        lines.append("**Governing IS 456 Clauses:**")
        for clause in candidate.governing_clauses:
            lines.append(f"- {clause}")
        lines.append("")

    # Add optimization context
    lines.append("**Design Characteristics:**")

    if candidate.utilization > 0.85:
        lines.append("- ✅ High utilization (>85%) - Efficient use of materials")
    elif candidate.utilization > 0.7:
        lines.append("- ✅ Good utilization (70-85%) - Balanced design")
    else:
        lines.append("- ⚠️ Low utilization (<70%) - Consider smaller section")

    pt = 100 * candidate.ast_provided / (candidate.b_mm * candidate.d_mm)
    if pt < 1.0:
        lines.append(f"- ✅ Low steel ratio ({pt:.2f}%) - Cost effective")
    elif pt < 2.0:
        lines.append(f"- ✅ Moderate steel ratio ({pt:.2f}%) - Typical design")
    else:
        lines.append(f"- ⚠️ High steel ratio ({pt:.2f}%) - Consider larger section")

    return "\n".join(lines)
