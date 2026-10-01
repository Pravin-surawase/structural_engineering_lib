# WP04 beam serviceability

WP04 publishes four host-free IS 456 operations. FO07 resolves deflection
limits, FO08 resolves crack-width limits, AO09 evaluates either a span/depth
screen or an explicit component-based deflection result, and AO10 calculates
Annex F flexural crack width from actual bar geometry. Excel and ETABS adapters
may construct these requests, but the operations do not access either host.

The [typed beam checks example](../../../Python/examples/beam_checks_workflow.py)
shows screening, supplied-component deflection and actual-bar crack width.
Run `python3 Python/examples/beam_checks_workflow.py` with the current source
build. Its service components and strain are explicit teaching inputs, not
results inferred from the elastic solver. Omitting duration or strain produces
an unevaluated result in the same example.

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

The supplied creep multiplier is the additional/initial permanent-load
deflection ratio established by its named model. It is not automatically the
material creep coefficient theta: cracked-section stiffness can change.

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


## Legacy scalar Annex C correction — 1 October 2026

The separate `codes/is456/beam/serviceability.py` Level-B/C helpers have a
bounded source-defined profile `IS456_ANNEX_C_RECT_SINGLE_V1`. They are not
WP04's supplied-component operation and do not populate its chronology or
provenance by inference. Existing WP04/physical-beam code remains unchanged.

Derive elastic section equilibrium and deflection from mechanics; original
standards define the code-specific empirical relationships. Comparator source
and independent benchmarks provide additional evidence. NPTEL is supporting
reference material only. Direct inspection of original
[IS 456 Annex C, printed pages 88–89](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=101)
and [Cl. 6.2.5.1](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=29)
identifies these corrections:

- C-2.1 effective inertia uses `Icr/[1.2-(Mr/M)(z/d)(1-x/d)(bw/b)]`, with
  `Icr <= Ieff <= Ig`. For the supported rectangle `bw/b=1`, `z=d-x/3`.
  The former cubic Branson blend was a different model with incorrect IS attribution.
- C-4.1 computes additional permanent-load creep as the difference between
  long-term and initial deflection. `Ec_eff=Ec/(1+theta)` changes the modular
  ratio, neutral axis, cracked inertia and effective inertia; multiplying
  the initial deflection by theta at fixed inertia is not this procedure.
- C-3.1 uses overall depth `D`: `phi_sh=k4*eps_cs/D`. The source-defined
  percentage-based k4 branches and support k3 values remain empirical code
  approximations; they are not replaced by an accuracy claim.
- The source default ultimate theta is `2.2/1.6/1.1` at loading ages
  `7/28/365 days`. The previous humidity/size equation, clamping and its
  nonexistent Table C.2 attribution are removed. Intermediate ages need
  a selected model; humidity/size context does not invent a calibration.
- Double integration of `EI*v''=M(x)` gives `5*Mmid*L²/(48*EI)` for SS UDL
  and `Mroot*L²/(3*EI)` for a cantilever end point load. The old `1/2`
  cantilever coefficient corresponded to a different load pattern despite
  its end-point label. Negative moments use magnitudes and zero external
  moment retains the shrinkage estimate.

The scalar profile supports singly reinforced rectangles with elastic service
steel, same-direction unfactored permanent/live actions, and either SS UDL or
cantilever end point loading. Concrete default linear creep is limited to
permanent-load stress no greater than `fck/3`; default material parameters above
M55 need additional data. This is a source-default ultimate estimate, not a
finite-time, cyclic, construction-history or post-finishes calculation.

| Missing basis or domain | Current result |
|---|---|
| Level B duration and one moment, without permanent load/loading age/shrinkage | `HOLD_UNSUPPORTED`, with immediate outputs when qualified |
| Cracked helper call without neutral-axis and effective-depth geometry | `ValueError` naming the missing C-2.1 basis |
| Shrinkage helper call without overall D or with `pt-pc < .25%` | Unsupported; no extrapolation |
| Continuous scalar support, without support/midspan moments | `HOLD_UNSUPPORTED`; no assumed `.6` factor or blended support coefficient |
| Compression steel without its depth/layout | `HOLD_UNSUPPORTED`; no assumed bar position |
| Opposing sustained/live moments, unsupported loading age or nonlinear creep stress | `HOLD_UNSUPPORTED`; no safe total |

Unsupported results have `is_ok=False`, `computed.status=HOLD_UNSUPPORTED`, a
specific reason and no finite qualified total (`delta_total_mm=inf`). Direct
helpers raise `ValueError` for missing basis. The legacy duration multiplier
remains an explicitly unqualified compatibility helper and is not used by an
IS456 Level-B/C total check. Additional geometry keywords on direct helpers
are compatibility changes documented here rather than silently inferred.

Independent fixtures in
[`sls_annexc_reference.json`](../../../Python/tests/data/benchmark_vectors/sls_annexc_reference.json)
use 60-digit Decimal equilibrium and virtual-work integration, with 62 numerical
states and eight retained unsupported domains. Raw predecessor/new-model results
and isolated-wheel evidence are retained with the material packet. Latest complete
IS amendment-set verification remains open; the controlled Amendment-5 copy and
targeted Amendment-6 check do not certify every later edition or material type.
