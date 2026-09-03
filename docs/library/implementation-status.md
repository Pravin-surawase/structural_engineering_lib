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
