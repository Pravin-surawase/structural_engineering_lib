---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: index
task: GIT-001
---

# GIT-001 — Git Research, Project Workflow, and Future-Proof Governance

## Authority boundary

This directory is the task-owned, non-normative research record for GIT-001.
Its contents may describe official Git/GitHub/Codex facts, observed project
state, incidents, alternatives, and proposals. They do **not** change project
policy.

The current normative policy is
[`docs/git-automation/git-workflow-single-source.md`](../../git-automation/git-workflow-single-source.md)
and now includes the owner-accepted GIT-7B read-only state/intake contract.
GIT-7C1 is integrated, GIT-7C2 server enforcement is applied, and GIT-7D is
complete: GIT-7D1 integrated through PR #746, while GIT-7D2 integrated through
PRs #747-#748 and has a non-destructive preservation/disposition reconciliation.
GIT-7E semantic guidance and durable handoff remain the next separate packet.

## Objective

Develop an evidence-backed Git operating model for human and AI work from task
start through integration, recovery, retention, and cleanup. The model must
prevent predictable mistakes, fail closed in abnormal states, preserve unknown
work, make recovery deterministic, and remain efficient during normal work.

## Starting topology

| Role | Path / branch | Start state |
|---|---|---|
| Integration anchor | primary checkout / `main` | Refreshed and clean at `69d9f68c` on 2026-08-12 |
| GIT-001 research lane | `structural_engineering_lib-git-governance-research` / `codex/git-governance-research` | Synchronized and published at `54a03557`; tree exactly matches `69d9f68c` while retaining research ancestry |
| Preserved engineering evidence | remote PMM forensic/recovery refs | Selective recovery and independent benchmark integrated through PRs #738-#740; PMM remains experimental |
| Preserved workflow evidence | remote `codex/parallel-task-policy` | PR #723 closed after bounded replacement through PRs #736-#737; remote retained for audit |

## Phase ledger

| Phase | Purpose | Status | Advancement gate |
|---|---|---|---|
| 0 | Preservation baseline | Complete for program start | Reproducible inventory, unknowns explicit, no cleanup disposition |
| 1 | Official Git/GitHub/Codex research | Complete | Two independent reviews passed; primary-source facts, project observations, unresolved choices, and N/A topology are separated |
| 2 | Project forensic study | Complete | Ten incident families trace evidence, impact, confirmed or explicit unconfirmed root causes, recovery, and proof |
| 3 | Gap and risk analysis | Complete | Thirteen outcome-changing gaps compare ideal facts, incidents, policy, live settings, automation, CI, and behavior |
| 4 | Operating-model design | Complete as proposal | Four control planes, one typed state model, lane lifecycle, permissions, CI/server policy, recovery, and four packets defined |
| 5 | Scenario validation | Complete for proposal | Disposable Git and live read-only checks reproduce current defects, validate primitives, and define falsifiable GIT-7B–7E gates |
| 6 | Canonical policy proposal | Accepted 2026-08-13 | Owner accepted the operating model and authorized GIT-7B only |
| 7 | Controlled implementation | 7A-7D complete; GIT-7E next | GIT-7D2 merged through PRs #747-#748; non-destructive cleanup reconciliation preserves every held lane and makes no deletion-ready claim without complete evidence |
| 8 | Adoption and closeout | Not started | Integrated workflow verified; supersession and maintenance established |

## Artifact map

- [Phase 0 preservation baseline](GIT-001-phase-0-preservation-baseline.md)
- [Official evidence register](GIT-001-official-evidence-register.md)
- [Lifecycle research](GIT-001-lifecycle-research.md)
- [Phase 7A preservation and workflow recovery](GIT-001-phase-7A-preservation-workflow-recovery.md)
- [Reconciled future-work and disposition plan](GIT-001-next-agent-disposition-plan.md)
- [Phase 2 incident register](GIT-001-phase-2-incident-register.md)
- [Phase 3 gap/risk matrix](GIT-001-phase-3-gap-risk-matrix.md)
- [Phase 4 operating-model proposal](GIT-001-phase-4-operating-model.md)
- [Phase 5 simulation and verification report](GIT-001-phase-5-scenario-validation.md)
- [Phase 6 canonical-policy proposal](GIT-001-phase-6-canonical-policy-proposal.md)
- [Phase 7B read-only state/intake kernel](GIT-001-phase-7B-state-intake-kernel.md)
- [Phase 7C1 required CI topology](GIT-001-phase-7C1-required-ci-topology.md)
- [Phase 7C2 server enforcement](GIT-001-phase-7C2-server-enforcement.md)
- [Phase 7D1 targeted index generation](GIT-001-phase-7D1-targeted-index-generation.md)
- [Phase 7D2 inspection-only branch disposition](GIT-001-phase-7D2-branch-disposition.md)
- [Phase 7D cleanup reconciliation](GIT-001-phase-7D-cleanup-reconciliation.md)
- [Phase 7D machine-readable preservation receipt](GIT-001-phase-7D-cleanup-reconciliation.json)
- Phase 7E durable handoff — planned
- Phase 8 adoption/closeout report — planned

## Ownership and non-goals

The GIT-001 lane owns this directory plus its parent-owned task/session records.
`AGENTS.md`, canonical Git policy, task handoffs, `SESSION_LOG.md`, generated
indexes, manifests, registries, routes, and lock files remain single-writer
surfaces. The parent agent is the integration owner for any necessary updates.

Phases 0-3 will not clean branches, delete worktrees, rewrite history, repair
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
