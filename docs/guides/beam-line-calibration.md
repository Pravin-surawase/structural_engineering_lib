# Beam-line reference comparison (W3H software contract)

This is a pure, bounded numerical comparison API, not an installed ETABS run or
acceptance of a structural model. The first Windows W3H checkpoint is **L1 local
software evidence only**. Model-specific L5 calibration remains held.

```python
from structural_lib import (
    BeamLineComparisonRequestV1,
    BeamLineCalibrationV1,
    compare_beam_line_to_reference_v1,
)

def compare(request: BeamLineComparisonRequestV1) -> BeamLineCalibrationV1:
    return compare_beam_line_to_reference_v1(request)
```

The exact public signature is
`compare_beam_line_to_reference_v1(request: BeamLineComparisonRequestV1, /) -> BeamLineCalibrationV1`.
Immutable contracts live in `core/beam_line_calibration.py`; pure orchestration
lives in `services/beam_line_calibration.py`. No COM, file access, model changes,
new dependency, HTTP route or Excel write is introduced.

## Inputs that must be supplied

- The complete hash-bound W3G solver result, not an array of guessed actions.
- Independently established current reference identity: model **file** digest
  and distinct normalized **model identity** digest, baseline, catalogue,
  model-definition/topology, scenario-definition and analysis-settings digests,
  ETABS version, exact selection ID/kind/name, step type and step number.
- A `BeamLineReferenceV1` bundle retaining full signed `BeamActionRowV1` rows,
  optional displacement/reaction rows, source references, and explicit topology
  and linear-response review evidence for this identity. This bundle is a
  caller-normalized input, not a replacement W3D/W3F extractor. Its provenance
  and physical validity require independent review; hashing cannot prove them.
- An explicit member/span/station and joint/node mapping. Local scenario/result
  IDs are mapped separately to the reference selection ID; internal IDs need
  not equal ETABS names. Every retained reference action row must map exactly
  once, every solver span needs reference actions, and each requested joint
  evidence set must cover every solver node. Reference extraction scope must
  be declared before comparison; this function cannot detect upstream omissions.
- `BeamLineComparisonCriteriaV1`, with a declaration reference and predeclared
  absolute/relative tolerances. There are **no project tolerance defaults**.
  The declaration flag records the caller's statement; it does not prove the
  historical time or engineering suitability of that decision.

The reference's `reference_sha256` is SHA-256 of UTF-8 JSON from
`model_dump(mode="json")`, excluding only `reference_sha256`, serialized with
`sort_keys=True`, `separators=(",", ":")`, and `allow_nan=False`. Existing action
and joint row hashes use the same convention, excluding `row_sha256`. Output
binds the complete request, reference, station mapping, criteria and exact
current identity; retain the canonical request beside the output.

## Numerical and mapping rules

For every declared component:

```text
signed_error = local_value - mapped_reference_value
allowed_error = absolute_tolerance + relative_tolerance * abs(mapped_reference_value)
pass = abs(signed_error) <= allowed_error
```

Relative tolerance is dimensionless. Absolute tolerance uses the component's
unit: kN, kN.m, mm or rad. Solver numerical residual tolerances are **not** model
calibration criteria. Signed shear and moment are mandatory. Optional node
displacement, rotation and reaction components are compared only when their
criteria are explicitly supplied. Missing requested evidence blocks; it is
never silently dropped or replaced by zero. An explicitly action-only request
does not establish displacement/reaction agreement.

Frame mappings explicitly select the V2/M3 or V3/M2 bending plane and signs.
Axes, signs, source-station origin and direction must remain consistent across
one span. Station distance and LEFT/RIGHT/CONTINUOUS side must match the exact
solver station index, within the declared coordinate tolerance. There is no
nearest-station lookup, interpolation or selective sign flip. Joint mappings
declare coordinate basis, separate translation/rotation axes and signs. Solver
metres become millimetres explicitly for displacement comparison. All unused
P/V2/V3/T/M2/M3 components remain retained in the reference, not derived by the
surrogate or implicitly certified.

## Outcomes and invalidation

