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
