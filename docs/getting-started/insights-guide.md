# Advisory Insights Guide

> **Status:** Preview (v0.13.0+)
> **Stability:** Experimental - API may change before v1.0

Advisory insights provide quick heuristic assessments of beam designs to help engineers make informed decisions early in the design process.

## Overview

The insights module offers three types of analysis:

1. **Precheck** - Fast heuristic validation before detailed design
2. **Sensitivity Analysis** - Identify critical design parameters
3. **Constructability Scoring** - Assess ease of construction

All insights are **advisory only** and do not replace code compliance checks.

---

## Quick Start

### Python API

```python
from structural_lib.api import design_beam_is456
from structural_lib.insights import (
    quick_precheck,
    sensitivity_analysis,
    calculate_constructability_score,
)

# 1. Precheck (before design)
precheck = quick_precheck(
    span_mm=5000,
    b_mm=300,
    d_mm=450,
    D_mm=500,
    mu_knm=140,
    fck_nmm2=25,
    fy_nmm2=500,
)

if precheck.risk_level == "HIGH":
    print(f"Warning: {precheck.warnings[0].message}")
    print(f"Suggestion: {precheck.warnings[0].suggestion}")

# 2. Sensitivity analysis (after design)
params = {
    "units": "IS456",
    "mu_knm": 140,
    "vu_kn": 85,
    "b_mm": 300,
    "D_mm": 500,
    "d_mm": 450,
    "fck_nmm2": 25,
    "fy_nmm2": 500,
}

sensitivities, robustness = sensitivity_analysis(
    design_beam_is456,
    params,
    ["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"],
)

# Most critical parameters
for s in sensitivities[:3]:
    print(f"{s.parameter}: sensitivity={s.sensitivity:.2f}, impact={s.impact}")

print(f"Robustness: {robustness.score:.2f} ({robustness.rating})")
```

### CLI

```bash
# Run design with insights
python -m structural_lib design beams.csv -o results.json --insights

# Creates two files:
# - results.json (design results)
# - <output_stem>_insights.json (advisory insights)
#   Example: -o results.json -> results_insights.json
```

---

## Precheck

**Purpose:** Catch potential issues before running detailed design.

### What it checks

- **Depth adequacy** - Ensures depth is sufficient for span (Cl. 23.2)
- **Flexural capacity** - Quick estimate of required reinforcement area
- **Geometry ratios** - Checks b/D, d/D ratios for typical beams

### Risk Levels

- **LOW** - Design likely to pass (proceed with confidence)
- **MEDIUM** - May need iteration (review parameters)
- **HIGH** - Likely to fail (revise geometry or loads)

### Example

```python
from structural_lib.insights import quick_precheck

# Check a beam before designing
result = quick_precheck(
    span_mm=6000,
    b_mm=230,  # Narrow beam
    d_mm=400,
    D_mm=450,
    mu_knm=180,  # High moment
    fck_nmm2=25,
    fy_nmm2=500,
)

print(f"Risk level: {result.risk_level}")
print(f"Recommendation: {result.recommended_action}")

# Check for specific warnings
for warning in result.warnings:
    if warning.severity.value == "warning":
        print(f"⚠️  {warning.message}")
        print(f"   Suggestion: {warning.suggestion}")
        print(f"   Basis: {warning.rule_basis}")
```

**Output:**
```
Risk level: MEDIUM
Recommendation: review
⚠️  Beam width (230mm) is below typical minimum (250mm)
   Suggestion: Consider increasing width to 250-300mm for better constructability
   Basis: IS 456 Cl. 23.1 (typical practice)
```

---

## Sensitivity Analysis

**Purpose:** Identify which parameters most affect the design.

### What it computes

- **Normalized sensitivity** - `S = (ΔU/U) / (Δp/p)` (dimensionless)
- **Impact classification** - Critical / High / Medium / Low
- **Robustness score** - How much can parameters vary before failure

### Sensitivity Coefficient

The normalized sensitivity `S` is dimensionless and comparable across different parameter types:

- `S = -2.0` means a 10% increase in parameter decreases utilization by 20%
- `S = +0.5` means a 10% increase in parameter increases utilization by 5%

Negative sensitivity = good (parameter helps when increased)
Positive sensitivity = bad (parameter hurts when increased)

### Example

