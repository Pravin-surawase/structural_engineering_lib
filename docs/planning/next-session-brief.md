# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Implement audit increments A/B: transparent assumptions, immutable external snapshots, workbook-bound offline review and visible command outcomes.
- Completed: Replaced the obsolete chunk-sheet plan with the active A/B contract before implementation. Carried the eight local planning/audit predecessor commits together; no sibling worktree was mutated or separately published.; Added Assumptions, Open Snapshot and Review Snapshot. Canonical demo inputs remain explicit and editable; only requested projections create sheets. Small custom XML references identify the document/artifact; the complete snapshot and raw provenance stay external, with in-memory member/station indices. Legacy tools remain usable in separate standalone workbooks.; Added strict input/artifact tests and a maintained installed acceptance harness. Twelve new host-free checks passed during implementation. A narrow real Excel diagnostic exercised import, review, report, metadata-failure rollback, save/reopen and session eviction (zero resident sessions on close). These diagnostics guide implementation; final qualification must bind the accepted source and signed installed XLL through the external receipt.
- Git receipt: docs/verification/wp10-05-git-handoff-receipt.json | sha256:bd56e028c2f104be93a5fe2dae708e88c98430c0e8cf18ba94ecf5b82c79cb39 | HOLD
- Git identity: codex/wp10-05-offline-session@ac60595d6d03a57c0ae5a909ac0f0f393e1069e1 | upstream=NONE@UNKNOWN | base=origin/main@973cea8c39edf347ccfb19561cf10a06b48bf770 | tree=dirty | operation=none
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
review. Its active contract separates exact installed Excel proof from later
design orchestration, production acquisition and multi-member qualification.

| State | Next action / claim boundary |
|---|---|
| **Current** | WP10-04 normalizes the unchanged retained WP10-03 artifact to 97 model records plus 13 action rows, with all getter evidence retained and Python/.NET canonical parity. Its [receipt](../verification/wp10-04-normalization-evidence.json) records offline proof; inspect the exact PR and delivery ledger for subsequent delivery facts. |
| **Next** | Check WP10-05's delivery ledger and exact external installed receipt against its [active A/B contract](xll-product/wp10-etabs-read-adapter.md#wp10-05-active-packet-ab--2026-09-05). It implements transparent assumptions, external immutable storage, memory indices, visible review and transactional requested projections. After acceptance, implement audit increment C: actual-bar design/check orchestration. Snapshot integrity does not establish design readiness or live freshness. |
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
