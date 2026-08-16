# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Implement only bounded strip flexure, caller-provided straight bars,
- Git receipt: docs/verification/india-2-flat-c-git-handoff-receipt.json | sha256:c6e826371e25316605ec5c9127fbe91481f5d37c46c00e9e0634cf772b36301d | HOLD
- Git identity: codex/india-2-flat-c@0603f853124b8cba5a4b5f48686aef9ee1e097e7 | upstream=origin/main@0603f853124b8cba5a4b5f48686aef9ee1e097e7 | base=origin/main@0603f853124b8cba5a4b5f48686aef9ee1e097e7 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: WAIT_FOR_EXACT_HEAD_AUDIT
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-0, INDIA-1, and the INDIA-2-STAIR family are complete |
| **Program** | Umbrella INDIA-2 remains in progress; INDIA-3 and INDIA-4 remain planned |
| **Next** | Finish `INDIA-2-FLAT-E`, integrate it unchanged after green checks, then run flat-slab focused family acceptance |

## Required Reading

1. [INDIA-2 remaining-elements execution plan](india-2-remaining-is456-elements-plan.md)
2. [Canonical Indian-code completion waves](indian-code-completion-plan.md)
3. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
4. [Current task board](../TASKS.md)
5. [INDIA-2 staircase cumulative evidence](../verification/india-2-cumulative-gate-evidence.md)
6. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

The historical INDIA-2A-D packets and their cumulative software gate are the
completed `INDIA-2-STAIR` family. Do not reopen them, add another stair topology,
add React, or begin release work without a new owner-approved scope.

`INDIA-2-WALL` is accepted through one regular 100-200 mm thick, one-grid,
braced empirical vertical-compression workflow. WALL-A-D are integrated and the
focused family receipt is
[`india-2-wall-family-acceptance-evidence.md`](../verification/india-2-wall-family-acceptance-evidence.md).
Do not expand the accepted wall topology while implementing flat-slab packets.

```bash
./run.sh session brief --agent orchestrator
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Require a clean fresh branch from verified current `origin/main` and
`source_bound=true`. Preserve every unrelated worktree. Branch, remote-ref, or
worktree cleanup remains a separate exact-target authorization.

## INDIA-2-WALL acceptance result

[`india-2-wall-family-acceptance-evidence.md`](../verification/india-2-wall-family-acceptance-evidence.md)
records the integrated A-D head, public clause/source visibility, independent
benchmark, unsafe and fail-closed behavior, semantic-contract correction,
focused validation, retained holds, and deferred broad-gate boundary.

## INDIA-2-DEEP-G0 decision result

[`india-2-deep-g0-scope-evidence.md`](../verification/india-2-deep-g0-scope-evidence.md)
records GO for one simply supported solid rectangular deep-beam positive-
reinforcement check. [`india-2-deep-a-geometry-evidence.md`](../verification/india-2-deep-a-geometry-evidence.md)
records the implemented typed effective-span, classification, lever-arm,
caller-action, and fail-closed contracts. [`india-2-deep-b-reinforcement-evidence.md`](../verification/india-2-deep-b-reinforcement-evidence.md)
records the required/provided positive tie, placement, continuity, anchorage,
side-face, and composed checks. [`india-2-deep-c-public-workflow-evidence.md`](../verification/india-2-deep-c-public-workflow-evidence.md)
records the typed public Python composition, executable benchmark, public API
docs, and retained holds. [`india-2-deep-d-publication-evidence.md`](../verification/india-2-deep-d-publication-evidence.md)
records the thin transport and truthful capability/semantic/manifest
publication over that exact workflow. The focused family acceptance receipt is
[`india-2-deep-family-acceptance-evidence.md`](../verification/india-2-deep-family-acceptance-evidence.md).
Bearing and compression-nodal regions require a caller-supplied external verification;
continuous beams, openings, hanging action, negative moment, load generation,
generalized strut-and-tie, nonlinear analysis, and FEM remain held.

## INDIA-2-FLAT-G0 decision result

[`india-2-flat-g0-scope-evidence.md`](../verification/india-2-flat-g0-scope-evidence.md)
records GO for one equal-span square interior panel under identical uniform
gravity loading, using the direct design method and one centred square-column
punching check. The frozen hand benchmark covers eligibility, both directional
moment distributions, flexure, straight-bar detailing, reviewed no-drop
span/depth, and no-reinforcement punching. Unequal/exterior/drop/head/opening,
patterned-load, moment-transfer, punching-reinforcement, equivalent-frame, and
FEM cases remain held.

## INDIA-2-FLAT-A implementation result

[`india-2-flat-a-geometry-evidence.md`](../verification/india-2-flat-a-geometry-evidence.md)
records typed grid/panel/material/load contracts, both clear-span and strip
directions, direct-design eligibility, exact Clause 31 identifier registration,
and fail-closed behavior for every topology outside G0. Flat slab remains held
until FLAT-E publication.

## INDIA-2-FLAT-B implementation result

[`india-2-flat-b-moment-evidence.md`](../verification/india-2-flat-b-moment-evidence.md)
records the both-direction total static, interior negative/positive, and
column/middle-strip moment distribution. It reproduces every frozen hand value,
preserves distribution totals, and retains the FLAT-A topology and load gates.
Flat slab remains held until FLAT-E publication.

## INDIA-2-FLAT-C implementation result

[`india-2-flat-c-reinforcement-evidence.md`](../verification/india-2-flat-c-reinforcement-evidence.md)
records both-direction strip flexure, minimum and caller-provided straight bars,
the 1650 mm no-drop support-top extension, and the reviewed 23.0769/23.4
span/depth comparison. Direct deflection, crack width, punching, and public
workflow remain held.

## INDIA-2-FLAT-D implementation result

[`india-2-flat-d-punching-evidence.md`](../verification/india-2-flat-d-punching-evidence.md)
records the centred square interior-column full-perimeter demand, concrete-only
capacity, punching-reinforcement-or-redesign disposition, mandatory-redesign
boundary, and fail-closed support-reaction/applicability contracts. PR #784
merged as `d1884946`. Alternate columns/perimeters, openings, moment transfer,
and punching-reinforcement design remain held.

## INDIA-2-FLAT-E publication candidate

[`india-2-flat-e-publication-evidence.md`](../verification/india-2-flat-e-publication-evidence.md)
records the typed Python composition, thin REST route, canonical capability and
semantic truth, manifest promotion, full nested OpenAPI result, benchmark, and
retained holds. It must pass exact-head local audit and hosted checks before
integration; family acceptance remains a separate packet from the integrated
head.

## Review and gate boundary

Each calculation packet requires focused tests, benchmarks, architecture and PR
checks, plus the quick gate. The expensive full Python and 30-check gate runs
once after the whole accepted INDIA-2 wave is integrated unless an
outcome-changing repository-wide issue appears earlier.

Deep-beam acceptance and flat-slab G0/A-D are complete. Finish FLAT-E without
expanding topology or adding React, then run the focused flat-slab family
acceptance packet. Foundation programs follow as separate G0 decisions.

Cumulative qualified structural-engineering review belongs to INDIA-4 after the
accepted INDIA-2 and INDIA-3 scope is frozen. Packet-level source and engineering
checks still occur before each implementation GO. Software completion does not
grant professional approval, stable-release authorization, engineering-use
authorization, or cleanup authority.
