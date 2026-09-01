---
owner: Main Agent
status: active
last_updated: 2026-09-01
doc_type: migration
tags: [beam, api, websocket, compatibility]
---

# Supplied-beam check V1 to V2 migration

`POST /api/v1/design/beam/check` keeps its path and OpenAPI operation ID,
`check_beam_api_v1_design_beam_check_post`. Its former flat request was not a
truthful supplied-reinforcement check: accepted compression steel, effective
depth, stirrup area, and stirrup spacing did not all reach the engineering
calculation. The route now rejects that flat shape before calculation and
accepts only `beam-supplied-check/v2`.

## V1 field disposition

`DEPRECATED` means the old spelling is no longer accepted at this route and the
row gives its explicit V2 replacement. `REJECTED` means no compatibility value
is inferred. The route never silently ignores an accepted field.

| V1 field or behavior | Disposition | V2 replacement or reason |
|---|---|---|
| `width` | `DEPRECATED` | `section.b_mm` |
| `depth` | `DEPRECATED` | `section.D_mm` |
| `moment` | `DEPRECATED` | `actions.mu_knm` |
| `shear` | `DEPRECATED` | `actions.vu_kn`; omission is rejected instead of defaulting to zero |
| `ast_provided` | `DEPRECATED` | `reinforcement.tension`, with explicit diameter and bars per layer |
| `asc_provided` | `DEPRECATED` | `reinforcement.compression_or_hanger`, with explicit layers |
| `stirrup_area` | `DEPRECATED` | `reinforcement.stirrup_diameter_mm` plus `reinforcement.stirrup_legs`; area is calculated from those declared dimensions |
| `stirrup_spacing` | `DEPRECATED` | `reinforcement.stirrup_spacing_mm` |
| `fck` | `DEPRECATED` | `materials.fck_nmm2` |
| `fy` | `DEPRECATED` | `materials.fy_nmm2`; also provide `materials.fy_transverse_nmm2` |
| `clear_cover` | `DEPRECATED` | `reinforcement.clear_cover_mm`; a derived depth basis must repeat the same cover explicitly |
| `effective_depth` | `DEPRECATED` | Supply exactly one of `section.d_mm` or `section.effective_depth_basis` |
| Flat V1 object, partial V2 object, unknown fields, numeric strings, booleans as numbers, or non-finite values | `REJECTED` | HTTP returns a typed 422 problem; WebSocket returns terminal `beam-supplied-check-error/v2` with `ERROR` |
| Hidden defaults for identity, tension face, bar layout, selection constraints, support widths, or source references | `REJECTED` | These facts must be supplied explicitly. Omitted support widths produce a typed engineering `HOLD`, not an adequate Boolean |

Every accepted V2 engineering field is consumed by the shared supplied-check
service or carried into its canonical request/result evidence. In particular,
effective depth, compression/hanger layers, actual tension-steel area, stirrup
diameter/legs/spacing, bar type, bend flags, selection constraints, support
basis, source references, identity, tension face, and correlation identity are
not transport-only values.

## Result and transport behavior

REST and WebSocket return the same `beam-supplied-check-result/v2` data object.
The terminal status vocabulary is `PASS`, `FAIL`, `HOLD`, and `ERROR`; normal
engineering results use the first three, while transport/intake failures use
the error contract. `HOLD` must never be converted to an adequate Boolean.

The WebSocket client message is `{"type":"check_beam","params":<V2 request>}`.
It emits exactly one terminal `check_result` or `error` message and preserves
`correlation_id`. The checked-in machine schema is
[`beam-supplied-check-websocket-v2.schema.json`](../reference/beam-supplied-check-websocket-v2.schema.json).
The live HTTP request/response schema remains authoritative in `/openapi.json`.

## Maintained callers

- Python: `StructuralDesignClient.check_supplied_beam_v2(request)`
- TypeScript: `StructuralDesignClient.checkSuppliedBeam(request)`
- React: `checkSuppliedBeam(request)`
- Python facade: `structural_lib.design.is456.beam.check_supplied(request)`

Callers must build the nested V2 request; there is intentionally no automatic
flat-payload adapter because the old area-only inputs cannot reconstruct exact
bar layers, transverse steel, source references, or a complete effective-depth
basis.
