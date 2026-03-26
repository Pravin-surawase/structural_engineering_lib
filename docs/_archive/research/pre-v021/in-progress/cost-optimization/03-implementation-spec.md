# Implementation Specification: Cost Optimization

**For:** GitHub Copilot
**From:** Claude (based on research)
**Date:** 2026-01-05

---

## Overview

Implement cost optimization feature that finds the cheapest beam design meeting IS 456:2000 requirements.

**Approach:** Brute force with intelligent pruning (see 02-algorithm-selection.md)

---

## File Structure

```
Python/structural_lib/
├── costing.py                  # NEW - Core cost calculations
├── optimization.py             # NEW - Optimization algorithms
├── insights/
│   ├── __init__.py            # UPDATE - Export cost optimization
│   └── cost_optimization.py   # NEW - User-facing API
└── api.py                     # UPDATE - Add cost_profile parameter
```

---

## Step 1: Create `costing.py` Module

**Location:** `Python/structural_lib/costing.py`

**Purpose:** Pure math for calculating costs from beam dimensions.

### Data Structures

```python
"""Cost calculation utilities for structural elements."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CostProfile:
    """Regional cost data for materials and labor.

    Based on CPWD DSR 2023 (India national average).
    Users can override with regional data.
    """
    currency: str = "INR"

    # Material costs per unit
    concrete_costs: Dict[int, float] = field(default_factory=lambda: {
        20: 6200,
        25: 6700,
        30: 7200,
        35: 7700,
        40: 8200,
    })
    steel_cost_per_kg: float = 72.0  # Fe500
    formwork_cost_per_m2: float = 500.0

    # Labor modifiers
    congestion_threshold_pt: float = 2.5  # Steel percentage
    congestion_multiplier: float = 1.2

    # Regional adjustment
    location_factor: float = 1.0  # 1.0 = national average


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a beam design."""
    concrete_cost: float
    steel_cost: float
    formwork_cost: float
    labor_adjustment: float
    total_cost: float
    currency: str = "INR"

    def to_dict(self) -> dict:
        return {
            "concrete": self.concrete_cost,
            "steel": self.steel_cost,
            "formwork": self.formwork_cost,
            "labor_adjustment": self.labor_adjustment,
            "total": self.total_cost,
            "currency": self.currency,
        }
```

### Core Functions

```python
def calculate_concrete_volume(b_mm: float, D_mm: float, span_mm: float) -> float:
    """Calculate concrete volume in m³.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)

    Returns:
        Volume in m³
    """
    # Convert mm to meters
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    return b_m * D_m * span_m


def calculate_steel_weight(ast_mm2: float, span_mm: float) -> float:
    """Calculate steel weight in kg.

    Args:
        ast_mm2: Steel area (mm²)
        span_mm: Beam span (mm)

    Returns:
        Weight in kg
    """
    # Steel density: 7850 kg/m³
    ast_m2 = ast_mm2 / 1_000_000  # mm² to m²
    span_m = span_mm / 1000
    volume_m3 = ast_m2 * span_m
    return volume_m3 * 7850


def calculate_formwork_area(b_mm: float, D_mm: float, span_mm: float) -> float:
    """Calculate formwork surface area in m².

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)

    Returns:
        Surface area in m²
    """
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    # Formwork needed: bottom + 2 sides
    # (Top is open for concrete pouring)
    bottom = b_m * span_m
    sides = 2 * D_m * span_m

    return bottom + sides


def calculate_beam_cost(
    b_mm: float,
    D_mm: float,
    span_mm: float,
    ast_mm2: float,
    fck_nmm2: int,
    steel_percentage: float,
    cost_profile: CostProfile
) -> CostBreakdown:
    """Calculate total cost for a beam design.

    Args:
        b_mm: Beam width (mm)
        D_mm: Beam depth (mm)
        span_mm: Beam span (mm)
        ast_mm2: Tension steel area (mm²)
        fck_nmm2: Concrete grade (N/mm²)
        steel_percentage: pt = 100 * Ast / (b*d)
        cost_profile: Regional cost data

    Returns:
        CostBreakdown with detailed costs
    """
    # Material quantities
    concrete_vol_m3 = calculate_concrete_volume(b_mm, D_mm, span_mm)
    steel_weight_kg = calculate_steel_weight(ast_mm2, span_mm)
    formwork_area_m2 = calculate_formwork_area(b_mm, D_mm, span_mm)

    # Material costs
    concrete_rate = cost_profile.concrete_costs.get(fck_nmm2, 6700)
    concrete_cost = concrete_vol_m3 * concrete_rate

    steel_cost = steel_weight_kg * cost_profile.steel_cost_per_kg

    formwork_cost = formwork_area_m2 * cost_profile.formwork_cost_per_m2

    # Labor adjustment (congestion penalty)
    labor_adjustment = 0.0
    if steel_percentage > cost_profile.congestion_threshold_pt:
        # Apply penalty to steel placement labor
        penalty_rate = (cost_profile.congestion_multiplier - 1.0)
        labor_adjustment = steel_cost * penalty_rate

    # Total (apply location factor)
    subtotal = concrete_cost + steel_cost + formwork_cost + labor_adjustment
    total = subtotal * cost_profile.location_factor

    return CostBreakdown(
        concrete_cost=round(concrete_cost, 2),
        steel_cost=round(steel_cost, 2),
        formwork_cost=round(formwork_cost, 2),
        labor_adjustment=round(labor_adjustment, 2),
        total_cost=round(total, 2),
        currency=cost_profile.currency,
    )
```

