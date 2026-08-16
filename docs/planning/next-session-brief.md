# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: frontmatter checker contract and exactly eight invalid records
- Baseline: GIT-001 Phase 8 started from fetched origin/main 86f92ed16164a97b7cbb1edacd64a50a5a71e13d, tree 1bb7e448fd26208ba2227b1d9e2f3f0f976ed46e
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested
- Git outcome: Phases 0-8 close on merge of the unchanged adoption packet; transition receipts are time-bound and final merge facts require a fresh successor observation
- Primary/e54a: primary was clean/equal at packet start; detached dirty e54a remains retained and untouched
- Other lanes: Excel is HOLD_UNKNOWN_OWNER; every other pre-existing lane remains UNKNOWN/HOLD; no cleanup authority exists
- Confirmed next defect: frontmatter JSON mode reports eight invalid records but exits zero because it returns before applying the text-mode failure rule
- Scope guard: repair only that exit-code contract, its direct regression tests, and the eight named lifecycle/doc-type records; leave 60 permitted legacy records alone
- Next action: begin only DOC-FRONTMATTER-CONTRACT in a fresh fetched-current-main lane
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; GIT-001 adoption closes with retained holds and no cleanup |
| **Next** | `DOC-FRONTMATTER-CONTRACT` only |
| **Later** | Clause 38.2 truth hygiene, pile-cap G0, raft G0, accepted GO packets, INDIA-2 broad closeout |
| **Held** | Cleanup/deletion, release, React expansion, professional approval, dependency majors |

## Required Reading

1. [Next-session Git/issues/INDIA-2 plan](india-2-next-session-publication-and-closeout-plan.md)
2. [Current task board](../TASKS.md)
3. [Phase 8 adoption closeout](../research/git-governance/GIT-001-phase-8-adoption-closeout.md)
4. [`check_docs.py`](../../scripts/check_docs.py)

## Exact start

Fetch and verify `origin/main`, then create one fresh
`codex/doc-frontmatter-contract` worktree. Do not write on primary, reuse the
Phase 8 lane, or touch retained worktrees.

```bash
./run.sh session brief --agent doc-master
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with fetched `origin/main` before editing.

## Packet order

1. `DOC-FRONTMATTER-CONTRACT`
   - make JSON mode return nonzero whenever `invalid_frontmatter` is nonzero;
   - preserve the JSON payload exactly;
   - add direct invalid/valid exit-code regressions;
   - repair exactly the eight already identified status/doc-type records;
   - do not bulk-add frontmatter to 60 permitted legacy documents.
2. `INDIA-2-TRUTH-HYGIENE-38-2`
   - trace live metadata/decorator/provenance/arithmetic consumers;
   - rebind supported source identities;
   - change arithmetic only if an independent benchmark proves an outcome
     defect.
3. Decision-only `PILE-CAP-G0`, then its A-D/acceptance chain only after `GO`.
4. Decision-only `RAFT-G0`, then any owner-accepted chain.
5. `INDIA-2-CLOSEOUT` with broad Python and the full 30-check gate once.
6. Post-INDIA-2 dependency-major compatibility packets only afterward.

## Frozen frontmatter scope

The confirmed root cause is the early unconditional JSON return in
`check_frontmatter()`. The eight data defects are:

- invalid `status`: the library-first master plan, combined-C public-workflow
  evidence, and wall/deep/flat family-acceptance evidence; and
- invalid `doc_type: verification`: strap A, B, and C evidence.

Give each record a schema-valid lifecycle/doc type while preserving its
narrative completion/acceptance meaning. Do not rewrite engineering evidence,
expand the schema, or sweep unrelated legacy metadata.

## Owner-decision boundaries

- Primary, `e54a`, Excel, Phase 8, and every other retained lane stay untouched.
- Historical task-to-Git receipts are time-bound evidence; do not rewrite them
  to suppress stale holds.
- Closing dependency PRs, deleting branches/worktrees, release/tag/package
  publication, and professional approval require separate authority.

## Gate cadence

Run focused checker tests, both live JSON and text modes, exact eight-record
replay, links/indexes, quick `10/10`, normal hooks, exact-head review, hosted
documentation checks, and merge-tree verification. Broad Python and the full
30-check gate remain deferred to final INDIA-2 closeout unless a confirmed
repository-wide failure forces them earlier.

The session entry must contain `Issues encountered` and `Root causes and
resolutions`, including visible symptom, main-process impact, confirmed cause,
implemented correction, and executable proof.

## Efficiency card

- Freeze the eight paths and checker/test paths before editing.
- Use one writer, one candidate, one generator pass, one quick gate, one push,
  and one hosted-check cycle.
- Preserve the JSON payload while changing only the exit status.
- Record orientation, implementation, repair, CI wait, closeout, and total
  elapsed workflow time separately.

## Stop rule

Start and finish only `DOC-FRONTMATTER-CONTRACT`. Do not begin Clause 38.2,
pile-cap, raft, dependency, broad-gate, or cleanup work in that lane.
