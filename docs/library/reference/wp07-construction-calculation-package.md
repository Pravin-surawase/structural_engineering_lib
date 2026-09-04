# WP07 construction data and calculation package

WP07 publishes four host-free operations with matching Python and .NET
semantics. AO19 creates a bar bending schedule and deterministic cutting plan
from AO18 physical reinforcement paths. AO04 measures steel, concrete,
formwork, and fabrication waste. AO20 applies a dated commercial rate profile.
AO24 creates the immutable calculation, report, drawing, and schedule model
that a renderer can turn into files.

The portable schema is
`contracts/structural-engineering/schemas/wp07.schema.json`. Required fields are
never inferred from an Excel cell, ETABS model, regional price list, or report
template. Omitted cost means no cost. An entered zero is a supplied numerical
value.

## AO19: create BBS and cutting data

`create_bbs` / `BbsOperations.Create` consumes one passing AO18 schedule bound
to the same profile, project, member, and detail revision. One BBS mark may
contain only the homogeneous geometry, diameter, grade, role, bundle size, and
ordered bend-plane pattern that AO18 qualified.

Every downstream request carries both the upstream operation `result_id` and a
canonical `output_payload_id`. The operation recomputes the payload identity
from the supplied typed record and rejects a detached or changed result. AO04,
AO20, and AO24 repeat this check across the complete dependency chain.

The fabrication convention in this packet is
`resolved_centreline_v1`. Each BBS row retains two separately named values:

- centreline developed length from tangent straights and circular arcs; and
- fabrication cut length produced by the declared convention.

They are equal for this convention but remain separate fields so a future,
separately versioned fabrication convention cannot silently change geometric
length. A lap is already present in the two physical overlapping paths and is
not added again. A coupler is a separate hardware record with no invented lap
length.

Bundles multiply the scheduled physical bar count. The steel mass basis is
`pi / 4 * diameter_mm^2 * scheduled_cut_length_mm / 1e9 * density_kg_per_m3`.
For four 20 mm bars, each 6000 mm long, at 7850 kg/m3, the mass is
59.18760559 kg.

The stock policy names available lengths, kerf per extracted cut, the minimum
retained offcut, and the allocation method. WP07 implements deterministic
first-fit-decreasing and reports it as a heuristic; it does not claim a proven
global optimum. Stock pieces do not mix diameter or grade. Every plan satisfies:

`stock = scheduled cuts + kerf + reusable offcuts + unreusable waste`

Reusable offcuts and waste are mutually exclusive. A cut must fit together
with its required kerf. Link zones state their first and last possible station
and whether each boundary is included. Adjacent zones cannot both own a shared
station, and the generated station set must match the resolved physical link
paths.

## AO04: calculate construction quantities

`calculate_construction_quantities` / `QuantityOperations.Calculate` measures
the current BBS. It does not accept a required steel area as a substitute for
physical bars. Steel output retains every mark, scheduled count, cut length,
grade, and mass, including links, side bars, anchorage geometry, and lap paths.
The output keeps scheduled steel mass and purchased stock mass separate.

Concrete is supplied as explicit owned net segments. Each segment has a
cross-section area, physical length, material, monolithic-interface ownership,
and uniquely owned volume deductions. The named overlap policy tells a caller
which member owns a slab, support, or other monolithic region. Duplicate
physical ownership is rejected.

Formwork is supplied as separate contact faces: soffit, left side, right side,
end bulkhead, slab interface, support interface, or another declared face.
Every face has unique physical ownership, gross area, deductions, and an
included or explicitly excluded measurement state. This measures work; it does
not design temporary works.

The independent reference beam uses a 300 x 500 mm section over 6000 mm. Its
concrete volume is 0.9 m3. Its soffit and two sides are 7.8 m2. The result's
`direct_cost` is null because AO04 never invents rates.

## AO20: estimate declared direct cost

