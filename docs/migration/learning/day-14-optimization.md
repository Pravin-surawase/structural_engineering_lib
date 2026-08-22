# Day 14: Optimization (Deep Dive)

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Prerequisites:** Days 1-4 (beam design), Day 13 (exports — to understand what we're optimizing)
**Library files:** `Python/structural_lib/services/optimization.py`, `Python/structural_lib/services/multi_objective_optimizer.py`, `Python/structural_lib/services/rebar_optimizer.py`, `Python/structural_lib/services/costing.py`
**IS 456 Clauses:** Cl 26.5.1.1 (min steel), Cl 38.1 (flexure), Annex G (limiting moment)

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why there are many valid designs for the same beam, and how to find the "best" one
- Single-objective cost optimization: brute-force search with IS 456 constraints
- Multi-objective optimization: Pareto frontiers and the NSGA-II algorithm
- Rebar optimization: finding the best bar arrangement for a given $A_{st}$
- How the frontend shows trade-off curves so engineers can pick their preferred design
- **Things to know** — search space size, brute force vs genetic, dominated designs
- **What can be done better** — constraint handling, adaptive grids, machine learning
- **Innovation** — topology optimization, AI-assisted design, real-time optimization
- **Next repo must-add** — cost database, constraint plugins, optimization history

---

## Part 1: Why Optimize?

A beam that needs to carry $M_u = 120$ kNm can be built many ways:

| Design | Width | Depth | Grade | Steel | Cost |
|--------|-------|-------|-------|-------|------|
| A | 230mm | 600mm | M25 | 4×16mm | ₹2,800 |
| B | 300mm | 500mm | M25 | 4×20mm | ₹3,200 |
| C | 300mm | 450mm | M30 | 5×16mm | ₹3,500 |
| D | 400mm | 400mm | M30 | 6×16mm | ₹4,100 |

All four pass IS 456. All are safe. But Design A costs 32% less than D. Over 50 beams, that's lakhs of rupees. The optimizer evaluates **all** combinations in milliseconds.

---

## Part 2: Single-Objective Cost Optimization

### 2.1 The Search Space

```
Width options:   [230, 300, 400] mm              → 3 choices
Depth options:   [300, 350, 400, ..., 900] mm    → ~12 choices
Concrete grades: [25, 30] N/mm²                  → 2 choices
Steel grades:    [500] N/mm²                     → 1 choice
─────────────────────────────────────────
Total:           3 × 12 × 2 × 1 = ~72 combinations
```

### 2.2 The Algorithm

```python
def optimize_beam_cost(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    cover_mm: int = 40,
) -> CostOptimizationResult:
```

For each combination:
1. Check feasibility (depth/width ratio)
2. Design the beam (`flexure.design_singly_reinforced()`)
3. Check IS 456 compliance (min steel, max steel)
4. Calculate cost (concrete + steel + formwork)
5. Rank by total cost

### 2.3 Cost Breakdown

$$C_{total} = C_{concrete} + C_{steel} + C_{formwork}$$

- **Concrete:** volume × rate/m³ (grade-dependent)
- **Steel:** weight × rate/kg (typically 60-70% of total)
- **Formwork:** surface area × rate/m² (wood/plywood)

### 2.4 Result Structure

```python
@dataclass
class CostOptimizationResult:
    optimal_candidate: OptimizationCandidate
    baseline_cost: float              # Conservative design cost
    savings_amount: float             # How much saved (₹)
    savings_percent: float            # e.g. 18.5%
    alternatives: list                # Top 3 designs
    candidates_evaluated: int         # e.g. 72
    candidates_valid: int             # e.g. 45
    computation_time_sec: float       # e.g. 0.03
```

---

## Part 3: Multi-Objective Optimization (Pareto)

Cost isn't everything. Engineers also care about safety margin, steel weight, and utilization. These objectives **conflict** — cheapest ≠ safest.

### 3.1 What Is a Pareto Frontier?

A Pareto-optimal design: you can't improve one objective without worsening another.

```
    Cost (₹)
     ↑
  5000│
     │  ×                      × = dominated (suboptimal)
  4000│     ●                  ● = Pareto optimal
     │         ●     ×
  3000│   ×        ●
     │              ●   ×
  2000│                 ●
     │                     ●
  1000│──────────────────────→ Safety Margin
     0    10%   20%   30%   40%
```

### 3.2 NSGA-II Algorithm

1. Generate random beam designs (initial population)
2. Evaluate objectives (cost, utilization, weight)
3. Non-dominated sorting (rank 1 = Pareto optimal)
4. Crowding distance (prefer spread-out designs)
5. Selection + Crossover + Mutation (breed new designs)
6. Repeat ~50 generations

### 3.3 The Dominance Check

```python
def _dominates(a: list[float], b: list[float]) -> bool:
    """Does solution a dominate b? (all objectives minimized)"""
    all_less_equal = all(ai <= bi for ai, bi in zip(a, b))
    any_less = any(ai < bi for ai, bi in zip(a, b))
    return all_less_equal and any_less
```

---

## Part 4: Rebar Optimization

Even after knowing $A_{st,required} = 1200$ mm², you need actual bars:

| Combination | Area | Bars | Excess | OK? |
|-------------|------|------|--------|-----|
| 4 × 20mm | 1257 mm² | 4 | 4.8% | ✓ |
| 3 × 25mm | 1472 mm² | 3 | 22.7% | ✓ wasteful |
| 6 × 16mm | 1206 mm² | 6 | 0.5% | ✓ tight fit |

```python
result = optimize_bar_arrangement(
    ast_required_mm2=1200,
    b_mm=300, cover_mm=40, stirrup_dia_mm=8,
    objective="min_area",     # or "min_bar_count" or "max_spacing"
)
```

Three objectives available:
- `"min_area"` — least excess steel (cost-efficient)
- `"min_bar_count"` — fewer bars (labor-efficient)
- `"max_spacing"` — easier concrete pouring

---

## Part 5: Pareto in the Frontend

```
    ┌──────────────────────────────────────┐
    │  Cost vs Safety Trade-off            │
    │  ₹5000 │                             │
    │        │  ●                          │
    │  ₹4000 │     ●  ← Click for details  │
    │        │        ●                    │
    │  ₹3000 │           ●                 │
    │        │              ●              │
    │  ₹2000 │─────────────────────        │
    │        0.7  0.8  0.9  1.0            │
    │            Safety Factor             │
    │  Selected: 300×500mm M25, 4×20mm     │
    └──────────────────────────────────────┘
```

Each point is a `ParetoCandidate` with full design details. Click to see dimensions, bars, cost breakdown, governing IS 456 clauses.

---

## Part 6: Library Examples

### Example 1: Cost Optimization

```python
from structural_lib.services.optimization import optimize_beam_cost

result = optimize_beam_cost(span_mm=5000, mu_knm=120, vu_kn=80)

opt = result.optimal_candidate
print(f"Optimal: {opt.b_mm}×{opt.D_mm}mm, M{opt.fck_nmm2}")
print(f"Cost: ₹{opt.cost_breakdown.total_cost:.0f}")
print(f"Savings: {result.savings_percent:.1f}%")
print(f"Evaluated: {result.candidates_evaluated} designs")
```

### Example 2: Pareto Front

```python
from structural_lib.services.multi_objective_optimizer import optimize_pareto_front

result = optimize_pareto_front(
    span_mm=5000, mu_knm=120, vu_kn=80,
    objectives=['cost', 'steel_weight', 'utilization'],
)
print(f"Pareto front: {len(result.pareto_front)} designs")
print(f"Best by cost: ₹{result.best_by_cost.cost:.0f}")
print(f"Best by weight: {result.best_by_weight.steel_weight_kg:.1f} kg")
```

### Example 3: Rebar Arrangement

```python
from structural_lib.services.rebar_optimizer import optimize_bar_arrangement

result = optimize_bar_arrangement(
    ast_required_mm2=1200, b_mm=300, cover_mm=40,
    stirrup_dia_mm=8, objective="min_area",
)
if result.is_feasible:
    arr = result.arrangement
    print(f"Use: {arr.no_of_bars} × ∅{arr.bar_dia_mm}mm")
    print(f"Area: {arr.area_provided_mm2:.0f} mm²")
```

---

## Part 7: Hand-Calculated Cost Comparison

**Problem:** 5m span, $M_u = 120$ kNm.

**Design A (conservative, 300×600mm M25):**
- $A_{st} \approx 626$ mm², use 4×16mm (804 mm²)
- Concrete: 0.3×0.6×5 = 0.9 m³ → ₹5,400
- Steel: 31.6 kg → ₹2,054
- Formwork: 7.5 m² → ₹2,625
- **Total: ₹10,079**

**Design B (optimized, 230×500mm M25):**
- $A_{st} \approx 789$ mm², use 4×16mm (804 mm²)
- Concrete: 0.575 m³ → ₹3,450
- Steel: 31.6 kg → ₹2,054 (same steel!)
- Formwork: 6.15 m² → ₹2,153
- **Total: ₹7,657**

**Savings: ₹2,422 (24%)** — same steel, less concrete and formwork. Found by the optimizer in 0.03 seconds.

---

## Part 8: Exercises

### Exercise 1: Run Cost Optimization

```python
from structural_lib.services.optimization import optimize_beam_cost

result = optimize_beam_cost(span_mm=6000, mu_knm=150, vu_kn=100)
# What's the optimal width/depth? Cost? Savings %?
```

### Exercise 2: Explore Pareto

```python
from structural_lib.services.multi_objective_optimizer import optimize_pareto_front

result = optimize_pareto_front(
    span_mm=6000, mu_knm=150, vu_kn=100,
    objectives=['cost', 'steel_weight'],
)
# How many Pareto-optimal designs? Is cheapest also lightest?
```

### Exercise 3: Compare Rebar Objectives

```python
from structural_lib.services.rebar_optimizer import optimize_bar_arrangement

for obj in ["min_area", "min_bar_count", "max_spacing"]:
    result = optimize_bar_arrangement(
        ast_required_mm2=1500, b_mm=300, cover_mm=40,
        stirrup_dia_mm=8, objective=obj,
    )
    if result.is_feasible:
        arr = result.arrangement
        print(f"{obj}: {arr.no_of_bars}×∅{arr.bar_dia_mm}mm = {arr.area_provided_mm2:.0f} mm²")
```

---

## Part 9: Can You Explain? (Self-Check)

### Q1: Why brute force for cost optimization?

<details><summary>Answer</summary>

72 combinations → evaluates in ~30ms. Brute force guarantees global optimum, is deterministic, gives complete ranking. Gradient descent/simulated annealing have overhead exceeding brute-force time for this search space.
</details>

### Q2: Can Pareto-optimal designs be impractical?

<details><summary>Answer</summary>

Yes. Pareto only considers specified objectives (cost, weight, utilization). It doesn't know about: construction constraints (bars too crowded), architectural requirements (uniform depths), material availability, or standardization needs. The engineer must apply judgment.
</details>

### Q3: min_area vs min_bar_count?

<details><summary>Answer</summary>

For $A_{st} = 1200$ mm²: min_area picks 6×16mm (0.5% excess, cost-efficient), min_bar_count picks 3×25mm (22.7% excess, labor-efficient). Trade-off: steel cost vs labor cost.
</details>

### Q4: How are IS 456 constraints enforced?

<details><summary>Answer</summary>

Every candidate checked against: min steel (Cl 26.5.1.1), max steel ($p_t \leq 4\%$), moment capacity ($M_u \leq M_{u,lim}$), practical depth (span/20 to span/8), standard widths. Violations → `is_valid=False` with `failure_reason`.
</details>

---

## Part 10: Things to Know (Critical Knowledge)

### 10.1 Brute Force Has Limits

```
Current: 3 widths × 12 depths × 2 grades = 72 combinations → instant
Add: 5 bar configurations × 3 stirrup spacings = 72 × 15 = 1,080 → still fast
Add: column interaction checks = 1,080 × N sections → might need NSGA-II

Rule of thumb:
  < 10,000 combinations → brute force
  > 10,000 combinations → genetic algorithm (NSGA-II)
```

### 10.2 Dominated Designs Are Still Useful

```
Pareto says Design X is dominated by Y (Y is cheaper AND safer).
But X might still be useful if:
  - Y requires M30 concrete (unavailable at site)
  - Y has 230mm width (architect wants 300mm)
  - Y uses 32mm bars (not stocked by local supplier)

Keep dominated designs for manual review.
```

### 10.3 Cost Data Is Regional and Time-Sensitive

```python
# CPWD 2023 rates (default in library):
CostProfile(
    concrete_per_m3={25: 6000, 30: 7200, 35: 8500},
    steel_per_kg=65,
    formwork_per_m2=350,
)

# Reality: prices vary by:
#   - City (Mumbai 2× Delhi for labor)
#   - Season (monsoon = expensive formwork)
#   - Quantity (bulk steel discounts)
#   - Year (inflation 8-10% annual)
```

### 10.4 Rebar Spacing Is a Hard Constraint

```
IS 456 Cl 26.3.2 minimum spacing:
  1. Bar diameter (for bottom bars)
  2. Aggregate size + 5mm (typically 25mm)
  3. 25mm (absolute minimum)

For 300mm beam with 40mm cover + 8mm stirrup:
  Available width = 300 - 2×(40+8) = 204mm
  Max bars of 20mm: (204 + 25) / (20 + 25) = 5.09 → 5 bars
  Max bars of 16mm: (204 + 25) / (16 + 25) = 5.59 → 5 bars
```

---

## Part 11: What Can Be Done Better

### 11.1 Current Limitations

| Issue | Current | Better |
|-------|---------|--------|
| **Cost data** | Hardcoded CPWD 2023 | Database with regional/temporal rates |
| **Grid resolution** | Fixed 50mm depth steps | Adaptive grid (finer near optimum) |
| **Constraint handling** | Filter out invalid | Penalty function (soft constraints) |
| **Multi-story** | Single beam at a time | Joint optimization across floors |
| **No learning** | Start fresh every time | Cache results for similar beams |

### 11.2 Missing Adaptive Grid

```
Current: Evaluate at D = 300, 350, 400, 450, ...
Problem: Optimum at D = 478 — closest evaluated are 450 and 500

Better (adaptive):
  Pass 1: D = 300, 400, 500, 600 (coarse)
  Pass 2: D = 410, 430, 450, 470, 490 (refine around minimum)
  Pass 3: D = 475, 477, 479, 481 (fine-tune)

Result: Same accuracy with ~25% fewer evaluations
```

### 11.3 No Sensitivity Analysis

```
How sensitive is the optimal design to cost changes?

Current optimal: 230×500mm M25 at ₹7,657
If steel price increases 20%: optimal shifts to 300×550mm M25 (less steel, more concrete)
If concrete price decreases 10%: optimal shifts to 300×600mm M25 (more concrete, less steel)

This analysis doesn't exist yet — the optimizer gives one answer, not a robust range.
```

---

## Part 12: Innovation Directions

### 12.1 Topology Optimization

```
Current: Choose width × depth × grade
Future:  Optimize the shape itself

Instead of rectangular cross-sections:
  - I-beams, T-beams, tapered beams
  - Non-standard sections that minimize material
  - 3D-printed concrete with optimized internal voids

Libraries: TopOpt (Python), OpenSees (structural analysis)
```

### 12.2 Machine Learning for Warm-Start

```python
# Train an ML model on 100,000 past optimizations:
# Input: span, Mu, Vu, cost_profile
# Output: approximate optimal (b, D, fck)
# Use as warm-start for NSGA-II → converge in 10 generations instead of 50

model = load_optimization_surrogate("beam_v3.onnx")
initial_guess = model.predict(span=5000, mu=120, vu=80)
result = optimize_pareto_front(warm_start=initial_guess, generations=10)
```

### 12.3 Real-Time Optimization

```
Current:  Design → Optimize → Wait → Results
Future:   Slider: drag depth → cost/safety update in real-time

WebSocket stream:
  User moves depth slider: 400mm → 450mm → 500mm
  Server: recalculates cost + safety every 50ms
  Client: Pareto curve updates live
```

### 12.4 Innovation Comparison

| Approach | Benefit | Difficulty | Time to Implement |
|----------|---------|-----------|-------------------|
| Adaptive grid | 25% fewer evaluations | Low | 1 day |
| ML warm-start | 5× faster convergence | Medium | 1 week |
| Real-time slider | Instant feedback UX | Medium | 3 days |
| Topology opt | Material savings 20-40% | High | 1 month |
| Sensitivity analysis | Robust decisions | Low | 2 days |

---

## Part 13: Next Repo Must-Add

### 13.1 Cost Database

```python
# Instead of hardcoded CostProfile:
class CostDatabase:
    def get_rates(self, city: str, year: int, quarter: int) -> CostProfile:
        """Regional, time-indexed cost data."""
        ...

    def get_bulk_discount(self, steel_kg: float) -> float:
        """Volume-based steel discount."""
        if steel_kg > 5000: return 0.05  # 5% discount
        if steel_kg > 1000: return 0.02
        return 0.0
```

### 13.2 Constraint Plugin System

```python
# Let users add custom constraints without modifying optimizer:
class Constraint(ABC):
    def check(self, candidate: BeamDesign) -> tuple[bool, str]:
        """Returns (is_valid, failure_reason)."""
        ...

class ArchitecturalConstraint(Constraint):
    def __init__(self, max_depth_mm: float, min_width_mm: float):
        self.max_depth = max_depth_mm
        self.min_width = min_width_mm

    def check(self, candidate):
        if candidate.D_mm > self.max_depth:
            return False, f"Exceeds max depth {self.max_depth}mm"
        return True, ""
```

### 13.3 Day-1 Checklist for Next Repo Optimization

- [ ] Cost database with regional/temporal rates (not hardcoded)
- [ ] Adaptive grid search (coarse → fine refinement)
- [ ] Constraint plugin system (custom user constraints)
- [ ] Sensitivity analysis (how robust is the optimum?)
- [ ] Optimization history/cache (similar beams → instant results)
- [ ] Multi-beam joint optimization (entire floor at once)
- [ ] ML surrogate model for warm-starting NSGA-II
- [ ] Real-time optimization via WebSocket (slider → live updates)
- [ ] Export optimization report (why this design was chosen)
- [ ] Pareto front persistence (save/load/compare across sessions)

---

## Part 14: Summary

| Concept | What It Does | Library File |
|---------|-------------|-------------|
| **Cost optimization** | Cheapest valid beam | `services/optimization.py` |
| **Brute-force search** | Evaluate all ~72 combos | `optimize_beam_cost()` |
| **Multi-objective** | Pareto frontier (cost vs safety) | `services/multi_objective_optimizer.py` |
| **NSGA-II** | Genetic algorithm for Pareto | `optimize_pareto_front()` |
| **Dominance** | A dominates B if better in all objectives | `_dominates()` |
| **Rebar optimization** | Best bar combo for given $A_{st}$ | `services/rebar_optimizer.py` |
| **Three objectives** | min_area, min_bar_count, max_spacing | `optimize_bar_arrangement()` |
| **Cost breakdown** | Concrete + steel + formwork | `services/costing.py` |
| **IS 456 constraints** | Min/max steel, depth, moment capacity | Every candidate checked |
| **Governing clauses** | Which IS 456 clause controls design | `GOVERNING_CLAUSES` |

---

## 📎 References

- **IS 456:2000** — Cl 26.5.1.1 (Min/max reinforcement), Cl 38.1 (Flexure), Annex G (Limiting moment)
- **NSGA-II paper:** Deb, K. et al. (2002) IEEE Trans Evolutionary Computation
- **CPWD 2023** — Central Public Works Department Schedule of Rates
- **Library source:** `services/optimization.py`, `multi_objective_optimizer.py`, `rebar_optimizer.py`, `costing.py`

---

## What's Next?

**Day 15: FastAPI Basics** — You've built the Python library. Now we wrap it in a REST API so the React frontend (and any HTTP client) can call the design functions. `POST /api/v1/design/beam` → JSON result in 50ms.
