# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: UIX-001 Session 1 P0-P8 accepted; prepare fresh Session 2 P9 packet
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Branch:** codex/ui-quick-design-p4

**Base:** origin/main at c10ac736
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | UIX-001 P9 | Start the capability catalogue on a fresh Session 2 branch from updated main |
| **Next** | UIX-001 P10 | Expose the accepted catalogue through the thin API contract |
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

## Session 1 accepted closeout

Master-plan section 22 now accepts P0-P8. Quick design is latest-request-wins;
imported projects preserve stable source identity; batch evidence, dashboard,
BOQ, and export are revision bound; and the decomposed viewport provides
selection, filtering, fit/isolate, truthful status/utilization, deterministic
camera behavior, and non-WebGL inspection.

The final live pass fixed three coupled root causes. Large EventSource GET URLs
hit HTTP 431 at the maintained 153-member sample, so large batches now stream
from a JSON-body POST. Project navigation now follows durable workspace stage
truth instead of route position, and results/dashboard reload restores the
workspace without downgrading it to review. The live sample settles 153/153 PASS,
reloads the dashboard and BOQ, and produces a current-revision CSV.

Closeout evidence: 222 React tests, 374 FastAPI tests, React lint/build,
`./run.sh frontend check`, quick 10/10, and the integrated full gate pass.
Chromium production UAT passed 1440/1024/390 px, context loss/recovery, five
resource-stable route cycles, and an interactive 1,530-member fixture. Safari
desktop smoke passed; exact responsive authority remains Chromium. No GitHub
Pages, release, tag, package publication, or professional-use action occurred.

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
