# WP01-WP08 implementation status

This record captures the review performed after each work packet and any change
to the next packet before implementation continues.

## WP01 review

State: implemented and focused verification passing.

Confirmed outcomes:

- Python and .NET expose FO01-FO04, AO03, and AO06 with the same semantic IDs.
- Canonical input bytes and normalized IDs match for common vectors.
- Effective inputs remain distinct from outputs and retain density, profiles,
  section data, bars, faces, and code-data revisions.
- Actual bars carry physical face, coordinate, diameter, and layer.
- Rectangular singly/doubly and eligible flanged positive/reverse bending cases
  are calculated; unsupported axial interaction cannot qualify.
- The pure packages have no Excel, ETABS, UI, HTTP, or renderer dependency.

Corrections made during review:

- Replaced the initial .NET envelope that stored outputs as effective inputs.
- Replaced one-face inferred reinforcement with explicit face/layer geometry.
- Treated flange-in-tension reverse bending as a supported web-section check.
- Added result identity separately from normalized input and calculation IDs.

WP02 plan update:

- Shear and torsion will accept actual transverse-link geometry, rather than
  required link area alone.
- Torsion interaction will require one concurrent action row containing shear,
  torsion, and bending components; component envelopes will be rejected.
- Axis and link-perimeter identity will be explicit so WP03 normalization can
  bind vendor actions without changing the engineering operation.

## WP02 review

State: implemented and focused verification passing.

Confirmed outcomes:

- FO05 evaluates Table 19/20 concrete limits and actual axis-specific link
  capacity, minimum provision, and spacing.
- AO07 checks signed station demands on V2 and V3 without mixing their section
  or active-leg bases.
- AO08 binds shear, torsion, and flexure to one concurrent source row and checks
  actual closed links and identified corner bars.
- Missing actual reinforcement remains `not_evaluated`; invalid input,
  unsupported scope, and completed engineering failure remain distinct.

Corrections made during review:

- Nonzero V3/M2 interaction now returns `not_applicable` for the bounded WP02
  profile instead of preserving and then silently ignoring those components.
- Torsion effective depth now follows the physical primary tension face.
- Link centre dimensions must fit the concrete section, both link directions
  need active legs, and perimeter ids must resolve four physical corners.

WP03 plan update:

- The action normalizer must preserve all six components and mark their
  concurrency basis before any design operation consumes a row.
- Topology must bind physical faces, local axes, support faces, span measures,
  section regions, and analysis elements without deriving them from load sign.
- The beam-line solver remains a bounded planar major-axis solver; unsupported
  minor-axis response stays visible in the normalized snapshot rather than
  being discarded.

## WP03 review

State: implemented and focused verification passing.

Confirmed outcomes:

- AO01 normalizes station, force, and moment units while preserving source,
  model, analysis/result epoch, member/span/object/element/station/case/step,
  local-axis, concurrency, and same-row P/V2/V3/T/M2/M3 identity.
- AO15 binds separate left-face, centre, and right-face support coordinates to
  clear, centreline, and effective design spans. Section regions and analysis
  elements must cover each physical span without gaps or overlap.
- AO02 solves the bounded planar V2/M3 Euler-Bernoulli profile with nodal,
  uniform, point, and prescribed support-movement inputs. It reports physical
  span/analysis element station identity and force/moment equilibrium.
- Python and .NET match the action-row and snapshot canonical identities and
  the closed-form simply supported UDL response.

Corrections made during review:

- Added the omitted WP02 portable request schema discovered by the
  prior-packet review.
- Changed the first .NET normalizer from an interaction-check gate to a source
  snapshot service, so component/design envelope classifications remain
  visible and are not silently converted or rejected during normalization.
- Replaced the first .NET single-face topology model with explicit support
  left/centre/right faces and exact region/mapping coverage.
- Replaced interpolated .NET station results with solved station degrees of
  freedom and calculated action fields, and exposed calculated equilibrium
  residuals instead of placeholder values.
- Kept free-force and free-moment residuals dimensionally separate.

WP04 plan update:

- FO07 and AO09 will distinguish span/depth screening from calculated
  deflection; a screen cannot be presented as a calculated displacement.
- Deflection inputs will bind the service action case, analysis result identity,
  cracked/uncracked stiffness basis, and explicit short-term, creep, shrinkage,
  and sustained-load assumptions.
- FO08 and AO10 will use the actual tension-face bar coordinates, diameters,
  spacing, cover, strain/stress basis, exposure, and declared crack criterion.
- Serviceability operations will preserve missing evidence as `not_evaluated`
  and unsupported methods as `not_applicable`; neither can qualify the later
  complete-member result.

## WP04 review

State: implemented and focused verification passing.

Confirmed outcomes:

- FO07 resolves separate total-final and after-finishes limits with an explicit
  code, project, or supplied source. An override can be stricter but cannot
  weaken the applicable code limit.
- FO08 maps harmful cracking and exposure to 0.3, 0.2, or 0.1 mm ceilings and
  applies the same explicit-source rule.
