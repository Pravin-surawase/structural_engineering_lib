# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-12
- Focus: COLUMN-PMM-001 candidate complete; GIT-001 Phase 1 continues
<!-- HANDOFF:END -->

**Current release:** `v0.23.1a1` Alpha
**Branch:** `codex/column-pmm-completion`
**Integration base:** `origin/main` at `b069428b`; immutable Alpha tag `v0.23.1a1` remains unchanged
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | COLUMN-PMM-001 | Review and integrate the independently benchmarked experimental PMM candidate without stable API exposure |
| **Next** | GIT-001 Phase 2 | Forensic incident study only after the Phase 1 coverage review passes |
| **Held** | Broad policy implementation and remote cleanup | Historical refs stay preserved; PMM production/public support remains a separately approved contract |

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

- [GIT-001 research index](../research/git-governance/GIT-001-README.md)
- [AI token-efficiency policy](../guidelines/ai-token-efficiency.md)
- [IS 456 solid slabs master plan](is456-solid-slabs-master-plan.md)
- [IS 456 library-first evidence](../verification/is456-library-first-evidence.md)
- [UI experience foundation master plan](ui-experience-foundation-master-plan.md)
- [Session 2 acceptance](../verification/ui-experience-session-2-acceptance.md)
- [Current task board](../TASKS.md)
- [Release policy](../getting-started/releases.md)

## GIT-001 research state

- Dedicated `codex/git-governance-research` worktree was created from refreshed
  `origin/main` at `6bc356c3`; primary `main` remains clean and synchronized.
- Phase 0 records eight clean worktrees, sixteen local branches, eight open PRs,
  the active main ruleset, no stashes, protected unique work, and explicit unknowns.
- Column PMM is remotely preserved, recovered onto current `main`, and checked
  against an independent closed-form oblique benchmark. It remains experimental.
  PR #723 is closed after its bounded replacement merged via #736.
- Phase 1 has begun with official Git, GitHub, and OpenAI sources. Research facts,
  project observations, proposed decisions, and normative policy stay separate.
- Existing conflicting Git guides and retired-wrapper learning text are Phase 2
  evidence candidates, not early rewrite targets.
- Integrated packet 7A restores lane-safe intake and index-runtime behavior;
  canonical policy, GitHub settings, broad cleanup, and release remain held.
- SPARK-001 remains integrated at PR #734, but Wave 0 stays behind owner gate G0.

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
