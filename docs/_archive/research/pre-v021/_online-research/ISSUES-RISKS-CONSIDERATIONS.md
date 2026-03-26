# PARETO PROJECT — Issues, Risks, and Considerations

**Type:** Risk Analysis
**Status:** Critical Review
**Created:** 2026-01-13
**Archive After:** When issues resolved or logged in TASKS.md

---

## 🚨 CRITICAL ISSUES (Must Address Before Starting)

### Issue 1: Cost Profile Accuracy

**Problem:**
- Your library uses CPWD DSR 2023 (national average)
- Regional variations ±30% (coastal areas, hilly regions, metro cities)
- Cost profile is hardcoded (not dynamic)

**Impact:** Pareto frontier might be wrong for specific region

**Solution Options:**
1. **Accept limitation** — Document that costs are "national average" only
2. **Add regional customization** — Let user input regional cost factors
3. **Build cost model** — Show ₹ range, not single number

**Recommendation:** Option 2 (medium effort, solves concern)

```python
# Add this to CostProfile
regional_variants = {
    'north': 0.85,  # 15% cheaper
    'metro': 1.25,  # 25% more expensive
    'coastal': 1.10,
}
```

**Action:** Add to API before MVP release
**Effort:** 1-2 hours

---

### Issue 2: Limited Concrete Grades in Optimization

**Problem:**
```python
# From optimization.py:
grade_options = [25, 30]  # Only M25, M30
# Missing: M20 (common), M35, M40 (high strength)
```

**Impact:** Frontier misses cheap (M20) and premium (M40) options

**Solution:**
```python
grade_options = [20, 25, 30, 35, 40]  # All standard grades
```

**Action:** Extend before data generation
**Effort:** 30 minutes (just add to list)

---

### Issue 3: Limited Width Options

**Problem:**
```python
width_options = [230, 300, 400]  # Only 3 widths
```

**Impact:** Limited design diversity, misses optimal width for many cases

**Solution:**
```python
width_options = [200, 230, 250, 300, 350, 400, 450, 500]
# More realistic sampling of design space
```

**Action:** Extend before data generation
**Effort:** 30 minutes

---

### Issue 4: Carbon Footprint Not Implemented

**Problem:**
- No carbon emission tracking in library
- Can't show carbon vs cost trade-off

**Impact:** Missing "sustainability" angle, less impressive visualization

**Solution:**
- Add `CarbonProfile` class (like `CostProfile`)
- Calculate: concrete carbon + steel carbon + formwork carbon
- Use standard factors: M25 concrete ~320 kg CO2/m³, Steel ~2.1 kg CO2/kg

**Action:** Build before visualization
**Effort:** 2-3 hours

---

### Issue 5: No Batch Processing Helper

**Problem:**
- API functions designed for single beams
- Processing 1000 beams requires manual loop
- No parallelization

**Impact:** Slow data generation (10-20 minutes for 1000 designs)

**Solution:**
```python
def design_batch(designs_spec: list[dict]) -> pd.DataFrame:
    """Process multiple designs in parallel."""
    from multiprocessing import Pool

    with Pool(8) as p:  # 8 cores
        results = p.map(design_and_detail_beam_is456, designs_spec)

    return pd.DataFrame(results)
```

**Action:** Build batch module
**Effort:** 2-3 hours

---

## ⚠️ HIGH-RISK ASSUMPTIONS (Validate Early)

### Risk 1: Pareto Frontier Convergence

**Assumption:** 1000 randomly sampled designs will capture ~95% of true Pareto frontier

**Reality check:**
- Design space has 5+ dimensions
- Random sampling might miss clusters
- Smart sampling (Latin Hypercube) might be needed

**Mitigation:**
- Test with 500 designs, then 1000, then 2000
- Measure frontier stability (does it change?)
- If unstable, use Latin Hypercube Sampling

**Action:** Validate during data generation
**Effort:** Testing, not coding

---

### Risk 2: Visualization Clarity

**Assumption:** 2D scatter plot (cost vs weight) will be clear to engineers

**Reality check:**
- 50-100 dots on graph is readable, but?
- Colors for 3rd objective might be confusing
- Need user testing

**Mitigation:**
- Build prototype with 3 engineers
- Ask: "What trade-offs do you see?"
- Iterate visualization based on feedback

**Action:** User testing after MVP
**Effort:** 1-2 hours (scheduling) + iteration

---

