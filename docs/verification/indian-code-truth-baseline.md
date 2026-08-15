# INDIA-0 Indian-Code Truth Baseline

**Type:** Reference
**Audience:** Developers
**Status:** Active
**Created:** 2026-08-15
**Last Updated:** 2026-08-15
**Importance:** Critical
**Evidence boundary:** PR #753 exact-head checks passed and the reviewed tree
was squash-merged as `0373de68`; INDIA-1 packets now update the generated
manifest from fresh integrated-main lanes

**Manifest:**
[`indian-code-capability-coverage.json`](indian-code-capability-coverage.json)

**Git handoff:** [`INDIA-0-git-handoff.json`](INDIA-0-git-handoff.json)
**Claim ceiling:** Software scope and traceability evidence only; qualified
structural-engineering review remains required before stable or engineering-use
approval.

## Purpose

INDIA-0 replaces two incompatible measurements with one deterministic,
standard-namespaced manifest:

- capability families are either `SUPPORTED` or `HELD`;
- implementation is either `IMPLEMENTED_BOUNDED` or `NOT_IMPLEMENTED`;
- standard-reference decorators are `REGISTERED`, `METADATA_ONLY`, or
  `REGISTRATION_ONLY`.

Decorator registration is not implementation, numerical verification,
provenance, or whole-standard completeness. No percentage in the manifest is a
professional approval score.

## Generated sources

| Source | Role |
|---|---|
| `Python/structural_lib/services/capabilities.py` | Canonical supported IS 456 workflows and held boundaries |
| `Python/structural_lib/codes/is456/clauses.json` | Distributable identifier/search metadata; legacy IS 13920 records are split into their own manifest namespace |
| `Python/structural_lib/codes/is456/**/*.py` | Deterministically discovered IS 456 decorator registrations |
| `Python/structural_lib/codes/is13920/**/*.py` | Deterministically discovered IS 13920 decorator registrations |

The generator fails on a non-literal decorator reference or an unsupported
standard name. The committed artifact is checked byte-for-byte against fresh
generation.

## Reconciled scope

| Standard namespace | Supported | Held | Boundary |
|---|---:|---:|---|
| `IS456:2000` | 4 families | 8 families | Beam, rectangular column, isolated footing, and solid slab are bounded; other declared families remain held |
| `IS13920:2016` | 3 check families | 2 families | Beam/column detailing and pure-math SCWB checks exist; complete seismic design is not claimed |
| `IS875` | 0 | 2 families | Gravity and wind load generation are not implemented; editions/parts are not yet selected |
| `IS1893` | 0 | 2 families | Equivalent-static and response-spectrum analysis are not implemented; editions are not yet selected |

The IS 13920 reference registry also exposes registration-only identifiers.
That is a traceability metadata gap, not a computational failure and not a
reason to erase the working beam, column, or SCWB checks.

## Root-cause corrections

| Symptom | Confirmed root cause | Correction |
|---|---|---|
| Parity reported slabs and Annex D as planned | A hand-maintained 17-item table treated file existence as implementation | Dashboard now consumes declared capability families from the generated manifest |
| “IS 456” clause report mixed IS 13920 entries and omitted slab/footing modules | Mixed metadata, a static module import list, and a registry projection that discarded the decorator standard | AST discovery scans maintained code roots and namespaces references before aggregation |
| Strategic and task tables contradicted completed slab/footing work | Historical plans were retained as live-looking status tables | Current tables were reconciled or explicitly archived in place; the generated manifest is the status authority |

## Reproduction

```bash
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
./scripts/python_runtime.sh scripts/check_clause_coverage.py --summary
./scripts/python_runtime.sh scripts/parity_dashboard.py --section capabilities
./scripts/python_runtime.sh -m pytest Python/tests/test_indian_code_manifest.py -q
```

The first command reports standard-namespaced decorator registration only. The
second reports declared supported versus held capability families. Neither is a
whole-standard-completeness score or professional approval. Declared capability
scope is informational and excluded from the dashboard's actionable cross-layer
composite; intentionally held families are not failed parity checks.

## Remaining gates

- The fail-closed Git handoff remains a retained pre-publication receipt. PR
  #753 passed its exact-head gate and its reviewed tree equals the integrated
  squash-result tree at `0373de68`.
- INDIA-1 must use the manifest's held cases to close or retain limitations in
  the already supported beam, column, isolated-footing, and solid-slab families.
- Release, stable approval, engineering-use approval, and branch/worktree
  retirement remain separately authorized actions.
