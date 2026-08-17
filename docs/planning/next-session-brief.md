# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: complete refreshed exact review and publish the authorized v0.23.1a2 Alpha candidate
- Candidate branch: `codex/release-0231a2`; base `970a78c1931a3aa0439f487e6892a888bb113962`
- Build anchor: `a115b16efbb85db0459c79836f55b6c43a586470`; Python tree `25aa0468135c07d3c260eca43776fb451865f833`
- Exact wheel: `structural_lib_is456-0.23.1a2-py3-none-any.whl`; SHA-256 `34892d867845d044249236f32b700ab5e10ec558225407a47717fe3c3c2614bb`
- Local evidence: 5,553 installed tests pass; 29/29 release UAT cases and 12/12 advertised commands pass
- Evidence record: `docs/verification/alpha-0231a2-local-prepublication-rehearsal.md`
- Git handoff receipt: `docs/verification/release-0231a2-preparation-git-handoff-receipt.json`
- Release state: `CANDIDATE_TECHNICALLY_READY` locally and `PUBLICATION_HOLD`; target publication is owner-authorized after refreshed exact review, while professional approval remains unauthorized
- Whole-building workflow: Packet H remains inactive; component-only claims remain
- Exact next action: freeze and push the repaired candidate, pass required PR checks and exact-head Weekly Verification, obtain refreshed independent review, then execute the authorized publication sequence
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` remains public; exact v0.23.1a2 source and wheel are locally prepared and verified |
| **Next** | Required hosted checks, exact-head Weekly Verification, independent review, TestPyPI, merge, tag, PyPI, and GitHub prerelease |
| **Held** | Publication until refreshed review passes; professional approval, Packet H, dependency work, and retained-lane cleanup remain held |

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

- Reuse the refreshed exact local rehearsal record; do not rebuild or rerun
  green local suites while the Python tree remains
  `25aa0468135c07d3c260eca43776fb451865f833`.
- Push the final candidate once and open one release PR against `main`.
- Require PR Validation and manually dispatched Weekly Verification on the
  same final head, followed by independent review of that exact head/tree.
- If Python content changes, the wheel evidence expires. A documentation-only
  repair may retain the wheel only after proving the Python tree is unchanged.
- Target authorization is already recorded. After refreshed review, update only
  its version-specific receipt, authorization binding, and validator-permitted
  indexes.
- Target-specific owner authorization is recorded for TestPyPI, PyPI, and the
  GitHub Release after refreshed review passes. No current evidence grants
  professional approval.
