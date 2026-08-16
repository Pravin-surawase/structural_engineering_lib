# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Merge STRAP-B unchanged, then begin only STRAP-C public Python workflow
- Combined acceptance: PR #792 squash-merged as 8e039b112e38436fcae36326b46afa9c436fb970; tree=873aea4cdca8aa9633b30a7c9b74138e5a73a6ce
- STRAP-G0: PR #793 squash-merged as 70cd2894485d88b72d22544ee18533733789d0f1; audited tree=60d5636265e157e723236909b1de7f582791b297
- STRAP-A: PR #794 squash-merged as c410b28024e44e3e2670c8b359b69ae29165f2ae; audited tree=08899dbedd35e3d0b0e2c9ba2e78813d87be1f70
- STRAP-B: exact strap strength/detailing composition implemented; public Python/FastAPI remain held
- Next action: START_STRAP_C_ONLY_AFTER_B_MERGE
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-0, INDIA-1, and the INDIA-2-STAIR family are complete |
| **Program** | Umbrella INDIA-2 remains in progress; INDIA-3 and INDIA-4 remain planned |
| **Next** | Begin `INDIA-2-FOUNDATION-STRAP-C` only after STRAP-B merges unchanged |

## Required Reading

1. [Next-session publication and closeout plan](india-2-next-session-publication-and-closeout-plan.md)
2. [INDIA-2 remaining-elements execution plan](india-2-remaining-is456-elements-plan.md)
3. [STRAP-G0 scope decision](../verification/india-2-foundation-strap-g0-scope-evidence.md)
4. [Combined focused family acceptance](../verification/india-2-foundation-combined-family-acceptance-evidence.md)
5. [Combined D publication evidence](../verification/india-2-foundation-combined-d-publication-evidence.md)
6. [Combined C public-workflow evidence](../verification/india-2-foundation-combined-c-public-workflow-evidence.md)
7. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
8. [Current task board](../TASKS.md)
9. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

The historical INDIA-2A-D packets and their cumulative software gate are the
completed `INDIA-2-STAIR` family. Do not reopen them, add another stair topology,
add React, or begin release work without a new owner-approved scope.

`INDIA-2-WALL`, `INDIA-2-STAIR`, `INDIA-2-DEEP`, and `INDIA-2-FLAT` are
accepted only within their recorded bounded cases. Do not reopen or expand
those families while implementing the bounded strap-footing sequence.

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

## INDIA-2-FLAT acceptance result

[`india-2-flat-e-publication-evidence.md`](../verification/india-2-flat-e-publication-evidence.md)
and [`india-2-flat-family-acceptance-evidence.md`](../verification/india-2-flat-family-acceptance-evidence.md)
record the accepted regular interior direct-design and concrete-only punching
workflow, exact public truth, independent benchmark, nested semantic contract,
and focused gates. PR #785 integrated publication and PR #786 accepted the
family. Unequal/exterior/drop/head/opening, patterned-load, moment-transfer,
punching-reinforcement, equivalent-frame, and FEM cases remain held.

## INDIA-2-FOUNDATION-COMBINED G0/A-D result

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
boundary. [`india-2-foundation-combined-c-public-workflow-evidence.md`](../verification/india-2-foundation-combined-c-public-workflow-evidence.md)
records the canonical typed composition, immutable public types, executable
benchmark, complete caller-basis provenance, retained holds, and public API
docs. [`india-2-foundation-combined-d-publication-evidence.md`](../verification/india-2-foundation-combined-d-publication-evidence.md)
records the strict nested transport, thin public route, exact OpenAPI drift,
and capability/semantic/manifest promotion to one supported bounded workflow.
[`india-2-foundation-combined-family-acceptance-evidence.md`](../verification/india-2-foundation-combined-family-acceptance-evidence.md)
records the integrated G0/A-D chain, frozen and independent non-frozen
benchmarks, valid failures, every maintained fail-closed boundary, truthful
public surface, focused gates, and retained review/approval holds.

## Review and gate boundary

Each calculation packet requires focused tests, benchmarks, architecture and PR
checks, plus the quick gate. The expensive full Python and 30-check gate runs
once after the whole accepted INDIA-2 wave is integrated unless an
outcome-changing repository-wide issue appears earlier.

Using the accepted cadence: run focused gates for every packet, with broad
Python and the full 30-check repository gate only at the final INDIA-2
integration boundary unless a confirmed repository-wide failure forces them
earlier.

Flat-slab acceptance is complete without expanding topology or adding React.
Combined footing is accepted within the bounded case. Strap G0 is GO within
its separate bounded model; pile-cap and raft remain later G0 decisions. The
two deferred clause-registry truth defects are recorded in the next-session
plan and must not be mixed into STRAP-A-D or strap acceptance.

Cumulative qualified structural-engineering review belongs to INDIA-4 after the
accepted INDIA-2 and INDIA-3 scope is frozen. Packet-level source and engineering
checks still occur before each implementation GO. Software completion does not
grant professional approval, stable-release authorization, engineering-use
authorization, or cleanup authority.

## Exact next action

After verifying STRAP-B merged unchanged into current `origin/main`, create a
fresh STRAP-C lane. Publish only the typed Python composition, immutable
provenance/result/status types, canonical exports, executable frozen benchmark,
and public API documentation over A/B. FastAPI, capability promotion, React,
broad Python, and the 30-check gate remain outside STRAP-C.
