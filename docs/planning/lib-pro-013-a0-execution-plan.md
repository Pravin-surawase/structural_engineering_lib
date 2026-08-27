---
owner: Main Agent
status: ready
last_updated: 2026-08-27
doc_type: spec
complexity: advanced
tags: [lib-pro-013, a0, audit, execution, efficiency]
---

# LIB-PRO-013 A0 Consolidated Renewal Audit — Execution Plan

## 1. Authority and boundary

This is a derivative execution plan for the **A0 Consolidated Renewal Audit**
defined by Sections 9–16 of
[LIB-PRO-013](lib-pro-013-whole-library-renewal-audit-plan.md). LIB-PRO-013
remains the scope, method, severity, and acceptance authority. LIB-PRO-012
remains the remediation authority for known external-API work. If this file
and either master plan disagree, the master plan wins.

A0 begins only after the post-merge S0 acceptance task is integrated on the
project default branch. It is one read-only audit cycle covering G1 and every
remaining initial audit lane through C2. It may write audit evidence, the task
board, session log, and handoff documents; it may not edit runtime,
dependencies, public signatures, generated API/client owners, protected
sources, retained worktrees, or release artifacts.

## 2. Entry gate

At A0 start, one parent must prove all of the following before any audit
evidence is written:

1. `origin/main` is freshly fetched, clean, conflict-free, and contains the
   accepted S0 merge plus this plan or a clean descendant.
2. `git_state.py --json --worktrees` shows no overlapping active candidate on
   audit evidence, task, session, or shared generated owners. Every dirty,
   detached, ignored, stashed, archived, and protected item is preserved.
3. The public `0.24.0a1` wheel/sdist/tag identities, the current source head and
   tree, and a newly built source-free current-head wheel are recorded as
   different evidence objects.
4. Current control, context, API classification, compatibility, workflow,
   capability, package, dependency, test, agent, skill, worktree, and CI
   authorities are queryable. A stale retained count is never promoted to live
   truth.
5. One session is started as `LIB-PRO-013-A0-CONSOLIDATED-RENEWAL-AUDIT` on
   `codex/lib-pro-013-a0-consolidated-renewal-audit` using the maintained routed
   role.

Identity ambiguity, an overlapping writer, or missing preservation evidence is
a stop condition, not a reason to reset, rebase, clean, or reorganize another
lane.

## 3. One-cycle deliverable

The canonical A0 output is one report:

`docs/verification/lib-pro-013-a0-renewal-audit.md`

It contains the exact baseline, Section 7 coverage crosswalk, audit-of-audits
matrix, advertised journey inventory, finding register, evidence-class matrix,
retention proposals, peer decisions, and C2 remediation portfolio. Existing
classification, compatibility, capability, workflow, package, and control
files are referenced as authorities; A0 does not copy or silently rewrite
them.

Each finding uses the LIB-PRO-013 schema: stable ID, domain, priority, evidence
state, exact identity, journey/reproducer, expected and observed outcomes,
impact, cause state, owner, compatibility effect, disposition, dependency,
focused proof, cumulative gate, provenance, and review boundary. Route-level
evidence remains visible even when several findings share one root cause.

## 4. Four batched passes

The master estimate remains **15–24 engineer-days**. Efficiency comes from
shared inventories and evidence reuse, not from claiming less audit work.

| Pass | Included LIB-PRO-013 packets | Estimate | Frozen outcome |
|---|---|---:|---|
| **A0.1 Authority and recurrence truth** | G1, U1, U2, R2, R3 | 2–3 days | Exact audit-of-audits, installed-user journeys, public contract census, architecture/generated ownership, and test/evidence taxonomy |
| **A0.2 Product and engineering outcomes** | U3, U4, E1, E2, E3, P1, P2, P3, P4 | 6–9 days | Validation/result/composition, every supported family, engineering evidence classes, CLI/export, REST/client, React, and separately labelled Windows evidence |
| **A0.3 Professional development system** | R1, R4, R5, A1, A2, A3, A4, C1 | 4–7 days | Package/dependency/platform, docs/support/naming, Git/CI/recovery, agent/skill/tool/efficiency, retention, and official-source peer decisions |
| **A0.4 C2 synthesis** | C2 plus the Section 7 completeness gate | 3–5 days | Deduplicated prioritized portfolio with every finding owned, dependency-ordered, estimated by class, and assigned to a later cycle or explicit hold |