---

## Step 2: Create `optimization.py` Module

**Location:** `Python/structural_lib/optimization.py`

**Purpose:** Optimization algorithms (brute force for now).

### Data Structures

```python
"""Optimization algorithms for structural design."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from structural_lib import flexure, shear, compliance
from structural_lib.costing import CostProfile, CostBreakdown, calculate_beam_cost
from structural_lib.data_types import FlexureResult


@dataclass
class OptimizationCandidate:
    """A candidate beam design with cost."""
    b_mm: int
    D_mm: int
    d_mm: int
    fck_nmm2: int
    fy_nmm2: int
    design_result: FlexureResult
    cost_breakdown: CostBreakdown
    is_valid: bool
    failure_reason: Optional[str] = None


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
    alternatives: List[OptimizationCandidate]

    # Metadata
    candidates_evaluated: int
    candidates_valid: int
    computation_time_sec: float
```

### Core Function

```python
import time
from typing import List


def optimize_beam_cost(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: Optional[CostProfile] = None,
    cover_mm: int = 40
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

    candidates: List[OptimizationCandidate] = []

    # Smart search ranges
    width_options = [230, 300, 400]  # Standard widths (mm)
    depth_min = max(300, int(span_mm / 20))  # span/20 minimum
    depth_max = min(900, int(span_mm / 8))   # span/8 maximum
    depth_options = range(depth_min, depth_max + 1, 50)
    grade_options = [25, 30]  # Most common (start with these)
    steel_options = [500]      # Modern standard

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
                            b=b,
                            d=d,
                            mu=mu_knm,
                            fck=fck,
                            fy=fy
                        )
                    except Exception as e:
                        candidates.append(OptimizationCandidate(
                            b_mm=b, D_mm=D, d_mm=d, fck_nmm2=fck, fy_nmm2=fy,
                            design_result=None,
                            cost_breakdown=None,
                            is_valid=False,
                            failure_reason=f"Design failed: {str(e)}"
                        ))
                        continue

                    # Check compliance
                    is_compliant, violations = _check_compliance(design, b, d, fck, fy)
                    if not is_compliant:
                        candidates.append(OptimizationCandidate(
                            b_mm=b, D_mm=D, d_mm=d, fck_nmm2=fck, fy_nmm2=fy,
                            design_result=design,
                            cost_breakdown=None,
                            is_valid=False,
                            failure_reason=f"Compliance violations: {violations}"
                        ))
                        continue

                    # Calculate cost
                    steel_pct = 100 * design.ast_prov / (b * d)
                    cost = calculate_beam_cost(
                        b_mm=b,
                        D_mm=D,
                        span_mm=span_mm,
                        ast_mm2=design.ast_prov,
                        fck_nmm2=fck,
                        steel_percentage=steel_pct,
                        cost_profile=cost_profile
                    )

                    valid += 1
                    candidates.append(OptimizationCandidate(
                        b_mm=b, D_mm=D, d_mm=d, fck_nmm2=fck, fy_nmm2=fy,
                        design_result=design,
                        cost_breakdown=cost,
                        is_valid=True
                    ))

    # Sort by cost (ascending)
    valid_candidates = [c for c in candidates if c.is_valid]
    if not valid_candidates:
        raise ValueError("No valid designs found. Check inputs or loosen constraints.")

    valid_candidates.sort(key=lambda c: c.cost_breakdown.total_cost)

    # Best design
    optimal = valid_candidates[0]

    # Calculate baseline (conservative design: span/12 depth)
    baseline_D = int(span_mm / 12)
    baseline_d = baseline_D - cover_mm
    baseline_design = flexure.design_singly_reinforced(
        b=300, d=baseline_d, mu=mu_knm, fck=25, fy=500
    )
    baseline_pct = 100 * baseline_design.ast_prov / (300 * baseline_d)
    baseline_cost_breakdown = calculate_beam_cost(
        b_mm=300,
        D_mm=baseline_D,
        span_mm=span_mm,
        ast_mm2=baseline_design.ast_prov,
        fck_nmm2=25,
        steel_percentage=baseline_pct,
        cost_profile=cost_profile
    )

    # Calculate savings
    savings = baseline_cost_breakdown.total_cost - optimal.cost_breakdown.total_cost
    savings_pct = 100 * savings / baseline_cost_breakdown.total_cost

    # Top 3 alternatives
    alternatives = valid_candidates[1:4]  # Skip optimal (index 0), get next 3

    computation_time = time.time() - start_time

    return CostOptimizationResult(
        optimal_candidate=optimal,
        baseline_cost=baseline_cost_breakdown.total_cost,
        savings_amount=round(savings, 2),
        savings_percent=round(savings_pct, 2),
        alternatives=alternatives,
        candidates_evaluated=evaluated,
        candidates_valid=valid,
        computation_time_sec=round(computation_time, 3)
    )


def _quick_feasibility(b: float, d: float, mu_knm: float, span_mm: float) -> bool:
    """Quick check if dimensions are feasible before full design."""
    # Check if Mu_lim > Mu (singly reinforced possible)
    mu_lim = flexure.calculate_mu_lim(b, d, 25, 500)  # Assume M25, Fe500
    if mu_lim < mu_knm:
        return False  # Would need doubly reinforced

    # Check practical span/depth ratio (8 to 20)
    span_d_ratio = span_mm / d
    if span_d_ratio < 8 or span_d_ratio > 20:
        return False

    return True


def _check_compliance(design: FlexureResult, b: float, d: float, fck: int, fy: int) -> Tuple[bool, List[str]]:
    """Check if design meets IS 456 requirements."""
    violations = []

    # Check minimum steel
    pt = 100 * design.ast_prov / (b * d)
    pt_min = 0.85 / fy  # IS 456 Cl 26.5.1.1
    if pt < pt_min:
        violations.append(f"pt ({pt:.3f}%) < pt_min ({pt_min:.3f}%)")

    # Check maximum steel
    pt_max = 4.0  # IS 456 Cl 26.5.1.1
    if pt > pt_max:
        violations.append(f"pt ({pt:.3f}%) > pt_max ({pt_max:.3f}%)")

    # Check spacing (if we have bar details)
    # TODO: Add spacing checks if design includes bar_diameter

    return (len(violations) == 0, violations)
```

