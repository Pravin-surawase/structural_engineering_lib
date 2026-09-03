---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: spec
complexity: advanced
tags: [beams, excel, csharp, etabs, automation]
---

# Beam automation: product requirements and C# foundation

**Product direction, 3 September 2026:** standalone beam design in Windows Excel is the first user workflow. The complete automation workflow is ETABS forces → Excel add-in design and checks → candidate search and reanalysis → reinforcement, BBS, quantities and reports. Both entry routes use the same engineering core, member model and result contracts.

The foundation is implemented in [CSharp](../../../../CSharp/README.md). It builds a packed x64 Excel-DNA add-in and provides five working APIs: force normalization, reinforcement geometry, bar-path quantities, planar beam analysis and candidate ranking. This document completes the requirements for the wider product; full IS-code member design, live ETABS acquisition, model updates and the finished workbook are subsequent implementations. A compiled XLL is build evidence; installed Excel and ETABS behavior is established by application tests.

## 1. What the engineer must be able to do

An engineer starts with a project, design basis and beam geometry. They may enter loads for a standalone beam or import a selected ETABS model's force results. The workbook checks input completeness, explains the governing cases, selects actual reinforcement, verifies the member, and produces an understandable calculation report and construction schedule. Changing a section, load, material, bar arrangement or code profile updates the affected results and their identities.

The workflow has eight connected stages:

1. Define project rules, material/bar catalogues, exposure, fire requirements, units and required checks.
2. Define physical members, spans, supports, sections, local axes and reinforcement regions.
3. Acquire service/ultimate actions from standalone analysis, manual input or an ETABS snapshot.
4. Evaluate strength, serviceability and applicability at all required stations and physical faces.
5. Resolve bars, layers, links, anchorage, laps, cutoffs and construction fit, then recalculate dependent checks.
6. Produce BBS, cutting schedules, concrete/formwork quantities and itemized costs from those actual details.
7. Search alternatives, reanalyse when the analysis model changes, and compare complete feasible results.
8. Save and export a current, reproducible workbook, calculation report and construction package.

## 2. Requirements, signatures and schemas

The [requirements register](requirements.json) contains 26 requirement groups; [CSV](requirements.csv) supports filtering. Each maps to an [operation](operations.json), an [example](examples.json), measurable acceptance conditions and [sources](source-crosswalk.json). The catalogue contains five implemented foundation APIs and 21 engineering/application operations to implement. Every operation specifies its request/result names, signature, inputs, units, required/default/conditional behavior, result meaning and examples.

The five [foundation schemas](../../../../CSharp/schemas) are generated from the compiled C# DTOs. The [member input schema](member-inputs.schema.json) defines 38 shared/member/check types, including the complete input envelopes for the nine leaf checks. It separates physical geometry, material properties, action identities, actual reinforcement, serviceability, anchorage, splices and seismic context. The remaining orchestration operations use the catalogue's composition contracts; their full transport payloads are completed with their adapters and workflow implementation.

Version `1.0.0` applies to the current contracts. Required values are explicit. Optional values have a documented meaning: for example, omitted quantity rates mean no cost, and a free beam support DOF is null while zero means restrained at zero. A blank Excel cell is not a numeric zero. Profile-derived engineering values are returned with their method and source; hidden code defaults cannot silently supply a missing design decision. Additive optional fields require a compatible version policy; changed meaning, units, required fields or enum semantics require a new contract version and migration examples.

The larger member-check response separates execution, evaluated/remaining checks and freshness. Each check retains demand, capacity, unit, utilization where meaningful, governing action row, rules, effective input digest and explanation. Foundation math helpers return their narrower typed results; they do not claim a whole-member engineering pass. Required checks cannot be satisfied by omitted, not-evaluated or not-applicable outcomes.

## 3. Inputs that must survive every layer

| Input group | Required detail | Why it changes the result |
| --- | --- | --- |
| Project and rules | Code edition/amendments/dataset digest, ordinary or seismic profile, exposure/fire, catalogue versions | Fixes the numerical and detailing basis |
| Member topology | Physical member/span/node IDs, support centres/faces/widths, offsets, releases, sections and local axes | Establishes where analysis and construction quantities apply |
| Lengths | Centreline, clear, effective design, flexible analysis and physical quantity lengths; bar cut lengths separately | One ambiguous span cannot serve design, analysis and fabrication |
| Materials | Concrete/steel grades, E and its method, density, bar type/bond, maximum aggregate and ductility | Controls stiffness, capacity, development and placement |
| Actions | All six signed components, station, case/combination, step, factor state and self-weight inclusion | Preserves interaction, direction and service/ultimate meaning |
| Reinforcement | Every bar's group/face/layer/diameter/centre/path; link diameter/legs/spacing/zones/hooks | Actual depth, capacity, congestion and quantities depend on provision |
| Serviceability | Total/sustained/transient selections, stiffness/cracking method, age, humidity, duration, shrinkage and finishes | Calculated deflection/cracking cannot be inferred from ULS design |
| Construction | Stock lengths, splice/coupler rules, bend convention, physical faces/deductions, dated unit rates | Produces fabricable bars and reconcilable quantities/cost |

