---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: GIT-001
phase: 7C1
owner_decision: authorized-draft-publication-2026-08-14
implementation_authorized: GIT-7C1-workflow-only
---

# GIT-001 Phase 7C1 — Required CI Topology

## Authorization and boundary

After GIT-7B merged through PR #744, the repository owner authorized the next
planned workflow packet for publication as a draft PR on 2026-08-14. This
packet changes repository workflow code and its regression evidence only.

No GitHub ruleset, bypass actor, merge method, branch-deletion setting, release,
cleanup, recovery, product runtime, or professional-approval boundary is
changed. Those GitHub server settings remain the separately gated GIT-7C2
packet and may be considered only after this workflow code is green on `main`.

## Lane and preservation receipt

- Primary `main` and `origin/main` were clean and exact at `0fdb48ed`, the
  GIT-7B squash result, before the implementation lane was created.
- The fresh lane is `codex/git-7c-ci-enforcement` at
  `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-7c-ci-enforcement`.
- Worktree-bound Python diagnosis returned `source_bound=true`.
- The retained GIT-7B worktree and every other existing lane were left
  untouched. No branch, worktree, stash, ref, GitHub object, or unknown change
  was deleted, rewritten, reset, cleaned, or stashed.

## Implemented topology

| Route | Applies when | Required outcome |
|---|---|---|
| `control-plane-validation` | Scripts, `run.sh`, agent/session controls, registries, Git workflow policy, workflow definitions, or their maintained tests change | Semantic workflow checker and the exact Git, intake, session, persistence, pipeline, governance, and CI-contract regression families pass |
| `documentation-validation` | `docs/**`, `mkdocs.yml`, package metadata, or package source used by generated API docs changes | `mkdocs build --strict` passes at the same PR head |
| `repository-validation` | Every PR | Existing repository policy and maintenance checks pass |
| `PR Gate` | Every PR | Change detection, repository validation, and every applicable component, control-plane, and documentation route conclude `success` |

`PR Gate` rejects failed, cancelled, timed-out or otherwise non-successful
applicable jobs. It also rejects an applicable job that is unexpectedly skipped
and a non-applicable job that unexpectedly runs, so routing cannot silently
degrade into false-green evidence.

## Cancellation and duplicate-work control

- PR Validation remains grouped by workflow and pull-request number. A newer
  head cancels only the older run for that same PR; unrelated PRs have distinct
  groups.
- The separate documentation workflow no longer runs on pull requests. It is
  retained for `main` pushes and manual build evidence only, grouped by ref
  instead of the former repository-wide `deploy-docs` group.
- Strict documentation validation therefore runs once in the required PR
  topology instead of once as required evidence and again as a non-required,
  globally cancelling signal.

## Regression contract

`Python/tests/test_ci_workflow_contract.py` parses the maintained workflow and
executes the real inline `PR Gate` shell program against a result matrix. It
proves:

1. scripts, agent/session controls, Git workflow policy, documentation inputs,
   and every selected regression file route to the intended jobs;
2. control-plane and documentation jobs are direct `PR Gate` dependencies;
3. strict MkDocs is the documentation job's outcome;
4. successful applicable control-plane and documentation routes pass;
5. `failure`, `cancelled`, `skipped`, and an unexpected timeout-like result all
   fail when the route is applicable;
6. unexpected execution fails when a route is non-applicable; and
7. PR and post-merge documentation concurrency groups are scoped to their PR
   or ref rather than shared globally.

The existing semantic checker independently enforces the same required routes,
runtime binding, test files, and removal of the globally cancelling docs PR
workflow.

## Issue and root-cause evidence

The newly required agent-governance family initially failed before this packet
changed its behavior. Its workflow assertion still searched for
`python -m pip install -e Python pytest PyYAML`, while GIT-7B had correctly
changed Repository Validation to install `Python/[dev]` so the shared test
configuration could import Hypothesis.

Git history confirmed the assertion originated in `0d01fa1f` and the install
contract changed in the GIT-7B squash result `0fdb48ed`. The test had not been
part of the prior focused workflow route, so the stale assertion did not block
that PR. This packet updates the assertion to inspect the Repository Validation
job's actual supported dependency contract and includes the entire maintained
family in the required control-plane route.

The first required session-end check also reported that today's completed entry
was absent and not newest. The canonical session-log header had been embedded
after older entries, so session start inserted the new skeleton in the middle
while session end inspected the file's leading dated block and bounded prefix.
This packet restores only the canonical header and today's task-owned entry to
newest-first position, preserving the text and order of all historical entries.
The handoff and session-completeness checks then pass; the overall session-end
command remains intentionally nonzero until the intended worktree changes are
committed.

The first commit attempt then stopped at the Python-version consistency hook.
The documentation job had carried Python 3.12 from the standalone workflow into
`fast-checks.yml`, where the repository contract requires its project-minimum
Python 3.11. The integrated job now uses 3.11, and the CI topology regression
test enforces that version so later edits cannot reintroduce the mismatch.

## Scenario status

| GIT-7C scenario | Status in this packet |
|---|---|
| Control-plane change runs exact maintained regressions | Implemented and locally proved; draft PR is the live route proof |
| Changed control-plane test file runs its family | Implemented; the new CI-contract test is itself an explicit route input |
| Docs change runs strict MkDocs as a `PR Gate` dependency | Implemented and locally proved; this receipt is a docs change |
| Failure, cancellation, timeout, or unexpected skip fails `PR Gate` | Proved by executable result-matrix tests |
| Same-PR supersession cancels only the old run | Static contract proved; live draft-PR evidence to be recorded after publication |
| Direct main update is rejected | Held for GIT-7C2 server settings |
| Merge cannot bypass failed or pending checks | Held for GIT-7C2 server settings |
| Merge-method exact-SHA receipts | Held for GIT-7C2 integration receipt |
| Before/after ruleset JSON matches approved delta | Held for GIT-7C2 owner authorization |

## Local verification

- New fail-closed CI contract: 13 tests passed.
- Maintained Git/intake/session/persistence/pipeline/governance family: 160
  tests passed.
- Combined control-plane route: 173 tests passed.
- Semantic Codex-native workflow checker: passed.
- Black, Ruff, YAML parsing, and `git diff --check`: passed.
- `mkdocs build --strict`: passed in 8.1 seconds.
- `./run.sh check --quick`: 10/10 passed in 2.7 seconds.
- `./run.sh check`: 30/30 passed in 9.7 seconds.
- Exact-head draft-PR checks remain the live publication gate.

## Next gate

Completed 2026-08-15: PR #745 passed every applicable job and `PR Gate` at
reviewed head `c3edd247`, then squash-merged as `729cc41b` with an identical
tree. Both post-merge main workflows passed. The separately authorized GIT-7C2
delta is recorded in
[`GIT-001-phase-7C2-server-enforcement.md`](GIT-001-phase-7C2-server-enforcement.md).
