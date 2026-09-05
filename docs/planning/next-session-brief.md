# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Review the next work against implemented code and installed evidence, correct the plan's current state, and define an executable WP10-05 Excel-import packet with truthful later acquisition and scale requirements. Planning only; no product changes, added tests, COM attachment or workbook writes.
- Completed: Confirmed WP10-04's merged output and traced missing XL-CMD-02 through the workbook enum, command/ribbon, input reader, transaction and freshness owners. Distinguished real WP09 Excel and WP10-02/03 ETABS evidence from WP10-04's offline replay and from future installed proof.; Added a source-backed WP10-05 plan with bounded text-chunk storage, explicit project/member bindings, atomic readback/rollback, stale-result prevention, target identity/cancellation rules and X1–X10 software/installed acceptance. An in-memory 93-chunk round-trip of the exact 1,669,798-byte retained output preserved its receipt SHA; this proves storage feasibility only.; Named the missing production acquisition/file handoff as WP10-05B and multi-member profile/dataset preparation as WP10-05C before WP10-06. Preserved the original PF9 100/1,000-member workload sizes, p95 limits and memory limit. Updated current plan entry points and the next-session handoff accordingly.
- Recurrence controls: RR-021 x1 / unknown: Trace every acceptance workload through real source callers; assign missing consumer and scale work before qualification, keeping original budgets intact.; RR-005 x40 / unknown: Use maintained launchers, literal PowerShell blocks, exact paths, native output tools, and one shell per operation.
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