### Risk 3: Real-Time Interactivity

**Assumption:** Regenerating Pareto for new load takes <5 seconds

**Reality check:**
- Processing 1000 designs takes 1-2 minutes sequentially
- Even with parallel: 20-40 seconds
- <5 seconds needs caching or interpolation

**Mitigation:**
- Phase 1: Batch (engineer adjusts load, waits 30 seconds)
- Phase 2: Cache common variations (only 20-30 combinations needed)
- Phase 3: Interpolation (estimate frontier for new load based on nearby ones)

**Action:** Set realistic expectations, plan phased approach
**Effort:** Architecture decision only (no coding yet)

---

### Risk 4: Cost Validation Against Reality

**Assumption:** Cost calculations match real construction practice

**Reality check:**
- Library uses simplified models (per-volume costs)
- Real construction has economies of scale, waste factors, site variation
- Discrepancy could be ±20-30%

**Mitigation:**
- Validate against 5-10 real projects (if you have data)
- Otherwise: Document assumptions, note ±20% uncertainty
- Show cost as range, not single number

**Action:** Data collection or assumption documentation
**Effort:** 2-3 hours (validation or documentation)

---

### Risk 5: Design Code Compliance at Scale

**Assumption:** All 1000 generated designs will be IS 456 compliant

**Reality check:**
- Edge cases exist (e.g., very thin beams, very small sections)
- Some depth/width combos might fail checks
- Pareto frontier might be biased toward feasible region

**Mitigation:**
- Filter to only valid designs (is_valid == True)
- Report: "1000 designs generated, 850 valid (85%), 150 rejected"
- Show rejection reasons
- Pareto on valid subset only

**Action:** Add validation logic, document rejection rate
**Effort:** Built into batch processor

---

## ❌ THINGS TO AVOID

### Anti-Pattern 1: Too Much Data in Graph

**Don't:** Show all 1000 designs as dots
- Graph becomes unreadable "bean soup"
- Hard to see patterns
- Slow to render

**Do:** Show only Pareto frontier (50-100 designs)
- Clean, clear, highlights best trade-offs
- Allow hover to see more

---

### Anti-Pattern 2: Misleading Cost Simplification

**Don't:** Show cost without explaining assumptions
- Users might think it's exact
- Reality varies by region, contractor, time

**Do:** Always show:
```
Cost: ₹9,500 ± 20% (regional variation)
Based on: CPWD DSR 2023 national average
Concrete: ₹340/m³, Steel: ₹72/kg, Formwork: ₹500/m²
```

---

### Anti-Pattern 3: Ignoring Design Constraints

**Don't:** Optimize without checking constraints
- Some "optimal" designs violate IS 456
- Graphs become misleading

**Do:** Only show compliant designs on Pareto
- Tag non-compliant (for research, not use)
- Document: "All designs meet IS 456:2000"

---

### Anti-Pattern 4: Over-Optimizing Performance

**Don't:** Spend 2 weeks optimizing from 2 minutes to 30 seconds
- Diminishing returns
- Time better spent on features

**Do:** Get to "good enough" performance early
- 30-60 second Pareto is acceptable
- Optimize only if users complain

---

### Anti-Pattern 5: Too Many Objectives

**Don't:** Show 5-6 objectives on one graph
- Visualization becomes unreadable
- Decision paralysis

**Do:** Start with 2 (cost vs weight)
- Add 3rd (carbon) with color
- Keep 4th+ for advanced users / expert mode

---

## ✅ THINGS TO DO

### Best Practice 1: Validate Incrementally

**Do this:**
```
Week 1: Generate 100 designs, visualize, verify costs make sense
Week 2: Generate 500 designs, check Pareto frontier stability
Week 3: Generate 1000 designs, final frontier
Week 4: Validate 20 random designs against hand calcs
```

**Not this:**
```
Generate all 1000 designs blindly, hope everything works
```

---

### Best Practice 2: Document Assumptions Explicitly

**For every visualization, note:**
- Cost assumptions: "CPWD DSR 2023 national average"
- Constraints: "All designs meet IS 456:2000"
- Limitations: "M25, M30 concrete only (v1.0)"
- Accuracy: "Cost ±20%, weight ±5%, carbon ±15%"

---

### Best Practice 3: Build with Extensibility

**Structure code so it's easy to add:**
- New objective functions (e.g., constructability score)
- New constraints (e.g., environmental regulations)
- New visualizations (e.g., parallel coordinates)