- `CALIBRATED`: every declared numerical comparison meets the supplied criteria.
  This is scoped numerical agreement only, **not** acceptance of the mappings,
  criteria, model assumptions, general ETABS parity or L5 campaign completion.
- `OUT_OF_BAND`: at least one declared comparison exceeds tolerance; retain all
  comparisons and stop the dependent calibration/candidate workflow.
- `NOT_COMPARABLE`: missing five-state evidence, stale identities, bad hashes,
  incomplete/ambiguous mapping or invalid input. No partial comparison is
  returned. Noncanonical nonfinite constructed objects raise `ValueError`
  because no honest request digest can be recorded.

Output always retains `SURROGATE_ONLY`, `HELD_NOT_SUPPORTED` for independent
frame analysis, `NUMERIC_COMPARISON_ONLY` and `NOT_PROVIDED` professional
approval. A synthetic reference remains synthetic. Neither this function nor
its status authorizes W3I screening or replaces mandatory ETABS final actions.

Any change to the file, model, topology (geometry/releases/offsets/modifiers/
supports), loads/combinations/scenario, selection, settings or ETABS version
invalidates the frozen identity. Never relabel old snapshots after a save.

## Historical software checkpoint and current project hold

The owner reported saving the copied model while closing ETABS. Read-only
hashing proved the existing `.ebk` still contains the accepted old model bytes;
the saved `.EDB` is a distinct revision. Both remain untouched. That resolves
the unexplained-change concern, but does not refresh results or snapshots.

The accepted W3F reference still reports `calibration_fields_complete=false`,
unavailable spring evidence and unavailable diaphragm/slab context. No project
mapping or engineering tolerance declaration was supplied. Therefore no model
comparison, ETABS/Excel access, calibration pass or W3I work belongs to this
checkpoint. The next packet must establish those exact inputs and choose the
reference revision; using the saved revision requires fresh accepted reference
evidence after the recurring installed preflight. Preserve the old backup and
all old evidence; do not restore over or reinterpret the saved file.

Read-only process inspection during closeout also observed an ETABS window
titled `ETABS License Message`. This task did not launch it, inspect its body or
dismiss it. Licensing/model state is therefore an additional unverified live-run
boundary, not a reason to reopen or retry ETABS from this software checkpoint.

Evidence: [W3H software receipt](../verification/etabs-w3h-comparison-evidence.json),
[W3F retained holds](../verification/etabs-w3f-spring-live-evidence.json),
[accepted foundation plan](../planning/etabs-data-analysis-optimization-foundation-plan.md).

### Saved-revision access recovery (2026-08-30 successor)

The later owner-resumed Windows observation supersedes the live-state facts
above: both current copy and backup now match saved-revision hash `92b3fa00...`;
neither is the historical `99b7f3f1...` file. A separate verified immutable copy
of the saved revision is retained outside Git and was never opened.

After owner-restored COM registration, audited getter signatures were
revalidated. All cases reported finished and the requested combination reported
selected, but two force getters returned code 1/zero rows. One explicit
`SetComboSelectedForOutput(name, True)` reassertion of the already-true selection
returned 0 and restored result readback without analysis, restart or save.
This is observed output-state inconsistency; the internal CSI cause remains
unconfirmed. Do not silently add this setter to read-only extraction or repeat
it when force access already works.

The [successor receipt](../verification/etabs-w3h-access-recovery-evidence.json)
binds a complete fresh W2 baseline/catalogue and the bounded 40-getter W3F
refresh to that saved revision. File bytes/size/mtime, lock, statuses, selection
flags and restored units remained exact. No blocking dialog was visible at
postflight; license duration/entitlement was not certified.

Spring and diaphragm/slab evidence remains unavailable, and independent
physical mapping and predeclared criteria are still missing. Required-
calibration replay blocks without partial snapshots. Those are the current L5
and W3I boundary, not COM activation or unreadable forces. The next packet must
establish that basis from engineering evidence; endpoint restraint flags alone
do not model a building member coupled to other beams/columns. A synthetic
benchmark or ETABS-derived boundary fitted to the same forces is not independent
calibration of this building.

### Saved-evidence feasibility checkpoint (2026-08-30)

