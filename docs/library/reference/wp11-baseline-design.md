# WP11 supported native baseline beam design

**Type:** Reference | **Audience:** Developers | **Status:** Active |
**Importance:** High | **Created:** 2026-09-08 | **Last Updated:** 2026-10-02

`StructuralEngineering.Beam.BaselineDesignOperations` turns a validated WP10
snapshot and explicitly accepted engineering inputs into actual reinforcement
and complete-member check evidence. It runs without Excel, ETABS, file I/O or a
Python process. Excel exposes this strict operation through Design and the
independent provisional workflow through Review Beams.

## Persistent assumptions and provisional review

Start from [`BeamReviewFields.All`](../../../CSharp/src/StructuralEngineering.Beam/BeamReviewFields.cs)
for the complete field/unit/consumer/fallback matrix. Use the maintained
[`demo-beam-preset.json`](../../planning/xll-product/demo-beam-preset.json)
through `BeamReviewPresetReader.Parse`; hosts supply its text so the native
layer remains free of file I/O.

```csharp
var preset = BeamReviewPresetReader.Parse(presetJson);
var resolved = BeamReviewResolver.Resolve(snapshot, memberIds, preset, savedLedger);
var review = BeamReviewOperations.Review(snapshot, resolved,
    previous: previousReview, cancellationToken: cancellationToken);
// Preserve the whole ledger: entered text, effective values, scope, origin and revisions.
var edits = BeamReviewResolver.ApplyEdit(resolved.Ledger.Edits,
    BeamReviewResolver.Edit("design.cover", BeamInputScope.Project, "", null, "40", 1));
var changed = BeamReviewResolver.Resolve(snapshot, memberIds, preset, resolved.Ledger, edits);
```

Use a monotonically increasing edit sequence. Member/material/story/span/selection
edits require `BeamReviewResolver.ModelBinding(snapshot)`; project preferences
can cross models. Explicit edits equal to defaults remain overrides. Invalid or
formula text stays visible with its last valid/source/preset fallback. Equal
priority conflicting scopes retain both alternatives and an explicit fallback.

`BaselineDesignOperations.PreviewCore` returns the distinct
`BeamCorePreviewResult`: actual bars and independent checks, without a complete
member result. Required fire and missing service evidence stay unavailable;
known unsupported actions stay unchanged. `BeamReviewOperations.Review` accounts
for every selected member and every stage, even when another member fails.
`WorkflowComplete` means the review finished, not that the beam is qualified.
`Design`, `DesignMember` and `BaselineReplay` retain the strict contract below.

The coordinator reuses structural evidence for rate-only edits. Supply compatible
`BeamReviewQuantityEvidence` to price existing measured quantities through
`BeamReviewCostProjection`; structural/member/detail identities must match.
The optional named cost example is a separate teaching basis, never a member
takeoff. Optional `BeamReviewExamples.Owned` accepts only the exact WP11 fixture
and appears separately from source results. Analysis-affecting section alternatives
remain unverified until copied-model reanalysis.

Excel commands, shared input views, persistence and the acceptance procedure are
in the [Excel guide](../excel/README.md). The
[U1–U5/R01–R12 plan](../../planning/xll-product/etabs-design-workflow.md)
owns installed qualification and the next work; the native APIs alone make no
live acquisition, reanalysis or issued-report claim.

## Native contract and call path

### Offline member intent and input readiness (LIB-2 / LNV-01)

`BeamReadinessOperations` binds the existing review ledger to the existing
`is456-ordinary-rectangular-simple-span-baseline-v1` input mapper. It performs
input admission only: `Engineering=NotEvaluated`, `Approval=Unreviewed`, and
physical/material/current installed qualification remains **HOLD**. A ready
input is not a completed design or an engineering approval.

```csharp
// Supply member.intent=OrdinaryBeam, member.support and selection.role through
// explicit scoped BeamReviewResolver.Edit records. Unknown intent stays Unknown.
var resolved = BeamReviewResolver.Resolve(snapshot, memberIds, preset,
    savedLedger, edits);
// Optional: existing BaselineProjectInputs, separately and explicitly accepted.
// Never turn the resolver's provisional ValuesAccepted=false into true implicitly.
var acceptance = new BeamReadinessAcceptance(resolved.Ledger.Revision, acceptedInputs);
var request = new BeamReadinessRequest("my-retained-cohort/v1", memberIds,
    snapshot, preset, savedLedger, edits, acceptance);
var readiness = BeamReadinessOperations.Assess(request);
var portableJson = BeamReadinessOperations.Serialize(readiness);
var replay = BeamReadinessOperations.Parse(portableJson); // reruns native owners
var current = BeamReadinessOperations.IsCurrent(replay, currentRequest);
```

