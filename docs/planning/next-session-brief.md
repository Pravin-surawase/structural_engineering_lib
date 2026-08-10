# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: UIX-001 Session 1 Wave 1 P2/P3 foundations active
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Branch:** codex/ui-workbench-session-1

**Base:** origin/main at 32b9f33b
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | UIX-001 Session 1 Wave 1 | Implement P2 shell/primitives and P3 revisioned workspace/persistence boundaries |
| **Next** | UIX-001 P4 handoff | Start quick migration only after parent acceptance of P2/P3 contracts |
| **Held** | Stable/engineering use | Requires cumulative qualified structural-engineering review |

## Required Reading

- [UI experience foundation master plan](ui-experience-foundation-master-plan.md)
- [Current task board](../TASKS.md)
- [Adoption and trust surface plan](adoption-trust-surface-plan.md)
- [Bundled sample BOQ evidence](../verification/bundled-sample-boq-evidence.md)
- [Release policy](../getting-started/releases.md)

## Completed foundation

- ADOPT-001 Packets A-G merged through PR #707. Public examples, capability
  discovery, typed API contracts, production auth fail-close, evidence identity,
  React/BOQ trust presentation, and Alpha/docs policy are on `main`.
- Python compatibility PR #708 merged Ruff 0.16.1, PyArrow 25, WebSockets 17,
  Python 3.11-safe scientific pins, and retirement of Streamlit dependencies and
  hooks.
- React compatibility PR #709 merged the compatible #680-#682 updates and fixed
  all three strict hook-effect violations while retaining ESLint 9 and Vite 7.
- Governance PR #710 allows Codex to merge an unchanged, in-scope reviewed head
  after required checks pass and conflicts/blockers are clear.
- Dependabot guard PR #712 prevents Python 3.12-only NumPy/SciPy proposals and
  incompatible standalone `pydantic-core` locks while Python 3.11 remains the
  maintained runtime.
- No GitHub Pages deployment or release action was performed.

## Session 1 Wave 1

Wave 0 is accepted in master-plan section 22. It froze the route map, three-width
wireframes, quantitative simplification targets, IndexedDB project persistence,
revision-bound result/export lifecycle, one AbortSignal-aware React transport
facade, GeometrySpaceV1, essential 3D layers, and the browser/scene baselines.

1. **Parent:** own typed routes/navigation, WorkspaceSnapshotV1, result/request
   identity, persistence/migrations, status/export truth, and shared integration.
2. **Frontend flow:** implement only the approved visual tokens, repeated
   primitives, and shell presentation against parent-owned contracts.
3. **3D foundation:** implement GeometrySpaceV1 contract/golden fixture and return
   the decomposition map; no P8 layers yet.
4. **Checkpoint:** accept P2/P3, stale/out-of-order negatives, reload/recovery,
   narrow-shell reachability, and the 3D fixture before the P4 follow-up.

## Open dependency holds

- PR #711 is superseded by #708/#712 and still fails because it requests NumPy
  2.5.1 and SciPy 1.18 on Python 3.11.
- PR #683 remains a coordinated ESLint 10 migration, not a standalone update.
- PR #684 remains blocked until a coordinated Vite 8 migration.
- Keep all dependency work outside UIX-001.

## Operational holds

- Provisioning and management of the real production JWT secret remains an owner
  operation.
- Tags, package publication, GitHub Releases, issue/PR closure, branch deletion,
  and professional-use claims retain their existing approval boundaries.
- GitHub Pages remains disabled.

## Terminal issues recorded

- The first Dependabot guard assertion assumed three configured ecosystems; the
  repository has four. Selecting pip entries by ecosystem and directory passed
  fail-fast validation.
- Updating the old UIX branch from current `main` produced documentation-only
  conflicts in `TASKS.md`, the planning indexes, and this briefing. Resolution
  retained the accepted UIX plan and current merged dependency/adoption evidence.
- During Wave 0 another task merged the planning branch and switched the shared
  root checkout. Work resumed only after PR #718 reached main and the dedicated
  codex/ui-workbench-session-1 branch was created. Parallel tasks must use
  separate worktrees and must never switch this checkout.
- The optional agent-browser CLI was unavailable, so the maintained in-app
  Chromium browser was used for the live three-width baseline.
- The archived `scripts/generate_folder_index.py` path was replaced by the
  maintained targeted `scripts/generate_enhanced_index.py` command.
