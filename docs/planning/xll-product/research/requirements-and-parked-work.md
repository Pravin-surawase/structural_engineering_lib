---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

**Historical research synthesis.** R01–R13 and B01–B23 are retained; phase tags in this snapshot predate the original XLL-plan comparison. Use the [corrected research map](README.md) for current phase assignments. No item is newly accepted or closed.

# StructAutomate: product blueprint and parked research
> What to carry forward from the competitor studies
> Research paused • Proposed product requirements • 3 September 2026

## 1. Direction after the research

**Keep the Excel product idea, and define its first useful promise more narrowly: help an engineer complete one traceable Indian RC member check, then extend it into a controlled ETABS revision workflow.** The long-term sequence remains read → check/design → compare → approve → update a model copy → reanalyse → verify → report. Each stage must be independently understandable and testable.

This is a synthesis of the existing market report and its saved source ledger. No new external research was conducted for this document. Facts and prices retain their original evidence dates; they are not refreshed quotations. Proposed requirements below are our design decisions to consider, not claims that competitors implement them or that customers have agreed to buy them.

**Already specified:** desktop Excel x64, C#, an Excel-DNA XLL and native Ribbon. The supplied Windows brief limits P0 to the shell, diagnostics and pure demonstration functions. It explicitly places one focused C# beam calculation in P1, before ETABS integration. That sequence is preserved. No product implementation, project creation or environment changes were performed in this synthesis.

**Recommended improvement:** organize the product around a reviewed engineering job, with visible inputs, assumptions, revisions and outputs. Keep calculation code independent of the Excel interface and future ETABS connector. An engineer should be able to understand and test a calculation without first opening an ETABS model.

**Deferred:** whole-building optimization, AI control, full drawing/BBS production, foundations, broad code coverage and complete replacement of ETABS. These remain possible later directions. Their value and engineering scope have not been established for our first release.

The central business hypothesis is that this workflow reduces total engineering and review effort on recurring revisions. Existing evidence does not prove an empty market, unique functionality, a suitable selling price or customer willingness to pay.

## 2. What to take from each completed study

### StructPro: explicit Excel commands and reusable calculations

