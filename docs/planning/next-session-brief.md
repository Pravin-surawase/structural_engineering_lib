# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Review delivered WP10-03 and prepare the executable WP10-04 offline normalization card. This is documentation and read-only evidence inspection; no product implementation, new tests, COM, Excel, or workflow redesign.
- Recurrence controls: RR-017 x1 / unknown: Inspect configured refspecs and fetch exact required existing refs; preserve configuration and branches unless cleanup is separately authorized.
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. WP10-01 freezes AO16, WP10-02 adds the exact getter port, and
WP10-03 adds bounded operation control; the next packet is WP10-04 offline
normalization.

| State | Next action / claim boundary |
|---|---|
| **Current** | IMP-M1 WP01–WP08 and IMP-M2 WP09 are implemented and qualified. WP10-01 freezes AO16's host-free boundary. WP10-02 supplies the exact getter adapter and accepted 410-call capture. WP10-03 adds the process lease, STA/message-pump broker, deadlines, 820-record durable ledger, exact replay, atomic artifact, postflight, and cleanup receipt; its one final installed run preserved the protected-state digest. |
| **Next** | Start `WP10-04` semantic intake from its [executable plan card](xll-product/wp10-etabs-read-adapter.md#wp10-04-executable-plan-card). Resolve material-kind evidence, matrix/face conventions, revision context and complete projection/disposition counts before product writes. Then validate the exact retained artifact and prove offline normalization, same-row actions, conservation and deterministic identity. |
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
