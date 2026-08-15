---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-2C
---

# INDIA-2C Staircase Structural-Design Evidence

INDIA-2C composes the accepted INDIA-2B per-metre actions into one bounded
waist-slab design check. It does not add public consumers or promote staircase
capability from `HELD`.

## Implemented calculation boundary

`design_straight_flight_staircase()` checks:

- singly reinforced rectangular flexure using the accepted IS 456 stress block;
- minimum main and distribution reinforcement for the supplied steel grade;
- caller-provided main/distribution bar areas, diameters, and spacings;
- ordinary one-way concrete shear using the maintained Table 19/20 provider;
- the basic simply supported effective-span/effective-depth limit of 20; and
- integrity of the retained geometry/action carrier before design.

The result is `PASS`, `REVIEW_REQUIRED`, or `FAIL`. It never invents a
modification factor or treats software checks as professional approval.

## Independent benchmark

For `NPTEL-M9L20-EX9.1`, using M20 concrete, Fe415 steel, 224 mm effective
depth, 12 mm main bars at 120 mm, and 8 mm distribution bars at 160 mm:

| Quantity | Software | Published target |
|---|---:|---:|
| Factored moment | 68.0490 kNm/m | 102.08/1.5 = 68.0533 kNm/m |
| Limiting moment | 138.4492 kNm/m | capacity must exceed demand |
| Required main steel | 921.196 mm2/m | 920.64 mm2/m |
| Provided main steel | 942.478 mm2/m | about 942 mm2/m |
| Provided distribution steel | 314.159 mm2/m | about 314 mm2/m |
| Nominal shear stress | 0.21756 N/mm2 | 0.217 N/mm2 |
| Design concrete shear strength | 0.48616 N/mm2 | demand must be lower |
| Basic span/depth ratio | 22.7679 | basic limit 20 |

The required-steel difference is within the frozen 2 mm2/m tolerance because
the published example reads a rounded percentage from SP 16, while the library
solves the stress-block quadratic without table rounding.

The example returns `REVIEW_REQUIRED`: flexure, supplied bars, and ordinary
shear pass, but the unmodified basic L/d limit is exceeded. A shorter accepted
member below L/d 20 returns `PASS`; insufficient main steel and singly
reinforced capacity exceedance return `FAIL`.

## Retained holds

Modification factors, direct deflection, crack width, development-length
layout, landing torsion, bar selection, continuity, concentrated actions,
load generation/combinations, alternate stair systems, public service/FastAPI,
React, qualified review, and release remain outside this packet.

## Verification cadence

This packet receives focused safe/review/fail/integrity tests, architecture and
import checks, the quick gate, commit hooks, and hosted PR checks. Broad Python
and the full repository gate remain deferred until INDIA-2D is integrated.
