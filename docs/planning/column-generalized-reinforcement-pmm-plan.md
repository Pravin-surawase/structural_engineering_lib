---
owner: structural-math
status: active
last_updated: 2026-08-10
doc_type: spec
---

# Generalized Column Reinforcement and Experimental P-M-M Plan

## Decision

Implement a library-only rectangular section-analysis capability on a dedicated
branch. Preserve the existing symmetric Cl. 39.5 P-M API as a compatibility
route and preserve the Bresler Cl. 39.6 biaxial check as the supported
production route. The generalized fiber surface remains explicitly
experimental until independently benchmarked.

## Scope contract

Included:

- discrete longitudinal bars defined by `(x_mm, y_mm, area_mm2, material)`;
- a symmetric two-face adapter that preserves half of total steel on each face;
- rectangular-section concrete fiber integration with vectorized NumPy arrays;
- arbitrary intermediate, corner, edge, and multilayer bar coordinates;
- uniaxial slices at caller-selected neutral-axis orientations;
- discrete 360-degree P-M-M surface sampling and JSON-ready result types;
- regression validation of 0-degree and 90-degree slices against the existing
  supported P-M solver.

Excluded:

- changing the existing P-M or Bresler signatures or algorithms;
- FastAPI, React, CLI, Excel, or database integration;
- slenderness and second-order effects;
- circular sections, confinement models, seismic detailing, bar-diameter or
  spacing checks, and automatic reinforcement design;
- any claim of independent formula certification or professional approval.

## Formula and source mapping

| Calculation | Implemented mapping | Authority/evidence boundary |
|---|---|---|
| Concrete strain | Linear strain plane with 0.0035 extreme compression strain while the neutral axis is in-section; modified whole-section compression profile when it lies beyond the far face | IS 456 Cl. 38.1 stress-strain assumptions |
| Concrete stress | Parabolic-rectangular design curve with 0.446 fck peak and 0.002 plateau strain | Existing Cl. 38.1 constants and stress-block implementation |
| Steel stress | Existing five-point design stress-strain interpolation for each bar material | IS 456 Fig. 23 / SP:16 Table F implementation already used by the P-M solver |
| Net bar force | Steel force minus concrete displaced at the bar coordinate | Section equilibrium convention used by the current uniaxial solver |
| Section resultants | Sum of concrete-fiber and bar forces; `Mx=sum(F*y)`, `My=-sum(F*x)` | Explicit centroidal coordinate convention |
| Compression cap | `0.4 fck Ac + 0.67 fy Asc`, evaluated bar by bar | IS 456 Cl. 39.3 |
| Experimental status | No pass/fail design claim; Bresler remains production | Independent benchmark has not yet been completed |

## Acceptance evidence

Reference section: 300 x 500 mm, M25, Fe415, 3000 mm² total steel,
75 mm face-to-bar-centroid distance. Fiber comparison used 48 x 64 cells and
160 neutral-axis depths; the existing P-M comparator used 400 points.

| Pu (kN) | Mx difference vs existing P-M | My difference vs swapped-axis P-M |
|---:|---:|---:|
| 0 | 0.07% | 0.17% |
| 500 | 0.13% | 0.35% |
| 800 | 0.45% | 0.53% |
| 1200 | 0.82% | 0.88% |
| 1600 | 1.39% | 1.17% |
| 2000 | 4.21% | 3.11% |

The Cl. 39.3 nominal axial result is exactly 2304.15 kN for the reference
section. The larger near-cap difference is retained as an explicit experimental
boundary: the fiber integration and the existing SP:16 Table I interpolation
are not identical whole-section-compression formulations. Tests also prove that
an asymmetric layout containing an intermediate bar produces different
positive- and negative-axis capacities, so the solver does not collapse the
layout back to the former two-face idealization.

## Delivery state

- Generalized bar and layout types: complete.
- Symmetric compatibility adapter: complete.
- Uniaxial slice regression gate: complete for both principal axes.
- Discrete P-M-M sampling: complete as an experimental capability.
- Production replacement of Bresler: intentionally not done.
- Independent benchmark and qualified structural-engineering review: required
  before changing the capability status from experimental.