The tutorials demonstrate model reads/writes, distinct editable tables and named-cell calculation templates with reports. Its current delivery and licence scope remain uncertain. [Tutorial catalogue](https://www.structprollc.com/p/tutorial.html).

**Our proposal:** give Read, Calculate, Preview Changes and Apply Changes distinct actions. Version calculation templates and retain their inputs and outputs. Show Design versus Check mode beside results. A zero or missing utilization must never silently mean a passed check. **Acceptance example:** editing a result cell cannot write into ETABS; only an explicit, validated action can do so. Requirements R02, R03, R05 and R09 below.

### SideKick: small commands can deliver practical value

The historical demonstration shows focused extraction, load-input and geometry workflows in Excel. GenCol, CDC, LCM and the discontinued spColumn bridge are separate offerings, not included engineering capabilities. [SideKick product](https://excelcrib.com/downloads/spreadsheets/ETABS-Sidekick.html), [GenCol bridge](https://excelcrib.com/downloads/Plug-ins/ETABS-to-Prokon-GenCol.html).

**Our proposal:** make the first repeatable task short and predictable. Every imported force needs its member identity, units, combination, station and local-axis meaning. Keep retrieval separate from adding or replacing loads. **Acceptance example:** a failed command retry does not duplicate a load; the completion report identifies changed, skipped and failed objects. R04, R05 and R10.

### RCDC: preserve reviewed work and explain revisions

Historical update documents describe retaining adequate reinforcement, mapping levels and reporting changes. Indian-code reference packages exist, but the inspected examples are not current ETABS integration tests. [Beam/update change report](https://bentleysystems.service-now.com/sys_attachment.do?sys_id=b0bdb7d197118b540b8af4f3a253af74), [Indian validation index](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0110823).

**Our proposal:** treat engineer-selected reinforcement as a recorded decision. On revision, recheck it before suggesting a replacement; show what changed and why. Maintain a provision-by-provision code coverage list and independently worked references. **Acceptance example:** increased demand marks the earlier check as outdated, retains the earlier bar choice in history and identifies whether that choice still passes the supported checks. R03, R06, R07 and R11.

### ETABS MATE: detailing assumptions and editable outputs

The current guides disclose material-name-dependent defaults, detailing/check settings and a reset that discards column-section edits. Drawings and schedules provide a useful output benchmark. [Quick Start](https://www.etabsmate.com/File/ETABS%20MATE%20Quick%20Start_EN.pdf), [Reset behaviour](https://www.etabsmate.com/File/ETABS%20MATE%20Update%201.3.610.pdf), [Schedule catalogue](https://etabsmate.com/File/ETABS%20MATE%20Catalog_EN.pdf).

**Our proposal:** distinguish imported, calculated, defaulted and manually entered values. Display the consequence of resetting an override before applying it. Later, link each bar mark to the calculation and drawing revision that produced it. **Acceptance example:** an unmapped material prevents a verified result; a reset preview lists the overrides it would replace. A quantity report must disclose whether cutting waste and purchasing constraints are included. R04, R07 and R11.

### ACE OCP: a defined search objective and inspectable candidates

Its historical guide documents candidate models, section bounds/locks, quantities, feasibility and analysis limits. Modern compatibility remains unresolved. [ETABS guide, physical pp.55–72](https://www.aceocp.com/wp-down/html/ACE_OCP_ETABS2016_Guide/files/assets/common/downloads/publication.pdf).

**Our proposal:** introduce optimization only after one manually approved change can be evaluated reliably. Record allowed changes, grouping, constraints, unit rates and excluded costs. Preserve candidate files and results. **Acceptance example:** a cheaper candidate that fails a required check cannot be ranked as an acceptable recommendation. Say best found within the stated search, not guaranteed minimum cost. R08, R09 and R12.

### ConGro: separate conversation, execution and engineering acceptance

The founder distinguishes its assistant from a separately initiated optimizer. Historical fixes also illustrate why operational success needs separate engineering verification. [Founder clarification](https://www.linkedin.com/in/afrasayab), [Release disclosure](https://www.linkedin.com/posts/afrasayab_congro-ai-ai-for-structural-engineering-activity-7467302402027769856-BAg_).

**Our proposal:** future AI may explain supported results or draft a proposal; the same deterministic calculation and approval rules govern execution. Completion, convergence and passing all specified checks need different statuses. **Acceptance example:** an unsupported check is visibly unavailable, even if every automation command succeeded. Set time/iteration/cost limits for long operations and preserve recoverable state. R03, R09, R10 and R12.

### CivilAI: office-specific workflow knowledge has value

The public audit established a custom service offering rather than a delivered packaged competitor. Its fees do not estimate the cost of developing and supporting our product. [Service positioning](https://civilai.arpitkhandelwal.com/), [Pricing](https://civilai.arpitkhandelwal.com/pricing).

**Our proposal:** standardize the calculation engine and exchange format while allowing controlled office templates, bar preferences and report branding. Distinguish configuration from bespoke programming. **Acceptance example:** changing report branding cannot alter an engineering formula; a changed engineering preference creates a new recorded configuration version. R02, R06 and R13.

## 3. Lessons from the screened products and foundations

These products received narrower reviews. Their observations are useful design prompts, with lower confidence about complete behaviour. This section covers the remaining named comparisons without promoting screening into validation.

| Comparator | Saved evidence | Proposed lesson for StructAutomate |
| --- | --- | --- |
| ETABS and CSI API | Native design, tables and external automation already exist. [Features](https://www.csiamerica.com/products/etabs/features), [Developer](https://www.csiamerica.com/developer) | Benchmark the native task first; add value through review, traceability or less repeated effort. R04, R13 |
| SAFE | Adjacent foundation/slab host in the CSI workflow. [CSI sales](https://www.csiamerica.com/sales) | Keep future host support modular and separately tested. Foundation support remains deferred. R01, R06 |
| CSiXCAD | Model changes can flow into CAD while retaining drawing edits. [Product](https://www.csiamerica.com/products/csixcad) | Treat drawing edits and revision reconciliation as first-class requirements if detailing is added. R07, R11 |
| CalcTree | Typed, unit-aware connections and reusable calculation/report workflows are described. [Connection Nodes](https://www.calctree.com/blog/desktop-connection-nodes-launch) | Use typed inputs with explicit units and track dependencies from source to report. R02, R04, R05 |
| S-CONCRETE | Batch section checking and intermediate calculations; code coverage varies. [Product](https://www.siemens.com/en-us/products/simcenter/mechanical-simulation/s-frame/concrete/) | Develop one trustworthy check before batch processing; publish exact coverage. R03, R06 |
| VIS | Revised-model import and reinforcement transfer are documented. [Manual19.0](https://www.vis-concretedesign.com/wp-content/uploads/2026/01/User_Manual_1900.pdf) | Study reconciliation rules later; avoid silently attaching old reinforcement to a different member. R04, R07 |
| IDEA StatiCa Concrete | Specialist ETABS concrete links and local checks. [Integration](https://www.ideastatica.com/bim-links/supported-integrations/etabsconcrete) | Recognize when a problem needs a specialist tool; export clear inputs and scope limits. R06, R11 |
| PROKON Concrete / GenCol | Modular checks and module-specific code lists. [Concrete](https://prokon.com/concrete/), [GenCol specification](https://read.prokon.com/view/730985369/3/) | Separate connector accuracy from calculation-engine accuracy and licence rights. R04, R06, R13 |
| Tekla Structural Designer | Integrated design and model-linked reports in another host. [India product](https://www.tekla.com/in/products/tekla-structural-designer) | Compare total task effort and output consistency, including migration. R05, R11, R13 |
| ProtaStructure | File exchange with ETABS and integrated design/deliverables are advertised. [2027 release](https://protasoftware.com/community/blog/prota-structure-suite-2027-new-features/) | File exchange needs versioned mapping and discrepancy reports; it does not imply continuous synchronization. R01, R04 |
| CYPECAD | Documentation distinguishes redesign using prior forces from full analysis. [Analysis options](https://info.cype.com/en/product/cypecad-options-in-the-analyse-menu-on-the-beam-input-tab/) | Explain which changes invalidate analysis and force a rerun. R05, R09 |
| GoCalc | Separate AI and Excel offers; early-product evidence. [Product](https://gocalcsoft.somee.com/) | Define the licensed module and provider dependencies clearly. No product architecture change is justified. R13 |
| Structon.AI | Experimental/invitation-only claims; limited accessible evidence. [Product](https://structon.ai/) | Keep as a parked lead; infer no technical requirement from unverified feature breadth. |

The GenCol/CDC/LCM/spColumn bridge family is an integration-boundary lesson from the SideKick review, not a validated shared engine. A future external-module option would require current delivery, permitted use, exact transfer semantics and matching calculation validation.

### Development foundations do not replace engineering validation

| Foundation | Role in the existing research | Decision for our idea |
| --- | --- | --- |
| Excel-DNA | .NET/XLL development framework. [Introduction](https://excel-dna.net/docs/introduction/) | Retain the user-specified C# XLL baseline; prove its lifecycle in P0. R01 |
| PyXLL | Licensed Python integration, including end-user costs. [Pricing](https://www.pyxll.com/pricing.html) | A cost/architecture comparator; no reason from this review to replace the C# baseline. R13 |
| xlwings | Excel/Python automation with free and paid capabilities. [Pricing](https://www.xlwings.org/pricing) | Assess distribution and support if ever reconsidered; no Python dependency in P0. R01, R13 |
| BHoM ETABS Toolkit | Public integration toolkit. [Repository](https://github.com/BHoM/ETABS_Toolkit) | Potential mapping reference after version and reuse-licence review. R04 |
| ExcelCSIToolBoxAddIn | Public Excel/CSI project. [Repository](https://github.com/Anhbq1298/ExcelCSIToolBoxAddIn) | Study command/interface ideas later; source availability does not establish engineering correctness. R01, R04 |
| ETABS-mcp | Public action-interface claims with unresolved reuse/validation. [Repository](https://github.com/mdvaleed7/ETABS-mcp) | No dependency selected; future commands must use our ordinary approval and validation path. R09, R12 |
| Python in Excel | Cloud execution restrictions differ from desktop automation. [Microsoft documentation](https://support.microsoft.com/en-us/excel/python/data-security-and-python-in-excel) | Do not plan local ETABS control through this feature. Keep deployment assumptions explicit. R01 |

These are learning references. We have not approved reuse of competitor code, paid services, proprietary formulas or restricted outputs. Public descriptions can inform requirements without making those products dependencies.

## 4. Proposed requirements with acceptance examples

The following is a requirements register for discussion and later implementation. Each identifier links back to the source lessons above. Except for the supplied P0/P1 direction, these are recommendations, not completed features or newly approved engineering scope.

### R01 — Predictable Excel lifecycle and a supported environment

**Stage: P0; compatibility expands only with evidence.** Display product, Excel, runtime and XLL identities. Handle callback errors; support repeatable load, restart and unload/reload. Follow the supplied x64/net48 baseline and its specified diagnostic receipt. **Accept when:** the prescribed disposable-workbook checks pass and ETABS calls remain zero. Record untested environments separately from tested support.

### R02 — Pure calculation engine and versioned inputs

**Stage: P1, then reusable worksheets.** Keep calculation inputs, computation and results independent of Excel COM and ETABS. Give each calculation and configuration a version. UDF recalculation must not perform model writes or other external operations. **Accept when:** identical inputs produce identical results in a standalone test and in Excel; changing a report template does not change those results.

### R03 — Honest results with a defined meaning

**Stage: P1.** Display the check name, Design/Check mode where relevant, inputs, units, assumptions, intermediate values and governing result. Distinguish pass, fail, unsupported, missing input, outdated and execution error. **Accept when:** an unimplemented shear check cannot make the member appear fully verified because its flexural check passed. Initial supported beam geometry and provisions must be specified before coding the check.

### R04 — Validate every data boundary

**Stage: manual input in P1; ETABS import in P3.** Record model identity, revision, object identity/geometry, cases/combinations, units, axes, stations, materials and required tables. Distinguish defaults from source values. Preserve force components together with their originating case/station; component-wise envelopes must not masquerade as a simultaneous force vector. Reconcile changed names and geometry; do not trust a display label alone. **Accept when:** missing material mapping or ambiguous member matching blocks a verified output and tells the engineer exactly what to correct.

### R05 — Track which results belong to which revision

**Stage: P1 for inputs; P3/P4 for model runs.** Store a source snapshot, calculation version and analysis-run identity with each result. Define which input/model changes invalidate which checks. **Accept when:** changing a load after a saved check visibly marks that check and its report as outdated. Copying old result cells does not restore verified status.

### R06 — Publish narrow engineering coverage and reference cases

**Stage: P1 onward.** Specify code edition/amendments, member type, loading and detailing assumptions, supported provisions and exclusions. Use independently worked references with declared numerical tolerances; track formula version and regression cases. **Accept when:** the selected first beam check passes normal, boundary and invalid-input examples and every expected value has an identifiable independent basis. ETABS agreement alone is not sufficient validation.

### R07 — Preserve deliberate engineering choices

**Stage: P2/P3 for stored choices; P5 for wider detailing.** Save engineer overrides with value, reason, author/time and version. Recheck a retained choice after changed demand. Show resets and geometry conflicts before discarding work. **Accept when:** a renamed, split or merged member requires explicit reconciliation if identity is uncertain; old reinforcement is not silently transferred to it.

### R08 — Compare alternatives under the same assumptions

**Stage: manual alternatives in P2/P4; automatic search later.** Show dimensions, reinforcement, supported check results, quantities, rates and excluded costs together. Separate a member-only comparison from a globally reanalysed model. **Accept when:** a cheaper alternative remains labelled unverified until its required checks are complete; a candidate that changes stiffness cannot inherit the original model's analysis approval.

### R09 — Preview, approve and apply a specific model change

**Stage: P4, after read-only import is reliable.** Preview old/new values, affected members and the exact destination copy. Distinguish redefining a shared section from assigning an existing section to one member. Bind approval to that proposal and source revision; reject changed context. Read back applied values, rerun required analysis/design and verify the resulting state. **Accept when:** the original model remains intact, approval expires if the proposal changes and an unsuccessful reanalysis cannot produce a final passed revision.

### R10 — Recover transparently from partial failure

**Stage: P0 error handling; full transaction behaviour in P4.** Show completed, skipped and failed actions. Check current state before retrying. Preserve an audit trail and an identifiable recovery copy; make cancellation boundaries visible. **Accept when:** repeating a partially completed load operation does not duplicate loads and interrupted work cannot be mistaken for a completed revision.

### R11 — Issue reproducible, scoped deliverables

**Stage: first calculation report in P1; drawings/BBS later.** Attach source revision, calculation/code version, configuration, limitations and review status to outputs. Maintain history of superseded issues. Link future schedules to member/bar identities; distinguish engineering quantities from purchasing/cutting allowances. **Accept when:** a reviewer can reproduce a reported result from retained inputs, and old reports remain identifiable after a revised issue.

### R12 — Add search and AI behind proven controls

**Stage: P6, deferred.** Separate language assistance, deterministic checks and search logic. Define permitted variables, fixed constraints, cost/time/iteration budgets and stop reasons. Apply the same proposal/approval mechanism to AI-generated requests. Keep the calculation core independent of cloud AI; show any proposed external data transfer and require an explicit choice. **Accept when:** reaching an iteration limit, converging, passing checks and receiving engineer approval produce separate recorded outcomes. AI wording cannot convert an unsupported check into a pass.

### R13 — Make ownership cost and support understandable

**Stage: product planning now; commercial implementation later.** State host prerequisites, supported versions, licence unit, permitted client use, updates, transfer/recovery rights and data handling clearly. Link each delivered build to matching documentation, release notes and verification evidence. Track setup and review effort alongside fees. **Accept when:** a prospective buyer can work out the first-year and three-year cost under stated assumptions, and a pilot can measure total engineer-plus-reviewer time. Do not implement licensing/updating in P0.

## 5. A workflow a beginner can follow

Consider one beam whose loads change after an earlier calculation. This is a proposed example, not a tested project or a statement that the first release covers complete beam design.

1. **Identify:** select the member and see which project/revision supplies its data.
2. **Check inputs:** review units, materials, geometry, load context and supported calculation scope.
3. **Calculate:** run the specified check and inspect its workings. Keep unsupported checks visible.
4. **Compare:** examine an alternative reinforcement or section choice under stated assumptions.
5. **Review:** save the proposed change and the engineer's decision. Approval attaches to those exact values.
6. **Apply and rerun, once P4 exists:** change the identified model copy, read back the change, run analysis/design and review fresh results.
7. **Issue:** export the scoped calculation or revision report with its provenance and review status.

When the source moves from revision R3 to R4, an R3 result remains in history and becomes outdated for the new revision. It becomes current only after the appropriate new calculation and review. Think of a dated drawing: copying its numbers into a new sheet does not make it a newly checked design.

The future interface should make four things easy to find: **source and revision; inputs and assumptions; checks and explanations; proposed changes and history**. These describe later working screens. P0 retains only About, Diagnostics, Open Panel and the two demonstration UDFs from the original brief.

## 6. Development order and completion gates

These are proposed stages, not a time or cost estimate. Complete the evidence gate before expanding scope; teaching should use one small example, the user's implementation and a review of the result at each step.

| Stage | Deliverable | Gate before moving on |
| --- | --- | --- |
| P0 — Excel shell | Packed x64 XLL, Ribbon, diagnostic panel/dialog, pure demo UDFs | Original packaging/lifecycle receipt; zero ETABS calls; existing projects preserved |
| P1 — one beam check | Agreed calculation specification, pure C# function, Excel input/output and worked report | Independently checked examples and explicit unsupported scope; no ETABS dependency |
| P2 — reusable worksheet work | Batch rows, saved inputs, configuration/template versions, manual alternatives | Correct row mapping; outdated-result and override behaviour demonstrated |
| P3 — read ETABS | Narrow connector with input manifest, preview and import reconciliation | Known model mapped correctly; units/cases/stations verified; no model writes |
| P4 — one controlled revision | Preview, approval, model copy, read-back, reanalysis and final check | Repeatable changed-load/changed-section and interruption tests; original unchanged |
| P5 — broader engineering/output scope | Additional members/provisions, grouping and selected detailing | Separate reference cases and traceability for every added capability |
| P6 — search/optional AI | Bounded alternatives search and optional explanatory assistant | Reuses proven checks/transactions; clear stop reasons, budgets and acceptance states |

P1 must begin with a written definition of the beam calculation: geometry, supported loading/check, code provisions, inputs, outputs and exclusions. The existing brief does not yet settle those details. This is an engineering specification task, not a reason to resume broad competitor research.

Our first product pilot should prove one useful repeatable job. A broad list of member types, codes, drawings and AI features would make both teaching and validation harder before that job is established.

## 7. Pricing and commercial lessons to retain

The saved prices represent different purchases. SideKick's observed India offer was ₹17,576 including GST; RCDC's ₹1,73,563 annual starting figure belonged to an entire STAAD.Pro Advanced package, with standalone pricing unresolved. [SideKick offer](https://excelcrib.onfastspring.com/ETABS-Sidekick-Perpetual), [Bentley package](https://www.bentley.com/products/staad-pro/).

MATE's US$1,600 activation had qualified hardware/update rights. ACE OCP's €659 annual rental was clearer than its conflicting permanent price. ConGro's monthly/annual prices must be considered alongside credits, while StructPro had no verified numeric quote. These are dated reference points, not a price range for our product. [MATE price](https://www.etabsmate.com/price_en.htm), [ACE shop](https://www.ace-hellas.gr/shop/product/ace-ocp-gia-etabs/), [ConGro plans](https://congro.ai/), [StructPro purchase](https://www.structprollc.com/p/purchase.html).

**Proposed commercial design:** use a clear licence unit for any future deterministic desktop product, state included updates/support separately, and publish exact prerequisites. If optional AI later creates variable costs, disclose its budget and charging basis separately. Perpetual versus subscription, individual versus firm pricing and the actual amount remain open decisions.

Evaluate three costs separately: **building/supporting our software**, **operating it in an engineering office**, and **the construction quantities affected by its designs**. A lower concrete quantity does not prove lower construction cost; a free framework does not mean free development; a low licence fee does not prove lower review effort.

For an eventual pilot, record setup hours, total task and review time, corrections, support incidents and output acceptance on the same task using the existing workflow and our tool. A proposed value calculation is: net time recovered × the office's usable value of that time, minus incremental software, setup and operating costs. Do not assign market savings before measuring these inputs.

Own-use selection and commercial validation remain separate. Our office might rationally use an existing entitled tool; that does not settle whether another segment needs a product from us. Conversely, a useful internal script does not establish an affordable repeatable commercial offering.

## 8. Parked research: exact remaining items

**All items below are parked.** Priority means the order if the user later resumes relevant work; it is not a scheduled task or authorization to browse, purchase, contact vendors or run models. First reopen the question that could change a concrete decision. Stop once comparable evidence answers it, or record that it remains unavailable.

### A. Products not yet studied closely

| Parked item / priority | Decision it could change | Evidence and reopening condition |
| --- | --- | --- |
| B01 Native ETABS/SAFE/CSiXCAD — high | Whether a separate feature earns its effort/cost | Reopen before a pilot or buying decision; complete the same scoped task natively and record total effort/output gaps |
| B02 VIS — high for revisions | Override/reinforcement reconciliation design | Reopen before P4/P5 design; inspect matching, renamed/split members and retained edits on a current supported workflow |
| B03 S-CONCRETE — high for member checks | Build versus buy for Indian checks | Reopen if considering purchase/engine integration; obtain exact element/code matrix, current import and one worked comparison |
| B04 CalcTree — medium/high for templates | Internal workbook library versus another platform | Reopen if calculation reuse is the main bottleneck; demonstrate dependencies, outdated results, enterprise connector scope and quote |
| B05 IDEA StatiCa — conditional | Handling specialist members/details outside our scope | Reopen when a real excluded detail needs it; identify destination product, supported codes/link and accepted calculation |
| B06 PROKON/GenCol; CDC/LCM bridges — conditional | External engine integration versus our own check | Reopen only for an intended module; establish current delivery, licence, mapping and independent transferred case; keep discontinued spColumn bridge separate |
| B07 Tekla, ProtaStructure, CYPECAD — conditional | Retaining ETABS versus migrating the office workflow | Reopen only if core-host replacement is acceptable; same-project comparison including codes/modules, migration and review cost |
| B08 GoCalc and Structon.AI — low | Whether a newer product changes the shortlist | Reopen after a concrete stable release/demo changes evidence; avoid repeating broad marketing searches |
| B09 Excel-DNA runtime/packaging — P0 task | Whether the specified shell works on this machine | Use the brief's environment inventory and lifecycle evidence; no renewed market survey needed |
| B10 PyXLL, xlwings, Python in Excel — low | Whether to reconsider the C# baseline | Reopen only if a documented requirement cannot be met economically by the baseline; compare runtime, distribution and licence consequences |
| B11 BHoM Toolkit, ExcelCSIToolBoxAddIn, ETABS-mcp — conditional | Reuse of a specific component | Reopen before code reuse; inspect exact licence, version, boundaries and a reproducible case; no dependency chosen now |
| B12 FOUNDA MATE/NICA and wider foundations — low | Whether to expand beyond our member/revision scope | Price mentions are not close studies; reopen only after foundation or related scope is explicitly selected |

Items B01–B12 are a decision backlog. The existing market report contains the current screening evidence and source links; no new availability or price has been assumed here.

### B. Unresolved questions in the completed close studies

- **B13 StructPro:** obtain an actual current package, compatible Excel/ETABS matrix and consistent team licence/quote. Then demonstrate a model write and a calculation/report revision on that build. A repaired website alone would not close the behaviour question.
- **B14 SideKick:** confirm delivered package, Excel bitness/current ETABS support, device recovery and post-included-support cost. Complete one extraction and one load-change task, including read-back and repeated-command behaviour. Historical tutorial frames are insufficient.
- **B15 RCDC:** obtain a matching standalone India quote or verify existing entitlement. Demonstrate current ETABS import and changed-load/geometry updates, with reference values independent of RCDC. Separate retained design from upstream write-back and automatic reanalysis.
- **B16 ETABS MATE:** confirm current delivered build, Indian-code applicability, client-use rights and transfer/update charges. Demonstrate override preservation/reset after reimport, material mapping and schedule reconciliation. Keep old sample issues separate from current behaviour.
- **B17 ACE OCP:** resolve current compatibility, trial access, licence rights and the permanent-price discrepancy. Reopen only if search is needed; use a feasible reference, declared rates/constraints and an independently rerun final candidate.
- **B18 ConGro:** resolve supported versions, current delivery, evaluation rights and model-context data handling. Demonstrate a changed member, partial failure, reanalysis and actual usage charges. Separate chat actions from optimizer behaviour and engineering checks.
- **B19 CivilAI:** if procurement is considered, require a delivered-workflow demonstration, acceptance criteria, ownership/redistribution rights and post-support costs. No public package or validated deliverable was established; a service price is not our build budget.

For B13–B19, close a question only against an identified product build, terms/quote and a retained result. Reopen just the candidate relevant to the immediate task; there is no need to test every competitor before learning or building P0/P1.

### C. Evidence needed for engineering and a business decision

- **B20 First calculation specification — before P1:** decide exact beam scope and applicable provisions; retain independently worked expected results, units and tolerances. Completion means a reviewable specification, not a general claim of Indian-code support.
- **B21 Common revision benchmark — before P4/pilot:** define changed load, changed section, renamed/split member, missing data and interrupted command cases. Completion requires original/working files, input snapshots, expected outcomes, final read-back and scoped check reports.
- **B22 Customer need and willingness to pay — before a commercial commitment:** when outreach is separately authorized, examine actual recent revisions, existing licences, reviewer time and purchase decisions in relevant offices. Completion means a sufficiently consistent recurring problem and meaningful pilot commitments, not a favourable reaction to a feature list.
- **B23 Economics and support — before sale:** measure setup/review/support effort and retention in a narrow pilot; specify distribution, updates, recovery, data handling and permitted use. Completion means defensible operating cost and contractual scope; final selling price and market size remain unknown.

## 9. How we will use this document

Use the market report as the evidence archive, this blueprint as the proposed requirement set, and the original Windows brief as the authority for P0. Keep research findings, design proposals and verified implementation results visibly separate.

The next instructional step, when implementation resumes, is the P0 environment inventory and the meaning of each shell component. After its acceptance receipt, define and implement the narrow P1 beam calculation. Later lessons should each cover the concept in plain language, a small example, the user's implementation steps, expected output and one meaningful verification.

The synthesis is complete at the desk-review level. Research remains paused. Current runtime behaviour, engineering validation, procurement rights, customer value and final pricing remain explicitly open; they should be revisited only at the relevant decision gate.
