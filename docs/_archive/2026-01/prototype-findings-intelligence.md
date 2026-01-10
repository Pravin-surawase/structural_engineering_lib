# Prototype Findings: Intelligence Features (Sensitivity + Heuristics)

**Date:** 2025-12-30
**Prototype Version:** v0.1 (pre-release)
**Scope:** Sensitivity analysis + Predictive validation
**Status:** ✅ Validated against golden vectors

---

## Executive Summary

Implemented and validated two "smart library" features:

1. **Predictive Validation** - Fast heuristic pre-checks (<10ms) to catch issues before full design
2. **Sensitivity Analysis** - Identify critical parameters and assess design robustness

**Key Result:** Prototype matched 3/3 sample vectors with deterministic, traceable outputs
(small sample; not a general accuracy claim).

---

## 1. Predictive Validation (Heuristic Pre-Checks)

### Implementation

**Module:** `structural_lib/intelligence.py` (prototype) → `structural_lib/insights/precheck.py` (v0.13)
**Function:** `quick_precheck(span_mm, b_mm, d_mm, D_mm, mu_knm, fck_nmm2, fy_nmm2)`
**Performance:** < 1ms (target: <10ms)

**Heuristic Rules Implemented:**

| Rule | Basis | Threshold |
|------|-------|-----------|
| Span/depth ratio | IS 456 Table 23 | > 20 → deflection risk |
| Steel estimate | Lever arm approximation | > 4% → doubly reinforced likely |
| Width check | Constructability | < 150mm → bar spacing issues |
| Cover adequacy | Practical limits | cover/D > 0.25 → check inputs |
| Concrete grade | Common practice | M15-M50 range |

### Validation Results

**Tested against 3 golden vectors:**

| Vector | Description | Steel % | Precheck | Actual | Match? |
|--------|-------------|---------|----------|--------|--------|
| G1 | Light steel (80 kN·m) | 0.32% | PROCEED | SAFE ✓ | ✅ Correct |
| G2 | Typical steel (120 kN·m) | 0.51% | PROCEED | SAFE ✓ | ✅ Correct |
| G3 | Heavy steel (160 kN·m) | 0.71% | PROCEED | SAFE ✓ | ✅ Correct |

**Match rate:** 3/3 (sample-only)
**False positives:** 0 (sample-only)
**False negatives:** 0 (sample-only)

### Example Output

```
============================================================
QUICK PRE-CHECK (Heuristic Validation)
============================================================
Check time: 0.0ms
Overall risk: HIGH
Recommendation: REVIEW GEOMETRY

Found 2 potential issue(s):

1. DEFLECTION RISK 🔴 [HIGH]
   ├─ Issue: Span/depth ratio = 24.0 > 20, deflection likely critical
   ├─ Fix: Increase d to at least 333mm for better deflection control
   └─ Basis: Typical span/d ratio: 10-12 for simply supported beams (IS 456 Table 23)

2. HIGH STEEL CONGESTION 🟡 [MEDIUM]
   ├─ Issue: Estimated steel %: 3.20% > 2%, potential bar congestion
   ├─ Fix: Check bar spacing and constructability carefully
   └─ Basis: Steel % > 2% may cause spacing issues
============================================================
```

### Findings

✅ **Strengths:**
- Fast (<1ms vs ~10-50ms for full design)
- Clear, actionable warnings with fix suggestions
- Clause references provide traceability
- Severity levels guide user priorities

⚠️ **Limitations:**
- Conservative (intentionally) - may flag cases that pass full design
- Heuristic thresholds based on typical practice, not absolute limits
- No structural analysis - just quick sanity checks

📋 **Recommendations:**
1. Refine thresholds based on SP:16 verified examples (expand from 3 to 10-15 cases)
2. Add constructability scoring (Rule 6: bar spacing, lapping zones)
3. Make severity levels configurable (strict/relaxed modes)

---

## 2. Sensitivity Analysis

### Implementation

**Module:** `structural_lib/intelligence.py` (prototype) → `structural_lib/insights/sensitivity.py` (v0.13)
**Function:** `sensitivity_analysis(design_function, base_params, parameters_to_vary, perturbation=0.10)`
**Method:** Perturbation analysis (±10% by default)

**Algorithm:**
```python
for param in parameters_to_vary:
    # Perturb +10%
    perturbed_value = base_value * 1.10
    perturbed_result = design_function(**perturbed_params)

    # Calculate sensitivity
    delta_utilization = perturbed_util - base_util
    sensitivity = delta_utilization / perturbation  # (%/%​)
```

