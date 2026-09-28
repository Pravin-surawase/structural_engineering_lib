# WP01 reinforcement and flexure reference

WP01 publishes six semantic operations:

| ID | Semantic operation | Purpose |
|---|---|---|
| FO01 | `structural.reinforcement.bar_area/v1` | Nominal circular bar area |
| FO02 | `structural.reinforcement.mass_per_length/v1` | Bar mass from diameter and declared density |
| FO03 | `structural.reinforcement.effective_depth/v1` | Area-weighted effective depth from actual coordinates |
| FO04 | `is456.beam.flexural_capacity/v1` | Supplied-section capacity without a demand decision |
| AO03 | `structural.reinforcement_geometry.evaluate/v1` | Area, centroid, cover, clear spacing, and fit |
| AO06 | `is456.beam.flexure.check/v1` | Positive and negative demand checks using physical faces |

The profile covers rectangular singly and doubly reinforced sections and T/L
sections with an eligible compression flange. Reverse bending of a flanged
section uses the web rectangle because the flange is then in tension. Nonzero
axial interaction is explicitly `not_applicable` for this profile.

Capacity method `is456-flexural-capacity-wp01-v3` uses each bar's actual depth.
Plane-section strains are `0.0035*(1-y/x)` with compression positive. Fig 23A
defines the deformed-steel curve, including the 0.975fy point and design strength
`fy/1.15`; Fe250 uses a definite yield point. Each compression bar displaces
concrete at its local Fig 21 stress. A bar may be in tension regardless of its
nominal face label. The existing 0.36/0.42 rectangular and Annex G flange
design blocks supply the concrete resultant.

The solver equilibrates concrete and every bar, then sums their actual moments.
`bar_responses` retains bar identity/layer, depth, area, signed strain, steel
stress, displaced-concrete stress and net force. `force_residual_n` makes
equilibrium inspectable. Area-weighted depths remain geometric outputs and
inputs to minimum-steel and downstream depth checks.

The most strained tension bar must satisfy 38.1(f),
`fy/(1.15*200000)+0.002`. The limiting axis is derived at that extreme bar,
not the group's centroid. An over-reinforced section returns its actual
equilibrated resistance with engineering FAIL; its axis is not clipped to a
limiting value. This changes some numerical results from v2, including the
rounded 0.87fy plateau. Existing operation IDs and request constructors remain.
The historical direct `materials.get_steel_stress` helper remains unchanged.

The [multilayer acceptance](../../planning/multilayer-member-workflow.md)
qualifies the complete rectangular case and retains independent reference
vectors, including mirrored bending and the existing flange branches. It does
not establish general axial/biaxial interaction or moment-curvature analysis.

The demand check applies `0.04*b*D` separately to the tension and compression
groups, as required by IS 456 clauses 26.5.1.1(b) and 26.5.1.2. Capacity outputs
name these limits `maximum_tension_steel_area_mm2` and
`maximum_compression_steel_area_mm2`. The existing
`maximum_total_steel_area_mm2` field remains a compatibility alias for the
per-group value; it must not be applied to the sum of both groups. The C# output
provides the corresponding `MaximumTensionSteelAreaMm2` and
`MaximumCompressionSteelAreaMm2` properties without changing its constructor.

AO03 checks clear spacing between every physical bar pair, including opposite
face labels. It uses a cover/link rectangle and one declared minimum spacing.
Use [AO26](wp05-detailing-constructability.md#full-reinforcement-arrangement)
for link bend corners and the more complete arrangement criteria.

Portable schemas, normalized code constants, projections, and expected values
are under `contracts/structural-engineering`. Conformance compares canonical
input identity and independently expected values; Python/.NET agreement alone
is not treated as independent engineering evidence.
