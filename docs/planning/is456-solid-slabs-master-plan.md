---
task: IS456-SLAB-001
title: IS 456 Solid Slabs Expansion Master Plan
status: active
owner: Main Agent and repository owner
created: 2026-08-10
last_updated: 2026-08-11
doc_type: spec
baseline_commit: a0e115e17009cc14b3d883e3c291d47c32f7ca4e
branch: codex/is456-slabs-plan
implementation_started: true
current_wave: implementation_complete
flat_slab_status: separate_owner_and_qualified_engineer_approval_required
---

**Type:** Master Plan and Implementation Packet
**Audience:** Product owner, structural-math, library, API, frontend, reviewer,
tester, and qualified structural-engineering reviewer
**Status:** S0-S13 implemented and verified; public-distribution permission passed; qualified-review gate remains
**Importance:** Critical
**Created:** 2026-08-10
**Last Updated:** 2026-08-11

---

# IS456-SLAB-001 — IS 456 Solid Slabs Expansion Master Plan

## 1. Executive decision

The next element program will complete a useful, evidence-backed solid-slab
workflow under IS 456 without pretending to solve every slab system.

The product outcome is:

```text
Define panel and supports
  -> validate the approved analysis method
  -> obtain auditable design actions
  -> design/check reinforcement by region and direction
  -> check detailing, deflection boundary, and one-way shear
  -> review explicit HOLD items
  -> save/export a calculation passport
```

The program covers:

1. simply supported and coefficient-method continuous one-way solid slabs;
2. common beam/wall-supported two-way rectangular panel conditions;
3. coefficient selection with provenance, exact bounds, and no silent fallback;
4. middle/edge strip distribution and corner torsion reinforcement;
5. main detailing, serviceability, and ordinary slab one-way-shear checks; and
6. Python, FastAPI, React, saved-result, and evidence surfaces for the same
   supported cases.

Flat slabs remain a separately approved extension. This program does not
introduce column strips, drops, column heads, direct-design/equivalent-frame
methods, unbalanced column moment transfer, or flat-slab punching design.

Packet S0 froze the controlled source identity, coefficient data policy,
support-case identities, interpolation decision, and benchmark ledger before
calculation work began. The 2026-08-10 owner decision authorized direct
implementation of all IS-code content required by the approved slab scope. On
2026-08-11 the owner confirmed source/licensing permission for public
distribution of that approved-scope normalized data; the release tooling now
validates the canonical decision record fail closed.

## 2. Why this is an extension, not a new slab engine

The repository already contains a deliberately bounded slab foundation:

| Layer | Current accepted behavior | Important limitation |
|---|---|---|
| Types/classification | Solid rectangular geometry; effective spans normalized; `Ly/Lx > 2` one-way and `<= 2` two-way | Axis-neutral normalization cannot safely carry physical edge topology |
| One-way calculation | Simply supported, uniformly loaded strip flexure | No continuity, load-pattern analysis, or slab shear |
| One-way detailing | Minimum steel, supplied bar diameter/spacing, and basic `Lx/d` review boundary | No modification-factor calculation, direct deflection, cracking, or schedule zones |
| Two-way calculation | One interior, four-edge-continuous flexure case using externally accepted coefficients | No built-in coefficients, edge/corner cases, strips, torsion, shear, or serviceability |
| Python facade | `design_one_way_slab_is456()` and bounded `design_two_way_slab_is456()` | Public names must retain compatibility |
| FastAPI | `POST /api/v1/design/slab/one-way` | No continuous one-way or two-way consumer |
| React | No dedicated slab workflow | No panel/support input, review surface, or slab passport |

The implementation must extend these contracts. It must not create a parallel
`slabs.py`, duplicate rectangular flexure math, or reinterpret the current
two-way route as a complete design.

## 3. Scope contract

### 3.1 Supported physical system

The target physical system is a cast-in-place, solid, rectangular reinforced
concrete building slab panel supported by beams or walls, with orthogonal spans
and substantially uniformly distributed gravity loading.

Inputs remain explicit:

- effective spans and slab dimensions: mm;
- strip width: mm, normally 1,000 mm;
- characteristic or factored area loads: kN/m2, never mixed in one field;
- line loads: kN/m;
- design actions: kN m/m and kN/m;
- concrete and steel strengths: N/mm2;
- reinforcement areas: mm2/m;
- bar diameters and spacing: mm; and
- shear stresses: N/mm2.

### 3.2 Initial one-way supported cases

1. **Simply supported strip:** one-way solid slab, UDL, caller-supplied
   effective span, existing `wL2/8` flexure path, completed with strict
   serviceability and one-way shear results.
2. **Continuous strip:** uniform cross-section, substantially UDL, at least
   three spans, and span variation inside the Clause 22.5 coefficient-method
   boundary. The first slice uses one approved loading arrangement and explicit
   factored permanent/imposed components. More general patterned loading waits
   for its own accepted benchmark.

If the coefficient method is inapplicable, the library returns an unsupported
analysis-method result. It does not approximate an elastic analysis.

### 3.3 Initial two-way supported cases

The two-way program starts with five practical support topologies:

1. interior panel, all four edges continuous, corners restrained;
2. exterior edge panel, one edge discontinuous, corners restrained where
   required;
3. corner panel, two adjacent edges discontinuous, corners restrained;
4. all four edges discontinuous with corners prevented from lifting; and
5. simply supported on four edges with corners free to lift and no torsion
   resistance assumed.

After the corner-panel vertical slice is accepted, the coefficient registry may
be completed for the remaining restrained-panel cases represented by the
approved source. Case identity must be derived from physical edge conditions;
users must not select a table row that contradicts the entered edges.

### 3.4 Explicit non-goals

The following are outside IS456-SLAB-001:

- flat slabs, drops, column heads, column strips, equivalent-frame/direct-design
  methods, and slab-column moment transfer;
- flat-slab or column-supported punching shear;
- slabs with openings, re-entrant corners, irregular/skew/circular geometry,
  non-orthogonal supports, or varying thickness;
