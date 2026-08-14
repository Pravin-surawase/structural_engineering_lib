---
owner: Main Agent
status: active
last_updated: 2026-08-13
doc_type: reference
task: GIT-001
phase: 5
implementation_authorized: false
---

# GIT-001 Phase 5 — Scenario and Feasibility Validation

## Validation boundary

Phase 5 tests whether the proposed operating model is grounded in observable
Git/GitHub behavior and whether every implementation packet has a falsifiable
acceptance scenario. It does not pretend that proposed code or server settings
already exist.

Results use four labels:

- `PASS-EXISTING` — a current control already satisfies the required outcome;
- `PASS-PRIMITIVE` — read-only Git/GitHub primitives expose the evidence the
  design needs;
- `FAIL-CURRENT` — the current control reproduces an outcome gap and the future
  packet must reverse it;
- `PACKET-GATE` — executable proof is defined and remains mandatory before that
  implementation packet can integrate.

Disposable Git mutations occurred only under
`/tmp/git-001-phase5.jV1xK1`. No project branch, ref, index, worktree, setting,
PR, check, or release state was changed by the simulations.

## Scenario matrix

| ID | Scenario | Expected operating-model result | Evidence | Result |
|---|---|---|---|---|
| S01 | Clean attached feature lane | `READY_LOCAL`, with head/base/upstream/publication facts separate | Live research lane and porcelain-v2 observation | PASS-PRIMITIVE |
| S02 | Dirty owned/unowned lane | `HOLD_DIRTY` until ownership and preservation are explicit | Live research task brief reported four dirty paths | PASS-PRIMITIVE; packet must add staged/unstaged/untracked classes |
| S03 | Detached HEAD | `HOLD_DETACHED`, nonzero strict guard | Disposable detached worktree; current guard warned and exited 0 | FAIL-CURRENT; GIT-7B gate |
| S04 | Active merge in linked worktree | `HOLD_OPERATION` from real worktree Git path | Disposable two-parent merge stopped before commit | FAIL-CURRENT; GIT-7B gate |
| S05 | Diverged histories | `HOLD_DIVERGED` with correctly named left/right counts | Disposable branches returned `1 1` | PASS-PRIMITIVE; GIT-7B gate |
| S06 | Git query failure/unknown | `HOLD_UNKNOWN`, never clean/ready | Existing session-trust regression rejects unknown/failed Git commands | PASS-EXISTING; kernel must preserve it |
| S07 | Sibling worktree observation | Bounded, optional-lock, per-lane result; timeout becomes unknown | `GIT_OPTIONAL_LOCKS=0 status --porcelain=v2 --branch` succeeded in linked worktree | PASS-PRIMITIVE; GIT-7B timing/timeout gate |
| S08 | Targeted generated-data preview | One owned folder, no write, exact proposed paths | Underlying generator dry-run processed 1/1 and status was unchanged | PASS-EXISTING primitive; preferred CLI routing remains GIT-7D |
| S09 | Unexpected all-folder generated drift | Stop on unowned changes; no implicit acceptance | Phase 2 records 23-28 unrelated generated paths | FAIL-CURRENT default; GIT-7D gate |
| S10 | Old/squash-equivalent cleanup candidate | Hold for PR/patch/tree/ownership evidence; no deletion | GIT-001 and PMM receipts reproduce ancestry ambiguity | PASS-PRIMITIVE; current deletion-capable classifier fails GIT-7D design |
| S11 | Control-plane code changes | Exact maintained outcome tests become required PR dependencies | Static workflow review shows current script path lacks those tests | FAIL-CURRENT; GIT-7C gate |
| S12 | Documentation build failure/cancellation | Exact-head strict build blocks required aggregator | Live ruleset/workflow inspection shows docs build is separate and non-required | FAIL-CURRENT; GIT-7C gate |
| S13 | Direct main/bypass path | Server refuses integration outside PR-required exact-head gate | Live ruleset lacks PR rule and has always-bypass actor | FAIL-CURRENT; owner-approved GIT-7C gate |
| S14 | Task-to-task handoff | Durable receipt names local/remote/PR/check/retention identities or explicit unknowns | Phase 1 proves product contract unresolved; current prose has exact facts but no schema | PASS-PRIMITIVE; GIT-7E gate |
| S15 | Fast local intake | Current lane <=0.50 s; six lanes <=2.0 s; no network | Six-worktree `task brief` completed in 0.26 s | PASS-PRIMITIVE; proposed kernel budget feasible |
| S16 | Fast local quick Git classification | <=0.50 s and no remote/large-file work | Current validator took 4.05 s because it mixes optional diagnostics | FAIL-CURRENT; GIT-7B gate |

## Disposable Git scenario receipt

### Repository construction

The disposable repository used one empty base commit, two branches with one
independent empty commit each, an attached linked worktree for `left`, and a
detached linked worktree for `right`. Empty commits were sufficient to create a
real diverged graph and a no-content two-parent merge stopped before commit;
no shell-created fixture file was required.

### Directional divergence

```text
DIVERGENCE_LEFT_RIGHT=1 1
```

The result proves the kernel can label unique commits directionally without
parsing `git status` prose. The current validator's corresponding human labels
are reversed in its divergence branch, so GIT-7B must test both directions.

### Linked-worktree operation state

```text
LINKED_GIT_DIR=/private/tmp/git-001-phase5.jV1xK1/repo/.git/worktrees/left-wt
LINKED_MERGE_PATH=/private/tmp/git-001-phase5.jV1xK1/repo/.git/worktrees/left-wt/MERGE_HEAD
LITERAL_MARKER=false
GIT_PATH_MARKER=true
CURRENT_MERGE_GUARD_EXIT=0
```

