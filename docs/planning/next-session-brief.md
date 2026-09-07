# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-07
- Focus: Finish the product's read-only ETABS force handoff, multi-member data and integrated qualification against the whole-product goal; learning excluded.
- Completed: Implemented WP10's complete group acquisition, explicit model interpretation, versioned compact transport and production Excel worker/store handoff.; Verified actual reference and 1,000-member / 100,000-row capture, exact offline reopen and cancellation, plus independent Python replay and source equality.; Reconciled the final functional completion contract and deferred PF9 speed/ memory work to WP10-PERF-FINAL under the owner's amended order.
- Recurrence controls: RR-003 x7 / unknown: Finish code, docs and generated projections before freeze; serialize mutations against formatting, then run read-only integrity after acceptance.; RR-033 x1 / unknown: Replay historical transport from its exact retained dossier; validate current exports using their own source-bound identities without regenerating or weakening frozen evidence.; RR-004 x13 / unknown: Use canonical timed gate commands and admitted delivery transitions; finish location-independent session/handoff records before the candidate.
- Git receipt: docs/verification/wp10-completion-git-handoff-receipt.json | sha256:ec3be6c11afce308699647311e715e99092de788f94d50eb9a8f017246cc8551 | HOLD
- Git identity: codex/wp10-completion@8927740cf7929ea53dab0b4e7f8e1df200825e24 | upstream=NONE@UNKNOWN | base=origin/main@c822809ddc0252816c71791825c60b2f07aac48c | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. WP10-01 freezes AO16, WP10-02 adds the exact getter port, and
WP10-03 adds bounded operation control and WP10-04 adds offline normalization;
WP10-05 A/B now adds transparent assumptions and external-snapshot offline
review. WP10-COMPLETION implements running-model connection, complete group
force handoff, bounded compact snapshots and source interpretation. Its active
contract separates exact installed/hosted acceptance from later design
orchestration and the owner's deferred project-end performance qualification.

| State | Next action / claim boundary |
|---|---|
| **Current** | WP10's complete production group capture and worker/store passed the actual 153/3,502 reference and 1,000/100,000 medium member/row workloads, exact offline reopen and cancellation. Heavy data remains outside worksheets; support/span ambiguities stay explicit. Final signed installed and hosted results are exact-candidate external receipts. |
| **Next** | Read the WP10-COMPLETION delivery ledger and external installed/PR handoff. If its required gates are unfinished, close them first; after acceptance plan WP11's public assumptions/actions mapper and actual-bar member design orchestration. Do not repeat completed capture implementation or resume deferred timing experiments. |
| **Then** | Add bounded multi-option design search, supported physical-span/group constraints, controlled owned-copy ETABS reanalysis and baseline comparison. Overnight automation depends on these services. PF9 timing/working-set certification resumes as WP10-PERF-FINAL at project end; existing targets and failed evidence remain unchanged. |
| Definition boundary | PF0–PF11 remains the approved requirements, semantics, signature, assurance, application, packaging, migration and implementation-order authority. |
| Application boundary | Excel and ETABS remain adapters. Worksheet calculations consume immutable validated data; live COM and mutations are explicit application commands. |
| Implementation boundary | WP10-01 is pure offline validation, WP10-02 is the exact getter-only host boundary, and WP10-03 is the bounded acquisition-control boundary. WP10-04 adds offline projection and normalization without COM or Excel. The pure analysis package must not depend on the optional ETABS assembly. |
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
