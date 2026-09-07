---
owner: Main Agent
status: active
last_updated: 2026-09-07
doc_type: guide
complexity: advanced
---

# StructAutomate — current plan

**Active work (7 September):** complete WP10 under the
[completion contract](wp10-etabs-read-adapter.md#wp10-completion-contract--2026-09-07).
The functional implementation connects Excel to an identified running ETABS
model, captures its required complete source group, filters beam forces locally,
normalizes explicit units and provenance, and keeps heavy data in memory and
external snapshots. Workbook ownership, cancellation, source freshness and
offline reopen remain mandatory. The current milestone is in final worker,
installed-Excel and cumulative correctness qualification; completion requires
its exact candidate receipts and reviewed PR, not this source status alone.

The owner explicitly deferred PF9 timing and incremental-memory certification
to **WP10-PERF-FINAL at the end of the project**. Existing 5 s / 30 s p95 and
512 MiB targets and failed measurements remain unchanged. Do not resume speed
experiments or imply a performance pass while closing this functional milestone.
The actual 1,000-member / 100,000-row capacity and complete-source checks remain
part of WP10. Learning work is excluded.

**Next after WP10 acceptance:** plan the WP11 application mapping and design
orchestration from accepted assumptions and concurrent snapshot actions into
actual reinforcement and all applicable member checks. Then expose bounded
multi-option search and explicit physical-span/group constraints, followed by
controlled copied-model reanalysis and comparison against a fixed baseline.
Missing support/span evidence must remain visible. Overnight automation follows
those verified services and recovery boundaries; it is not available merely
because Connect ETABS and Get Forces work.

[PF0's product and library charter](library-definition/pf0/README.md) through
[PF11's implementation blueprint](library-definition/pf11/README.md) are
complete. WP01–WP08 implement the shared native Python and .NET beam libraries,
and [WP09](wp09-standalone-excel.md) now supplies the signed, installed-tested
standalone Excel product. [WP10](wp10-etabs-read-adapter.md) has frozen its
portable contract, exact getter adapter, bounded STA broker and offline
normalization. WP10-05's completed A/B contract replaced the old chunk-table
plan and was qualified with its installed Excel harness and external exact
XLL/source/workbook receipt.
The reviewed plan identifies production acquisition handoff (WP10-05B) and
multi-member support (WP10-05C) as prerequisites to final WP10-06 qualification.

The owner subsequently requested a **ribbon-first interface with worksheets
created only on demand**. The [UI review and proposed workflow](excel-ui-review.md)
records actual sample inspection, current input/feedback gaps and this decision.
The [whole-product audit](etabs-design-workflow.md#whole-product-audit-and-decisions--2026-09-05)
compares the original architecture, implemented packages and recent proposal.
It recommends a hybrid: one transparent Assumptions sheet and requested outputs,
active model/force data in memory, and external replayable snapshots/journals/run
history. Saved snapshots support offline work; live actions require current
model binding. Heavy workbook snapshot tables and a new database are not default
prerequisites. Keep the typed kernels and transaction/freshness guarantees; add
the missing design/candidate orchestration and public mapper. Stage the eventual
ribbon by implemented capability, with local Solver Check in applicable details.
The ribbon exposes Assumptions, Connect ETABS, Get Forces, Open Snapshot and
Review Snapshot, with legacy tools in their own menu. The owner brought live connection
ahead of automatic design: WP10-05B delivered running-model connection and
source context (audit increment D). Existing-force handoff and WP10-05C broad
capture are implemented in this completion candidate. Increment C follows the accepted data path. This changes delivery
order, not engineering acceptance or the final product goal.
Source completion alone does not assert an installed acceptance pass.

The subsequent [end-to-end workflow refinement](etabs-design-workflow.md) defines
broad capture with local filtering, session-based heavy data, transparent defaults,
physical-span/group sizing, bounded ETABS copy reanalysis and a fixed baseline
for comparable savings. A general-purpose indexed project store is a later improvement. It
refines overall product behavior and the upcoming WP10/WP11 work; it
does not claim those integrations complete or expand beam design to the building.

**Use the original architecture's P0–P6 phase meanings.** My earlier v2 synthesis changed those meanings and compared the older optimizer roadmap instead of this document. That comparison is superseded.

## Read these in order

1. [Library definition programme PF0–PF11](library-definition/README.md), with machine-readable phase, capability, deliverable and decision controls. This is the current work authority.
2. [Automation requirements and delivery sequence](automation/README.md), with operation contracts, examples, source crosswalk and member/check schemas.
3. [WP09 standalone Excel record](wp09-standalone-excel.md), with the canonical
   adapter decision and installed acceptance evidence.
4. [WP10 read-only ETABS plan](wp10-etabs-read-adapter.md), with completed
   WP10 completion contract, source/capacity evidence and installed gates.
5. [Working C# foundation](../../../CSharp/README.md), its exact build/test commands and implemented boundaries.
6. [Reusable Python/.NET library research](reusable-library-research.md), covering proposed library boundaries, peer libraries, public signatures and ETABS result semantics.
7. [Requirements-first research](requirements-first/README.md), including the historical failure audit and three-project source inventory.
8. [Original XLL architecture decision](../excel-dna-xll-product-architecture-decision.md) and [phase review](phase-review.md), retained for architectural history. [Source provenance](source-manifest.json) records the supplied and publication hashes.

## Original phases, retained

| Phase | Original purpose |
| --- | --- |
| P0 | Packaging/runtime spike |
| P1 | Focused C# kernel |
| P2 | Read-only ETABS |
| P3 | Bounded solver and optimizer |
| P4 | Workbook delivery: BBS, quantities, reports, PDF and evidence |
| P5 | Controlled ETABS transaction on a model copy |
| P6 | Commercial hardening |

The original shell-only Windows P0 packet remains historical evidence of the first narrow exercise: preservation and environment checks, x64 Excel-DNA 1.9.0/net48, About/Diagnostics/Open Panel, and pure SA_HELLO/SA_ADD functions. It did not authorize or establish ETABS calls, structural calculations, solver work, or installed acceptance.

The C# solution now implements the native WP01–WP08 contracts, beam checks,
analysis, topology, serviceability, detailing, member aggregation, bar paths,
construction outputs, calculation packages and bounded candidate search. WP09
replaced the earlier four-function Excel demo with the canonical Excel-DNA
adapter, versioned workbook commands, a sample, signed packaging, and installed
Excel evidence. Its workbook evaluates the one declared current physical
candidate; it does not yet expose a useful multi-option search domain.

Implementation sequencing follows PF11: WP09 and WP10-01 through WP10-04 are
complete, as are WP10-05 offline import and the first WP10-05B connection unit.
Finish WP10-06 integrated correctness qualification of the complete force path.
WP11 exposes multi-option fixed-action search in
Excel before adding controlled copied-model reanalysis, and WP12 completes
migration and release readiness.

## Learning and evidence status

The source clarification is resolved. [Lesson 1 — Excel, C# and the XLL](learning/01-excel-xll-foundations.md) remains available; [the learning record](learning/README.md) tracks the separate user-led exercises. WP09 installed acceptance is complete, while no user lesson observation is recorded as complete.

Broad market research remains paused. All B01–B23 items remain parked in the [original register](research/requirements-and-parked-work.md#8-parked-research-exact-remaining-items). Existing price and competitor evidence keeps its original date and limitations.

## Earlier documents remain available as history

The [v2 synthesis](history/foundation-and-delivery-plan-v2.md) and its unchanged Word snapshot ([local evidence, not bundled](local-evidence-index.md)) contain useful engineering and product recommendations, but their phase numbering is superseded. The [previous optimizer crosswalk](history/optimizer-to-provisional-crosswalk.md) is an archived record of that earlier interpretation.

The [engineering-depth assessment](research/engineering-depth.md) and [readiness audit](research/foundation-readiness.md) remain dated evidence. They establish neither a completed XLL nor independent engineering approval.

The approved implementation sequence now follows WP10's completion contract. Model operations
use an identified application/model and the repository transaction workflow;
package releases retain their per-release authorization process.
