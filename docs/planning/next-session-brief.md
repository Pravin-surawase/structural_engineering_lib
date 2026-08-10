# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: UIX-001 Session 1 Wave 0 active; implementation edits remain contract-gated
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` at `3f880d5b`
**Maintenance baseline:** `22bc8a45`
**Task board:** [TASKS.md](../TASKS.md)

## Required Reading

- [Current task board](../TASKS.md)
- [UI experience foundation master plan](ui-experience-foundation-master-plan.md)
- [IS 456 library-first master plan](is456-library-first-master-plan.md)
- [Release evidence crosswalk](../verification/is456-library-first-evidence.md)

| State | Target | Decision |
|---|---|---|
| **Current** | v0.23.0 Alpha | Released; public artifact UAT and current-main Weekly Verification are green |
| **Active work** | UIX-001 Session 1 Wave 0 | Run parent plus two Terra read-only audits and freeze shared contracts |
| **Next** | UIX-001 Session 1 Wave 1 | Starts only after the Wave 0 contract lock is accepted |

## Closed outcome

- Merged automation recovery PR #695 and GitHub Actions runtime PR #692.
- Repaired the real Weekly Verification typing failure through PR #699 and the
  final NumPy `<2.5` compatibility constraint in PR #700.
- Exact current-main Weekly Verification run `31334828353` passed wheel/CLI,
  locked audits, Docker health, Python, FastAPI, repository drift, and React.
- Closed stale PR #548 and all 129 historical `Nightly QA failed` issues after
  the current-main workflow passed; GitHub now has zero open issues.
- Removed verified merged release/automation branches, their linked worktree,
  and the superseded orphan `task/TASK-DOCSYNC` branch. Remote non-Dependabot
  branches are now only `main` and `gh-pages`.
- Moved 22 generated release/build artifacts (5.6 MB) out of the repository to
  recoverable staging at `/private/tmp/structural-lib-maint-20260810.sLuHRf`.
- Project health, audit readiness, and efficiency baselines were 100/100,
  19/19, and PASS before this handoff.

## Retained release boundary

The v0.23.0 Alpha remains a case-qualified development preview, not a
whole-standard or professional-approval claim. Retain the accumulated source,
benchmark, unit, unsafe-case, limitation, and exact-artifact evidence for one
cumulative qualified structural-engineering review before any stable or
engineering-use approval.

## Next action

1. Continue Session 1 Wave 0 on `codex/ui-experience-foundation`: parent
   journey/IA baseline, Terra application/API/state audit, and Terra 3D/browser
   audit. Freeze contracts before Wave 1 implementation.
2. Respect external worktree locks: do not edit AGENTS.md; do not edit React
   package manifests, ImportView, or BuildingEditorPage until their parallel
   branches are owner-merged and this branch is updated normally.
3. Keep DEPS-MAINT-001 separate and queued. Do not mix dependency upgrades into
   the UI branch.

## GitHub state

- Open issues: 0.
- Open PRs: nine Dependabot PRs (#679-#684 and #686-#688).
- Green but still compatibility-sensitive: #679, #681-#683, and #688.
- Currently failing their relevant lane: #680, #684, #686, and #687.

## Terminal issues recorded

- The documented active path `scripts/generate_folder_index.py` no longer exists;
  it is archived. `.venv/bin/python scripts/generate_enhanced_index.py
  docs/planning` is the current targeted replacement and completed successfully.

- Finder Trash staging was denied by macOS privacy controls and
  `/usr/bin/realpath` is absent. `.venv/bin/python` path resolution plus an
  explicit `/private/tmp` recoverable staging directory worked.
- The first exact Weekly dispatch was cancelled when `main` changed during the
  Actions update. The next run exposed Mypy/NumPy stub incompatibility.
- PR #699 correctly constrained Mypy but did not constrain the unpinned NumPy
  install surface. CI logs proved NumPy 2.5.2 was the remaining root cause; PR
  #700 fixed that boundary, and the exact current-main rerun passed.
- A zsh unmatched-glob lookup for `Python/requirements*.txt` was replaced by
  an `rg --files` lookup.
- Newly merged squash commits required an explicit fetch before local tree-ID
  comparison. Branch cleanup was performed only after equal trees were proven.
