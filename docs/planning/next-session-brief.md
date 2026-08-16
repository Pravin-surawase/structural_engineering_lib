# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: decision-only pile-cap G0
- Baseline: INDIA-2-TRUTH-HYGIENE-38-2 started from fetched origin/main df3635e8811a4d7e69f8786349ce3507f8a28001, tree 4de5ae83cdc115fe1984e2b97b616676e094e578
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested
- Clause outcome: controlled Clause 38.1/Annex G provenance, one shared exact beam/slab stress-block solver, and a supported false-safe discriminator repaired; 190 focused tests pass
- Scope guard: G0 is decision/benchmark only; missing controlled companion source or accepted structural benchmark requires HOLD
- Retained lanes: primary, detached dirty e54a, Excel HOLD_UNKNOWN_OWNER, and every other pre-existing lane remain untouched; no cleanup authority exists
- Next action: begin only INDIA-2-FOUNDATION-PILE-CAP-G0 in a fresh fetched-current-main lane after the Clause 38.2 candidate merges
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; frontmatter contract repair complete on merge |
| **Next** | Decision-only `INDIA-2-FOUNDATION-PILE-CAP-G0` |
| **Later** | Pile-cap chain only after GO; raft G0; INDIA-2 broad closeout |
| **Held** | Cleanup/deletion, release, React expansion, professional approval, dependency majors |

## Required Reading

1. [Next-session Git/issues/INDIA-2 plan](india-2-next-session-publication-and-closeout-plan.md)
2. [Current task board](../TASKS.md)
3. [IS 456 public-distribution permission](../verification/is456-public-distribution-permission.json)
4. Discover the live clause database, beam flexure, decorator, provenance,
   manifest, and nearest focused-test paths with `rg --files` before reading.

## Exact start

Fetch and verify `origin/main`, then create one fresh
`codex/india-2-foundation-pile-cap-g0` worktree. Do not write on primary, reuse
the Clause 38.2 lane, or touch retained worktrees.

```bash
./run.sh session brief --agent structural-engineer
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with fetched `origin/main` before editing.

## Packet order

1. Decision-only `PILE-CAP-G0`; publish `GO`, `REVISE`, or `HOLD`.
2. Execute pile-cap A-D/acceptance only after an accepted `GO`.
3. Decision-only `RAFT-G0`, then any owner-accepted chain.
4. `INDIA-2-CLOSEOUT` with broad Python and the full 30-check gate once.
5. Post-INDIA-2 dependency-major compatibility packets only afterward.

## Frozen pile-cap G0 scope

Investigate exactly one centred axial two-pile structural cap with caller-owned
pile reactions/capacity/geotechnical approval. Decide the pile-reaction model,
layout and topology discriminator, bearing/nodal checks, anchorage, deep-region
treatment, and companion-code dependencies. Freeze one independently replayed
benchmark and the supported/fail/unsupported matrices without creating
calculation modules.

The repository currently retains controlled IS 456 sources but no controlled
IS 2911 companion source or accepted structural pile-cap benchmark. Official
catalogue discovery and previews are scope evidence only. If both prerequisites
cannot be bound, publish `HOLD` with exact reactivation conditions; do not
improvise calculation authority.

## Owner-decision boundaries

- Primary, `e54a`, Excel, the frontmatter lane, and every other retained lane
  stay untouched.
- Public-source distribution permission is already recorded; do not reopen it.
- Pile-cap/raft implementation without accepted GO, cleanup/deletion, release/tag/package
  publication, and professional approval remain separately gated.

## Gate cadence

Run focused source/decision-contract and documentation gates, links, quick
`10/10`, normal hooks, exact-head review, hosted checks, and merge-tree
verification. Broad Python and the full 30-check gate remain deferred to final
INDIA-2 closeout unless a repository-wide failure forces them earlier.

The session entry must contain `Issues encountered` and `Root causes and
resolutions`, with executable evidence for the corrected outcome.

## Efficiency card

- Freeze source identities, benchmark case, decision matrix, and reactivation
  conditions before editing.
- Use one writer, one candidate, one generator pass, one quick gate, one push,
  and one hosted-check cycle.
- Record orientation, implementation, repair, CI wait, closeout, and total
  elapsed workflow time separately.

## Stop rule

Start and finish only decision-only `INDIA-2-FOUNDATION-PILE-CAP-G0`. Do not
begin calculation code, raft, dependency, broad-gate, cleanup, release, or
React work in that lane.
