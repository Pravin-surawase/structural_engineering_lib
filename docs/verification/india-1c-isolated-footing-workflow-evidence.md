---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-1C
---

# INDIA-1C Composed Isolated-Footing Workflow Evidence

INDIA-1C publishes the existing bounded concentric isolated-footing composition
through `structural_lib.services.api` and the package root. No footing structural
formula was rewritten in this packet.

## Supported outcome

`design_concentric_isolated_footing_is456(request)` composes the maintained
service-load sizing, factored flexure, one-way shear, punching shear, load-
transfer, and provided-bar detailing functions. It reports deterministic depth
candidates and fail-closed calculation, detailing, and aggregate statuses.

The request carries distinct service and factored load-combination identities.
Its service axial load must already include footing self-weight and overburden.
Allowable soil pressure and the effective supporting area are explicitly
approved external inputs with retained source and basis fields. Results retain
clause/source provenance and require qualified engineering review.

## Accepted public benchmark

The focused public-contract test fixes a 400 mm square column on a 2000 mm by
2000 mm M25/Fe415 footing under 800 kN service and 1200 kN factored concentric
axial load, with an approved allowable soil pressure of 200 kPa. At the fixed
500 mm overall thickness and 400 mm effective depths, it verifies:

- governing flexural moment: 192.0 kNm in each direction;
- final one-way shear utilization: 0.95648558 using actual provided steel;
- punching utilization: 0.63;
- provided load-transfer steel: 1256.6371 mm2;
- calculation, detailing, and aggregate statuses: `PASS`; and
- JSON serialization of the complete dataclass evidence carrier.

## Retained boundaries

Eccentric, partial-contact, and moment-transfer cases remain held, as do
combined, strap, raft and pile foundations. Settlement, soil-structure
interaction, lateral/sliding/uplift/global-overturning checks, edge/corner
punching, and stepped, sloped or arbitrary geometry are not claimed.

This packet receives focused tests, benchmark proof, architecture/import checks,
the quick repository gate, and required hosted PR checks. The broad Python suite
and full repository gate are intentionally deferred until INDIA-1A through
INDIA-1D are integrated, unless an earlier repository-wide outcome risk appears.
