# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-12
- Focus: SPARK-001 published through PR #734 for G0 review; Wave 0 remains held
<!-- HANDOFF:END -->

**Current release:** `v0.23.1a1` Alpha
**Branch:** `codex/gpt-5-3-spark-work-program`
**Integration base:** `origin/main` at `8d47de73`; immutable Alpha tag `v0.23.1a1` remains unchanged
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | SPARK-001 Phase 3 | PR #734 carries the preserved plan, integrated `main`, picker fix, and green local gates |
| **Next** | Owner review gate G0 | Accept, revise, or reject Wave 0 after the reconciled control plane passes verification |
| **Held** | Stable/engineering-use claims | Alpha publication does not grant qualified professional approval or complete-code coverage |

## Integrated footing scope

- The maintained scope is one concentric square/rectangular isolated-footing
  workflow with explicit service and factored actions, external allowable-soil-
  pressure approval, and approved A1 load-transfer evidence.
- Overall thickness and effective depth remain distinct; flexure, directional
  one-way shear, punching shear, bearing, and uniform-depth selection are
  fail-closed.
- Optional two-layer bottom-reinforcement detailing returns physical directional
  depths, bar schedules, rectangular central/outer-band zones, anchorage evidence
  and linked dowels. Missing or unsupported inputs remain visible HOLDs.
- The release inclusion receipt binds 15 footing-owned file hashes and six
  cross-layer markers; verify it after the complete merge before any PR action.

## Public-distribution permission

- The repository owner confirmed source/licensing permission on 2026-08-11 for
  approved-scope normalized IS 456 data. The canonical record is
  [`is456-public-distribution-permission.json`](../verification/is456-public-distribution-permission.json);
  release preflight, candidate checks, and publish CI validate it fail closed.
- The private corpus remains private, protected prose/images remain excluded,
  and each release still needs separate owner authorization. Do not report this
  gate as pending unless the owner explicitly changes the recorded decision.

## Required Reading

- [GPT-5.3-Codex-Spark work program](gpt-5-3-codex-spark-work-program.md)
- [AI token-efficiency policy](../guidelines/ai-token-efficiency.md)
- [IS 456 solid slabs master plan](is456-solid-slabs-master-plan.md)
- [IS 456 library-first evidence](../verification/is456-library-first-evidence.md)
- [UI experience foundation master plan](ui-experience-foundation-master-plan.md)
- [Session 2 acceptance](../verification/ui-experience-session-2-acceptance.md)
- [Current task board](../TASKS.md)
- [Release policy](../getting-started/releases.md)

## SPARK-001 planning state

- Draft PR #734 publishes the recovered work program and picker fix for review;
  publication alone does not authorize any execution wave.
- The original draft was preserved at checkpoint `47fce48e` before integrating
  current `origin/main` through merge commit `f0314f3e`; no product or calculation
  implementation was started and no history was rewritten.
- The plan records verified preview properties, current usage/pricing uncertainty,
  protected structural and security areas, active worktree ownership, mandatory
  tests, escalation triggers, cost-learning fields, and independent review gates.
- Seventy bounded packets are organized into eight waves covering control-plane
  calibration, documentation truth, automation contracts, API examples, bounded
  React behavior, runnable examples, verification operations, and post-merge
  integration.
- Wave 0 remains unauthorized until the repository owner accepts or revises the
  plan. Acceptance of G0 authorizes only the specifically approved first wave.
- The recovered control plane now treats Spark as an unpriced preview, exercises
  the real model-table CLI, and keeps ambiguous/high-risk work on Terra with
  approval-gated Sol escalation.

## IS456-SLAB-001 implementation outcome

- Existing compatibility slab functions remain available; the implementation
  extends the maintained slab package rather than creating another engine.
- Built-in Tables 12/13 and Tables 26/27 resolution is implemented with exact
  provenance, bounded adjacent interpolation and explicit extrapolation errors.
  External coefficient providers remain available with distinct trust status.
- Oriented physical edges drive common two-way cases, strip widths and full/
  half/none/free corner-torsion dispositions without silent span rotation.
- Complete bounded routes cover provided bars, minimum/maximum detailing,
  reviewed span/depth serviceability and ordinary one-way shear. Direct
  deflection, automatic shear reinforcement and irregular/concentrated-load
  panels remain held.
- Five new FastAPI routes and the `/workbench/slabs` React flow are live-verified.
  Results preserve revision identity and stale results cannot be exported.
- Flat slabs, drops, column strips, slab-column transfer and column-supported
  punching remain under a separately approved FS0 extension.

### Verification at handoff

- 5,532 Python tests passed, 3 skipped and 6 deselected.
- 388 FastAPI tests and 241 React tests passed.
- Frontend lint/test/TypeScript/production build passed.
- Quick gate 10/10 and integrated gate 30/30 passed.
- Live continuous and B04 two-way flows passed without browser console errors;
  stale passport export was blocked as designed.

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
