# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-04
- Focus: Deliver WP09 standalone Windows Excel over the completed native libraries
- Git receipt: WP01–WP08 merged by PR 962 at `1b9da3165cc4fed12a87af9bca553ed51f04fa57`
- Current branch: `codex/wp09-standalone-excel`
- Next action: implement and qualify the WP09 function, command, workbook, package, installed-lifecycle and performance slices
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 now implements WP01–WP08 as native
Python and .NET libraries with common semantic contracts, independently testable
calculations and host-free orchestration. WP09 is the next packet and owns the
standalone Windows Excel product around those libraries.

| State | Next action / claim boundary |
|---|---|
| **Current** | IMP-M1 WP01–WP08 is implemented: portable contracts, flexure, shear, torsion, analysis, serviceability, detailing, full member/bar paths, construction outputs and finite-domain optimization are present in Python and .NET. |
| **Next** | Execute WP09 as one standalone Excel milestone: pure worksheet projections, versioned workbook tables, explicit bulk commands, rollback/freshness, sample workbook, installed lifecycle and measured performance. |
| Definition boundary | PF0–PF11 remains the approved requirements, semantics, signature, assurance, application, packaging, migration and implementation-order authority. |
| Application boundary | Excel and ETABS remain adapters. Worksheet calculations consume immutable validated data; live COM and mutations are explicit application commands. |
| Implementation boundary | WP09 uses the completed native libraries and owns AO23, AO25, PF8 worksheet projections and XL-CMD-01/03/04/06/07. Live ETABS begins only in WP10. |
| Release boundary | Package publication and GitHub releases retain the repository's separate per-release authorization and evidence process. |

## Implementation order

1. IMP-M1: WP01–WP08 pure dual-language libraries are implemented and qualified.
2. IMP-M2: WP09 now delivers the standalone Excel XLL, workbook and installed
   evidence.
3. IMP-M3: WP10–WP12 deliver getter-only ETABS intake, copied-model reanalysis,
   migration, performance and release readiness.

## Required Reading

1. [PF11 implementation blueprint](xll-product/library-definition/pf11/README.md)
2. [WP09 standalone Excel plan](xll-product/wp09-standalone-excel.md)
3. [WP01–WP08 library status](../library/implementation-status.md)
4. [Library getting started](../library/getting-started.md)
5. [Structural Library Definition Programme](xll-product/library-definition/README.md)
6. [Decision register](xll-product/library-definition/decision-register.json)
7. [Current XLL plan](xll-product/current-plan.md)
8. [Automation requirements](xll-product/automation/README.md)
9. [Newest session entry](../SESSION_LOG.md)
10. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
