# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Optimization algorithms for structural design."""

from __future__ import annotations

import time
from dataclasses import dataclass

from structural_lib import flexure
from structural_lib.costing import CostBreakdown, CostProfile, calculate_beam_cost
from structural_lib.data_types import FlexureResult


@dataclass
class OptimizationCandidate:
    """A candidate beam design with cost."""

    b_mm: int
    D_mm: int
    d_mm: int
    fck_nmm2: int
    fy_nmm2: int
    design_result: FlexureResult | None
    cost_breakdown: CostBreakdown | None
    is_valid: bool
    failure_reason: str | None = None


@dataclass
class CostOptimizationResult:
    """Result of cost optimization."""

    # Best design
    optimal_candidate: OptimizationCandidate

    # Comparison with conservative baseline
    baseline_cost: float
    savings_amount: float
    savings_percent: float

    # Alternatives (top 3 designs)
    alternatives: list[OptimizationCandidate]

    # Metadata
    candidates_evaluated: int
    candidates_valid: int
    computation_time_sec: float


def optimize_beam_cost(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    cover_mm: int = 40,
) -> CostOptimizationResult:
    """Find cheapest beam design meeting IS 456:2000.

    Uses brute force with intelligent pruning.

    Args:
        span_mm: Beam span (mm)
        mu_knm: Factored bending moment (kNm)
        vu_kn: Factored shear force (kN)
        cost_profile: Regional cost data (defaults to India CPWD 2023)
        cover_mm: Concrete cover (default 40mm)

    Returns:
        CostOptimizationResult with optimal design and alternatives

    Example:
        >>> profile = CostProfile()  # India rates
        >>> result = optimize_beam_cost(5000, 120, 80, profile)
        >>> print(f"Optimal design costs ₹{result.optimal_candidate.cost_breakdown.total_cost}")
        >>> print(f"Savings: {result.savings_percent:.1f}%")
    """
    start_time = time.time()

    if cost_profile is None:
        cost_profile = CostProfile()

    candidates: list[OptimizationCandidate] = []

    # Smart search ranges
    # NOTE: Limited search space for v1.0 (most common grades/steel)
    # Future enhancement: Add M20, M35, Fe415 for comprehensive optimization
    # Current: ~30-50 combinations, Full spec: ~300-500 combinations
    width_options = [230, 300, 400]  # Standard widths (mm)
    depth_min = max(300, int(span_mm / 20))  # span/20 minimum
    depth_max = min(900, int(span_mm / 8))  # span/8 maximum
    depth_options = range(depth_min, depth_max + 1, 50)
    grade_options = [25, 30]  # Most common (M20, M35 reserved for v2.0)
    steel_options = [500]  # Modern standard (Fe415 reserved for v2.0)

    evaluated = 0
    valid = 0

    # Brute force search
    for b in width_options:
        for D in depth_options:
            d = D - cover_mm

            # Quick feasibility check
            if not _quick_feasibility(b, d, mu_knm, span_mm):
                continue

            for fck in grade_options:
                for fy in steel_options:
                    evaluated += 1

                    # Design beam
                    try:
                        design = flexure.design_singly_reinforced(
                            b=b, d=d, d_total=D, mu_knm=mu_knm, fck=fck, fy=fy
                        )
                    except Exception as e:
                        candidates.append(
                            OptimizationCandidate(
                                b_mm=b,
                                D_mm=D,
                                d_mm=d,
                                fck_nmm2=fck,
                                fy_nmm2=fy,
                                design_result=None,
                                cost_breakdown=None,
                                is_valid=False,
                                failure_reason=f"Design failed: {str(e)}",
                            )
                        )
                        continue

                    # Check compliance
                    is_compliant, violations = _check_compliance(design, b, d, fck, fy)
                    if not is_compliant:
                        candidates.append(
                            OptimizationCandidate(
                                b_mm=b,
                                D_mm=D,
                                d_mm=d,
                                fck_nmm2=fck,
                                fy_nmm2=fy,
                                design_result=design,
                                cost_breakdown=None,
                                is_valid=False,
                                failure_reason=f"Compliance violations: {violations}",
                            )
                        )
                        continue

                    # Calculate cost
                    steel_pct = 100 * design.ast_required / (b * d)
                    cost = calculate_beam_cost(
                        b_mm=b,
                        D_mm=D,
                        span_mm=span_mm,
                        ast_mm2=design.ast_required,
                        fck_nmm2=fck,
                        steel_percentage=steel_pct,
                        cost_profile=cost_profile,
                    )

                    valid += 1
                    candidates.append(
                        OptimizationCandidate(
                            b_mm=b,
                            D_mm=D,
                            d_mm=d,
                            fck_nmm2=fck,
                            fy_nmm2=fy,
                            design_result=design,
                            cost_breakdown=cost,
                            is_valid=True,
                        )
                    )

    # Sort by cost (ascending)
    valid_candidates = [c for c in candidates if c.is_valid]
    if not valid_candidates:
        raise ValueError("No valid designs found. Check inputs or loosen constraints.")

    valid_candidates.sort(
        key=lambda c: c.cost_breakdown.total_cost if c.cost_breakdown else float("inf")
    )

    # Best design
    optimal = valid_candidates[0]

    # Calculate baseline (conservative design: span/12 depth)
    # Try M25 first, upgrade to M30 if needed, increase depth if still failing
    baseline_D = int(span_mm / 12)
    baseline_d = baseline_D - cover_mm
    baseline_fck = 25
    baseline_design = flexure.design_singly_reinforced(
        b=300, d=baseline_d, d_total=baseline_D, mu_knm=mu_knm, fck=baseline_fck, fy=500
    )

    # If baseline fails with M25, try M30
    if not baseline_design.is_safe or baseline_design.ast_required == 0:
        baseline_fck = 30
        baseline_design = flexure.design_singly_reinforced(
            b=300,
            d=baseline_d,
            d_total=baseline_D,
            mu_knm=mu_knm,
            fck=baseline_fck,
            fy=500,
        )

        # If still fails, increase depth until it works (span/10)
        if not baseline_design.is_safe or baseline_design.ast_required == 0:
            baseline_D = int(span_mm / 10)  # More conservative
            baseline_d = baseline_D - cover_mm
            baseline_design = flexure.design_singly_reinforced(
                b=300,
                d=baseline_d,
                d_total=baseline_D,
                mu_knm=mu_knm,
                fck=baseline_fck,
                fy=500,
            )

    # Verify baseline is actually valid before using it
    if not baseline_design.is_safe or baseline_design.ast_required == 0:
        # Baseline itself is infeasible - use optimal cost as baseline (no savings)
        baseline_cost_breakdown = optimal.cost_breakdown
    else:
        baseline_pct = 100 * baseline_design.ast_required / (300 * baseline_d)
        baseline_cost_breakdown = calculate_beam_cost(
            b_mm=300,
            D_mm=baseline_D,
            span_mm=span_mm,
            ast_mm2=baseline_design.ast_required,
            fck_nmm2=baseline_fck,
            steel_percentage=baseline_pct,
            cost_profile=cost_profile,
        )

    # Calculate savings
    if baseline_cost_breakdown and optimal.cost_breakdown:
        savings = baseline_cost_breakdown.total_cost - optimal.cost_breakdown.total_cost
        savings_pct = 100 * savings / baseline_cost_breakdown.total_cost
        baseline_cost = baseline_cost_breakdown.total_cost
    else:
        savings = 0.0
        savings_pct = 0.0
        baseline_cost = 0.0

    # Top 3 alternatives
    alternatives = valid_candidates[1:4]  # Skip optimal (index 0), get next 3

    computation_time = time.time() - start_time

    return CostOptimizationResult(
        optimal_candidate=optimal,
        baseline_cost=baseline_cost,
        savings_amount=round(savings, 2),
        savings_percent=round(savings_pct, 2),
        alternatives=alternatives,
        candidates_evaluated=evaluated,
        candidates_valid=valid,
        computation_time_sec=round(computation_time, 3),
    )


