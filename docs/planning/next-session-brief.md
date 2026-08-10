# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: UIX-001 Session 1 P2/P3 accepted; P4 quick-design migration ready
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Branch:** codex/ui-workbench-session-1

**Base:** origin/main at 32b9f33b
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | UIX-001 P4 | Migrate quick design onto the accepted workbench and latest-request-wins contracts |
| **Next** | UIX-001 P5/P6 | Connect project intake, design, results, and export to durable revision truth |
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

## Session 1 Wave 1 checkpoint

Wave 0 and the P2/P3 foundation checkpoint are accepted in master-plan section
22. P2 provides the live two-destination shell, typed four-stage project
navigation, restrained landing route, responsive reachability, and lazy heavy
visualization delivery. P3 provides WorkspaceSnapshotV1, exact revision-bound
evidence, fail-closed migration, atomic IndexedDB persistence and recovery,
undo/revert invalidation, autosave, and multi-tab conflict detection. The
AbortSignal-aware REST facade and two-frame GeometrySpaceV1 fixture are also in
place.

1. **P4:** connect quick design to the accepted latest-request coordinator and
   workspace lifecycle; cancelled, delayed, and edit-stale responses must not
   become current or exportable.
2. **P5/P6:** remain out of the P4 packet. Imported-project resume and complete
   project result/export parity are not yet accepted.
3. **P7:** the frame fixture is ready; viewport decomposition remains separate.
4. **Checkpoint evidence:** 197 React tests, lint, production build, and the
   canonical quick gate pass. Chromium UAT passed at 1440, 1024, and 390 px and
   proved real IndexedDB save/reload/delete plus BroadcastChannel conflict
   notification without leaving synthetic data.

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
- The in-app browser does not support `networkidle`; `domcontentloaded` plus an
  explicit meaningful-element wait produced the repeatable live timings.
- The first 3D source inspection used the obsolete `services/geometry_3d.py`
  assumption; targeted file discovery found the maintained module at
  `Python/structural_lib/visualization/geometry_3d.py`.
- The archived `scripts/generate_folder_index.py` path was replaced by the
  maintained targeted `scripts/generate_enhanced_index.py` command.
