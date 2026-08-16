---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-CLOSEOUT
---

# INDIA-2 Final Closeout Evidence

## Closeout decision

**CLOSE INDIA-2 within its explicitly bounded accepted/held scope.** Six
families are accepted only for the cases recorded below: wall, staircase, deep
beam, flat slab with column punching, combined footing, and strap footing.
Pile-cap and raft remain `HELD / NOT_IMPLEMENTED`; their G0 decisions created
no calculation or publication workflow and record exact reactivation gates.

This closeout adds no structural calculation, service, API, React, capability,
release, cleanup, or professional-approval behavior. “Complete” does not mean
complete IS 456 coverage, qualified engineering approval, or release authority.

## Exact starting tree and truth target

- Fresh closeout base: `d28852156752ea6e44b0c9fbb67988088851bf3e`,
  tree `38958c8a484d5f63a1092b2e852af64bef7afc2a`.
- Runtime diagnosis: `source_bound=true`.
- Local Git authority: clean linked worktree, no operation marker, zero
  ahead/behind against `origin/main`, and `READY_LOCAL` before editing.
- Generated truth target: 13 supported and 8 held families; 81/81 public
  endpoints directly tested; pile-cap and raft have no public workflow.

## Accepted family evidence index

| Family | Source and frozen benchmark | Publication and focused acceptance | Integrated acceptance receipt |
|---|---|---|---|
| Wall | [G0 scope](india-2-wall-g0-scope-evidence.md), `IS456-2000-A6`, `INDIA-2-WALL-HAND-01` | [D publication](india-2-wall-d-publication-evidence.md); [135-test acceptance](india-2-wall-family-acceptance-evidence.md); [Git receipt](india-2-wall-acceptance-git-handoff-receipt.json) | PR #773, merge `90ea7c1e4adf05c04e986dc3657e0403d598930d`, tree `1512923877c29d1bb0da6ffe849a9bfd28f890bd` |
| Staircase | [G0 scope](india-2a-staircase-scope-evidence.md), controlled Clause 33 sources, NPTEL `NPTEL-M9L20-EX9.1` | [D publication](india-2d-staircase-publication-evidence.md); [cumulative acceptance](india-2-cumulative-gate-evidence.md); [Git receipt](india-2-cumulative-git-handoff-receipt.json) | PR #764, merge `9d68f53e70dc088c3ee7034ca99d0ed1c418717a`, tree `ee3934183b96ed9bdf4c204a99cb25951f9a1cbc` |
| Deep beam | [G0 scope](india-2-deep-g0-scope-evidence.md), controlled Clause 29/Amendment 3 sources, `INDIA-2-DEEP-HAND-01` | [D publication](india-2-deep-d-publication-evidence.md); [157-test acceptance](india-2-deep-family-acceptance-evidence.md); [Git receipt](india-2-deep-acceptance-git-handoff-receipt.json) | PR #779, merge `f7eb91c3f2719dd04e5739e67572e9530b60ad3e`, tree `507d47576e8c85b6cdcaafcc31df1a7fa3a1b4a6` |
| Flat slab/punching | [G0 scope](india-2-flat-g0-scope-evidence.md), controlled Clause 31/Figure 16 sources, `INDIA-2-FLAT-HAND-01` | [E publication](india-2-flat-e-publication-evidence.md); [214-test acceptance](india-2-flat-family-acceptance-evidence.md); [Git receipt](india-2-flat-acceptance-git-handoff-receipt.json) | PR #786, merge `3f82e7e26b6df60a7c18dff90aa9f4d00c42bcfe`, tree `81b9c61fbe94da1863571f99b72f553d77a02b62` |
| Combined footing | [G0 scope](india-2-foundation-combined-g0-scope-evidence.md), controlled IS 456 plus NPTEL rigid-method source, `INDIA-2-COMBINED-HAND-01` | [D publication](india-2-foundation-combined-d-publication-evidence.md); [84-family/339-focused acceptance](india-2-foundation-combined-family-acceptance-evidence.md); [Git receipt](india-2-foundation-combined-acceptance-git-handoff-receipt.json) | PR #792, merge `8e039b112e38436fcae36326b46afa9c436fb970`, tree `873aea4cdca8aa9633b30a7c9b74138e5a73a6ce` |
| Strap footing | [G0 scope](india-2-foundation-strap-g0-scope-evidence.md), controlled IS 456 plus independent equilibrium source, `INDIA-2-STRAP-HAND-01` | [D publication](india-2-foundation-strap-d-publication-evidence.md); [85-family acceptance](india-2-foundation-strap-family-acceptance-evidence.md); [Git receipt](india-2-foundation-strap-acceptance-git-handoff-receipt.json) | PR #798, merge `f56e1ec312902caf98e872c77ce8b71bdbc8440e`, tree `28698a28d96f3e5cbad26fd6964cf835cda6e1b4` |

