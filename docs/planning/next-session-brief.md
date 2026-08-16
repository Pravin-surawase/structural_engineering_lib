# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Clause 38.2 beam-flexure truth hygiene
- Baseline: DOC-FRONTMATTER-CONTRACT started from fetched origin/main c8fcd2f0f9b933eb8e8787dc901ee440e05ae984, tree 41d878c0681e5e51d159615d14290d5c3964c822
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested
- Frontmatter outcome: JSON and text modes agree; zero invalid records; 60 permitted legacy/no-frontmatter records unchanged; two direct payload/exit regressions pass
- Scope guard: source-audit every live 38.2 consumer and independently benchmark equilibrium before deciding metadata-only versus arithmetic repair
- Retained lanes: primary, detached dirty e54a, Excel HOLD_UNKNOWN_OWNER, and every other pre-existing lane remain untouched; no cleanup authority exists
- Next action: begin only INDIA-2-TRUTH-HYGIENE-38-2 in a fresh fetched-current-main lane after the frontmatter candidate merges
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; frontmatter contract repair complete on merge |
| **Next** | `INDIA-2-TRUTH-HYGIENE-38-2` only |
| **Later** | Pile-cap G0, raft G0, accepted GO packets, INDIA-2 broad closeout |
| **Held** | Cleanup/deletion, release, React expansion, professional approval, dependency majors |

## Required Reading

1. [Next-session Git/issues/INDIA-2 plan](india-2-next-session-publication-and-closeout-plan.md)
2. [Current task board](../TASKS.md)
3. [IS 456 public-distribution permission](../verification/is456-public-distribution-permission.json)
4. Discover the live clause database, beam flexure, decorator, provenance,
   manifest, and nearest focused-test paths with `rg --files` before reading.

## Exact start

Fetch and verify `origin/main`, then create one fresh
`codex/india-2-truth-hygiene-38-2` worktree. Do not write on primary, reuse the
frontmatter lane, or touch retained worktrees.

```bash
./run.sh session brief --agent structural-engineer
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with fetched `origin/main` before editing.

## Packet order

1. `INDIA-2-TRUTH-HYGIENE-38-2`
   - enumerate every live `38.2` metadata, decorator, result-provenance, test,
     documentation, and generated-manifest consumer;
   - bind each supported identity to the controlled Clause 38.1 or Annex G
     evidence actually used;
   - independently replay rectangular stress-block equilibrium and compare the
     legacy `4.6` approximation with the shared exact helper;
   - change arithmetic only if benchmark evidence proves a supported outcome
     can change.
2. Decision-only `PILE-CAP-G0`, then A-D/acceptance only after accepted `GO`.
3. Decision-only `RAFT-G0`, then any owner-accepted chain.
4. `INDIA-2-CLOSEOUT` with broad Python and the full 30-check gate once.
5. Post-INDIA-2 dependency-major compatibility packets only afterward.

## Frozen Clause 38.2 scope

The open defect is a source/provenance contradiction, not permission to delete
a label mechanically. The clause database, beam decorators,
`calculate_ast_required`, singly/doubly reinforced design, serialized
`sources_used`, tests, docs, and generated manifest must be traced together.

Back-substitute required steel into the exact equilibrium independently. If
the legacy approximation cannot change a supported PASS/FAIL or public result,
leave arithmetic stable and repair only unsupported identities. If it can,
fix the shared root cause with compatibility and benchmark evidence.

Do not copy protected clause prose, mass-replace `38.2`, change unrelated beam
behavior, infer approval from metadata, or expand supported cases.

## Owner-decision boundaries

- Primary, `e54a`, Excel, the frontmatter lane, and every other retained lane
  stay untouched.
- Public-source distribution permission is already recorded; do not reopen it.
- Pile-cap/raft implementation, cleanup/deletion, release/tag/package
  publication, and professional approval remain separately gated.

## Gate cadence

Run focused flexure, traceability, manifest, public-contract, architecture, and
import gates; generate the maintained manifest/indexes once; then run links,
quick `10/10`, normal hooks, exact-head review, hosted checks, and merge-tree
verification. Broad Python and the full 30-check gate remain deferred to final
INDIA-2 closeout unless a repository-wide failure forces them earlier.

The session entry must contain `Issues encountered` and `Root causes and
resolutions`, with executable evidence for the corrected outcome.

## Efficiency card

- Freeze consumers, source identities, benchmark cases, tests, and public
  signatures before editing.
- Use one writer, one candidate, one generator pass, one quick gate, one push,
  and one hosted-check cycle.
- Record orientation, implementation, repair, CI wait, closeout, and total
  elapsed workflow time separately.

## Stop rule

Start and finish only `INDIA-2-TRUTH-HYGIENE-38-2`. Do not begin pile-cap,
raft, dependency, broad-gate, cleanup, release, or React work in that lane.
