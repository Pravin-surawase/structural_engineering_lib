---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# StructAutomate: product foundation and delivery plan
> Version 2 · 3 September 2026 · Revised using the completed research and engineering audit

**Historical proposal — phase sequence superseded.** This synthesis was written before the intended original XLL architecture was supplied. Its P2–P6 numbering does not match that source. Use the [current plan](../current-plan.md) and [corrected comparison](../phase-review.md) for the roadmap. The Word copy remains the unchanged earlier snapshot; it does not contain this correction notice.

**Decision: keep the Excel-DNA direction and strengthen the way engineering knowledge becomes a delivered feature.** Our existing work contains substantial mechanics, reinforcement logic and worked examples. The next advantage to prove is that these pieces help an engineer check a real revision accurately, understand the result and preserve reviewed decisions with less repeated work.

This was the earlier planning synthesis. Its engineering recommendations and C01–C08 acceptance examples remain useful, with corrected phase assignments in the current research map. It does not certify the product or change the original P0 task. Research remains paused. Product implementation, installed Excel acceptance, engineering sign-off and commercial validation remain outstanding.

## 1. What changes, and why

The initial direction was sound: a native Excel shell, one C# beam calculation, reusable worksheets, read-only ETABS import, then controlled model revisions. Keep that order. The depth audit changes how we prepare and accept those stages. [S1–S4]

| Finding from our research | Change to the plan | Practical consequence |
| --- | --- | --- |
| The library has useful interacting engineering, but public, experimental and incomplete routes differ. | Promote one named capability at a time. | A useful beam function does not silently bring columns, seismic design or a complete beam approval into scope. |
| Sourcebook has meaningful examples and boundary cases, plus a verified narrative/input mismatch. | Curate the selected records and distinguish independent scenarios from related regressions. | A passing numerical test cannot make an incorrect explanation acceptable. |
| The older product has useful recovery patterns, but its ETABS adapter and beam worker still return held results. | Reuse selected contracts and lessons after inspection; keep the new runtime small. | The old host stack is not evidence that the intended XLL workflow already works. |
| A recent ETABS acquisition exercise proved some table mapping; its comparison epoch remained blocked. | Test mapping and result freshness separately. | Correct rows and field names do not prove that forces belong to the current model state. |
| Competitors already offer many individual workflow features. | Measure the complete engineering-and-review job. | Repository depth and feature counts do not establish customer value or a selling price. |

The core product hypothesis is now precise: **for a recurring Indian RC member revision, preserve an engineer's chosen inputs and reinforcement, recheck the supported scope, explain changes, and eventually verify an approved update on a model copy.** Start with one rectangular beam flexure check. Broader member design remains a later capability.

## 2. Give every project a clear role

Think of the system as a workshop. Excel is the workbench. The C# calculation is the measuring instrument. The structural library supplies engineering methods to study. Sourcebook supplies worked exercises. StructProof demonstrates how to show the workings. ETABS supplies model context and analysis results when the connector is ready. Each has a different job.

| Asset | Intended role | Rule for reuse |
| --- | --- | --- |
| New StructAutomate XLL | Excel commands, input/output and the delivered C# calculation | Own the user-facing behaviour and support contract. Keep the calculation independent of Excel COM. |
| structural_engineering_lib | Engineering reference, candidate algorithms, contracts and regression examples | Pin exact source; inspect the selected route and assumptions; translate or adapt deliberately and validate the delivered C# behaviour. |
| StructProof | Typed inputs, proof steps, explicit exclusions and guarded calculation patterns | Reuse patterns selectively. Its Python runtime and separate roadmap do not become XLL dependencies. |
| Sourcebook | Curated worked references, explanations and comparison methods | Review selected cases and their independence. Derive text, drawings and results from one consistent record. |
| Older optimizer and beam/column projects | Office workflow knowledge, recovery examples and interface lessons | Evaluate each reusable component separately. Prototype formulas and active-model mutation paths are not calculation or transaction authorities. |
| Future ETABS adapter | Explicit acquisition and later controlled writes | Exchange typed snapshots. Prove identity, units, simultaneous force context and freshness on identified installed versions. |

**The intended runtime is simple:** Excel interface → C# calculation → scoped result and explanation. At P3, an ETABS adapter supplies reviewed input snapshots. At P4, a separate command path applies an approved proposal to a model copy and verifies new results. Worksheet recalculation never performs an external write.

