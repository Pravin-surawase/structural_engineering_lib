---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: spec
complexity: advanced
tags: [safety, validation, public-api, release-hold]
---

# Public Route Safety Closure Plan

**Task:** `LIB-PRO-003`
**Source base:** hosted `main` at `e40c0b564acae82f6696e204e8b382342fbf4321`
**Decision:** `HOLD` for a new package, stable/professional claims, and
engineering-use approval until the bounded packets below close.

## Audit decision

The 2026-08-22 exact-tree replay confirmed that the bounded Gravity Workflow
V1 and E1 contracts remain valid, while 13 outcome-changing behaviours remain
available through older or lower-level public routes. Mechanical green checks
do not supersede those direct public outcomes.

The confirmed families are:

1. non-finite flexure, shear, compliance, and column actions can report safe;
2. an empty compliance aggregate can report success;
3. beam shear inputs, steel percentages, and unsupported material grades can
   be substituted, clamped, or accepted as top-level success;
4. column reinforcement limits, an unrounded capacity boundary, and one stale
   result key can produce false PASS or a crash;
5. footing provenance can accept an unknown origin;
6. slab over-capacity, malformed legacy CSV, and negative BOQ rates do not use
   truthful structured failure contracts; and
7. Excel add-in CI, audit-tool exit policy, release wording, and route-count
   wording are not decisive or synchronized.

This is a new evidence-driven program. It does not reopen or rewrite the
historical `LIB-PRO-001` or `LIB-PRO-002` ledgers.

## Frozen sequence

### Packet A — Numeric and aggregate fail-closed boundaries

**Status:** integrated through PR #832 at `e7698a63` with reviewed and merged
trees equal.

**Owned behaviour:**

- add one stable finite-real validation issue and apply it before arithmetic in
  public lower-level beam flexure, beam shear, compliance, and column routes;
- reject empty compliance reports instead of relying on vacuous `all([])`;
- reject non-finite unified-column actions before minimum-moment amplification;
- decide uniaxial-column safety from exact utilization and round only the
  returned display value.

**Acceptance:** the reproduced NaN, infinity, empty-report, `-infinity`
column, and `1.0000` rounded-utilization cases fail closed; all affected valid
tests and independent column benchmarks remain unchanged.

### Packet B — Beam, column, and provenance domains

**Status:** integrated through PR #833 at `e19b757c` with reviewed and merged
trees equal.

Reject supplied non-positive shear steel instead of substituting it; reject
out-of-domain steel percentages and unsupported material grades; enforce
column reinforcement limits; repair the stale uniaxial result key; and require
a declared footing provenance origin.

### Packet C — Structured failure and intake truth

**Status:** integrated through PR #834 at `02755445` with reviewed and merged
trees equal.

Return a structured slab capacity `FAIL`, make the legacy CSV route block
malformed numeric cells without zero coercion or row loss, and reject negative
BOQ rates at the request boundary.

### Packet D — Decisive gates and repository truth

**Status:** local candidate accepted on `codex/public-route-decisive-gates`
from exact hosted Packet C merge `02755445`; hosted and exact-tree merge
closure remain.

Run the Excel add-in tests for `excel_addin/**` changes, require the frozen
public-route adversarial regressions in readiness evidence, return nonzero for
both `PARTIAL` and `FAIL`, reconcile release and endpoint-count wording with
clearly named metrics, and make documentation front-matter/budget part of the
required audit. The owner-selected active Markdown hard cap is 500.

After A-D pass focused, quick, broad, and hosted acceptance, the owner may
resume `INDIA-3-G0`. A future package remains a separate versioned artifact and
owner-authorized release operation.

The local A-D regression set is green, but readiness remains `PARTIAL`/exit 2
because two heuristic diagnostics remain unresolved. This preserves a package
and professional-use `HOLD`; it does not block a later read-only INDIA-3 truth
audit after Packet D merges.

## Non-goals

- no IS 456, IS 13920, IS 875, or IS 1893 formula expansion;
- no ETABS or desktop Excel activity;
- no package version bump, tag, upload, or GitHub Release;
- no claim of formula certification, professional approval, or project fitness;
- no cleanup, deletion, or reinterpretation of preserved branches/worktrees.