- AO09 keeps the bounded span/depth screen separate from calculated component
  aggregation. The calculated branch retains total and sustained service rows,
  analysis and reinforcement identities, short/long-term components, load and
  finish chronology, environmental values, and named calculation methods.
- AO10 evaluates Annex F flexural crack width from the physical tension face,
  area-weighted effective depth, minimum clear cover, supplied mean strain, and
  distance from the checked surface point to the nearest actual bar surface.
- Python and .NET match the exact component-aggregation and arrangement-sensitive
  Annex F vectors. Missing calculation history, actual bars, or mean strain is
  `not_evaluated`; a valid limit exceedance is an engineering failure.

Corrections made during review:

- Replaced the first .NET-specific bar record with the shared `BarCoordinate`
  contract and restored member, station, service-row, reinforcement-revision,
  and physical-face identity.
- Added the omitted effective depth and actual L/d evaluation to the .NET
  screening branch, and replaced method labels with the required numeric load,
  finish, duration, humidity, and notional-size evidence.
- Corrected effective depth to an area-weighted distance from the compression
  face and corrected `acr` to measure to the nearest bar surface rather than its
  centre.
- Populated every calculated deflection component in the .NET result and added
  validation for source, support, tension-face, and bar-face enum values.
- Rejected branch-specific displacement limits on a screening request and
  rejected invalid bar-face identity instead of retaining ignored inputs.
- Replaced the compact initial .NET draft with readable public contracts,
  operations, and tests.

WP05 plan update:

- AO11 anchorage will check the actual available bar path from a named critical
  section through support faces, bends, hooks, bond conditions, bar stress, and
  diameter. Required development length alone will not qualify a bar.
- AO12 lap and curtailment will retain each bar mark, physical face, start/end
  stations, splice zone, stagger group, continued steel, and shear demand near
  cutoffs. It will not assume that required area exists along the full span.
- AO13 seismic detailing will require an explicit IS 13920 applicability and
  context profile. Ordinary IS 456 members remain visibly not applicable to a
  seismic-only rule rather than silently passing it.
- AO26 arrangement checks will use actual coordinates, layers, cover, clear
  spacing, link/core geometry, bend space, and support-zone congestion. Area
  equivalence alone cannot establish constructability.

## WP05 review

State: implemented and focused verification passing.

Confirmed outcomes:

- FO06 calculates development length from the actual bar diameter and stress,
  concrete grade, bar surface, stress state, and bundle size. The normalized
  Amendment 6 epoxy modifier is explicit in the result and code-data revision.
- AO11 checks usable straight bar path and credited scheduled bends from a
  named critical section. Simple supports use the separate near face and
  centreline evidence required for the moment/shear-plus-Lo criterion.
- AO12 checks actual splice zones, lap or qualified-coupler evidence, percentage
  spliced, stagger group, termination extension, continuing steel at the demand
  station, anchorage, shear at cutoff, and any explicitly required extra links.
- AO13 makes the IS 13920 applicability decision visible and requires the full
  member, joint, bar, link-zone, anchorage, dependent-joint, and capacity-shear
  evidence for the supported seismic profile.
- AO26 evaluates the complete physical arrangement: section and link cover,
  cage closure and bend fit, bar enclosure, all bar collisions, aligned-row and
  physical-layer clearances, role centroids, obstacles against bars and each
  numbered cage segment, and the declared placement opening.
- Python and .NET publish matching typed requests and results, operation
  identities, optional inputs, code-data revisions, and conformance examples.

Corrections made during review:

- Replaced the legacy simplified schedule assumptions with actual bar paths,
  faces, station demands, splice and cutoff records, and qualified dependent
  result references.
- Kept the 36 mm restriction specific to lap splices; a larger bar can use a
  qualified coupler with installation evidence.
- Made extra-link evidence conditional on the detail declaring that it is
  required, and made that decision an explicit required field in both language
  contracts.
- Required exact operation identities for anchorage and shear dependencies so
  an unrelated passing result cannot qualify a curtailment or seismic check;
  seismic anchorage and joint results are also bound to their exact face and
  joint so duplicate evidence cannot qualify missing locations.
- Ordered physical layers from actual coordinates instead of trusting user
  layer numbers, and included link segments in obstacle checks.
- Aligned .NET link-segment numbering and optional prohibited-zone input with
  the Python and JSON wire contracts.

WP06 plan update:

- AO14 will create an immutable versioned project and design profile containing
  selected code-data revisions, required operations, criteria, accepted action
  bases, material and detailing rules, and catalogue identities.
- AO17 will compose existing leaf results without repeating their formulas. A
  member qualifies only when every profile-expected leaf is present, current,
  complete, applicable where required, and passing; rejected, partial, stale,
  or unqualified `not_applicable` evidence remains visible and disqualifying.
- AO18 will resolve each selected bar into a mark, count, diameter, physical
  role and layer, tangent straight segments, bend arcs, hooks, and exact start
  and end stations. Those paths feed AO11, AO12, and AO26 rather than assuming
  required steel continues for the full span.
