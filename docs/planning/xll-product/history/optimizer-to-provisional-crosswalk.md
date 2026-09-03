---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

**Superseded phase comparison.** This retained document compared the older optimizer with a provisional XLL synthesis. Use the [original-phase review](../phase-review.md) for the actual XLL phases.

# Original phases and the current learning plan

Reviewed 3 September 2026. This compares the actual older optimizer documents with the later Windows XLL brief and v2 plan. It is a navigation and sequencing clarification; no implementation stage is newly accepted.

## 1. There are three different planning levels

**Long-term product breadth:** the older master plan has five releases, R1–R5. They describe which engineering families the product would eventually cover.

**Older optimizer implementation:** its roadmap has G0 and P0–P13, using an Excel add-in, a separate .NET host, a Python worker and WebView2. These belong to the preserved older project.

**Current XLL delivery:** the later Windows brief specifies a small native Excel-DNA shell first, followed by one pure C# beam calculation. The research blueprint expands this into the current P0–P6 roadmap. The original pasted brief explicitly says to preserve the older optimizer as reference.

Use “old optimizer P1” or “XLL P1” when discussing historical work. The same number refers to different things. The structural library and StructProof have separate queues; their progress does not complete an XLL stage.

Sources: older roadmap ([local evidence, not bundled](../local-evidence-index.md)), older master plan, product sequence ([local evidence, not bundled](../local-evidence-index.md)), preserved handoff ([local evidence, not bundled](../local-evidence-index.md)), [current v2 plan](foundation-and-delivery-plan-v2.md).

## 2. Keep the five-release ambition as a direction

| Older release | Original intent | Improvement to its use today |
| --- | --- | --- |
| R1 — Beams | Qualified RC beam checks, candidates, cost/carbon ranking and fresh copied-model ETABS verification | Deliver a useful manual-input beam check first, then revisions and integration. A P1 flexure check is an early milestone, not completion of old R1. |
| R2 — Columns | Axial/biaxial checks, detailing, candidates and global guardrails | Reuse the validated workflow, but qualify column mechanics and reinforcement assumptions separately. |
| R3 — Slabs and walls | Shell results, topology, supported design and model updates | Treat as new engineering and connector capabilities. Do not extrapolate beam validation to shell behaviour. |
| R4 — Foundations | Isolated, combined and strap footings with explicit soil inputs | Retain the original distinction between reaction import, calculation and output. Initial foundation scope does not imply ETABS footing writes; raft/SAFE remain separate decisions. |
| R5 — Whole-model portfolio | Coordinated member changes under constructability, cost/carbon and change-count objectives | Keep as a later hypothesis. Each selected portfolio needs fresh global verification and all declared governing checks. |

The order is a useful default, not a commitment to finish every family before learning whether the beam workflow is valuable. Pilot evidence can change the next investment. Cost/carbon objectives remain documented ambitions; no current calculation or data source is accepted merely because the old roadmap named them.

## 3. Where each older implementation phase goes

These are correspondences of purpose, not claims that old code satisfies the new stage.

| Older optimizer phase | Current destination | What changes |
| --- | --- | --- |
| G0 inventory; P0 scaffold | XLL P0 | Refresh the prescribed preservation/toolchain checks and build the isolated shell. Avoid importing the old platform scaffold. |
| P1 host/worker/Excel/3D health | Small part in XLL P0; the rest deferred | Prove Ribbon, diagnostics and pure demo UDFs. Host, Python, WebView2 and 3D are outside this P0. |
| P2 read-only ETABS | XLL P3 | Move behind the first C# calculation and worksheet workflow. Prove mapping and freshness separately. |
| P3 exact Python beam capability | XLL P1, then capability-by-capability expansion | C# is the delivered calculation. Pin Python/Sourcebook references and validate the selected translation. |
| P4 independent frame screening | Optional later capability | Keep solver scope, analytical references and any ETABS calibration explicit. It is not a prerequisite for checking supplied member forces. |
| P5 local discrete optimizer | Manual alternatives in XLL P2; automatic search in P6 | Prove one understandable alternative first. Keep local screening distinct from globally verified acceptance. |
| P6 one copied-model cycle | XLL P4 | Preserve exact source identity, approval, original protection, read-back, fresh analysis and recovery. |
| P7 finite multi-cycle optimization | XLL P6 | Use bounded candidates, fresh baseline copies and independent final-candidate verification. |
| P8 engineering workbench | Incrementally in XLL P1–P5 | Introduce explanation, comparison and history when needed. A full 3D interface is not a first-use prerequisite. |
| P9 installer and pilot | Narrow internal pilot after P2; commercial release gate later | Learn from internal task/review effort early. Installation, signing, updates and support still need evidence before sale. |
| P10 columns; P11 slabs/walls; P12 foundations | Separate XLL P5 capability additions | Preserve each family's engineering and global-interaction requirements. No blanket “all members supported” claim. |
| P13 coordinated portfolio | Later P6 extension | Requires the relevant families, interactions and global checks to be qualified first. |

The old project's architecture remains governed by its own instructions. This crosswalk neither changes that repository nor authorizes transplanting its stack into the new XLL.

## 4. The current phases, in beginner language

| XLL phase | Question we are proving | Most useful improvement from the research |
| --- | --- | --- |
| P0 — Shell | Can Excel load our add-in and call simple functions reliably? | Test the actual packed XLL lifecycle. Record problems clearly. |
| P1 — One calculation | Does one precisely defined engineering check give a defensible, understandable answer? | Review a few independent cases and keep the report consistent with the inputs. |
| P2 — Reusable worksheet | Can an engineer repeat the task and understand a revision? | Preserve choices, mark old results outdated and compare total task/review effort. |
| P3 — Read ETABS | Can we import the right information from the right model state? | Verify identity, units, axes, combination/station and freshness. |
| P4 — Controlled revision | Can we apply and verify one approved change on a model copy? | Bind approval to exact values; read back and reanalyse; expose partial failure. |
| P5 — Add a capability | Can we extend coverage without weakening previous evidence? | Qualify each new check/member/output separately, prioritizing real pilot needs. |
| P6 — Search and optional AI | Can we compare many allowed alternatives with trustworthy limits? | Reuse accepted checks and transactions; disclose budgets, stop reasons and missing evidence. |

**P5 is repeatable capability expansion.** It does not require every column, slab, wall and footing feature before a beam-only P6 experiment. First qualify the beam checks and interactions required by that experiment. A P1 flexure pass alone cannot establish a constructible, feasible beam optimization candidate.

Local enumeration and ranking may be qualified without ETABS writes; the result stays locally screened. Model-verified search additionally requires P4's accepted transaction, fresh copied-model analysis, all declared governing checks and an independently rerun selected candidate. The v2 plan now includes these clarifications directly in P5/P6.

## 5. What stays strong, and what improves

Keep the original idea of completing one element workflow before coordinating many element families. Keep global analysis with ETABS, explicit engineering scope, preserved model originals and reviewable alternatives.

Improve the starting point: a smaller runtime, engineering before integration, useful reports before elaborate UI, and a measured internal task before broad expansion. The library's practical reinforcement work becomes an intentional next engineering capability, rather than being either ignored or imported wholesale.

Use the [research map](../research/README.md) when a decision arises. It directs us to the relevant study, requirement, acceptance challenge and parked question. We do not need another full market review before beginning P0.

**Learning resumes at [Lesson 1: Excel, C# and the XLL](../learning/01-excel-xll-foundations.md).** Its first exercise is observation in Excel; the user remains the implementer.
