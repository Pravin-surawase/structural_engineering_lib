# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Refine the owner's overnight automation draft, populate development inputs, and show explicit ribbon stages sharing one future orchestrator.
- Completed: Added demo-beam-preset.json with editable example material, cover, exposure, fire, aggregate, bar/layer/stock, section catalogue and synthetic rate inputs. The preset retains demo provenance and cannot overwrite actual model facts or establish a real-project design approval.; Updated excel-ui-review.md and etabs-design-workflow.md: Connect ETABS, Get Forces, Design, Optimise, Solver Check, Update & Recheck, Auto Run, Compare Runs and Assumptions. Manual and unattended paths share services; ordinary inputs and a bounded run scope replace technical controls and per-iteration prompts.; Defined separate context/result capture, copied-model analysis preparation, complete design dependencies, qualified local solver comparisons, distinct analysis/data/design failures, bounded overnight operation and small durable per-frame/check history while heavy data stays in memory. Updated current-plan and WP10 preparation; no immutable capability baseline was expanded.
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
