# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: LIB-IS456-C3 exact local artifact freeze for the bounded IS 456 product milestone
<!-- HANDOFF:END -->

**Current branch:** `codex/release-v0.23.0`
**Integrated baseline:** `d4eb9e9d`
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
plan reconciliation and C1 Git integration are complete. Product remediation
is checkpointed at `2ff5a42a`, closeout truth at `fbd24350`, and automation
commit `f812eb3f` is integrated at `d4eb9e9d` without history rewriting or
lost work.

C2 source/live product UAT is complete. Focused Python/FastAPI/React suites
passed, and live Vite-to-FastAPI checks agreed with the source-tree outcomes.
The UAT found one main-process defect: local development proxied `/api` and
`/ws` but not the React batch EventSource `/stream` path. The Vite proxy now
forwards `/stream` to FastAPI. A safe plus unsafe-shear batch then rendered one
PASS/one FAIL, and applying results left the unsafe beam pending.

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
- C2 focused matrix: pure-library/service cases green; 58 FastAPI cases green;
  16 focused React cases green; Node 24 production build green.
- C2 live evidence: safe/unsafe SSE `PASS`/`FAIL`, 1 passed/1 failed in React,
  unsafe beam not applied, standard live 422 envelope, and successful live
  column, footing and one-way-slab responses.
- C2 export bytes: BBS 959 bytes (`c34cb245...f8067`), DXF 48,522 bytes
  (`037a879e...0134`), and unsafe HTML report 8,725 bytes
  (`1524c1ab...7f8a`).

The wheel was disposable and removed after inspection. A stale source-tree
`Python/build/lib` was proven to contaminate an ordinary build with excluded
migration/research/ACI/EC2 files; the release gate now rejects that content.

## Next actions

1. Run the canonical v0.23.0 release preflight once on the clean current
   candidate.
2. Remove only stale ignored `Python/build`/`Python/dist` artifacts through the
   maintained safe-delete workflow, then build one exact wheel and sdist.
3. Record local filenames, sizes, SHA-256 values, inventories, allowlist and
   protected-content results, SBOM, and exact-wheel clean-install/CLI UAT.
4. Continue only after C3 passes: C4 evidence freeze, then final qualified
   review. Publication remains separately gated.

## Terminal issues recorded

- A contract test initially depended on `PYTHONPATH=Python:.`; it is now
  repository-root stable under `./run.sh test`.
- `tool_registry.py --validate` is not a supported flag; the maintained
  `check_scripts_index.py`, script-reference gate, and full check were used.
- An unmatched zsh release-doc glob failed before execution; explicit paths
  and `git diff --name-only | rg` worked.
- zsh reserves `status`; the deliberate release-failure proof used `rc`.
- Assigning to zsh-reserved `path` removed command lookup during Git
  classification; rerunning with `file_path` restored normal execution.
- The automation finder had no exact C2 mapping; the maintained UAT,
  release-preflight and quality-gate skills plus exact test paths were used.
- An unmatched `scripts/dev.*` zsh glob failed before inspection; `rg --files
  scripts | rg 'dev|server'` found the maintained launcher safely.
- A first hidden-input file chooser timed out; the visible labelled CSV drop
  zone opened the documented chooser and imported the fixture successfully.
- `rg` was given the nonexistent `react_app/src/pages` path; the live route
  files under `react_app/src/components/pages` were used instead.
- The first C2 commit attempt crossed the local date boundary and the session
  hook correctly rejected the missing 2026-08-10 durable entry; the session
  log and generated indexes were refreshed before retrying.
