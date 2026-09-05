# ETABS workflow: capture, design, reanalyse and compare

Date: 2026-09-05. Latest task: XLL-PRODUCT-ARCHITECTURE-AUDIT.
Status: source-reviewed architecture recommendation; automatic product integration
is not implemented. The owner requested a fair comparison of the original,
implemented and proposed workflows before further coding. The audit below
supersedes the recent RAM-only/reacquire-only recommendation and the older
workbook-resident snapshot plan. Use memory for active work, small Excel inputs/
outputs, and external replayable evidence. A general-purpose database remains optional.

## Direction and authority

The owner wants to acquire the required ETABS model data, interpret it in the
library, keep heavy data out of Excel, design and search for practical changes,
update sizes in ETABS, reanalyse and repeat, then compare savings. Small useful
tables may be written when requested, including the default Assumptions sheet
on first explicit setup. Retain the
[ribbon-first decision](excel-ui-review.md#owner-decision-ribbon-first-worksheets-on-demand):
loading the add-in creates no sheets; setup creates only Assumptions.

This refinement follows [PF8](library-definition/pf8/baseline.json),
[PF11](library-definition/pf11/baseline.json) and the
[WP10 read boundary](wp10-etabs-read-adapter.md). ETABS mutation remains WP11's
owned-copy transaction after the read/import path is qualified. This review
performs no live acquisition, setter, model copy or analysis and changes no
engineering code, approved design scope or original P0-P6 meaning.

## Whole-product audit and decisions — 2026-09-05

### Verdict and audit boundary

Keep the existing engineering and evidence foundation; add the missing
application services and a simpler public UI. Neither the old sample-workbook
layout nor a RAM-only overnight application is the recommended final product.
The original architecture already called for reusable in-memory sessions and
durable identities/evidence. Much of the new direction improves its presentation
and integration, rather than replacing its engineering architecture.

This audit inspected the source at `e4d1a940457d99635ea5e9806f5c5651f38cff69`,
the WP01-WP10-04 implementation record and retained acceptance receipts. Two
bounded read-only reviews covered the engineering chain and Excel session/UI;
the parent independently inspected the decisive source paths and performed the
verification below. It is an architecture/integration audit with existing
regression evidence, not a clause-by-clause recertification of every formula,
an installed acceptance of new commands, or approval of a building design.

| Approach | What was good | What is insufficient for the intended product | Decision |
|---|---|---|---|
| Original XLL architecture | Pure C# ownership, bounded solver, explicit commands, reusable memory and durable evidence | Many proposed controls; early single-process/runtime assumptions preceded installed work | Retain the principles; use current qualified runtime and later host boundary |
| Implemented WP01-WP08 | Explicit units, real reinforcement geometry, scoped checks, identities, complete-result aggregation and deterministic ranking | Operations require caller-supplied engineering inputs/evidence; they do not yet automate the whole design journey | Reuse; build orchestration instead of rewriting kernels |
| Implemented WP09 | Strict inputs, controlled writes, readback/rollback, freshness, save/reopen and installed evidence | Technical JSON tables, one-candidate evaluation and discarded ribbon feedback | Preserve engine guarantees and legacy compatibility; replace ordinary input/output presentation |
| Older WP10-05 proposal | Exact portable snapshot storage/replay and explicit import/mapping | Heavy chunked workbook tables are an awkward model/result store for repeated runs | Keep the snapshot contract; retire workbook-resident heavy storage as the new default |
| Recent UI and RAM proposal | Transparent assumptions, separate capture stages, physical-span decisions, fewer manual steps | Summary-only persistence cannot replay lost inputs; nine buttons do not supply the missing services; mandatory local-solver comparison is too broad | Retain the useful UI; use hybrid storage, capability-based controls and qualified solver applicability |

### What WP01-WP10-04 actually provides

The [implementation record](../../library/implementation-status.md) remains the
packet-by-packet source. Completion means its declared scope, not every future
workflow that may call it.

| Packet | Reusable implementation | Boundary relevant to this product |
|---|---|---|
| WP01 | Canonical contracts, actual bar geometry, flexural operations | Imported actions and reinforcement choices still need mapping/synthesis |
| WP02 | Actual-link shear/torsion checks with concurrent actions | Unsupported interaction components cannot be discarded to obtain a pass |
| WP03 | Action normalization, support-face/span topology validation, planar beam solver | Callers supply support/span semantics and applied loads; a source graph is not reconstructed automatically |
| WP04 | Explicit SLS screening/component aggregation/crack checks | Required strain, chronology, stiffness and displacement evidence must be obtained or calculated; forces alone are insufficient |
| WP05 | Detailing, anchorage/lap, seismic/fit operations within declared scope | Applicable inputs and actual arrangements must be produced and rechecked |
| WP06 | Validated project basis and complete-member evidence aggregation | `MemberDesignOperations.Design` consumes `LeafResults`; it does not run all leaf calculations or choose bars |
| WP07 | Bar paths, schedules, quantities, cost and calculation packages | Resolved actual paths and concrete/formwork ownership are inputs; required steel area is not a BBS |
| WP08 | Finite candidate generation/ranking and fixed/coupled result semantics | `OptimizeBeam` ranks supplied `Evaluations`; evaluator execution and common-section group search remain to be built |
| WP09 | Qualified standalone Excel functions/commands and controlled outputs | No connected-model session, public one-sheet mapper, new ribbon or unattended loop is accepted |
| WP10-01 | Portable request/snapshot, units, identities and row dispositions | A generic schema is not a qualified producer for every model/result type |
| WP10-02 | Exact-version getter matrix and retained one-member live capture | Not broad geometry capture, all-model results, or a launch/analysis service |
| WP10-03 | STA lease, deadline/fence, journal, postflight and durable artifact | Broker library is not a packaged production host; timeout completion does not imply COM quiescence |
| WP10-04 | Offline projection, conservation and Python/.NET replay | Accepted projector/normalizer is bounded to the declared horizontal-frame, kN_m_C, static-concurrent policy |

Decisive source paths:

- [MemberDesign.cs](../../../CSharp/src/StructuralEngineering.Beam/MemberDesign.cs):
  `Design`, `ExpectedLeaves`, `ValidEvidence` and depth-iteration validation.
- [OptimizationOperations.cs](../../../CSharp/src/StructuralEngineering.Optimization/OptimizationOperations.cs):
  `OptimizeBeam` builds a domain and supplies request evaluations to `Rank`.
- [BeamTopologyBuilder.cs](../../../CSharp/src/StructuralEngineering.Analysis/BeamTopologyBuilder.cs):
  `Define` requires supplied ordered supports, spans, regions and mappings.
- [PlanarBeamSolver.cs](../../../CSharp/src/StructuralEngineering.Analysis/PlanarBeamSolver.cs):
  solver inputs include actual applied loads, restraints and stiffness.
- [WorkbookInputReader.cs](../../../CSharp/src/StructuralEngineering.ExcelDna/WorkbookInputReader.cs)
  and [WorkbookCommandEngine.cs](../../../CSharp/src/StructuralEngineering.ExcelDna/WorkbookCommandEngine.cs):
  strict legacy tables and transactional/freshness behavior to preserve.
- [EtabsLiveGetterProbe.cs](../../../CSharp/src/StructuralEngineering.Etabs/EtabsLiveGetterProbe.cs),
  [EtabsCaptureProjector.cs](../../../CSharp/src/StructuralEngineering.Etabs/EtabsCaptureProjector.cs)
  and [AnalysisSnapshotNormalizer.cs](../../../CSharp/src/StructuralEngineering.Analysis/AnalysisSnapshotNormalizer.cs):
  explicit one-member and policy boundaries, not a generic full-model importer.

No numerical kernel defect was demonstrated by this audit. Two existing UI
limitations are confirmed: ribbon callbacks discard returned results, and blank
legacy setup seeds a sample. The new adapter must present command outcomes and
make sample creation explicitly DEMO; do not silently convert that sample into
a connected project's design basis. Those runtime changes belong to the first
UI implementation packet and are not claimed fixed by this document.

### Data decision: memory for work, files for replay, Excel for people

| Option | Strength | Cost / failure mode | Verdict |
|---|---|---|---|
| Everything in workbook tables | One portable workbook; useful for the existing small standalone workflow | Excel formatting/serialization and repeated heavy writes; opaque chunk tables; workbook save becomes a data checkpoint | Retain legacy support; reject as default connected-model storage |
| Everything only in RAM | Fast transient prototype and local filtering | Process loss loses exact trial inputs; summary rows cannot reconstruct forces or a baseline | Allow disposable development runs; insufficient for unattended acceptance |
| RAM plus immutable external snapshots/journals and compact workbook | Fast local work, inspectable history and replay using existing codecs | Must bind storage/project identity and support export/relocation | Recommended next implementation |
| Embedded SQLite project store | Transactions and indexed cross-run queries without a server | New dependency, schema migration and packaging/backup work | Reconsider when measured history/query needs justify it; not required to begin |

SQLite is a credible later application-file format, not a mandatory service or
current performance claim. Its own [usage guidance](https://www.sqlite.org/whentouse.html)
supports local application storage. Begin with maintained canonical JSON codecs
and immutable per-run files; avoid implementing a custom relational database.

The proposed storage contract is:

| Owner | Persisted / live content | Lifecycle |
|---|---|---|
| Workbook | Assumptions with units/origins, small model summary, document/project IDs, selected run reference and requested Results/reports | Ordinary Save; outputs identify historical or current basis |
| Session memory | Immutable model context, indexed required force rows, effective inputs, active designs and bounded candidate summaries | Reuse across selections; release on close; no workbook force/joint dump |
| Private local project working folder | Manifest, frozen input/profile/catalogue versions, acquisition journals/raw artifacts, validated snapshots, run/transaction records and detailed review evidence | Successful capture/trial checkpoints do not depend on final workbook Save |
| ETABS files | Preserved original/baseline, identified candidate copies, retained best/final copies | Owned-copy mutation only; uncertain copies cannot be treated as accepted parents |

Use a project-owned local folder, initially under the existing per-user evidence/
application-data convention; persist only its locator and identity in Excel.
An unsaved workbook may edit assumptions, but a durable run must have a resolved
project identity and writable storage. Moving/sending only the workbook is not
project transfer: provide an explicit portable export later and report missing
external artifacts honestly. Keep live journals local, with a single owning
writer; shared/network project collaboration is separate scope.

Retain each actual ETABS analysis snapshot used in a run, not a duplicate full
snapshot for every local bar/size candidate. Preserve baseline and verified
best/final inputs, all ETABS trial assignments/outcomes, candidate input deltas,
check reasons and governing evidence references. Reuse immutable artifacts by
content identity. Do not strip raw/provenance fields from the current canonical
snapshot to save space; a leaner runtime projection may reference that intact
artifact. Compression/partitioning requires byte-equivalent replay proof.

On reopen, restore assumptions and historical summaries. Validated saved
snapshots can support explicitly offline review/recalculation without ETABS;
they do not establish current live-model state. Reconnect/revalidate before new
live capture or mutation, reacquiring whenever coverage or freshness cannot be
proved. A crash does not resume setters automatically. This distinction retains
the old replay benefit without placing heavy snapshots in Excel.

Document identity, project identity, analysis identity and the initiating live
workbook object are separate. Save As/duplicate opening must resolve that binding
without transferring model-mutation ownership accidentally. A filename change
alone need not invalidate identical physics; ambiguous document/session binding
does block writes. Specify and qualify these cases before adding long commands.

### Acquisition and model understanding

Connect needs an additive model-context contract that can exist before analysis.
Do not weaken `analysis_snapshot/v1` to call a context-only or unlocked model a
complete force snapshot. Preserve source objects, analysis elements and derived
physical spans as separate identities. Geometry for beams/columns/joints and
relevant support objects is shared by design, group formation and a later 3D view.
Slab/wall presence may matter for support/loading context even when their design
is unsupported; absent context must remain an explicit scope limit.

Acquire the declared model context once per verified revision and the required
result domain once per analysis revision; then filter/index locally. Repeating
the one-member probe for every beam would repeat shared catalogs and pre/post
work and is not the broad-model implementation. Prefer qualified bulk getters/
tables plus deduplicated property reads. CSI documents
[GetAllFrames](https://docs.csiamerica.com/help-files/etabs-api-2015/html/9241fd9f-23d8-89c9-f4be-d6f7066a95a4.htm)
as a bulk interface in an older API; that is evidence to investigate, not proof
of the installed 23.3.1 signature, completeness or speed.

The retained one-member snapshot is 1,669,798 bytes with 13 force rows and shared
catalog/ledger data. Do not linearly extrapolate that size or its 410 calls to
1,000 members. Measure API, normalization, indexing, disk and Excel times
separately on PF9's 100-member/10,000-row and 1,000-member/100,000-row workloads.
Do not replace concurrent force rows with independently maximized components.

The source-to-topology service must classify real supports and derive faces,
spans and candidate construction groups from IDs, connectivity, axes, section
orientation, offsets, releases and member roles. Coordinate proximity alone is
insufficient. A 3D rendering is a projection of this shared model, not proof of
support conditions, actual load paths or design suitability.

### Application, host and solver decisions

Add a host-free application layer that maps a frozen source/project basis to
real requests, invokes the engineering operations, selects actual reinforcement,
rechecks affected leaves and creates current quantities/evaluations. Excel calls
this layer; it does not calculate structural formulas or ask users to populate
internal leaf-result JSON. The same layer must support standalone/offline use,
manual stages and the later Auto Run.

For live handoff, retain WP10's versioned file/message boundary and target a
packaged, bounded ETABS worker using the existing STA broker. Keep it a product
component with no permanent service or separate normal user UI. Qualify its
actual launch, lifetime, lease, progress, timeout/quiescence and cleanup before
shipping it. This updates the original single-product-process preference;
single XLL distribution and a worker executable are different packaging claims.
The pure engineering libraries remain usable without that worker.

All Excel object-model access/writes return to the initiating Excel thread.
Long computation and ETABS calls must not block that thread. Microsoft's
[Excel threading guidance](https://learn.microsoft.com/en-us/office/client-developer/excel/multithreading-and-memory-contention-in-excel)
explains the command/main-thread boundary. The broker's completion and quiescence
tasks are distinct: a timeout can return while cleanup still holds the lease.
Neither an overnight retry nor another workbook may ignore that state.

Solver comparison is conditional on a qualified equivalent local model. It is
not a universal extra pass required for every real ETABS beam. Acquire actual
loads, supports, modifiers and comparison criteria where the profile supports
them; source output forces cannot reconstruct those inputs. An explicitly
supported ETABS-only analysis route may continue when local comparison is not
applicable. An unexpected disagreement on a claimed equivalent model needs
diagnosis, not a larger beam or a widened tolerance.

Global ETABS analysis, required global/other-member checks and actual-bar beam
checks remain distinct. Neither the solver nor a green analysis status permits
the product to claim an entire building is safe. Final-size reanalysis and
redesign are required by CSI's
[concrete frame procedure](https://docs.csiamerica.com/help-files/etabs/Getting_Started/Concrete_Frame_Design_Procedure.htm).

### UI decision and implementation order

Keep Assumptions, Connect ETABS, Get Forces, Design, Optimise, Update & Recheck,
Auto Run and Compare Runs as the eventual routine actions. Keep Solver Check
available in the Optimise/diagnostics detail for applicable models rather than
requiring an extra manual step in every run. Show only implemented capabilities
in the shipping ribbon; the nine-button illustration remains a proposal.
Legacy commands stay usable without forcing their technical worksheet layout on
new users. A persistent status/reason is more valuable than another control.

| Increment | Concrete outcome and acceptance | Boundary |
|---|---|---|
| A — Reconcile WP10-05 contracts | Freeze session/project/document IDs, context versus force snapshot, typed input mapper, external-artifact lifecycle, output ownership and invalidation matrix | Retire the old chunk-table/reconstruct-in-workbook card; preserve current wire schemas and legacy behavior |
| B — Public input and offline review | One DEMO-labelled Assumptions sheet, explicit one-beam input/detail entry when needed, validated saved-snapshot review in memory, visible command outcomes and on-demand Results | No live ETABS or claim that imported forces alone constitute a complete design |
| C — Complete supported baseline design | One explicit supported beam basis drives actual bars/layers/links, all required leaf requests, consistent depth iteration and current detailed outputs | Use standalone/retained fixtures; unresolved SLS/detailing inputs remain blocked; no profile weakening to force a pass |
| D — Live handoff and model context | WP10-05B worker and separate Connect/Get Forces services; qualify exact target, progress/cleanup, required metadata and existing-result capture | Missing analysis initially returns Analysis needed; automatic preparation appears only after an owned-copy capability is qualified |
| E — Broad capture and read qualification | WP10-05C supports representative multiple members, context-to-span mapping and local filtering; WP10-06 passes installed Excel/ETABS and PF9 workloads | Multiple beam selections cause zero extra acquisition calls within the same complete current snapshot |
| F — Practical search | A span/group evaluator invokes the baseline design service, feeds WP08 ranking and shows complete/incomplete fixed-action alternatives | Qualified local Solver Check is optional by profile; all section changes remain provisional |
| G — One coupled change | Apply one proposal to a copy, read back, analyse, reacquire, redesign, check required effects and save matching evidence/model | Original unchanged; final dimensions equal analysed dimensions; unqualified effects prevent wider acceptance |
| H — Bounded unattended work | Same manual services, retained baseline/best, each ETABS trial recorded, no duplicate loops, stop budgets, safe pause and morning review after process loss | Qualify real application/modal/error behavior; no automatic replay of uncertain setters or global-optimum promise |

Owner sequencing update (2026-09-05): A/B is merged. Bring D's running-model
connection and context ahead of C so engineers can check actual model intake
first, then qualify existing-force handoff and E's broader capture before C.
The letters identify capabilities, not mandatory dependency order. The active
WP10-05B plan card owns the current bounded connection packet. Recheck this
whole-product goal and dependency order at each packet intake; change only the
affected canonical plans when evidence or owner priorities change.

These are implementation increments within the existing WP10/WP11 programme,
not a renumbering or a claim that one session can cross every installed gate.
The first coding packet should implement A/B with exact acceptance, not all
eight increments or all eventual ribbon callbacks at once. C supplies the missing
engineering orchestration; it is substantial work, not a UI rename.

### Verification performed and readiness conclusion

- Locked .NET restore and Release solution build passed with zero warnings/errors.
- Existing native WP01-WP10 tests: 121 passed. Existing Excel/workbook and WP10
  offline host tests: 58 passed. Environment-dependent live/configured tests were
  explicitly excluded; they are not counted as a new installed pass.
- The separately configured retained-artifact normalization test passed. The
  newly emitted snapshot replayed in Python with identical canonical bytes and
  SHA-256 `b0379473f0e195c4a8e947b89218e0af4e1294f80e72824bd731d7fa65af627c`:
  one member, 13 force rows and 110 accepted model/action records.
- Existing Python WP10 contract/conformance tests: 19 passed. Original raw and
  retained snapshot file hashes matched their WP10-04 receipt. No new tests were
  added and no live Excel or ETABS instance was operated.
- WP09's retained installed receipt records its 20-member/200-operation
  standalone acceptance. It remains evidence for that scope, not the proposed
  public mapper, connected session or overnight run. New performance, whole-model
  and installed workflow claims remain unqualified.

Proceed with the reconciled application/session and public-input packet. Reuse
the accepted kernels and receipts. The principal remaining work is orchestration,
source completeness, topology, live handoff and recovery; changing storage or
ribbon labels alone cannot complete the automation product.

## 1. Connect and preserve a baseline

An explicit ribbon command identifies the process, installed API, exact model,
saved-file relationship, model state, analysis availability and result selection.
An unsaved or changed open model cannot silently share its disk-file identity.
Resolve that relationship before binding a reconstructible baseline B0.

Preserve the original model and keep B0's source data, design basis, units,
case/combination definitions and quantity/rate basis in memory throughout the
run. Keep required acquisition/transaction evidence separately. Record
the parent accepted iteration separately: original-model and previous-iteration
comparisons have different meanings.

Keep the attached source getter-only: no unit/selection setters, unlock, analysis
or save. Any required selection/analysis preparation belongs to a separately
identified owned-copy operation. Broad acquisition cannot silently extend the
accepted getter matrix or change result selections on the attached source.

### Connect and Get Forces are separate actions

Connect attaches to a uniquely identified running model or opens a connection
dialog. With no suitable instance, the launch path starts installed ETABS and
lets the engineer choose a model using ETABS' own Open dialog. Finish this
interactive setup before an unattended run. Launch/open/API compatibility still
requires installed qualification; a launched process is not permission to mutate
an original model. Show source and active working-copy paths distinctly.

Connect reads model name/path, runtime, source/display units, stories, section/
material definitions, object classifications, joints, axes, offsets, releases and
connectivity needed for model understanding and physical spans. It does not read
force arrays or start analysis. Local 3D/context views use this same graph.

Get Forces verifies required case completion, result epoch/currentness, selected
combination dependency closure and data coverage. Locked state or a result file
alone does not establish current complete results. If results are usable, capture
them once. If missing/stale, the UI may continue automatically through a separate
owned-copy preparation/analysis capability within the bound run authority, then
acquire its results. Do not promote the attached source to owned mode or call
analysis/setters on it. The UI needs no extra technical ownership button.
Keep that effectful service separate from WP10's accepted read-only adapter.

## 2. Acquire once per source revision, then interpret locally

Capture broad model context and the complete result domain required by the
declared design profile. "All required data" is a bounded manifest, not every
possible output or time-history step. Do not omit required combinations for speed.

| Dataset | Interpretation and purpose |
|---|---|
| Catalogue | Stories, object/member IDs and classifications, section/material definitions, assignments and source units |
| Geometry/topology | Joints, coordinates, beams, columns and required slab/wall/support context; object/element mapping, local axes, offsets, insertion, releases, restraints and diaphragm/constraint context |
| Analysis basis | Loads, self-weight/mass assumptions, stiffness modifiers, cases/combinations and dependencies, relevant settings and result status |
| Results | Required members, stations, cases and steps; concurrent P, V2, V3, T, M2, M3 rows, plus required displacement/global-check evidence |
| Design basis | Verified strengths, exposure/cover, profiles, reinforcement and construction/rate inputs; distinguish imported facts, overrides and missing data |

Build one shared C# model with source-ID-based member/joint adjacency indexes.
Beam/floor selection and neighbour lookup use this model without returning to
ETABS. Keep unsupported objects as identified context; do not classify every
frame as a beam or every nearby endpoint as a support. Spans and support faces
need verified geometry/offsets and must be recomputed after relevant size changes.

Normalize once to the existing explicit kernel units; retain source units,
signs, axes/physical faces, row and case/step provenance. Display-unit changes do
not change physical quantities. Separate component maxima cannot be combined
into a fictitious simultaneous force vector. Missing required mappings prevent
completion of affected designs.

Prefer verified bulk API/table reads where the installed version supports the
required semantics; qualify equivalence to the accepted getter path first.
Deduplicate section/material reads. Keep COM acquisition serialized in the
existing STA broker; bounded parallelism is for pure library work. Pre/post
source checks reject mixed-revision captures. Preserve the current explicitly
evidence-derived revision semantics where ETABS supplies no native epoch.

## 3. Keep active data in memory and replay evidence outside Excel

| Location | Contents and behavior |
|---|---|
| C# memory | Model graph, source/current/baseline forces, active inputs and candidate calculations; reused within this session |
| Assumptions sheet | Small visible typed project inputs, source facts and named defaults, with units, origin and missing/override state |
| Requested outputs | Results, quantities or savings and small identity records; preserved by ordinary workbook Save |
| External working folder | Required acquisition journals/raw artifacts, validated per-analysis snapshots, frozen inputs and run/model-copy transaction records; no workbook force database |

Auto Run additionally persists a compact trial history after each state/trial:
source/copy and run/candidate identities, assumptions/profile/catalogue revisions,
changed assignments, stage and per-frame/check outcomes, quantities and stop
reasons. Store baseline assignments once and reconstruct trial assignments from
bound changes where useful. Retain the corresponding replayable analysis inputs
once per actual ETABS trial, not once per local candidate. Morning review must
not depend on a final Excel Save succeeding.

"Does not change" means unchanged within a verified revision. Materials,
sections, units and criteria are versioned too. The Assumptions sheet is an input
owner with typed validation; result summaries are projections. Design reads and
validates inputs in one action, with no separate Apply control. See the
[default policy](excel-ui-review.md#one-transparent-assumptions-sheet).

Closing Excel/workbook, unloading the add-in or a crash releases its heavy working
memory. Reopening restores assumptions and historical reports, with no active
ETABS connection. Validated external snapshots permit offline review and
recalculation; fresh live binding is required before live operations. Missing or
stale required data needs reacquisition. Saved cells never resume a coupled run.
Compare with the identified B0; restore its validated saved identity or establish
a new baseline explicitly, rather than calling the current candidate the original.

Use indexed arrays, shared property records and bounded candidate summaries.
Retain all required force rows in the supported workload; an envelope cannot
replace concurrent governing data. If the complete workload cannot fit, report
the supported limit instead of dropping rows. A durable partitioned project
store and automatic cross-session continuation can be added later behind this same model.

Share unchanged geometry/properties by verified content identity. After an
analysis change, old forces are stale even if member IDs are unchanged: refresh
the complete required result domain. Initial implementation compares the full
required model manifest; incremental acquisition needs a proven change detector.

Resolve input-sheet ownership, workbook/session binding, closure behavior and
memory limits before implementation. A general-purpose database is not a v1 gate;
the replay/history contract is a prerequisite to unattended acceptance.
No hidden data sheets are used. Preserve legacy WP09 workbooks and existing
portable snapshot/evidence contracts; qualify the new session lifecycle honestly.

## 4. Design the baseline and freeze a practical search

The [development preset](demo-beam-preset.json) supplies transparent example
inputs for demo models. It is not an approval of a connected real model. Keep
demo/source/override values distinct and include effective input origins in
every run. Demo reports stay labelled demo even if example checks pass.

Evaluate B0 using the same complete beam profile, detailing, quantity conventions
and rates as the candidates. Resolve required missing inputs before search;
baseline failures remain visible. Remediation differs from optimizing a feasible
baseline.

Define eligible beams/groups, fixed dimensions/exclusions, section and bar
catalogues, hard checks, permitted changes, cost/objective basis, candidate and
ETABS-analysis counts, wall-time budget and stopping rule. Use existing owner
authorization within this explicit scope, without asking again for each ordinary
iteration. Do not invent source facts to keep a run moving.

Favor a practical limited catalogue, repeated beam groups, continuity-compatible
bars, stock lengths and explicit construction constraints. Complete designs use
actual bars, spacing, anchorage, laps and stirrup zones. Rank feasible candidates
by the declared objective, including supported concrete, steel, formwork,
labor/waste components. Smallest section alone does not imply lowest cost.

Design is a dependency-driven sequence: validate basis and actions, design
flexure, choose longitudinal bars and layers, resolve actual effective depths,
design shear/torsion reinforcement, then complete serviceability, detailing,
anchorage/laps, continuity and applicable seismic/joint checks. Bar/link/layer
changes can alter effective depth or fit and must trigger affected rechecks.
Only a consistent complete arrangement produces qualified BBS/quantities.
The UI may show these stages one by one; it must not freeze an early flexural
pass while later detailing invalidates its geometry.

## 5. A fast library loop, followed by an ETABS loop

### Physical spans, feasible sizes and construction groups

Distinguish an analysis element, a physical span between verified supports and a
continuous beam line containing several spans. Grouping is derived from source
IDs, support faces, releases, offsets and member roles, not station spacing or
coordinate proximity alone. CSI's [frame meshing guidance](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Auto_Mesh_Options.htm)
confirms that internal analysis meshing does not change object definitions.

For ordinary prismatic beams, default to one width/depth pair throughout each
physical span. This is our construction policy, not a universal code mandate.
Continuity needs its own detailing checks; it does not force every adjacent span
to have identical dimensions. A continuous-line or repeated-beam group may use
a common section for constructability when all members permit it. Preserve fixed
sections, haunches, transfer/deep beams and other exceptions as explicit special
scope; do not flatten them automatically. Unresolved groups cannot be optimized.

Generate allowed `(width, overall depth)` pairs and actual bar arrangements.
Find each span's feasible candidate set across every required station/case/check,
then evaluate common pairs across every member of a proposed construction group.
Rank total group quantities/cost and practicality; if no common pair works,
report the exception rather than silently enlarging/splitting the group.
Independent minimum width and depth do not establish a feasible or optimal pair.
Station minima and capacity checks are screening aids, not finished span designs.

Keep mandatory strength/interaction, shear/torsion, serviceability/crack control,
bar fit/cover/spacing, anchorage/laps/curtailment, continuity and applicable seismic
or joint checks in the profile. Available actions, support geometry and actual
bars determine whether each check can complete. Do not expose routine switches
to disable required checks. All required leaves must pass before qualification.

### Local search and global reanalysis

**Local loop:** generate a deterministic candidate domain, perform cheap
applicability/geometry checks and evaluate complete member designs. Cache by full
effective-input/result identity. Reuse actions for bars/detailing changes only
when analysis assumptions remain unchanged, while reevaluating dependent checks.
Reinforcement-dependent stiffness or nonlinear-model changes need coupling review.

Size alternatives screened with existing actions remain provisional. Our native
beam-line solver supports bounded planar linear beam cases; it cannot supply
replacement whole-building forces or capture 3D redistribution. ETABS forces are
not a set of applied loads from which that solver reconstructs the building.
Qualified local models can help search order. Heuristic pruning means incomplete
search unless exclusions are proven valid for the final coupled problem.

Solver Check is a bounded local comparison, not a second whole-building solver.
First establish compatible topology, restraints, loads, stiffness/modifiers,
units, signs and stations against a reference ETABS case. Compare using qualified
criteria that are not tuned until a candidate passes. An unsupported local model
shows Not applicable and may use an explicitly allowed ETABS-only route. An
unexpected disagreement on a supposedly equivalent case requires investigation;
it blocks solver-led acceptance. Do not repair a mismatch by increasing sizes.

**ETABS loop:** combine compatible shortlisted changes into a model candidate
and evaluate their interaction together. Analyse selected model candidates, not
every bar option. Each iteration:

1. Bind its accepted parent snapshot and exact old/new assignments.
2. Preflight an owned candidate copy; preserve B0 and the last accepted copy.
3. Validate changes, apply declared setters and read back. Do not alter a shared
   section definition affecting undeclared members; assign distinct properties
   where needed.
4. Run required ETABS cases and dependencies; inspect successful completion.
   Relevant stiffness, mass, load or geometry changes invalidate old actions.
5. Capture a new complete required snapshot; recompute affected topology,
   beam checks, actual bars and quantities from the new actions.
6. Evaluate required global behavior and affected other-member/joint checks
   through their qualified owner. Missing column/wall/global capability prevents
   automatic whole-building acceptance. Checking neighbours alone is insufficient.
7. Accept a feasible, current candidate under the declared comparison policy;
   otherwise retain the previous best. A further proposed analysis change starts
   another iteration, not a final-design claim.

Maintain separate verdicts for analysis execution, force freshness/coverage,
local-solver comparison and engineering checks. ETABS completing analysis is not
a strength/detailing pass; execute required ETABS design/global checks where they
are part of the declared profile, plus the library's complete member checks.
An engineering failure may justify another section/bar candidate. A known failed
candidate can be rejected and search can continue from a verified parent; unknown
model/API state or a solver/data mismatch must stop for diagnosis instead.

CSI's [concrete frame procedure](https://docs.csiamerica.com/help-files/etabs/Getting_Started/Concrete_Frame_Design_Procedure.htm)
requires final-size analysis followed by design using those actions. Its
[locking guidance](https://docs.csiamerica.com/help-files/etabs/Menus/Analyze/Lock_Model.htm)
explains that unlocking removes results and describes preserving the original
before changes. Future transaction API calls need installed-version qualification.

## 6. Stop with a verified result and recoverable state

### One orchestrator for manual and overnight work

Auto Run uses the same Get Forces, Design, Optimise, Solver Check and Update &
Recheck services as the manual buttons. Bind the model/copy, eligible spans,
assumptions, allowed changes, objective and limits once. The demo preset uses
8 hours, 20 ETABS analyses and 10,000 local evaluations, whichever limit is met
first. These are adjustable run-policy examples, not a runtime guarantee.
Do not expose low-level numerical tolerances or per-check bypasses.

Freeze input revisions for a run. Worksheet edits either apply to the next run or
pause at a safe boundary; they never change the active run halfway through an
analysis. Pause stops scheduling new operations after the current non-interruptible
call; Stop finalizes history and preserves the last verified state. Neither
control promises to abort an in-flight ETABS call instantly.

The supported overnight environment needs an awake host, available ETABS license,
completed model selection and no unresolved input/modal state. Missing runtime
capability is an explicit preflight outcome, not an overnight retry loop. No
Codex scheduled automation is created by this product-design decision.

Keep the best verified feasible model and previously evaluated candidate IDs.
Stop on completed finite search, no accepted improvement under the stopping rule,
a repeated candidate or an analysis/evaluation/time budget. Budget/cancellation
returns the best verified result with incomplete-search status. If none exists,
report no verified feasible result. Do not promise convergence or a global optimum.

Final acceptance binds assignments, analysis revision, forces, reinforcement,
checks, quantities and the saved model. Final sections must be those actually
analysed. When using ETABS design checks, also verify analysis/design section
agreement; agreement alone does not establish constructible detailing or all
library checks.

Deliver an identified optimized ETABS copy and matching design data. Bar details
that ETABS cannot represent remain in the authoritative project schedule, bound
to the same model/member revision; do not claim those were written into ETABS.

Within one session, validated state supports bounded unattended work. Later
mutation keeps durable transaction stages; it does not require a full v1 force
archive in Excel. After process loss, validate saved inputs, reacquire missing or
stale live data and reconcile model state; no automatic cross-session continuation
is claimed. An uncertain setter,
analysis or save is never blindly
replayed: record the last confirmed stage and isolate the uncertain copy. A hung
call, unresolved popup, changed model or missing required fact stops with a useful
reason. Ordinary iterations require no human click once scope and inputs are
settled; unattended behavior still needs actual application qualification.

## 7. Compare savings on a common basis

Compare Runs provides a concise run table and on-demand per-frame details for
all trials, including rejected/incomplete ones. Each frame record includes:
source ID/label/story and physical span/group; old/proposed/verified dimensions;
longitudinal bars/layers and link zones; steel mass/concrete volume/formwork;
required check statuses with governing case/station, demand/capacity and reasons;
analysis/solver status; input/run identity and comparable cost/quantity changes.
Unavailable values are null with reasons, never zero or an invented pass.

Keep raw trial history separate from the best verified feasible shortlist. The
engineer can inspect why a cheaper trial failed, whether an unchanged frame became
governing, and which saved ETABS copy matches the selected report. Persist detailed
per-check summaries and governing evidence alongside compact history; render large
Excel reports on demand. Do not fill worksheets with thousands of rejected trials
during the search or claim a summary alone reconstructs the heavy source snapshot.

Show final-versus-B0 and final-versus-previous-accepted values separately. Use
matching member identities/scope, design requirements, rates, stock/waste rules
and concrete/formwork interface deductions. Include all changed quantities in
the reported scope, not only favorable member reductions.

Compare concrete volume, detailed steel mass, formwork area, supported cost and
section/bar standardization. Cost saving is comparable baseline cost minus final
cost; percentage requires a positive baseline and complete comparable inputs.
Show cost increases and missing components explicitly.

Required steel area from ETABS is not an issued bar schedule. Without baseline
actual bars/lengths, report same-method design-estimate savings using our detailing
on the original sizes, separately from issued-schedule savings. Beam-only
estimates do not establish whole-building or realized site savings.

## 8. Implement and qualify in useful increments

| Increment | Exit condition |
|---|---|
| WP10 session/context replan | Audit increments A/B: typed input/session/projection and external replay ownership; context/force contracts and required coverage fixed |
| Supported baseline design | Audit increment C: application service executes the required checks and synthesizes/rechecks actual bars, rather than accepting fabricated leaf results |
| WP10 import and scale | Audit increments D/E: multiple selections from one capture with zero extra ETABS calls; units/axes/coverage validated; offline replay and fresh live binding distinguished; memory measured |
| WP11 local search | Complete physical-span/group candidates from one snapshot; no setter; truthful provisional and incomplete-search states |
| WP11 one coupled change | One beam/group candidate applied to a copy, read back, reanalysed and redesigned; original unchanged and required effects evaluated |
| WP11 bounded repeated loop | Shared manual/Auto Run services, retained B0/best model, durable per-frame trial history, no duplicate cycles, safe pause/stop and final saved-model/results agreement |
| Integrated outputs | Comparable baseline/final quantities; requested sheets refresh without duplication; actual Excel/ETABS proof |

These are internal increments, not programme renumbering. Supported beams remain
the initial design scope; broad model context does not silently add column, slab,
wall or complete-building design capability.

Reuse snapshot codec/normalizer, getter matrix/STA broker, member/detailing/quantity
operations, candidate domain/ranking and freshness identities. Source owners are
the `StructuralEngineering.Analysis`, `.Etabs`, `.Optimization` and `.ExcelDna`
projects under `CSharp/src`. `OptimizationOperations.OptimizeBeam` builds/ranks a
domain from supplied evaluations; it does not itself orchestrate live ETABS.
WP10-01 through 04 and bounded WP09 installed acceptance are complete; the broad
importer, ribbon/project storage and coupled automatic loop remain future work.

Measure acquisition calls/bytes, normalization/indexing, persistence/reopen,
peak memory, candidate throughput, ETABS analysis count/time and optional Excel
writes separately against [PF9's budgets](library-definition/pf9/baseline.json).
Existing acquisition workloads are 100 members/10,000 rows and 1,000 members/
100,000 rows. Richer/larger domains need additional benchmarks. No speed target
permits skipping new forces or required checks.

No new scripts, skills or scheduled jobs are needed for this planning decision.
Affected implementation tests belong to the later packets; this review adds none.
