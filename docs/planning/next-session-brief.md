# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-10
- Focus: IS456-SLAB-001 master plan complete; start only the S0 source, coefficient-policy, and benchmark gate
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Planning branch:** `codex/is456-slabs-plan`

**Base:** clean `main` at `a0e115e1`; slab calculation implementation has not started
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | IS456-SLAB-001 planning | Deep solid-slab scope, architecture, benchmarks, pitfalls, API/UI sequence, and flat-slab HOLD are recorded |
| **Next** | IS456-SLAB-S0 | Freeze controlled source pages, coefficient shipping/interpolation policy, physical support-case IDs, and independent B02/B04 benchmarks before code |
| **Held** | Stable/engineering use | Requires cumulative qualified structural-engineering review |

## Required Reading

- [IS 456 solid slabs master plan](is456-solid-slabs-master-plan.md)
- [IS 456 library-first evidence](../verification/is456-library-first-evidence.md)
- [UI experience foundation master plan](ui-experience-foundation-master-plan.md)
- [Session 2 acceptance](../verification/ui-experience-session-2-acceptance.md)
- [Current task board](../TASKS.md)
- [Release policy](../getting-started/releases.md)

## IS456-SLAB-001 planning outcome

- Extend the existing slab package; do not create a second engine. The current
  simply supported one-way and external-coefficient interior two-way routes stay
  compatible.
- Add oriented physical edge/corner topology before coefficient work; the
  existing axis-neutral span normalization is unsafe once edges are attached.
- Sequence continuous one-way actions/completion before a two-adjacent-edge
  two-way vertical slice that exercises built-in/external coefficient trust,
  strips, torsion, serviceability, and shear.
- Separate coefficient-provider architecture from protected table data. No
  built-in values ship until S0 records source/licensing permission and the
  exact-match/interpolation decision.
- Treat SP 16 only as withdrawn legacy comparison evidence; primary IS 456
  formulas and controlled current sources govern.
- Keep punching explicitly not applicable/unsupported for the initial
  beam/wall-supported UDL panels. Do not reuse the footing punching workflow.
- Keep flat slabs, drops, column strips, slab-column transfer, and flat-slab
  punching under a separately approved FS0 extension.

### First packet — S0 only

Return an approved source-page map, coefficient packaging decision, support-case
IDs/transforms, interpolation policy, characteristic/factored/service-load
contract, independent B02/B04 calculations and tolerances, remaining HOLDs, and
explicit authorization for S1. Do not edit calculation, public API, FastAPI, or
React code in S0.

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
