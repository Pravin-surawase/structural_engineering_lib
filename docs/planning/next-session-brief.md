# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-09
- Focus: LIB-IS456-C1 Git integration for the bounded IS 456 product milestone
<!-- HANDOFF:END -->

**Current branch:** `codex/release-v0.23.0`
**Current commit:** `b1634a5f`
**Plan:** [is456-library-first-master-plan.md](is456-library-first-master-plan.md)

## Required Reading

- [IS 456 library-first master plan](is456-library-first-master-plan.md)
- [Professional remediation evidence ledger](professional-library-remediation-plan.md)
- [Current task board](../TASKS.md)

| Release state | Version | Decision |
|---|---|---|
| **Current** | v0.23.0 | Prepared development candidate on release hold; not published |
| **Next** | v0.24.0 | Future roadmap only; inactive until C0-C4 closeout and owner activation |

## Outcome

T0 and R1-R8 are implemented; do not repeat them. The owner selected the
bounded IS 456 product milestone, not the v0.24/v1.0 multi-code roadmap. C0
plan reconciliation is complete. C1 must turn the current mixed worktree into
reviewable scoped checkpoints and integrate the separately landed automation
commit `f812eb3f` without reset, rebase, stash, or lost work.

Until that final qualified review is recorded, the repository and every
candidate artifact are development software: they are not approved or usable
for engineering decisions. AI code or engineering review may be used during
development, but it does not satisfy the final professional gate.

## Implemented remediation

- Supported beam and footing entry points reject booleans, non-real values,
  NaN, and infinities before arithmetic.
- Batch completion is separate from engineering safety; unsafe shear is FAIL
  across Python, SSE, React display/export, and apply-to-store behavior.
- Reports normalize legacy `is_safe` to canonical `is_ok`; missing status is
  NOT EVALUATED and unsafe sections override stale overall PASS.
- Footing flexure requires total thickness for minimum steel, and dowel count
  is a strict positive integer through Python and FastAPI.
- Two-way slab output explicitly distinguishes bounded flexure computation,
  coefficient provenance, qualified acceptance, and complete design approval.
- A machine-readable semantic contract covers every supported capability,
  unit, field, alias, status, limitation, and v0.24 report-alias removal.
- `docs/reference/api-manifest.json` is the only Python API manifest. The stale
  service manifest was safely removed and is recoverable from
  `tmp/deleted_backups/api_manifest_20260809_222544.json`.
- Both API validators share the raw OpenAPI baseline; request-validation 422s
  use the maintained `{success,data,error}` envelope with field detail.
- Release checks bind source/docs, wheel filename/METADATA/content, clean
  installed version, and packaged CLI behavior. Published wording and
  nonexistent tag-install examples were removed.

## Verification evidence

- Python: 5,445 passed, 3 skipped, 6 deselected.
- FastAPI: 349 passed.
- React: 147 passed; lint and production build passed on Node 24.
- Quick gate: 9/9; full gate: 29/29.
- Readiness audit: 19/19; health: 100/100; parity: 93%.
- API manifest: 73/73 compatible functions.
- OpenAPI: 62 endpoints, 65 schemas, no drift.
- Exact clean-source wheel: 181 members, zero excluded namespaces, imported
  `structural_lib.__version__ == 0.23.0`, CLI help passed, SHA-256
  `1414a06acbac36f503c9e18c11461a10d02f722f87f78c95a530336f35063770`.

The wheel was disposable and removed after inspection. A stale source-tree
`Python/build/lib` was proven to contaminate an ordinary build with excluded
migration/research/ACI/EC2 files; the release gate now rejects that content.

## Next actions

1. Inspect `git status --short` and preserve the concurrent governance/model
   policy lanes. Nothing is staged or committed.
2. Preserve the automation-owned paths from `f812eb3f`; separate product,
   remediation, policy, terminal, and documentation checkpoints deliberately.
3. Synchronize `origin/main` only after a clean checkpoint and inspect every
   overlap. Do not rewrite history or discard uncommitted work.
4. Continue in order: C2 final product UAT, C3 frozen artifacts, C4 evidence
   freeze, then final qualified review. Publication remains separately gated.

## Terminal issues recorded

- A contract test initially depended on `PYTHONPATH=Python:.`; it is now
  repository-root stable under `./run.sh test`.
- `tool_registry.py --validate` is not a supported flag; the maintained
  `check_scripts_index.py`, script-reference gate, and full check were used.
- An unmatched zsh release-doc glob failed before execution; explicit paths
  and `git diff --name-only | rg` worked.
- zsh reserves `status`; the deliberate release-failure proof used `rc`.