**The development evidence path is separate:** pinned references → reviewed specification → independently derived expected results → C# implementation → comparisons → acceptance receipt. Python may support offline reference work later; an end user does not need Python for the planned XLL. P0 retains its complete prohibition on companion hosts, Python, Node, WebView2 and engineering migration. [S1, S3, S4]

We will not maintain two silently interchangeable production engines. If a C# result disagrees with a Python comparator, record the disagreement, its assumptions and the resolution. Agreement with a second implementation helps; it does not replace a defensible engineering reference.

## 3. Make P1 one concrete calculation

**Working choice for P1: check the flexural capacity of a rectangular singly reinforced section against a supplied factored bending moment.** This choice narrows the earlier unspecified “one beam calculation”; it is a planning decision, pending the engineering specification and reference-case gate below. It does not authorize a claim of complete beam design.

Checking a supplied choice is a useful starting point for our eventual revision workflow. The question is, “Does this specified section and tension steel satisfy this particular flexural check under these assumptions?” Required-steel design, bar selection and practical arrangement checking are separate later increments.

### P1a — Write and review the calculation contract

Specify the adopted IS 456 edition and amendments, applicable provisions, exact material grades/ranges, rectangular geometry, supported bending direction, singly reinforced assumptions and limit handling. Review the applicable authoritative engineering references when this work resumes. This planning document does not settle clause interpretations or manufacture expected design values.

The proposed input record contains a case/member label, section width and overall depth, declared effective depth, concrete/steel grades, provided tension-steel area, factored moment and a clearly defined tension-face convention. Units and the source of each value are explicit. Effective depth is supplied in this first calculation; it is not inferred from an unimplemented bar arrangement. Axial force, compression reinforcement and flanged geometry are outside this first route.

Define outputs before coding: normalized inputs, assumptions, intermediate values including neutral-axis/depth information, limiting conditions, capacity, demand/capacity comparison and an explanation. The specification must decide which minimum/maximum reinforcement conditions are included, which are exclusions and which make the assumed calculation route inapplicable. An inapplicable branch cannot be presented as an ordinary passing capacity check. Do not silently cap an over-reinforced section and report a pass using an assumed yielding-steel formula.

Cover missing inputs, nonfinite numbers, invalid dimensions, inconsistent depth, unsupported materials, sign conventions, units, equality/tolerance behaviour and the singly reinforced limit. Record whether each rejected case means invalid input or unsupported engineering scope. Separate numerical comparison tolerances from display rounding and the engineering acceptance inequality. Begin with two separately worked ordinary cases using materially different supported inputs, a meaningful supported failure, a derived applicability boundary and its adjacent values, plus invalid/scope cases. Retain their expected intermediate values before implementing the C# result.

For each borrowed item in this small packet, record its pinned source, intended role (implementation reference, independent comparison or explanation), reuse treatment, unit conversion and applicability mapping. Retain already established ownership/rights evidence; investigate only unresolved rights relevant to the selected reuse or future distribution. No universal contract for every existing library is required.

### P1b — Implement the calculation independently of Excel


Implement a pure C# function: explicit input in, explicit result out. It has no Excel/ETABS dependency and no file or network operations. Compare it with the reviewed expected values and selected frozen reference implementations. Failures must identify the affected input or unsupported condition in plain language.

### P1c — Expose and explain the same result in Excel

Add a small input/output surface and worked calculation report. The standalone calculation, Excel display and report must agree on inputs, units, values, limits and result identity. Changing a governing input immediately invalidates the displayed prior result until recalculated; P2 extends this to saved rows and revision comparisons. Test the packed XLL for the actual P1 feature; P0 installation success does not validate later engineering code.

The result label should say, for example, “Flexural capacity check: satisfied within the stated scope.” Shear, torsion, deflection, anchorage, detailing and seismic checks remain visibly outside this result. A whole-beam green approval would misrepresent P1.

**Why not start with the deepest library feature?** A small complete calculation lets us learn C#, test the explanation, expose input mistakes and prove delivery. The deeper reinforcement work becomes a valuable next feature once this path is trustworthy.

## 4. Use one traceable record from input to report

A result needs an identity, like a drawing needs its drawing number and revision. Store the capability and calculation version; exact normalized inputs and units; input provenance; engineering/configuration basis; delivered build identity; result and intermediate steps; and report-template identity. Record review status separately. At P3/P4 add source model, object, geometry and analysis-run evidence. Implement fields only when the stage needs them. A small immutable snapshot is enough initially; no database, generic event store or dependency-graph platform is required for P1.

