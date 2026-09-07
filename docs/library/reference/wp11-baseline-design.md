# WP11 supported native baseline beam design

**Type:** Reference | **Audience:** Developers | **Status:** Active |
**Importance:** High | **Created:** 2026-09-08 | **Last Updated:** 2026-09-08

`StructuralEngineering.Beam.BaselineDesignOperations` turns a validated WP10
snapshot and explicitly accepted engineering inputs into actual reinforcement
and complete-member check evidence. It runs without Excel, ETABS, file I/O or a
Python process. Excel integration is the separate successor milestone B.

## Native contract and call path

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

The dependency is Beam → Analysis/IS456/Reinforcement/Core/Contracts. Analysis
does not import Beam. Native IS456 producers remain pure calculations. The
existing member aggregator receives genuine leaf results; equal station
calculations retain every scope leaf and bind each unique calculation once.

## Supported engineering profile

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
