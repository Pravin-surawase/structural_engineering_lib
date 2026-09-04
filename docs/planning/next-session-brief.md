# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-04
- Focus: Reconstruct why WP09 consumed about 6.5 hours, distinguish necessary installed-product qualification from preventable rework, implement controls that would have changed the delivery outcome, and re-sequence WP10 without weakening Excel or ETABS acceptance.
- Completed: Reconstructed the WP09 scope, commit and hosted-check timeline, duration limits, repair classes, and the root causes behind repeated candidate cycles.; Added a hosted-equivalent pre-freeze candidate-integrity command and explicit timed-task closeout guidance, with focused regression coverage.; Recorded the postmortem and updated the WP09/WP10 plans so later host work uses bounded slices, an early host micro-probe, staged acceptance, and one consolidated repair boundary.
- Recurrence controls: WP09's repeated families were late acceptance boundaries, host assumptions, evidence normalization/rebinding, session/handoff state, and Windows command shapes. The postmortem now records each small issue and its prevention rule, including valid product defects that must remain in acceptance.; Every future `session begin` reads the bounded recurrence controls generated from the newest entry. Closeout fails if the entry omits issues, root causes, or recurrence controls.; Subagents receive the relevant controls in their bounded packet and return issues, root causes, and proof. The parent writes one deduplicated versioned entry so parallel agents do not create conflicting log blocks.
- Git receipt: docs/verification/wp09-postmortem-controls-git-handoff-receipt.json | sha256:e1d3c72274ae596288d7eff1483b2d5f1510fc9c6f1e6323376d1ce82188f021 | HOLD
- Git identity: codex/wp09-postmortem-controls@ac1bd2b3e38f61b165504331ea35e5642cd49860 | upstream=NONE@UNKNOWN | base=origin/main@ac1bd2b3e38f61b165504331ea35e5642cd49860 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. The next packet is WP10's getter-only ETABS read adapter.

| State | Next action / claim boundary |
|---|---|
| **Current** | IMP-M1 WP01–WP08 and IMP-M2 WP09 are implemented and qualified. The native Python/.NET libraries now feed the standalone Excel-DNA XLL, versioned workbook tables, explicit bulk commands, rollback/freshness, sample workbook and installed lifecycle. |
| **Next** | Execute WP10-01 from the ready WP10 plan: freeze portable ETABS snapshot contracts and shared Python/.NET fixtures before adding the optional Windows CSI adapter. |
| Definition boundary | PF0–PF11 remains the approved requirements, semantics, signature, assurance, application, packaging, migration and implementation-order authority. |
| Application boundary | Excel and ETABS remain adapters. Worksheet calculations consume immutable validated data; live COM and mutations are explicit application commands. |
| Implementation boundary | WP10 reads model metadata, geometry, assignments and selected analysis results through a getter-only STA broker. It must not alter units, result selection, the attached model or analysis state. |
| Release boundary | Package publication and GitHub releases retain the repository's separate per-release authorization and evidence process. |

## Implementation order

1. IMP-M1: WP01–WP08 pure dual-language libraries are implemented and qualified.
2. IMP-M2: WP09 now delivers the standalone Excel XLL, workbook and installed
   evidence.
3. IMP-M3: WP10–WP12 deliver getter-only ETABS intake, copied-model reanalysis,
   migration, performance and release readiness.

## Required Reading

1. [WP10 ETABS read-adapter plan](xll-product/wp10-etabs-read-adapter.md)
2. [PF11 implementation blueprint](xll-product/library-definition/pf11/README.md)
3. [WP09 standalone Excel plan](xll-product/wp09-standalone-excel.md)
4. [Native library and Excel status](../library/implementation-status.md)
5. [Library getting started](../library/getting-started.md)
6. [Structural Library Definition Programme](xll-product/library-definition/README.md)
7. [Decision register](xll-product/library-definition/decision-register.json)
8. [Current XLL plan](xll-product/current-plan.md)
9. [Automation requirements](xll-product/automation/README.md)
10. [Newest session entry](../SESSION_LOG.md)
11. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
