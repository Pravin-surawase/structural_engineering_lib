---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: reference
complexity: advanced
---

# Reusable structural engineering in Python and .NET

For the product owner and library implementation team • 3 September 2026

## Recommended direction

Build one engineering specification with native Python and native .NET implementations for a deliberately maintained common capability set. Keep Excel, ETABS, file export and project approval outside the calculation packages. Preserve reusable member-design services: a library should be able to design a beam, resolve reinforcement, produce BBS data and optimize a declared objective without a workbook or running ETABS instance.

The qualification to our earlier discussion matters: two native implementations do not mean half the work. They require two implementations and two sets of language-specific maintenance. Shared contracts, normalized code data, examples and conformance checks reduce drift; they do not eliminate it. The existing Python library makes this approach practical, but every old function does not deserve an automatic C# copy.

The migration should improve the public engineering model first. A language change alone would preserve misleading defaults, incomplete quantities and application coupling. The research below defines the proposed boundary; it does not claim that these new interfaces or full Python/.NET parity have already been implemented.

## What belongs in a normal library

A reusable function does not depend on the caller being Excel, a web app or an ETABS session. It can still perform a substantial engineering workflow. The useful separation is by responsibility and dependency.

| Responsibility | Reusable examples | Inputs that belong elsewhere |
|---|---|---|
| Numerical and geometric calculations | Bar area/mass, section centroid, spacing geometry, coordinate transformations, bounded beam analysis | Workbook path, reviewer, ETABS version, report template |
| Design-code calculations | Flexure, shear, torsion, serviceability, development, laps, seismic detailing | UI status, database session, COM objects, cell addresses |
| Member-design services | Design/check a beam, choose bars, evaluate all stations, resolve paths, build BBS data, rank feasible candidates | A requirement to launch Excel or ETABS |
| Application adapters | Acquire ETABS results, read Excel ranges, persist projects, render reports, export DXF | Independent copies of engineering formulas |

An ordinary script should be able to call a small bar-area function, one flexure check, a whole-member check, or an optimization. A small scalar calculation may return a scalar. A multi-output calculation should return a named result. A design check should return its engineering outcome and basis. Requiring a large project envelope or source hash for every arithmetic call would be another usability mistake.

Keep these meanings separate: section capacity, check against supplied demand, required reinforcement, selected reinforcement, whole-member completeness, and engineering approval. A section capacity is useful on its own; it is not an approved beam design.

## Where the existing 26 operations belong

This maps the current [automation catalogue](automation/operations.json), including operations whose implementation is still to follow. “Service” here means a callable library service; it does not require a server.

| Operation IDs | Engineering responsibility | Proposed owner |
|---|---|---|
| AO01 | Normalize units/axes and preserve source evidence | General normalization service; ETABS extraction in its adapter |
| AO02 | Solve a declared beam-line model | Optional analysis module |
| AO03 | Compute actual bar area, centroid and gaps | Geometry module; code limits supplied explicitly |
| AO04 | Quantities from resolved paths/contact geometry | Quantities module; apply prices separately |
| AO05 | Rank evaluated feasible candidates | Reusable search service with explicit objective |
| AO06–AO08 | Flexure, shear and torsion checks | IS 456 code module |
| AO09–AO10 | Deflection and crack-width checks | Code/serviceability module with correct action basis |
| AO11–AO13 | Anchorage, laps/curtailment, seismic detailing | Code rules composed by member services |
| AO14–AO15 | Create a beam project and define topology | Reusable domain construction; persistence/UI outside |
| AO16 | Acquire an ETABS snapshot | ETABS adapter |
| AO17 | Design a complete member | Member-design service |
| AO18–AO19 | Resolve bar paths and create BBS data | Fabrication/member service; file rendering outside |
| AO20 | Apply a priced construction scope | Pricing service over quantity data |
| AO21 | Generate, evaluate and select beam candidates | Optimization service with declared constraints |
| AO22 | Apply a candidate to an ETABS copy | Explicit ETABS application command |
| AO23 | Map/recalculate a workbook | Excel adapter/application command |
| AO24 | Prepare calculation data and render a report | Reusable calculation record plus format-specific renderer |
| AO25 | Measure workbook performance | Excel integration benchmark, separate from kernel benchmark |
| AO26 | Check full reinforcement arrangement | Geometry checks plus design-code constraints |

