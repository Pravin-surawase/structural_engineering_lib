---
owner: Main Agent
status: active
last_updated: 2026-08-12
doc_type: log
task: GIT-001
packet: 7A
---

# GIT-001 Phase 7A — Preservation and Workflow Recovery

## Authorization and boundary

The repository owner authorized Git operations, merge/deletion when proven
safe, parallel subagents, preservation of Column PMM, and selective recovery of
PR #723. This packet does not approve the wider Phase 7 policy program.

## Column PMM disposition

| State | Evidence | Decision |
|---|---|---|
| Unique history | `8a52ed0f` is the unpublished PMM commit | Preserve remotely |
| Remote backup | local and `origin/codex/column-pmm-experimental` match exactly | Complete |
| Focused regression | 9 tests pass when explicitly imported from the old worktree | Useful, not independent |
| Engineering benchmark | plan expressly lacks an independent full P-Mx-My surface benchmark | Hold integration |

The old branch remains the preserved research artifact. It is not presented as
production-capable, and its generalized fiber calculation was not copied into
the fresh recovery lane. Advancement requires a trusted independent benchmark
covering oblique neutral-axis cases, not only axial capacity or principal-axis
slices. Software verification remains distinct from qualified engineering
review and professional approval.

## PR #723 selective recovery

The old pull request was not merged or cherry-picked as a unit. It is 53
commits behind current `main`, conflicts with current shared surfaces, and mixes
useful controls with broad historical policy and generated changes.

Selected outcomes:

1. `./run.sh task brief <description> [--json]` performs read-only intake from
   live branch, head, dirty state, base/upstream, and sibling-worktree evidence;
   it reuses the existing router and tool registry and supplies safe start/close
   guidance.
2. `./run.sh generate indexes --help` is non-writing, while actual index
   generation invokes the `python_runtime.sh` belonging to the current
   worktree.

Rejected from this packet: broad parallel-task policy, canonical-policy edits,
agent-instruction rewrites, registry/map changes, generated index churn, and
unrelated product/runtime work already superseded by current `main`.

## Verification and retirement gate

- Runtime diagnosis must be source-bound to the recovery worktree.
- Focused intake/generator regressions and `./run.sh check --quick` must pass.
- The replacement branch must be pushed and reviewed through a new PR at an
  exact unchanged head.
- PR #723 and its branch/worktree may be retired only after replacement CI and
  merge demonstrate that the selected behavior is present on `main`; retirement
  must preserve this disposition record and the old commit reachability needed
  for audit.

This packet records a selective replacement, not a claim that all historical PR
#723 work was desirable or recovered.

## Integration receipt

- Replacement PR: #736, required CI green at unchanged head `aec9fbb2`.
- Integrated main commit: `30ec598d`.
- Integrated verification: `task brief` reports `main` at that commit and index
  help remains non-writing.
- Historical disposition: PR #723 closed at head `75d66681`; its remote branch
  remains available for audit.
- Local cleanup: the clean temporary PMM recovery, workflow recovery, and old
  PR #723 worktrees/branches were removed after exact status and reachability
  checks.
- Preserved engineering artifact: `codex/column-pmm-experimental` remains local
  and remote at `8a52ed0f`; independent full-surface benchmarking remains its
  integration gate.