Version labels alone are insufficient. The audit found current source and a released wheel sharing a version string while containing different work. Pin a source commit and packaged artifact hash alongside the human-readable version. The Sourcebook comparator pin must also be explicit; updating the pin requires reviewing what changed. [S3, S4]

Use three separate questions in the interface:

- **Did the operation run?** Completed, failed or cancelled describes execution.
- **What did this check conclude?** Satisfied, not satisfied, unsupported or insufficient input describes the named engineering check.
- **Does the result still apply, and has it been reviewed?** Current/outdated/unknown and reviewed/unreviewed describe applicability and review.

Store these separately rather than putting every meaning into a single PASS flag. An operation can complete successfully and return an unsupported check. A previously satisfactory result can be outdated. A current calculated result can still be unreviewed.

For a simple revision example, keep an earlier result as revision R3. Change only the factored moment for R4. Preserve the engineer's previous reinforcement choice, mark its R3 result outdated for R4, recompute the supported check, and show the input and result differences. Copying R3 cells into an R4 sheet must not restore current status.

Approval later binds to exact proposed values, source state and destination copy. A changed proposal or model context requires a new review. Changing report branding must not change engineering arithmetic; changing an engineering assumption must produce a new calculation identity.

## 5. Turn our knowledge assets into trusted reference cases

The Sourcebook findings justify a specific curation gate. BEAM-RFLEX-028's prose describes different geometry, material and reinforcement from its frozen inputs and calculation steps. The audit established this inconsistency; it did not establish that the numerical calculation itself is wrong. Keep that record's customer-facing explanation out of the selected P1 evidence until reconciled and reviewed. [S4]

For every selected case, retain the physical scenario, typed inputs, governing assumptions, independently derived expected values, units, tolerances, intermediate steps, provenance and review status. Generate repeated descriptions from the same inputs where practical. Review interpretive prose separately. Check that the report and any diagram describe the calculation actually performed. Curate the selected packet; repairing the entire Sourcebook is not a prerequisite for P0 or P1.

Distinguish four kinds of evidence:

- **Independent physical scenarios** exercise materially different engineering behaviour.
- **Boundary regressions** vary a case around a limit, including equality, to test disposition changes.
- **Input and scope cases** prove that invalid or unsupported requests are handled honestly.
- **Teaching examples** explain a method; they may overlap with the other categories.

Keep these categories and overlaps visible. The inspected RFLEX ledger had 33 records: 29 numerical records and four validation/unsupported matrices. Sixteen numerical records were equality or near-equality variants, with another unit-conversion repeat. These are useful regressions; they are not 33 independently validated engineering situations. [S4]

Also record the level of independence: output from the same implementation, a separate implementation, a separately derived analytical/reference calculation, or independent engineering review. Two implementations based on the same assumptions can share an error. Preserve unresolved differences instead of changing expected values merely to make comparisons pass.

**Capability promotion rule:** a feature moves from reference material into the delivered product only after its scope is explicit, its selected cases are curated, its expected results have a defensible independent basis, the delivered implementation matches that basis, its explanation is consistent, and its intended deployment is verified. Claims of professional readiness additionally need engineering review and the pilot/release evidence described below. Tests alone do not provide that review.

## 6. Delivery stages and the evidence that closes each one

No stage below is marked accepted by this document. Cached test runs, read-only audits and machine preflight are supporting evidence with limits; they are not substitutes for the stage's own receipt. Stages are work order, not time or cost estimates.

### P0 — Prove the specified Excel shell

Follow the preserved Windows task exactly: new isolated repository only after its preservation checks; net48 primary target; Excel-DNA 1.9.0; packed x64 XLL; About, Diagnostics, Open Panel; a WinForms diagnostic panel/dialog; SA_HELLO and SA_ADD. A net8 comparison is conditional on the brief's existing-prerequisite rule. No new architecture is introduced here.

**Exit evidence:** the original task's build, pure-function/diagnostic tests, installed Excel load/restart/unload and callback/panel/UDF checks, artifact hash and machine-readable receipt. Retain its exact acceptance-disposition vocabulary and trust/signing rules. P0 must record zero ETABS calls and zero changed paths in preserved projects. Existing preflight is not that receipt. [S1, S5]

### P1 — Prove one calculation and its explanation