def _quick_feasibility(b: float, d: float, mu_knm: float, span_mm: float) -> bool:
    """Quick check if dimensions are feasible before full design."""
    # Check if Mu_lim > Mu for HIGHEST grade we're testing (M30)
    # If it fails for M30, it will fail for all grades (IS 456:2000)
    mu_lim = flexure.calculate_mu_lim(b, d, 30, 500)  # Use M30 (highest grade)
    if mu_lim < mu_knm:
        return False  # Would need doubly reinforced even with M30

    # Check practical span/depth ratio (8 to 20)
    span_d_ratio = span_mm / d
    if span_d_ratio < 8 or span_d_ratio > 20:
        return False

    return True


def _check_compliance(
    design: FlexureResult, b: float, d: float, fck: int, fy: int
) -> tuple[bool, list[str]]:
    """Check if design meets IS 456 requirements."""
    violations = []

    # Check if design was successful
    if design.ast_required <= 0 and design.mu_lim > 0:
        violations.append("Design failed to provide steel area")
        return False, violations

    # Check minimum steel
    pt = 100 * design.ast_required / (b * d)
    pt_min = 100 * 0.85 / fy  # IS 456 Cl 26.5.1.1
    if pt < pt_min:
        violations.append(f"pt ({pt:.3f}%) < pt_min ({pt_min:.3f}%)")

    # Check maximum steel
    pt_max = 4.0  # IS 456 Cl 26.5.1.1
    if pt > pt_max:
        violations.append(f"pt ({pt:.3f}%) > pt_max ({pt_max:.3f}%)")

    return (len(violations) == 0, violations)


