---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# StructAutomate — current plan

Updated 3 September 2026 for the owner's request to implement the C# automation foundation. The first product workflow is standalone beam design in Windows Excel; the complete automation path includes ETABS forces, design/checking, candidate search, reanalysis, detailing and construction outputs.

**Use the original architecture's P0–P6 phase meanings.** My earlier v2 synthesis changed those meanings and compared the older optimizer roadmap instead of this document. That comparison is superseded.

## Read these in order

1. [Automation requirements and delivery sequence](automation/README.md), with operation contracts, examples, source crosswalk and member/check schemas.
2. [Working C# foundation](../../../CSharp/README.md), its exact build/test commands and implemented boundaries.
3. [Requirements-first research](requirements-first/README.md), including the historical failure audit and three-project source inventory.
4. [Original XLL architecture decision](../excel-dna-xll-product-architecture-decision.md) and [phase review](phase-review.md), retained for architectural history. [Source provenance](source-manifest.json) records the supplied and publication hashes.

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

The C# solution now provides typed force normalization, beam-line analysis, reinforcement geometry, bar-path quantities and candidate ranking, with an Excel-DNA x64 build. The automation specification defines full member checks, ETABS adapters, candidate evaluation, detailing and workbook/report delivery. Installed Excel and ETABS behavior is verified with the actual applications as those interfaces are implemented.

The next engineering increment ports ordinary-beam strength checks with actual reinforcement, followed by serviceability and full detailing through the same contracts. Application increments connect ETABS intake and the workbook, then complete candidate generation/reanalysis and construction/report delivery. This does not change the original phase meanings or the separate library beam programme.

## Learning and evidence status

The source clarification is resolved. [Lesson 1 — Excel, C# and the XLL](learning/01-excel-xll-foundations.md) is ready to resume; [the learning record](learning/README.md) tracks progress. No user exercise or installed XLL acceptance is recorded as complete. Saved preflight describes an earlier environment observation, not acceptance.

Broad market research remains paused. All B01–B23 items remain parked in the [original register](research/requirements-and-parked-work.md#8-parked-research-exact-remaining-items). Existing price and competitor evidence keeps its original date and limitations.

## Earlier documents remain available as history

The [v2 synthesis](history/foundation-and-delivery-plan-v2.md) and its unchanged Word snapshot ([local evidence, not bundled](local-evidence-index.md)) contain useful engineering and product recommendations, but their phase numbering is superseded. The [previous optimizer crosswalk](history/optimizer-to-provisional-crosswalk.md) is an archived record of that earlier interpretation.

The [engineering-depth assessment](research/engineering-depth.md) and [readiness audit](research/foundation-readiness.md) remain dated evidence. They establish neither a completed XLL nor independent engineering approval.

The latest owner request authorizes this implementation and setup. Model operations use an identified application/model and the existing repository transaction workflow; package releases retain their per-release authorization process.