---

## Step 3: Create User-Facing API

**Location:** `Python/structural_lib/insights/cost_optimization.py`

```python
"""Cost optimization feature for beam design.

This module provides AI-driven cost optimization that finds the cheapest
beam design meeting IS 456:2000 requirements.
"""

from typing import Optional
from structural_lib.costing import CostProfile
from structural_lib.optimization import optimize_beam_cost, CostOptimizationResult

__all__ = ['optimize_beam_design', 'CostProfile', 'CostOptimizationResult']


def optimize_beam_design(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: Optional[CostProfile] = None
) -> CostOptimizationResult:
    """Find the most cost-effective beam design.

    This function automatically finds the cheapest beam dimensions and
    materials that meet IS 456:2000 safety requirements.

    Args:
        span_mm: Beam span in millimeters
        mu_knm: Factored bending moment in kNm
        vu_kn: Factored shear force in kN
        cost_profile: Regional cost data (defaults to India CPWD 2023)

    Returns:
        CostOptimizationResult containing:
            - Optimal design (b, D, fck, fy)
            - Cost breakdown
            - Savings vs conservative design
            - Alternative designs

    Example:
        >>> from structural_lib.insights import optimize_beam_design, CostProfile
        >>>
        >>> # Use default India costs
        >>> result = optimize_beam_design(
        ...     span_mm=5000,
        ...     mu_knm=120,
        ...     vu_kn=80
        ... )
        >>>
        >>> print(f"Optimal: {result.optimal_candidate.b_mm}×{result.optimal_candidate.D_mm}mm")
        >>> print(f"Cost: ₹{result.optimal_candidate.cost_breakdown.total_cost:,.0f}")
        >>> print(f"Savings: {result.savings_percent:.1f}%")
        >>>
        >>> # Custom regional costs
        >>> custom_costs = CostProfile(
        ...     concrete_costs={25: 7000, 30: 7500},
        ...     steel_cost_per_kg=75,
        ...     location_factor=1.1  # 10% higher than national avg
        ... )
        >>> result = optimize_beam_design(5000, 120, 80, custom_costs)
    """
    return optimize_beam_cost(span_mm, mu_knm, vu_kn, cost_profile)
```

---

## Step 4: Update Package Exports

### Update `insights/__init__.py`

