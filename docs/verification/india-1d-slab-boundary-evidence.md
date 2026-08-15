---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-1D
---

# INDIA-1D Solid-Slab Boundary Evidence

INDIA-1D closes the decision boundary around already supported solid-slab
serviceability, shear, and loading behavior. It does not add or promote new
structural formulas.

## Supported outcome

The complete simply supported, continuous one-way, and common two-way
beam/wall-supported workflows retain:

- reviewed span/depth serviceability with explicit source and qualified-
  acceptance references;
- ordinary one-way concrete shear using the maintained Table 19/20 lookup and
  solid-slab depth factor;
- supplied reinforcement and topology checks appropriate to each route; and
- one caller-selected factored UDL or declared coefficient-method action basis
  per call.

The result carriers now serialize the ceiling. `SlabServiceabilityResult`
identifies both direct deflection and crack width as held, while complete
workflow results expose `load_envelope_status`. `SlabShearResult` already
reports `not_automatically_designed` for shear reinforcement regardless of its
concrete-capacity disposition.

## Boundary benchmark

The focused public test uses the accepted simply supported one-way strip with a
3000 mm effective span, 150 mm overall depth, 125 mm effective depth, 10 kN/m2
factored UDL, M20 concrete, Fe415 steel, and supplied 10 mm main bars at 250 mm.
It verifies:

- actual and reviewed modified span/depth ratios: 24.0, utilization 1.0;
- nominal shear stress: 0.12 N/mm2;
- design concrete shear capacity: 0.4688283053 N/mm2;
- concrete-capacity status: `concrete_capacity_satisfied`;
- automatic shear reinforcement: `not_automatically_designed`; and
- JSON serialization of the serviceability, shear, and load-envelope holds.

A separate focused failure case verifies that exceeding ordinary concrete shear
capacity never changes the automatic-reinforcement disposition into a design
claim.

## Retained boundaries

Direct deflection needs a separately accepted slab contract with explicit
service actions/combinations, load duration, reinforcement positions, cracking
and effective inertia, creep and shrinkage, plus independent slab benchmarks.
Crack width needs explicit bar geometry, cover, neutral-axis depth, exposure
limit, and service steel stress or strain validated for the supported slab
domain. Beam serviceability utilities are not promoted as slab-qualified by
analogy.

Automatic slab shear reinforcement remains held: a failed ordinary shear check
requires increased depth or separate engineering. Concentrated loads, openings,
irregular panels, project load-combination/pattern generation, and envelope
analysis remain excluded from every public slab signature. Flat/drop/ribbed and
column-supported slabs, punching, and FEM remain separate extensions.

This packet receives focused tests, architecture/import validation, the quick
repository gate, and required hosted PR checks. Broad Python and the full
repository gate run once after INDIA-1A through INDIA-1D are integrated.