**Impact Classification:**
- High: |sensitivity| > 0.5 (10% param change → >5% utilization change)
- Medium: 0.2 < |sensitivity| ≤ 0.5
- Low: |sensitivity| ≤ 0.2

### Validation Results

**Tested on G2 (typical beam: 300×500mm, Mu=120 kN·m, M25, Fe500)**

| Parameter | Sensitivity | Impact | Engineering Sense |
|-----------|-------------|--------|-------------------|
| d (depth) | -0.24 | MEDIUM 🟡 | ✅ Correct - depth most critical for bending |
| mu_knm (moment) | +0.14 | LOW 🟢 | ✅ Correct - moderate utilization (12.6%) has headroom |
| b (width) | -0.13 | LOW 🟢 | ✅ Correct - width less important than depth |

**Robustness Score:** 0.90 (EXCELLENT)
**Vulnerable Parameters:** d only (1 parameter)

### Example Output

```
============================================================
SENSITIVITY ANALYSIS
============================================================

Critical Parameters (ranked by impact):

1. d            🟡 MEDIUM
   └─ +10% change → utilization 12.6% → 10.2%
   └─ Sensitivity: -0.24

2. mu_knm       🟢 LOW
   └─ +10% change → utilization 12.6% → 14.1%
   └─ Sensitivity: 0.14

3. b            🟢 LOW
   └─ +10% change → utilization 12.6% → 11.4%
   └─ Sensitivity: -0.13

------------------------------------------------------------
ROBUSTNESS ASSESSMENT
------------------------------------------------------------
Score:  0.90 (EXCELLENT)
Status: Design has moderate sensitivity to 1 parameters.

⚠ Vulnerable to: d
============================================================
```

### Findings

✅ **Strengths:**
- Identifies physically meaningful critical parameters (depth > width)
- Robustness score (0-1) provides intuitive design quality metric
- Ranked output guides where to focus attention
- Deterministic and repeatable

⚠️ **Limitations:**
- Perturbation method assumes local linearity (valid for ±10%)
- Doesn't capture parameter interactions (e.g., b and d together)
- Utilization is proxy metric - doesn't capture serviceability

📋 **Recommendations:**
1. Add multi-parameter perturbation (e.g., simultaneous b+d variation)
2. Extend to serviceability sensitivity (deflection, crack width)
3. Provide "what-if" helper: "To reduce mu_knm sensitivity, increase d by X%"

---

## 3. Validation Summary

### Test Coverage

| Test Type | Count | Pass | Fail | Notes |
|-----------|-------|------|------|-------|
| Golden vectors | 3 | 3 | 0 | 100% accuracy |
| Demo scenarios | 3 | 3 | 0 | Typical, shallow, high-moment |
| Combined workflow | 1 | 1 | 0 | Precheck → design → sensitivity |

**Total:** 7 scenarios, 7 passed

### Engineering Validation

✅ **Heuristics align with practice:**
- Span/depth ratio check matches IS 456 Table 23 guidance
- Steel percentage thresholds match typical construction limits
- Width checks align with bar spacing requirements

✅ **Sensitivity ranking correct:**
- Depth more critical than width (lever arm dominates)
- Moment sensitivity proportional to utilization level
- Robustness score inversely correlates with utilization

✅ **Outputs deterministic:**
- Same input → same output (verified with golden vectors)
- No randomness, no ML black boxes
- Full traceability to engineering rules

---

## 4. Integration Recommendations

### For v0.13 (Next Release)

**Priority: P0 (Core Innovation, Safe by Default)**

1. **Insights module (opt-in):**
   ```python
   from structural_lib.insights import precheck, sensitivity
   ```
   No changes to `design_beam_is456()` or result schemas.

2. **Separate insights output:**
   ```
   results.json   # schema v1 (unchanged)
   insights.json  # insights-v1 (new, advisory-only)
   ```

3. **Optional CLI command:**
   ```bash
   python -m structural_lib insights results.json -o insights.json
   ```

4. **Report integration (later):**
   Add insights sections to reports once outputs are stable.

### Effort Estimate

| Task | Effort | Dependencies |
|------|--------|--------------|
| Insights module finalization | 0.5 week | None |
| Optional CLI integration | 0.5 week | Insights done |
| Insights schema (new, separate) | 0.5 week | Insights done |
| Refine heuristics (SP:16) | 1 week | Verified examples ready |
| Unit tests | 0.5 week | Insights done |
| Report updates (optional) | 1 week | Insights stabilized |

**Total:** ~3-4 weeks (aligns with v0.13 timeline)

### Future Enhancements (v0.14+)