**Don't:** Hardcode everything

---

### Best Practice 4: Test Sensibility Checks

**Verify your results make intuitive sense:**
```
✓ Deeper beams have less steel (makes sense)
✓ Lower cost designs have more steel % (makes sense)
✓ Heavier designs cost more (makes sense)
✗ Cheapest design is lightest (SUSPICIOUS, investigate)
✗ Pareto has huge jumps (SUSPICIOUS, check outliers)
```

---

### Best Practice 5: Plan for User Feedback Loop

**Week 7-8 (before publishing):**
- Show prototypes to 3-5 structural engineers
- Ask: "What's surprising? What's confusing? What's missing?"
- Iterate: Update visualizations, add features
- Document feedback in publication

---

## 🎯 SPECIFIC TECHNICAL CONSIDERATIONS

### Consideration 1: Floating-Point Precision

**Be careful:**
- Cost calculations involve many floating-point ops
- Rounding errors accumulate
- Two designs might be "same cost" within rounding error

**Solution:**
```python
# Round costs to nearest ₹100
cost = round(cost_calculated / 100) * 100

# When comparing, use tolerance
if abs(design_a.cost - design_b.cost) < 100:
    # Consider them equivalent
```

---

### Consideration 2: Design Space Sampling Strategy

**Latin Hypercube Sampling (LHS)** is better than random:
```python
from scipy.stats import qmc

sampler = qmc.LatinHypercube(d=5)  # 5 dimensions
samples = sampler.random(n=1000)  # 1000 stratified points

# Result: Designs are spread evenly across space
# vs random: Designs might cluster in some region
```

**Benefit:** Need fewer designs to capture frontier
**Effort:** Use existing library, easy

---

### Consideration 3: Pareto Filtering with 3+ Objectives

**2 objectives:** Easy (cost vs weight)
**3 objectives:** Need to generalize
```python
def is_dominated(d1, d2, objectives=['cost', 'weight', 'carbon']):
    """Check if d2 dominates d1 (lower on all objectives)."""
    return all(d2[obj] <= d1[obj] for obj in objectives)
```

**4+ objectives:** Becomes complex, consider alternative
- Weighted sum: cost = 0.5*cost + 0.3*weight + 0.2*carbon
- Engineering judgment to pick weights

---

### Consideration 4: Handling Infeasible Designs

**Some designs fail IS 456:**
- Too thin (deflection fails)
- Steel percentage exceeds limits
- Shear strength insufficient

**Strategy:**
1. Mark as invalid (is_valid=False)
2. Don't show on Pareto
3. Report: "X designs infeasible, Y% of total"
4. Optionally: Show "relaxed" frontier (what if we ignore ductility?)

---

### Consideration 5: Export Strategy

**Engineers will want:**
1. CSV/Excel (for further analysis)
2. PDF report (for submission)
3. DXF drawings (for construction)
4. Calculation sheets (for audits)

**Your library already does 3 & 4 via `compute_dxf()` and `compute_report()`**

**You need to add:**
- CSV export of frontier designs
- Bulk PDF generation for selected designs

---

## 📋 PRE-IMPLEMENTATION CHECKLIST

Before you code, verify:

- [ ] Extended `CostProfile` with regional factors
- [ ] Extended `optimization.py` to include M20, M35, M40, more widths
- [ ] Created `carbon.py` module with emission factors
- [ ] Decided on batch processing strategy (sequential vs parallel)
- [ ] Chose sampling strategy (random vs Latin Hypercube)
- [ ] Defined "acceptable cost accuracy" (±20%? ±10%?)
- [ ] Listed visualization requirements (which graphs must be MVP?)
- [ ] Identified performance target (30s? 60s? 2min?)
- [ ] Planned validation strategy (hand calcs? real projects?)
- [ ] Scheduled user testing (who, when, how many?)

---

## 🚀 NEXT ACTION

Create a detailed **IMPLEMENTATION PLAN** that addresses:
1. API extensions (carbon, batch processing)
2. Data generation (1000 designs, how long, which combos)
3. Pareto filtering (algorithm, validation)
4. Visualization (Plotly or Streamlit, which graphs)
5. Testing & validation (sensibility checks, user feedback)
6. Documentation (assumptions, limitations, usage)

This checklist and risk analysis should inform that plan.

---

**All findings in this research folder will be archived (2026-01-27) once implementation starts. Keep key insights in the main documentation.**
