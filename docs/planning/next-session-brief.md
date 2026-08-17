# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: exact technical-acceptance artifact steps 3 and 4 after LIB-PRO-002 I-J
- Integrated predecessor: Packet I merged through PR #819 at `0ba2f397aec267bc74a31281f9158189fde2749d`
- Packet J outcome: hosted full suites bind the setup-python interpreter; preflight verdicts are mode-accurate and publication remains fail-closed
- Git handoff receipt: `docs/verification/lib-pro-002-j-hosted-repair-git-handoff-receipt.json`
- Focused Packet J evidence: 103 workflow/release/environment tests pass
- Release state: `PUBLICATION_HOLD`; no version bump, tag, upload, GitHub Release, or professional approval exists
- Whole-building workflow: Packet H remains inactive; component-only claims remain
- Exact next action: perform release-preflight steps 3 and 4 only—build one temporary exact technical-acceptance wheel from synchronized `main`, then clean-install and verify that same artifact
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; Packets A-G and I-J correct current source, not the already-published old artifact |
| **Next** | One temporary technical-acceptance wheel plus source-free clean-install/UAT evidence from unchanged synchronized `main` |
| **Held** | Version bump, tag, TestPyPI/PyPI upload, GitHub Release, professional approval, Packet H, dependency work, and retained-lane cleanup |

## Required Reading

1. [Active readiness plan](pre-release-input-safety-and-professional-readiness-plan.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
4. [Publication authorization record](../verification/release-publication-authorization.json)
5. [Exact-candidate review template](../verification/exact-candidate-review-receipt-template.json)

## Resume safely

Start from the primary checkout. Fetch first, inspect every worktree and open
task-owned PR, and require clean synchronized `main` plus `source_bound=true`.
Do not reuse Packet I/J worktrees, disturb retained detached/dirty lanes, or
assume this handoff's Git state is still current.

```bash
./run.sh session brief --agent ops
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Stop before mutation if `main` is behind/diverged/dirty, an operation marker is
present, or another candidate overlaps packaging, verification, indexes, or
release guidance. Preserve unknown state; never reset, stash, clean, rebase, or
delete it as recovery.

## Step 3 — build the exact technical-acceptance artifact

- Confirm Packet J's PR checks and exact-head Weekly Verification passed, and
  verify synchronized `main` has the same accepted tree before building.
- Use a new clean temporary output directory; do not reuse `Python/dist` or any
  historical artifact.
- Build exactly one wheel from unchanged synchronized `main` and record source
  head, source tree, Python tree, filename, size, and SHA-256.
- Verify wheel filename, METADATA version, contents, protected-source boundary,
  advertised-entrypoint inventory, and source/library content identity.
- Treat this as technical evidence for current source only. Because current
  source still says `0.23.1a1`, the wheel must never replace or be confused with
  the already-published `0.23.1a1` artifact.
- Do not bump a version, write release notes, tag, upload, or authorize a target.

## Step 4 — clean-install and verify the same artifact

- Create a source-free temporary virtual environment and remove repository
  `PYTHONPATH`/`VIRTUAL_ENV` inheritance.
- Install the exact recorded wheel, then prove `structural_lib.__file__` comes
  from that environment rather than the checkout.
- Run expanded exact-wheel UAT and public examples, including all 29 declared
  negative/positive cases and the 12-command advertised-entrypoint inventory.
- Run the exact-wheel candidate check and preflight against the same path. The
  expected successful technical verdict is `CANDIDATE_TECHNICALLY_READY` plus
  `PUBLICATION_HOLD`, not `READY_TO_PUBLISH`.
- Record the clean-install interpreter, imported version/origin, matrix hash,
  case count, public-example result, wheel hash, and all remaining holds.
- A failed or mismatched case is `NOT_READY`; do not repair by weakening the
  launcher, UAT, artifact identity, review, hosted, or authorization controls.

## Acceptance and stop rules

Step 3 accepts only one exact, source-bound wheel with a recorded SHA-256 and
no excluded/protected content. Step 4 accepts only source-free installation of
that same hash with all entrypoint/UAT/public-example checks passing.

Even after both steps pass, publication remains held. A later separately
authorized release-preparation task must select and bump the next Alpha
version, rebuild the final versioned artifact, repeat exact review and hosted
gates, and obtain explicit target authorization. Do not publish, tag, create a
GitHub Release, claim professional approval, activate Packet H, close work, or
delete branches/worktrees in this technical-acceptance session.
