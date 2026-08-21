# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: complete one deterministic review-bundle export successor, then rerun the frozen Windows G3 journey once
- Validated predecessor: `codex/e1-blank-workbook-guard` at `514155b266af6dff3e30bf39ee28671c17345454`, tree `57e563909f84736a0d3b1a161d2e4d02ee4a4fe3`
- Successor lane: `codex/e1-review-bundle-export`, stacked directly on the validated predecessor
- Evidence: `docs/verification/e1-review-bundle-export-evidence.md`
- Git handoff receipt: `docs/verification/e1-review-bundle-export-git-handoff-receipt.json` (`HOLD`; file SHA-256 `b5a8e9624c6d11503bdc197e31a2a11ab851ce42bac4a11847d64f4046d270fe`)
- Current verdict: `FOCUSED LOCAL PASS / CLOSEOUT PENDING / G3 HELD`
- Held: Windows G3 until one immutable successor passes local/hosted evidence; all ETABS/VBA, write-back, optimization, nightly work, publication, release, merge, cleanup, and professional approval
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | Windows W0 is `READY_FOR_G3`; first G3 preflight stopped before workbook creation because the installed pane/API could not export the complete deterministic evidence required by the frozen plan |
| **Next** | Freeze and verify the single export successor: full Python bundle, fail-closed REST attachment, pane byte/hash verification, source-free wheel, quick gate, hooks, and immutable audit |
| **After local closeout** | Push one stacked draft PR, run hosted checks, then send the exact head/tree/wheel/pane identities to a fresh Windows task for one impact-mapped blank-workbook check and the full G3 journey |
| **Held** | ETABS/VBA execution, real model access, analysis control, write-back, optimization, publication, release, and professional approval remain outside this packet |

## Confirmed G3 blocker and repair

The blank-workbook guard and its static-module route pass on Windows at the
exact predecessor head. The fresh G3 task then proved two separate gaps:

- the installed pane has no export control and the router has no export route;
- the existing Markdown renderer is a status summary, not the complete
  mapping/result/passport/issue evidence required by the plan.

The successor accepts the current selected-table snapshot plus retained hashes,
regenerates the result in Python, requires source/mapping/engine/result identity
agreement, and returns the complete result as deterministic JSON. The pane
verifies the exact bytes before initiating one download. Edits or unverified
reopen state disable export.

## Frozen Windows G3 journey after successor closeout

1. Reuse the proven entitlement, certificate, restricted catalog, and loopback
   setup; install only the exact new wheel and pane files.
2. Run one blank-workbook guard check because `taskpane.mjs` changed.
3. Open the unchanged packaged workbook and run the frozen PASS, FAIL, HOLD,
   blocked, and blank-row vectors with full reconciliation.
4. Export twice from one current snapshot and require identical bytes and
   complete mapping/results/passports/issues.
5. Edit one calculation-bearing input; require `STALE` and disabled export.
6. Recalculate, export twice, close/reopen, pass freshness, and export again;
   same-snapshot bytes and identities must match.
7. Capture G3 receipt and stop. Do not start ETABS.

## Required Reading

1. [Review-bundle export evidence](../verification/e1-review-bundle-export-evidence.md)
2. [Blank-workbook guard evidence](../verification/e1-blank-workbook-guard-evidence.md)
3. [Windows W0 evidence](../verification/e1-windows-w0-setup-evidence.md)
4. [E1 evidence](../verification/e1-excel-routine-workbench-v1-evidence.md)
5. [E1 execution plan](e1-excel-routine-workbench-v1-plan.md)
6. [Current task board](../TASKS.md)
7. [Git workflow single source](../git-automation/git-workflow-single-source.md)

Historical VBA/API reference files remain preserved at
`C:\CodexWork\reference\etabs-vba-handoff`. They are not part of this repair.
Keep macros disabled and do not run ETABS or legacy VBA until a separately
approved, bounded packet begins.