- ribbed, waffle, filler, precast, composite, prestressed, post-tensioned,
  bridge/deck, raft, footing, stair, ramp, or shell behavior;
- concentrated/line loads, heavy equipment, vehicle loads, or local load
  dispersion;
- seismic diaphragm analysis, membrane forces, temperature-gradient analysis,
  progressive collapse, fire design, vibration, durability-life prediction,
  or construction-stage/propping analysis;
- finite-element, yield-line, grillage, elastic plate, or strip-analysis solver;
- automatic load combinations, imposed-load reduction, load pattern generation,
  or analysis-envelope generation outside the approved coefficient method;
- automatic bar optimization or fabrication-ready BBS/DXF in the first release;
  and
- any wording that implies qualified design approval.

## 4. Authority, research, and source policy

### 4.1 Governing authority

The primary controlled calculation authority is the repository's protected
IS 456:2000 source consolidated through Amendment 5 plus the official Amendment
6 review already identified in
`docs/verification/is456-library-first-evidence.md`.

Current public authority checks performed on 2026-08-10 found:

- the BIS record lists IS 456:2000 as active, reaffirmed in 2021, with six
  amendments; and
- official Amendment 6 changes cement/material provisions and must still be
  recorded in the slab source review as having no slab-route change before
  implementation relies on that conclusion.

The controlled standard governs. Secondary worked examples help establish
independent arithmetic and implementation interpretation, but cannot override
the standard.

### 4.2 Research references

