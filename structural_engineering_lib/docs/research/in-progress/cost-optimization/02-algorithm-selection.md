# Algorithm Selection: Cost Optimization

**Date:** 2026-01-05
**Status:** In Progress
**Researcher:** Claude + User

---

## Problem Recap

**Goal:** Find cheapest beam design (b, D, fck, fy) that meets IS 456:2000 for given (span, loads).

**Search space:** ~2,400 combinations (feasible for exhaustive search)

---

## Candidate Approaches

### Approach 1: Brute Force (Exhaustive Search)

**Description:**
- Try every combination of (b, D, fck, fy)
- For each, check IS 456 compliance
- Calculate cost
- Return cheapest valid design

**Algorithm:**
```python
def optimize_beam_cost_bruteforce(span, mu, vu, ...):
    best_cost = infinity
    best_design = None

    for b in [230, 300, 400, 500]:  # Standard widths
        for D in range(300, 900, 50):  # Depths in 50mm steps
            for fck in [20, 25, 30, 35]:
                for fy in [415, 500]:
                    # Design beam
                    design = flexure.design_singly_reinforced(b, D-cover, mu, fck, fy)

                    # Check compliance
                    if not complies_with_is456(design):
                        continue

                    # Calculate cost
                    cost = calculate_total_cost(b, D, span, design.ast, fck)

                    if cost < best_cost:
                        best_cost = cost
                        best_design = design

    return best_design, best_cost
```

**Pros:**
- ✅ Guarantees global optimum (finds true best solution)
- ✅ Simple to implement (no complex algorithm)
- ✅ Easy to debug and validate
- ✅ Fast enough (2,400 iterations << 1 second)

**Cons:**
- ⚠️ Doesn't scale to more variables (e.g., doubly reinforced)
- ⚠️ May find impractical designs (e.g., b=230, D=850)

**Complexity:** O(n × m × k × l) = O(4 × 20 × 4 × 2) = O(2,400) → **< 1 second**

---

### Approach 2: Heuristic Search (Greedy)

**Description:**
- Start with conservative thumb rule (span/12 for depth)
- Try variations: deeper (less steel) vs wider (more concrete)
- Pick direction that reduces cost most
- Iterate until no improvement

**Algorithm:**
```python
def optimize_beam_cost_heuristic(span, mu, ...):
    # Start with thumb rule
    D_initial = span / 12
    b_initial = 300  # Standard

    current_design = design_beam(b_initial, D_initial, mu, ...)
    current_cost = calculate_cost(current_design)

    improved = True
    while improved:
        improved = False

        # Try increasing depth
        deeper_design = design_beam(b_initial, D_initial + 50, mu, ...)
        deeper_cost = calculate_cost(deeper_design)

        if deeper_cost < current_cost:
            current_design = deeper_design
            current_cost = deeper_cost
            D_initial += 50
            improved = True

        # Try increasing width (similar logic)
        ...

    return current_design
```

**Pros:**
- ✅ Very fast (5-10 iterations typically)
- ✅ Intuitive (mimics engineer thinking)
- ✅ Scales better to complex problems

**Cons:**
- ❌ May find local optimum (not guaranteed best)
- ❌ Depends on starting point
- ❌ Harder to validate correctness

**Complexity:** O(log n) iterations → **< 0.1 second**

---

### Approach 3: Genetic Algorithm

**Description:**
- Create population of random designs
- "Breed" best designs (crossover)
- Random mutations
- Iterate for N generations

**Algorithm:**
```python
def optimize_beam_cost_genetic(span, mu, ...):
    population = initialize_random_designs(100)

    for generation in range(50):
        # Evaluate fitness (lower cost = better)
        fitnesses = [1/calculate_cost(d) for d in population]

        # Select parents (tournament selection)
        parents = select_parents(population, fitnesses)

        # Breed children (crossover b, D, fck, fy)
        children = crossover(parents)

        # Mutate some children
        mutate(children, mutation_rate=0.1)

        # New population
        population = select_best(population + children, keep=100)

    return best_design_in_population
```

**Pros:**
- ✅ Good for very large search spaces
- ✅ Can handle complex constraints
- ✅ Finds good solutions even if not optimal

**Cons:**
- ❌ Overkill for our problem (2,400 combinations)
- ❌ Non-deterministic (different runs give different results)
- ❌ Harder to tune (mutation rate, population size, etc.)
- ❌ Slower than brute force for small spaces

**Complexity:** O(population × generations) = O(100 × 50) = O(5,000) → **~1 second**

---

### Approach 4: Gradient-Based Optimization

**Description:**
- Start with initial guess
- Calculate gradient of cost w.r.t. (b, D)
- Move in direction of steepest descent
- Iterate until convergence

**Problems for our case:**
- ❌ Cost function is **discrete** (b, D must be integers)
- ❌ Gradient doesn't exist at discrete steps
- ❌ Many local minima due to IS 456 constraints
- ❌ Complex constraints (pt_min, pt_max, etc.)

**Verdict:** ❌ Not suitable for this problem

---

## Comparison Matrix

| Approach | Optimality | Speed | Complexity | Suitability |
|----------|-----------|-------|------------|-------------|
| **Brute Force** | ✅ Global optimum | ✅ < 1s | ✅ Low | **⭐⭐⭐⭐⭐** |
| **Heuristic** | ⚠️ Local optimum | ✅ < 0.1s | ⚠️ Medium | ⭐⭐⭐ |
| **Genetic Algorithm** | ⚠️ Near-optimal | ⚠️ ~1s | ❌ High | ⭐⭐ |
| **Gradient** | ❌ N/A | N/A | ❌ High | ❌ |

---