```python
from structural_lib.api import design_beam_is456
from structural_lib.insights import sensitivity_analysis

params = {
    "units": "IS456",
    "mu_knm": 140,
    "vu_kn": 85,
    "b_mm": 300,
    "D_mm": 500,
    "d_mm": 450,
    "fck_nmm2": 25,
    "fy_nmm2": 500,
}

# Analyze top 4 parameters
sensitivities, robustness = sensitivity_analysis(
    design_beam_is456,
    params,
    parameters_to_vary=["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"],
    perturbation=0.10,  # 10% variation
)

# Results sorted by |sensitivity| (most critical first)
print("Parameter Sensitivities:")
print("=" * 60)
for s in sensitivities:
    sign = "↓" if s.sensitivity < 0 else "↑"
    print(f"{s.parameter:12s} | S={s.sensitivity:+6.2f} {sign} | {s.impact:8s}")
    print(f"  Base: {s.base_value:.1f} → Perturbed: {s.perturbed_value:.1f}")
    print(f"  Utilization: {s.base_utilization:.2%} → {s.perturbed_utilization:.2%}")
    print()

print(f"\nRobustness Score: {robustness.score:.2f} ({robustness.rating})")
print(f"Base Utilization: {robustness.base_utilization:.2%}")
if robustness.vulnerable_parameters:
    print(f"Vulnerable to: {', '.join(robustness.vulnerable_parameters)}")
```

**Output:**
```
Parameter Sensitivities:
============================================================
d_mm         | S= -2.37 ↓ | critical
  Base: 450.0 → Perturbed: 495.0
  Utilization: 78% → 61%

b_mm         | S= -0.91 ↓ | high
  Base: 300.0 → Perturbed: 330.0
  Utilization: 78% → 71%

fck_nmm2     | S= -0.68 ↓ | medium
  Base: 25.0 → Perturbed: 27.5
  Utilization: 78% → 73%

fy_nmm2      | S= +0.28 ↑ | low
  Base: 500.0 → Perturbed: 550.0
  Utilization: 78% → 80%

Robustness Score: 0.82 (excellent)
Base Utilization: 78%
Vulnerable to: d_mm, b_mm
```

### Interpretation

**Depth (d_mm) has highest sensitivity:**
- 10% increase in depth → 30% reduction in utilization (S=-2.37)
- Most effective parameter for improving design
- Small errors in depth are critical

**Width (b_mm) moderately sensitive:**
- 10% increase in width → 9% reduction in utilization (S=-0.91)
- Less effective than depth but still important

**Steel strength (fy_nmm2) has positive sensitivity:**
- Increasing fy can sometimes increase utilization
- Happens when design is compression-controlled
- Not a reliable parameter for optimization

### Robustness Score

- **0.80-1.00 (Excellent)** - Very robust, can tolerate 20%+ variations
- **0.65-0.79 (Good)** - Robust for normal construction tolerances
- **0.50-0.64 (Acceptable)** - Requires careful quality control
- **<0.50 (Poor)** - Fragile design, little margin for error

---

## Constructability Scoring

**Purpose:** Assess how easy the design is to construct.

### Scoring Factors

Based on Singapore BDAS framework (Poh & Chen, 1998):

| Factor | Ideal | Penalty If | Impact |
|--------|-------|------------|--------|
| Bar clear spacing | ≥60mm | <40mm | High rework risk, poor concrete consolidation |
| Stirrup spacing | ≥125mm | <100mm | Poor vibration access |
| Bar variety | ≤2 sizes | >2 sizes | Procurement delays, site confusion |
| Standard sizes | 8,10,12,16,20,25,32mm | Other sizes | Higher cost, tooling issues |
| Layer count | ≤2 layers | >2 layers | High placement difficulty |
| Depth increments | 50mm multiples | Odd sizes | Higher formwork cost |
| Bar configuration | 2-3 bars/layer | >5 bars/layer | Placement complexity |

### Score Interpretation

- **85-100 (Excellent)** - Easy construction, low labor cost
- **70-84 (Good)** - Typical construction complexity
- **55-69 (Acceptable)** - Requires experienced crew
- **<55 (Poor)** - Congested, high rework risk

### Example

```python
from structural_lib.api import design_beam_is456
from structural_lib.detailing import create_beam_detailing
from structural_lib.insights import calculate_constructability_score

# Run design
design = design_beam_is456(
    units="IS456",
    mu_knm=140,
    vu_kn=85,
    b_mm=300,
    D_mm=500,
    d_mm=450,
    fck_nmm2=25,
    fy_nmm2=500,
)

# Get detailing
detailing = create_beam_detailing(
    beam_id="B1",
    story="L1",
    b=300,
    D=500,
    span=5000,
    cover=40,
    fck=25,
    fy=500,
    ast_start=1200,
    ast_mid=1200,
    ast_end=1200,
    asc_start=400,
    asc_mid=400,
    asc_end=400,
    stirrup_dia=8,
    stirrup_spacing_start=150,
    stirrup_spacing_mid=200,
    stirrup_spacing_end=150,
)

# Assess constructability
score = calculate_constructability_score(design, detailing)

print(f"Constructability: {score.score:.0f}/100 ({score.rating})")
print("\nFactors:")
for factor in score.factors:
    if factor.penalty < 0:
        print(f"❌ {factor.factor}: {factor.message}")
        print(f"   {factor.recommendation}")
    elif factor.score > 0:
        print(f"✅ {factor.factor}: {factor.message}")
```