The passes are evidence checkpoints inside one session and branch. They are not
separate commits, PRs, hosted runs, or status-only handoffs.

## 5. Efficient method

### 5.1 Inventory once, replay by class

- Query maintained registries and generators once during A0.1 and store their
  command, source bytes/hash, runtime, platform, and observation time in the
  report.
- Build one advertised-workflow-to-owner matrix. Use it to drive Python,
  transport, consumer, documentation, and artifact sampling instead of keeping
  separate hand lists.
- Sample every distinct route/contract class. When a class fails, expand from
  the maintained inventory to every member of that class; do not broaden an
  already passing class without a stated risk.
- Reuse the accepted S0 direct-source and exact-wheel evidence for unchanged
  owners. Reproduce only claims whose source bytes, environment, artifact, or
  contract changed.
- Deduplicate by confirmed root cause while retaining all journey identities
  and affected consumers.

### 5.2 Separate evidence classes

For every promoted engineering journey, label evidence as independent
arithmetic, controlled source example, external-software comparison, blind
internal recomputation, wrapper/transport parity, generated regression, UI
projection, qualified review, or `NOT_TESTED`. No generated or wrapper parity
is upgraded into independent validation.

The Windows Excel/ETABS lane is satisfied only by exact installed Windows
evidence or an explicit `NOT_TESTED / HELD` record naming what is needed. Mac
or source-only evidence cannot satisfy it.

### 5.3 External research once

C1 uses current official documentation and primary sources only. Each source
is captured once with access date, comparable journey, local finding, benefit,
cost, compatibility/dependency effect, and `ADOPT`, `ADAPT`, or `REJECT`
decision. Popularity alone is not evidence.

### 5.4 Verification cadence

During the audit, run only bounded inventories, reproducers, source-free
journeys, and browser/transport checks required by the active pass. Do not run
the broad repository suites as discovery tools.

After the report, task, session, and handoff content freezes:

1. replay every finding reproducer and the report's completeness validator;
2. run relevant architecture/import, package-content, documentation/link,
   generated-drift **check-only**, control/context, and evidence-schema checks;
3. run `./run.sh check --quick` once;
4. stage only A0-owned evidence/status paths and run normal commit hooks;
5. create one immutable evidence candidate, push once, open one PR, and wait for
   every changed-path hosted check on that exact head.

The broad Python/React/full cumulative gate remains owned by the later R0
candidate unless A0 itself exposes a repository-wide outcome whose diagnosis
requires it.

## 6. Decisions and routing

Each C2 item must be routed without duplicating LIB-PRO-012:

| Finding outcome | Route after A0 |
|---|---|
| Common contract, canonical beam, or downstream convergence | B0 (LIB-PRO-012 C/D/E) |
| Family facade/construction convergence | F0 (LIB-PRO-012 F1/F2/F3) |
| Documentation, generated gates, package, cumulative artifact, or independent audit closure | R0 (LIB-PRO-012 G/H/I plus LIB-PRO-013 C3) |
| New outcome-changing P0 | Stop A0 completion and request a separately authorized, bounded safety repair before B0 |
| Unsupported scope, unavailable Windows/professional evidence, release, publication, or qualified review | Explicit `HOLD` with exact authority/evidence required |
| Cosmetic, speculative, or no-main-outcome concern | Exclude as P3; do not create remediation work |

No finding may silently expand the supported engineering scope or add a
dependency. A proposed dependency, formula change, signature break, deletion,
or public claim needs its own authority after the audit.

## 7. Acceptance and stop rules

A0 is complete only when every Section 7 domain has an owner, method, artifact,
and disposition; every advertised journey is accounted for; every earlier
audit is reconciled within its original scope; every finding has exact evidence
and a dependency-ordered disposition; and C2 has no unresolved P0.

Stop early and report the exact blocker when:

- a new P0 safe-looking result or artifact is reproduced;
- identity, preservation, or generated ownership is ambiguous;
- a valid golden engineering result changes during read-only replay;
- an audit conclusion needs protected source content copied into Git;
- an active candidate overlaps the report/task/session owners; or
- release, deletion, dependency, signature, formula, or professional authority
  is required.

Software/audit acceptance does not authorize B0 automatically. After the
unchanged green A0 merge, the owner may start B0 from the integrated C2
portfolio. Release, publication, qualified review, professional approval, and
engineering-use claims remain separate.