| Reference | Planned use | Authority limit |
|---|---|---|
| [BIS IS 456 record](https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?Standard_Number=IS%20456&id=11286) | Active/reaffirmed/amendment status | Metadata, not clause text |
| [BIS Amendment 6](https://www.services.bis.gov.in/tmp/CED19013804_03062024_1.pdf) | Current amendment review | Must be checked against controlled consolidated source |
| [IIT Kharagpur/NPTEL Lesson 18 — one-way slabs](https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m8l18.pdf) | Continuous coefficient-method conditions, shear/detailing interpretation, independent example | Secondary educational source |
| [IIT Kharagpur/NPTEL Lesson 19 — two-way slabs](https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m8l19.pdf) | Strip/corner interpretation and two-adjacent-edge benchmark | Secondary educational source |
| [IIT Kharagpur/NPTEL Lesson 30 — yield-line analysis](https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m12l30.pdf) | Confirms coefficient method is not a universal analysis solver | Background only |
| [BIS SP 16 record](https://standardsbis.bsbedge.com/search_redirect.aspx?id=17706) | Legacy comparison only | BIS lists SP 16:1980 as withdrawn; it is not current normative authority |

### 4.3 Coefficient data implementation and distribution policy

On 2026-08-10 the owner authorized direct implementation of any IS code content
needed by an approved feature scope, including formulas, normalized tables,
limits, figure-derived values, lookup, and interpolation. On 2026-08-11 the
owner confirmed source/licensing permission for public distribution of that
approved-scope normalized data. This gate is passed and is not a question for
later agents to repeat unless the owner explicitly changes the decision. The
canonical record is
[`is456-public-distribution-permission.json`](../verification/is456-public-distribution-permission.json).
This slab program therefore separates calculation architecture, provenance,
protected-source exclusion, standing distribution permission, and per-release
execution authority:

1. `CoefficientSourceRecord` identifies standard, edition/amendments, table,
   support case, aspect ratio, extraction reviewer, checksum, and packaging
   permission.
2. The existing external-coefficient route remains available and explicitly
   reports that the library did not verify the coefficient truth.
3. Built-in normalized lookup and interpolation are implementation scope now;
   agents must not request this permission again.
4. Protected screenshots, clause prose, and unrelated standard content must not
   enter source, tests, docs, package data, logs, or generated indexes.
5. Tests cover table points, interpolation boundaries, and accepted benchmarks
   without reproducing protected prose.
6. Release preflight, candidate verification, and publish CI fail closed unless
   the canonical public-distribution permission record remains valid. A tag or
   publication still requires separate owner authorization for that release.

### 4.4 SP 16 treatment

SP 16 examples may be retained as historical comparison evidence, but no new
calculation is justified solely by SP 16. New steel-area benchmarks must also be
computed from the accepted IS 456 stress-block equation or another current,
owner-approved independent calculation. A mismatch between direct computation
and a legacy aid is a stop condition, not a reason to loosen tolerance.

## 5. Engineering domain model

### 5.1 Do not reuse axis-neutral geometry for support topology

`SolidRectangularSlabGeometry` safely normalizes two spans for classification.
That behavior becomes unsafe when an edge condition is attached: swapping spans
would also have to rotate four physical edges and every reinforcement direction.

Add a package-local oriented panel contract, tentatively:

```python
@dataclass(frozen=True)
class OrientedSolidSlabPanelGeometry:
    lx_effective_mm: float
    ly_effective_mm: float
    thickness_mm: float
    d_x_mm: float
    d_y_mm: float
    strip_width_mm: float = 1000.0
```

Contract:

- `0 < lx <= ly`, with no silent swap;
- `1 <= ly/lx <= 2` for the Annex D two-way route;
- `0 < d_y <= d_x < thickness` only if the source-approved bar-layer
  convention confirms that ordering; otherwise both depths are independently
  validated and no relative ordering is assumed;
- physical edges remain `x_min`, `x_max`, `y_min`, and `y_max`; and
- the old axis-neutral geometry remains supported for classification and the
  existing one-way route.

### 5.2 Support topology

Use explicit physical inputs:

```python
class SlabEdgeCondition(StrEnum):
    CONTINUOUS = "continuous"
    DISCONTINUOUS = "discontinuous"

@dataclass(frozen=True)
class TwoWaySlabSupportTopology:
    x_min: SlabEdgeCondition
    x_max: SlabEdgeCondition
    y_min: SlabEdgeCondition
    y_max: SlabEdgeCondition
    corners_prevented_from_lifting: bool
```

The topology resolver returns a canonical support-case ID, rotations/reflections
used to match the controlled source, required coefficient family, and a corner
classification for all four corners. It rejects impossible combinations, such
as requesting the unrestrained simply supported coefficient method while also
requesting restrained-corner torsion behavior.

### 5.3 Loads

Do not overload the existing single `factored_area_load_kn_per_m2` field for
continuous analysis. Define separate action inputs:

```text
characteristic inputs, if a future load-combination service is approved
OR
factored permanent area load + factored imposed area load
```

The first continuous slice accepts already factored components and records their
meaning. It must not apply hidden factors or infer whether imposed load is fixed,
patterned, reducible, sustained, or transient.

For the first two-way slice, a single caller-supplied total factored UDL may
remain acceptable because the Annex D design action uses the total design load;
serviceability still requires separately supplied service-load data.

### 5.4 Coefficients and action regions

Do not hard-code a result as four unlabelled alpha values. Use labeled records:

```text
axis: x or y
sign: positive or negative
location: midspan, x_min edge, x_max edge, y_min edge, y_max edge
coefficient value
coefficient method: exact, interpolated, or external
source record ID
design strip: middle or edge
```

This avoids applying a negative coefficient at a discontinuous edge and makes
the React reinforcement map possible without re-deriving engineering meaning.

### 5.5 Result semantics

Every composed result must distinguish:

- `method_applicability_status`;
- `coefficient_review_status`;
- `calculation_status` for completed arithmetic;
- `check_status` for each evaluated limit;
- `unsupported_dependencies`;
- `qualified_review_required`; and
- `is_safe` only when every required check in that route was actually evaluated.

`supported=True`, coefficient acknowledgement, or successful HTTP response must
never be translated into a complete or safe design.

## 6. Calculation design

### 6.1 One-way simply supported completion

Retain the existing flexure formula and benchmark. Add composition around it:

1. strict support/load-case identity;
2. required and provided main/distribution steel;
3. bar diameter and spacing checks;
4. basic or approved modification-factor deflection check;
5. slab one-way-shear check; and
6. a regional bar schedule with bottom main steel, distribution steel, support
   continuation/anchorage intent, and explicit unavailable development-length
   dependencies.

The existing public function remains backward compatible. If new mandatory
inputs are required for a stronger status, use an opt-in nested check request or
a new complete workflow rather than changing old calls from valid to invalid.

### 6.2 One-way continuous coefficient analysis

The coefficient method is supported only when the source conditions pass. The
first applicability contract includes:

- uniform cross-section;
- three or more spans;
- substantially UDL;
- span variation within the source limit;
- accepted end-support condition;
- approved load-component meaning; and
- no moment redistribution after coefficient analysis.

The analysis result contains positive moment per span, negative moment at every
interior support, relevant end-support negative action, and design shears. For
unequal spans or unequal loading, any source-required averaging is implemented
only in the later packet with an independent benchmark. S2 initially fails
closed outside the equal-span/equal-load benchmark envelope.

Use the same `_flexure` stress-block solver separately at every governing
positive and negative region. Do not take absolute moment and then lose the bar
face/location. Negative action maps to top reinforcement over the labeled
support; positive action maps to bottom reinforcement in the labeled span.

### 6.3 Two-way coefficient selection

The coefficient resolver sequence is:

```text
validate oriented geometry
  -> validate physical support topology and corner restraint
  -> derive canonical support case
  -> validate coefficient-method domain
  -> resolve exact source point
  -> interpolate only if S0 explicitly approved it
  -> return provenance-bearing coefficients
```

Rules:

- no extrapolation below `Ly/Lx = 1` or above `2`;
- no nearest-neighbor substitution;
- no rounding an arbitrary ratio to a table key;
- exact tolerance applies only to floating representation, not engineering
  approximation;
- interpolation, if approved, reports lower/upper points, fraction, method, and
  source identity;
- equivalent rotated/reflected cases retain the transform in the result; and
- caller-supplied coefficients never become `verified_by_library=True` merely
  because their arithmetic succeeds.

### 6.4 Two-way moments and flexure

For each accepted coefficient record, compute the labeled positive/negative
moments per metre using the controlled Annex D relationship and the effective
short span. Feed each moment to the existing slab rectangular stress-block
solver with the correct direction-specific effective depth.

The result must retain:

- action region and sign;
- coefficient and provenance;
- factored design moment in kN m/m;
- required steel in mm2/m;
- limiting moment and neutral-axis check;
- direction-specific depth and strip width; and
- unsupported actions/checks.

### 6.5 Strip distribution

For restrained panels, model one middle strip and two edge strips in each
direction. The controlled source review is expected to confirm the familiar
three-quarter middle strip and one-eighth edge strips, but source acceptance S0
remains authoritative.

Implementation behavior:

- coefficient moments apply to the relevant middle strip and are not
  redistributed;
- edge strips receive the required minimum reinforcement parallel to the edge;
- strip widths are returned in mm and sum exactly to the physical panel width;
- positive and negative bar regions retain their extension rules as structured
  zones, not prose only; and
- strip actions are not multiplied/divided again by strip width when the source
  moment is already per unit width.

### 6.6 Corner torsion

Each physical corner is classified from its two meeting edges:

| Corner condition | Target behavior, subject to S0 source lock |
|---|---|
| Both meeting edges discontinuous; corner restrained | Four layers, each based on 75% of the steel required for the governing maximum midspan moment; extend at least one-fifth short span in both directions |
| One meeting edge discontinuous; corner restrained | Half of the preceding torsion amount, with explicit layer/direction schedule |
| Both meeting edges continuous | No Annex D corner torsion steel |
| Corner free to lift under the simply supported method | No restrained-corner torsion design; method and assumption remain visible |

The function returns reinforcement areas and geometric zones. Bar selection may
remain provided-bar checking in the first packet. It must not silently convert
torsion reinforcement into ordinary edge minimum steel or omit one of the four
layers.

### 6.7 Detailing

Create a shared slab detailing kernel only where one-way and two-way rules are
actually identical:

- minimum reinforcement by steel type/grade;
- maximum bar diameter relative to total slab thickness;
- maximum main-bar spacing;
- maximum secondary/distribution spacing; and
- provided area per metre from diameter and spacing.

Keep region-specific curtailment/extension behavior in one-way or two-way
modules. Output a structured schedule:

```text
region ID
panel/span/support/corner ID
top or bottom face
x or y direction
design purpose: positive, negative, minimum, distribution, torsion
required and provided area per metre
bar diameter and spacing
start/end or zone dimensions
governing clause/source ID
status and limitations
```

Development length, anchorage into supports, laps, cover, durability, and fire
must either be explicitly checked from adequate inputs or returned as incomplete
dependencies. A pretty bar schedule is not evidence that those checks ran.

### 6.8 Serviceability

Use staged levels:

**Level A — required for first supported routes**

- strict support-condition span/depth check;
- supplied modification factors, or an explicit `review_required` outcome if
  they are not available;
- shorter span for approved two-way deemed-to-satisfy checks;
- explicit service-load versus factored-load separation; and
- cracking status remains `not_evaluated` unless all required service stress and
  geometry inputs are supplied.

**Level B — later approved packet**

- source-backed tension-steel modification-factor calculation;
- approved two-way span/overall-depth shortcut only inside its load, span,
  reinforcement-grade, and support bounds; and
- crack-width calculation with slab-specific bar spacing/cover/stress geometry.

**Level C — not required for the first slab milestone**

- direct short/long-term deflection, creep, shrinkage curvature, and construction
  sequence. These need a separate benchmark and must not reuse beam formulas
  without a slab-specific applicability review.

The current beam helper defaults unknown support inputs to simply supported and
omitted modifiers to `1.0`. A slab route must wrap or refactor that behavior to
fail closed/review-required; it must not inherit a silent default that changes a
design outcome.

### 6.9 One-way shear for ordinary solid slabs

Add a slab-local shear check that reuses only the accepted generic Table 19/20
lookups and applies the slab depth factor from Clause 40.2.1.1.

Inputs include factored shear per metre, strip width, effective/overall depth,
concrete strength, and relevant tension-steel percentage. Outputs include
`tau_v`, base `tau_c`, slab factor `k`, enhanced `k*tau_c`, `tau_c_max`,
utilization, and status.

Boundaries:

- first slice: ordinary floor/roof slabs under UDL;
- no concentrated-load enhancement;
- no deck/bridge/local wheel-load behavior;
- no invented stirrup design when ordinary slab depth is inadequate; and
- a failed check recommends redesign/increased depth and qualified review, not
  an automatically detailed shear-reinforcement solution.

### 6.10 Punching boundary

Punching is not a mandatory check for the beam/wall-supported UDL panels in the
initial capability. Return one of these explicit dispositions:

- `not_applicable_no_column_or_concentrated_load_interface`;
- `not_evaluated_missing_local_load_geometry`;
- `unsupported_flat_slab_extension`; or
- `evaluated` only in a separately approved future workflow.

Do not call `footing_punching_shear()` for a building slab. That function embeds
footing pressure, full interior perimeter, concentric load, and footing-specific
remedies. Any future shared punching kernel must first separate perimeter
geometry/capacity physics from footing and slab demand models, then cover
interior/edge/corner columns and unbalanced moment as approved cases.

## 7. Public API and compatibility plan

### 7.1 Preserve current workflows

- Keep `design_one_way_slab_is456()` valid for its existing simply supported
  strip contract.
- Keep `design_two_way_slab_is456()` as the externally accepted coefficient,
  interior flexure-only expert route until a deprecation plan is approved.
- Do not relabel historical `review_required` coefficients as verified.

### 7.2 Candidate new workflows

Names are frozen only in the public-contract packet:

```python
design_complete_simply_supported_one_way_slab_is456(...)
design_continuous_one_way_slab_is456(...)
design_restrained_two_way_slab_is456(...)
design_simply_supported_two_way_slab_is456(...)
check_slab_one_way_shear_is456(...)
```

If capability discovery prefers one schema-driven facade, use one new
`design_solid_slab_is456(request)` discriminated request while retaining the old
functions as compatibility wrappers. Do not make the facade a dictionary-driven
god function; request variants must be typed and dispatch only to pure accepted
calculations.

### 7.3 Capability registry

Update `services/capabilities.py` only after each vertical slice passes. The
record must list support topology, load method, coefficient provenance, completed
checks, and held cases. Separate statuses for coefficient truth, arithmetic,
checks, and qualified review are mandatory.

## 8. FastAPI plan

Recommended routes after pure-library acceptance:

```text
POST /api/v1/design/slab/one-way/simply-supported
POST /api/v1/design/slab/one-way/continuous
POST /api/v1/design/slab/two-way/restrained
POST /api/v1/design/slab/two-way/simply-supported
GET  /api/v1/design/slab/support-cases
```

The existing `/api/v1/design/slab/one-way` remains compatible and may call the
old or complete simply supported service based on an explicit versioned request,
not shape guessing.

FastAPI requirements:

- Pydantic discriminators for analysis method/support type;
- cross-field validators for span order, depths, support topology, coefficient
  approval, and service/factored load separation;
- response models that preserve all statuses and limitations;
- standard 422 envelope for unsupported/invalid input;
- no formula or coefficient lookup in routers/models;
- OpenAPI baseline and React client-signature synchronization; and
- no `is_safe=True` when serviceability, shear, or required detailing remains
  unexecuted.

## 9. React slab workbench

### 9.1 User journey

Add one slab workflow inside the existing structural workbench, not a separate
mini-application:

```text
Choose slab method
  -> enter oriented panel/spans and thickness
  -> set physical edge continuity and corner restraint
  -> enter design and service loads
  -> review coefficient method/provenance
  -> calculate
  -> inspect moments/checks/reinforcement map
  -> acknowledge HOLD items
  -> save revision-bound result and export passport
```

### 9.2 Minimum UI surfaces

1. **Method card:** simply supported one-way, continuous one-way, restrained
   two-way, or simply supported two-way; unsupported methods disabled with why.
2. **Panel sketch:** oriented `Lx/Ly`, four clickable edge conditions, and four
   derived corner classes. The drawing is explanatory, not an analysis canvas.
3. **Inputs:** geometry, material, design loads, service loads, and provided bars
   with units at every field.
4. **Coefficient review:** case ID, exact/interpolated/external method, source
   identity, aspect-ratio bounds, and library-verification status.
5. **Results:** action diagram/table, governing checks, serviceability/shear,
   middle/edge strips, and corner torsion schedule.
6. **Trust panel:** supported case, excluded cases, qualified-review requirement,
   stale/recalculation state, and calculation identity.
7. **Export:** a revision-bound calculation passport; no current export when
   inputs changed after calculation.

### 9.3 UI boundaries

- No coefficient math, support-case inference, bar-area calculation, or safety
  aggregation in React.
- No generic schema renderer for complex edge topology until the curated slab
  interaction proves the contract.
- No decorative 3D slab viewer in the first vertical slice. A clear 2D
  reinforcement/strip diagram is more useful. Add 3D only if it materially helps
  inspect top/bottom layers and passes non-WebGL fallback requirements.
- Slab work must use the current revision-safe request/result/persistence model.

## 10. Evidence and benchmark ledger

### 10.1 Accepted starting benchmarks

| ID | Case | Inputs/expected result | Use |
|---|---|---|---|
| SLAB-B01 | Existing simply supported one-way strip | `Lx=3.0 m`, accepted existing load/material case; `Mu=11.25 kN m/m`, `Ast=260.7266 mm2/m` | Regression anchor; do not alter arithmetic |
| SLAB-B02 | Continuous one-way, NPTEL Lesson 18 Problem 8.1 | `L=3.0 m`, `D=140 mm`, `d=115 mm`, M20/Fe415, factored dead/live `6.75/7.50 kN/m`; positive `10.6875`, negative `12.825 kN m/m`, shear `17.1 kN/m`, direct-equation steel about `270.615/328.34 mm2/m`, `tau_v=0.148 N/mm2` | First continuous action/flexure/shear benchmark; verify against controlled source and independent worksheet |
| SLAB-B03 | Existing interior two-way arithmetic | `Lx=4 m`, `Ly=6 m`, `wu=10 kN/m2`, external `alpha_x=.08`, `alpha_y=.06`; moments `12.8/9.6 kN m/m` | Compatibility anchor for external-coefficient route |
| SLAB-B04 | Restrained two-way corner panel, NPTEL Lesson 19 Problem 8.2 | `Lx=4 m`, `Ly=6 m`, `wu=15.5 kN/m2`, two adjacent edges discontinuous; negative `Mx/My=18.6/11.66`, positive `13.89/8.68 kN m/m`, shear `31 kN/m`, torsion zone `800 mm` | First built-in/topology/strip/torsion vertical slice; coefficient points require S0 source approval |

NPTEL results are independent educational evidence. Each benchmark packet must
also include a project-owned hand calculation from controlled primary formulas.
Round only presentation fields; compare unrounded calculation values.

### 10.2 Required negative/governing cases

- `Ly/Lx` exactly 2 and just above 2;
- span input reversal with physical edge topology (must reject, never rotate
  silently);
- continuous method with fewer than three spans;
- continuous spans outside permitted variation;
- non-UDL/concentrated-load request;
- aspect ratio below 1 or above 2 for Annex D;
- exact coefficient point, allowed interpolation interior point, and prohibited
  extrapolation;
- inconsistent edge topology/corner restraint;
- two-discontinuous-, one-discontinuous-, and zero-discontinuous-edge corners;
- `d >= D`, invalid directional depth, invalid strip width, non-finite input;
- factored loads accidentally supplied to serviceability fields and vice versa;
- flexural demand at/just above limiting capacity;
- provided steel/spacing/diameter at and just beyond each limit;
- shear at/just above `k*tau_c` and at `tau_c_max`;
- stale saved result after any geometry/support/load/rebar edit; and
- unsupported flat-slab/punching request.

### 10.3 Tolerances

Define tolerance per quantity and benchmark source before implementation:

- exact topology/status/source IDs: exact equality;
- coefficient exact table points: exact decimal representation approved by S0;
- coefficient interpolation: documented absolute tolerance and endpoint proof;
- equilibrium/design actions: tight relative tolerance justified by arithmetic;
- nonlinear steel root: benchmark-specific relative/absolute tolerance;
- UI formatting: display tolerance only, never calculation acceptance; and
- no tolerance widening merely to reconcile a benchmark mismatch.

## 11. Dependency-ordered execution packets

One packet owns one independently verifiable main process. Do not open downstream
API/UI work before its pure calculation and benchmark are accepted.

| Order | Packet | Outcome | Main dependencies |
|---:|---|---|---|
| 0 | S0 — Source, legal, case, benchmark lock | Approved source-page map, coefficient policy, topology IDs, interpolation decision, benchmark ledger | Owner/source reviewer |
| 1 | S1 — Oriented geometry and support topology | Physical edges/corners resolve deterministically without span normalization errors | S0 |
| 2 | S2 — Continuous one-way action coefficients | One equal-span/equal-load continuous strip produces labeled moments/shears | S0-S1 |
| 3 | S3 — One-way complete design | Simply supported and continuous flexure/detailing/serviceability/shear compose truthfully | S2 |
| 4 | S4 — Two-way coefficient provider | Exact approved case lookup plus external provider; interpolation only if approved | S0-S1 |
| 5 | S5 — Corner-panel two-way flexure | B04 moments and steel by labeled region/direction | S4 |
| 6 | S6 — Strip and corner torsion schedule | Middle/edge strips and C1/C2/C3 corner zones match B04 | S5 |
| 7 | S7 — Two-way detailing/serviceability/shear | Complete bounded checks for the accepted corner panel | S3, S6 |
| 8 | S8 — Common support-case expansion | Remaining approved restrained cases plus simply supported free-corner case | S7 |
| 9 | S9 — Public facade and capability truth | Stable new workflows, semantic contract, compatibility behavior | S3, S8 |
| 10 | S10 — FastAPI vertical slices | Typed request-to-service-to-response paths | S9 |
| 11 | S11 — React simply supported/continuous one-way | First end-to-end slab user outcome and revision-safe passport | S10 |
| 12 | S12 — React two-way topology/reinforcement map | Common support cases, provenance, strips, corners, and checks | S11 |
| 13 | S13 — Integrated evidence and documentation | Browser/API/library evidence, capabilities, examples, limitations | S12 |
| HOLD | FS0 — Flat-slab extension decision | Separate scope/source/analysis/punching program | Explicit new approval only |

## 12. Worker-ready packet cards

### S0 — Source, legal, case, and benchmark lock

**Objective:** turn the research into an approved calculation/source contract.

**Owned artifacts:** this plan, a new slab evidence ledger under
`docs/verification/`, and private source-review records only in the ignored
controlled-source area.

**Required decisions:**

- exact primary source pages/clauses for 22.2, 22.5, 23.2, 24, 26.3, 26.5,
  40.2.1.1, Annex D, and Tables 12/13/19/20/26/27;
- whether normalized coefficient values may ship in the open-source package;
- exact support-case IDs and physical-edge transforms;
- exact-match versus interpolation policy;
- characteristic/factored/service load contract; and
- accepted values/tolerances for B02 and B04 independent calculations.

**Non-goals:** code, public exports, copying tables, UI.

**Acceptance:** every future function has a primary source ID, benchmark,
units, domain, and licensing disposition; unresolved interpretation narrows the
case instead of being guessed.

**Return:** source map, approved decisions, HOLDs, benchmark worksheet IDs,
checksums, and first code packet authorization.

### S1 — Oriented panel and support topology

**Likely files:** `slab/models.py`, new `slab/supports.py`, slab contract tests.

**Objective:** represent physical axes, edges, corners, continuity, and corner
restraint without calculation behavior.

**Pitfalls:** silent span rotation; conflating support with corner restraint;
allowing user-selected case IDs to contradict edges; placing UI labels in core.

**Acceptance:** all approved physical topologies resolve to canonical source
cases and transforms; reversal/mismatch failures are explicit; architecture and
imports pass.

**Narrow checks:** exact slab contract/support test paths, architecture boundary,
and structural-lib import validation.

### S2 — Continuous one-way action coefficients

**Likely files:** new `slab/one_way_continuous.py`, optional approved coefficient
provider data, focused tests.

**Objective:** calculate labeled positive/negative actions and shear for the
first approved continuous strip.

**Non-goals:** bar design, serviceability, broad patterned loading, elastic
analysis, two-way behavior.

**Pitfalls:** mixing dead/live components; applying coefficients outside their
conditions; losing moment sign/location; redistributing coefficient moments.

**Acceptance:** B02 action values match; inapplicable methods fail closed; every
action retains span/support ID, coefficient, units, and source record.

### S3 — Complete one-way composition

**Likely files:** `slab/one_way.py`, `slab/one_way_detailing.py`, new
`slab/shear.py`, new `slab/serviceability.py`, `services/slab_api.py`, tests.

**Objective:** compose simply supported and continuous actions into flexure,
provided-bar detailing, Level A serviceability, and one-way shear.

**Pitfalls:** breaking old service signature; defaulting missing modifiers;
using factored actions for serviceability; returning safe with an unevaluated
required check.

**Acceptance:** B01 remains unchanged; B02 flexure/shear matches; serviceability
has pass/fail/review/not-evaluated truth; regional bar schedule is complete for
the supported case.

### S4 — Provenance-bearing two-way coefficient provider

**Likely files:** evolve `slab/external_coefficients.py`, new
`slab/coefficients.py`, focused tests; built-in data only if S0 permits it.

**Objective:** resolve topology/aspect ratio to approved coefficients or validate
external coefficients without confusing the two trust levels.

**Pitfalls:** reproducing protected tables; rounding to nearest ratio;
extrapolation; coefficient acknowledgement becoming correctness verification;
axis transform errors.

**Acceptance:** exact point/provenance, prohibited out-of-domain cases, and
external review semantics pass; interpolation tests exist only if S0 approved
the method.

### S5 — Two-way corner-panel flexure

**Likely files:** `slab/two_way.py`, `_flexure.py` only if a confirmed shared
root defect exists, focused tests.

**Objective:** produce B04 labeled negative/positive x/y moments and required
steel while preserving B03 compatibility.

**Pitfalls:** using one effective depth for both directions; applying negative
steel to a discontinuous edge; double scaling per-unit-width moments; changing
external route status.

**Acceptance:** B03 arithmetic/status unchanged; B04 moments and independent
steel roots match; limiting-flexure unsafe case fails closed.

### S6 — Strip distribution and corner torsion

**Likely files:** new `slab/two_way_detailing.py`, support/topology models, tests.

**Objective:** generate structured middle/edge strip and corner reinforcement
zones for B04.

**Pitfalls:** applying moments to edge strips; omitting top/bottom or x/y torsion
layers; measuring extension from the wrong edge; using long span for the
one-fifth zone; treating no torsion required as a universal no-reinforcement
result.

**Acceptance:** strip widths close exactly; every B04 region is labeled; C1/C2/C3
amount and zone invariants pass; unsupported corner-restraint mismatch rejects.

### S7 — Two-way detailing, serviceability, and shear

**Likely files:** shared slab detailing/serviceability/shear modules,
`two_way_detailing.py`, tests.

**Objective:** complete the required checks for the accepted two-adjacent-edge
panel without claiming punching evaluation.

**Pitfalls:** duplicate common limits; inappropriate one-way `L/d`; reporting
punching safe because it is absent; using minimum steel as tension percentage
without region/face justification.

**Acceptance:** provided-bar limits, Level A serviceability, ordinary one-way
shear, and punching disposition are all explicit; B04 shear benchmark matches.

### S8 — Common support-condition expansion

**Objective:** add one support case at a time through the same S4-S7 pipeline,
then add the simply supported/free-corner method.

**Required order:** interior regression -> one discontinuous edge -> two
adjacent discontinuous edges -> all discontinuous restrained -> simply supported
free corners -> remaining approved source cases.

**Acceptance per case:** source point, one independent benchmark, topology
transform, strip/corner schedule, unsafe/unsupported case, and truthful
capability wording.

### S9 — Public facade and semantic contract

**Likely files:** `services/slab_api.py`, `services/api.py`, top-level exports,
`services/capabilities.py`, API reference, contract tests.

**Objective:** expose only accepted workflows with explicit units/statuses and
preserve old callers.

**Pitfalls:** exporting expert helpers; ambiguous `design_two_way` wording;
capability docs ahead of code; aliases with different semantic truth.

**Acceptance:** exact signatures rediscovered; serialization is stable; semantic
contract distinguishes completed and held checks; public docs match behavior.

### S10 — FastAPI vertical slices

**Likely files:** split slab models/router from `library_core.py` if needed,
application wiring, OpenAPI baseline, focused API tests.

**Objective:** provide thin typed consumers for one-way and two-way workflows.

**Pitfalls:** monolithic request with irrelevant optional fields; router math;
HTTP 200 interpreted as safe; manual response types drifting from dataclasses.

**Acceptance:** representative valid and invalid requests map exactly to service
results/statuses; 422 envelope, typed response, OpenAPI, and signature checks pass.

### S11 — React one-way slab vertical slice

**Likely files:** curated slab feature folder, API client/generated types,
workbench route/stage integration, workspace result record, focused tests.

**Objective:** let a user complete and save one simply supported or continuous
one-way slab calculation without dead ends.

**Pitfalls:** duplicate editable state; stale response overwrite; hidden units;
client-side safety aggregation; export after input change.

**Acceptance:** input -> API -> results -> edit/stale -> recalculate -> passport
works at maintained widths; unsafe/review states remain visible.

### S12 — React two-way topology and reinforcement map

**Objective:** add physical edge/corner input, coefficient provenance, strips,
torsion zones, and two-way results using the accepted API.

**Pitfalls:** UI orientation differs from calculation axes; mirrored corners;
color alone communicates top/bottom/status; diagram becomes formula authority.

**Acceptance:** B04 physical topology and every returned region render correctly;
keyboard/text alternatives exist; no WebGL dependency; stale and unsupported
states pass.

### S13 — Integrated evidence and documentation

**Objective:** close the bounded program with reproducible software evidence and
honest public wording.

**Evidence:** focused calculation/API/React tests, exact benchmark worksheet IDs,
capability/schema/OpenAPI checks, responsive browser flow, exported passport
bytes, quick gate, one full gate, and cumulative qualified-review ledger entry.

**Non-goals:** stable release, professional-use approval, merge/release/branch
deletion unless separately authorized.

**Acceptance:** one source-to-UI case for each advertised route; no unsupported
case is advertised; software evidence and qualified approval remain separate.

## 13. Likely file map

```text
Python/structural_lib/codes/is456/slab/
  models.py                    # extend only for package-local slab contracts
  supports.py                  # oriented physical topology and case resolution
  coefficients.py              # provider contract/provenance; data policy gated
  external_coefficients.py     # preserve current external trust route
  one_way.py                   # preserve simply supported root calculation
  one_way_continuous.py        # coefficient-method continuous actions
  one_way_detailing.py         # evolve without breaking current result
  two_way.py                   # labeled moments/flexure, old route compatible
  two_way_detailing.py         # strips, regions, corner torsion
  serviceability.py            # strict slab adapters/calculations
  shear.py                     # ordinary slab one-way shear

Python/structural_lib/services/slab_api.py
Python/structural_lib/services/capabilities.py
fastapi_app/models/slab.py      # split when slab surface warrants it
fastapi_app/routers/slab.py
react_app/src/features/slab/    # use actual current feature convention at S11
docs/verification/is456-slab-evidence.md
```

Do not add shared `core/` abstractions unless two current elements demonstrably
need the exact same stable contract. Slab package-local types are the default.

## 14. Main pitfalls and implementation tips

| Pitfall | Outcome-changing consequence | Required prevention |
|---|---|---|
| Silent `Lx/Ly` normalization after edges are attached | Coefficients and torsion go to the wrong physical edge/corner | Oriented geometry; reject reversed axes |
| Support case selected independently of edges | Valid table row applied to a different physical panel | Derive case ID from edge topology |
| Built-in and external coefficient trust merged | User believes library verified supplied coefficients | Separate providers/status fields |
| Ratio rounded or extrapolated | Wrong design action without visible error | Exact/interpolation provenance; hard bounds |
| Factored and service loads share a field | Invalid strength/serviceability outcome | Distinct typed fields and validators |
| Negative moment converted to `abs()` without region | Top steel placed at wrong support/face | Preserve sign, support, and face |
| Per-unit-width moment scaled twice | Reinforcement badly over/under-designed | Freeze dimensional contract and unit tests |
| One effective depth used both ways | Long-direction capacity error | Direction-specific depths |
| Strip moments redistributed | Violates approved coefficient method | Explicit no-redistribution invariant |
| Torsion layer omitted | Corner restraint requirement incomplete | Four explicit face/direction records |
| Beam serviceability defaults reused | Missing modifier silently treated as acceptable | Strict slab adapter/review state |
| Footing punching function reused | Wrong demand/perimeter and misleading safety | Explicit punching disposition; separate future kernel |
| SP 16 treated as current code | Withdrawn aid becomes normative source | Primary IS 456 equation and current source dominate |
| Tests reproduce full tables | Source/licensing exposure and brittle duplication | Minimal benchmark points/invariants |
| UI computes engineering meaning | Python/API/UI drift | Render returned topology/actions only |
| Capability updated early | Product overclaims partial work | Update only after vertical-slice acceptance |

Tips:

- First make the physical topology and result semantics boring and explicit;
  coefficient math becomes much safer afterward.
- Use one high-learning two-way case—two adjacent discontinuous edges—before
  expanding all support rows; it exercises signs, strips, C1/C2/C3 corners, and
  orientation in one benchmark.
- Keep bar *checking* before bar *optimization*. A deterministic provided-bar
  contract is easier to verify and does not hide constructability choices.
- Return structured zones and source IDs from Python so API, UI, and exports are
  thin consumers.
- Treat every `review_required` result as a first-class outcome, not an error to
  suppress or a pass to color green.

## 15. Verification commands

Use the narrowest affected tests during each packet. Expected closeout ladder:

```bash
.venv/bin/pytest Python/tests/codes/is456/slab -q
.venv/bin/pytest fastapi_app/tests -q -k "slab"
cd react_app && npm test -- --run <exact-slab-tests>
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib
./run.sh find --api <new_public_function>
./run.sh frontend check
./run.sh check --quick
./run.sh check
```

Run the full gate once at stable program closeout, not after every packet. Release
preflight is outside this plan unless the owner separately starts a release.

## 16. Definition of done

IS456-SLAB-001 is software-complete only when:

- each advertised one-way/two-way case has controlled source identity and an
  independent benchmark;
- support topology, coefficient selection, moments, reinforcement regions,
  detailing, serviceability, and shear remain traceable end to end;
- coefficient source/trust and any interpolation are visible at every public
  boundary;
- all required checks are evaluated before a route can return an aggregate safe
  status;
- simply supported and continuous one-way workflows are available through the
  requested consumers;
- common two-way support cases include correct strip and corner behavior;
- punching and flat-slab requests are explicitly held rather than silently
  omitted;
- the slab UI saves revision-bound results and blocks stale export;
- capability/docs/examples describe only the accepted cases;
- focused, cross-layer, quick, full, and live evidence is retained; and
- the cumulative qualified structural-engineering review ledger is ready for
  the future stable/engineering-use gate.

Passing these gates proves the bounded software behavior. It does not certify a
project design or replace a qualified structural engineer.

## 17. Owner decisions and HOLD ledger

| Decision | Recommended default | Effect if not approved |
|---|---|---|
| May normalized IS 456 coefficients be implemented? | **Approved by owner on 2026-08-10; do not ask again** | Built-in lookup is required implementation scope |
| Is linear interpolation permitted? | **Approved for implementation on 2026-08-10** with exact endpoint and bounds tests | No extrapolation or silent topology fallback |
| May a public production release distribute normalized coefficient data? | **Approved by owner on 2026-08-11; canonical record is release-validated; do not ask again unless explicitly changed** | Protected source content remains excluded; each tag/publication still needs separate owner authorization |
| First continuous load envelope | Equal spans/equal UDL components | Unequal/patterned loading remains unsupported |
| First two-way completion benchmark | B04 two adjacent discontinuous edges | Use another case only with equal source/benchmark quality |
| Bar selection versus provided-bar check | Provided-bar check first | Optimization deferred |
| Serviceability level | Strict Level A first | Level B/C deferred, status review-required |
| Punching | Explicitly not applicable/unsupported for this system | No punching-safe claim |
| Flat slabs | Separate program and approval | Entire Cl. 31 system remains HOLD |

### Flat-slab extension approval packet, when requested

FS0 must independently define analysis method, column/middle strips, drops and
column heads, column locations, punching perimeters, unbalanced moment transfer,
openings, edge/corner columns, shear reinforcement policy, serviceability,
benchmarks, API/UI scope, and qualified-review plan. Approval of solid slabs or
generic shear helpers does not authorize FS0.

## 18. Implementation checkpoint

S0-S13 have been implemented on `codex/is456-slabs-plan` across the pure slab
domain, public service facade, capability contract, FastAPI routes and React
workbench. The calculation paths include built-in and external coefficient
providers, exact/bounded interpolation with no extrapolation, oriented physical
edge topology, continuous one-way actions, common two-way panel actions,
provided-bar checks, strip/corner distribution, strict span/depth carriers and
ordinary one-way shear.

The compatibility functions remain available. The new UI preserves request
revision identity and disables passport export after inputs become stale.
Final acceptance still requires focused and repository-wide gates plus this
session's issue/root-cause record. Flat slabs remain under FS0 and are not
authorized by this checkpoint.

## 19. IS456-SLAB-001A workflow-truth and React closeout

The closeout keeps all compatibility-route arithmetic unchanged while correcting
the semantics serialized by complete workflows. A complete one-way result now
marks its retained flexure/detailing records as composed and removes obsolete
claims that reinforcement, serviceability, or shear remain pending. Complete
two-way workflows retain actual coefficient provenance and no longer describe
implemented built-in lookup/interpolation as held; their returned serviceability
dependency records that the reviewed-limit check was evaluated by the wrapper.

The existing React workbench now exposes the supported Table 12/13 action
locations and physical two-way edge/corner topology. Its review surface displays
coefficient source/case/interpolation bounds, provided-reinforcement adequacy,
strip widths, each corner-torsion zone, shear and serviceability dispositions,
and truthful remaining holds. Inadequate or exceeded checks produce a redesign/
qualified-review outcome. Revision-bound results and stale-export blocking remain
unchanged.

This closeout adds no slab formula, analysis method, element type, or professional
approval claim. Direct deflection, crack width, automatic slab shear
reinforcement, irregular/concentrated-load panels, flat slabs, column-supported
punching, and the other Section 3.4 non-goals remain held.
