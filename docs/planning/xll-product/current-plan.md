---
owner: Main Agent
status: active
last_updated: 2026-09-05
doc_type: guide
complexity: advanced
---

# StructAutomate — current plan

Updated 5 September 2026 after completion of PF0–PF11, the WP01–WP08 native
library milestone, WP09 standalone Windows Excel, and WP10-01 through WP10-03.
The next implementation unit is offline ETABS-capture normalization; the complete
automation path includes ETABS forces,
design/checking, candidate search, reanalysis, detailing and construction
outputs.

[PF0's product and library charter](library-definition/pf0/README.md) through
[PF11's implementation blueprint](library-definition/pf11/README.md) are
complete. WP01–WP08 implement the shared native Python and .NET beam libraries,
and [WP09](wp09-standalone-excel.md) now supplies the signed, installed-tested
standalone Excel product. [WP10](wp10-etabs-read-adapter.md) has frozen its
portable contract, exact getter adapter, and bounded STA broker. WP10-04 next
normalizes the retained raw capture without ETABS or Excel.

**Use the original architecture's P0–P6 phase meanings.** My earlier v2 synthesis changed those meanings and compared the older optimizer roadmap instead of this document. That comparison is superseded.

## Read these in order

1. [Library definition programme PF0–PF11](library-definition/README.md), with machine-readable phase, capability, deliverable and decision controls. This is the current work authority.
2. [Automation requirements and delivery sequence](automation/README.md), with operation contracts, examples, source crosswalk and member/check schemas.
3. [WP09 standalone Excel record](wp09-standalone-excel.md), with the canonical
   adapter decision and installed acceptance evidence.
4. [WP10 read-only ETABS plan](wp10-etabs-read-adapter.md), with completed
   WP10-01 through WP10-03 evidence and the next offline-normalization boundary.
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

Implementation sequencing follows PF11: WP09 and WP10-01 through WP10-03 are
complete, WP10-04 now adds offline normalization, WP11 exposes multi-option fixed-action search in
Excel before adding controlled copied-model reanalysis, and WP12 completes
migration and release readiness.

## Learning and evidence status

The source clarification is resolved. [Lesson 1 — Excel, C# and the XLL](learning/01-excel-xll-foundations.md) remains available; [the learning record](learning/README.md) tracks the separate user-led exercises. WP09 installed acceptance is complete, while no user lesson observation is recorded as complete.

Broad market research remains paused. All B01–B23 items remain parked in the [original register](research/requirements-and-parked-work.md#8-parked-research-exact-remaining-items). Existing price and competitor evidence keeps its original date and limitations.

## Earlier documents remain available as history

The [v2 synthesis](history/foundation-and-delivery-plan-v2.md) and its unchanged Word snapshot ([local evidence, not bundled](local-evidence-index.md)) contain useful engineering and product recommendations, but their phase numbering is superseded. The [previous optimizer crosswalk](history/optimizer-to-provisional-crosswalk.md) is an archived record of that earlier interpretation.

The [engineering-depth assessment](research/engineering-depth.md) and [readiness audit](research/foundation-readiness.md) remain dated evidence. They establish neither a completed XLL nor independent engineering approval.

The approved implementation sequence now continues with WP10-04. Model operations
use an identified application/model and the repository transaction workflow;
package releases retain their per-release authorization process.
