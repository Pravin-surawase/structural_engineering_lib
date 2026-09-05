# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Inspect the existing Excel workbook and XLL interface, explain its completion boundary, and propose a simple daily workflow before implementation.
- Completed: Read the ribbon, workbook commands, controlled table mapping, sample inputs and installed WP09 evidence. The XLL provides native standalone commands; ETABS import remains pending. Its five ribbon callbacks were reviewed in source because the validated test installation was removed after WP09.; Opened the exact shipped sample in actual Excel and inspected the overview and SA_Members sheets. Closed it without saving and confirmed its unchanged SHA-256 `2c9385900b2d9e1f5b66f315f1e7928d6e83f602d1c559653bec7bebdcaf5ae9`. Excel subsequently exited and its workbook lock file disappeared normally. No XLL was installed/loaded, and ETABS was not attached or modified.; Wrote excel-ui-review.md and incorporated the owner's subsequent decision: one ribbon, native selection/input dialogs, and worksheets only on explicit request. Proposed C# memory plus versioned project persistence replaces the mandatory-sheet assumption; WP10-05 storage requires replan before implementation. Existing engineering owners and legacy workbook compatibility are preserved.
- Recurrence controls: RR-004 x9 / unknown: Admit intake, use shared completion parsing, keep projected prose location-independent, refresh the handoff, and preserve delivery history.; RR-005 x43 / unknown: Use maintained launchers, literal PowerShell blocks, exact paths, native output tools, and one shell per operation.; RR-022 x1 / unknown: Present typed completion and failure outcomes at the UI entry point, and qualify that real user action separately from the command contract.
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. WP10-01 freezes AO16, WP10-02 adds the exact getter port, and
WP10-03 adds bounded operation control and WP10-04 adds offline normalization;
the next packet is WP10-05 transactional Excel import. Its reviewed executable
card now separates installed Excel proof from later production acquisition
handoff, multi-member support and final paired qualification.

| State | Next action / claim boundary |
|---|---|
| **Current** | WP10-04 normalizes the unchanged retained WP10-03 artifact to 97 model records plus 13 action rows, with all getter evidence retained and Python/.NET canonical parity. Its [receipt](../verification/wp10-04-normalization-evidence.json) records offline proof; inspect the exact PR and delivery ledger for subsequent delivery facts. |
| **Next** | Implement WP10-05 from its [reviewed plan card](xll-product/wp10-etabs-read-adapter.md#wp10-05-preparation-review-and-executable-plan--2026-09-05): bounded chunked storage, explicit source binding, shared transaction, cache invalidation and actual Excel save/reopen/rollback. Preserve cardinal insertion and separate modifiers; import readiness does not establish design readiness or live freshness. The new XLL must be installed/preflighted; earlier WP09 cleanup removed its test installation. WP10-05 implementation has not started. |
| **Then** | WP10-05B supplies the missing production acquisition/file handoff; WP10-05C supplies a compatible multi-member profile and real PF9 dataset manifests. WP10-06 qualifies the integrated path only after those prerequisites; a single-member capture does not prove the 100/1,000-member workloads. |
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
