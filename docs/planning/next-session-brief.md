# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: execute the owner-authorized v0.23.0 Alpha release after completed C0-C4 closeout
<!-- HANDOFF:END -->

**Current branch:** `codex/release-v0.23.0`
**Frozen artifact source:** `9be6eb35`
**Plan:** [is456-library-first-master-plan.md](is456-library-first-master-plan.md)

## Required Reading

- [IS 456 library-first master plan](is456-library-first-master-plan.md)
- [Professional remediation evidence ledger](professional-library-remediation-plan.md)
- [Current task board](../TASKS.md)

| Release state | Version | Decision |
|---|---|---|
| **Current** | v0.23.0 | Alpha release authorized; exact CI artifact and publication pending |
| **Next** | v0.24.0 | Future roadmap only; inactive pending separate owner activation |

## Outcome

T0 and R1-R8 are implemented; do not repeat them. The owner selected the
bounded IS 456 product milestone, not the v0.24/v1.0 multi-code roadmap. C0
plan reconciliation and C1 Git integration are complete. Product remediation
is checkpointed at `2ff5a42a`, closeout truth at `fbd24350`, and automation
commit `f812eb3f` is integrated at `d4eb9e9d` without history rewriting or
lost work.

C0-C4 are complete on draft PR #696. C2 source/live product UAT repaired the
missing Vite `/stream` proxy and proved one PASS/one FAIL with the unsafe beam
left unchanged. C3 froze the exact local v0.23.0 wheel/sdist from source commit
`9be6eb35` after fixing stale egg-info package leakage at the manifest boundary.
C4 froze the bounded source, unit, benchmark, limitation, unsafe-case, claim and
artifact evidence requested by the owner.

The owner moved qualified structural-engineering review to the final
stable/engineering-use gate on 2026-08-10. Development packets and Alpha
publication no longer require separate qualified sign-off. Every candidate
remains development software and cannot claim professional approval; its
source, benchmark, units, unsafe cases and limitations accumulate for the final
review.

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
- `MANIFEST.in` now prunes every non-product namespace so stale generated
  egg-info cannot override the package allowlist.
- The release-preflight skill distinguishes a future-version positional check
  from an already-bumped current candidate verified with `--wheel`.

## Verification evidence

- Source candidate preflight: 5,452 passed, 3 skipped, 6 deselected.
- FastAPI: 349 passed.
- React: 147 passed; lint and production build passed on Node 24.
- Quick gate: 9/9; full gate: 29/29.
- Readiness audit: 19/19; health: 100/100; parity: 93%.
- API manifest: 73/73 compatible functions.
- OpenAPI: 62 endpoints, 65 schemas, no drift.
- Exact local wheel: 478,970 bytes, 181 members, zero excluded namespaces,
  clean import/CLI passed, SHA-256 `08377c11...2d8875`.
- Exact local sdist: 398,319 bytes, 206 members, zero excluded namespaces,
  SHA-256 `f3c6da86...4cbac3`.
- Exact-wheel UAT: 5,404 passed, 51 skipped, 6 deselected plus job, critical
  and report CLI workflows. Candidate preflight: 5,452 passed, 3 skipped,
  6 deselected, clean install and React build green, zero preflight warnings.
- Local CycloneDX 1.6 SBOM: 196 components, 239,585 bytes, SHA-256
  `810b1be2...9f0eb7`; CI must regenerate its own release evidence.
- C2 focused matrix: pure-library/service cases green; 58 FastAPI cases green;
  16 focused React cases green; Node 24 production build green.
- C2 live evidence: safe/unsafe SSE `PASS`/`FAIL`, 1 passed/1 failed in React,
  unsafe beam not applied, standard live 422 envelope, and successful live
  column, footing and one-way-slab responses.
- C2 export bytes: BBS 959 bytes (`c34cb245...f8067`), DXF 48,522 bytes
  (`037a879e...0134`), and unsafe HTML report 8,725 bytes
  (`1524c1ab...7f8a`).

The exact local artifacts remain ignored under `Python/dist/` for owner review.
They are prepublication evidence, not the CI publication identity.

## Next actions

1. Merge PR #696 after its current-commit PR Gate passes.
2. Run the protected CI/TestPyPI rehearsal and capture the exact CI-built wheel,
   sdist, inventories, hashes, SBOM and clean-install UAT.
3. If that evidence is green, create v0.23.0 and let the tag-only workflow
   publish to PyPI and GitHub Releases; then run exact-version PyPI UAT.
4. Retain accumulated engineering evidence for qualified review before any
   stable or engineering-use approval.

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
- The positional `release preflight 0.23.0` form rejected the already-bumped
  equal version; the corrected current-candidate form supplied the exact wheel
  and passed with no warnings.
- A fresh `Python/build`/`Python/dist` cleanup did not remove stale ignored egg-
  info, which reintroduced excluded namespaces; generated metadata was moved to
  Trash, explicit manifest prunes were added, and the final build passed.
- The first archive inventory snippet used an illegal backslash inside an
  f-string expression; an intermediate boolean produced the intended read-only
  evidence on the retry.
- The archived `check_doc_metadata.py` entrypoint no longer exists and a custom
  front-matter status was outside the validated enum; `check_docs.py --metadata`
  and `--frontmatter` were used, with machine status kept `active` while the
  visible plan status records bounded closeout complete.
- ⚠️ TERMINAL ISSUE: unsupported `check_links.py --modified` and broad index rewrites → the full link check passed and only generated cache diffs were reversed.
