---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: guide
complexity: intermediate
tags: []
---

# Cost Optimization Guide

**Type:** Guide
**Audience:** Users
**Status:** Approved
**Importance:** Medium
**Version:** 1.0.0
**Created:** 2025-12-20
**Last Updated:** 2026-08-23

---

This guide explains the bounded rectangular-beam cost optimizer. It evaluates
the supplied material grades and section grid with maintained IS 456 flexure
and shear design, then ranks the valid candidates by cost.

## What It Does
- Searches the exact section grid and material grades supplied by the caller.
- Produces a ranked set of alternatives with cost breakdowns.
- Applies the factored shear with the supplied vertical-stirrup area.
- Preserves deterministic outputs (same input -> same output).

The current quantity and cost basis includes required longitudinal
reinforcement, concrete, and formwork. It does not include stirrup mass because
stirrup perimeter and anchorage geometry are not optimizer inputs. The shear
result and designed stirrup spacing are still decisive safety checks.

## Prerequisites
- Python package installed: `structural-lib-is456`
- Units: mm, kN, kN-m, N/mm^2

## Quick Example (Python)

```python
import math

from structural_lib import (
    CostProfile,
    OptimizationConstraints,
    optimize_beam_cost,
)

clear_cover_mm = 25.0
main_bar_diameter_mm = 16.0
stirrup_diameter_mm = 8.0
stirrup_legs = 2

effective_depth_deduction_mm = (
    clear_cover_mm + stirrup_diameter_mm + main_bar_diameter_mm / 2
)
asv_mm2 = stirrup_legs * math.pi * stirrup_diameter_mm**2 / 4

result = optimize_beam_cost(
    units="IS456",
    span_mm=5000,
    mu_knm=120,
    vu_kn=80,
    effective_depth_deduction_mm=effective_depth_deduction_mm,
    fck_nmm2=25,
    fy_nmm2=500,
    asv_mm2=asv_mm2,
    constraints=OptimizationConstraints(
        min_width_mm=200,
        max_width_mm=500,
        min_depth_mm=300,
        max_depth_mm=800,
        width_step_mm=50,
        depth_step_mm=50,
        min_flexural_utilization=0.7,
    ),
    cost_profile=CostProfile(
        currency="INR",
        concrete_costs={25: 6000.0},
        steel_cost_per_kg=60.0,
        formwork_cost_per_m2=400.0,
        congestion_threshold_pt=2.5,
        congestion_multiplier=1.2,
        location_factor=1.0,
    ),
    max_alternatives=5,
)

print(result.summary())
print(result.optimal_design.ast_required_mm2)
print(result.optimal_design.stirrup_spacing_mm)
print(result.savings_percent)
```

## Interpretation
- `optimal_design`: the lowest-cost valid design candidate.
- `alternatives`: additional valid options with costs and tradeoffs.
- `flexural_utilization`: factored moment divided by the limiting singly
  reinforced moment resistance.
- `shear_utilization`: nominal shear stress divided by the maximum design shear
  stress.
- `stirrup_utilization`: required shear carried by stirrups divided by the
  capacity available at the reported practical spacing; values above one are
  rejected as infeasible.
- `savings_percent`: cost improvement against the valid candidate nearest the
  conventional 300 mm width and span/12 overall-depth basis.

The REST endpoint `POST /api/v1/optimization/beam/cost` requires the material,
clear-cover/bar basis, currency and all cost modifiers, and candidate grid.
Unknown request fields are rejected so misspelled project inputs cannot be
silently discarded. It accepts only
`optimize_for: "cost"`; unsupported objectives receive HTTP 422 rather than a
cost-ranked approximation.

## References
- API: `docs/reference/api.md`
- Insights API: `docs/reference/insights-api.md`
- Design suggestions: `docs/getting-started/insights-guide.md`
