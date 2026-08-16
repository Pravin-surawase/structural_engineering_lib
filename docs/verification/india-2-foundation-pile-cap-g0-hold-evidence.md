---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-PILE-CAP-G0
---

# INDIA-2 Foundation Pile-Cap G0 Hold Evidence

## Decision

**HOLD.** Do not create pile-cap calculation, service, API, React, or capability
implementation files.

The frozen candidate remains one constant-depth rectangular reinforced-
concrete cap over exactly two identical circular piles on one axis, with one
centred rectangular column and symmetric caller-approved vertical pile
reactions. That candidate cannot yet be implemented truthfully because the
repository retains neither a controlled IS 2911 companion source nor an
accepted, independently replayable structural two-pile-cap benchmark. Without
both, G0 cannot select between a footing critical-section model and a deep-
region/strut-and-tie model or bind the resulting bearing/nodal, tie/action, and
anchorage checks.

This is a completed decision gate, not a support claim. Pile-cap design remains
`HELD / NOT_IMPLEMENTED`, has no public workflow, and is excluded from INDIA-2
implementation unless the reactivation contract below is satisfied in a new
G0 packet.

## Exact inspected baseline

- Fresh packet base: `origin/main = 1139e9ea06751c72b66098a575c1f5e327c56ef5`,
  tree `0abefcd0255157bd1444549f2066eb937f45e5a0`.
- Runtime diagnosis returned `source_bound=true`; local Git authority
  `scripts/git_state.py` returned `READY_LOCAL`, a clean linked worktree, zero
  ahead/behind, and no operation marker before editing.
- Controlled consolidated IS 456:2000 through Amendment 5 SHA-256:
  `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
- Controlled Amendment No. 6 (2024) SHA-256:
  `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
- The controlled-source inventory contains only that IS 456 source set and
  its derived registry/reference records. No IS 2911 or pile-cap companion
  source is retained.
- No `pile_cap` code directory, service, route, or direct test exists. The
  generated Indian-code manifest already declares pile-cap design held and
  not implemented.

The linked worktree does not materialize the ignored `private_sources/`
directory. The inventory and hashes above were therefore read without mutation
from the primary checkout's retained private-source registry.

## Discovery evidence and authority boundary

