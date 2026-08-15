---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-1B
---

# INDIA-1B rectangular-column decision evidence

## Decision

The stable IS 456 column decision remains bounded to solid rectangular tied
sections. `design_column_is456()` and `design_long_column_is456()` accept one
total longitudinal-steel area, `Asc_mm2`, and one face-centroid depth,
`d_prime_mm`. The maintained section calculation therefore represents equal
steel area on two opposite faces; it does not represent individual perimeter
bars, unequal face steel, or arbitrary layers.

Circular-section design, asymmetric/perimeter-resolved reinforcement, and
arbitrary multilayer layouts remain held for separate approved packets. The
supplied circular-helix check is retained as a bounded reinforcement check and
does not make circular-column design supported.

The calculation-only module `codes.is456.column.pmm` remains experimental. It
has an independent oblique strain-plane benchmark, but it has no stable service
facade, no stable safety-decision result, and excludes slenderness, second-order
response, confinement, detailing, and automatic design. INDIA-1B therefore
does not promote it or use it to broaden the stable column claim.

## Governing model and provenance

- Standard: IS 456:2000, fourth revision.
- Stable member routes: effective length and classification under Cl. 25.1.2
  and Table 28; minimum eccentricity under Cl. 25.4; rectangular short-column
  interaction under Cl. 39.5 and 39.6; additional moment/slender member route
  under Cl. 39.7.
- Reinforcement model: `Asc_mm2 / 2` on each of two opposite faces at
  `d_prime_mm`, using explicit mm, N/mm2, kN, and kN m units.
- Existing independent vectors: the maintained column golden-vector suite
  records IS 456/SP:16 provenance and tolerances for classification, minimum
  eccentricity, axial, uniaxial, biaxial, and slender-column outcomes.
- Experimental evidence: `column-pmm-benchmark.md` checks one 45-degree
  strain plane analytically but explicitly does not prove a supported design
  decision.

## Executable boundary

The capability contract names only `design_column_is456` and
`design_long_column_is456` as stable column workflows. An integration
regression asserts that the stable signature exposes `Asc_mm2` and
`d_prime_mm`, exposes no arbitrary reinforcement or section-shape input, and
that both experimental PMM functions are absent from `services.api.__all__`
and `structural_lib.__all__`.

Unsupported layout and geometry cases fail closed at the public contract: they
cannot be expressed as supported stable inputs. Direct imports from the
experimental module remain expert/internal use and carry their experimental
warnings.

## Acceptance and remaining boundary

INDIA-1B closes the geometry/layout decision without changing structural math
or claiming a wider design model. Focused golden vectors, capability semantics,
manifest generation, architecture/import checks, the quick gate, commit hooks,
and hosted PR checks are the packet evidence. Broad Python and full repository
gates are deferred to the cumulative INDIA-1A through INDIA-1D closeout under
the owner-approved validation cadence.

Software verification is not qualified structural-engineering review or
professional design approval. The cumulative qualified review remains required
before stable or engineering-use approval.
