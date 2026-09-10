# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-10
- Focus: Explain row/storage limits and implement lightweight connection plus requested-member acquisition under caller budgets.
- Completed: Started from fetched main `307e3359` in an isolated admitted worktree, preserving the primary checkout's unrelated edit and all predecessor lanes.; Traced capture, transport, decoded memory, workbook references and explicit writes. Import keeps full admitted snapshots outside worksheets; the viewer and explicit selected-member report both include every captured member row. The 100,000-row/1,000-member/64 MiB admission envelope remains unchanged.; Replaced production All-group force dispatch with exact requested-object calls and preflight/incremental caller row budgets. Existing bulk/group schemas, default envelopes and complete-row accounting remain available. The qualified fixture returned one requested member's 51 rows through one object force call; cancellation and exact offline reopening passed.
- Recurrence controls: RR-041 x1 / unknown: Route force calls by explicit requested members and enforce caller admission during capture; retain complete-result accounting and reject partial snapshots.; RR-002 x34 / unknown: Probe exact host boundaries and ownership before acceptance; verify cleanup of owned child processes and resources explicitly.; RR-042 x2 / unknown: Use the producing codec or its observed exact wire schema for retained evidence; test portable wire round trips before live acceptance.
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. WP10-01 freezes AO16, WP10-02 adds the exact getter port, and
WP10-03 adds bounded operation control and WP10-04 adds offline normalization;
WP10-05 A/B now adds transparent assumptions and external-snapshot offline
review. WP10-COMPLETION implements running-model connection, complete group
force handoff, bounded compact snapshots and source interpretation. It completed
functional installed/hosted acceptance in PR #981. WP11 A and B completed
their bounded native and installed Excel acceptance in PRs #982 and #983.
The owner's [model-coverage and future-issue sequence](xll-product/etabs-design-workflow.md#model-coverage-and-future-issues--2026-09-10)
now controls the next work; performance certification remains at project end.

| State | Next action / claim boundary |
|---|---|
| **Current** | The [bounded acquisition packet](xll-product/etabs-design-workflow.md#bounded-acquisition-and-excel-data-flow--2026-09-10) adds a 33-getter overview, explicit detailed handoff and exact requested-object forces with caller row admission. Overview, force import and explicit sheet writes have separate meanings. The large model is overview-qualified; its current dynamic selections and native API units are not admitted by the existing detailed-force profile. Exact delivery state is external. |
| **Next** | Continue C0a from the [second-model observations](xll-product/etabs-design-workflow.md#second-model-observations-and-revised-next-work--2026-09-10): native-unit detailed geometry, raw-shape handling, modeling-aid roles, support/material/station facts and selected-load dependency semantics. Then measure admitted object workloads for a batch planner and larger storage/viewing scopes. Preserve snapshot meanings and continue independent-model/holdout intake. |
| **Then** | C0b separates core completion from pending checks; C0c qualifies named combined-action/section/support/reinforcement profiles. Cross-model evidence precedes practical alternatives, copied-model reanalysis, automation and portable delivery. Accounting for every beam is not support; PF9 certification stays at project end. |
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
