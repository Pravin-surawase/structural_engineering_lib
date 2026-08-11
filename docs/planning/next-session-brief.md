# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-11
- Focus: SPARK-001 master plan ready for owner review; implementation remains paused
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Branch:** `codex/gpt-5-3-spark-work-program`

**Base:** clean `main` at `a0e115e17009cc14b3d883e3c291d47c32f7ca4e`
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | SPARK-001 planning | Isolated branch and worker-ready 70-packet program prepared |
| **Next** | Owner review gate G0 | Accept, revise, or reject Wave 0; do not begin implementation before acceptance |
| **Held** | Stable/engineering use | Requires cumulative qualified structural-engineering review |

## Required Reading

- [GPT-5.3-Codex-Spark work program](gpt-5-3-codex-spark-work-program.md)
- [AI token-efficiency policy](../guidelines/ai-token-efficiency.md)
- [UI experience foundation master plan](ui-experience-foundation-master-plan.md)
- [Session 2 acceptance](../verification/ui-experience-session-2-acceptance.md)
- [Current task board](../TASKS.md)
- [Release policy](../getting-started/releases.md)

## SPARK-001 planning state

- The isolated program branch was created from clean `main`; no product or
  calculation implementation was started.
- The plan records verified preview properties, current usage/pricing uncertainty,
  protected structural and security areas, active worktree ownership, mandatory
  tests, escalation triggers, cost-learning fields, and independent review gates.
- Seventy bounded packets are organized into eight waves covering control-plane
  calibration, documentation truth, automation contracts, API examples, bounded
  React behavior, runnable examples, verification operations, and post-merge
  integration.
- Wave 0 remains unauthorized until the repository owner accepts or revises the
  plan. Acceptance of G0 authorizes only the specifically approved first wave.

## Fresh-start maintenance closeout

- Local `main` is synchronized to the merged UIX result.
- Five clean disposable `/private/tmp` worktrees were removed while their branches
  were retained; two named external worktrees were preserved for their owners.
- No server is listening on the maintained frontend/backend ports, no stash was
  present, and the stale-branch dry run found nothing eligible for deletion.
- Five API/router counts and all 32 generated indexes are synchronized. Index
  drift detection now includes child-folder projections rather than direct files
  only.
- Generated build/test/type/lint/coverage and bytecode caches were cleaned while
  environments, dependencies, logs, benchmarks, recovery backups, and user state
  were preserved.
- Health is 100/100, token-efficiency passes, the quick gate is 10/10, the full
  gate is 30/30, and the root checkout is the fresh baseline for the next
  owner-selected packet.

## Accepted UIX outcome

Session 1 delivered revision-safe quick/project results, durable project identity,
revision-bound exports, and authoritative 3D inspection. Session 2 delivered one
immutable beam catalogue, thin discovery API, curated schema renderer, one
default-disabled bounded workflow, one generated provider-neutral beam manifest,
canonical workbench routes, and integrated live acceptance.

The final live pass fixed three main-process causes:

- React Strict Mode cancelled the initial quick-design effect while a one-shot
  ref prevented its replacement; the hook now retains the current runner.
- Catalogue inputs were rendered beside the legacy input surface; catalogue and
  manual modes now have mutually exclusive ownership.
- Project route guards redirected before IndexedDB hydration began; idle/loading
  are now explicit restore states.

The bundled sample settles 153/153 PASS and restores canonical results directly.
Safe, unsafe, stale/recalculate, export, bounded workflow, legacy redirects,
390/1024/1440 px, and WebGL interruption flows pass in maintained Chromium.

## Verification

- 91 focused Python/FastAPI tests, 87 focused React tests, and 76 focused
  geometry/streaming tests pass.
- React/API signature scan matches 29 maintained call sites.
- `./run.sh frontend check` passes lint, 239 tests, and production build.
- `./run.sh check --quick` passes 10/10 and the final integrated gate passes
  30/30; pull-request checks remain the merge authority.

## Holds

- Workflow execution remains unavailable by default and is enabled only through
  explicit development/test flags.
- Firefox, exact Safari responsive automation, GitHub Pages, public workflow
  activation, release/tag/package publication, and professional-use claims are
  not part of UIX acceptance.
- Production JWT secret provisioning remains an owner operation.
- PR #711 remains superseded; PR #683 belongs to a coordinated ESLint 10
  migration; PR #684 remains blocked on a coordinated Vite 8 migration.

## Repeat-prevention record

Every session must record observed issue, confirmed root cause, resolution, and
verification in the newest `docs/SESSION_LOG.md` block. Shared `AGENTS.md` and
agent templates enforce that schema, and session closeout validates the newest
entry only. Log terminal/tool failures with the maintained command or evidence
path that succeeded; do not treat an observer limitation as a product failure.
