# Cost Optimization Guide

**Type:** Guide
**Audience:** Users
**Status:** Approved
**Importance:** Medium
**Version:** 1.0.0
**Created:** 2025-12-20
**Last Updated:** 2026-01-13

---

This guide explains how to use the cost optimization features to explore cheaper beam designs while meeting IS 456 requirements.

## What It Does
- Searches common beam sizes and material grades to find a lower-cost design.
- Produces a ranked set of alternatives with cost breakdowns.
- Preserves deterministic outputs (same input -> same output).

## Prerequisites
- Python package installed: `structural-lib-is456`
- Units: mm, kN, kN-m, N/mm^2

## Quick Example (Python)
```python
from structural_lib.api import optimize_beam_cost

result = optimize_beam_cost(
    units="IS456",
    span_mm=5000,
    mu_knm=120,
    vu_kn=80,
    cover_mm=40,
)

print(result["optimal_design"])
print(result["savings_percent"])
```

## Interpretation
- `optimal_design`: the lowest-cost valid design candidate.
- `alternatives`: additional valid options with costs and tradeoffs.
- `savings_percent`: cost improvement vs baseline.

## References
- API: `docs/reference/api.md`
- Insights API: `docs/reference/insights-api.md`
- Design suggestions: `docs/getting-started/insights-guide.md`
