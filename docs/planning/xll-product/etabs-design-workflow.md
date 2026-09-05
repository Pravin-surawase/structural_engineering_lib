# ETABS workflow: capture, design, reanalyse and compare

Date: 2026-09-05. Task: WP10-WORKFLOW-REFINEMENT.
Status: source-backed proposal, not an implemented automatic loop.

## Direction and authority

The owner wants to acquire the required ETABS model data, interpret it in the
library, keep heavy data out of Excel, design and search for practical changes,
update sizes in ETABS, reanalyse and repeat, then compare savings. Small useful
tables may be written when requested. Retain the
[ribbon-first decision](excel-ui-review.md#owner-decision-ribbon-first-worksheets-on-demand):
loading the add-in or reading a model does not automatically create sheets.

This refinement follows [PF8](library-definition/pf8/baseline.json),
[PF11](library-definition/pf11/baseline.json) and the
[WP10 read boundary](wp10-etabs-read-adapter.md). ETABS mutation remains WP11's
owned-copy transaction after the read/import path is qualified. This review
performs no live acquisition, setter, model copy or analysis and changes no
engineering code, approved design scope or original P0-P6 meaning.

## 1. Connect and preserve a baseline

An explicit ribbon command identifies the process, installed API, exact model,
saved-file relationship, model state, analysis availability and result selection.
An unsaved or changed open model cannot silently share its disk-file identity.
Resolve that relationship before binding a reconstructible baseline B0.

Preserve B0's model copy, source data, design basis, units, case/combination
definitions, analysis evidence and quantity/rate basis throughout the run. Record
the parent accepted iteration separately: original-model and previous-iteration
comparisons have different meanings.

Keep the attached source getter-only: no unit/selection setters, unlock, analysis
or save. Any required selection/analysis preparation belongs to a separately
identified owned-copy operation. Broad acquisition cannot silently extend the
accepted getter matrix or change result selections on the attached source.

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

## 3. Keep heavy data out of worksheets, but preserve it

| Location | Contents and behavior |
|---|---|
| C# memory | Model graph, reusable properties, active inputs and result partitions; fast filtering and design |
| Versioned local project storage | Settings, facts/overrides, immutable baseline, canonical snapshots, accepted iterations and recoverable model-copy references; heavy payloads outside worksheets |
| Optional Excel sheets | Project/design-basis summary, member inputs, checks, changes, quantities or savings; explicit create/refresh only |

"Does not change" means unchanged within a verified revision. Materials,
sections, units and criteria are versioned too. Excel summaries are projections;
optional editable input tables need an explicit apply/validate route.

RAM-only storage would lose comparison and recovery evidence when Excel closes.
Persist reconstructible baseline and accepted results. Partition heavy results
by analysis revision, case and member group; load active partitions into memory.
Retain raw records needed for canonical replay and concurrent governing rows;
envelopes alone are insufficient. Baseline and accepted evidence are durable
project records, not disposable cache. Evict optional caches only when their
inputs remain reconstructible.

Share unchanged geometry/properties by verified content identity. After an
analysis change, old forces are stale even if member IDs are unchanged: refresh
the complete required result domain. Initial implementation compares the full
required model manifest; incremental acquisition needs a proven change detector.

Resolve the exact format, atomic save/recovery, portable packaging, retention and
workbook association before implementation. No mandatory hidden sheets are used.
Preserve the existing WP09 path for compatible legacy workbooks.

## 4. Design the baseline and freeze a practical search

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

## 5. A fast library loop, followed by an ETABS loop

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

CSI's [concrete frame procedure](https://docs.csiamerica.com/help-files/etabs/Getting_Started/Concrete_Frame_Design_Procedure.htm)
requires final-size analysis followed by design using those actions. Its
[locking guidance](https://docs.csiamerica.com/help-files/etabs/Menus/Analyze/Lock_Model.htm)
explains that unlocking removes results and describes preserving the original
before changes. Future transaction API calls need installed-version qualification.

## 6. Stop with a verified result and recoverable state

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

Durable stages support unattended work. Pure reads/calculations can resume from
validated checkpoints. An uncertain setter, analysis or save is never blindly
replayed: record the last confirmed stage and isolate the uncertain copy. A hung
call, unresolved popup, changed model or missing required fact stops with a useful
reason. Ordinary iterations require no human click once scope and inputs are
settled; unattended behavior still needs actual application qualification.

## 7. Compare savings on a common basis

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
| WP10 storage/context replan | Versioned save/reopen/recovery and acquisition coverage fixed; zero mandatory worksheets |
| WP10 import and scale | Multiple beam selections from one capture with zero additional ETABS calls; units/axes/coverage validated and medium workload measured |
| WP11 local search | Multi-option design and estimate comparison from one snapshot; no setter; truthful cancellation/incomplete-search states |
| WP11 one coupled change | One beam/group candidate applied to a copy, read back, reanalysed and redesigned; original unchanged and required effects evaluated |
| WP11 bounded repeated loop | Retained B0/best model, no duplicate cycles, safe recovery and final saved-model/results agreement |
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
