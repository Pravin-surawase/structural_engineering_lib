---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: verification
task: INDIA-2-FOUNDATION-STRAP-A
---

# INDIA-2 Foundation Strap A Analysis Evidence

## Scope and retained boundary

This packet implements only the G0-frozen two-footing property-line analysis:
strict typed topology/action/approval inputs, reaction statics, equal uniform
net-pressure eligibility, gross service bearing, clear-strap shear and moment,
and vertical/moment equilibrium. Strap strength, the public composition,
FastAPI transport, capability promotion, React, release, broad Python, and the
full 30-check gate remain outside this packet.

The contract requires separate caller-qualified references for both footing
slabs, transfer regions, reinforcement/anchorage, supporting areas, settlement,
and construction clearances. It fails closed for strap soil contact, unequal
pressure, independently factored actions, unsupported topology/actions, missing
approvals, non-finite values, or absent provenance.

## Frozen and independent evidence

`INDIA-2-STRAP-HAND-01` reproduces `1200/1600 kN` service reactions,
`200 kN/m2` equal net pressure, `220 kN/m2` gross service pressure, `0.88`
bearing utilization, and exact service/factored vertical and moment closure.
The clear-strap faces reproduce service `V = 174.4375/141.4375 kN` and
`M = -611.125/-176.796875 kN m`; the factored envelope is `261.65625 kN`
shear and `916.6875 kN m` top-tension moment. Setting the strap line load to
zero independently reproduces the source reaction equations. A valid bearing
failure returns `False`; inputs outside the frozen domain raise the typed
contract error without a design result.

## Provenance and cadence

The implementation carries normalized Clause 34 identities, the controlled
base/amendment source IDs, the IISc/NPTEL strap-model identity, the frozen hand
benchmark ID, and caller references. No source scan, protected prose, or table
image is committed. Focused gates run for A; broad Python and the 30-check gate
remain deferred to the final INDIA-2 boundary unless a confirmed repository-
wide failure forces either earlier.

## Verification

- Direct STRAP-A benchmark/boundary tests pass.
- Formatting, lint, typing, architecture, imports, deterministic manifest,
  maintained indexes/links, source binding, and the quick gate pass.
- Capability remains held at `12 supported / 9 held`; its limitation now says
  G0 and A exist while strength/publication remain pending.
- Exact candidate commit/tree, independent audit, hosted checks, and merge
  identity are bound by the packet Git handoff receipt.