Complete P1a–P1c above. **Exit evidence:** reviewed scope and reference packet, standalone and packed-XLL calculation results, normal/boundary/invalid/scope cases, consistent report, and visible exclusions. A first passing example alone does not close P1. This stage closes the engineering definition portion of B20 only when that work is actually completed.

### P2 — Make the same check reusable through revisions

Add saved input rows, stable row/case identities, versioned settings, scoped manual alternatives, input-change detection, retained choices and a readable comparison report. Compare alternatives under the same fixed supplied demand; do not imply that a changed section has been globally reanalysed.

**Exit evidence:** reorder rows, add/delete a row, change demand, change a supported input and reset an override. Results remain attached to the correct case, old results become outdated, and earlier decisions remain in history. A narrow internal-use pilot can now assess this manual-input job after engineering review.

**Next engineering increment:** actual bar arrangement, centroid/effective-depth feedback and spacing checks are the strongest near-term extension suggested by the library audit. Define and validate this as a separate capability before making arrangement or constructibility claims. It is not silently included in P1 or achieved by merely comparing steel areas. It need not block a later read-only connector that transfers only already-supported inputs.

### P3 — Import one narrow ETABS snapshot

Choose one identified installed ETABS/API version and one supported extraction path. Preview member matching, geometry, materials, units, axes, combinations and stations. Preserve simultaneous force components from the same case/station; independently enveloped maxima must not become a fictitious simultaneous vector.

**Two exit checks are required:** mapping agrees with an independently inspected known model; and the run/state evidence establishes what the imported results represent. The earlier accepted SQLite fields/row counts establish part of acquisition, while its blocked comparison epoch remains a separate unresolved issue. If freshness cannot be established, retain the snapshot as unknown/outdated and prevent a current engineering conclusion. [S3]

P3 performs no model writes and does not trigger analysis/design. It may ask the engineer to supply a newly analysed and saved state outside the connector. Evidence must describe saved-file versus attached-memory state accurately; a file timestamp alone cannot prove freshness. Other versions remain untested until demonstrated.

### P4 — Prove one approved revision on a model copy

Choose one change type, such as a supported section assignment, and specify exactly which objects it affects. Preview old/new values, shared-section consequences and the destination copy. Bind approval to the proposal and source state. Apply, read back, run the required analysis/design sequence, acquire fresh results and recheck the supported scope. Changed-demand behaviour can be exercised using a separately prepared source revision; supporting both load editing and section editing is not required for the first controlled transaction.

**Exit evidence:** the source model is preserved; altered proposals or context invalidate approval; read-back matches; partial failure and retry do not duplicate actions; cancellation leaves a known disposition; unsuccessful reanalysis cannot yield a final accepted revision. A recovery record says what completed and what requires inspection. Do not promise automatic rollback unless that behaviour has itself been demonstrated.

This stage can support a controlled ETABS revision pilot. It still does not establish complete building design, all code compliance or production readiness across unspecified environments.

### P5 — Add engineering and deliverables according to demonstrated need

Select the next capability from actual pilot work. Options include practical beam reinforcement, further beam checks, stable column routes, selected foundation checks or scoped schedules. Experimental P–M–M, partial joint checks and broad detailing remain clearly separate until promoted with their own evidence.

**P5 is a recurring capability gate.** Qualified beam-only P6 work can complete the first beam release without first adding columns, slabs, walls or foundations. Qualify the checks and interactions required by that beam search; P1 flexure alone does not establish a constructible, feasible beam candidate. The original element-family expansion remains a longer-term direction, as mapped in the phase crosswalk.

**Exit evidence for each addition:** specific provisions and exclusions, curated references, independent comparisons, connected input-to-report cases and regression impact. Confirm quantities, diagrams and schedules use the same member/revision and reinforcement choices as the accepted calculation. Do not make every library feature a release requirement.

### P6 — Search within proven limits; add AI only for a useful job

Start automatic search only after a manual alternative can be evaluated and, where relevant, applied/reanalysed reliably. State candidates, constraints, grouping, locks, rates, exclusions and budgets. Report “best found within this search.” A cost-ranked candidate with missing required evidence remains on hold.

Local enumeration/ranking can be qualified without ETABS writes. Its result remains locally screened. A model-verified search requires the accepted P4 transaction, fresh copied-model analysis, all declared governing checks and an independently rerun selected candidate. Local ranking cannot inherit that disposition. AI is optional in either workflow.

An optional assistant can explain supported results or draft proposals. It follows the same calculation, review and transaction path. It does not turn missing checks into acceptance. **Exit evidence:** bounded jobs, inspectable candidates, honest stop reasons, final verification and measurable benefit beyond the existing deterministic workflow.

