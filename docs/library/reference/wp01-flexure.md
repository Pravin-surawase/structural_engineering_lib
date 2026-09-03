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

Flexural capacity resolves tension and compression steel from actual bar
coordinates. It solves force equilibrium, applies the IS 456 limiting neutral
axis, reports brittle over-reinforcement as engineering failure, and retains
minimum and maximum longitudinal steel criteria for the demand check.

Portable schemas, normalized code constants, projections, and expected values
are under `contracts/structural-engineering`. Conformance compares canonical
input identity and independently expected values; Python/.NET agreement alone
is not treated as independent engineering evidence.
