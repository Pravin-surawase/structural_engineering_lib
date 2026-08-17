# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: exact v0.23.1a2 release-candidate hosted review, without tag or publication
- Candidate branch: `codex/release-0231a2`; base `970a78c1931a3aa0439f487e6892a888bb113962`
- Build anchor: `c71e4e27749a9da58fe0d689bc1a1ba8b396f14d`; Python tree `501fac1360f06ff2be4f6aea3b5e167f956ce840`
- Exact wheel: `structural_lib_is456-0.23.1a2-py3-none-any.whl`; SHA-256 `5bca57ba12a35803715ad581420fa6ea5be32a0cd736fd42246b9a026584cc19`
- Local evidence: 5,553 installed tests pass; 29/29 release UAT cases and 12/12 advertised commands pass
- Evidence record: `docs/verification/alpha-0231a2-local-prepublication-rehearsal.md`
- Git handoff receipt: `docs/verification/release-0231a2-preparation-git-handoff-receipt.json`
- Release state: `CANDIDATE_TECHNICALLY_READY` locally and `PUBLICATION_HOLD`; tag, uploads, GitHub Release, and professional approval remain unauthorized
- Whole-building workflow: Packet H remains inactive; component-only claims remain
- Exact next action: freeze the final documentation-only descendant, push one release PR, run required PR checks and exact-head Weekly Verification, then obtain independent exact-candidate review
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` remains public; exact v0.23.1a2 source and wheel are locally prepared and verified |
| **Next** | One release PR, required hosted checks, exact-head Weekly Verification, and independent review |
| **Held** | TestPyPI/PyPI upload, tag, GitHub Release, professional approval, Packet H, dependency work, and retained-lane cleanup |

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

## Candidate evidence and next gate

- Reuse the exact local rehearsal record; do not rebuild or rerun green local
  suites while the Python tree remains `501fac1360f06ff2be4f6aea3b5e167f956ce840`.
- Push the final candidate once and open one release PR against `main`.
- Require PR Validation and manually dispatched Weekly Verification on the
  same final head, followed by independent review of that exact head/tree.
- If Python content changes, the wheel evidence expires. A documentation-only
  repair may retain the wheel only after proving the Python tree is unchanged.
- After review, add only the version-specific review receipt, authorization
  JSON, and validator-permitted indexes. Do not pre-check publication approval.
- Stop for direct owner authorization before any TestPyPI/PyPI upload, tag, or
  GitHub Release. No current evidence grants professional approval.
