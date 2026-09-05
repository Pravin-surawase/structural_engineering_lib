# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Deliver Connect ETABS and source-context review as the first bounded WP10-05B unit, aligned with the complete beam design and automation product.
- Completed: Updated the active plan to deliver connection/context and existing-force handoff before actual-bar design orchestration. The B1–B8 contract limits this unit to running-model source geometry, preserving later span mapping, result coverage, controlled reanalysis and overnight-run gates.; Added typed context contracts, a separate exact getter matrix, verified process discovery, bulk source capture, durable raw provenance, a shared process lease and the packaged STA worker. The original force artifact and getter matrix remain compatible.; Added asynchronous Connect ETABS, model details and local frame review with source-ID adjacency. Workbook identity and request identity fence completion; close/unload cancels and evicts context. Heavy data stays in memory and external evidence; connection creates no worksheets and is session-only.
- Recurrence controls: RR-002 x18 / unknown: Freeze acceptance rows and run an exact-host micro-probe before building the host adapter or package.; RR-005 x61 / unknown: Use maintained launchers, literal PowerShell blocks, exact paths, native output tools, and one shell per operation.
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. WP10-01 freezes AO16, WP10-02 adds the exact getter port, and
WP10-03 adds bounded operation control and WP10-04 adds offline normalization;
WP10-05 A/B now adds transparent assumptions and external-snapshot offline
review. WP10-05B now adds running-model connection and source context. Its active
contract separates exact installed Excel proof from later existing-force
handoff, multi-member result qualification and design orchestration.

| State | Next action / claim boundary |
|---|---|
| **Current** | WP10-05B implements Connect ETABS and source-context review through a packaged worker, with source-ID indices in memory and getter evidence outside Excel. Its first profile covers ETABS 23.3.1 kN-m-C geometry; supports, physical spans and forces remain absent. Check the exact delivery ledger and external signed installed receipt before claiming qualification. WP10-05 offline assumptions/snapshot review remains available. |
| **Next** | Complete the remaining WP10-05B existing-force handoff against the verified source binding, then WP10-05C multi-member result coverage and real PF9 dataset manifests. Recheck the final product goal and active connection contract in the WP10 plan before extending capture. Source geometry alone is not a design-ready model. |
| **Then** | Implement audit increment C: map verified source/actions/assumptions into actual-bar design and every dependent check. WP10-06 qualifies the integrated path after acquisition prerequisites; source-frame counts do not prove the 100/1,000-member force workloads. Span/group optimization and owned-copy reanalysis follow the accepted whole-product workflow. |
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