The [official BIS IS 2911 catalogue](https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?Standard_Number=IS+2911&id=0)
identifies the active concrete-pile parts, including Parts 1/Sections 1-4,
and the load-test Part 4. The
[official BIS Part 1/Section 1 preview](https://www.services.bis.gov.in/tmp/SR2911_1_1.pdf)
confirms a concrete-pile design-and-construction scope and references IS 456.
These public pages prove discovery and scope only. They are not authenticated,
repository-controlled implementation inputs and do not contain the complete
structural cap contract required by this G0.

The public benchmark search found
[NPTEL pile-group material](https://archive.nptel.ac.in/content/storage2/courses/105101083/Slides/Module%205/Lecture%2027/10.html)
covering group capacity and settlement and an
[NPTEL reinforced-concrete course syllabus](https://archive.nptel.ac.in/content/syllabus_pdf/105103824.pdf)
that lists pile-cap design/detailing as a topic. Neither result is an accepted,
numerically complete structural two-pile-cap example that can independently
replay equilibrium, tie/action demand, bearing or nodal/critical-section
checks, and anchorage. No numerical benchmark is claimed from either page.

Owner authorization to distribute normalized IS-code implementation content
within approved feature scopes remains valid through
[`is456-public-distribution-permission.json`](is456-public-distribution-permission.json).
That permission does not supply a missing controlled source, benchmark, or
feature activation decision.

## Why neither structural model is selected

| Candidate model | Evidence available | G0 outcome |
|---|---|---|
| IS 456 footing critical-section analogy | Controlled footing clauses and existing isolated/combined footing helpers | Rejected for activation: a cap transfers concentrated column load to discrete pile reactions rather than a continuous approved soil-pressure field; no source-bound rule proves this analogy for the frozen cap. |
| Deep-region/strut-and-tie | A bounded Clause 29 deep-beam workflow and controlled corbel/deep-beam source content | Rejected for activation: the supported deep-beam route expressly excludes generalized strut-and-tie modelling, and no pile-cap nodal/bearing/tie benchmark or companion contract is retained. |

Reusing either existing family would convert implementation convenience into
engineering authority. G0 therefore leaves model selection undecided and
prevents mixed footing/deep-region arithmetic.

## Frozen candidate and caller-owned boundary

The future G0 candidate remains intentionally narrow:

- one rectangular, constant-depth M30 cap over two identical circular piles;
- piles and a centred rectangular column share one longitudinal centreline;
- symmetric vertical compression only, with equal caller-supplied service and
  factored pile reactions and explicit units;
- Fe500 uncoated deformed reinforcement, explicit cover, bar geometry, and
  available anchorage; and
- caller-approved pile axial capacity, reaction basis, pile layout and
  construction suitability, group behavior, settlement, durability,
  geotechnical design, and professional review.

G0 does not generate pile reactions, pile capacity, pile/group geometry,
loads, combinations, material grades, cap depth, reinforcement, or approval
references.

## Decision matrix retained while held

| Input/outcome class | Required future behavior | Current state |
|---|---|---|
| Frozen centred axial two-pile topology with complete approvals | Return a source-bound `PASS` or valid `FAIL` only after one model and benchmark are accepted | `HELD / NOT_IMPLEMENTED`; no calculation |
| Valid in-domain inadequate bearing/nodal, tie/action, critical-section, reinforcement, or anchorage provision | Return `FAIL` with the exact failed check, never an unsupported disposition | Contract cannot be frozen without source and benchmark |
| Any alternate topology or missing prerequisite | Fail closed before calculation | Held cases include unequal reactions, eccentric/biaxial action, lateral/uplift/seismic action, three or more piles, multiple columns, battered piles, pile/soil design, settlement, automatic sizing, FEM, and missing external approval |

No `PASS`, `FAIL`, numeric capacity, or engineering recommendation is emitted
by this packet.

## Exact reactivation contract

A future `INDIA-2-FOUNDATION-PILE-CAP-G0-REACTIVATION` may return `GO` only
when one fresh packet binds all of the following:

1. a repository-controlled, authenticated IS 2911 edition/part source with
   exact identity and SHA-256, plus any other authority needed for the chosen
   structural cap model;
2. one accepted independent structural benchmark for the exact centred axial
   two-pile candidate, with enough published inputs and intermediate results to
   replay vertical and moment equilibrium, tie/action demand, bearing, the
   chosen nodal or critical-section result, anchorage, and tolerance;
3. one model-selection decision explaining why the alternative model is
   excluded rather than mixed into the calculation;
4. explicit supported, valid-failure, and unsupported matrices, including a
   topology discriminator and every caller-owned geotechnical approval; and
5. proposed A-D public signatures and capability wording that stays
   `HELD / NOT_IMPLEMENTED` through A-C and changes only after D acceptance.

Catalogue pages, previews, a syllabus, a worked example without independently
replayable intermediates, or an existing footing/deep-beam implementation do
not satisfy this contract.

## Dormant packet shape after a future GO

The prior file plan remains non-authorizing:

- A: `codes/is456/pile_cap/models.py` and `analysis.py` for topology,
  eligibility, equilibrium, and only the accepted action model;
- B: `strength.py` for accepted cap-specific bearing/nodal or critical-section,
  tie/action, reinforcement, anchorage, and detailing checks;
- C: `services/pile_cap_api.py`, immutable public request/result/provenance
  types, canonical exports, and an executable benchmark;
- D: strict FastAPI request/response models, one route, exact OpenAPI update,
  semantic/capability truth, and deterministic manifest promotion; and
- acceptance: one non-frozen independent replay, valid failure, all fail-
  closed exclusions, exact-head audit, hosted checks, and no new behavior.

No file above is created by this HOLD packet.

## G0 acceptance and next boundary

The focused contract passes only when:

- the generated manifest has `pile_cap` as `HELD / NOT_IMPLEMENTED`, with no
  workflow and this G0 evidence attached;
- the task board, completion plans, and compact brief all say `HOLD` and name
  decision-only `INDIA-2-FOUNDATION-RAFT-G0` next;
- documentation metadata, indexes, internal links, token-efficiency checks,
  and the quick `10/10` repository gate pass; and
- the unchanged audited head passes every applicable hosted check and its
  merged tree matches the audited candidate tree.

Broad Python and the full 30-check repository gate remain deferred to the
final INDIA-2 closeout. Pile-cap calculation, raft work, cleanup/deletion,
React, release, package publication, and professional approval remain outside
this lane.
