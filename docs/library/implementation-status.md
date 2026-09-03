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
