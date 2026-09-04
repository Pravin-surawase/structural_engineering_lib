# WP04 beam serviceability

WP04 publishes four host-free IS 456 operations. FO07 resolves deflection
limits, FO08 resolves crack-width limits, AO09 evaluates either a span/depth
screen or an explicit component-based deflection result, and AO10 calculates
Annex F flexural crack width from actual bar geometry. Excel and ETABS adapters
may construct these requests, but the operations do not access either host.

## Deflection limits and screening

`deflection_limit` / `Serviceability.DeflectionLimit` distinguishes total final
deflection from deflection occurring after finishes are installed. The code
limits are L/250 and the smaller of L/350 or 20 mm, respectively. A project or
supplied limit must be selected explicitly, must be positive, and cannot be
less restrictive than the applicable code limit.

The span/depth branch requires the effective span, effective depth, support
condition, three explicit modification factors, and references for the span
and factor basis. It compares the actual L/d ratio with the modified basic
ratio of 7, 20, or 26. Its result kind is
`screening_not_calculated_displacement`; it never reports a calculated
deflection in millimetres.

## Calculated deflection

The calculated branch accepts externally evaluated, positive-downward
components and the identities that produced them. It requires the service
action snapshot, separate total and sustained action rows, analysis result,
reinforcement revision, effective span, load and assessment ages, sustained
duration, humidity, notional size, finishes history, and named stiffness,
cracking, creep, and shrinkage methods.

The aggregation is:

```text
creep additional = instantaneous sustained * creep multiplier
total final       = instantaneous total + creep additional + shrinkage
after finishes    = max(0, total final - deflection at finish installation)
```

This operation does not predict creep, shrinkage, cracking, or effective
stiffness from incomplete evidence. Missing conditional evidence produces a
completed `not_evaluated` result. Invalid chronology or component geometry is
rejected input.

## Crack-width limits and Annex F calculation

`crack_width_limit` / `Serviceability.CrackWidthLimit` selects 0.3 mm only for
non-harmful cracking under mild exposure, 0.2 mm for harmful cracking or
weather/moderate/severe exposure, and 0.1 mm for very severe or extreme
exposure. A project or supplied value may make the criterion stricter but may
not exceed the applicable ceiling.

The Annex F operation requires a member, station, service action row,
reinforcement revision, physical top or bottom tension face, section and
neutral-axis geometry, service steel stress, steel properties, a supplied mean
tension-surface strain, and actual positioned longitudinal bars. It computes:

```text
d    = area-weighted tension-steel depth from the compression face
cmin = minimum clear cover from the tension face to a bar surface
acr  = distance from the checked surface point to the nearest bar surface
wcr  = 3 * acr * mean strain / (1 + 2 * (acr - cmin) / (h - x))
```

The bounded profile requires `0 < x < d < h`, service stress no greater than
`0.8 fy`, and supplied mean strain no greater than
`fs/Es * (h-x)/(d-x)`. Missing bars or strain remains `not_evaluated`.
Geometrically or materially invalid inputs are rejected. A valid calculation
that exceeds its limit is a completed engineering failure.

The conformance corpus includes equal-area arrangements with different bar
spacing. Their crack widths differ because `acr` uses the nearest actual bar
surface rather than an equivalent reinforcement area.
