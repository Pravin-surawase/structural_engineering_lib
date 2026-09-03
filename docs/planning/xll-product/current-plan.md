---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# StructAutomate — current plan

Updated 3 September 2026 after reading the user-supplied original XLL architecture decision. The user implements; the assistant teaches and reviews observed results.

**Use the original architecture's P0–P6 phase meanings.** My earlier v2 synthesis changed those meanings and compared the older optimizer roadmap instead of this document. That comparison is superseded.

## Read these in order

1. [Original XLL architecture decision](../excel-dna-xll-product-architecture-decision.md). Its text is preserved in this LF-normalized publication copy. The exact supplied bytes are retained in the [intake archive](../../_archive/xll-product-intake-2026-09-03/excel-dna-xll-product-architecture-decision.md). [Source provenance](source-manifest.json) records the original and published hashes; the earlier Mac Git revision has not been independently verified.
2. [Phase comparison and research improvements](phase-review.md). This preserves the original phases, corrects the earlier mapping, and proposes clearer completion evidence.
3. [Windows P0 task](windows-p0-task.txt). This separately supplied, narrower packet controls the first implementation exercise.
4. [Research map](research/README.md). Use it to find the evidence, requirements, costs and parked questions relevant to each phase.

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

The current exercise is the **shell-only Windows P0 packet**: preservation and environment checks, x64 Excel-DNA 1.9.0/net48, About/Diagnostics/Open Panel, and pure SA_HELLO/SA_ADD functions. A separate net8 comparison is conditional on existing prerequisites. Its explicit exclusions include CSI references and ETABS calls, structural calculations and solver work. Follow the packet's signing and acceptance rules.

The architecture's larger Windows matrix spans later capabilities. Completing the shell packet cannot close that matrix. Record deferred CSI compatibility proof before live P2 integration; the companion review explains the proposed scheduling. After P0 passes its receipt rules, P1 is one specified C# beam calculation.

## Learning and evidence status

The source clarification is resolved. [Lesson 1 — Excel, C# and the XLL](learning/01-excel-xll-foundations.md) is ready to resume; [the learning record](learning/README.md) tracks progress. No user exercise or installed XLL acceptance is recorded as complete. Saved preflight describes an earlier environment observation, not acceptance.

Broad market research remains paused. All B01–B23 items remain parked in the [original register](research/requirements-and-parked-work.md#8-parked-research-exact-remaining-items). Existing price and competitor evidence keeps its original date and limitations.

## Earlier documents remain available as history

The [v2 synthesis](history/foundation-and-delivery-plan-v2.md) and its unchanged Word snapshot ([local evidence, not bundled](local-evidence-index.md)) contain useful engineering and product recommendations, but their phase numbering is superseded. The [previous optimizer crosswalk](history/optimizer-to-provisional-crosswalk.md) is an archived record of that earlier interpretation.

The [engineering-depth assessment](research/engineering-depth.md) and [readiness audit](research/foundation-readiness.md) remain dated evidence. They establish neither a completed XLL nor independent engineering approval.

This update changes planning and learning documents only. The supplied architecture remains a research decision; it does not itself authorize later implementation, model activity or release.