## 7. A small, connected acceptance project

Use one controlled beam scenario through the relevant stages instead of accumulating unrelated demonstrations. The following are planned acceptance challenges, not completed tests and not numerical design examples. Expected engineering values and tolerances belong in the P1 reference packet.

| Challenge | First stage | Evidence it should produce |
| --- | --- | --- |
| C01 Base check and explanation | P1 | Same inputs, scoped result and workings in standalone C#, Excel and report. |
| C02 Limits and missing information | P1 | Reviewed behaviour around the governing limit; invalid/unsupported requests cannot appear accepted. |
| C03 Changed demand, retained choice | P2 | Previous result becomes outdated; same chosen steel is rechecked; revision report explains the change. |
| C04 Actual reinforcement arrangement | Separate arrangement capability | Changed layers/centroid alter effective depth and relevant checks consistently; area alone is insufficient. |
| C05 Imported identity and forces | P3 | Known member/case/station, units, axes and material mapping agree with an independently inspected source. |
| C06 Stale or ambiguous ETABS context | P3 | Missing freshness or uncertain renamed/split-member mapping is visible and blocks a current conclusion. |
| C07 Changed section on a copy | P4 | Exact preview/approval, scoped change, read-back, fresh analysis and new supported check. |
| C08 Interrupted or repeated command | P4 | No duplicated mutation, preserved original and a clear recovery disposition. |

Run each challenge when its feature exists. P0 should not acquire this whole test burden. Add further tests only for a concrete engineering risk, a discovered defect or a required stage gate.

## 8. Resolve audit findings at the stage they affect

**Before P1 reference selection:** identify the precise structural-library commit and calculation route, the StructProof/Sourcebook pins used, and the selected examples. Reconcile any narrative/input discrepancy in those examples. Review adaptation/redistribution rights for material actually reused. A public repository or a project we own does not by itself settle the rights to every embedded reference or third-party dependency.

**Before depending on a newly packaged library artifact:** resolve the observed historical clean-wheel fixture/replay failure against the exact proposed artifact. The audit recorded one failed weekly check while other suites passed, followed by source changes without an observed later equivalent successful run. This is an unresolved packaging/evidence question; it is not proof that current mathematics is wrong, and it does not block the independent P0 shell. [S3]

**When consulting legacy projects:** retain workflow ideas but replace the confirmed unit/deflection error and unconditional torsion-OK behaviour before any relevant formula reuse. The older column assistant's reinforcement selection is not an independent general P–M–M solver or proof of minimum construction cost. Its active-model update/error paths do not satisfy P4's planned transaction contract. [S3]

**Before ETABS comparison:** resolve freshness and state provenance separately from schema completeness. An old or simulated adapter, cached C# tests and Ubuntu CI do not establish installed Windows Excel/ETABS behaviour. Identify what each result actually tested. [S3]

**Before commercial release:** verify the intended clean-machine installation and recovery path, supported versions, exact packaged build, code-signing/distribution approach, update/support responsibilities, dependency rights and permitted customer use. These decisions enter at the release gate; they do not add an installer, updater or licence system to P0.

## 9. Test value for our office and for customers separately

The library's depth can lower development effort, improve explanations and create a growing regression corpus. Its lasting value after release depends on keeping those assets consistent and using them to diagnose real defects. It also creates maintenance work: duplicated implementations, changing codes, host-version differences and inconsistent examples can consume the savings.

For reuse, compare **avoided implementation effort with adaptation, independent validation and continuing maintenance**. A large existing module is not automatically cheaper to adopt than a small well-understood implementation.

For the first internal pilot, choose one recurring task already within the delivered engineering scope and compare it with the office's current workflow. Capture setup, engineer time, reviewer time, corrections/rework, support interventions and accepted output. Record training effects and task complexity so an easy demonstration does not masquerade as a broad saving. Stop scope expansion if review effort or correction burden outweighs the benefit; fix the narrow workflow first.

For a future commercial decision, require evidence that relevant offices repeatedly encounter the problem, can adopt the product and will commit to a meaningful pilot or purchase. Outreach needs separate authorization. Existing licences and good native workflows may make a competing or bundled tool the rational choice for some offices.