BBS and construction must not disappear from the library just because they are used by an application. Bar placement, cut lengths, quantities and schedule records are reusable engineering outputs. Sheet formatting, drawing layers and PDF layout are presentation choices. Formwork contact-area measurement is also distinct from structural design of temporary formwork and shoring.

## Patterns from other libraries

Five structural libraries were examined through their maintainers' documentation/source. They provide useful architecture examples; none of the reviewed material establishes our complete IS-code beam, fabrication and Excel/ETABS workflow.

**StructuralCodes (fib).** Its section calculator separates geometry, integration and calculation. `calculate_bending_strength(theta=0, n=0, ...)` returns an `UltimateBendingMomentResults` object; moment-curvature calculation has its own result type. Borrow typed results, explicit calculation methods and replaceable numerical strategies. Its documented sign convention must be mapped explicitly to ours. [StructuralCodes section calculator](https://fib-international.github.io/structuralcodes/api/sections/section_calculator.html)

**sectionproperties.** It distinguishes geometric, warping, plastic and stress analysis. `calculate_frame_properties()` exposes a compact frame-analysis projection; material weighting changes the meaning of some returned properties. Borrow the separation of section properties from frame analysis. In our shared interface, use named properties with dimensional meaning and prerequisites, rather than an unexplained tuple or reliance on a previous mutation of the same object. [sectionproperties analysis guide](https://sectionproperties.readthedocs.io/en/stable/user_guide/analysis.html)

**concreteproperties.** Its `ConcreteSection.ultimate_bending_capacity(theta=0, n=0)` returns `UltimateBendingResults`; cracked properties and moment-curvature are distinct operations. Borrow the distinction between response/capacity and downstream processing. A numerical capacity result still needs a separate design-code check and member-completeness decision in our product. Do not substitute a prestressed-section signature for the ordinary reinforced-concrete class. [ConcreteSection reference](https://concrete-properties.readthedocs.io/en/stable/gen/concreteproperties.concrete_section.ConcreteSection.html)

**PyNite.** Its model API defines materials, nodes, members, loads and named combinations before analysis. The quickstart then reads reactions by combination. Borrow the explicit analysis model and scenario identity. Its mutable model/results workflow is useful interactively; our transport snapshots should be immutable and self-contained so Excel recalculation and cross-language replay do not depend on hidden call order. [PyNite quickstart](https://pynite.readthedocs.io/en/stable/quickstart.html)

**BHoM.** Its adapter interface separates batched `Push` and request-based `Pull`; `IAdapterId` stores an identifier from external software. Borrow adapter-owned external IDs and batch boundaries. A domain member's identity should survive changing analysis vendor. Avoid copying the broad `object` dispatch into our focused engineering API where concrete types are available. [BHoM adapter interface](https://github.com/BHoM/BHoM_Adapter/blob/develop/Adapter_oM/IBHoMAdapter.cs), [external identity interface](https://github.com/BHoM/BHoM/blob/develop/BHoM/Interface/IAdapterId.cs)

These are architecture references, not a recommendation to install five dependencies or translate their formulas into IS 456. Any later numerical comparison must align geometry, material law, units, signs, code factors and applicability first. Agreement between two packages alone is not an independent engineering proof.

## Corrections and lessons from our own code

The inspected baseline is commit `5300767eda1dd5f98328c7e3c3116891967e75ab`, the merged C# foundation. The findings distinguish current implementation behavior, deliberate limitations and historical repairs.

**1. Vendor-specific fields have entered the new common contract.** `EtabsForceBatch` and `AnalysisSource.EtabsVersion` are in the common C# contracts; the normalizer requires the ETABS version. Its actual unit-conversion work is useful for any analysis source. Introduce vendor-neutral action/provenance records and keep ETABS session details in an adapter envelope. Preserve object/element identities rather than deleting provenance. Python's analysis contract already demonstrates a vendor-neutral dependency boundary. [C# forces](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/CSharp/src/StructAutomate.Contracts/Forces.cs#L9), [Python analysis contracts](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/core/analysis_contracts.py#L1)

**2. A preserved row is not automatically a concurrent action vector.** The C# normalizer preserves components without manufacturing an envelope, which is good. However, the request lacks an explicit classification of the source combination/output semantics. The catalogue's concurrent-force wording therefore promises more than the normalizer establishes. Add the action-basis distinction before using imported rows for interacting checks. [Current AO01 contract](automation/operations.json), [normalizer](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/CSharp/src/StructAutomate.Application/ForceNormalizer.cs#L11)

**3. Cover has meant different physical quantities.** The legacy cost optimizer explicitly retains `cover_mm` as a compatibility name for `D - d`, not clear cover. The documentation acknowledges the meaning, but a straightforward port could still use it incorrectly. New signatures should say `nominal_cover_mm`, `link_diameter_mm`, actual bar positions, or `effective_depth_mm`, according to what they accept. Preserve old-call compatibility through translation. [Optimizer contract](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/optimization.py#L115)

**4. A missing concrete rate can silently become 6700.** `calculate_beam_cost` uses a dictionary fallback, whereas the newer BOQ resolver rejects an incomplete caller-supplied rate table. Use one explicit pricing policy and return missing-rate details. A missing price must not create a plausible objective value that changes candidate ranking. [Legacy costing](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/costing.py#L155), [BOQ rate validation](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/boq.py#L92)

**5. A limited estimator can be mistaken for construction optimization.** The old optimizer documents that its quantity/cost includes required longitudinal reinforcement and excludes stirrup mass. This is a declared limitation, not proof that its calculations are erroneous. The new construction objective must use selected bars, links, bends, laps, waste policy and priced scope; retain an estimator only with its exact cost basis. [Optimizer scope](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/optimization.py#L122)

**6. Zero has doubled as a request for a default.** In the older stirrup-length function, `hook_length_mm=0` selects an implicit hook rule. The schedule also counts each stirrup zone with `int(length / spacing) + 1`. Those conventions need explicit first/last positions, zone-boundary ownership and fabrication rules before generating a complete schedule. This is a representational limitation; the audit does not claim every old schedule is wrong. [Stirrup length](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/bbs.py#L279), [zone counting](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/bbs.py#L721)

**7. A broad re-export surface obscures what users need.** `services/api.py` combines calculations, member workflows, ETABS helpers and output functions, although implementation has already been split into narrower modules. Keep compatibility imports, document focused entry points, and avoid eagerly importing optional application integrations. File length alone is not a defect, and the existing optional dependency groups are a useful strength. [Public facade](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/structural_lib/services/api.py#L1), [package dependencies](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/Python/pyproject.toml#L26)

**8. The two languages do not yet share one normative contract.** The current five C# request schemas are generated from .NET types. Python has separate Pydantic contracts; field vocabulary and required evidence differ. Generating schemas from one language does not establish parity with the other. Define semantic operations and conformance cases first, then generate suitable projections and check handwritten domain logic. [C# schema export](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/CSharp/src/StructAutomate.Contracts/ContractSchemas.cs#L8)

**9. A serialization hash is not a universal calculation identity.** The current force-row hash includes the source acquisition timestamp and .NET JSON serialization. That can identify that acquisition record, but should not become a portable numeric cache key. Keep raw-artifact identity, normalized engineering-input identity and execution receipt separate. If cross-language canonical JSON is adopted, implement an actual canonicalization contract and its test vectors; simply sorting dictionary keys is insufficient. [Current hashing](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/CSharp/src/StructAutomate.Application/ForceNormalizer.cs#L55), [RFC 8785, June 2020](https://www.rfc-editor.org/rfc/rfc8785.html)

Historical repairs remain lessons rather than a list of current bugs. The earlier [failure register](requirements-first/failure-register.json) records partial-check aggregation, stale result identity and consumer-contract mismatches, alongside corrected sourcebook formulas/applicability. Their prevention rules are concrete: required checks cannot disappear from an overall decision; changed effective inputs invalidate results; producer and consumer replay the same contract examples; source corrections must propagate to every implementation and fixture. Duplicate issue titles are not evidence of separate root causes.

Six historical records were checked against their underlying session/correction records:

| Repaired behavior | Cause recorded in the history | Rule for this migration |
|---|---|---|
| Partial secondary checks could affect an overall decision | UI fallback and inconsistent combined status | One required-check aggregation rule |
| Changed torsion/SLS inputs retained old evidence | Identity covered an earlier, smaller input contract | Hash all effective engineering dependencies |
| React read the wrong response shape | API wrapped results while consumers expected direct data | One shared transport example per operation |
| Compression-steel interpolation needed correction | Missing interpolation node/offset in reference owners | Versioned table plus node/interior examples |
| Deflection used an overgeneral coefficient | Support label stood in for load-shape assumptions | Explicit loading/coefficient basis |
| Deep-beam distribution used the wrong steel quantity | Required steel substituted for provided steel | Distinct required, selected and scheduled quantities |

The first three are documented in the [August identity/status repair](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/docs/_archive/session-logs/2026-08.md#L7558) and [April response-envelope repair](https://github.com/Pravin-surawase/structural_engineering_lib/blob/5300767eda1dd5f98328c7e3c3116891967e75ab/docs/_archive/session-logs/2026-04.md#L34). The last three are corrected reference findings F06, F07 and F09 in the linked failure register, verified against the sourcebook's 27 August correction record. They are not asserted to be current Python calculation defects.

Preserve the good work: explicit units, actual bar-coordinate centroids, resolved fabrication path pieces, fixed-analysis candidate ranking, incomplete-search reporting, normalized action provenance and optional reporting dependencies. Migration should build on these strengths.

## ETABS changes the adapter contract, not the engineering API

CSI's ETABS 23.3 release notes explicitly add support for .NET 10 clients using COM. This machine contains ETABS `23.3.1.4563`; reflection of installed `CSiAPIv1.dll` reports version `2.16.0.0` and target `.NET Standard 2.0`. The key extraction/setup methods remain present. This is useful compatibility evidence, not a completed live connection test. [CSI 23.3.0/23.3.1 release notes, API ticket 12108](https://www.csiamerica.com/software/ETABS/23/ReleaseNotesETABSv2331plus2330.pdf)

The public method reference describes `FrameForce` returning arrays for object/element identities, both stations, case, step information and six force components. Convert those arrays to typed rows at the ETABS boundary and check their lengths and return status. Do not expose parallel `ref` arrays to ordinary library users. [CSI FrameForce reference, ETABS 2016](https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm)

An extraction request should identify the process/model, selected cases/combinations, stations and result-output settings. Capture units and local axes, verify relevant case statuses, and preserve the case/combo definition and dependency basis. A model's locked flag alone does not prove the requested results belong to the intended current calculation. Snapshot creation and revision management are adapter/application responsibilities. [CSI case status](https://docs.csiamerica.com/help-files/etabs-api-2016/html/a24b2f43-be87-e0ff-587b-068339d9a350.htm), [result setup](https://docs.csiamerica.com/help-files/etabs-api-2016/html/8bbbf004-5565-5351-8009-d19f6bec5866.htm)

Use two explicit layers of data: `SectionActions` for the engineering values at a section, and `ActionRecord`/`AnalysisSnapshot` for source identity, location and evidence. Record whether a result is a static vector, a particular step, a component envelope, a statistical response result, or a justified code design envelope. The last three need their declared combination/design treatment; they cannot silently become a concurrent vector. CSI specifically explains why combining independent maxima before design can create an unrealistic force set. [CSI envelope guidance, updated 13 April 2012](https://web.wiki.csiamerica.com/wiki/spaces/etabs/pages/1476970/Envelope%2Bcombination%2Bnot%2Bfor%2Bdesign), [combination definitions](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Combinations/Load_Combination_Data_Form.htm)

Retain six-component source data, but let each check declare the effects it supports. A uniaxial flexure method must neither require irrelevant ETABS metadata nor silently ignore an axial/biaxial effect that makes its assumed model inapplicable. Local-axis signs must be mapped to physical reinforcement faces using actual orientation. Carry both object and element station systems through support-face checks and detailing.

SLS needs its own service-action and duration basis; ULS forces alone cannot supply long-term deflection, cracking history, creep/shrinkage or finishing dates. Reinforcement and construction also need geometry, supports, joint context, bar stock and fabrication rules. An ETABS force export cannot supply every beam-design input by itself.

Excel should calculate from a validated immutable snapshot. Import, model modification, analysis and file/report creation should be explicit application commands. Keep worksheet functions free of live COM calls and workbook mutations. Excel-DNA requires Excel COM object-model access on the main Excel thread; that constraint must not leak into the pure engineering API. [Excel-DNA COM guidance](https://excel-dna.net/docs/guides-basic/excel-programming-interfaces/using-the-excel-com-automation-interfaces/)

For optimization, distinguish fixed-demand reinforcement search from section/stiffness changes requiring global reanalysis. A candidate that changes ETABS analysis inputs needs a new snapshot before its result can be compared as a completed coupled design. A local beam solver remains useful for its own stated analysis scope.

## A public signature standard that stays usable

Use stable semantic operation IDs and idiomatic names: for example `beam.flexure.check/1` can map to Python `is456.check_flexure(request)` and C# `Is456.Flexure.Check(request)`. These are proposed interfaces. They do not require the same capitalization or identical class internals.

For each public operation specify: engineering purpose; input quantities and units; sign/coordinate convention; required and conditional fields; how optional values are resolved; code edition/data revision; applicability; named outputs; invalid-input behavior; engineering pass/fail behavior; numerical tolerance; examples; and compatibility policy. Source and example identity belong in operation documentation and structured check results. Tiny general geometry functions do not need a code edition.

| Proposed operation | Minimum meaningful contract | Result |
|---|---|---|
| `bar_area(diameter_mm)` | Finite positive diameter | Area in mm² |
| `reinforcement_geometry(section, bars)` | Section geometry and actual bar coordinates | Areas, centroids and geometric clearances |
| `is456.check_flexure(request)` | Section, materials, provided reinforcement, demand and applicable rule basis | Capacity, utilization, governing mode and check basis |
| `check_beam(request)` | Member topology, ULS/SLS action sets, detailed reinforcement and required-check profile | Per-check/per-station results and completeness |
| `design_beam(request)` | Design inputs, catalogues and constraints | Selected reinforcement plus the resulting checks |
| `build_bbs(resolved_member, rules)` | Bar paths/placements, shape and rounding rules | Schedule records, lengths, quantities and provenance |
| `price_quantities(quantities, rates)` | Quantity scope and complete dated rate basis | Priced items and missing-rate diagnostics |
| `etabs.read_snapshot(session, selection)` | Vendor session and acquisition settings | Vendor-neutral analysis snapshot plus source evidence |

Optional must mean one thing at a time. Use an explicit choice between a supplied effective depth and a geometry-derived depth; reject conflicting definitions. Do not use zero, an empty cell or an absent field interchangeably. A default stock list or density can be useful when chosen through a named policy and returned as an effective input. Do not silently default geometry, critical design actions or a missing price.

Separate mathematical failure, invalid input, engineering failure, inapplicability and an unevaluated required check. Rich results should include field-specific diagnostics and governing evidence. Return large traces, all-candidate tables and stress samples only when requested; ordinary calculations should not allocate a report on every call.

## Keeping Python and .NET aligned

| Execution strategy | Benefit | Cost and fit |
|---|---|---|
| Native Python + native .NET | Both are ordinary libraries in their ecosystems; Excel uses .NET directly | Two implementations to maintain; recommended for the agreed common feature set |
| One .NET engine + Python.NET wrapper | One numerical implementation exposed to Python | Python users need a compatible .NET runtime and type conversion; choose only if that deployment tradeoff is acceptable |
| One service process called by both | One running calculation engine | Process lifecycle, transport and offline-use complexity; useful for a service product, unnecessary for basic library calls |

Python.NET genuinely supports calling .NET assemblies from Python and selecting CoreCLR. That makes a wrapper viable, but it is not equivalent to a Python-only installation. Conversely, embedding Python inside .NET brings Python-runtime initialization and GIL management into the host. Neither bridge should be added to the normal Excel calculation path merely to avoid writing a small C# kernel. [Python.NET: .NET from Python](https://pythonnet.github.io/pythonnet/python.html), [Python from .NET](https://pythonnet.github.io/pythonnet/dotnet.html)

For native parity, share operation definitions, normalized tables, enum meanings, units, defaults, applicability and source/example identities. Keep package versions, implementation versions, schema versions and code-data revisions distinct. Generate mechanical projections where helpful; retain semantic validation and algorithms as reviewed code. JSON Schema alone cannot prove equilibrium, valid detailing or correct code applicability.

Maintain conformance per capability, not a single whole-library “same” claim. Replay valid, invalid, boundary and unsupported cases in both runtimes. Compare results using quantity-specific absolute and relative tolerances, while requiring agreement on discrete engineering outcomes. Investigate disagreements near a design limit; do not increase tolerance to conceal a pass/fail difference. Use independently verified examples as the oracle so the same bug cannot pass merely because both implementations reproduce it.

Keep mathematical values unrounded until a declared engineering or presentation rule requires rounding. Specify optional/null/zero behavior, enum strings, array order, timestamps, non-finite rejection and canonical identity explicitly. Separate source acquisition evidence from the numeric input identity so a fresh import of unchanged values does not defeat a numerical cache.

Python and .NET do not need duplicate Excel automation, identical internal solvers or identical UI helpers. A C# ETABS adapter can export the common snapshot for either library to consume. The normal Python package should not install Excel/CSI dependencies; the normal .NET package should not require Excel to load. The existing Python optional dependency groups and C# platform-neutral engineering projects already support that direction.

## Performance and the next implementation sequence

Language choice is only one part of performance. Import once, normalize once, evaluate batches in memory, reuse immutable geometry/material preparation, and compute detailed traces on demand. Cache by engineering-input and code-data identity. Keep result objects for correctness while using efficient internal arrays where profiling justifies them.

Benchmark the real boundaries separately: scalar calculation, member/check batch, candidate search, serialization, ETABS acquisition and Excel recalculation. Compare both runtimes with identical inputs, scope, warm/cold conditions and correctness checks. The existing C# microbenchmark is not evidence of a Python speedup or finished workbook performance; no new comparative benchmark was run for this research.

Proceed through complete engineering slices. First establish vendor-neutral actions and the signature/optional-input rules. Then implement one flexure slice in both libraries, from actual selected bars through a check and a shared independent example. Continue with shear/torsion, SLS, member detailing, fabrication/BBS, quantities/pricing and optimization. Each slice should have direct library examples before adapters expose it.

Prioritize corrections to misleading defaults, action-basis semantics and required/provided distinctions before expanding coverage. Preserve old entry points through tested compatibility translators. Keep implementation, sourcebook examples and application acceptance as different evidence: a corrected sourcebook record must reach both engines; a passing library example must still be exercised through the Excel/ETABS adapter before claiming that workflow works.

## Evidence and research limits

This research used two bounded independent lanes, parent inspection of consequential local findings, five external structural-library references, Python.NET and Excel-DNA documentation, CSI release/method/combination references, and installed API metadata. Web references were accessed on 3 September 2026; undated live documentation is cited as accessed, not assigned an invented publication date.

The installed CHM was located, but two extraction attempts produced no usable topics; the extraction cause remains unconfirmed. Current assembly metadata and public CSI documentation supplied the interface evidence instead. No running ETABS model, Excel workbook, dependency installation, numerical implementation or comparative performance test was changed or exercised. Older CSI method pages are identified by version, and assembly presence is not treated as live acceptance.

Historical findings are bounded by the inspected source/history and the earlier failure register. This is not a claim that every past issue has been re-audited or that deliberate scope limits are unfixed defects.
