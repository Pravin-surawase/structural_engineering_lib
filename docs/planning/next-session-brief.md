# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: UIX-001 Session 1 Wave 0 active; implementation remains contract-gated
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Branch:** `codex/ui-experience-foundation`

**Base:** `origin/main` at `fa0ee995`
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | UIX-001 Session 1 Wave 0 | Run the parent baseline and two read-only audits, then freeze shared contracts |
| **Next** | UIX-001 Session 1 Waves 1-2 | Begin implementation only after the Wave 0 contract lock passes |
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

## Session 1 Wave 0

1. **Parent:** capture the live landing, sample, quick-design, import/project,
   result, and export journeys; classify exposed/dormant features; confirm the
   route/IA target; produce three-width wireframes and measurable baselines.
2. **Application-truth audit:** reconcile React clients/hooks/stores with current
   FastAPI/OpenAPI shapes; map revisions, latest-request-wins behavior, storage,
   status truth, and export truth. Evidence only; no edits.
3. **3D/browser audit:** freeze source/canonical/renderer axes, units, member IDs,
   and schema versions; capture browser, bundle, scene, fallback, and performance
   evidence. Evidence only; no edits.
4. **Checkpoint:** freeze the route model, workspace/result revision contract,
   API-client approach, storage decision inputs, authoritative 3D contract,
   essential layer list, owned paths, and P0/P1 acceptance ledger before Wave 1.

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
- The archived `scripts/generate_folder_index.py` path was replaced by the
  maintained targeted `scripts/generate_enhanced_index.py` command.
