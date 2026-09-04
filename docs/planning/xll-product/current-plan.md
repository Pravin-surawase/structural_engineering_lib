---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: advanced
---

# StructAutomate — current plan

Updated 4 September 2026 after completion of PF0–PF11 and the WP01–WP08 native
library milestone. The first product workflow is standalone beam design in
Windows Excel; the complete automation path includes ETABS forces,
design/checking, candidate search, reanalysis, detailing and construction
outputs.

[PF0's product and library charter](library-definition/pf0/README.md) through
[PF11's implementation blueprint](library-definition/pf11/README.md) are
complete. WP01–WP08 now implement the shared native Python and .NET beam
libraries. [WP09](wp09-standalone-excel.md) is the active milestone and delivers
the standalone Excel product over those libraries before live ETABS work.

**Use the original architecture's P0–P6 phase meanings.** My earlier v2 synthesis changed those meanings and compared the older optimizer roadmap instead of this document. That comparison is superseded.

## Read these in order

1. [Library definition programme PF0–PF11](library-definition/README.md), with machine-readable phase, capability, deliverable and decision controls. This is the current work authority.
2. [Automation requirements and delivery sequence](automation/README.md), with operation contracts, examples, source crosswalk and member/check schemas.
3. [WP09 standalone Excel plan](wp09-standalone-excel.md), with the canonical
   adapter decision, delivery slices and acceptance evidence.
4. [Working C# foundation](../../../CSharp/README.md), its exact build/test commands and implemented boundaries.
5. [Reusable Python/.NET library research](reusable-library-research.md), covering proposed library boundaries, peer libraries, public signatures and ETABS result semantics.
6. [Requirements-first research](requirements-first/README.md), including the historical failure audit and three-project source inventory.
7. [Original XLL architecture decision](../excel-dna-xll-product-architecture-decision.md) and [phase review](phase-review.md), retained for architectural history. [Source provenance](source-manifest.json) records the supplied and publication hashes.

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
replaces the earlier four-function Excel demo with the canonical Excel-DNA
adapter, versioned workbook commands and installed Excel evidence.

Implementation sequencing follows PF11: WP09 is the standalone Excel milestone,
WP10 adds getter-only ETABS acquisition, WP11 adds controlled copied-model
reanalysis, and WP12 completes migration and release readiness.

## Learning and evidence status

The source clarification is resolved. [Lesson 1 — Excel, C# and the XLL](learning/01-excel-xll-foundations.md) is ready to resume; [the learning record](learning/README.md) tracks progress. No user exercise or installed XLL acceptance is recorded as complete. Saved preflight describes an earlier environment observation, not acceptance.

Broad market research remains paused. All B01–B23 items remain parked in the [original register](research/requirements-and-parked-work.md#8-parked-research-exact-remaining-items). Existing price and competitor evidence keeps its original date and limitations.

## Earlier documents remain available as history

The [v2 synthesis](history/foundation-and-delivery-plan-v2.md) and its unchanged Word snapshot ([local evidence, not bundled](local-evidence-index.md)) contain useful engineering and product recommendations, but their phase numbering is superseded. The [previous optimizer crosswalk](history/optimizer-to-provisional-crosswalk.md) is an archived record of that earlier interpretation.

The [engineering-depth assessment](research/engineering-depth.md) and [readiness audit](research/foundation-readiness.md) remain dated evidence. They establish neither a completed XLL nor independent engineering approval.

The latest owner direction authorizes careful completion of PF0–PF11 before further implementation. Model operations will use an identified application/model and the existing repository transaction workflow; package releases retain their per-release authorization process.
