# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-27
- Focus: Freeze external API findings, audit-gap root causes, peer comparison, and ordered repair packets; runtime fixes and release action remain excluded.
- Completed: Published the evidence-bound LIB-PRO-011 external API readiness audit.; Froze prioritized repair packets and a regression matrix for the next work.; Bound the current session, receipt, and next-session handoff to this task.
- Git receipt: docs/verification/lib-pro-011-external-api-readiness-audit-git-handoff-receipt.json | sha256:d93c07e4680994a2617853f526f912ba91710a1a7f670a1368832bff7f3c5ed7 | HOLD
- Git identity: codex/lib-pro-011-external-api-audit@24221e3bf07ba0267f39ba36b6b87665c5a80d6b | upstream=NONE@UNKNOWN | base=origin/main@6a4683eb8b21bff77f2991230b4458463e61f419 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Latest Handoff

| State | Boundary |
|---|---|
| **Current** | `v0.24.0a1` is released from tag `71b70652`; GitHub and PyPI expose the same exact wheel and sdist hashes. `RELEASE-SMOOTH-001` focused release-control evidence is green after one exact stale-expectation repair, and its one quick gate passed 10/10 |
| **Decision** | The next publish uses one prepared candidate and one exact PR/Weekly run. After review, only one bounded metadata/authorization packet is allowed; authorization must validate final metadata before release tests, and public verification reuses exact workflow UAT instead of repeating it |
| **Next** | Freeze the candidate commit and publish one normal control PR with impact-mapped hosted checks only; do not run Weekly or a broad local suite |
| **Source** | IS 13920:2016 First Revision plus Amendment 1 (2017) and Amendment 2 (2020); reaffirmation is not a new edition and the draft successor is unused |
| **Held** | Beam provided-reinforcement compliance, column derived applicability/non-rectangular/provided-longitudinal checks, whole-joint assessment, walls/foundations, IS 875/1893, INDIA-4 qualified review, source/distribution/support/version/release/professional-use changes, and branch/worktree/archive/source/alias deletion |

## Cumulative M0 result

- The beam benchmark returns 72 mm close-link spacing and explicitly reports
  provided reinforcement as not evaluated. The column benchmarks return
  governing hoop areas 222.28915662650604 mm2 and 277.10843373493975 mm2 with
  caller-confirmed applicability and explicit provided confinement.
- The joint benchmark requires 280 kNm for 200 kNm beam capacity at the fixed
  1.4 factor; 250 kNm returns ratio 0.8928571428571429 and fails. Direction,
  opposing column-capacity direction, factored axial-load basis, applicability,
  and interior/left-exterior/right-exterior topology are explicit.
- Capability truth now states the joint's one-plane/one-direction boundary and
  has 22 known IS 13920 references with zero registration-only references.
  Three families remain `IMPLEMENTED_BOUNDED`; wall and foundation remain held.
- A source-free 0.23.1a2 wheel replays all three benchmarks. The existing
  29-case package UAT passes and retains qualified review required with
  professional approval false. No version or publication action occurred.
- The cumulative Python gate passes 7,024 cases with 3 skipped and 6 deselected;
  FastAPI passes 498. No structural formula or runtime behavior changed in M0.

## Ordered follow-on gates

1. Merge `RELEASE-SMOOTH-001` only after its one focused local batch, one quick
   gate, and impact-mapped PR checks pass. Do not run Weekly for this
   release-control-only packet.
2. For the next selected release, freeze one prepared candidate and run its PR
   and Weekly verification once on the exact head.
3. After exact review or truthful waiver, create one bounded final metadata and
   authorization packet; do not rerun Weekly unless a non-allowlisted path or
   Python content changes.
4. Let TestPyPI and production publication workflows retain their distinct
   protected checks. After matching public hashes to the workflow manifest, run
   public identity-only verification; run full public UAT only if exact workflow
   evidence is missing or identity differs.
5. Keep benchmark replay separate from engineering check and qualified review;
   keep stable/engineering-use wording and professional approval held.
6. Conduct INDIA-4 qualified review before any stable or engineering-use claim,
   then expand in order: IS 13920 walls, foundations, IS 875, then IS 1893.

## Required Reading

1. [M0 cumulative evidence](../verification/india-3-is13920-m0-evidence.json)
2. [G0 decision evidence](../verification/india-3-g0-is13920-audit-decision.json)
3. [Column repair evidence](../verification/india-3-column-r1-evidence.json)
4. [Beam repair evidence](../verification/india-3-beam-r1-evidence.json)
5. [Joint repair evidence](../verification/india-3-joint-r1-evidence.json)
6. [Source metadata repair evidence](../verification/india-3-source-meta-r1-evidence.json)
7. [Indian-code completion order](indian-code-completion-plan.md)
8. [Generated Indian-code capability truth](../verification/indian-code-capability-coverage.json)
9. [Current task board](../TASKS.md)
10. [Bounded release candidate plan](bounded-release-candidate-plan.md)
11. [Replay and engineering-status clarification](../verification/lib-pro-009-is13920-status-semantics.json)
12. [v0.24.0a1 scope freeze](../verification/lib-pro-010-rc-scope-freeze.json)
13. [v0.24.0a1 local artifact evidence](../verification/lib-pro-010-rc-local-artifact.json)