## Recommended Approach

### **Primary: Brute Force with Intelligent Pruning**

**Rationale:**
1. **Small search space** (2,400 combinations) → brute force feasible
2. **Guarantees best solution** → users trust it
3. **Easy to implement and test** → fast development
4. **Deterministic** → same inputs always give same output

**Enhancements:**
```python
def optimize_beam_cost_smart_bruteforce(span, mu, vu, ...):
    """Brute force with intelligent pruning."""
    candidates = []

    # Generate candidates (prune infeasible early)
    for b in [230, 300, 400]:  # Standard widths (pruned from 15 options)
        for D in range(max(300, span//20), min(900, span//8), 50):  # Smart range
            for fck in [25, 30]:  # Most common grades (prune 20, 35 initially)
                for fy in [500]:  # Modern standard (prune 415)
                    # Quick feasibility check before full design
                    if not quick_feasibility_check(b, D, mu, span):
                        continue

                    # Full design
                    design = design_beam(b, D, mu, fck, fy)

                    # Check all IS 456 constraints
                    if not is_compliant(design):
                        continue

                    # Calculate detailed cost
                    cost = calculate_total_cost(b, D, span, design, fck)

                    candidates.append({
                        'design': design,
                        'cost': cost,
                        'params': (b, D, fck, fy)
                    })

    # Return top 3 candidates (not just cheapest)
    # User can review and pick based on other factors
    return sorted(candidates, key=lambda x: x['cost'])[:3]
```

**Optimizations:**
1. **Smart bounds** - D between span/20 and span/8 (typical practice)
2. **Standard sizes first** - Try common (300mm width, M25, Fe500) before exotic
3. **Early feasibility** - Check Mu_lim before full design
4. **Pruned grades** - Start with M25/M30, Fe500 only
5. **Return top 3** - Let user choose (may prefer slightly more expensive but simpler)

**Expected performance:**
- Pruned search space: ~300-500 combinations (down from 2,400)
- Time: **< 0.5 seconds**
- Quality: **Global optimum** within pruned space

---

### **Fallback: Heuristic for Very Large Problems**

If future features expand search space (e.g., doubly reinforced, flanged beams):

**Strategy:**
1. Use brute force if combinations < 5,000
2. Use heuristic if combinations > 5,000
3. Automatically switch based on problem size

---

## Validation Strategy

**How to verify algorithm works:**

### Test Case 1: Simple Residential Beam
- Span: 5m
- Mu: 120 kNm
- Expected: b=300, D≈450, M25, Fe500
- Manual verification: Check cost is indeed minimal

### Test Case 2: Heavy Commercial Beam
- Span: 8m
- Mu: 400 kNm
- Expected: Deeper beam or higher grade
- Verify: Cost savings vs standard design

### Test Case 3: Edge Cases
- Very light load → minimum section
- Very heavy load → may need doubly reinforced
- Long span → depth drives cost

**Acceptance criteria:**
- [ ] All designs pass IS 456 compliance
- [ ] Cost savings of 10-20% vs conservative design
- [ ] Runs in < 1 second
- [ ] Returns practical, constructible designs

---

## Implementation Checklist

**Phase 1: Core Function (Day 3)**
- [ ] Create `costing.py` module
  - [ ] `calculate_concrete_cost(b, D, L, fck)`
  - [ ] `calculate_steel_cost(ast, L)`
  - [ ] `calculate_formwork_cost(b, D, L)`
  - [ ] `calculate_total_cost(design, span, cost_profile)`

**Phase 2: Optimization (Day 3)**
- [ ] Create `optimization.py` module
  - [ ] `optimize_beam_cost(span, mu, vu, cost_profile)`
  - [ ] Return `CostOptimizationResult` with:
    - Best design
    - Cost breakdown
    - Savings vs standard
    - Alternative options (top 3)

**Phase 3: Integration (Day 4)**
- [ ] Update `api.py` to accept `cost_profile` parameter
- [ ] Add to `insights/__init__.py`
- [ ] Write unit tests (20 validation beams)

---

## Data Structures

### Input: CostProfile
```python
@dataclass
class CostProfile:
    """Regional cost data for materials and labor."""
    currency: str = "INR"

    # Material costs
    concrete_m25_per_m3: float = 6700
    concrete_m30_per_m3: float = 7200
    steel_fe500_per_kg: float = 72
    formwork_per_m2: float = 500

    # Labor modifiers
    congestion_threshold_pt: float = 2.5  # Percentage
    congestion_multiplier: float = 1.2

    # Regional factors
    location_factor: float = 1.0  # 1.0 = national avg
```

### Output: CostOptimizationResult
```python
@dataclass
class CostOptimizationResult:
    """Result of cost optimization."""

    # Best design found
    optimal_design: BeamDesign
    optimal_cost: float

    # Cost breakdown
    concrete_cost: float
    steel_cost: float
    formwork_cost: float
    labor_cost: float

    # Comparison
    standard_design_cost: float  # Conservative baseline
    savings_amount: float
    savings_percent: float

    # Alternatives
    alternative_designs: List[Tuple[BeamDesign, float]]  # Top 3

    # Metadata
    iterations_evaluated: int
    computation_time_sec: float
```

---

## Next Steps

**Tomorrow (Day 3):**
1. Implement `costing.py` (core cost calculations)
2. Implement `optimization.py` (brute force algorithm)
3. Test on 10 sample beams
4. Measure cost savings vs standard design

**Success Metric for Day 3:**
- [ ] 10/10 beams optimized successfully
- [ ] All show 10-20% savings vs standard
- [ ] Runs in < 1 second average

---

**Status:** Algorithm selected (brute force). Ready to prototype!
