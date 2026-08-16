# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Merge COMBINED-B unchanged, then publish only the typed Python C workflow
- Git receipt: docs/verification/india-2-foundation-combined-b-git-handoff-receipt.json | HOLD
- Math candidate: codex/india-2-foundation-combined-b@b9cb06f7afe632339c10ab84e17a4d09d0299ade | tree=f5e405ad445f88d019a1c2b064292e6be9b495b6 | independent audit=PASS
- Live integration identity: VERIFY_WITH_GIT_STATE_AND_GITHUB_BEFORE_C
- Next action: START_FRESH_COMBINED_C_ONLY_AFTER_B_MERGE
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-0, INDIA-1, and the INDIA-2-STAIR family are complete |
| **Program** | Umbrella INDIA-2 remains in progress; INDIA-3 and INDIA-4 remain planned |
| **Next** | Begin `INDIA-2-FOUNDATION-COMBINED-C` from verified main after B merges |

## Required Reading

1. [Next-session publication and closeout plan](india-2-next-session-publication-and-closeout-plan.md)
2. [INDIA-2 remaining-elements execution plan](india-2-remaining-is456-elements-plan.md)
3. [Combined B strength evidence](../verification/india-2-foundation-combined-b-strength-evidence.md)
4. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
5. [Current task board](../TASKS.md)
6. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

The historical INDIA-2A-D packets and their cumulative software gate are the
completed `INDIA-2-STAIR` family. Do not reopen them, add another stair topology,
add React, or begin release work without a new owner-approved scope.

`INDIA-2-WALL`, `INDIA-2-STAIR`, `INDIA-2-DEEP`, and `INDIA-2-FLAT` are
accepted only within their recorded bounded cases. Do not reopen or expand
those families while publishing the combined-footing workflow.

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
The foreign retained `e54a` worktree was last observed detached with one dirty
path; its ownership/root cause are unconfirmed, and the next INDIA-2 packet
must not use or mutate it.

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

## INDIA-2-FLAT acceptance result

[`india-2-flat-e-publication-evidence.md`](../verification/india-2-flat-e-publication-evidence.md)
and [`india-2-flat-family-acceptance-evidence.md`](../verification/india-2-flat-family-acceptance-evidence.md)
record the accepted regular interior direct-design and concrete-only punching
workflow, exact public truth, independent benchmark, nested semantic contract,
and focused gates. PR #785 integrated publication and PR #786 accepted the
family. Unequal/exterior/drop/head/opening, patterned-load, moment-transfer,
punching-reinforcement, equivalent-frame, and FEM cases remain held.

## INDIA-2-FOUNDATION-COMBINED G0/A/B result

[`india-2-foundation-combined-g0-scope-evidence.md`](../verification/india-2-foundation-combined-g0-scope-evidence.md)
records GO for exactly two identical square columns with equal concentric loads
on one symmetric rigid rectangular constant-depth footing under externally
approved uniform pressure. Its independent benchmark covers equilibrium,
bearing, longitudinal/transverse actions, flexure/detailing, one-way and
two-way shear, bearing/dowels, and anchorage. General/asymmetric soil
interaction, capacity/settlement calculation, and public capability remain
held. [`india-2-foundation-combined-a-analysis-evidence.md`](../verification/india-2-foundation-combined-a-analysis-evidence.md)
records the typed eligibility, service gross and factored gross/net pressure,
resultant alignment, whole-width critical-section actions, transverse actions,
equilibrium closure, and fail-closed contracts.
[`india-2-foundation-combined-b-strength-evidence.md`](../verification/india-2-foundation-combined-b-strength-evidence.md)
records flexure/minimum/provided steel, spacing/cover/anchorage, one-way shear,
concrete-only punching, bearing/dowels, exact compression development, valid
`FAIL`, unsupported fail-closed behavior, provenance correction, and review
boundary. Public workflow and capability remain held; after B merges, begin
only COMBINED-C.

## Review and gate boundary

Each calculation packet requires focused tests, benchmarks, architecture and PR
checks, plus the quick gate. The expensive full Python and 30-check gate runs
once after the whole accepted INDIA-2 wave is integrated unless an
outcome-changing repository-wide issue appears earlier.

Flat-slab acceptance is complete without expanding topology or adding React.
Combined-footing A/B are complete within the G0 case; COMBINED-C may begin only
after B's unchanged reviewed head merges. Strap, pile-cap, and raft remain
separate later G0 decisions. The two deferred clause-registry truth defects are
recorded in the next-session plan and must not be mixed into C/D.

Cumulative qualified structural-engineering review belongs to INDIA-4 after the
accepted INDIA-2 and INDIA-3 scope is frozen. Packet-level source and engineering
checks still occur before each implementation GO. Software completion does not
grant professional approval, stable-release authorization, engineering-use
authorization, or cleanup authority.

## Exact next action

After verifying B is merged into clean synchronized `main`, create a fresh
`codex/india-2-foundation-combined-c` worktree and implement only the typed
public Python workflow `design_symmetric_combined_footing_is456`, stable
input/provenance/result/status types, executable benchmark, root/services
exports, public API docs, and C evidence. Capability truth must remain 11/10
with combined footing held. FastAPI, semantic/capability promotion, alternate
foundations, React, broad Python, and the 30-check gate remain outside C.
