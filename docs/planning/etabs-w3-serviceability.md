---
owner: Main Agent
status: active
last_updated: 2026-09-01
doc_type: reference
complexity: advanced
tags: [etabs, w3, serviceability, verification]
---

# W3E bounded serviceability

Base: accepted PR #936, merge `773d96739aaa68d5205d606010f0e0540dc4aa7c`.
This packet adds software checks, not acceptance of the actual building.
Exact local/hosted/merge results belong to the external task closeout.

## Chosen route and rejected shortcuts

Use the existing IS456 calculation owners through canonical Python/REST v2
and the W3 audit. No new solver, ETABS call, load-factor conversion or automatic
reinforcement inference is needed. The new `beam-serviceability-checks/v1`
variant requires both supported checks and explicit traceable inputs. The old
opaque dictionaries remain held; they are not silently reinterpreted.

| Supported check | Required evidence | Boundary |
|---|---|---|
| Cl 23.2.1 span/depth | Effective span, support, Figure 4/5 modification factors and their references | Rectangular beam, effective span <=10 m; basic ratios 7/20/26; factors externally justified within plotted limits. Not a displacement prediction. |
| Annex F flexural crack at tension surface | Service steel stress/modulus, mean surface strain, neutral axis, nearest longitudinal-bar surface distance, minimum longitudinal-bar cover, exposure, explicit limit and references | Separate service analysis; x < d, steel stress <=0.8fy, mean strain no greater than the unmodified elastic surface strain. No thermal, shrinkage, shear or other crack model. |

Member, station, face, width/depth/effective depth, service case, bar revision
reference and source digest travel with the input. Service and factored case
identities must differ. A W3 member supplies exactly one association per retained
strength row, by row id and digest. Each association must match station and face;
it is not a calculation of SLS forces from that strength row. Zero-moment face
associations and missing/extra/duplicate/stale associations fail closed.

The caller remains responsible for the complete service scenario envelope and
the provenance/physical validity of supplied factors, strains and bar geometry.
The software checks these values, not the truth of external calculations. The
service scenario is retained separately in the resulting W3 check. Either
service check failing changes the canonical result and W3 verdict to FAIL.
Optional old text stays UNAVAILABLE; required missing evidence blocks the whole
audit; justified NOT_APPLICABLE retains its existing explicit state.
Automatic detailing/BBS is held for this variant: a generated bar arrangement
is a new reinforcement revision and requires its own service analysis. The
supplied service PASS must not be transferred to a different generated layout.
The complete member association list is retained once in the build request.
Each output row carries only its own service evidence; indexed lookup avoids
repeated scans and copying the entire member list into every result row.

## Source review

Reviewed original IS456 pages 37–39 and 95 from the retained source PDF,
SHA-256 `6ec8f9033bc521420f2f550123edb6f0f444d9d3b7033a87b1b7ec569c143f8d`.
Its older amendment coverage is insufficient for exposure limits. The original
[consolidated standard and Amendment 4](https://studylib.net/doc/27999126/456-2000-amd5-reff2021)
were therefore checked together: Cl 35.3.2 limits particularly aggressive
very-severe/extreme categories to 0.1 mm. The bounded contract uses ceilings
0.3 mm only for non-harmful mild exposure, 0.2 mm for harmful/weather exposure,
and 0.1 mm for very-severe/extreme; a stricter caller limit is allowed.

The original [June 2024 Amendment 6](https://studylib.net/doc/27908701/rcc-is-456-amendment-no-6-june-2024)
changes materials/workmanship, bond and the torsion cross-reference, but does
not change Cl 23.2.1, Cl 35.3.2 or Annex F. These primary documents were read
through mirrors because the BIS temporary PDF URL no longer fetched. The
configured controlled-corpus identities are retained in the route source basis;
this Windows review does not claim a fresh byte match to that private corpus.
Review id: `ETABS-W3E-SERVICEABILITY-CLAUSES-23-35-ANNEX-F`.
No protected source prose/images enter Git.

## Root causes and prevention

| Cause | Implemented correction | Recurrence evidence |
|---|---|---|
| Untyped serviceability and silent defaults could not support canonical acceptance | Versioned complete strict variant; explicit factors, strain and limit; existing opaque route held | Invalid types, missing groups, methods, provenance and geometry rejected |
| Older very-severe default was 0.2 mm and EXTREME fell back to moderate | Shared owner now supports EXTREME and uses 0.1 mm for both aggressive categories; strict caller cannot loosen the ceiling | Independent 0.163636 mm case must FAIL at 0.1 mm |
| Factored demand could be mistaken for a service basis | Separate case/load/source evidence and exact row/location associations | Changing factored Mu does not change the supplied service calculation; mismatches block |
| A service check could be computed without affecting the parent result | Existing compliance aggregate and W3 service governor consume both checks | Independent deflection and cracking failures propagate through canonical and W3 |
| Source review id was hashed internally but absent from public canonical provenance | Expose route source ids and review id with the canonical result | Public result traceability assertion |
| Automatic detailing could select bars different from the supplied service basis | Explicit serviceability detailing/BBS hold until new layout reanalysis/binding exists | Direct and combined consumer diagnostic rejects before producing detailing |
| Repeating the whole member service list in every result inflated review size quadratically | Keep only row-specific evidence in row results and index associations once | Existing complete-domain/replay/Node fixtures reconcile with smaller serialized review |

Independent hand vector: L/d = 5000/500 = 10, allowable = 20×1.2×1.1 = 26.4;
crack width = 0.180/1.100 = 0.1636363636 mm. Regression evidence uses synthetic
inputs only. Focused Python, API, W3J, types, architecture, quick/hooks/hosted
gates follow the frozen source. Preserve historical review fixtures; generate
the newly named serviceability revision after the last source-byte change.

## Remaining W3 sequence

1. Accept this bounded software packet, then supply project-specific service
   analysis and bar/factor evidence. Missing actual-building data stays held.
2. Use the supported torsion distribution/BBS consumer for rectangular beams at
   or below its 450 mm width limit. Resolve wider, multilayer or coupled-design
   candidates separately; do not promote them through the bounded route.
3. Resolve H physical support/mesh/slab-transfer compatibility. The three saved
   candidates remain NOT_COMPARABLE_AS_IS; broader getters cannot fix that.
4. Only after E/H/R dependencies are accepted, implement I screening, K/L and
   cumulative integration/Mac review. Keep the broad 32-check gate for cumulative
   W3 closeout unless a material cross-domain risk requires it earlier.

Detailed direct/long-term deflection, spans over 10 m, automatic Figure 4/5
interpolation and full SLS scenario acquisition are separately bounded work.
No reliable whole-W3 completion time follows from this packet: H route choice
and missing physical evidence still determine the remaining effort. No release,
professional approval or construction-use claim is made.
