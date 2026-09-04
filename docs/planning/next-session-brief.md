# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-04
- Focus: Implement the exact-version, getter-only C# ETABS boundary and prove one bounded installed matrix without combining WP10-03 broker/ledger work, WP10-04 normalization, Excel, performance, or release work.
- Completed: Admitted a clean current lane, bound the fixed WP10 plan and WP10-01 authority, and kept one parent session with no subagents.; Freshly verified .NET 10.0.400, the one ETABS 23.3.1.4563 process, exact PID and process start, ETABSv1 2.16.0.0 assembly identity/hash, x64 type-library hash, saved copied-model path/hash/size/mtime, lock, unit enum 6, 15 finished analysis cases, and the one intended output combination.; Added `StructuralEngineering.Etabs` as an optional `net10.0-windows` project with no compile-time CSI binary. It loads and validates the exact installed assembly at runtime, attaches by exact PID, rejects identity/version/file drift, exposes the 48-entry frozen getter matrix through a runtime read-only dictionary, validates exact reflected parameter names, and attempts every acquired COM release even when an earlier release fails.
- Recurrence controls: RR-002 x9 / unknown: Freeze acceptance rows and run an exact-host micro-probe before building the host adapter or package.; RR-005 x28 / unknown: Use maintained launchers, literal PowerShell blocks, exact paths, native output tools, and one shell per operation.; RR-011 x1 / unknown: Use ./run.sh format --check with the affected scope so the outside-scope byte guard and changed-path selection remain authoritative.
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. WP10-01 freezes AO16 and WP10-02 adds the exact getter port;
the next packet is WP10-03 operation control.

| State | Next action / claim boundary |
|---|---|
| **Current** | IMP-M1 WP01–WP08 and IMP-M2 WP09 are implemented and qualified. WP10-01 freezes AO16's host-free boundary. WP10-02 supplies a vendor-independent build, exact-version/PID host binding, a 48-operation getter whitelist, strict fake-host failure controls, and one 410-call installed capture with identical preflight/postflight state. |
| **Next** | Start `WP10-03` as a separate bounded task for the STA broker, one operation lease, deadlines and uncertain-call fencing, hash-chained call ledger, durable raw artifact, postflight, and cleanup receipt. Do not repeat WP10-02's installed getter matrix unless an exact bound identity changes. |
| Definition boundary | PF0–PF11 remains the approved requirements, semantics, signature, assurance, application, packaging, migration and implementation-order authority. |
| Application boundary | Excel and ETABS remain adapters. Worksheet calculations consume immutable validated data; live COM and mutations are explicit application commands. |
| Implementation boundary | WP10-01 is pure offline validation and WP10-02 is the exact getter-only host boundary. WP10-03 adds operation control without normalization or Excel. CSI/COM remains outside the pure libraries and may not alter units, result selection, the attached model, or analysis state. |
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
