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
