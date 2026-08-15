---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-2-CUMULATIVE
---

# INDIA-2 Cumulative Gate Evidence

INDIA-2A-D are integrated through exact `origin/main`
`18da6c112e67af49d8adf32bf0babf65285e2cd4`. The cumulative gate packet ran
from that SHA in the isolated `codex/india-2-cumulative-gates` lane with
`source_bound=true`; the unrelated primary checkout and sibling worktrees were
not modified.

## Integrated packet receipts

| Packet | Pull request | Integrated SHA | Outcome |
|---|---:|---|---|
| INDIA-2A | #760 | `1cd08b9cab20a34b9dad1806f500eef01a2f4739` | One straight-flight scope and benchmark frozen |
| INDIA-2B | #761 | `5bf8c0b50c62f144847e032ec436f6d0522acf8e` | Geometry and equilibrated actions implemented |
| INDIA-2C | #762 | `bb1abd1818028118f92b1f7c8b0ed1ba57994fdf` | Structural checks and dispositions implemented |
| INDIA-2D | #763 | `18da6c112e67af49d8adf32bf0babf65285e2cd4` | Typed Python/FastAPI workflow published |

## Cumulative validation

- `./run.sh test`: 5,950 passed, 3 skipped, 6 deselected, with 46 warnings in
  41.96 seconds.
- `./run.sh check`: 30/30 passed in 10.0 seconds.
- The generated Indian-code manifest is current. Its informational capability
  view reports 8 supported and 13 held families out of 21; there is no unknown
  capability status.
- `IS456:2000:stair` remains `SUPPORTED` / `IMPLEMENTED_BOUNDED` with exactly
  one public workflow, `design_straight_flight_staircase_is456`.
- The staircase completeness check reports `L2 API Complete`: one Python API,
  one tested FastAPI router, 19 discovered Python test functions, and no React
  claim.
- The API manifest and OpenAPI baseline are current with no drift.

## Essential integrated review

The Python public facade, service result, capability registry, FastAPI request
and response models, route, generated manifests, and OpenAPI identity agree on
the same bounded workflow. The router delegates calculation to the service and
adds no engineering math. Request validation rejects non-finite and alternate-
scope inputs; capacity exceedance remains a JSON-safe `FAIL` with an explicitly
unevaluated nullable steel limit.

The public workflow reproduces IIT Kharagpur NPTEL Example 9.1 at 5100 mm
effective span, 68.048997 kNm/m factored moment, and 921.196 mm2/m required main
steel. Its aggregate disposition remains `REVIEW_REQUIRED`, not `PASS`, because
the unmodified span/depth ratio is 22.7679 against the bounded basic limit of
20. Shorter accepted and insufficient-steel cases retain `PASS` and `FAIL`.

## Claim boundary

The supported scope is one cast-in-situ solid longitudinal straight waist-slab
flight with two collinear landing effective segments spanning between outer
beam or wall supports. Horizontal-plan actions use explicit concrete
self-weight, caller-supplied superimposed service loads and landing shares, and
an explicit ultimate factor.

Alternate stair systems, transverse/stringer action, IS 875 load generation,
project combinations or envelopes, continuity, redistribution, modification
factors, direct deflection, crack width, development-length layout, landing
torsion, automatic bar selection, React, and every other held capability remain
outside INDIA-2. Qualified structural-engineering review, professional
approval, release authorization, and branch/worktree cleanup remain separate
holds.