For a directly runnable retained input, load the shipped conformance document.
Its stored engine identity includes runtime/platform/build, so `Parse` rightly
requires the original engine. `ImportRequest` imports strict, identity-checked
inputs without accepting its stored readiness; `Assess` uses the current engine:

```csharp
using var fixture = File.OpenRead(
    "contracts/structural-engineering/conformance/beam-readiness-v1.gz");
using var gzip = new System.IO.Compression.GZipStream(fixture,
    System.IO.Compression.CompressionMode.Decompress);
using var payload = new MemoryStream();
gzip.CopyTo(payload);
var imported = BeamReadinessOperations.ImportRequest(payload.ToArray());
var preview = BeamReadinessOperations.Assess(imported with { Acceptance = null });
// This named owned fixture already has explicit accepted project inputs.
// After reviewing their match to the current ledger, rebind that existing basis:
var rebound = imported with { Acceptance = imported.Acceptance! with {
    LedgerRevision = preview.Ledger!.Revision } };
var ready = BeamReadinessOperations.Assess(rebound);
var changedEdits = BeamReviewResolver.ApplyEdit(rebound.Edits,
    BeamReviewResolver.Edit("member.support", BeamInputScope.Member,
        rebound.MemberIds[0], BeamReviewResolver.ModelBinding(rebound.Snapshot!),
        "Continuous", 1000));
var changed = BeamReadinessOperations.Assess(rebound with { Edits = changedEdits });
// First member is Unsupported; peers remain accounted. The old result is stale.
```

The same edit API accepts `member.intent` (`OrdinaryBeam`, `Other`, `Unknown`)
or `selection.role` at `BeamInputScope.Selection` with the source selection ID
(`Uls`, `SlsTotal`, `SlsSustained`). New values must be reconciled with accepted
inputs before rebinding; changing a revision label alone cannot bypass the
effective-value comparison. File I/O in this example belongs to the caller.

Pass `Acceptance=null` to inspect the provisional scenario, or `Snapshot=null`
to account for missing retained input. The accepted basis must bind the exact
resolved ledger revision and match its material, section, context, catalogue and
action-role values. Evidence/revision labels remain independently recorded in
the request; they are not silently overwritten in the supplied input. A changed
ledger requires explicit reconciliation and rebinding. A change to any accepted
project input or its provenance also changes the request identity, even when
the resolved numeric values are unchanged. `IsCurrent` compares the full current
request, not a snapshot timestamp or the ledger revision alone.

Every distinct requested ID receives an ordered outcome, including a member
absent from the snapshot. The existing `BaselineRunState` values have these
readiness meanings:

| State | Meaning in this input-only operation |
|---|---|
| `Complete`, `ReadyForSelectedProfile=true` | The existing strict mapper admits the supplied basis. |
| `Incomplete` | Provisional assumptions or intent remain; review may continue. |
| `NeedsInput` | Missing member/source, conflicting entry or mismatched accepted basis. |
| `Unsupported` | The existing profile excludes the source action, geometry or intent. |
| `Failed` | Invalid source evidence or a member projection failure; peers remain accounted. |
| `Stale` | The retained source's recorded offline basis is stale. |

The original validated snapshot travels with the request: source identities and
result epoch, units, axes/physical faces, sections/materials, station side,
case/combination/step, action basis, same-row vectors and getter provenance remain
unchanged. Roles classify existing selections; they neither create combinations
nor turn component envelopes into concurrent vectors. Known profile guards,
including nonzero axial/minor-axis/torsional exclusion, are unchanged.

Ledger fields expose `source_state`, `entered_state` and effective `state` beside
their original text and origin. Zero, absence, blank input, source/supplied values,
derived geometry, assumptions, invalid last-valid fallback and conflicts remain
distinguishable. `member.intent` defaults to `Unknown`; old saved ledgers and
presets migrate through the same resolver. Source orientation and zero mass or
weight modifiers never establish physical purpose.