Every accepted result retains explicit units, source/clause identity, frozen
benchmark identity, qualified-review truth, and machine-visible exclusions.
Each linked family receipt states the exact supported topology and the valid
unsafe and out-of-domain behavior that was replayed before acceptance.

## Held foundation decisions

| Family | Decision and blocker | Integrated receipt | Reactivation boundary |
|---|---|---|---|
| Pile cap | [G0 HOLD](india-2-foundation-pile-cap-g0-hold-evidence.md): no controlled IS 2911 companion source and no accepted independently replayable structural two-pile-cap benchmark | PR #804, merge `def0b493e33fa566fd3f23bf166287fcda6169d6`, tree `7da91c66143e83933a88bb9a4d5396bede89cf6d`; [Git receipt](india-2-foundation-pile-cap-g0-git-handoff-receipt.json) | Acquire and bind the authenticated companion source, choose one action model, and accept the complete frozen benchmark before a new G0 may return `GO` |
| Raft | [G0 HOLD](india-2-foundation-raft-g0-hold-evidence.md): no controlled IS 2950 source/amendment binding and no accepted independently replayable structural raft benchmark | PR #805, merge `d28852156752ea6e44b0c9fbb67988088851bf3e`, tree `38958c8a484d5f63a1092b2e852af64bef7afc2a`; [Git receipt](india-2-foundation-raft-g0-git-handoff-receipt.json) | Acquire and bind the authenticated source/amendment set and accept a complete regular rigid-raft structural benchmark before a new G0 may return `GO` |

Official catalogue pages, previews, method descriptions, and unsolved examples
remain discovery evidence only. They are not implementation authority and do
not satisfy either reactivation contract.

## Cross-cutting truth correction

Before foundation decisions, Clause 38.2 metadata/provenance and the rounded
inverse stress-block false-safe were corrected and independently replayed. PR
#803 merged as `1139e9ea06751c72b66098a575c1f5e327c56ef5`, tree
`0abefcd0255157bd1444549f2066eb937f45e5a0`; the exact evidence is
[INDIA-2 truth hygiene 38.2](india-2-truth-hygiene-38-2-evidence.md).

## Final cumulative validation

- Initial `./run.sh test`: 6,301 passed and 11 failed because older golden and
  isolated-footing tests still froze the approximate stress-block values
  corrected by PR #803. After independent exact-equilibrium replay and a
  test/data-only repair, the required corrective rerun **PASSed** with 6,312
  passed, 3 skipped, and 6 deselected in 50.59 seconds.
- Initial `./run.sh check`: 29/30 passed and exposed a generated public API
  manifest that omitted the five already-integrated strap-footing exports.
  After regenerating only that maintained artifact, the required corrective
  full-gate rerun **PASSed 30/30** in 11.0 seconds.
- Final focused truth, frontmatter, links, parity, index, and quick-gate checks
  pass after the closeout documentation is frozen.
- Required hosted checks must pass on the unchanged reviewed closeout head.
- The closeout Git receipt binds the exact candidate head/tree; the squash
  merge is accepted only when its tree is identical to that audited tree.

## Final boundary

INDIA-2 stops here. INDIA-3 companion-code work, dependency-major work,
qualified cumulative engineering review, stable release, package/tag/GitHub
publication, branch/worktree retirement, and professional approval require
separate authorization.