The [feasibility receipt](../verification/etabs-w3h-feasibility-evidence.json)
records a successor assessment, not another recovery or calibration run. All
81 prior evidence files rehash correctly. The complete saved frame population
contains 77 horizontal, one-to-three-span geometric groups. The endpoint-only
graph leaves 23 groups apparently isolated; geometric projection locates every
one on other frame interiors. All 77 therefore have external endpoint or
interior geometric contacts. Coincidence and text-export meshing flags are
**not** an audited analysis-mesh graph or an effective support model.

One narrow installed read checked the shortest candidate and its two joints:
31 audited getter records, no new force extraction, no setter. Both joints have
six false restraint flags and nonzero vertical displacement for the exact
accepted combination. The member has both bending rotations released at both
ends and zero end-length offsets. Seven spring-related calls return CSI 1;
their evidence remains unavailable, not absent. File, backup, immutable-copy,
lock, units, case statuses and all selection flags remain exact.

The current solver cannot encode imposed vertical settlement or surrounding
frame/slab participation. Replacing these moving joints with zero-displacement
supports would change the physical basis; declaring the isolated line FREE
does not represent its supporting structure. This does not prove all 153
members unsuitable or rule out a justified action-only study of a pinned
member. Such a study must explicitly declare its reduced scope and cannot
establish displacement agreement or full project calibration.

The next engineering input is a specific independently reviewed reduced-line
mapping: member/span/station/axis identity, effective supports, complete loads,
slab participation, linear-response basis and predeclared comparison criteria.
Ask the originating engineer for that basis, not the owner to guess defaults.
Alternatively, a separately accepted programme decision may define a fully
specified independent benchmark for installed software verification only; it
must not be relabelled as calibration of this building or unlock W3I.

Do not repeat registration, output-selection recovery, full extraction or
analysis to address this hold. No solver/comparator, Excel or service was run
in this checkpoint. The external notebook replays three code cells through
Python and retains outputs; Jupyter-kernel/nbclient validation was not performed
because those optional packages are absent. No dependency was installed.

### Independent installed software benchmark (2026-08-30 successor)

The owner chose to continue without involving the originating engineer. That
authorizes a separately specified software test, not guessed building supports
or professional approval. The [benchmark receipt](../verification/etabs-w3h-independent-benchmark-evidence.json)
records one new isolated ETABS 23.3.1 instance/model: a 6 m, 300 x 500 mm elastic
simple beam, E = 25,000 N/mm2, explicit pin/roller and out-of-plane restraints,
zero self-weight, and a -10 kN/m global-Z linear-static case. No building member
or old model was changed. Both preanalysis and analyzed test copies are retained.

Geometry, loads, signs and numerical criteria were frozen before ETABS startup.
The declared scope is all 13 signed force stations plus both endpoint
displacement/rotation/reaction rows. All 34 comparisons pass through the public
solver/comparator; peak sagging moment is 45 kNm and each support reaction is
30 kN. Full same-row P/V2/V3/T/M2/M3 remains in the external reference. Interior
displacement is explicitly NOT_REQUESTED: this packet does not reconcile
ETABS shear deformation with the Euler-Bernoulli solver. The comparator's
`CALIBRATED` status is scoped numeric agreement, not building/L5 acceptance.

Installed startup returns a null filename before a model exists. After the
first new-model save, its full-path getter instead named the auto-created
`.$et` text export while the filename-only getter named `.EDB`. The guard
stopped before analysis. One statically audited reload of the exact newly
saved `.EDB` restored exact API identity with unchanged file bytes; the internal
CSI cause is unconfirmed. Never strip/replace the extension to manufacture an
identity or generalize this recovery to a user's open model.

Exactly one analysis invocation ran; ETABS also generated its internal `~LLRF`
case. No design command ran. Selection and units were restored, the test
instance closed, and the owner copy/backup/immutable baseline, lock, units,
15 case statuses and 77 selection flags stayed exact. No Excel/service started.

At this checkpoint the next software-only packet was to define a separate
two-span linear benchmark and independent reference values before results. Audit
only additional required operations, retain the new immutable baseline, and
use one candidate/check sequence per stable packet. Do not repeat this passed
run or the building recovery. Multi-span, interior-displacement and physical
building calibration remain separate; W3I and professional approval stay held.