Keep three budgets distinct: **our development/support costs; the customer's ownership/operation costs; and the construction quantities/costs being compared.** The saved competitor prices belong to different licence units, packages, dates and support terms. They do not form our target price range. The earlier report retains those numbers and qualifications; this plan does not refresh them. Selling price, licence model, development budget and market size remain unproven. [S2]

Before sale, cost the intended licence/support arrangement with measured pilot assumptions, including first-year and three-year customer costs. If optional AI creates variable charges later, show those separately. Our competitive claim should describe an observed supported workflow benefit, with its scope and evidence, rather than claiming uniqueness or using repository/test counts as a proxy.

## 10. Maintain the foundation after release

Treat a reported discrepancy as a reproducible engineering question. Retain the exact inputs, calculation/build identity and environment; reproduce the issue; derive an independent expectation; fix the bounded cause; add the regression case; and review which capabilities and prior outputs may be affected. A new release must not silently relabel old reports as recalculated.

A changed code basis, reference case, configuration or dependency needs a documented impact review proportional to the change. Preserve known disagreements and experimental scope. Keep calculation changes separate from report styling where possible so reviewers can see which engineering outcomes could change.

This is how the projects can remain a strength after completion: the engineering library informs improvements, curated examples explain and challenge them, the product carries exact identities into real jobs, and reported failures return as understood regression cases. The quality of that feedback matters more than simply adding more functions.

## 11. How we will learn and implement

You remain the implementer. Each lesson will explain the concept in simple language, show a small example, ask you to predict the result, give a short implementation step, verify the outcome and record what it proves. We will distinguish the behaviour we observed from what we still assume.

The next implementation lesson remains P0: explain an XLL, a native Ribbon callback, a pure UDF and the packed artifact; review the saved inventory; refresh only information necessary for the task's preservation and environment checks; then build the prescribed shell. The existing preflight is dated evidence, not permission to assume the machine or target directory remains unchanged.

After P0 acceptance, the next lesson is P1a's engineering contract and worked reference. We will use a small diagram and step-by-step arithmetic there once the exact scope and references are settled. We will not invent a design example here merely to make the plan look complete.

## 12. Plan authority, requirements and parked work

**Authority correction:** the earlier claim that this v2 synthesis defined the product roadmap is superseded. Follow current user instructions, the supplied original XLL architecture for its phase meanings, and the narrower Windows brief for the current P0 packet, as explained in the current plan. This v2 document, the earlier blueprint and research/audits are supporting history. The structural library, StructProof and Sourcebook retain their own repository roadmaps; their phase names do not advance the XLL stages.

The existing R01–R13 identifiers remain valid. This version strengthens R01 with distinct installed-stage evidence; R02/R04 with explicit asset and data boundaries; R03 with separate execution, engineering and applicability/review states; R05 with exact input/build/reference identities; R06 with curated cases and independence levels; R07/R08 with retained choices and scoped alternatives; R09/R10 with exact approval, copy, read-back and recovery evidence; R11 with input-to-explanation consistency; and R12/R13 with measured search/commercial value. No requirement is marked implemented by writing this plan.

**B01–B23 remain parked with their original identifiers, descriptions and reopening conditions in the earlier blueprint source.** This revision does not close them. B09 is addressed by executing P0, B20 by completing P1a and its references, B21 by the relevant connected revision challenges, and B22/B23 by later authorized customer and pilot work. Each closes only when its evidence exists. Reopen a competitor question only when it could change a concrete build/buy/feature decision.

### Evidence used in this revision

- **S1 — Original task:** [Preserved Windows P0 brief](../windows-p0-task.txt). Binding shell constraints and acceptance receipt.
- **S2 — Prior synthesis:** [Product blueprint and all 23 parked items](../research/requirements-and-parked-work.md) and [market report source](../research/market-study.md). Competitor observations, costs and R01–R13. Original source dates and uncertainty remain in those documents.
- **S3 — Readiness audit:** [Foundation and GitHub readiness assessment](../research/foundation-readiness.md). Exact repository/artifact identities, CI, installed-evidence limits and legacy defects.
- **S4 — Engineering depth:** [Engineering depth and product strength](../research/engineering-depth.md). Source-level engineering evidence, Sourcebook denominators and narrative defect, independence and scope limits; includes pinned GitHub code links.
- **S5 — Existing preflight:** [P0 readiness](windows-p0-readiness.md). Useful inventory history, distinct from a completed runtime receipt.

All recommendations here are synthesis and planning judgments based on these saved sources. No new competitor search, refreshed quote, engineering validation run or vendor commitment is implied.