Python exposes **inspection and binding validation** of the native-produced
document through `structural_lib.beam_readiness`. It does not resolve changed
inputs or run the native baseline engineering engine:

```python
from structural_lib.beam_readiness import (
    parse_beam_readiness_json, canonical_beam_readiness_json,
    beam_readiness_freshness,
)

document = parse_beam_readiness_json(native_json)
same_json = canonical_beam_readiness_json(document)
freshness = beam_readiness_freshness(
    document, current_snapshot=current_snapshot,
    current_ledger_revision=current_native_ledger_revision,
    current_request_id=current_native_request_id,
    current_engine_identity=current_native_engine_identity,
)
```

The parser rejects unknown/duplicate fields, lossy projections, altered request
or document hashes, incomplete member accounting and invalid snapshot claims.
Hashes prove integrity, not who executed the native engine. Current bindings
must come from the caller's current native request; stored readiness alone
cannot establish currentness. Editing inputs requires another native `Assess`.
The [portable schema](../../../contracts/structural-engineering/schemas/beam-readiness.schema.json)
and [native-produced conformance document](../../../contracts/structural-engineering/conformance/beam-readiness-v1.gz)
retain the complete exchange. The repository fixture is gzip-compressed using
the existing retained-fixture pattern; its decompressed JSON has one final
newline. Canonical payload hashes exclude that terminator and compression bytes.
Python callers can use `gzip.decompress(path.read_bytes())` before parsing. Compact
[negative-case deltas](../../../contracts/structural-engineering/conformance/beam-readiness-cases-v1.json)
reconstruct native provisional, missing, unsupported and failed documents against
the same base without copying its snapshot. The snapshot uses the existing AO16 canonical JSON
owner; existing WP01–WP10 operations and numerical results are unchanged.

The named cohort is `lnv01-wp11-owned-rectangular-v1`: `member:PF9_B0001`,
`member:PF9_B0002`, `member:PF9_B0003` in the retained WP11 `.sasnap` fixture.
Its file SHA-256 is
`cd04be9d9a7ec41db0714f8259fb17bba14d19e73981e71241149da69d0b78f0` and snapshot
SHA-256 is `9ced40204f6db621b4b22c7a8a755d1a77ec77c69aaf9a4d76dc12316a72bf84`.
`BeamReadinessTests.ReadyRequest` supplies the exact ledger edits matching
`BeamReviewExamples.Owned`; it includes three explicitly captured ULS/total
SLS/sustained SLS selections. Negative scenarios retain separate identities.
The external 153-member building snapshot remains optional negative evidence,
not an additional admitted cohort. C0a's three noncollinear chains and five
incomplete envelopes remain restricted, with physical support/member role
qualification still absent. No new ETABS/Excel action or qualification follows.

### Existing complete design operation

The public records are `BaselineProjectInputs`, `BaselineDesignOptions`,
`BaselineBatchDesignResult` and `BaselineReplayRequest` in
`StructuralEngineering.Contracts`. These are native application contracts;
they do not introduce a Python API, a new shared operation manifest, or a
replacement for the existing WP06/WP10 semantic contracts.

```csharp
// snapshot: AnalysisSnapshot validated by the maintained WP10 authority
// inputs: explicit accepted project/material/catalogue/member/action bindings
// memberIds: source member IDs selected by the caller
var request = BaselineReplay.Request(snapshot, inputs, memberIds,
    new BaselineDesignOptions(MaximumCandidates: 1000));
var result = BaselineReplay.Run(request, snapshot, cancellationToken);
var savedRequestBytes = BaselineReplay.Serialize(request);
// A host owns external persistence and later supplies the exact snapshot:
var replay = BaselineReplay.Run(BaselineReplay.Parse(savedRequestBytes), snapshot);
```

`Design` additionally accepts member progress; `DesignMember` uses the identical
mapper and evaluator. The batch constructs one validated snapshot index.
Results account for every requested member independently. A caller supplies
stable inputs for the duration of a call; a background host freezes the request
before dispatch. JSON replay rejects unknown fields, omitted required
constructor arguments and numeric enum values.

