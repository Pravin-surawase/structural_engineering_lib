# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-19
- Focus: Preserve requested batch calculation inputs and outcomes in an isolated Mac lane.
- Completed: Fetched GitHub main `6aed0d4e` and created a dedicated Mac worktree. The primary checkout remains unchanged at `c822809d`; existing dirty/unknown worktrees are preserved.; Observed the active Windows source-qualification task on `codex/beam-c0a-source-qualification`. Python batch implementation is separate; publication remains dependent on predecessor/shared-document reconciliation.; Corrected the stale batch argument map: automatic and explicit serviceability, tension-steel percentage, all stirrup-zone spacings and complete effective-depth basis now reach the single-beam owner. Nullable depths preserve its defaults.
- Recurrence controls: RR-004 x20 / unknown: Use canonical timed gate commands and admitted delivery transitions; finish location-independent session/handoff records before the candidate.; RR-005 x180 / unknown: Use maintained launchers, exact paths and explicit cwd; inspect actual output envelopes before projecting diagnostic fields.
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
| **API first** | `ETABS-API-GUIDE` and `ETABS-API-READINESS` are merged in #993/#994. The [knowledge handoff plan](../guides/etabs-api-integration.md#completion-plan-and-current-knowledge-boundary) maps every interface, exposes gaps and links fourteen procedures to evidence. Discovery is separate from live qualification. |
| **Next** | Finish/verify the external delivery ledger for `BEAM-PROVISIONAL-REVIEW` before new work. U1–U4 are implemented: one persistent resolver, separate core preview, shared Excel inputs and automatic review/edit/reopen. U5 owns the frozen R01–R12, signed installed and cumulative gates. Evidence: `C:/CodexWork/evidence/beam-provisional-review-20260918`. After its accepted merge, advance C0a source qualification from the [active plan](xll-product/etabs-design-workflow.md#active-implementation-beam-provisional-review--2026-09-18). |
| **Then** | Finish C0a native-unit/material/support/station/load-dependency qualification, then C0c named combined-action/section/support/reinforcement profiles with independent evidence and the remaining C0b core/full states. Cross-model qualification precedes practical alternatives, copied-model reanalysis, automation and portable delivery. Accounting for every beam is not support; PF9 certification stays at project end. |
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
