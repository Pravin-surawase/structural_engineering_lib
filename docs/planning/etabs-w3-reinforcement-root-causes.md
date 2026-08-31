---
owner: Main Agent
status: active
last_updated: 2026-08-31
doc_type: reference
complexity: advanced
tags: [etabs, w3, root-cause, verification]
---

# W3 reinforcement root causes and prevention

## Decision and scope

The saved-source audit exposed representation gaps; tracing their actual
consumers exposed numerical defects. Fix the existing contracts, depth resolver,
shear/torsion owners and their real callers before enabling more checks.
This packet follows PR #935 merge `349502d31236680d32d58f7ff2d412d279f3e10f`.
It performs no ETABS/COM/UI/export/solver/model operation. All test models are
authored software fixtures. They are not acceptance of the actual building.

The [verification receipt](../verification/etabs-w3-reinforcement-root-causes.json)
records the bounded evidence. Required automated checks must pass before merge;
the external closeout owns the final commit/check identities.

## Root-cause register

| ID | Confirmed cause and impact | Implemented correction | Prevention / real outcome evidence |
|---|---|---|---|
| RC1 | One `fy` cannot retain FE500 longitudinal and FE415 transverse source identities. | Add a strict material variant with explicit transverse grade; route it to stirrup calculations only. Bind both grades into canonical and calculation evidence hashes. | `test_transverse_grade_changes_stirrups_and_evidence_not_longitudinal_flexure`; W3 audit and REST parity. |
| RC2 | Clear-cover arithmetic cannot consume a longitudinal-group centroid distance. The request also did not reject every nonpositive derived depth. | Add a centroid-cover variant to the existing resolver; use `d=D-centroid_cover`. Reject inconsistent single-layer detailing and invalid resolved depth at intake. | 40 mm centroid gives d=460 mm for D=500; 40 mm clear + 8 mm stirrup + 20 mm bar gives d=442 mm. Neither is substituted for the other. |
| RC3 | Shear spacing used supplied fy without the 415 N/mm2 design limit. | Apply the limit after validating the actual grade in both shear-demand and minimum-reinforcement calculations. Do not reduce longitudinal fy. | Independent Cl 40.4 vector: Vus=65.136 kN and spacing=225 mm for both Fe415 and Fe500. |
| RC4 | The torsion transverse equation used residual shear and omitted the equivalent-stress lower bound. | Implement both expressions in Cl 41.4.3 and take the controlling requirement. | Independent low-Vu and floor-governed vectors; corrected G7 golden vector. |
| RC5 | Torsion used stirrup-centre dimensions where Cl 41.4.3 requires longitudinal corner-bar centres. | Require explicit corner geometry in the raw kernel/compatibility path. Canonical and v1 single-layer adapters derive it from declared bar sizes. Keep stirrup dimensions separate for spacing limits. | Missing geometry is rejected. Canonical 300x500 fixture resolves b1=184 and d1=386 mm; Python/REST/report use the same resolver. |
| RC6 | An empirical longitudinal-area expression was labelled as Cl 41.4.2 and opposite-face moment demand was absent. | Use the maintained flexure owner for Me1 and max(Mt-Mu,0); carry opposite-face required steel to the strength result. Reject the incomplete legacy helper. Require singly reinforced capacity on each face. | Pure-torsion/opposite-moment and golden tests; no additive double counting of `Al_torsion`. |
| RC7 | Practical shear spacing could round a sub-75 mm requirement upward and return safe. | Return an explicit failed design with zero offered spacing when no supported spacing satisfies demand. | `test_shear_cap_and_constructibility_are_decisive`; no false pass after the grade correction. |
| RC8 | A strength result alone does not prove torsion corner/perimeter reinforcement distribution. | Block canonical torsion detailing/BBS until the distribution consumer exists. Continue exposing verified force/required-steel checks. | `TORSION_DETAILING_SCOPE_HOLD` is exercised through the actual detailing entrypoint. This is containment of an unimplemented consumer, not completed detailing. |

RC1-RC7 have implemented numerical/contract corrections subject to this packet's
gates. RC8 remains an explicit feature hold. Numerical corrections intentionally
change affected results; old accepted artifacts are historical evidence and are
not rewritten. Canonical calculation identity is now
`is456-rectangular-beam-strength/v2`. Existing single-grade and clear-cover input
shapes remain valid; new variants do not add null fields to those inputs.