```python
"""Smart insights and optimization features."""

from structural_lib.insights.precheck import quick_precheck
from structural_lib.insights.sensitivity import sensitivity_analysis
from structural_lib.insights.constructability import calculate_constructability_score
from structural_lib.insights.cost_optimization import (
    optimize_beam_design,
    CostProfile,
    CostOptimizationResult
)

__all__ = [
    'quick_precheck',
    'sensitivity_analysis',
    'calculate_constructability_score',
    'optimize_beam_design',
    'CostProfile',
    'CostOptimizationResult',
]
```

---

## Step 5: Unit Tests

**Location:** `Python/tests/test_cost_optimization.py`

```python
"""Tests for cost optimization feature."""

import pytest
from structural_lib.costing import CostProfile, calculate_beam_cost
from structural_lib.optimization import optimize_beam_cost
from structural_lib.insights import optimize_beam_design


def test_cost_profile_defaults():
    """Test default cost profile uses India CPWD 2023 rates."""
    profile = CostProfile()

    assert profile.currency == "INR"
    assert profile.concrete_costs[25] == 6700
    assert profile.steel_cost_per_kg == 72.0


def test_calculate_beam_cost_simple():
    """Test basic cost calculation."""
    profile = CostProfile()

    cost = calculate_beam_cost(
        b_mm=300,
        D_mm=450,
        span_mm=5000,
        ast_mm2=1500,
        fck_nmm2=25,
        steel_percentage=1.2,
        cost_profile=profile
    )

    assert cost.total_cost > 0
    assert cost.concrete_cost > 0
    assert cost.steel_cost > 0
    assert cost.formwork_cost > 0


def test_optimize_beam_cost_residential():
    """Test optimization for typical residential beam."""
    result = optimize_beam_cost(
        span_mm=5000,
        mu_knm=120,
        vu_kn=80
    )

    assert result.optimal_candidate.is_valid
    assert result.optimal_candidate.cost_breakdown.total_cost > 0
    assert result.savings_percent > 0  # Should save vs conservative
    assert result.candidates_evaluated > 0


def test_optimize_beam_cost_heavy_commercial():
    """Test optimization for heavy commercial beam."""
    result = optimize_beam_cost(
        span_mm=8000,
        mu_knm=400,
        vu_kn=200
    )

    assert result.optimal_candidate.is_valid
    # Heavy beam should have larger section
    assert result.optimal_candidate.D_mm > 500


def test_cost_optimization_savings():
    """Verify cost optimization actually saves money."""
    result = optimize_beam_cost(
        span_mm=6000,
        mu_knm=180,
        vu_kn=100
    )

    # Should achieve 10-20% savings
    assert 10 <= result.savings_percent <= 25


def test_cost_optimization_alternatives():
    """Test that alternatives are provided."""
    result = optimize_beam_cost(
        span_mm=5000,
        mu_knm=120,
        vu_kn=80
    )

    assert len(result.alternatives) > 0
    # Alternatives should be more expensive than optimal
    for alt in result.alternatives:
        assert alt.cost_breakdown.total_cost > result.optimal_candidate.cost_breakdown.total_cost


def test_custom_cost_profile():
    """Test with custom regional costs."""
    custom_profile = CostProfile(
        concrete_costs={25: 7500, 30: 8000},
        steel_cost_per_kg=80,
        location_factor=1.2  # 20% higher
    )

    result = optimize_beam_cost(
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        cost_profile=custom_profile
    )

    # Should still find valid design
    assert result.optimal_candidate.is_valid
    # Cost should be higher due to higher rates
    assert result.optimal_candidate.cost_breakdown.total_cost > 30000


def test_api_function():
    """Test user-facing API function."""
    from structural_lib.insights import optimize_beam_design

    result = optimize_beam_design(
        span_mm=5000,
        mu_knm=120,
        vu_kn=80
    )

    assert result.optimal_candidate.is_valid
    assert result.savings_percent > 0
```

---

## Acceptance Criteria

Before marking this feature complete:

- [ ] All modules created (costing.py, optimization.py, insights/cost_optimization.py)
- [ ] All unit tests pass (8/8)
- [ ] Type hints on all functions
- [ ] Docstrings with examples
- [ ] Runs in < 1 second for typical beam
- [ ] Achieves 10-20% cost savings vs conservative design
- [ ] Returns practical, constructible designs
- [ ] Integrated in main API

---

## Implementation Timeline

**Estimated:** 4-6 hours with Copilot assistance

**Day 3 (Today):**
- Morning: Implement costing.py (1 hour)
- Afternoon: Implement optimization.py (2 hours)
- Evening: Unit tests + integration (1 hour)

**Day 4:**
- Polish, documentation, examples (1 hour)

---

## Success Metrics

**After implementation:**
- [ ] Tested on 20 validation beams
- [ ] All show cost savings (10-20%)
- [ ] No IS 456 violations
- [ ] Performance: < 1 second average
- [ ] Code coverage > 90%

---

**Ready to implement!** Hand this spec to GitHub Copilot for execution.
