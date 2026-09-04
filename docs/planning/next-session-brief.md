# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-04
- Focus: Audit WP09, its postmortem controls, and WP10-01; freeze a causal model and replace descriptive delivery limits with one fail-closed executable state machine without changing WP10 product behavior.
- Completed: Reconstructed authoritative task durations, candidate/repair/retry counts, integrity/session-end repetitions, hosted runs, and PR #964/#965 history; recorded the causal model, keep/update/merge/narrow/remove/add decisions, and measurable acceptance contract.; Added persisted delivery transitions from intake through merge, exact candidate/tree and audit binding, a one-repair ceiling, digest-gated replan, one hosted-run ceiling, idempotent pre-push closeout, and automatically derived phase/counter/rework closeout metrics.; Made `session end` strictly read-only, moved admission before timer creation, admitted clean synchronized `main` for intake only, required both standard hooks, and made Git receipts conditional on an actual boundary transition.
- Recurrence controls: RR-004 x6 / unknown: Admit intake before opening the timer, then enforce the persisted delivery states through automatic post-merge closeout.; RR-005 x18 / unknown: Use maintained launchers, literal PowerShell blocks, exact paths, native output tools, and one shell per operation.; RR-008 x1 / unknown: Persist guarded delivery transitions, allow one repair candidate, and require an acceptance-digest change after a second audit rejection.
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
remains the implementation authority. IMP-M1 implements WP01–WP08 as native
Python and .NET libraries, and IMP-M2 completes the standalone Windows Excel
product in WP09. The next packet is WP10's getter-only ETABS read adapter.

| State | Next action / claim boundary |
|---|---|
| **Current** | IMP-M1 WP01–WP08 and IMP-M2 WP09 are implemented and qualified. WP10-01 now freezes AO16's host-free request, raw-capture, getter-ledger, normalized snapshot, result-state, diagnostic, provenance, canonical identity, and shared Python/.NET conformance boundary. |
| **Next** | Begin WP10-02 only from the frozen version-1 schemas and fixtures. First run the read-only exact-host micro-probe, then bind the installed 2.16.0.0 getter signatures without changing units, result selection, model state, or analysis state. |
| Definition boundary | PF0–PF11 remains the approved requirements, semantics, signature, assurance, application, packaging, migration and implementation-order authority. |
| Application boundary | Excel and ETABS remain adapters. Worksheet calculations consume immutable validated data; live COM and mutations are explicit application commands. |
| Implementation boundary | WP10-01 is pure offline validation. WP10-02 adds the exact getter adapter after its micro-probe; CSI/COM must remain outside the pure libraries and must not alter units, result selection, the attached model, or analysis state. |
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
