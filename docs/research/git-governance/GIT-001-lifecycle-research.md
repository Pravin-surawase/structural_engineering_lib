---
owner: Main Agent
status: active
last_updated: 2026-08-12
doc_type: reference
task: GIT-001
phase: 1
---

# GIT-001 Phase 1 — Lifecycle Research

## Status and boundary

This is a factual, non-normative lifecycle model under research. It does not
replace the canonical project workflow. Proposed transitions and permissions
will be designed in Phase 4 only after official research and project forensics.

## Foundational Git model

The first verified facts establish why a branch name alone cannot mean that
work is saved:

- Git stores immutable objects; refs such as branch names point to object IDs.
- `HEAD`, the index, the working tree, and untracked paths are distinct states.
- A commit records indexed content in history. Uncommitted index/working-tree
  content is not made durable merely by creating or naming a branch.
- Reachability counts compare commit graphs. They do not establish patch
  equivalence after squash, cherry-pick, or manual reproduction.
- Reflogs are valuable local recovery evidence, but they expire and are not a
  substitute for an intentional commit and remote publication strategy.

Sources: [Git glossary](https://git-scm.com/docs/gitglossary),
[`git status`](https://git-scm.com/docs/git-status),
[revision syntax](https://git-scm.com/docs/gitrevisions), and
[`git reflog`](https://git-scm.com/docs/git-reflog).

## Worktree isolation model

Official Git documentation says a linked worktree has its own working tree,
`HEAD`, index, and operation metadata, but shares repository data including many
refs and default configuration. Therefore filesystem isolation is necessary but
not sufficient for safe concurrency. Branch naming, shared-ref mutation,
configuration, hooks, and shared project files still require explicit
coordination. Git-aware path resolution such as `git rev-parse --git-path` is
required for operation markers in linked worktrees.

OpenAI describes the Codex app's worktree support as isolated task copies that
allow multiple agents to work on the same repository. GIT-001 must reconcile
that useful product isolation with Git's formally shared state rather than
assuming complete independence.

Sources: [`git worktree`](https://git-scm.com/docs/git-worktree) and
[Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/).

## PR and verification model

GitHub's current documentation distinguishes PR state, mergeability, reviews,
rules, and checks. Required checks must correspond to the latest relevant SHA;
a previous green head is not evidence for a changed head. Draft PRs cannot be
merged. Rulesets can require PRs, checks, current branches, or merge types and
can block force pushes.

These facts support later evaluation of the project's exact-head practice, but
they do not yet decide whether this project should use strict or loose required
checks, squash or merge commits, early draft PRs, or a merge queue.

Sources: [GitHub status checks](https://docs.github.com/en/pull-requests/reference/status-checks),
[required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks),
[ruleset rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), and
[merging a pull request](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request).

## Candidate lifecycle questions

The intended end-to-end sequence remains a hypothesis to test:

```text
Proposed -> Classified -> Isolated -> Active -> Verified
-> Published -> Reviewed -> Integrated -> Recoverable -> Closed
```

Research must determine, for every transition:

- required input identity and evidence;
- which Git/Codex/GitHub state changes;
- what is local, per-worktree, or shared;
- which actor owns the transition;
- permitted, approval-gated, and prohibited commands/actions;
- fail-closed hold states and exit evidence;
- recovery horizon and retained artifacts;
- measurements that reveal recurring friction or failure.

## Explicit hold states

The following are candidate hold categories, not yet accepted policy:

- detached HEAD;
- dirty state whose ownership is not established;
- wrong or missing upstream;
- behind or diverged task branch;
- merge, rebase, revert, or cherry-pick in progress;
- conflicted index;
- reviewed PR whose head or base changed;
- branch/worktree with uncertain unique work or patch-equivalence status;
- generated/shared-surface collision;
- missing exact release or artifact identity.

## Next Phase 1 packet

Complete the open source coverage in the evidence register, then write a source-
backed factual map for normal work, parallel work, integration, release, cleanup,
and recovery. Each statement must be marked as external fact, project
observation, unresolved choice, or not applicable. No project recommendation
advances to Phase 2/3 until the Phase 1 source-coverage review is complete.
