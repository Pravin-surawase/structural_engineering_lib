---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: reference
complexity: advanced
tags: [safety, validation, diagnostics, public-api]
---

# LIB-PRO-004 Lower-Level Safety and Diagnostic Evidence

**Source base:** `640c7839f043adb0e7db02d924a9e1a3a06e1131`

**Local verdict:** `PARTIAL`. The frozen lower-level boundary repair and
function-quality diagnostic pass. The rebuilt input-validation audit is
decisive and non-green because it exposes 370 unresolved parameter owners and
additional reproduced unsafe routes outside this packet.

## Boundary outcome

The public table/material helpers, legacy exports, and `IS456Code` delegates
reject booleans, strings, complex values, NaN, infinity, and unsupported
domains before arithmetic. Valid limits and benchmark values are unchanged.

Table 19 now has two explicit contracts:

- public `get_tc_value` rejects caller-supplied `fck` outside 15-40 N/mm2 and
  `pt` outside 0.15-3.0%;
- the private derived-reinforcement path validates finite, non-negative
  computed reinforcement and deliberately uses the nearest Table 19 row.

This split repaired the root cause found by the first broad run: a single
helper had previously mixed public validation with derived-value lookup.
Footing and slab calculations use the private path. Beam compliance bounds a
derived value only for its torsion lookup while retaining the exact value for
the decisive shear check, so an unsupported shear domain remains a structured
failure with no invented exact utilization.

## Diagnostic outcome

`check_function_quality.py --strict --summary` reports:

```text
Summary: 88 functions, 88 pass (100.0%), 0 fail
```

The checker retains eleven historical check IDs, separates five
outcome-critical contracts from advisories, recognizes semantic inputs and
explicit legacy unit metadata, and binds each of three exact-equality cases to
a rationale and decisive test.

`audit_input_validation.py` discovers declared route owners from
`api-classification.json`, the six explicit compatibility helpers, and public
`IS456Code` methods. Its frozen report is:

| State | Parameters |
|---|---:|
| `PROVEN` | 132 |
| `DELEGATED` | 86 |
| `UNPROVEN` | 370 |
| `NOT_APPLICABLE` | 131 |
| **Total** | **719 across 101 owners** |

All 370 unresolved rows are emitted and the diagnostic exits 1. Raw collection
annotations and ordinary numeric type hints are not treated as validation.

## G0 correction evidence

Direct runtime probes reproduce three unsafe maintained routes not identified
in the proposed six-helper scope:

| Probe | Observed result |
|---|---|
| `calculate_equivalent_shear(NaN, 10, 300)` | accepts and returns `NaN` |
| `calculate_equivalent_shear(True, 10, 300)` | accepts and returns `54.333...` |
| `calculate_development_length(bar_diameter=True, fck=25, fy=415)` | accepts and returns `ld=40.0` |
| `compute_beam_outline(NaN, 500, 3000)` | accepts and returns NaN points |

Therefore the planning claim that only a small set of lower-level defects
exists is rejected. The rebuilt scanner is useful precisely because it keeps
those gaps visible. Static ownership remains diagnostic evidence; runtime
reproducers are decisive.

## Verification

- new boundary, scanner, function-quality, and readiness tests: 90 pass;
- public-route safety gate: 20 Python targets and 4 FastAPI targets pass;
- affected direct-call/property/benchmark corpus: 2,122 tests selected; the
  outcome-mapped failed nodes were repaired and retested;
- architecture: 218 files, zero violations;
- imports: 244 files, 1,459 imports, zero broken imports;
- quick repository gate: 10/10 pass;
- complete product suites: 6,728 Python pass (3 skipped, 6 deselected), 479
  FastAPI pass, 276 React pass, and 21 Excel add-in pass.

The full repository gate and hosted PR checks are post-freeze read-only gates.
Their outcomes do not change this `PARTIAL` product verdict while any
`UNPROVEN` validation owner remains.

## Authority and limits

The maintained source authority remains IS 456:2000, reaffirmed in 2021, and
the prior Packet B domain/provenance evidence. This software evidence is not a
qualified structural-engineering review, package-release authorization, or
project-design approval.