Topology must include stations at support faces, point-load discontinuities, section and reinforcement changes, relevant extrema and user-required positions. The internal solver's automatic stations currently include element ends and zero-shear positions; richer member station generation is a separate workflow operation.

## 4. Engineering coverage

**Flexure:** both bending signs and physical tension faces; singly and doubly reinforced rectangular sections; eligible T/L sections with their compression-flange assumptions; actual d and compression-steel depth; minimum/maximum steel and strain/neutral-axis regimes. Retained axial and minor-axis actions require an applicable interaction method. They cannot simply disappear when a major-axis flexure function is called. Special deep, curved, prestressed, hollow or other beam systems have explicit applicability rules and their own methods.

**Shear and torsion:** evaluate the relevant local shear axes, concrete and steel contributions, maximum stress, minimum links, spacing and support-adjacent behavior. Near-support enhancement requires the covered concentrated-load context; a UDL does not inherit it. Combined torsion uses concurrent T/V/M, with transverse steel and longitudinal corner/side/perimeter provision. Closed links, corner distribution and anchorage matter as much as total steel area. Any compatibility-torsion redistribution needs its own structural basis. These distinctions follow the existing [shear](../../../../Python/structural_lib/codes/is456/beam/shear.py) and [torsion](../../../../Python/structural_lib/codes/is456/beam/torsion.py) owners and identify what their migration must extend.

**Serviceability:** span/depth screening remains identifiable as screening. Calculated short-term deflection uses the selected service actions, stiffness and cracking assumptions. Long-term and incremental-after-finishes checks preserve sustained share, loading/assessment ages, duration, humidity, notional size, creep/shrinkage method and finish installation date. Crack width uses actual cover, spacing, steel stress/strain, tension-region assumptions and a stated exposure limit. Equal total steel area can produce different serviceability results. Reuse the existing [serviceability branches](../../../../Python/structural_lib/codes/is456/beam/serviceability.py) and compare each with independent examples.

**Detailing and construction:** check all reinforcement groups together, with different horizontal and vertical clear-spacing rules, link enclosure including bend corners, side-face bars, aggregate passage and joint congestion. Development and anchorage use actual bar stress, bond conditions, support faces and available straight/bend/hook contributions. Laps preserve stress state, percentage spliced, staggering, zone restrictions and coupler qualification. Curtailment follows the demand envelope plus extension, shear and development requirements. Seismic design adds system/joint context, capacity-design shear, continuity, confinement, hooks and splice restrictions; the existing geometry-only seismic checks are only one part of that work.

