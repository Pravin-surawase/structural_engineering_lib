---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# Original XLL phases — corrected comparison and research improvements

Reviewed 3 September 2026 against the complete user-supplied architecture document and the separate Windows P0 packet.

**The supplied document is the intended original XLL plan.** My earlier comparison used the older optimizer roadmap and a new research synthesis. It did not preserve this plan's P2–P6 meanings. This review corrects that mistake without changing the original source.

[Preserved original](../excel-dna-xll-product-architecture-decision.md) · [Windows packet](windows-p0-task.txt) · [Research map](research/README.md)

## 1. What the original phases actually mean

The original implementation route is at [source line 405](../excel-dna-xll-product-architecture-decision.md#dependency-ordered-implementation-route).

| Original phase | Beginner explanation | Research improvement / proposed completion evidence |
| --- | --- | --- |
| **P0 — Packaging/runtime spike** | Can Excel load our add-in, show its controls and call simple functions reliably? | Use the separate shell packet for the immediate exercise. Record the actual packed artifact, runtime, load/restart/unload behaviour and signing limitations. Keep the broader compatibility work visibly deferred. |
| **P1 — Focused C# kernel** | Can one carefully defined engineering calculation give a correct, explainable result? | Specify one beam check, units, code provisions, assumptions and unsupported cases. Qualify C# against pinned Python evidence plus independently derived/reviewed reference answers. Show an early scoped result in Excel. |
| **P2 — Read-only ETABS** | Can we obtain the right information from the right member and model state? | Prove installed API compatibility, deliberate instance selection, identities, units, axes, case/station association and result freshness. No setters, including result-selection setters. |
| **P3 — Bounded solver and optimizer** | Can we solve a limited structural problem and compare permitted alternatives transparently? | Qualify solver and search separately within P3. State supported mechanics, candidate domain, required checks, objective, rejection reasons and search limits. Local ranking does not establish global model acceptance. |
| **P4 — Workbook delivery** | Can an engineer review and issue consistent calculations, schedules and reports? | Generate BBS, quantities, cost summaries, reports, PDF and replayable evidence from canonical results. Preserve choices and revision history; identify superseded outputs. |
| **P5 — Controlled ETABS transaction** | Can an approved change be applied to a model copy and verified after reanalysis? | Bind approval to exact source/destination and values. Read back changes, obtain fresh results, check governing effects and demonstrate the promised rollback/recovery behaviour. |
| **P6 — Commercial hardening** | Can the intended customer install, use, update and obtain support for the qualified product? | Prove signing, notices, entitlement, update/rollback, diagnostics and the support matrix. Add measured pilot value and ownership-cost evidence before making commercial claims. |

The core architecture remains Windows desktop Excel x64, C# through Excel-DNA, a focused pure engineering kernel, explicit Ribbon commands and ETABS as the global-analysis authority. Python remains development evidence for migration. Keep the existing workbench and older optimizer as separately governed projects.

## 2. Resolve the important P0 scope mismatch

There are two different proof scopes in the supplied material.

The **architecture's programme-level POC matrix** includes solver cases, optimizer behaviour, ETABS attachment/reads, reporting and commercial lifecycle evidence. Its final recommendation also groups beam UDFs, ETABS and the solver into a “first packet.” Those items span its own later phases.

The **separate Windows P0 task** explicitly permits only the shell and forbids engineering migration, solver work, CSI references and ETABS activity. It also makes the net8 comparison conditional. It is the applicable scope for the current learning exercise.

| Question | Original architecture | Current Windows exercise / proposed reconciliation |
| --- | --- | --- |
| Demo functions | Final recommendation mentions pure beam UDFs | P0 has SA_HELLO and SA_ADD. Engineering begins in P1. |
| ETABS/CSI | P0 route includes CSI assembly binding; broad POC includes live reads | No CSI references or calls in this packet. Track compatibility as deferred and resolve it in a separately scoped follow-up before live P2 work. This scheduling is a proposed clarification, not proof already obtained. |
| Solver | Included in broad POC and final recommendation | Keep it in original P3. |
| Runtime comparison | Original route names net48 and net8 | net48 baseline; compare net8 only if required tools/runtime already exist, as the Windows packet specifies. |
| Signing | Broad distribution goal is a signed packed XLL | Follow the packet: do not create/install a certificate; record SIGNING_HELD_NO_CERT if applicable. A successful unsigned development load is not signed-distribution acceptance. |
| Completion | Broad dispositions include ACCEPTED_SINGLE_XLL_NET48 | Use the separate packet's P0 dispositions and receipt. Do not substitute them for completion of the architecture's full matrix. |

Record both what passed and what remains deferred. The source text stays unchanged; this companion makes the difference explicit. Later implementation scopes retain their own authority requirements.

A development-machine load and a clean customer-like deployment are different evidence. The original architecture requires the latter without repository tooling. Collect it as the applicable feature set becomes available and repeat the release-relevant checks at P6. If signing is unavailable, preserve any successful technical observations but keep signing/distribution held; the packet provides HELD_TRUST_OR_SIGNING for that overall hold. Do not quietly label an unsigned experiment commercially accepted.

### Proposed assignment of the broad POC matrix

This is a scheduling clarification to the original matrix, not an assertion that its rows have passed. Each row applies again when the relevant code or supported environment changes.

| Original matrix row | First relevant proof and later completion |
| --- | --- |
| Packaging | P0 packed shell; full dependency graph and signed customer distribution as features mature, finalized for P6 release |
| Runtime | P0 shell targets under the packet; deferred installed CSI compatibility before live P2; supported co-resident add-ins/customer matrix before release |
| Ribbon/UI | P0 controls and error recovery; repeat for added commands |
| UDF safety | P0 demo functions; P1 engineering exports and subsequent new UDFs |
| Solver | P3a independently worked element/system and instability cases |
| Optimizer | P3b explicit domain, counts, constraints, rejection reasons and ranking |
| ETABS attach | P2 deliberate instance selection and identity |
| ETABS read | P2 bounded source/result mapping and context |
| Recalculation isolation | P0 pure demos/zero external calls; instrument again in P2 when an API adapter exists |
| Long operations | P2 vendor-read behaviour, P3 substantial computation and P5 mutation/analysis failure/cancel boundaries |
| Workbook/report | P1 minimal scoped result; P4 full BBS, quantity, evidence and PDF reconciliation |
| Lifecycle | P0 restart/unload/recovery; P6 qualified update-after-close and rollback |
| Security | P0 observed trust/signing disposition; signed/local/downloaded and policy cases for the released artifact before P6 acceptance |
| Resource use | P0 actual size/load/memory baseline; P2/P3/P5 operation cycles; P6 supportable release limits |

Closing the shell receipt therefore closes only its own observed checks. The broad architecture dispositions remain separate until their applicable evidence exists.

## 3. Strengthen the original plan using what we learned

### A. Qualify a complete, small engineering result in P1

The library has substantial mechanics and reinforcement logic, but those implementations are reference assets for the C# product. Choose one exact calculation before porting it. The v2 proposal of a rectangular, singly reinforced flexure check is a candidate for discussion, not an already approved engineering scope.

The selected contract should contain inputs, explicit units, code edition/provisions, assumptions, expected outputs, rounding/tolerances and invalid/unsupported behaviour. Keep “this flexure check passed” distinct from “this member is fully checked.” A useful early worksheet can show inputs, workings and limitations during P1; the full delivery suite still belongs to P4.

Retain the original requirement for both differential comparison and independent review. Matching Python can reveal a translation mistake, but cannot catch an assumption copied into both implementations. Curate the selected Sourcebook cases, including consistency between prose and numerical inputs. The recorded BEAM-RFLEX-028 mismatch is an explanation/input curation defect; it is not evidence that every reference result is wrong.

### B. Make P2 prove engineering meaning and freshness

An ETABS connection and a successful return code are necessary but insufficient. Keep force components attached to the correct member, position, case/combination, coordinate system and units. A saved-file hash alone cannot describe unsaved in-memory changes or establish a fresh analysis.

Our acquisition audit found useful installed evidence, with a result-epoch hold still recorded. Reuse its API contracts and lessons, while requiring fresh evidence for the selected XLL/environment. Do not silently change ETABS output selections to make a read succeed: the original plan explicitly treats selection setters as transactions. Missing context should produce a clear held/unsupported result.

### C. Split P3 into two understandable acceptance steps

**P3a — bounded solver:** declare exactly which elements, degrees of freedom, loads, restraints and result quantities exist. The audited library includes a bounded beam-line solver; this does not establish a general planar frame solver. Introduce axial/frame capabilities only with their own formulation and independently worked normal, boundary and singular/unstable cases. Retain the original SURROGATE_ONLY boundary and distinguish bounded agreement from global ETABS equivalence.

**P3b — candidate evaluation and search:** first prove that one actual reinforcement arrangement can be evaluated correctly, then enumerate many. Bar layers, centroid/effective depth, spacing, anchorage and all declared governing checks matter. A steel-area-only flexure result cannot establish a fully feasible detailing candidate.

Record the candidate domain, generation/pruning rules, counts, rejection reasons, supported constraints, cost basis, tie-breaking and stop reason. Label the winner according to the actual evidence, such as “best among the evaluated candidates.” A globally reanalysed candidate requires P5's qualified transaction; local P3 ranking can be completed earlier.

Keep deterministic enumeration first. Retain Math.NET as optional and OR-Tools as deferred, as the original already specifies. A new dependency needs a measured problem to solve.

### D. Treat revision behaviour as part of each feature

Add the smallest useful evidence record during P1: normalized inputs, calculation/configuration version, result meaning and reference basis. Extend it with model/result identity in P2 and candidate/search details in P3. P4 assembles full deliverables from those records.

Use the RCDC, MATE, VIS and StructPro lessons to preserve chosen reinforcement and explain what changed after new demand. Detect uncertain member identity rather than transferring old choices automatically. Distinguish engineering quantities from purchasing allowances such as laps, wastage or cutting allowances when those are outside the calculation scope.

Use Excel's fixed-format PDF export as the original proposes. A new report or worksheet template must not create a second calculation engine.

### E. Make P5 failure and recovery claims testable

Before applying a proposal, recheck the source context, exact destination copy and old/new values. Distinguish changing a shared section definition from assigning a section to one member. After mutation, read back the state and perform the required fresh analysis/design and supported checks.

Define rollback precisely for the supported workflow: which files/state are restored, what is preserved, and what happens after interruption. Prove that behaviour before claiming it. If recovery requires discarding a failed working copy and recreating it from the preserved baseline, say so. Do not present an unproven universal undo operation.

Use the old optimizer's useful contracts and failure patterns selectively; its host/worker architecture and cached tests do not constitute a ready net48 XLL implementation.

### F. Keep P6 commercial, and collect value evidence earlier

A working POC supports technical feasibility within its tested scope. It does not establish demand, willingness to pay, engineering approval or commercial viability. Qualify the original final recommendation accordingly.

Once a suitably scoped workflow is ready, measure an internal task and revision: engineer time, reviewer time, setup, correction and support effort, plus retained decisions and reproducibility. P6 should combine that evidence with a supportable signed product.

Use the existing price study as dated evidence. Compare host licences, add-in fees, licence unit, renewals, tax basis, training, setup and support under stated assumptions. Record first-year and three-year ownership cost when deciding what to buy or sell. No new price or revenue is established by this planning update.

## 4. Give each existing project a specific job

| Asset | Valuable contribution | Qualification needed before delivery |
| --- | --- | --- |
| structural_engineering_lib | Mechanics, actual reinforcement behaviour, constrained candidate evaluation and bounded solver contracts | Select a narrow scope, pin versions, port to C#, independently review and qualify the delivered artifact. |
| Sourcebook | Worked examples, boundary/invalid cases and an explanation structure | Curate numbers, units and narrative together; identify the independence of each expected answer. |
| StructProof | Proof records, traceable workings and guard patterns | Reuse the useful contracts; verify actual implemented coverage and version alignment. |
| Older StructAutomate optimizer | Model identity, proposals, recovery and evidence concepts | Adapt selected concepts to the XLL; do not import its host/Python/WebView2 stack into P0. |
| Existing ETABS acquisition campaign | Installed API observations and bounded acquisition evidence | Resolve recorded freshness/context gaps and requalify the exact XLL/runtime path. |
| Competitor studies | Workflow lessons, delivery expectations and cost questions | Convert each lesson into a measurable requirement; do not treat a vendor demonstration as our product's acceptance evidence. |

The potential strength is the connected chain from mechanics through actual reinforcement choices to understandable revision evidence. Repository size alone does not establish that chain. The [depth assessment](research/engineering-depth.md) and [readiness audit](research/foundation-readiness.md) supply the dated findings behind these recommendations.

## 5. Correct the earlier numbering explicitly

| Earlier v2 label | Destination under the actual original plan |
| --- | --- |
| P0 shell | Narrow Windows packet within original P0; broader compatibility proof remains tracked. |
| P1 one calculation | Original P1. |
| P2 reusable worksheet/revisions | Small result presentation starts in P1; revision context extends through P2/P3; full workbook delivery is original P4. |
| P3 read ETABS | Original P2. |
| P4 controlled model revision | Original P5. |
| P5 add engineering/deliverables | Delivery is original P4; new member families are separately qualified scope additions, not a replacement meaning for any phase. |
| P6 search and optional AI | Bounded solver/search is original P3; model-verified search additionally needs P5. Optional AI is a later proposal with no assigned original phase. Original P6 remains commercial hardening. |

The old optimizer's R1–R5 product releases and P0–P13 implementation stages remain historical context for that project. They are not the phase definitions for this XLL. A qualified beam product need not wait for every future member family before commercial evaluation.

Keep the original measured host-escalation triggers: responsiveness/isolation, recovery, durable jobs, dependency loading/resource use and security boundaries. Encountering a trigger starts an architecture review; it does not automatically add a host. Proposed size bands remain planning budgets until measured on actual builds.

## 6. Resume learning at the existing checkpoint

The architecture source is now available and compared. Resume [Lesson 1](learning/01-excel-xll-foundations.md) within the narrow Windows P0 packet. Its first exercise is to observe Excel version/bitness and ordinary formula recalculation. It does not build an XLL or complete P0.

The user remains the implementer. No lesson observation, engineering check, installed acceptance, ETABS action or release has been completed by this document review. Broad research remains paused, and B01–B23 remain parked.
