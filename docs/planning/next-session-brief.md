# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Separate calculated beam-steel demand, preliminary bar selection,
- Git receipt: docs/verification/lib-pro-007-p2-supplied-beam-reinforcement-git-handoff-receipt.json | sha256:550e650d38e224d038ffcdc38bb2c8642dfbff16b6715a0ed7ecdb7a22523226 | HOLD
- Git identity: codex/lib-pro-007-p2-supplied-beam-reinforcement@9119cadc1322a718a00dd4e00f5650a21f100af4 | upstream=origin/main@9119cadc1322a718a00dd4e00f5650a21f100af4 | base=origin/main@9119cadc1322a718a00dd4e00f5650a21f100af4 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-007-P2` has a source-bound supplied-beam-reinforcement candidate from exact merged P1 base `9119cadc` |
| **Next** | Complete the frozen P2 verification and hosted merge; then start P3 footing hooks/bends from exact new hosted `main` |
| **Why** | P2 keeps calculated demand, preliminary recommendations, and source-referenced supplied bars separate and makes spacing/depth/anchorage decisive |
| **Held** | P3-P7 implementation, live ETABS, write-back, INDIA-3 engineering, release, branch/worktree deletion, and professional approval |

## P2 outcome

- P1 merged through PR #853 at `9119cadc`; P2 starts from that exact hosted
  main and preserves the INDIA-3 source candidate plus every unrelated lane.
- `evaluate_supplied_beam_reinforcement_v1` evaluates exact supplied bar areas,
  horizontal/vertical clear spacing, effective depth, group clearance, and
  both support anchorages under explicit constraints and provenance.
- Gravity V1 remains additive: old beam bases calculate demand then `HOLD`;
  selection-only bases add a preliminary recommendation; complete reviewed
  bars can reach bounded `PASS`; inadequate complete bars return `FAIL`.
- The maintained open-hall example calculates
  `Ast=2129.575184323628 mm2`, recommends 7-20 mm bars in two layers, and
  remains `HOLD` because no project bar schedule was supplied.
- The shared spacing authority now checks clear distance and retains exact
  spacing before the outcome. The 40.6 mm centre / 24.6 mm clear vector fails
  the 25 mm minimum instead of rounding to a false pass.

## P2 verification boundary

- Run the focused beam/gravity Python/FastAPI/React contracts together, then the
  consolidated quick gate once and normal staged hooks once.
- Verify API manifest/classification, 89-operation/439-schema OpenAPI,
  architecture/imports, docs, and the machine-readable P2 evidence.
- Broad Python/FastAPI/React and full repository gates remain reserved for
  cumulative M0. P2 does not own protected sources, P3, release, professional
  approval, live ETABS, write-back, or INDIA-3 engineering.

## Required Reading

1. [Product-foundation convergence plan](lib-pro-007-product-foundation-convergence.md)
2. [P2 supplied-reinforcement evidence](../verification/lib-pro-007-p2-supplied-beam-reinforcement-evidence.json)
3. [Current task board](../TASKS.md)
4. [API classification](../reference/api-classification.json)
5. [Git workflow single source](../git-automation/git-workflow-single-source.md)
