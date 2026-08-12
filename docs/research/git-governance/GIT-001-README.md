---
owner: Main Agent
status: active-research
last_updated: 2026-08-12
doc_type: research-index
task: GIT-001
---

# GIT-001 — Git Research, Project Workflow, and Future-Proof Governance

## Authority boundary

This directory is the task-owned, non-normative research record for GIT-001.
Its contents may describe official Git/GitHub/Codex facts, observed project
state, incidents, alternatives, and proposals. They do **not** change project
policy.

The current normative policy remains
[`docs/git-automation/git-workflow-single-source.md`](../../git-automation/git-workflow-single-source.md)
until the owner reviews a Phase 6 proposal and separately authorizes Phase 7.
Learning material is an input, never silent operational authority.

## Objective

Develop an evidence-backed Git operating model for human and AI work from task
start through integration, recovery, retention, and cleanup. The model must
prevent predictable mistakes, fail closed in abnormal states, preserve unknown
work, make recovery deterministic, and remain efficient during normal work.

## Starting topology

| Role | Path / branch | Start state |
|---|---|---|
| Integration anchor | primary checkout / `main` | Clean at `6bc356c3`; no implementation work |
| GIT-001 research lane | `structural_engineering_lib-git-governance-research` / `codex/git-governance-research` | Created from refreshed `origin/main` at `6bc356c3` |
| Preserved engineering lane | `structural_engineering_lib-column-pmm` / `codex/column-pmm-experimental` | Reference only; untouched |
| Preserved workflow lane | `structural_engineering_lib-parallel-policy` / `codex/parallel-task-policy` | Reference only; PR #723 remains open and conflicted |

## Phase ledger

| Phase | Purpose | Status | Advancement gate |
|---|---|---|---|
| 0 | Preservation baseline | Complete for program start | Reproducible inventory, unknowns explicit, no cleanup disposition |
| 1 | Official Git/GitHub/Codex research | In progress | Primary-source coverage reviewed; facts separated from decisions |
| 2 | Project forensic study | Not started | Incident register traces evidence and confirmed root causes |
| 3 | Gap and risk analysis | Not started | Ideal, policy, settings, automation, and behavior compared |
| 4 | Operating-model design | Not started | Lifecycle, states, permissions, topology, merge and recovery proposals |
| 5 | Scenario validation | Not started | Disposable simulations and read-only project checks pass |
| 6 | Canonical policy proposal | Not started | Owner accepts, revises, or rejects proposal |
| 7 | Controlled implementation | Approval-gated | Separate owner authorization for each implementation packet |
| 8 | Adoption and closeout | Not started | Integrated workflow verified; supersession and maintenance established |

## Artifact map

- [Phase 0 preservation baseline](GIT-001-phase-0-preservation-baseline.md)
- [Official evidence register](GIT-001-official-evidence-register.md)
- [Lifecycle research](GIT-001-lifecycle-research.md)
- Phase 2 incident register — planned
- Phase 3 gap/risk matrix — planned
- Phase 4 operating-model proposal — planned
- Phase 5 simulation and verification report — planned
- Phase 6 canonical-policy proposal — planned
- Phase 7 implementation packets — owner-approval gated
- Phase 8 adoption/closeout report — planned

## Ownership and non-goals

The GIT-001 lane owns this directory plus its parent-owned task/session records.
`AGENTS.md`, canonical Git policy, task handoffs, `SESSION_LOG.md`, generated
indexes, manifests, registries, routes, and lock files remain single-writer
surfaces. The parent agent is the integration owner for any necessary updates.

Phase 0/1 will not clean branches, delete worktrees, rewrite history, repair
legacy documents, change GitHub settings, alter hooks, publish a release, or
implement proposed policy. Unknown ownership or recoverability is a hold state.

## Research method

Every conclusion must identify its evidence level:

1. official external fact;
2. project observation or incident evidence;
3. proposed architectural decision;
4. accepted normative policy.

Every external source records authority, URL, finding, applicability, decision
status, and verification date. Project incidents use the chain:

`Symptom -> Impact -> Confirmed root cause -> Unsafe reaction -> Preventive control -> Recovery -> Verification`.
