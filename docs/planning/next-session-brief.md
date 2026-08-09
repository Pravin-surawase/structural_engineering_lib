# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: ADOPT-001 Packet A complete; canonical capability discovery is next
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` at `3f880d5b`
**Maintenance baseline:** `22bc8a45`
**Task board:** [TASKS.md](../TASKS.md)

## Required Reading

- [Current task board](../TASKS.md)
- [Adoption and trust surface plan](adoption-trust-surface-plan.md)
- [IS 456 library-first master plan](is456-library-first-master-plan.md)
- [Release evidence crosswalk](../verification/is456-library-first-evidence.md)

| State | Target | Decision |
|---|---|---|
| **Current** | v0.23.0 Alpha | Released; public artifact UAT and current-main Weekly Verification are green |
| **Next** | ADOPT-001 | Packet A is committed; implement Packet B from the existing capability source |
| **Queued** | DEPS-MAINT-001 | Keep dependency triage separate from the trust-surface branch |

## Current outcome

- Created `codex/trust-surface-foundation` from clean merged `main` at
  `44e85587`; Packet A is committed at `88bca3c1`.
- Added the durable dependency-ordered ADOPT-001 plan with protected calculation
  paths, non-goals, packet files/commands, acceptance, rollback, and owner-only
  actions.
- Repaired the rejected public column example, incorrect aggregate status
  guidance, wrong REST request fields, stale health versions, and missing REST
  response envelope.
- Replaced the long stale REST response inventory with one executable beam
  contract, an explicit envelope/error boundary, endpoint families, and the live
  OpenAPI source of truth.
- Added three focused regressions for the documented Python column workflow,
  REST beam request/access path, health versions, and known stale guide strings.
- Focused tests, Ruff, Black, OpenAPI compatibility, 1,067 internal links, and
  the repository quick gate pass.
- The generated SDK templates were confirmed to be stale against the envelope
  and are now truthfully marked development-only until Packet C fixes their
  generator and typed schemas together.
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

Implement ADOPT-001 Packet B without widening the engineering scope:

1. Add one explicit JSON serialization contract to the existing frozen
   capability dataclasses.
2. Expose the same capability IDs and supported/held cases through Python, CLI
   JSON, and a typed REST route.
3. Refresh `llms.txt` from that truth and add focused semantic-equivalence tests.
4. Do not edit IS 456 calculation modules, generated clients, or production auth
   in Packet B. Those remain separate Packets C and D.
5. Keep dependency PR triage queued on a separate branch/session.

## GitHub state

- Open issues: 0.
- Open PRs: nine Dependabot PRs (#679-#684 and #686-#688).
- Green but still compatibility-sensitive: #679, #681-#683, and #688.
- Currently failing their relevant lane: #680, #684, #686, and #687.

## Terminal issues recorded

- `scripts/check_links.py --fail-fast` is no longer a supported invocation;
  `scripts/check_links.py --exclude-archive` completed with zero broken links.
- `./run.sh generate indexes` refreshed many unrelated stale folder indexes.
  The exact generator-created spillover was inspected and restored; only the
  changed planning/reference indexes were retained. Prefer direct targeted
  `generate_enhanced_index.py <folder>` for later packets.
- The first Packet A commit stopped because the end-of-file hook repaired two
  generated JSON files. Restaging only those scoped files made the retry pass.
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