Construction outputs include section/elevation views, layer dimensions, bar marks, shape dimensions, start/end stations, counts, resolved cut lengths, stock allocation and offcuts. Formwork lists soffit, exposed sides, end bulkheads, interfaces and deductions. Concrete net segments record slab/support overlap policy. Steel includes longitudinal bars, links, side/torsion bars, hooks, anchorage and laps. The quantity helper uses tangent straight lengths plus centreline bend arcs; it does not invent code-derived anchorage or convert arbitrary shape dimensions. [NPTEL construction material](https://archive.nptel.ac.in/content/storage2/courses/105103093/pdf/concrete_uc.pdf) supports the attention to placement and BBS; project-selected measurement conventions remain explicit.

## 5. ETABS and solver automation

The ETABS adapter acquires model/session/version identity, model/result state, units, selections, sections/materials, stiffness modifiers, offsets, releases, axes, object/element mappings and force rows. Every API call checks its return code and result-array dimensions. Every normalized row retains P, V2, V3, T, M2 and M3 together, along with object and element station, output case, step and source row. CSI's [FrameForce contract](https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm) documents these fields; it is historical documentation and is verified against the installed API when connecting the product.

The C# normalizer performs the explicit unit conversion and preserves the supplied orthonormal, right-handed axes. The acquisition adapter still owns live source verification and mapping those axes to physical beam faces. A governing check cites the concurrent row that produced it. Separate component maxima are useful envelope summaries, but cannot be assembled into a fictional simultaneous interaction vector.

Two solver meanings remain clear. The implemented **beam-line solver** analyses planar linear prismatic bending with UDL, nodal actions, springs and settlements. **Candidate search** evaluates discrete section/material/reinforcement choices, applies all hard checks and ranks feasible alternatives. It is not Excel Solver repeatedly guessing unconstrained cells. The current ranking API accepts already evaluated candidates; generation and full engineering evaluation are subsequent operations.

Fixed-action comparisons retain one declared force snapshot. Coupled alternatives that change stiffness, geometry, release/offset assumptions, self weight or applied loads update an identified ETABS model copy, run analysis and import new results before final comparison. CSI states that [unlocking a model deletes analysis results](https://docs.csiamerica.com/help-files/etabs/Menus/Analyze/Lock_Model.htm). A saved candidate cannot keep its old forces after changing the model that generated them.

## 6. Excel product and performance

The workbook provides stable tables for Project, Members, Sections, Materials, Actions, Reinforcement, Checks, BBS and Quantities, plus a readable report. Selected member/station/case and governing checks are easy to navigate. A ribbon or panel owns ETABS import, design/check, optimize, refresh and export commands. UDFs calculate from supplied values. Bulk table reads/writes avoid per-cell COM traffic; worksheet recalculation never edits an ETABS model or writes files. Microsoft documents the distinction between [multithreaded worksheet calculation and thread-safe functions](https://learn.microsoft.com/en-us/office/client-developer/excel/multithreaded-recalculation-in-excel).

Invalid rows report exact field/cell/member identifiers. Manual calculation, save/reopen, changed inputs, missing add-in and missing source revisions must make result freshness visible. Export uses the same current member/detail/quantity identity. Reports include the design basis, inputs, normalized substitutions, rule references, governing cases, required/provided values, utilization, reinforcement drawings and BBS/quantities. Prepared/checked/approved fields represent real recorded people and actions.

.NET 10 LTS is the new foundation baseline, with Excel-DNA 1.9.0 and managed Math.NET Numerics. This avoids adopting .NET 8 near its published support end; review the [.NET lifecycle](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core) at release. Excel-DNA documents [runtime and bitness constraints](https://excel-dna.net/docs/guides-basic/dotnet-runtime-support/). Host coexistence and the target CSI API are validated with the actual applications. Isolating adapters allows a compatibility bridge if an installed CSI runtime requires it.

Performance is measured, not inferred from the language name. The included CLI records cold time, warm median/p95 and allocations for a reproducible beam solve; that measurement excludes Excel/ETABS. Product tests add scalar and 1000-beam batches, force-table import, report creation and cancellable candidate search. Initial interaction targets are typical recalculation under one second and progress/cancellation within 250 ms on a named reference machine. These are acceptance targets, not measured claims about the finished workbook.

## 7. Reuse the old projects without repeating their mistakes

The Python library is a substantial reference: code math, criteria, identity, beam analysis, supplied reinforcement, candidate search and BBS already exist. The [source crosswalk](source-crosswalk.json) identifies exact owners. Port the mathematics by method and independent example; carry over valuable identity and traceability behavior. Extend limitations at their cause: one-layer/full-span schedules become actual multi-layer paths, torsion gets perimeter provision, and required-Ast cost estimates become actual-bar quantities.

StructProof contributes explicit example expectations and traceability. Sourcebook contributes the source/example inventory: the inspected snapshot has 180 records, of which 154 are numerical and 26 are other records. They are useful evidence, but counts are not passing C# tests. StructProof pins an older sourcebook revision, so each imported case reconciles source version, units, applicability, expected outputs and tolerances. Private source records are not copied into this public repository.

The earlier [20-pattern failure register](../requirements-first/failure-register.json) remains the detailed source-backed audit of historical repairs, observed risks and inferred prevention needs. This foundation addresses the repeated mechanisms directly:

| Repeated mechanism | New control |
| --- | --- |
| Public signatures drift from implementations | Compiled DTO schemas, exact method links and example fixtures |
| Hidden inputs/defaults alter the design | Required fields, conditional schemas, explicit zero/blank behavior and effective-input identity |
| Missing checks become a pass | Required-check completeness before candidate feasibility |
| Changed actions/geometry retain old results | Source/model/analysis identities and coupled reanalysis contract |
| Steel area is mistaken for constructible detail | Actual group centroids, bar paths and full-arrangement check requirements |
| Quantities/cost omit links, laps or interfaces | Itemized actual bars, net segments, explicit formwork faces and dated rates |
| Existing outputs verify themselves | Closed-form analysis oracles and independently sourced engineering examples |
| Plans multiply without working software | Buildable solution, packed XLL, locked dependencies, tests and required hosted verification |

## 8. Delivery sequence

The next engineering increment migrates ordinary-beam flexure, shear and combined torsion with actual reinforcement and complete results. It carries forward the Python golden vectors, adds independent source examples for branch boundaries, and implements the member applicability/aggregation contract. Serviceability and full detailing follow through the same schemas, including multi-layer fit, development, laps, curtailment and seismic context where selected.

The ETABS read adapter and workbook then connect those operations to real selected models and a complete standalone Excel example. Candidate generation and the evaluation loop use the same member checks and actual quantity model; coupled reanalysis runs on identified model copies. The final workflow increment delivers reports/BBS/quantities, installation/signing, save/reopen and representative performance tests. Release authorization follows the existing per-release repository process.

This sequence retains the original XLL P0–P6 meanings and the separate library beam programme. The latest user instruction authorizes this foundation work; the earlier shell-only teaching packet is historical context, not the limit of the current task. Normalized IS-data distribution permission is already recorded and is not reopened.

Run `bash scripts/python_runtime.sh docs/planning/xll-product/automation/validate_spec.py` from the repository root to verify links, schema definitions and foundation fixtures. Build/test commands and the exact XLL path are in [CSharp/README.md](../../../../CSharp/README.md).
