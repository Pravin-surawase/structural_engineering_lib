---
owner: Main Agent
status: active
last_updated: 2026-08-13
doc_type: reference
task: GIT-001
phase: 7B
owner_decision: accepted-2026-08-13
implementation_authorized: GIT-7B-only
---

# GIT-001 Phase 7B — Read-Only State and Intake Kernel

## Authorization and boundary

The repository owner accepted Phase 6 and authorized GIT-7B on 2026-08-13.
This packet implements only the read-only Git state authority, task intake,
session trust, quick-gate consumption, focused outcome tests, and the narrow
policy/CI routing required to keep those controls live.

GIT-7C through GIT-7E remain held. No GitHub setting, cleanup classifier,
generator contract, branch/worktree deletion, release, automatic recovery, or
product runtime was changed.

## Lane and preservation receipt

- Refreshed primary `main` and `origin/main` were exact at `f3ad94dc` before the
  implementation worktree was created.
- The fresh lane is `codex/git-7b-state-kernel` at
  `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-7b-state-kernel`.
- The approved proposal commit was replayed as `a879c28b` before implementation.
- The research lane remained clean and separate. No existing worktree, branch,
  ref, stash, GitHub object, or user-owned change was rewritten or removed.
- Worktree-bound Python diagnosis returned `source_bound=true` for the fresh
  lane.

## Implemented authority

`scripts/git_state.py` is the sole semantic source for local Git state. It:

- reads porcelain-v2 branch/index/tree evidence;
- resolves real worktree Git paths and the shared common directory;
- distinguishes default-base and upstream reachability with correctly named
  ahead/behind counts;
- identifies staged, modified, untracked, conflicted, operation, lock,
  detached, no-upstream, behind, diverged, and unknown states;
- emits typed JSON plus concise human output;
- sets `GIT_OPTIONAL_LOCKS=0` and `GIT_TERMINAL_PROMPT=0` for every Git query;
- performs no fetch or other network request and reports
  `remote_freshness=NOT_CHECKED`;
- returns `READY_LOCAL` or one explicit `HOLD_*` action without a recovery
  command.

Task brief, session start/trust/checkpoint state, and the quick Git checks now
consume this authority. The three former shell classifiers are thin kernel
delegates. The pre-commit compatibility entrypoint continues to allow a
classified conflict-free operation commit to complete while blocking unknown,
locked, or conflicted state.

## Focused CI contract

`fast-checks.yml` now identifies the GIT-7B control-plane paths. When any of
those paths changes, Repository Validation runs exactly:

```text
python -m pytest Python/tests/test_git_state.py Python/tests/test_session_automation.py -q
```

The existing `PR Gate` still requires Repository Validation. No server ruleset
or merge setting changed in this packet.

## Scenario evidence

The focused suite covers the twelve Phase 5 acceptance families:

1. clean feature, main, and detached states;
2. independent staged, modified, untracked, and conflicted classification;
3. merge, rebase, cherry-pick, revert, and bisect markers;
4. the same markers under real linked-worktree Git administration paths;
5. index lock preservation;
6. command timeout/error becoming `HOLD_UNKNOWN`;
7. no-upstream, ahead, behind, and diverged directionality;
8. default-base and upstream independence;
9. sibling dirty and unknown classification;
10. optional-lock and terminal-prompt disabling;
11. unchanged refs/status/index timestamp after kernel inspection;
12. current and six-worktree performance budgets.

Current focused result: 64 tests passed. Live current-worktree classification
was approximately 80 ms. A live seven-worktree inventory completed in 556 ms
with zero unknown lanes, below the two-second six-worktree budget.

## Issues encountered

- The accepted file list omitted three active legacy shell entrypoints and the
  existing pre-commit argument required to preserve operation completion; their
  old form would have retained split authority or blocked legitimate closeout.
- The first non-mutation test checked the index timestamp after its own ordinary
  `git status`, which refreshed the index and produced one false failure.
- The first worktree-creation command used the not-yet-created directory as the
  process working directory and could not start.
- The first live PR run correctly selected the new control-plane tests, but
  Repository Validation failed before collection because its environment did
  not contain Hypothesis.

## Root causes and resolutions

- Root cause: the proposal named consumers but not their compatibility files.
  Resolution: enumerate all live callers, amend the accepted packet before
  editing, and restrict the three shell files to kernel delegation. Evidence:
  the semantic workflow checker now rejects independent shell classification.
- Root cause: the test's final diagnostic did not set optional locks and ran
  before the timestamp assertion. Resolution: assert the timestamp immediately
  after kernel collection, then compare status. Evidence: the complete focused
  family passed.
- Root cause: process startup resolves `cwd` before running the command that
  would create it. Resolution: create the worktree from the existing research
  lane, then run lane commands from the validated new path. Evidence:
  `git worktree list` and Python diagnosis identify the expected lane.
- Root cause: Repository Validation installed the base package, pytest, and
  PyYAML even after it began running tests whose shared configuration imports
  Hypothesis from the existing `dev` extra. Resolution: install `Python/[dev]`
  in that job. Evidence: the focused suite and semantic workflow check pass
  against the corrected contract; PR #744 provides the live exact-head run.

## Closeout gate

- Focused state/intake tests: 64 passed.
- Expanded state/session/governance automation family: 109 passed.
- Black, Ruff, and MyPy: passed.
- Strict documentation, link, task, brief, session, script-index, semantic
  workflow, JSON, YAML, and shell-syntax checks: passed.
- Quick repository gate: 10/10 in 2.9 seconds; its two Git checks completed in
  292 ms.
- Full repository gate: 30/30 in 8.8 seconds; all four Git checks completed in
  365 ms.
- Live seven-worktree inventory: 556 ms, zero unknown lanes.

GIT-7B was published for review as draft PR #744 after explicit owner approval.
GIT-7C through GIT-7E remain held.
