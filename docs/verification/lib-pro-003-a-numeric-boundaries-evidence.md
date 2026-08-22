---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: verification
complexity: advanced
tags: [safety, validation, public-api, regression]
---

# LIB-PRO-003-A Numeric Boundary Evidence

## Identity and scope

- Source base: hosted `main` at
  `e40c0b564acae82f6696e204e8b382342fbf4321`.
- Branch: `codex/public-route-numeric-boundaries`.
- Runtime diagnosis: `source_bound=true`; initial Git state `READY_LOCAL`.
- Scope: finite-real public calculation boundaries, empty compliance
  aggregation, and exact uniaxial-column safety comparison only.
- No engineering formulas, supported grades, release artifacts, ETABS, or
  desktop Excel operations changed.

## Confirmed root causes and corrected outcomes

| Reproduction | Root cause | Corrected outcome |
|---|---|---|
| NaN flexure and shear returned safe results | Positive/range comparisons do not reject NaN | Shared `E_INPUT_017` finite-real validation returns an unsafe structured result before arithmetic |
| NaN compliance returned `is_ok=True` | Calculation inputs and derived utilization were not required to be finite | Direct and service compliance routes reject the input before component design |
| `check_compliance_report(cases=[])` returned success | `all([])` is vacuously true | Empty reports raise a stable `ValueError` and cannot produce a compliance disposition |
| Unified column accepted `Mux=-inf` | Minimum-moment `max()` replaced the invalid action with a finite value | Every numeric routing input is finite-validated before classification or amplification |
| Exact utilization slightly above one displayed `1.0000` and passed | Safety used the rounded display value | Safety uses exact utilization; the returned display ratio remains rounded and reports unsafe |

The shared helper also rejects booleans and non-real values. Every directly
consumed numeric argument in the affected flexure, shear, compliance, and
uniaxial-column routes is covered before arithmetic.

## Compatibility and contracts

- Result-returning beam functions preserve their existing result types and use
  the stable structured issue `E_INPUT_017`.
- Exception-based compliance and column service routes preserve their existing
  `ValueError`/structural-validation contracts.
- The compatibility `structural_lib.validation` facade exports the new helper.
- The public error registry records `E_INPUT_017`.
- Valid SP:16 column, beam verification-pack, and public API-stability vectors
  remain unchanged.

## Focused verification

- 260 unique implementation-focused tests are green across core validation,
  flexure/shear input validation, compliance validation, uniaxial columns, and
  public column return contracts. The first diagnostic run exposed six missing
  compatibility exports; after that root repair, the 86-test validation file
  passed and the other 174 tests remained green.
- 138 independent verification/API tests passed: 20 column golden vectors,
  seven beam/shear/compliance verification-pack tests, and 111 public API
  stability tests.
- Focused Ruff and `git diff --check` passed.
- The consolidated quick gate passed 10/10, including documentation, import,
  Git-state, CLI-smoke, hygiene, and unfinished-operation checks.

## Remaining release blockers

This packet closes only `LIB-PRO-003-A`. Packets B-D remain required for
beam/column domain contracts and footing provenance; structured slab, legacy
CSV, and BOQ failure; and decisive Excel CI/audit/documentation gates. A new
package and all stable/professional-use claims remain `HOLD`.