The merge was genuinely active: `git merge --no-commit --no-ff right` reported
that the automatic merge succeeded and stopped before committing. The literal
`.git/MERGE_HEAD` path did not exist because `.git` is a linked-worktree pointer
file. `git rev-parse --git-path MERGE_HEAD` resolved the actual marker. Both the
current unfinished-merge guard and the comprehensive validator exited zero; the
latter printed `No unfinished merge` and `Working tree clean`.

This reproduces G3-03 as an outcome defect, not a theoretical hardening gap.

### Detached HEAD

The disposable detached worktree returned an empty branch name. The current
branch guard printed:

```text
WARNING: detached HEAD. Commit on a branch to avoid losing work.
```

and exited zero. GIT-7B must return `HOLD_DETACHED` and nonzero in strict guard
mode while preserving read-only diagnostic output.

### Optional-lock observation

`GIT_OPTIONAL_LOCKS=0 git status --porcelain=v2 --branch` completed from the
linked merge worktree and reported the attached branch/head without changing
the operation. This validates the proposed non-locking observation primitive.

## Live project read-only receipt

### State and intake

- `main` was clean and exact with `origin/main` at `f3ad94dc`.
- Six attached worktrees were present; all were clean before this phase's
  task-owned documents were written.
- The GIT-001 lane was clean and exact with its upstream at `51a8a57a` before a
  normal merge of current main produced `845c3fa9`; its tree remained identical
  to main at the synchronization checkpoint.
- With four task-owned dirty paths, task brief reported the correct dirty count
  and all six worktrees but used upstream head `51a8a57a` as `base`, omitted the
  lane's `+2/-0` upstream relation, and did not report operation/PR/check state.
- Six-worktree task brief completed in 0.26 seconds.
- Current comprehensive Git validation took 4.05 seconds and included network
  and large-file work.

### Generator scope

The maintained Python generator accepted exactly
`docs/research/git-governance --dry-run`, reported one target folder and the two
index files it would generate, and left `git status --porcelain=v1` byte-for-byte
unchanged. The capability is sound; only the preferred `run.sh` contract and
scope guard remain to design/implement in GIT-7D.

### GitHub and CI

- Ruleset `main_branch_rule1` is active and strictly requires `PR Gate`, blocks
  deletion and non-fast-forward updates, lacks a pull-request rule, and exposes
  an always-bypass role to the current owner.
- The repository allows merge, squash, and rebase methods.
- The latest 30 workflow runs inspected were successful; recent PR/docs runs
  usually completed in roughly 34-90 seconds.
- Static workflow review confirmed changed scripts do not run the maintained
  session/task/runtime outcome tests in required CI.
- Strict MkDocs build is separate from the required aggregator and uses one
  globally cancelling concurrency key.

These checks validate the Phase 4 design direction while preserving the current
fast-path baseline as a regression target.

## Packet acceptance scenarios

### GIT-7B — state and intake kernel

Must automate at least:

1. clean attached branch;
2. main branch;
3. detached HEAD;
4. staged, unstaged, untracked, and conflicted paths independently;
5. merge, rebase, cherry-pick, revert, and bisect markers in a normal checkout;
6. the same operation markers in a linked worktree;
7. index lock and query timeout/error;
8. no upstream, ahead, behind, and diverged upstream;
9. default-base relation separate from upstream relation;
10. sibling dirty/timeout state with optional locks disabled;
11. no Git/network mutation under filesystem/ref before-and-after comparison;
12. current/six-worktree performance budgets.

Zero abnormal scenario may return `READY_LOCAL`.

### GIT-7C — CI and server enforcement

Use a disposable or draft test PR to prove:

1. control-plane change runs the exact state/intake tests;
2. changed control-plane test file runs its family;
3. docs change runs strict MkDocs build as an applicable `PR Gate` dependency;
4. failure, cancellation, timeout, or unexpected skip fails `PR Gate`;
5. superseding the same PR head cancels only the old run for that PR;
6. direct main update is rejected by a PR rule;
7. merge cannot bypass failed/pending required checks;
8. squash and merge-commit receipts record expected reviewed/resulting SHAs;
9. before/after ruleset JSON matches the approved delta exactly.

No setting changes before corresponding workflow code is green on main.

### GIT-7D — generated data and disposition

Must prove:

1. no-argument preferred generator is non-writing help;
2. one folder dry-run and write affect only expected maintained paths;
3. `--all` is explicit and previews the full target set;
4. unexpected new index topology fails without opt-in;
5. branch classifier performs no fetch/prune/delete or GitHub mutation;
6. Git command error becomes `UNKNOWN`, never merged/stale;
7. age alone never produces retirement-ready;
8. attached, dirty, open-PR, unique-commit, squash-equivalent, and retained-
   evidence branches receive distinct dispositions;
9. deletion-capable flag/path is absent after migration.

### GIT-7E — guidance and handoff

Must prove:

1. every live indexed instruction rejects retired command/flag fixtures;
2. archive/historical material is excluded only when clearly labeled;
3. branch/head/upstream/base/tree/operation receipt survives session handoff;
4. remote/PR/check fields are exact or explicitly unknown;
5. transcript/task archive state is never represented as Git retention proof;
6. aliases resolve maintained commands without permitting obsolete mutations.

## Phase 5 result

The disposable and live read-only evidence did not disprove any Phase 4 design
assumption. It reproduced the current linked-worktree merge and detached-HEAD
misclassifications, confirmed every required state primitive is available,
proved targeted dry-run generation and fast multi-worktree intake are feasible,
and converted every packet into measurable pass/fail scenarios.

Phase 5 is complete for proposal validation. It does not claim that GIT-7B–7E
pass their implementation gates. Those gates remain mandatory inside their
authorized packets.
