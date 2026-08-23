---
owner: Main Agent
status: active
last_updated: 2026-08-12
doc_type: guide
complexity: intermediate
tags: [git, worktree, recovery, scripts, learning]
---

# Git recovery case study: Column PMM

## Why this case matters

COLUMN-PMM-001 began as valuable unpublished engineering work on a stale branch.
It could not safely be treated as either disposable or ready to merge. The
successful path separated five questions that are easy to confuse:

1. Is the work unique and recoverable?
2. Is its Git base current?
3. Is its engineering evidence sufficient?
4. Which files express the useful intent?
5. When is local cleanup safe?

This case is reusable for any old feature lane whose intent is valuable but
whose history, tests, or public boundary no longer match current `main`.

## Starting evidence and decision

The historical branch `codex/column-pmm-experimental` pointed to `8a52ed0f`.
Its single large commit touched 36 files and was based on stale repository
history. The work was clean and unique, but its PMM tests compared primarily
against another repository solver rather than an independent oblique benchmark.

The disposition was therefore:

| Question | Decision | Reason |
|---|---|---|
| Delete the lane? | No | Unique unpublished calculation work existed. |
| Merge the old branch? | No | Its base and public/API assumptions were stale. |
| Cherry-pick the large commit? | No | It mixed the useful kernel with unrelated and premature surfaces. |
| Rebase it? | No | Rewriting did not solve evidence or scope problems. |
| Preserve it remotely? | Yes | Exact commit identity remained recoverable. |
| Recover onto current `main`? | Yes | A fresh lane gave current contracts and clean review scope. |

## Branch and worktree are different tools

A branch is a movable name for a commit. A worktree is a checked-out directory
with its own files, index, `HEAD`, and in-progress-operation state.

For this recovery, both were needed:

- branch `codex/column-pmm-completion` recorded the candidate history;
- worktree `structural_engineering_lib-column-pmm-completion` isolated its files
  from clean `main` and the active GIT-001 research lane.

Creating only a branch in the primary folder would have required switching
`main` away from its integration role. Creating only a folder would not have
provided an independent Git index or branch history.

The creation order also matters. The process working directory must already
exist, so run `git worktree add` from an existing checkout. Only afterward can a
command use the new worktree as its current directory.

## Recovery graph

```text
historical PMM 8a52ed0f  ── preserved on origin
                               │ selective intent recovery
current main b069428b ── completion lane ── a481d1ab
                                               │ PR #738 squash
main ───────────────────────────────────────── 402bf22c
                                               │ post-merge receipt
main ───────────────────────────────────────── d106ff59
```

Because PR #738 was squash-merged, `8a52ed0f` and `a481d1ab` are not ancestors
of the final `main`. Their intended content is integrated under the new commit
`402bf22c`. Cleanup therefore used PR, tree, tests, and remote-ref evidence—not
ancestry alone.

## The execution sequence

### 1. Inspect before mutation

```bash
./run.sh task brief "recover and benchmark experimental column PMM"
git status --short --branch
git worktree list --porcelain
git fetch origin main
```

`task brief` is read-only. It answers which lane is active, whether it is dirty,
which upstream/base is visible, and which worktrees already exist. Fetch updates
remote-tracking knowledge; it does not merge anything into the current branch.

### 2. Preserve before interpreting

The exact historical commit was pushed without rewriting it. Preservation made
later selection safe: rejecting files from the candidate no longer risked
destroying the only copy of the work.

### 3. Start from current main

The completion worktree was created at the verified `main` commit. The old
36-file commit was used as evidence, not applied as a unit. Only the generalized
reinforcement types, pure IS 456 PMM module, focused tests, and benchmark record
were recovered.

### 4. Prove runtime identity

```bash
./scripts/python_runtime.sh --diagnose
```

Linked worktrees may borrow the primary checkout's Python executable, but the
launcher prepends the invoking worktree's `Python/` source. Accept evidence only
when `source_bound` is `true` and the reported module path belongs to the lane.

### 5. Close the evidence gap

Passing comparisons against the existing uniaxial implementation were useful
regressions but not an independent benchmark. A closed-form 45-degree concrete
integral plus exact discrete-bar calculation supplied an independent expected
`Pu`, signed `Mx`, and signed `My`.

This is both a software and Git lesson: preserve first, but do not confuse a
preserved commit with an accepted feature.

### 6. Validate scripts as evidence producers

The focused quality command initially scanned every IS 456 module because it
matched `pmm` in the absolute worktree directory name. The fix compared against
the path relative to the IS 456 source root and added a PMM-named-parent
regression. A focused command is valid evidence only when it actually focuses.