# =============================================================================
# Beam Line Optimization
# =============================================================================


@dataclass
class BeamLineInput:
    """Input data for a single beam in beam line optimization."""

    beam_id: str
    b_mm: float
    D_mm: float
    mu_knm: float
    vu_kn: float = 50.0


@dataclass
class BeamConfig:
    """Optimized rebar configuration for a single beam."""

    beam_id: str
    bottom_layer1_dia: int
    bottom_layer1_count: int
    bottom_layer2_dia: int = 0
    bottom_layer2_count: int = 0
    ast_provided_mm2: float = 0.0
    ast_required_mm2: float = 0.0

    def to_dict(self) -> dict:
        """Return JSON-serializable dict."""
        return {
            "beam_id": self.beam_id,
            "bottom_layer1_dia": self.bottom_layer1_dia,
            "bottom_layer1_count": self.bottom_layer1_count,
            "bottom_layer2_dia": self.bottom_layer2_dia,
            "bottom_layer2_count": self.bottom_layer2_count,
            "ast_provided_mm2": round(self.ast_provided_mm2, 1),
            "ast_required_mm2": round(self.ast_required_mm2, 1),
        }


@dataclass
class BeamLineOptimizationResult:
    """Result of beam line optimization for construction consistency.

    Beam line optimization ensures adjacent beams use the same bar sizes
    where possible, improving construction efficiency and reducing errors.
    """

    beam_configs: list[BeamConfig]
    unified_bar_dia: int
    total_steel_kg: float
    beams_processed: int
    beams_skipped: int

    def to_dict(self) -> dict:
        """Return JSON-serializable dict for REST API."""
        return {
            "beam_configs": [c.to_dict() for c in self.beam_configs],
            "unified_bar_dia": self.unified_bar_dia,
            "total_steel_kg": round(self.total_steel_kg, 2),
            "beams_processed": self.beams_processed,
            "beams_skipped": self.beams_skipped,
        }


