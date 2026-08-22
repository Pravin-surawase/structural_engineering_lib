---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: spec
complexity: advanced
tags: [safety, validation, diagnostics, public-api]
---

# LIB-PRO-004 Lower-Level Safety and Diagnostic Closure

**Source base:** exact hosted Packet D merge
`640c7839f043adb0e7db02d924a9e1a3a06e1131`.

**G0 decision:** `REVISE`. The six reproduced table/material defects and the
function-quality false positives are bounded and repairable here. The proposed
input-auditor rewrite also reveals additional unsafe maintained routes, so this
packet must not claim complete public-route validation closure.

## Corrected truth model

Two inventories have different owners and must not be merged:

1. `@clause` is the IS 456 calculation-quality inventory used by
   `check_function_quality.py`.
2. `docs/reference/api-classification.json` is the declared Python-route
   authority used by `audit_input_validation.py`, supplemented by the six
   lower-level compatibility helpers and public `IS456Code` methods.

Each maintained input is reported as `PROVEN`, `DELEGATED`, `UNPROVEN`, or
`NOT_APPLICABLE`. Type annotations alone are not runtime validation, and a raw
collection annotation does not prove its contents. Every `UNPROVEN` parameter
is reported and keeps the diagnostic non-green. Adversarial runtime tests remain
decisive because static ownership is not safety proof.

## Frozen lower-level domains

| Route | Accepted numeric domain | Invalid behavior |
|---|---|---|
| `get_tc_value` | `fck` 15-40 N/mm2; `pt` 0.15-3.0% | reject before lookup/interpolation |
| `get_tc_max_value` | `fck` 15-40 N/mm2 | reject before lookup/interpolation |
| `get_ec`, `get_fcr` | `fck` 15-80 N/mm2 | reject before arithmetic |
| `get_xu_max_d` | `fy` 250-550 N/mm2 | reject before arithmetic |
| `get_steel_stress` | finite real strain; `fy` 250-550 N/mm2 | reject before arithmetic |
| `IS456Code` strength helpers | concrete 15-80; steel 250-550 N/mm2 | reject before arithmetic |

All boundaries reject booleans, non-real values, NaN, infinity, and unsupported
domains. Valid formulas, exact boundary values, and existing benchmark outputs
remain unchanged. The steel-stress helper retains its maintained continuous
250-550 range; it is not narrowed to a few benchmark grades.

## One-lane execution

### A — Lower-level boundary repair

Use one private finite-real/range validator in the IS 456 layer; apply it to the
six helpers and the two direct strength methods. Cover canonical modules,
legacy compatibility exports, and `IS456Code` delegates. No formula expansion.

### B — Input-auditor semantic repair

Replace the legacy percentage/grade with evidence-bearing ownership states,
registry discovery, keyword-only handling, per-function visitor state, direct
guard and validator attribution, complete unresolved output, JSON evidence, and
synthetic/current-source tests. Do not exempt `get_*` functions.

### C — Function-quality calibration

Retain outcome-critical checks, label advisory checks, treat unit suffixes
case-insensitively, recognize semantic non-dimensional parameters, bind legacy
short names to explicit function-level unit metadata, require a rationale and
decisive test for exact equality, and remove the tautological decorator check.

### D — Cumulative acceptance

Freeze all content before routine verification. Then run the affected tests,
public-route safety gate, independent material/table benchmarks, architecture
and import checks, quick gate once, normal hooks once, complete Python/FastAPI/
React/Excel suites, full repository gate once, and hosted PR checks once.

`PASS` requires both diagnostics to have zero unreviewed findings. A truthful
`PARTIAL` is the required outcome if the rebuilt input auditor retains any
`UNPROVEN` input. That result completes this diagnostic packet but does not
authorize a new package or professional-use claim.

## Confirmed successor boundary

Direct probes on the source base and repaired lane show additional maintained
routes accepting unsafe inputs:

- `calculate_equivalent_shear(NaN, 10, 300)` returns `NaN` and accepts boolean
  shear;
- `calculate_development_length(bar_diameter=True, ...)` returns a result; and
- `compute_beam_outline(NaN, 500, 3000)` returns NaN geometry.

These are outcome-changing findings, not scanner cosmetics. Their transitive
route families and every remaining `UNPROVEN` parameter require a separately
bounded successor with runtime reproducers before mutation.

## Non-goals

- no repair of newly discovered routes beyond the frozen six helpers and two
  direct strength methods;
- no new IS formula, table, structural element, or support claim;
- no ETABS/desktop Excel work or `INDIA-3` implementation;
- no version bump, tag, upload, GitHub Release, or professional approval;
- no cleanup or deletion of retained branches, worktrees, or unrelated changes.