### 7. Publish at one immutable head

Focused tests, the full Python suite, quick/full repository gates, and commit
hooks passed before publication. PR #738 was merged only after its head remained
`a481d1ab`, required checks passed, and GitHub reported CLEAN and MERGEABLE.

### 8. Record post-merge truth separately

The feature commit could truthfully say “candidate ready,” but could not contain
its own future merge receipt. A small documentation-only PR recorded the exact
merge commit and moved the task to completed state without changing engineering
code after review.

### 9. Clean up from exact evidence

Before removal, each PMM worktree was proven clean and each exact head was
verified on `origin`. The three local worktrees and local branch names were then
removed. Remote refs were retained as audit and recovery evidence.

## Script behavior learned in this session

| Tool | Mode | Question or action | Important boundary |
|---|---|---|---|
| `./run.sh task brief` | Read-only | What lane, base, route, and worktrees exist? | Does not fetch, branch, or edit. |
| `git worktree add -b` | Git mutation | Create an isolated branch and checkout. | Run from an existing directory; verify collisions first. |
| `python_runtime.sh --diagnose` | Read-only | Which source tree will Python import? | Interpreter location alone is insufficient. |
| `check_function_quality.py --module` | Read-only | Do selected IS 456 functions meet the static contract? | Selection must use repository-relative paths. It is not a numerical proof. |
| `./run.sh context` | Read-only | Validate routing and summarize live files on demand. | Generic committed folder indexes are retired. |
| `safe_file_delete.py` | Destructive workspace write | Delete one validated unreferenced file with a content-hashed backup. | Generic names such as `index.json` can produce broad matches; every maintained match must be resolved because no force bypass exists. |
| `./run.sh check --quick` | Read-only validation | Is the candidate safe for a reviewed commit? | Does not replace focused engineering tests. |
| `./run.sh check` | Read-only validation | Does the complete repository contract pass? | Run once after the candidate is stable. |
| GitHub required checks | Remote validation | Did CI pass at the published head? | Recheck if the head or base changes. |

## Context recurrence control

The original generator would create `index.json` and `index.md` in any requested
folder. During PMM work, targeting nested test directories created six new files
where the repository had no maintained index convention.

The maintained behavior is now read-only and on demand:

```bash
./run.sh context validate
./run.sh context show automation
./run.sh context summary path/to/folder
```

These commands read the live worktree and create no index files, eliminating the
accidental nested-index side effect that this case originally exposed.

## Issues, root causes, and reusable solutions

| Symptom | Root cause | Reusable solution |
|---|---|---|
| Command could not start in the future worktree | Its process directory did not exist yet | Create from an existing checkout, then enter the lane. |
| Passing old tests did not justify integration | Comparator was another repository solver | Require an independently derived benchmark for new engineering math. |
| Oblique benchmark moment symmetry drifted | Rectangular fiber mesh broke square x/y numerical symmetry | Match mesh topology to benchmark symmetry, then tighten by convergence. |
| Focused checker scanned 69 functions | Absolute path included `pmm` in worktree name | Filter on source-root-relative module paths and regression-test named parents. |
| Test command stopped before collection | Paths were guessed from memory | Discover maintained paths with `rg --files` before invoking tests. |
| Six unwanted index files appeared | Writer was targeted at folders without index ownership | Use live `./run.sh context summary`; do not regenerate folder indexes. |
| Safe deletion reported many references | Generic basename search matched unrelated `index.json` text | Inspect exact paths and Git status; never interpret basename count as proof. |
| Squash-integrated branch looked unmerged | Squash created a new commit identity | Use PR receipt, patch/tree equivalence, tests, and remote preservation—not ancestry alone. |

## How this work could be even better next time

1. Define the independent engineering benchmark before recovering code.
2. List intended handwritten, generated, and forbidden public-surface paths in
   the intake packet.
3. Discover test paths before composing the first combined command.
4. Run index generation only after handwritten content is stable and only at
   maintained parent folders.
5. Decide the post-merge receipt strategy in advance so candidate wording stays
   precise without an avoidable broad follow-up.
6. Retain one exact remote preservation ref until the replacement has passed
   integrated-main verification.

## Teach-back questions

1. Why did we need both a branch and a worktree?
2. Why was cherry-picking one clean commit still unsafe?
3. What does `source_bound=true` prove that a Python executable path does not?
4. Why can squash-integrated work fail an ancestry check?
5. Which scripts are read-only, which write files, and which delete them?
6. What evidence justified removing the local PMM worktrees?

If an answer uses “Git knows” or “the tests passed” without naming the exact
commit, checkout, source root, test boundary, and remote ref, inspect again.