## Source check and migration

The original [IS 456:2000 scan](https://civilengineeringtotalconceptcom.wordpress.com/wp-content/uploads/2021/02/456-2000.pdf)
was visually inspected at printed pages 37-38, 47-48, 73, 75 and 95. Relevant
owners are Cl 26.5.1.5-7, 40.4 and 41.4.2-3. The PDF and page images remain
external; the repository stores normalized formulas, authored vectors and source
references only. Existing controlled amendment identity remains in force.

[CSI's reinforcement form documentation](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Properties/Frame_Sections/Frame_Section_Property_Reinforcement_Data_Form.htm)
distinguishes longitudinal/confinement materials and beam centroid cover.
ETABS design overwrites are not proof of installed steel.

- Canonical Python/REST v2: add `materials.fy_transverse_nmm2` when known; use
  `section.effective_depth_basis.centroid_cover_mm` for that exact cover meaning.
- Raw `design_torsion`: supply `corner_bar_centres_mm` and `d_opposite_mm`.
  `design_beam_is456` accepts `torsion_corner_bar_centres_mm` and the explicit
  opposite-face depth basis `d_dash_mm`. Never use stirrup centres as bar centres.
- The standalone torsion REST endpoint now requires explicit effective depth,
  corner centres and opposite-face effective depth. Its old 25 mm depth offset
  is removed. The primary v1 route already has explicit bar/cover parameters;
  inconsistent or multilayer torsion input is held.
- `Al_torsion` is total required tension steel from the two equivalent moments,
  not additional steel to add to primary flexure. Opposite-face demand is exposed
  separately from flexural compression steel. Doubly reinforced coupled torsion and shop detailing remain held.
- The separate typed torsion facade requires explicit `corner_bar_centres_b1_mm`,
  `corner_bar_centres_d1_mm` and `d_opposite_mm`. The older read-and-detail pilot
  remains usable only for its supported zero-torsion detailing scope; do not drop
  a real nonzero torque to run it. W3 uses the separate audit route.
- The original `calculation-review-v1.json` fixture is retained unchanged. The
  active Python/JavaScript cross-runtime fixture is `calculation-review-reinforcement-v2.json`.

## Simplest supported route and stopping rules

| Alternative considered | Decision |
|---|---|
| Extend existing typed beam path, geometry resolver and code owners | Chosen: fixes the actual calculation and reaches W3 audit, Python, REST and report reconstruction. |
| Copy centroid cover to clear cover or replace all fy with FE415 | Rejected: changes physical meaning or longitudinal capacity and destroys provenance. |
| New ETABS getters or another COM/table client | Rejected for these causes: saved input already proves the distinctions; more extraction cannot repair formulas. |
| New solver, generic workflow framework or automatic reinforcement inference | Rejected: not needed for these defects and would expand validation substantially. |
| Immediately remove the canonical serviceability hold | Rejected: typed physical/method evidence still needs its own executable contract. Existing functions alone are not proof. |

Before a new diagnostic, identify the missing field or failed result, its current
owner, the simplest supported source and one decisive acceptance test. Stop a
repeated path when its output cannot resolve that named gap. Reopen a historical
failure only with a changed hypothesis/input and a new bounded acceptance test.
Do not describe unknown CSI/binder internals as diagnosed root causes.

Contract changes must also refresh the maintained API manifest, classification,
OpenAPI and family-facade recipe documentation. Their normal hooks reject stale
consumers; do not replace those generators with hand-edited projections.

## Remaining W3 work

1. Complete strict serviceability method/basis contracts. Source-verified span/depth
   and Annex F formulas are candidate routes; do not substitute factored moments
   for service actions or default an unknown support/strain/limit. Direct-deflection
   and long-term methods need independent validation before canonical acceptance.
2. Complete torsion perimeter/distribution detailing and other mandatory
   constructability/applicability criteria before candidate screening.
3. Resolve the physical support/mesh/slab-transfer matrix for W3H. The three saved
   candidates remain NOT_COMPARABLE_AS_IS; none is promoted by these software fixes.
4. Implement W3I/K/L after their E/H dependencies; finish cumulative integration,
   Mac review and the separate professional/release gates. No W3-complete claim.

The #931 CSI return and #932 binder causes remain unconfirmed. The #933 timestamp
normalization defect stays closed. No live retry, source file mutation or repeated
request for the already accepted pilot parameters is authorized by this packet.
