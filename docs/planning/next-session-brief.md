# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Git reconciliation and confirmed issue repairs before new foundation work
- Baseline: origin/main f56e1ec312902caf98e872c77ce8b71bdbc8440e; strap acceptance PR #798 merged with audited tree equality
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested
- Preserved primary: f87c8a32, nine behind, only .codex/config.toml dirty with low-to-medium verbosity intent
- Preserved e54a: detached 0fdb48ed, only docs/SESSION_LOG.md dirty; no cleanup authorization
- Git correction: GIT-7E PR #751 and orchestration PR #752 are merged; parent status is reconciled and Phase 8 must verify adoption/current disposition facts
- Issue correction: Clause 26.5.1.1 metadata was already fixed in STRAP-B and is not future work
- Confirmed issues: JSON frontmatter mode falsely exits zero; eight invalid records remain; live beam provenance still carries unsupported 38.2
- Next action: begin only GIT-001-P8-RECONCILIATION in a fresh current-main lane; no cleanup
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; bounded wall, stair, deep, flat/punching, combined-footing, and strap-footing families complete |
| **Next** | Git Phase 8 reconciliation, then issue repairs |
| **Later** | Decision-only pile-cap G0, raft G0, accepted GO packets, INDIA-2 broad closeout |
| **Held** | Cleanup/deletion, release, React expansion, professional approval, dependency majors |

## Required Reading

1. [Next-session Git/issues/INDIA-2 plan](india-2-next-session-publication-and-closeout-plan.md)
2. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
3. [GIT-001 index](../research/git-governance/GIT-001-README.md)
4. [GIT-001 disposition plan](../research/git-governance/GIT-001-next-agent-disposition-plan.md)
5. [INDIA-2 remaining-elements plan](india-2-remaining-is456-elements-plan.md)
6. [Strap family acceptance](../verification/india-2-foundation-strap-family-acceptance-evidence.md)
7. [Current task board](../TASKS.md)

## Exact start

Create a fresh `codex/git-001-phase8-reconciliation` worktree from fetched,
verified `origin/main`; do not use the dirty primary or retained `e54a` lane.

```bash
./run.sh session brief --agent ops
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and an exact
current-main base. Refresh GitHub PR evidence before making a current claim.

## Packet order

1. `GIT-001-P8-RECONCILIATION`
   - bind PR #751/#752 and verify the reconciled GIT-7E/task status;
   - prove adoption using recent immutable-head receipts;
   - classify primary/e54a/other lanes read-only;
   - ask for explicit owner decisions where required;
   - perform no synchronization, reset, stash, deletion, branch closure, or
     worktree removal.
2. `DOC-FRONTMATTER-CONTRACT`
   - make JSON output return nonzero when invalid records exist;
   - add direct regression coverage;
   - repair exactly the eight currently invalid lifecycle/doc-type records;
   - do not bulk-add frontmatter to 60 permitted legacy documents.
3. `INDIA-2-TRUTH-HYGIENE-38-2`
   - trace all live metadata/decorator/provenance/arithmetic consumers;
   - rebind supported source identities;
   - benchmark the legacy flexure approximation against exact equilibrium;
   - change arithmetic only when main-process outcome evidence requires it.
4. Decision-only `PILE-CAP-G0`, then any owner-accepted GO chain.
5. Decision-only `RAFT-G0`, then any owner-accepted GO chain.
6. `INDIA-2-CLOSEOUT` with broad Python and the full 30-check gate once.
7. Post-INDIA-2 dependency-major compatibility packets only afterward.

## Owner-decision boundaries

- Primary `.codex/config.toml`: publish `medium` from a fresh lane, retain it
  local-only, or explicitly authorize discard. No option is inferred.
- `e54a`: retain until named ownership/retention evidence and an exact
  classifier receipt exist. Even pending approval does not authorize deletion.
- Closing dependency PRs, deleting branches/worktrees, release/tag/package
  publication, and professional approval require separate authority.

## Gate cadence

Using the cadence quoted by the owner: focused gates per packet, with the broad
Python and 30-check gates only at the final INDIA-2 integration boundary unless
a repository-wide failure forces them earlier.

Each packet still requires focused tests, root-cause proof, architecture/import
checks where relevant, quick `10/10`, normal hooks, exact-head review, hosted
checks, merge-tree verification, and a session entry containing `Issues
encountered` plus `Root causes and resolutions`.

## Stop rule

The next session starts only GIT-001 Phase 8 reconciliation. Do not begin the
frontmatter fix, Clause 38.2 repair, pile-cap, raft, dependency update, broad
gate, or cleanup in the same packet.