The dependency is Beam → Analysis/IS456/Reinforcement/Construction/Core/Contracts. Analysis
does not import Beam. Native IS456 producers remain pure calculations. The
existing member aggregator receives genuine leaf results; equal station
calculations retain every scope leaf and bind each unique calculation once.

## Supported engineering profile

### Next-version admission decision: LIB-3 / LNV-02

The 3 October 2026 next-version continuation selects the completed LIB-2
input/readiness workflow and its public delivery examples. The conditional
LIB-4 complete concurrent M3/V2/T extension is **HOLD**. The proposed cohort is
one supplied ordinary, non-seismic rectangular member with aligned single-layer
longitudinal bars and actual closed links, zero P/V3/M2, unchanged stiffness,
no laps or cutoffs, and explicit signed same-row static ULS and SLS actions.
No nonzero-torsion range, support condition, numerical tolerance or new
engineering profile is admitted by this decision.

The following matrix traces the essential obligations to existing owners.
An available operation is reusable machinery; it is not full-profile evidence.

| Required obligation | Existing owner | Evidence decision for the proposed torsion member |
|---|---|---|
| Concurrent signed actions, axes, units and row provenance | WP10 snapshot, `BaselineInputMapper`, LIB-2 ledger/readiness | Existing transport is qualified. The baseline mapper deliberately excludes nonzero T. |
| Both-face flexure and torsion-induced opposite-face demand | AO01 flexure and AO08 `BeamOperations.CheckTorsion`; Python `beam.check_torsion` | Component implementation exists. A complete independently derived profile case set is not accepted. |
| Equivalent shear, concrete maximum shear and supplied links | AO08; `BaselineStrengthDetailChecks` | Reuse component evidence only within its stated domain. No blanket baseline-guard removal. |
| Corner/perimeter bars, closed links and consistent effective geometry | WP01/WP05 arrangement, WP06 paths; existing torsion-detailing packet | The authored torsion-detailing vector covers a bounded component arrangement. It does not qualify the complete proposed member. |
| Torsional restraint, equilibrium/compatibility basis and load path | Accepted engineering member context and source analysis evidence | **Missing:** the current context records flexural simple/continuous support and lateral restraints, without a qualified torsional-restraint/load-path contract. |
| Service torsion with bending/shear and both relevant faces | WP04 serviceability and `BaselineServiceChecks` | **Missing:** the current producer uses signed M3 for the flexural Annex F section and Figure 4 screening; it has no admitted combined-torsion SLS method/reference. |
| Continuity, end development and torsion reinforcement anchorage | AO11/AO12, WP05 and `BaselineStrengthDetailChecks` | Existing flexural support/development and link templates are controls. Torsion-specific physical support correspondence remains unaccepted. |
| Cover, durability, material eligibility, fit and lateral stability | WP01/WP05 and accepted member/material context | Preserve every existing physical/material HOLD and case restriction. |
| Fire and seismic scope | Fixed required-leaf profile and accepted context | Explicit ordinary/non-seismic and no-required-fire-rating decisions remain necessary. |
| Full-length bars, stock, marks, counts, cut lengths, BBS and quantities | WP06 construction paths, WP07 construction/BBS owners | Existing outputs are reusable only after all member obligations qualify on the same reinforcement revision. |
| Completeness, freshness, approval and calculation record | WP06 member contract, PF4 semantics, WP08 reporting | Missing obligations must remain draft/held; renderers cannot grant approval. |

