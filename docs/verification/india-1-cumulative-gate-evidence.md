---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-1-CUMULATIVE
---

# INDIA-1 Cumulative Gate Evidence

INDIA-1A through INDIA-1D are integrated on main as four independently gated
packets:

| Packet | Reviewed head | Squash merge | Integrated outcome |
|---|---|---|---|
| INDIA-1A beam | `5df4e996` | `3a7e162e` | bounded sagging T-beam composition |
| INDIA-1B column | `1f10778c` | `f44452dd` | symmetric two-face rectangular decision closure |
| INDIA-1C footing | `03a50688` | `236ce646` | public concentric isolated-footing composition |
| INDIA-1D slab | `9d7fe61d` | `ca55f22d` | serviceability, shear, and loading boundary closure |

For every packet, the reviewed feature-head tree equals its integrated squash-
merge tree. No branch, ref, or worktree cleanup was authorized or performed.

## Deferred gates

The first cumulative broad Python run exposed one stale CI-contract regression:
the test still expected `deploy-docs.yml` to run on pull requests after PR #745
moved strict MkDocs PR evidence into the required consolidated PR Validation
workflow. The correction now verifies that `deploy-docs.yml` remains main/manual
and build-only while `fast-checks.yml` owns strict pull-request documentation
validation.

After that root-cause repair:

- broad Python: 5,926 passed, 3 skipped, 6 deselected;
- full repository gate: 30/30 passed;
- generated API manifest: current;
- generated Indian-code manifest: current; and
- capability state: 21 records, zero unknown, with beam, column, isolated
  footing, and solid slab all `SUPPORTED` / `IMPLEMENTED_BOUNDED`.

The folder-index audit reported 29 of 32 indexes stale because the generator's
hash includes dates derived from linked-worktree filesystem mtimes. Those bulk
changes do not represent INDIA-1 content drift and were not committed.

## Cumulative review conclusion

The integrated public facades, numerical benchmarks, provenance, units,
supported cases, fail-closed holds, and serialized result boundaries are
consistent. No outcome-changing INDIA-1 software or claim defect was found.

This is software acceptance evidence only. Direct professional use, stable-
capability approval, package publication, tagging, and GitHub Release creation
remain outside this result. Qualified structural-engineering review and the
per-release owner authorization are still required.