### Two-span and earlier-building regression (2026-08-30 successor)

The owner approved the three-track validation plan: exact ETABS data transport,
beam design checks using ETABS actions and explicit design inputs, and separately
bounded independent force prediction. The earlier building remains a regression
asset rather than being discarded because one reduced-line mapping is missing.
See the [active plan](../planning/etabs-data-analysis-optimization-foundation-plan.md#owner-approved-validation-continuation-2026-08-30).

The [two-span receipt](../verification/etabs-w3h-two-span-evidence.json) records
two equal 6 m continuous spans, three vertically restrained/free-rotation joints,
300 x 500 mm sections, E = 25,000 N/mm2, no self-weight, and -10 kN/m on both
spans. Before any installed result, the specification froze three-moment,
equilibrium and integration reference formulas, 50 station rows, component
signs and numerical criteria. All 112 public comparisons pass: support
reactions 22.5/75/22.5 kN, middle-support moment -45 kNm and peak sagging
moment 25.3125 kNm. This is symmetric two-span software evidence only.

ETABS section shear-area modifiers were explicitly zero while all other
modifiers remained one. CSI defines zero shear area as suppressing transverse
shear deformation, so this authored test deliberately matches Euler-Bernoulli
kinematics; it is not a demonstration of native shear-flexible building parity.
See the [CSI analysis reference, printed page 116](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf#page=138)
and [modifier definitions](https://docs.csiamerica.com/help-files/etabs-api-2016/html/511bdadb-f147-812f-f69b-de6f6e723ca1.htm).
No interior displacement or torsion/3D claim was added.

One new instance/model and one analysis invocation were used. The known
post-save EDB/text-export getter inconsistency recurred; its predeclared single
exact-new-EDB reload restored identity with unchanged bytes and definition.
The requested case and ETABS internal `~LLRF` finished. Units and selection
were preserved/restored, both immutable test stages retained and only the
new instance closed. Owner copy/backup/baseline and all earlier benchmark EDBs
retained exact hash/size/mtime; owner lock, units, statuses and flags were exact.

Separately, an application-free replay verified 60 saved evidence files, the
153-beam/3,502-station saved-revision baseline, catalogue hashes and exact W3F
normalization. Explicit JSON rehydration was followed by complete serialized
value equality and canonical hash checks. This is a saved-data regression,
not a fresh Excel run, new force extraction, design comparison or calibration.
Required-calibration mode still blocks on the retained missing physical basis.

Next: a bounded saved-building capability/mapping assessment alongside
asymmetric/patterned-load benchmarks, without guessing effective supports.
Action-only comparisons must declare their reduced scope; neither this test
nor an unavailable building field is a reason to demand professional sign-off
before ordinary software development. W3I and construction approval stay held.

### Saved-building mapping assessment (2026-08-31 successor)

The [mapping receipt](../verification/etabs-w3h-building-mapping-evidence.json)
closes that bounded assessment. Both accepted manifests rehash (127 files),
and current public validators verify the complete saved baseline, catalogue,
definition, displacement and reaction identities. All 153 result sets and
3,502 signed station rows have unique IDs, complete components and exact member/
selection links. This is saved-byte evidence, not freshly queried application
state; no ETABS, Excel, solver, comparator or design operation ran.

The outcome-changing gaps are now explicit:

- Only one frame/three joints have a normalized foundation. One other frame
  has bounded raw definition evidence. Neither is a complete accepted reduced
  model; the broader force inventory must not imply broader physical coverage.
- The accepted combination has five ordered case factors, not two inferred
  from its label. Every contributing case/pattern and the nonzero self-weight
  multiplier must survive any future mapping. Direct frame loads alone do not
  prove complete area/slab/transferred loading.
- 132 of 153 beam result sets repeat an object-station coordinate. Preserve
  element identity, row identity and station side; never deduplicate or infer
  a nearest-station comparison from coordinates alone.
- All 153 beam sets have at least one exactly nonzero axial/minor-axis action.
  This is a coverage observation, not a code failure or recommended tolerance.
  W3E's explicit applicability bounds and face mapping cannot silently be zero
  or be fitted to these observed maxima. Pilot materials/detailing do not supply
  those criteria, serviceability scope or W3I families/scenarios/objectives.

The next bounded packet is **installed mapping-signature discovery**, not another
benchmark, analysis or blanket request for an engineer. Use installed metadata
to identify proved read-only analysis-element connectivity, area/load-transfer
and spring-inventory paths for the already-inspected target. Its external plan
freezes the information needs and static-only boundary. Only a later separately
bounded getter packet may read a copied model. If those sources cannot prove a
supported physical reduction, retain the exact hold. Do not fit supports/loads
from the reference actions or add settlement support just to obtain agreement.

Model-specific comparison still requires independently established mappings,
linear-response scope and predeclared criteria; W3I additionally requires its
complete screening basis. None is supplied by hashes or synthetic fixtures.
Actual-building L5 and W3I/K/L remain held, not permanently impossible.

For offline replay, use explicit JSON rehydration followed by exact complete
serialized-value equality and the public canonical validators. The inherited
`StrictPublicModel` before-validator exposes JSON arrays as Python lists before
strict tuple intake; a bare strict `model_validate_json` is not the accepted
replay path. This packet reuses the earlier replay's explicit `strict=False`
intake, rejects any changed serialized value and changes no library contract.
For open-workbook disk identity, a shared-read file handle can hash saved bytes
without closing/saving Excel; it does not prove unsaved workbook content.

### Installed mapping signatures (2026-08-31 successor)

The [static mapping receipt](../verification/etabs-w3h-mapping-signatures-evidence.json)
verifies forty selected operations against installed ETABS 23.3.1.4563 managed
metadata, the current generated COM-wrapper AST and forty installed help topics.
No COM instance was created and no model, workbook or application was operated.
The five installed files were freshly hashed; the wrapper is not assumed to be
byte-identical to its historical W3F generation. All parameter types, direction,
order and six defaults match. Four case-only parameter spellings are preserved;
use proved positional binding, not assumed cross-language keyword spellings.

The installed analysis-frame interface is `cLineElm`, reached from
`SapModel.LineElm`; there is no `cFrameElm`. `FrameObj.GetElm`, line/point/area
element getters and object spring/area-load getters exist. Their existence is
not complete semantic proof: installed help for the element getters omits
connectivity type-code meanings, numeric units and fixed-array lengths. Do not
infer these from similarly named object APIs or another CSI product/version.
`FrameObj.GetSupports` describes supporting objects, not mechanical restraint
or an isolated reduced system. Point spring property option 2 and area spring
future-release placeholders cannot become ordinary linear stiffness values.

The area-object load getters document pressure units, coordinate/direction and
one-/two-way distribution assignments. They do **not** establish the complete
slab-to-beam transferred action or prove all other load contributions absent.
Spring assignment CSI failure is unavailable evidence, never a zero spring.
Line and area spring properties use stiffness per length/area, unlike a point
spring; all preserve their own nonlinear options and units.

A documented alternative is `DatabaseTables.GetAvailableTables` followed by
`GetAllFieldsInTable`: exact keys, versions, descriptions and per-field unit
strings can be discovered without importing, editing or exporting model rows.
Table display selection/options are separate from result-selection flags and
must be guarded independently. No table key or field is presumed present yet.
`GetTableForDisplayArray` is row-major with an exact record/column product, but
has no row-limit argument: blank/All group requests all applicable objects. A
post-return cap is not a server-side extraction bound.

The next separate packet is therefore **read-only table catalogue/schema
discovery**, not another analysis or a trial numeric mesh decoder. Its external
`NEXT_PACKET.md` freezes the exact copied revision, full pre/post model and table
selection guards, at most 1000 catalogue entries and twelve schemas of at most
200 fields each. It reads zero frame/joint/area content and zero table data rows.
If actual schema descriptions cannot close the graph/load/spring meanings,
retain the exact unsupported-information hold. A later data read needs its own
proved keys, bounds and shape contract. Actual-building L5, W3I/K/L and all
professional/release claims remain held; software discovery needs no signature.

### Table metadata guard failure (2026-08-31 successor)

The [installed metadata receipt](../verification/etabs-w3h-table-metadata-evidence.json)
records the next packet's bounded stop. Exact copied-file identity, locked
state, present/database units, fifteen finished case statuses and all 77 result
flags passed before/after one existing-instance attachment. No visible dialog
appeared. Eleven saved-file identities and every earlier lane were preserved.

The first required table-display getter, `GetLoadCasesSelectedForDisplay`,
returned count 0, twelve null array entries and CSI code 1 for explicit in/out
placeholders `(0, [])`. The maintained decoder correctly failed closed. This
does not mean no selected cases or no available tables. Catalogue/schema calls
were NOT_REQUESTED after the failure, and no table data row was read. Table-
display preservation is NOT_PROVED; full model-guard preservation is proved.

The internal CSI/COM cause is unconfirmed. Successful model guards and exact
installed/runtime hashes do not establish whether the issue is marshaling,
table-provider behavior or another native condition. In particular, do not
label this trial-license denial, demand another analysis or recommend reinstall.
The installed comtypes code constructs omitted typed-null and explicit empty
SAFEARRAY parameters differently, but no causal comparison was executed.

Next is a separately frozen, static-first transport diagnosis of this same
getter, possibly through the installed managed interface. Preserve the exact
failed response; compare like input conditions or explicitly record any changed
placeholder variable. Do not retry the metadata campaign, skip selection guards,
change table/result selections, or export rows in that diagnostic. Actual-
building calibration and W3I/K/L remain held, not declared impossible.

### Transport-client guard failure (2026-08-31 successor)

The [transport receipt](../verification/etabs-w3h-table-transport-evidence.json)
records a different failure, before the table getter: one managed attachment
failed to bind the two-argument `LoadCases.GetNameList` guard. Postflight failed
at the same invocation. Zero managed/Python table calls or retries occurred.
The saved copy and eleven protected file identities are unchanged and the
visible model window has no blocking dialog, but full live model identity,
lock, units, case statuses and selections were **not freshly verified**.

Reflection shows a third optional enum argument whose default zero is unnamed.
PowerShell rejects a normal numeric enum-zero cast; explicit `Enum.ToObject`
works locally. However, a static stand-in with the exact default accepts both
omission and explicit zero, so the internal managed/COM binding cause remains
unconfirmed. This does not resolve or repeat the earlier CSI 1 table failure.
The initial offline proof covered only the table-call binder, not every guard.

The next packet must first exercise a complete fully typed compiled guard
client, all arguments explicit, including error/postflight/logger paths, without
ETABS. Freeze any new live comparison only after that whole-path proof and
fresh source/process/file/UI checks. Do not patch and rerun this frozen client,
infer full preservation from file hashes, or advance metadata/calibration.

### Typed-client and outer-launcher checkpoint (2026-08-31 successor)

The [typed-guard receipt](../verification/etabs-w3h-typed-guard-evidence.json)
records 45 compiled-client offline cases using actual installed interfaces,
explicit arguments and all 77 flags. These prove local wiring and error/logging/
postflight behavior, not installed COM compatibility.

The separately frozen launcher stopped **before attachment**. PowerShell JSON
parsing promoted its ISO process-start string to `DateTime`; comparing the
fresh string against that value falsely reported `Process replaced`. Exact
round-trip timestamps match. This is a confirmed outer-client type defect,
separate from the unconfirmed historical COM binding and CSI 1 failures.
Zero ETABS attachments/table calls, Python live calls or retries occurred.

The initial offline matrix omitted that outer launcher. A separate correction
preserves ISO strings with `-DateKind String` and adds 24 offline cases covering
outer guards/logger/file postflight plus the whole compiled path. Its live
mode is disabled for this closed packet. Reuse those components, but require
the next real-environment collector and launcher to pass offline through their
exact shared entrypoint before a new contract. Do not rerun any frozen attempt.

Eleven saved-file identities and 35 predecessor lanes are preserved; visible
pre/post UI has no blocking dialog. Complete fresh live model state and full
table-selection/options preservation remain NOT_PROVED. Only a separate
guarded managed success can make the matched Python observation eligible.
Actual-building W3H and W3I/K/L remain held.
