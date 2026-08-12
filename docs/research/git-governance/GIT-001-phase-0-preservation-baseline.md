---
owner: Main Agent
status: active
last_updated: 2026-08-12
doc_type: log
task: GIT-001
phase: 0
---

# GIT-001 Phase 0 — Preservation Baseline

## Receipt identity

- Observation time: `2026-08-12T21:17:05+05:30`
- Repository: `Pravin-surawase/structural_engineering_lib`
- Git: `2.48.1`
- Refresh: `git fetch origin --prune` completed immediately before lane creation.
- Verified base: local `main` = refreshed `origin/main` =
  `6bc356c37f094ff6dba1c5c2f06527bf1cda4966` (`0` ahead, `0` behind).
- Program-start mutation: the requested research worktree and branch were then
  created from that exact object. No existing checkout, branch, stash, commit,
  PR, or worktree was changed or removed.

## Research-lane identity

| Field | Observed value |
|---|---|
| Path | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-governance-research` |
| Branch | `codex/git-governance-research` |
| HEAD | `6bc356c37f094ff6dba1c5c2f06527bf1cda4966` |
| Upstream | None; branch is intentionally local until a reviewed publication point |
| Worktree state | Clean at creation |
| Common Git directory | primary checkout `.git` directory |
| Worktree Git directory | `.git/worktrees/structural_engineering_lib-git-governance-research` |
| Python source identity | Bound to this worktree's `Python/structural_lib/__init__.py` |

## Worktree inventory

All eight worktrees were inspected with `git --no-optional-locks ... status
--porcelain=v2 --branch`. No tracked, staged, or untracked paths were reported.

| Worktree | Branch | HEAD | Upstream state | Preservation disposition |
|---|---|---:|---|---|
| Primary checkout | `main` | `6bc356c3` | `origin/main`, `+0 -0` | Clean integration anchor |
| Alpha candidate | `codex/alpha-0231-release-closeout` | `127afb64` | branch upstream, `+0 -0` | Preserve; not assessed for cleanup |
| Alpha policy | `codex/release-preflight-alpha-policy` | `5da9c66a` | branch upstream, `+1 -0` | Preserve; unpublished local commit possible |
| Alpha integration | `codex/alpha-0231-integration` | `e3b9a6cb` | branch upstream, `+0 -0` | Preserve; not assessed for cleanup |
| Column PMM | `codex/column-pmm-experimental` | `8a52ed0f` | tracks `origin/main`, `+1 -53` | Protected unique engineering work; untouched |
| Excel planning | `codex/excel-product-planning` | `a0e115e1` | tracks `origin/main`, `+0 -53` | Preserve; not assessed for cleanup |
| GIT-001 research | `codex/git-governance-research` | `6bc356c3` | no upstream | Active task-owned lane |
| Parallel policy | `codex/parallel-task-policy` | `75d66681` | branch upstream, `+0 -0` | Preserve; open PR #723 |

## Local branch inventory relative to `origin/main`

Counts are `commits unique to origin/main | commits unique to local branch`.
They describe reachability only; they are not cleanup or patch-equivalence
decisions.

| Local branch | Tip | Main-only | Branch-only | Configured upstream |
|---|---:|---:|---:|---|
| `codex/alpha-0231-candidate-evidence` | `adb161b8` | 8 | 0 | matching remote branch |
| `codex/alpha-0231-integration` | `e3b9a6cb` | 24 | 0 | matching remote branch |
| `codex/alpha-0231-release-closeout` | `127afb64` | 6 | 0 | matching remote branch |
| `codex/ci-fastapi-load-lane-fix` | `21b9df1f` | 50 | 0 | matching remote branch |
| `codex/column-pmm-experimental` | `8a52ed0f` | 53 | 1 | `origin/main` |
| `codex/column-rectangular-e2e` | `007dfa0c` | 43 | 0 | matching remote branch |
| `codex/excel-product-planning` | `a0e115e1` | 53 | 0 | `origin/main` |
| `codex/footing-isolated-v1` | `886871ae` | 48 | 0 | matching remote branch |
| `codex/git-governance-research` | `6bc356c3` | 0 | 0 | none |
| `codex/gpt-5-3-spark-work-program` | `6cd22dcb` | 1 | 0 | matching remote branch |
| `codex/is456-beam-primary-route` | `aa4fe606` | 47 | 0 | matching remote branch |
| `codex/is456-slabs-closeout` | `d79a1558` | 36 | 0 | matching remote branch |
| `codex/is456-slabs-plan` | `7e623984` | 47 | 0 | matching remote branch |
| `codex/parallel-task-policy` | `75d66681` | 53 | 3 | matching remote branch |
| `codex/release-preflight-alpha-policy` | `5da9c66a` | 21 | 0 | matching remote branch; local is one ahead of it |
| `main` | `6bc356c3` | 0 | 0 | `origin/main` |

## GitHub inventory

Read-only GitHub inspection found eight open PRs. This is observation, not
priority or closure authority.

| PR | Head | State observed |
|---:|---|---|
| #723 | `codex/parallel-task-policy` | Draft; `DIRTY`; head `75d66681` |
| #717 | `dependabot/pip/mypy-2.3.0` | Open; `BEHIND` |
| #716 | `dependabot/npm_and_yarn/react_app/framer-motion-13.0.0` | Open; `BEHIND` |
| #715 | `dependabot/pip/Python/mypy-gte-1.19-and-lt-3` | Open; `BEHIND` |
| #714 | `dependabot/npm_and_yarn/react_app/types/node-26.1.2` | Open; `BEHIND` |
| #713 | `dependabot/npm_and_yarn/react_app/eslint-10.8.0` | Open; `BEHIND` |
| #684 | `dependabot/npm_and_yarn/react_app/vitejs/plugin-react-6.0.5` | Open; `BEHIND` |
| #683 | `dependabot/npm_and_yarn/react_app/eslint/js-10.0.1` | Open; `BEHIND` |

Repository settings observed through GitHub's API:

- default branch: `main`;
- branch deletion after merge: disabled;
- squash, merge-commit, and rebase merge methods: enabled;
- active branch ruleset: `11390214`, `main_branch_rule1`.

Settings behavior and fitness remain Phase 2/3 questions; this receipt does not
infer policy from configuration.

## Recovery and operation state

- `git stash list`: empty.
- In the GIT-001 worktree, `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`,
  `REBASE_HEAD`, `sequencer`, `rebase-merge`, and `rebase-apply` were absent
  using `git rev-parse --git-path` for linked-worktree-correct resolution.
- Other worktrees were clean, but their per-worktree operation markers were not
  individually enumerated. That remains an explicit unknown rather than a clean
  bill of health.

## Preserved lanes and holds

- `codex/column-pmm-experimental`: protected because it has one commit not
  reachable from `origin/main` and an unusual `origin/main` upstream.
- `codex/parallel-task-policy`: protected because it has three commits not
  reachable from `origin/main` and open draft PR #723 is conflicted.
- Alpha and Excel worktrees: preserved because reachability, remote parity, age,
  or a clean worktree does not establish safe deletion.
- All other local/remote branches: no cleanup decision until PR, patch,
  worktree, reflog, and ownership evidence are reconciled.

## Unknown or not assessed

- Patch equivalence of squash-merged branches.
- Unpushed commits outside the worktree tips listed here or objects reachable
  only from reflogs.
- Per-worktree operation markers outside GIT-001.
- Managed-worktree archival/snapshot state in Codex.
- Current review/check detail for PRs other than the compact open-PR inventory.
- Whether current GitHub settings match intended future governance.
- Ownership and retirement disposition of historical Git documents.

These unknowns are holds. No cleanup or recovery mutation is authorized by this
baseline.

## Reproduction commands

The baseline used only the following command families after the one authorized
worktree creation:

```text
git fetch origin --prune
git status --porcelain=v2 --branch
git rev-parse HEAD origin/main --git-common-dir --git-dir --git-path <marker>
git rev-list --left-right --count origin/main...<local-branch>
git worktree list --porcelain
git for-each-ref <formats> refs/heads
git stash list
git --no-optional-locks -C <worktree> status --porcelain=v2 --branch
gh pr list --state open --json <fields>
gh api repos/Pravin-surawase/structural_engineering_lib/rulesets
gh api repos/Pravin-surawase/structural_engineering_lib
./scripts/python_runtime.sh --diagnose
```

## Phase 0 decision

Phase 0 is complete for program start: the base and lane identities are exact,
the inventory is reproducible, protected states and unknowns are explicit, and
no cleanup disposition was made. Phase 1 may proceed. Phase 0 does not certify
any old lane as merged, redundant, recoverable, or safe to remove.
