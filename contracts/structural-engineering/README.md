# Structural engineering semantic contracts

This directory is the language-neutral authority for the reusable Python and
.NET libraries. An operation keeps the same semantic identifier, units, result
states, provenance meaning, and conformance values in both languages even when
its public language projection uses idiomatic names.

The interchange boundary uses explicit operation-specific units. Design checks
normally use millimetres, square millimetres, N/mm², kN, kNm, kg/m³, and kg/m;
the WP03 analysis boundary uses mm, N, Nmm, and radians to avoid hidden solver
conversion. All numbers must be finite before identity calculation.
`normalized_input_id` is SHA-256 over compact UTF-8 JSON with lexicographically
ordered object keys, preserved array order, canonical enum strings, and units
already normalized to this boundary. Presentation rounding is never hashed.

Folders have one purpose:

- `operations/` declares semantic operations, inputs, outputs, and projections.
- `schemas/` declares portable interchange records.
- `code-data/` contains normalized calculation constants and provenance.
- `conformance/` contains independently expected values and cross-language
  canonicalization vectors.

Run `./scripts/python_runtime.sh scripts/validate_structural_engineering_contracts.py`
after changing any contract artifact.

WP05 code data applies IS 456 Amendment 6 to epoxy-coated deformed bars and
binds the seismic beam profile to IS 13920:2016 Amendment 2. Its source and
scope decisions are documented in
`docs/library/reference/wp05-detailing-constructability.md`.

WP06 adds the immutable project/profile basis, profile-derived complete-member
aggregation, and exact reinforcement centreline path contracts. It carries no
new code table: every member leaf remains bound to the code-data revision of
its originating operation. Its signatures and geometry rules are documented
in `docs/library/reference/wp06-project-member-paths.md`.