The accepted [torsion-detailing component record](../../verification/etabs-w3-torsion-detailing-evidence.json)
retains its authored 300 by 500 mm, 3 m, M/V/T vector, stated corner geometry,
single-layer restrictions and serviceability HOLD. The
[ordinary and multilayer member references](../../planning/library-usability-improvement.md#complete-beam-implementation-and-independent-evidence)
retain their zero-torsion scope. Python/.NET conformance is transport/semantic
evidence with disclosed shared rules, rather than an independent engineering
reference. Sourcebook/StructProof leads have no accepted, exact complete-profile
export bound to this decision.

Resume LIB-4 only after the engineering-context owner supplies the exact torsional
restraint and source load-path correspondence, the serviceability owner selects
and substantiates the combined-action method, and the evidence owner accepts
independently derived governing, opposite-face, boundary, failure and unsupported
cases. Each case needs source/edition/amendment identity, signed same-row actions,
units/axes, actual bar/link coordinates, expected outputs, justified tolerances
and shared-lineage disclosure. Then freeze a separately named profile and its
complete required-leaf set before implementation. These missing dependencies
are an evidence HOLD, not a demonstrated defect in the current supported baseline.

### Public readiness example and migration to 0.25.0: LIB-5 / LNV-04

[The public example](../../../Python/examples/member_readiness_workflow.py)
uses installed `structural_lib.beam_readiness` and snapshot APIs without changing
Python's import path. From the repository root, using your chosen environment:

Install the exact version after the release ledger confirms publication; the
prepared source candidate can be exercised with the repository's bound runtime.

```bash
python3 -m pip install structural-lib-is456==0.25.0
python3 Python/examples/member_readiness_workflow.py \
  contracts/structural-engineering/conformance/beam-readiness-v1.gz
```

The three-member frozen control reports every requested member, its recorded
ready state, input/policy/engine identities, `freshness=unbound`,
`engineering=not_evaluated` and `approval=unreviewed`. This command inspects
stored evidence; it does not establish that an actual project is current.
The existing native negative-case deltas cover provisional, missing, unsupported
and failed outcomes. The example also accepts native readiness JSON directly.

For currentness, pass **all four** bindings obtained from the current native
owner: `--current-snapshot <snapshot.json>`, `--current-ledger-revision <revision>`,
`--current-request-id <identity>` and `--current-engine-identity <identity>`.
The snapshot file must be the current validated source, independently of the
stored readiness document. A changed binding reports stale and exits 2;
altered evidence exits 1; partial binding input exits 2. Inspection without
current bindings exits 0 but does not grant readiness for current use.

Migration keeps all 13 existing family-facade journeys and ordinary numerical
APIs. Readiness is a new `beam-readiness/v1` contract. Reuse existing ledger
edits through the native resolver, supply explicit member intent, support and
ULS/SLS roles, reconcile accepted inputs to the resulting ledger revision, then
run native `Assess` again. Do not relabel an old result current or fabricate a
new native readiness claim in Python. The identical freshness enum remains
available from prior public beam imports and now has its neutral owner in Core.
Native engine changes require replay and new current engine/request bindings.
No new HTTP/CLI entry point, installed-host qualification or support expansion
is selected. The new example's installed-package acceptance covers unbound
inspection, current/stale bindings, rejected evidence and missing bindings;
existing ordinary/multilayer examples and independent reference identities are reused.

The frozen profile is an ordinary, horizontal, simply supported, prismatic
rectangular beam at its captured dimensions, with normal positive-local-2 top
mapping, direct section assignment and zero source end offsets. Accepted
support centres coincide with the source ends; the conservative design span is
centre-to-centre and at most 10 m. Clear-span/depth must exceed 2 and total
depth must not exceed 750 mm. The qualified concrete grades are M20–M40 in
5 N/mm² steps; steel domains are explicit in the mapper.

Every captured row retains its signed concurrent P/V2/V3/T/M2/M3, source row,
case, step, station and evidence identity. Required axial, minor-axis and
torsion components above the declared 1e-12 numerical-zero tolerance are
Unsupported. The original values are never replaced with zero. Every selection
has an explicit ULS, total-SLS or sustained-SLS role, and every role has complete
captured station coverage. No extrema from unrelated cases are combined.

| Input | Responsible source and missing behavior |
|---|---|
| Section/material IDs, dimensions, axes, signed rows | Validated WP10 snapshot; invalid source cannot qualify |
| fck, longitudinal/link fy, steel modulus | Explicit mapping by captured material ID; no name/modulus inference |
| Support faces/centres, anchorage bounds, physical span | Accepted member context with evidence revision; adjacency alone is insufficient |
| Cover, aggregate, exposure, lateral restraint locations | Accepted member context; actual bars/links are checked against it |
| Fire basis | Explicit referenced project decision; unknown is Needs Input, required rating is Unsupported in this profile |
| Screening permission and harmful cracking classification | Explicit engineering context; no caller-supplied pass result |
| Bar/link sizes, spacing, counts/layers and stock lengths | Finite versioned catalogue with hard limits |
| Accepted values and professional approval | Separate project facts; calculation acceptance does not issue a design |

## Actual arrangement and required checks

The deterministic search holds the captured section fixed. It considers equal
diameter bars within each face, aligned rows with at least two bars per row,
full-length straight bars with no optional curtailment or splice, and one
uniform closed two-leg link zone. Stock and available anchorage must fit the
actual longitudinal paths. First-row bar centres accommodate the rounded
link bend; inner layers clear the selected hook tails and ordinary spacing.
Actual area-weighted face depths drive every affected calculation.

The required set is frozen before trials: station flexure/shear/torsion,
arrangement, both support and full-development anchorage, stirrup anchorage,
full-span continuity/stock, longitudinal paths, durability, lateral stability,
span deflection screening, and each service-row crack check. Ordinary seismic
and explicit no-fire-rating decisions retain genuine Not Applicable leaves.
They cannot be disabled by callers. Failed strength/fit trials are rejected
before spending time on their SLS calculations.

The closed link uses an inspectable 135°/6φ standard end-anchorage template,
internal bend radius 2φ and actual projected tangent tails. All longitudinal
bars must fit the rounded cage and clear both tails; the tails must fit the
section envelope and terminate inside the cage. This qualifies the bounded
anchorage template, not a fabrication BBS or issued placing drawing.

Deflection uses the existing permitted span/depth screening operation. Its
Figure 4 producer derives service steel stress from required/provided steel
and selects a documented conservative lower envelope of the 290 N/mm² curve;
compression/flange enhancement is not credited. It does not calculate a
displacement or certify a project requiring a different method.

Crack inputs use actual tension layers in the cracked transformed section and
the Annex F short/sustained strain expression. Opposite-face compression steel
is not credited. When the tension-stiffening subtraction is negative, the
producer uses the fully cracked elastic surface strain as a conservative upper
bound, explicitly labelled as an engineering-model inference. Edge and
inter-bar governing surface points are evaluated; the worst genuine check is
retained with the full derivation list and source row.

## Outcomes, currentness and limits

Complete requires the final arrangement and every required result to qualify
through the existing WP06 member contract. Needs Input, Unsupported, Stale,
Cancelled, budget-limited Incomplete and an exhausted No Feasible Arrangement
remain distinct. The latter concerns only this finite catalogue and layout
policy. It does not prove a beam cannot be designed using another allowed
domain or section. A failed trial remains inspectable in the retained result.

Effective identities include the source snapshot, accepted project/material/
member/catalogue/action basis and actual reinforcement. Engine identity also
binds the semantic revision, native module identities and runtime/platform.
Rebuilt modules or changed dependencies make earlier results stale. Replay
needs the exact recorded snapshot and engine; it never claims the live ETABS
model is unchanged. Hosts retain historical request/results externally.

## Qualification and source evidence

The owned production capture contains three beams and 153 real ETABS action
rows, snapshot SHA-256
`9ced40204f6db621b4b22c7a8a755d1a77ec77c69aaf9a4d76dc12316a72bf84`.
The safely retained fixture is
`CSharp/tests/StructuralEngineering.Tests/Fixtures/wp11-owned-snapshot.sasnap`.
Its explicit accepted test basis is `BaselineDesignTests.FixtureInputs`;
it is a nonbuilding calculation fixture, not a default for a user's model.
The separate proprietary 153-beam building capture remains external and proves
that known nonzero axial demand stays Unsupported before supplemental inputs.

Independent scalar anchors cover required steel, transformed-section neutral
axis/inertia/stress/strain, geometric hook coordinates, source loads/reactions,
stock/coverage, durability and lateral limits. The controlled IS456 PDF has
SHA-256 `6ec8f9033bc521420f2f550123edb6f0f444d9d3b7033a87b1b7ec569c143f8d`;
normalized records identify printed pages and methods without copied prose or
page images. Existing WP01–WP06 conformance evidence is reused for their
unchanged leaf formulas.

From `CSharp`, locked restore/build and portable tests use the commands in its
README. Focused xUnit executable selection uses `-class
StructuralEngineering.Tests.Baseline*`; set `WP11_BUILDING_SNAPSHOT` to the
external retained building file when requiring zero skipped reference tests.
The acceptance contract is
[wp11-baseline-design-acceptance.json](../../verification/wp11-baseline-design-acceptance.json).
Installed Excel, optimization, copied-model updates, overnight operation,
issued reports and final performance certification remain separate gates.
