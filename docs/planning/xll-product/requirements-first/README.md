---
owner: Main Agent
status: proposed
last_updated: 2026-09-03
doc_type: spec
complexity: advanced
tags: [beams, excel, csharp, requirements, contracts]
---

# Standalone Excel beam product: requirements before migration

The [automation requirements and C# foundation](../automation/README.md) extend this dated research with complete beam-workflow coverage and implemented foundational APIs. Use that package and the current plan for ongoing implementation; this directory preserves the original research, source inventory and failure evidence.

**Decision date:** 3 September 2026. **Primary workflow selected by the owner:** standalone beam design in Windows Excel. **Status:** research and proposed product specification; no C# engineering implementation or installed acceptance is established here.

The recommendation is to build a reusable C# calculation core and an Excel-DNA interface, starting with one complete ordinary beam workflow. The three existing projects provide useful calculations, cases and lessons. They do not make a reliable product a mechanical translation. The decisive work is reconciling engineering assumptions, preserving input/result identity, specifying what “complete” means, and delivering an understandable workbook and calculation report.

This packet supplements the [current XLL plan](../current-plan.md). It does not renumber its P0–P6 phases, replace the separate library beam programme, authorize a release, or silently expand the Windows P0 shell exercise. The user's request here authorizes research and specification. “Professional signatures” is interpreted as function/API contracts; this specification does not create an engineer's certification or signature.

## The deliverable and its authority

The [requirements register](requirements.json) is the canonical proposed acceptance inventory; [CSV](requirements.csv) is its convenient projection. The [failure register](failure-register.json) connects observed or historical problems to prevention requirements. The [operation catalogue](operations.json) connects each proposed public signature to the [example index](example-index.json). The [source records](sources.json) and [corpus summary](corpus-summary.json) preserve provenance and research limits.

Three wire contracts are concrete drafts: [section request](section-request.schema.json), [section result](section-result.schema.json), and [validation result](validation-result.schema.json). The five member/application operations are scenario specifications, not frozen wire schemas. This is deliberate: their fields depend on agreed analysis, detailing and report profiles. Every one has an attached scenario, but only OP01–OP03 have machine-checkable payloads in this packet. No file here is a production implementation or proof of numerical correctness.

## What the research found

The GitHub index contains 150 library issues and 47 StructProof issues. Of the library titles, 137 match repeated automation-alert patterns; these are not 137 independent engineering defects. Sourcebook has issues disabled, so its correction records, route contracts and cases provide the issue evidence. All returned issue records were indexed; selected high-impact bodies, source paths and histories were examined. This was not an exhaustive audit of every PR discussion, CI log or possible latent defect. Closed issues show recorded work status, not independent confirmation that a future C# product passes.

The inspected Sourcebook snapshot contains nine beam routes, 154 numerical case records and 26 other records. Matrices can contain multiple scenarios. Those counts describe an inventory, not passed C# tests or independently approved designs. StructProof's README binds an older Sourcebook revision; its evidence cannot automatically be transferred to the latest source revision. The exact snapshots and route counts are in the [corpus summary](corpus-summary.json). The source distinctions are documented in the [Sourcebook flexural-design contract](https://github.com/Pravin-surawase/structural-engineering-design-examples-sourcebook/blob/0b8ffeefa93a5772e0a9e15a532cdef534e0686b/docs/beam_fdesign_blind_proof_contract.md) and [StructProof README](https://github.com/Pravin-surawase/structproof/blob/280829fc4d8fc5186235c97042e029c3a83df7f6/README.md); both require repository access.

The strongest recurring cause is a mismatch between a component's bounded result and the product claim made around it. A required area is useful; it is not a checked bar layout. A flexural section pass does not establish shear, serviceability or anchorage. A source comparison does not establish installed Excel behavior. The current library pipeline also exposes structural defaults and optional serviceability/detailing checks. Those are observed contract risks for migration, not a claim that every existing caller currently produces an unsafe result. See the [inspected pipeline](https://github.com/Pravin-surawase/structural_engineering_lib/blob/7e2d620eb6e1dd7286192dd0de3b6976d7f87260/Python/structural_lib/services/beam_pipeline.py).

## The first professional user journey

The first sellable or professionally usable member workflow should complete the following sequence. The initial section milestone is a technical prerequisite, not completion of this journey.

1. Create a project/beam and select the supported code, analysis mode and checking profile. Show supported scope immediately.
2. Enter geometry, materials, cover, loads or actions, support information and reinforcement choices through labeled Excel tables with units.
3. Resolve validation errors and review effective assumptions. A blank structural input cannot silently become a convenient number.
4. Calculate required reinforcement or check supplied reinforcement. Keep those modes separate. Preserve the existing bars in check mode.
5. Select a feasible arrangement and recompute effective depths from actual bar centroids. Check strength, serviceability and detailing for the declared member profile.
6. Review the governing combinations/stations, failed or uncovered checks, section sketches and arrangement. A revision invalidates affected prior results.
7. Save, reopen and reproduce the calculation. Export a readable calculation report and, when resolved, the arrangement and schedule.

Two input routes are required for a useful standalone product. **Supplied actions** is the fastest route to a verified kernel: the engineer provides named ULS/SLS actions and their origin. **Loads plus analysis** makes the workbook independently useful for routine beams: begin with one prismatic simply supported span, full-span UDL and point loads, then add cantilevers and continuous spans only with separate analysis evidence. Keep load factors, self-weight inclusion and combination definitions explicit. The first solver must establish equilibrium, support reactions, discontinuities and extrema. A drawing of supports alone cannot define a solver model.

Vendor workflows reinforce the separation between analysis, design/check and reanalysis after relevant changes. CSI also locates results/design checks at stations and support offsets. We adopt these workflow lessons without treating vendor software as the authority for Indian design equations. See [CSI design procedure](https://docs.csiamerica.com/help-files/etabs/Getting_Started/Concrete_Frame_Design_Procedure.htm) and [output stations](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Output_Stations.htm).

## Beam coverage and honest completion

| Capability | First ordinary-member product | Later extension |
| --- | --- | --- |
| Geometry and flexure | Prismatic rectangular beam; supplied or derived actions; supported singly reinforced branches | Compression steel, T/L sections and their applicability branches |
| Shear | Concrete/shear limits, selected vertical links, spacing and station coverage | Other link systems and special shear cases |
| Torsion and axial force | Explicitly unsupported when outside the selected profile | Combined torsion/flexure/shear and eligible axial actions |
| Serviceability | Named screening/crack-control route, correct service actions and stated coverage | Calculated short/long-term deflection and crack-width routes |
| Detailing | Actual bars/layers, clear spacing, links, cover, anchorage/laps and resolved bar marks | More complex curtailment/redistribution and continuity cases |
| Analysis | Supplied actions plus a verified bounded single-span solver | Cantilever and continuous-member analysis, settlements and wider load forms |
| Seismic and special beams | Excluded visibly from the ordinary profile | Separate seismic system/joint context; deep and other special beam profiles |

“First-member” in the register is a release acceptance requirement, not a claim that it is already implemented. An ordinary profile cannot claim overall member compliance while omitting a check that is required for that scope. It may issue a narrower **section result** or a **draft partial report** with accurate labels. The required checks belong to the versioned workflow profile; a caller cannot remove shear/SLS from a list and thereby redefine complete member design.

For a member, preserve concurrent moment, shear, torsion and axial actions by case, combination and station. Do not combine independent maxima into a fictitious concurrent vector. Stations must cover discontinuities and action extrema as well as support faces; three stations are not a universal member envelope. Rebar centroids must agree with the effective depths used by strength and SLS checks. Cover convention, link diameter, aggregate-related spacing and multiple layers belong to geometry, not presentation. [CSI stations](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Output_Stations.htm) and [Oasys section definition](https://docs.oasys-software.com/structural/adsec/tutorials/section-definition/) support these product requirements.

Serviceability needs a named route. A span/depth screening result must not be described as calculated deflection. Calculated long-term response needs its own cracking, stiffness, creep, shrinkage and sustained-load assumptions. A missing SLS input yields uncovered scope. IIT Kharagpur's [deflection lesson](https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m7l17.pdf) is useful teaching evidence for this distinction; it is not the source for current amendment status.

## Public signatures and input discipline

Use named immutable request/result types, explicit quantities, and pure synchronous kernel calls. Avoid a long list of positional doubles and booleans. Reserve asynchronous cancellation for application work or genuinely long jobs; do not put Excel ranges, COM objects, file paths or HTTP requests into the engineering core. Microsoft documents the importance of parameter design and the compatibility impact of public API changes: [parameter guidance](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/parameter-design), [compatibility rules](https://learn.microsoft.com/en-us/dotnet/core/compatibility/library-change-rules).

```csharp
ValidationReport ValidateSection(SectionRequest request);
SectionResult DesignSection(SectionDesignRequest request);
SectionResult CheckSection(SectionCheckRequest request);
AnalysisResult AnalyzeMember(MemberAnalysisRequest request);
MemberResult DesignMember(MemberDesignRequest request);
MemberResult CheckMember(MemberCheckRequest request);
DetailResult DetailMember(MemberDetailRequest request);
Task<ReportArtifact> CreateReportAsync(
    ReportRequest request, CancellationToken cancellationToken);
```

These are proposed public signatures, not compiled declarations. `SectionDesignRequest` and `SectionCheckRequest` are discriminated views of `section-request.schema.json`, selected by `operation`; a C# consumer must enforce the same branches. OP01 validates those requests without providing an engineering verdict. All eight signatures link to EX01–EX08 in the catalogue. The five scenario-only DTOs must receive their own schemas before implementation; the generic word “request” is not permission to hide an undocumented dictionary.

Each public operation must document purpose, prerequisites, supported geometry/actions, units and signs, required and conditional fields, default policy, returned quantities, errors/unsupported outcomes, provenance, a worked success path and a relevant failure/unsupported path. XML documentation can carry parameter, return, exception and example information. [Microsoft documentation tags](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/recommended-tags).

| Input class | Example | Rule |
| --- | --- | --- |
| Required engineering | Section dimensions, material strength, action basis, ruleset | Missing, null or invalid input is rejected with a field path. |
| Conditional engineering | Supplied steel in check mode; support geometry for anchorage | Required by the selected operation/profile. Never guessed. |
| Profile-resolved engineering | Bar catalogue or a supported modeling option | A named versioned profile supplies the value before calculation; effective input records it. |
| Cosmetic optional | Display label or decimal places | May have a presentation default; cannot change a calculation or its engineering identity. |

Zero torsion is a known input; missing torsion is unknown unless the selected profile explicitly defines it. Null is not a request to choose a structural default. JSON Schema `default` is an annotation and does not populate inputs. JSON object properties are not required unless explicitly listed, and unknown-field handling must be chosen. The three draft schemas therefore use explicit required lists and `additionalProperties: false`. [Schema defaults](https://json-schema.org/understanding-json-schema/reference/annotations), [object constraints](https://json-schema.org/understanding-json-schema/reference/object).

## Concrete schema example and its limits

The first wire draft covers **rectangular singly reinforced flexure only**. It accepts a supplied effective depth, positive moment magnitude with an explicit tension face, and factored ULS actions. Axial force and torsion must be zero. It does not calculate shear, infer bar positions or establish member safety. Nonzero actions outside that scope need a different supported profile; a schema rejection should become a meaningful unsupported/input message in Excel.

EX01 describes a 300 × 500 mm section, d = 450 mm, M25/Fe415, supplied steel of 1256.6370614359173 mm² and 130 kNm ULS moment. It links to Sourcebook BEAM-RFLEX-001. This packet does not reproduce protected standard prose or claim a new numerical run. The example's all-zero data digest and illustrative ruleset are intentionally unresolved and **must fail execution admission**. The response fixture is `not_run`/`not_evaluated`; no capacity or required-steel number is fabricated.

The validator separates JSON shape, semantic geometry and source-identity resolution. Shape validation cannot prove `effective_depth_mm < overall_depth_mm`, source resolution, code applicability, numerical results or cross-field result identity. The supplied validator checks the narrow geometry relation, wire-result operation consistency, and source-ID/digest matching against an explicit registry. It tests matching, mismatched and missing synthetic registry entries without calculating engineering results. The illustration payloads remain unresolved. Source matching alone never establishes execution readiness: production validation must add grade/range applicability, complete profile-check membership, resolved source content and engineering invariants before enabling the operation. Rejected requests can carry their submitted-input digest without pretending an invalid request is a valid effective input.

Run the focused contract audit from the repository root:

```bash
./scripts/python_runtime.sh \
  docs/planning/xll-product/requirements-first/validate_contract.py
```

That audit checks schemas, positive/negative fixtures, links between requirement/source/operation/example IDs, and documented semantic constraints. It does not call an engineering implementation, execute reference cases, load Excel or qualify an XLL.

## Results, evidence and compatibility

Keep four independent dimensions: **execution** (completed, rejected, not run), **engineering** (pass, fail, unsupported, not evaluated), **completeness** (complete for declared scope or partial), and **freshness** (current, stale or unbound). A completed call can return a failed check. A flexure-only pass remains a flexure-only pass. A stale result can remain visible for comparison but cannot support a current issued package.

Calculation identity should bind normalized effective engineering input, ruleset/data content digest and engine version. Record source/clause/table/case references and applied branches per check. Maintain a separate report identity including calculation identity, template and export settings. Changing a report title should not force different structural mathematics; changing material strength must invalidate the old calculation. StructProof's [source-identity issue](https://github.com/Pravin-surawase/structproof/issues/86) records a concrete reason to bind source content, and its [evidence-state issue](https://github.com/Pravin-surawase/structproof/issues/88) distinguishes accepted and internal evidence.

Use binary64 numerical computation with finite-input validation. Preserve unrounded values for code decisions and give each comparison metric an absolute/relative tolerance tied to its scale and source. Do not use one universal tolerance to blur pass/fail boundaries. Display rounding is a separate presentation step. Expected numbers need source, assumptions and evidence classification; cross-project parity can be correlated evidence, not independent corroboration.

The draft schema version is `0.1.0-draft`. Freeze 1.0 only after C# and Excel consumers, examples and supported branches agree. Maintain separate contract, engineering ruleset, implementation and workbook/report-template versions. Strict schemas mean a newly added field can break an old consumer; do not promise that every additive minor change is automatically compatible. Supply explicit migrations and retain old fixtures. A future HTTP API may project the same contracts using [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html); an HTTP server is unnecessary for the first local XLL.

## Failures to prevent, with evidence boundaries

The failure register records 20 families with source IDs, state, cause, prevention requirements and acceptance evidence. Historical repairs are not reported as current defects. Current gaps are distinguished from inferred future risks. The main outcome-changing groups are:

- **Incomplete checks and stale results:** historical library repairs connected status, result identity and export eligibility. Enforce profile completeness and current input binding at the result/report boundary. See [August session history](https://github.com/Pravin-surawase/structural_engineering_lib/blob/7e2d620eb6e1dd7286192dd0de3b6976d7f87260/docs/_archive/session-logs/2026-08.md).
- **Duplicated contracts and quantity ownership:** API envelopes, UI fields and generated manifests drifted. Use one contract producer and validate the maintained consumers. See [April session history](https://github.com/Pravin-surawase/structural_engineering_lib/blob/7e2d620eb6e1dd7286192dd0de3b6976d7f87260/docs/_archive/session-logs/2026-04.md).
- **Formula and applicability corrections:** Sourcebook recorded corrections involving compression-steel interpolation, deflection assumptions, flange/lap eligibility, torsion capping and deep-beam steel distribution. Reconcile corrected sources before translation. The [correction record](https://github.com/Pravin-surawase/structural-engineering-design-examples-sourcebook/blob/0b8ffeefa93a5772e0a9e15a532cdef534e0686b/docs/sourcebook_phase2a_to_phase2f_assurance_corrections_20260827.md) is private; this packet contains authored summaries only.
- **Area-only results overstated as detailing:** preserve the source route's boundary and add actual fit, centroid and anchorage checks before member detail issuance. The [flexural-design contract](https://github.com/Pravin-surawase/structural-engineering-design-examples-sourcebook/blob/0b8ffeefa93a5772e0a9e15a532cdef534e0686b/docs/beam_fdesign_blind_proof_contract.md) explicitly limits its scope.
- **Repeated process work:** preserve candidate/runtime identity and run targeted evidence for bounded changes, then the named cumulative gate. Do not use successful process completion as a substitute for a delivered workflow. [StructProof cadence decision](https://github.com/Pravin-surawase/structproof/issues/94).

For future incidents, record one material failure family with the symptom, confirmed cause (or unconfirmed), fixing candidate and outcome evidence. Repeated automation alerts should link to that family. This audit does not infer CI root causes from failure titles alone. Keep controls only when they prevent an outcome-changing recurrence; do not build another large governance system around cosmetic observations.

## C# architecture and performance decision

Recommend **C#/.NET 10 LTS** for the new core, with a thin **Excel-DNA 1.9** adapter targeting Windows Excel. Official documentation supports .NET 10 in Excel-DNA, and Microsoft's current support table lists .NET 10 through 14 November 2028, while .NET 8 ends on 10 November 2026. This recommendation is dated and should be rechecked at implementation. [Excel-DNA release notes](https://excel-dna.net/docs/release-notes-1-9/), [.NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core).

An early installed spike must check deployment constraints. Modern .NET needs the matching Desktop Runtime and Excel bitness. Excel-DNA documents that a single modern .NET runtime is loaded per Excel process, which can affect other add-ins; .NET Framework 4.8 remains a compatibility option if required installed combinations fail. Do not retarget the existing net48 learning exercise silently. [Excel-DNA runtime support](https://excel-dna.net/docs/guides-basic/dotnet-runtime-support/).

The core owns quantities, materials, geometry, pure code calculations, validation and result/provenance types. Application services own member workflows, persistence, batch progress and report production. Excel-DNA owns range conversion, worksheet registration and user commands. ETABS later owns a separate adapter with model/results identity; it does not enter worksheet recalculation. Future slab, column and footing products reuse these foundations while retaining their own domain models.

Only truly pure/reentrant UDFs should be registered as thread-safe. Excel/COM access and file/report effects belong to commands with appropriate host-thread handling. Microsoft documents these restrictions and Excel's multithreaded calculation behavior. [Excel recalculation](https://learn.microsoft.com/en-us/office/client-developer/excel/multithreaded-recalculation-in-excel).

C# is a plausible fit for typed contracts, Windows integration and efficient scalar/batch calculations, but no speedup is established by this research. Profile kernel computation, marshaling, workbook recalculation and report generation separately. Use deterministic inputs and report cold/warm median/p95 times, allocations, machine/runtime/Excel versions and batch size. Proposed initial targets are warm section p95 below 50 ms and 1000 simple section calculations below 1 second in the kernel; these are product targets to calibrate, not measured results or release claims. Measure Excel end-to-end separately, and prove cancellation/responsiveness for long workflows. ETABS solver speed does not improve merely because an adapter changes language.

## Delivery sequence that closes work

| Packet | Concrete exit outcome | Evidence required |
| --- | --- | --- |
| A — runtime and contract proof | Exact XLL loads; one schema-bound section request becomes a traceable result in Excel | Runtime/coexistence evidence, contract fixtures, corrected-source numerical comparisons, installed workbook observation |
| B — useful standalone beam | Loads or supplied actions lead to an ordinary member result and readable report | Solver reference cases, required-check profile, final bar-depth consistency, save/reopen and stale-result checks |
| C — buildable arrangement | Actual bars/links, anchorage and schedule agree with the checked member | Geometry/fit/detailing references, complete marks/lengths, drawing/report identity, issued-package gate |
| D — coverage expansion | Each new family has explicit inputs, contracts and supported/unsupported cases | Reconciled doubly/flanged/torsion/SLS/seismic/special-beam evidence as applicable |
| E — ETABS integration | Current model results map into the same member contract | Versioned API adapter, units/axes/stations/cases, result freshness and installed tests |

These packet letters describe a proposed delivery sequence and are not replacements for the existing phase numbers. Keep one active bounded implementation packet. Every public operation must arrive with its example, documentation, validation and visible user output; do not accumulate disconnected functions and call that progress. One integrated candidate should carry the intended changes and affected evidence; repeat broader validation only at its required cumulative gate or to resolve an outcome-changing failure.

Before moving from this research into implementation, settle the remaining product choices in the first implementation packet: supported Excel versions/bitness, the initial bar catalogue and cover convention, exactly which serviceability/crack route constitutes the ordinary profile, and the supported first solver loads/restraints. Use the recommendations above as draft defaults. These choices do not prevent the requirements and contract work delivered here.

## Research limitations and remaining evidence

The source hierarchy is repository implementation/contract history for project behavior, source/amendment records for code reconciliation, and primary vendor/specification documents for platform/interface behavior. Two bounded research agents covered engineering workflow and failure evidence; the parent reconciled their results and independently inspected high-impact source records. Searches stopped after the material slots were supported or explicitly bounded; additional broad competitor searching would not settle the remaining implementation/installed questions.

The private projects were inspected locally but their raw repositories, source catalogs, protected documents and issue bodies are not copied into this public packet. Private links require the reader's access. The repository's standing permission for approved normalized IS content remains passed and is not reopened. This packet does not reproduce protected standard prose or figures. A public BIS page did not yield readable status text in this run; this report therefore does not claim a newly verified reaffirmation date or complete current seismic amendment inventory.

No current C# numerical benchmark, installed XLL observation, clean-machine installer proof or full member engineering qualification was produced by this task. Those are the concrete next-stage evidence requirements, not reasons to repeat this research. The complete requirement, failure, operation and example registers are supplied so implementation can proceed from a stable, reviewable baseline.