- **Constructability scoring** (v0.14)
- **Deterministic alternatives search** (v0.14, replaces stochastic optimization for now)
- **Pattern recognition from SP:16** (v0.15)
- **Serviceability sensitivity** (v0.15)
- **Design space exploration** (v0.16)

---

## 5. Files Created

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `structural_lib/intelligence.py` | Prototype implementation (superseded) | ~440 | ✅ Complete |
| `structural_lib/insights/*` | v0.13 implementation (opt-in) | TBD | ⏳ In progress |
| `examples/demo_intelligence.py` | Feature demonstration | ~280 | ✅ Complete |
| `examples/validate_intelligence.py` | Sample validation | ~230 | ✅ Complete |
| `docs/planning/research-smart-library.md` | Research documentation | ~946 | ✅ Complete |
| `docs/planning/prototype-findings-intelligence.md` | This document | ~350 | ✅ Complete |

**Total:** ~2,250 lines of code + documentation

---

## 6. Next Steps

### Immediate (This Week)

- [ ] Review findings with stakeholders
- [ ] Decide on v0.13 integration scope
- [ ] Update TASKS.md with breakdown

### Short-term (v0.13 - 3 weeks)

- [ ] Finalize insights module signatures (opt-in, separate outputs)
- [ ] Write comprehensive unit tests (target: >90% branch coverage)
- [ ] Integrate optional insights CLI + insights.json schema
- [ ] Refine heuristics based on 10-15 SP:16 examples
- [ ] Update documentation (insights guide, examples)

### Medium-term (v0.14+ - 6-12 weeks)

- [ ] Add constructability scoring
- [ ] Implement multi-objective optimization (pymoo)
- [ ] Extend sensitivity to serviceability checks
- [ ] Build design space exploration

---

## 7. Appendix: Technical Details

### Heuristic Rule Derivation

**Rule 1: Span/depth ratio**
- Basis: IS 456:2000 Table 23 (deflection control)
- Threshold: 20 (typical for simply supported beams is 10-12, conservative limit is 20)
- Source: Engineering practice + code guidance

**Rule 2: Steel estimate**
- Formula: `Ast ≈ Mu / (0.87 * fy * 0.9 * d)`
- Assumption: Lever arm ≈ 0.9d (typical for under-reinforced sections)
- Threshold: 4% (singly-reinforced economical up to ~4%, beyond needs compression steel)

**Rule 3: Width check**
- Minimum: 150mm (practical minimum for bar placement)
- Constructability: <200mm may have spacing issues for large bars

**Rule 4: Cover adequacy**
- Check: cover / D ratio
- Flag if > 0.25 (likely input error - cover should be ~10-15% of D)

**Rule 5: Concrete grade**
- Range: M15 to M50 (common in Indian practice per IS 456)
- Flag if outside range (may be input error or special case)

### Sensitivity Formula Derivation

Given:
- Base utilization: `U_base = Ast_req / Ast_max`
- Perturbed utilization: `U_perturbed`
- Perturbation: `δ = 0.10` (10%)

Sensitivity:
```
S = (U_perturbed - U_base) / δ
```

Units: `(% / %)` - dimensionless ratio

**Physical Meaning:**
- S = -0.24 → 10% increase in parameter → 2.4% decrease in utilization (beneficial)
- S = +0.14 → 10% increase in parameter → 1.4% increase in utilization (adverse)

### Robustness Score Calculation

```python
def calculate_robustness(sensitivities, base_utilization):
    # Count high-impact parameters
    high_impact = sum(1 for s in sensitivities if abs(s.sensitivity) > 0.5)
    med_impact = sum(1 for s in sensitivities if 0.2 < abs(s.sensitivity) <= 0.5)

    # Penalty for high/medium impacts
    impact_penalty = high_impact * 0.15 + med_impact * 0.05

    # Penalty for high utilization (less margin)
    util_penalty = max(0, (base_utilization - 0.5) * 0.2)

    # Score (0-1 scale, higher is better)
    score = 1.0 - impact_penalty - util_penalty
    score = max(0.0, min(1.0, score))

    # Rating
    if score >= 0.80: "EXCELLENT"
    elif score >= 0.65: "GOOD"
    elif score >= 0.50: "ACCEPTABLE"
    else: "POOR"
```

**Interpretation:**
- 0.90 (EXCELLENT) → Small parameter changes have minimal impact, good margins
- 0.70 (GOOD) → Moderate sensitivity, still acceptable
- 0.55 (ACCEPTABLE) → Borderline, consider increasing margins
- 0.40 (POOR) → High sensitivity, small changes → large impact on safety

---

**Document Version:** 1.0
**Last Updated:** 2025-12-30
**Author:** Prototype validation session
**Review Status:** Ready for stakeholder review
