# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-05
- Focus: Implement only WP10-03: the process lease, STA/message-pump broker, deadlines, durable hash-chained call journal, atomic raw artifact, postflight fence, exact recorded replay, and deterministic cleanup around the accepted WP10-02 getter adapter. Normalization, Excel, performance qualification, ETABS mutation, release, and general compatibility claims remain excluded.
- Completed: Checked the exact open ETABS model before implementation: process `7316`, ETABS `23.3.1.4563`, the saved 703,208-byte `vasant sawale - Copy.EDB`, model SHA-256 `e84918e042ce466d73066796186cdbd4bfd4102919b58dbd3c890149d4efa96f`, x64 ETABSv1 API/type library, lock/unit expectation, and selected combination matched the accepted WP10-02 evidence.; Added one process-keyed exclusive lease and dedicated STA worker with explicit Windows message pumping. Deadline/cancellation returns without waiting for a stuck call, publishes no final artifact, and retains the lease until the host call and cleanup quiesce; automatic retries remain zero.; Added write-through `started`/`returned` getter journaling, continuous WP10-01 canonical record hashes, paired final ledger validation, strict artifact hashing/tamper checks, and a no-overwrite atomic final move only after postflight, disposal, and lease-release proof.
- Recurrence controls: RR-003 x5 / unknown: Refresh dependency and generated projections before freeze, format only changed source paths, then run one read-only integrity check after audit acceptance.; RR-005 x35 / unknown: Use maintained launchers, literal PowerShell blocks, exact paths, native output tools, and one shell per operation.; RR-010 x3 / unknown: Update recurrence count, basis, last-seen task, session row, and generated handoff together before content freeze.
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
| **Next** | Start `WP10-04` as a separate offline-only task. Validate the exact WP10-03 artifact, project getter records to the portable raw-capture contract, then prove unit conversion, axes/faces, object/element/physical stations, all six same-row force components, row conservation, and deterministic snapshot identity without ETABS or Excel. |
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