def optimize_beam_line(
    beams: list[BeamLineInput] | list[dict],
    *,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
    stirrup_dia_mm: float = 8.0,
    unify_diameters: bool = True,
) -> BeamLineOptimizationResult:
    """Optimize multiple beams in a line for construction consistency.

    This function ensures all beams in a continuous line use the same
    bar diameter where possible, improving construction efficiency.

    The algorithm:
    1. Calculate individual optimal configs for each beam
    2. Find the maximum bar diameter needed across all beams
    3. Recalculate bar counts at the unified diameter

    Args:
        beams: List of BeamLineInput objects or dicts with keys:
               beam_id, b_mm, D_mm, mu_knm, vu_kn
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)
        cover_mm: Cover to reinforcement (mm)
        stirrup_dia_mm: Stirrup diameter (mm)
        unify_diameters: If True, use same bar diameter across all beams

    Returns:
        BeamLineOptimizationResult with unified configurations

    Example:
        >>> beams = [
        ...     {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 80, "vu_kn": 50},
        ...     {"beam_id": "B2", "b_mm": 300, "D_mm": 450, "mu_knm": 120, "vu_kn": 60},
        ...     {"beam_id": "B3", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 55},
        ... ]
        >>> result = optimize_beam_line(beams)
        >>> print(f"Unified diameter: {result.unified_bar_dia}mm")
        >>> for cfg in result.beam_configs:
        ...     print(f"{cfg.beam_id}: {cfg.bottom_layer1_count}-{cfg.bottom_layer1_dia}φ")

    References:
        - SP 34:1987, Section on construction practicality
        - IS 456:2000, Cl 26.5.1.1 (Spacing requirements)
    """
    import math

    if not beams:
        return BeamLineOptimizationResult(
            beam_configs=[],
            unified_bar_dia=0,
            total_steel_kg=0.0,
            beams_processed=0,
            beams_skipped=0,
        )

    # Normalize input to BeamLineInput
    beam_inputs: list[BeamLineInput] = []
    for b in beams:
        if isinstance(b, BeamLineInput):
            beam_inputs.append(b)
        elif isinstance(b, dict):
            beam_inputs.append(
                BeamLineInput(
                    beam_id=str(b.get("beam_id", "UNKNOWN")),
                    b_mm=float(b.get("b_mm", 300)),
                    D_mm=float(b.get("D_mm", 450)),
                    mu_knm=float(b.get("mu_knm", 100)),
                    vu_kn=float(b.get("vu_kn", 50)),
                )
            )

    # Standard bar diameters
    BAR_DIAMETERS = [12, 16, 20, 25, 32]
    BAR_AREAS = {d: math.pi * (d / 2) ** 2 for d in BAR_DIAMETERS}

    # Step 1: Calculate required steel area for each beam
    beam_requirements: list[tuple[BeamLineInput, float, int]] = []
    for beam in beam_inputs:
        d_eff = beam.D_mm - cover_mm - stirrup_dia_mm - 8  # Assume 16mm bar initially

        if d_eff <= 0 or fy <= 0:
            continue

        # Required steel area (approximate)
        ast_req = beam.mu_knm * 1e6 / (0.87 * fy * 0.9 * d_eff)
        ast_min = 0.85 * beam.b_mm * d_eff / fy
        ast_target = max(ast_req * 1.1, ast_min)

        # Find minimum bar diameter that works
        best_dia = 16
        for dia in BAR_DIAMETERS:
            area = BAR_AREAS[dia]
            count = math.ceil(ast_target / area)
            if 2 <= count <= 8:
                best_dia = dia
                break

        beam_requirements.append((beam, ast_target, best_dia))

    if not beam_requirements:
        return BeamLineOptimizationResult(
            beam_configs=[],
            unified_bar_dia=0,
            total_steel_kg=0.0,
            beams_processed=0,
            beams_skipped=len(beam_inputs),
        )

    # Step 2: Find maximum bar diameter if unifying
    if unify_diameters:
        max_dia = max(req[2] for req in beam_requirements)
    else:
        max_dia = 16  # Default

    # Step 3: Calculate bar counts at unified diameter
    configs: list[BeamConfig] = []
    total_steel_mm3 = 0.0
    skipped = 0

    for beam, ast_target, _ in beam_requirements:
        d_eff = beam.D_mm - cover_mm - stirrup_dia_mm - max_dia / 2

        if d_eff <= 0:
            skipped += 1
            continue

        # Recalculate with correct effective depth
        ast_req = beam.mu_knm * 1e6 / (0.87 * fy * 0.9 * d_eff)
        ast_min = 0.85 * beam.b_mm * d_eff / fy
        ast_target = max(ast_req * 1.1, ast_min)

        # Calculate bar count at unified diameter
        area_per_bar = BAR_AREAS[max_dia]
        count = max(2, math.ceil(ast_target / area_per_bar))

        # Check if fits in single layer
        clear_cover = cover_mm + stirrup_dia_mm
        available = beam.b_mm - 2 * clear_cover - max_dia
        min_spacing = max(max_dia, 25)
        max_bars_single = int(available / (max_dia + min_spacing)) + 1

        if count <= max_bars_single and count <= 6:
            # Single layer
            ast_provided = count * area_per_bar
            configs.append(
                BeamConfig(
                    beam_id=beam.beam_id,
                    bottom_layer1_dia=max_dia,
                    bottom_layer1_count=count,
                    bottom_layer2_dia=0,
                    bottom_layer2_count=0,
                    ast_provided_mm2=ast_provided,
                    ast_required_mm2=ast_target,
                )
            )
        else:
            # Need 2 layers
            layer1 = min(count // 2 + count % 2, 6)
            layer2 = count - layer1
            ast_provided = (layer1 + layer2) * area_per_bar
            configs.append(
                BeamConfig(
                    beam_id=beam.beam_id,
                    bottom_layer1_dia=max_dia,
                    bottom_layer1_count=layer1,
                    bottom_layer2_dia=max_dia if layer2 > 0 else 0,
                    bottom_layer2_count=max(0, layer2),
                    ast_provided_mm2=ast_provided,
                    ast_required_mm2=ast_target,
                )
            )

        # Estimate steel weight (assuming 1m length for simplicity)
        # Real weight needs span which we don't have here
        total_steel_mm3 += configs[-1].ast_provided_mm2 * 1000  # per meter

    # Convert to kg (steel density 7850 kg/m³)
    total_steel_kg = total_steel_mm3 * 7850 / 1e9

    return BeamLineOptimizationResult(
        beam_configs=configs,
        unified_bar_dia=max_dia,
        total_steel_kg=total_steel_kg,
        beams_processed=len(configs),
        beams_skipped=skipped + (len(beam_inputs) - len(beam_requirements)),
    )