**Output:**
```
Constructability: 75/100 (good)

Factors:
✅ standard_sizes: All bars are standard sizes
✅ depth_increment: Depth 500mm is 50mm multiple (formwork reuse)
❌ bar_spacing: Clear spacing 35mm is tight
   Consider spacing >= 60mm for easier placement. Impact: Increased labor time.
```

---

## CLI Integration

### Basic Usage

```bash
# Run design with insights
python -m structural_lib design beams.csv -o results.json --insights
```

Creates two files:
- `results.json` - Design results (complian ce, utilization, detailing)
- `results_insights.json` - Advisory insights (precheck, sensitivity, robustness)

### Insights JSON Schema

```json
{
  "schema_version": "1.0",
  "insights_version": "preview",
  "beams": [
    {
      "beam_id": "B1",
      "story": "L1",
      "precheck": {
        "check_time_ms": 0.15,
        "risk_level": "LOW",
        "warnings": [],
        "recommended_action": "proceed",
        "heuristics_version": "1.0"
      },
      "sensitivities": [
        {
          "parameter": "d_mm",
          "base_value": 450.0,
          "perturbed_value": 495.0,
          "base_utilization": 0.78,
          "perturbed_utilization": 0.61,
          "delta_utilization": -0.17,
          "sensitivity": -2.37,
          "impact": "critical"
        }
      ],
      "robustness": {
        "score": 0.82,
        "rating": "excellent",
        "vulnerable_parameters": ["d_mm"],
        "base_utilization": 0.78,
        "sensitivity_count": 4
      },
      "constructability": null
    }
  ]
}
```

---

## Best Practices

### 1. Use Precheck Early

Run precheck **before** detailed design to catch issues:

```python
# Bad: Design first, then realize it won't work
design = design_beam_is456(...)  # Might fail!

# Good: Precheck first
precheck = quick_precheck(...)
if precheck.risk_level != "HIGH":
    design = design_beam_is456(...)
```

### 2. Limit Sensitivity Parameters

Only analyze parameters you can actually change:

```python
# Don't analyze loads (usually fixed by analysis)
sensitivity_analysis(design_beam_is456, params, ["mu_knm", "vu_kn"])  # ❌

# Analyze geometry and materials (designer controls these)
sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2"])  # ✅
```

### 3. Act on High Sensitivity

If a parameter has high/critical sensitivity:

- **Specify tighter tolerances** in drawings
- **Coordinate with construction** team
- **Consider design margin** for that parameter

### 4. Use Constructability for Design Choices

When choosing between equivalent designs:

```python
# Option A: 4-20mm bars (more congested)
# Option B: 3-25mm bars (simpler)

# Compare constructability scores to inform decision
score_a = calculate_constructability_score(design, detailing_a)
score_b = calculate_constructability_score(design, detailing_b)

if score_b.score > score_a.score:
    print(f"Option B is easier to construct (+{score_b.score - score_a.score:.0f} points)")
```

---

## Limitations

### Insights are Advisory Only

- **Not a substitute** for code compliance checks
- **Heuristic-based** - may not catch all issues
- **Preview feature** - API may change before v1.0

### Precheck Limitations

- Uses simplified formulas (may over-/under-estimate)
- Doesn't check all code requirements
- Risk levels are indicative, not deterministic

### Sensitivity Limitations

- Assumes linear behavior (10% perturbation)
- Doesn't account for parameter interactions
- Requires successful base design (util < 1.0)

### Constructability Limitations

- Based on Singapore practice (may differ regionally)
- Doesn't account for local labor skill
- Scores are relative, not absolute

---

## Troubleshooting

### "Sensitivity analysis failed"

**Cause:** Base design is failing (utilization > 1.0)

**Fix:** Ensure base design passes before running sensitivity:

```python
design = design_beam_is456(**params)
if design.is_ok:
    sensitivities, robustness = sensitivity_analysis(...)
else:
    print("Fix base design first!")
```

### "Constructability score is None in CLI"

**Cause:** Constructability requires full detailing (not yet integrated for CSV input)

**Workaround:** Use Python API directly with `create_beam_detailing()`

### "Sensitivity shows infinity"

**Cause:** Perturbed design failed (crossed failure threshold)

**Interpretation:** Parameter is **extremely critical** - any decrease causes failure

---

## API Reference

See [insights-api.md](../reference/insights-api.md) for detailed API documentation.

---

## Further Reading

- [Sensitivity Analysis Blog Post (draft)](../publications/blog-posts/03-sensitivity-analysis/draft.md)
- [Constructability Scoring Research](../publications/findings/00-research-summary-FINAL.md)
- [IS 456 Formula Reference](../reference/is456-formulas.md)

---

**Last updated:** 2025-12-31
**Version:** v0.13.0 (preview)
