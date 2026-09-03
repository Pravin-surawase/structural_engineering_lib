---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# StructAutomate research map

Updated 3 September 2026 after comparing the supplied original XLL architecture. This is the entry point for reusing completed studies. It does not refresh prices, establish vendor behaviour or accept product features.

**Phase numbers below follow the actual original XLL plan:** P0 packaging/runtime, P1 C# kernel, P2 read-only ETABS, P3 solver/optimizer, P4 workbook delivery, P5 controlled ETABS transaction and P6 commercial hardening. Earlier blueprint/v2 phase tags remain historical. Their R and C identifiers are retained, with corrected phase assignments here.

## Start with the question you are answering

| Question | Open this | How to use it |
| --- | --- | --- |
| Which plan applies now? | [Current plan](../current-plan.md) | Read the original architecture and current Windows shell packet, then the companion improvements. |
| What did the original say? | [Preserved architecture](../../excel-dna-xll-product-architecture-decision.md) | Exact supplied text; [provenance](../source-manifest.json) records its origin/hash, not an independently verified Git commit. |
| What are we improving? | [Corrected phase comparison](../phase-review.md) | Keep P0–P6; clarify scope, reference quality, freshness, candidate meaning, recovery and commercial evidence. |
| What did we learn about a competitor? | [Market report source](market-study.md) | Read the named study, dates and limitations, then its supporting sources. |
| Which lessons became requirements? | [R01–R13 register](requirements-and-parked-work.md#4-proposed-requirements-with-acceptance-examples) | Reuse the requirement content; use the corrected assignments below instead of its historical stage tags. |
| What is strong in our engineering projects? | [Depth assessment](engineering-depth.md) | Inspect actual mechanics, detailing, constraints and the independence of reference evidence. |
| What ran, and on which version? | [Readiness/GitHub audit](foundation-readiness.md#11-what-was-verified-during-this-audit) | Distinguish source tests, cached/fake tests, installed evidence and remaining gaps. |
| Where are costs and licence qualifications? | [Cost comparison](market-study.md#9-public-prices-and-licensing-compare-the-whole-purchase) | Compare package, host requirements, licence unit, term, tax and support. Refresh a quote when a buying/pricing decision needs it. |
| What remains unfinished? | [B01–B23 parked register](requirements-and-parked-work.md#8-parked-research-exact-remaining-items) | Reopen only relevant questions under their recorded conditions. All 23 remain parked. |
| Where do we continue learning? | [Learning record](../learning/README.md) | Source clarification is resolved; Lesson 1 observations are still pending. |

## Research to requirement to original phase

R identifiers refer to the preserved blueprint register. C01–C08 refer to the useful acceptance challenges in the [historical v2 synthesis](../history/foundation-and-delivery-plan-v2.md). Their earlier “First stage” values are superseded by this table. These are planned checks, not completed results.

| Original phase / decision | Evidence to consult | Requirement / challenge to reuse | Parked work when relevant |
| --- | --- | --- | --- |
| P0 packaging/runtime; current shell packet | Windows brief; Excel-DNA foundation study; saved preflight | R01, R10; packet's exact P0 receipt. Broad architecture proof remains separate. | B09 |
| P1 focused calculation | Library/StructProof depth; Sourcebook curation; S-CONCRETE/RCDC scope and explanation lessons | R02, R03, R05, R06, R11; C01 base result, C02 limits; initial revision record | B20; B03 only for an actual build/buy decision |
| P2 read-only acquisition | SideKick, native CSI baseline, VIS matching; our acquisition/freshness audit | R04, R05, R07; C05 identity/forces and C06 stale/ambiguous context | B01, B02, B14; B11 before selected code reuse |
| P3a bounded solver | Original architecture; bounded beam-line implementation and independent references | R02, R03, R06, R11; defined elements/DOFs/loads, analytical and instability cases, explicit SURROGATE_ONLY boundary | No new market study required merely to specify bounded mechanics |
| P3b candidate evaluation/search | Library reinforcement/evaluator depth; ACE finite search; ConGro claim distinctions | R03, R06, R07, R08; deterministic-search part of R12; C04 actual reinforcement, complete declared constraints and count/stop evidence | B17, B18 if a competitive/reuse decision needs them |
| P4 workbook delivery | StructPro, RCDC, CalcTree, MATE override/schedule lessons; original Excel PDF choice | R05, R07, R08, R11; C03 retained choice/revision report; BBS/quantity/report reconciliation | B04, B21; relevant B16 detailing assumptions |
| P5 controlled copied-model transaction | RCDC revision lessons; ACE candidate copies; ConGro execution distinctions; old optimizer recovery patterns | R04, R05, R09, R10; C07 approved copy change and C08 interruption/retry; fresh global results for model-verified search | B21; B13/B15/B18 only for the specific competing workflow |
| P6 commercial hardening | Original signing/update/support requirements; cost study; CivilAI service/configuration lesson; scoped pilot results | R01, R10, R13; deployment/support evidence and measured engineer/reviewer/setup/support effort | B22, B23; relevant quote/compatibility gaps |
| Additional member families | Relevant library route plus RCDC, MATE, VIS, IDEA, PROKON or foundation evidence | Repeat scope-specific P1/P3 qualification, P4 delivery and P5 mutation qualification where applicable. This is not a replacement P5. | B02, B05, B06, B12, B16 as needed |
| Optional AI | R12's language-assistance and data-handling provisions; ConGro/CivilAI lessons | Later proposal; no original phase assigned. Keep deterministic calculation/search and model permissions separate. | B18, B19 only when deciding a concrete feature |

A small calculation result/worksheet appears in P1; full workbook delivery remains P4. Local search belongs to P3 and can precede mutation. Claims of model-verified improvement additionally require P5. Commercial hardening remains P6 even for a narrowly qualified beam product.

## Corrected use of the existing requirement identifiers

| ID | Requirement meaning | Application under original P0–P6 |
| --- | --- | --- |
| R01 | Predictable Excel lifecycle and supported environment | P0 shell evidence; P6 full distribution/support matrix |
| R02 | Pure calculation engine and versioned inputs | P1 kernel; P3 solver/evaluator; shared by P4 outputs |
| R03 | Honest result meaning and unsupported states | P1 onward; applies to P2 freshness and P3 candidate claims |
| R04 | Validate data boundaries | P1 manual inputs; P2 acquisition; P5 read-back and fresh results |
| R05 | Revision and result provenance | P1 inputs; P2 model/result epoch; P3 candidates; P4 issues; P5 revised model |
| R06 | Narrow coverage and independent reference cases | P1 and each P3/new engineering capability |
| R07 | Preserve deliberate engineering choices | P1 selected inputs; P2 matching; P3 candidate constraints; P4 revisions |
| R08 | Compare alternatives under the same assumptions | P3 local alternatives; P4 presentation; P5 globally reanalysed alternatives |
| R09 | Preview, approve and apply a specific change | P5 |
| R10 | Transparent recovery after partial failure | P0 callbacks; P2 read failures; P5 transactions; P6 update/rollback |
| R11 | Reproducible and scoped deliverables | P1 minimal explanation; P3 candidate/solver records; P4 full outputs |
| R12 | Controlled search and optional AI | Deterministic search in P3; model actions through P5; AI remains an unassigned later proposal |
| R13 | Understandable ownership cost and support | Planning/pilot measurement when relevant; P6 commercial implementation |

The earlier blueprint and Word reports remain dated snapshots. Do not use their historical phase tags to decide the next implementation packet.

## Find each completed close study quickly

| Study | Direct locator | Reusable lesson | Evidence limit to retain |
| --- | --- | --- | --- |
| StructPro | [Study](market-study.md#structpro--closest-excel-control-panel-comparator) | Explicit Read/Calculate/Preview/Apply actions and reusable calculation templates | Tutorials and sampled demonstrations do not establish the current delivered package or licence. |
| SideKick | [Study](market-study.md#etabs-sidekick--excel-productivity-with-a-verified-indian-offer) | Focused commands, precise extraction context and duplicate-safe retries | Separate historical demonstrations, observed offer and current compatibility. |
| RCDC | [Study](market-study.md#bentley-rcdc--first-priority-for-indian-rc-designdetailing) | Preserve reinforcement, recheck revisions, report changes and code coverage | Validation documents do not prove a current ETABS integration run; bundle pricing is not standalone pricing. |
| ETABS MATE | [Study](market-study.md#etabs-mate--reinforcement-detailing-checks-and-deliverables) | Explicit defaults/overrides, reset consequences and linked schedules | Build, Indian-code applicability and licence rights need the recorded follow-up. |
| ACE OCP | [Study](market-study.md#ace-ocp--dedicated-optimization-with-substantial-historical-evidence) | Bounds, locks, candidate copies, quantities and finite search | Historical technical evidence is stronger than established current delivery/compatibility. |
| ConGro | [Study](market-study.md#congro-ai--chat-agent-and-separately-initiated-optimizer) | Separate conversation, execution, optimization and engineering acceptance | Public claims/demos and usage prices do not prove our intended controlled workflow. |
| CivilAI | [Study](market-study.md#civilai--custom-indian-office-automation-service) | Office-specific configuration and a clear boundary between product and bespoke service | A service offering/price is not a delivered packaged competitor or our development budget. |

## Screened comparisons and foundations

These received narrower investigation than the close studies. Their feature descriptions are design prompts, not verified implementations.

- [ETABS / SAFE / CSiXCAD](market-study.md#3-the-baseline-we-would-compete-against): native baseline, adjacent hosts and drawing reconciliation.
- [CalcTree](market-study.md#calctree--calculation-knowledge-and-connected-reporting): reusable calculations, typed connections and dependencies.
- [S-CONCRETE](market-study.md#s-concrete--simcenter-s-frame-concrete--mass-section-checking): batch checking and explicit coverage.
- [VIS](market-study.md#vis--useful-design-interface-benchmark): matching and retained design on reimport.
- [IDEA StatiCa](market-study.md#idea-statica-concrete--specialist-checks-and-difficult-details): specialist scope and clear handoff inputs.
- [PROKON and the module/bridge distinctions](market-study.md#prokon-concrete--modular-calculations-and-schedules): module-specific coverage and independent transfer validation. SideKick's study records the separate GenCol/CDC/LCM/spColumn bridge family.
- [GoCalc / Structon.AI](market-study.md#gocalc-and-structonai--watchlist-limited-evidence): watchlist only; limited evidence does not justify architecture changes.
- [Tekla / ProtaStructure / CYPECAD](market-study.md#7-complete-alternatives-to-the-etabs-led-workflow): whole-workflow alternatives, migration effort and reanalysis semantics.
- [Excel-DNA / PyXLL / xlwings / Python in Excel / public projects](market-study.md#8-excelxll-foundations-and-public-projects): runtime, packaging, reuse and ownership-cost boundaries. BHoM, ExcelCSIToolBoxAddIn and ETABS-mcp are references; no new dependency is selected.

## Evidence discipline for future use

For a feature decision, read only its row and relevant sources. Record: the problem; evidence and date; its limit; the design decision; the linked R identifier; and what result will demonstrate success. Then return to implementation or the lesson.

A vendor description means “documented claim.” A demonstration means “shown under these conditions.” Our inspected code means “implementation examined.” A passing software test means “this test passed on this artifact/environment.” Installed behaviour and independently reviewed engineering need their own evidence. A plan is a proposed behaviour, not any of these results.

If a source changes, append a dated finding and explain which decision it changes. Retain old prices, code pins and audit results as historical evidence. Refresh unstable facts at the decision that needs them, particularly purchases, dependency changes and engineering/code-version adoption. Broad competitor research remains paused.

The detailed citation records remain in the [market source ledger](source-ledger.json) and [blueprint ledger](requirements-source-ledger.json). The machine assessment evidence ([local evidence, not bundled](../local-evidence-index.md)) records the engineering/GitHub audit's scope. This map does not duplicate or overwrite them.