`estimate_construction_cost` / `CostOperations.Estimate` binds one current AO04
result to a versioned rate profile. The profile records three-letter currency,
valuation date, time zone, geography, source, included and excluded categories,
individual measured rates, steel waste pricing basis, overhead treatment, and
tax treatment.

Every material, formwork, coupler, labour, and plant category is either
included or excluded exactly once. Included categories need explicit rates;
zero is the explicit way to supply a zero rate. Steel is priced from scheduled
mass or purchased-stock mass, never both. This prevents a fabrication waste
allowance from being charged twice.

Money crosses the portable boundary as nonnegative decimal strings. The
operation uses decimal arithmetic and returns each source quantity, unit rate,
line amount, direct subtotal, overhead, pre-tax amount, tax, and total. The
operation rounds each line to two currency decimals using round-half-to-even,
sums those displayed lines, then rounds overhead and tax by the same rule. The
result is a scoped estimate rather than a quotation or professional approval.

## AO24: create the calculation package

`create_calculation_package` / `CalculationPackageOperations.Create` combines
one AO17 member result with the exact AO18, AO19, AO04, and optional AO20 result
chain. It retains project, member, revision, engine, dataset, normalized-input,
calculation, and result identities.

The package profile must list the same complete leaf set derived by AO17. Each
leaf carries its operation, evidence result, required/provided/selected values,
unit, utilization, governing state, qualification, and reason codes. A matching
trace supplies the code/rule reference, formula reference, and normalized
substitution. Assumptions and limitations are explicit.

Drawing views are renderer-neutral data bound to the active detail revision.
Render sections identify semantic payloads for inputs, calculations,
reinforcement, BBS, quantities, cost, drawings, and recorded human actions.
PDF, HTML, spreadsheet, or drawing file creation belongs to a language-specific
adapter.

Prepared, checked, approved, and rejected fields are records of actual actions.
Each requires a real actor identity and display name, professional role,
timezone-aware timestamp, scope, and exact bound result identity. The operation
never invents a person or signature. A current complete chain produces an
`issue_ready` semantic model; an absent, partial, or stale dependency remains a
visible `draft` with partial result state. A recorded approval on stale evidence
cannot become active approval.

## Python surface

```python
from structural_lib.construction import (
    BbsRequest,
    CuttingStockPolicy,
    ShapeConvention,
    create_bbs,
)

request = BbsRequest(
    profile_id="ordinary-beam",
    project_basis_id="project-basis-r1",
    member_id="B1",
    detail_revision_id="detail-r1",
    schedule_result_id="schedule-result-r1",
    schedule_output_payload_id="output_payload_id:pf4-canonical-json-v1:...",
    schedule=typed_resolved_schedule,
    shape_convention=ShapeConvention("IS2502", "shape-r1"),
    stock_policy=CuttingStockPolicy(
        "project-stock",
        "stock-r1",
        (6000, 9000, 12000),
        kerf_mm=3,
        reusable_offcut_min_mm=500,
    ),
    steel_density_kg_per_m3=7850,
)
result = create_bbs(request)
assert result.engineering == "pass"
```

`structural_lib.reporting` contains the AO24 records and operation. Applications
may translate a validated operation-result payload back into the corresponding
typed request record at an interchange boundary; application tables and files
do not enter these pure operations.

## Corrections from the earlier library

The earlier Python BBS can infer full-span bars and link counts from zones, then
round cut lengths before the physical path exists. Its cutting helper counts
every remainder as waste and checks maximum cut length without including the
kerf later required by allocation. The earlier costing helpers can fall back to
generic INR prices and simple beam prisms or open-top formwork rules.

The older calculation report directly renders mutable results and fills dates
at runtime. It exposes engineer and checker text fields without requiring an
identity-bound recorded action. The earlier C# quantity kernel contains useful
bend-arc, mass, volume, contact-area, and decimal-cost arithmetic but does not
bind the active detail/result chain or distinguish retained offcuts.

WP07 retains the useful arithmetic and replaces those meanings with physical
paths, owned segments/faces, explicit policies, dated sourced rates, immutable
result identities, and renderer-neutral package data.
