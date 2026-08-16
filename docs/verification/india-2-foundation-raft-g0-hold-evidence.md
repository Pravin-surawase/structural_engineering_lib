---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-RAFT-G0
---

# INDIA-2 Foundation Raft G0 Hold Evidence

## Decision

**HOLD.** Do not create raft calculation, service, API, React, or capability
implementation files.

The frozen candidate remains one regular rectangular constant-depth rigid raft
under mainly vertical, regularly arranged column loads, using a conventional
non-FEM analysis with caller-approved soil-pressure and settlement bases. The
candidate is potentially useful and public discovery identifies an applicable
conventional method. It cannot yet be implemented truthfully because the
repository retains neither a controlled IS 2950 (Part 1) source nor an
accepted, independently replayable structural raft benchmark that closes
pressure, global equilibrium, strip actions, flexure, one-way/punching shear,
reinforcement, and anchorage.

This is a completed decision gate, not a support claim. Raft-foundation design
remains `HELD / NOT_IMPLEMENTED`, has no public workflow, and is removed from
the current INDIA-2 implementation scope unless the reactivation contract
below is satisfied in a new G0 packet.

## Exact inspected baseline

- Fresh packet base: `origin/main = def0b493e33fa566fd3f23bf166287fcda6169d6`,
  tree `7da91c66143e83933a88bb9a4d5396bede89cf6d`.
- Runtime diagnosis returned `source_bound=true`; local Git authority
  `scripts/git_state.py` returned `READY_LOCAL`, a clean linked worktree, zero
  ahead/behind, and no operation marker before editing.
- Controlled consolidated IS 456:2000 through Amendment 5 SHA-256:
  `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
- Controlled Amendment No. 6 (2024) SHA-256:
  `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
- The controlled-source inventory contains only that IS 456 source set and
  derived registry/reference records. No IS 2950 or raft companion source is
  retained.
- No `raft_foundation` code directory, service, route, or calculation test
  exists. The generated Indian-code manifest already declares raft-foundation
  design held and not implemented.

As with pile-cap G0, the linked worktree does not materialize the ignored
`private_sources/` directory. The inventory and hashes above were read without
mutation from the primary checkout's retained private-source registry.

## Discovery evidence and authority boundary

The [official BIS catalogue result](https://standardsbis.bsbedge.com/search_redirect.aspx?id=19058)
identifies IS 2950 (Part 1):1981, reaffirmed in 2023 with one amendment, as an
active raft-foundation design standard. The
[official BIS preview](https://www.services.bis.gov.in/tmp/SR2950_1.pdf)
states that Part 1 covers conventional rigid-foundation and simplified
flexible-foundation methods for buildings with mainly vertical and evenly
distributed loads. These pages prove current discovery and scope. They are not
an authenticated repository-controlled implementation source and do not bind
the amendment content to a committed source identity/hash.

The [IISc/NPTEL Advanced Foundation Engineering chapter](https://archive.nptel.ac.in/content/storage2/courses/105108069/mod03/lec03.pdf)
describes a conventional rigid-mat model: infinitely rigid foundation, planar
contact pressure, resultant/pressure centroid coincidence, whole-mat sections
in two orthogonal directions, and shear/moment from column loads and bearing
pressure. This supports candidate discovery, but the chapter does not provide a
complete numerical structural raft design benchmark with the required
strength/detailing intermediates.

An [NPTEL question set](https://archive.nptel.ac.in/content/storage2/courses/105105039/Questions_Final.pdf)
asks the reader to design a raft from a figure and soil data, but supplies no
accepted worked solution or structural result set. An assignment prompt is not
a benchmark. No numeric result is adopted or claimed from these materials.

Owner authorization to distribute normalized IS-code implementation content
within approved feature scopes remains valid through
[`is456-public-distribution-permission.json`](is456-public-distribution-permission.json).
That permission does not supply the missing controlled source, amendment
identity, benchmark, or feature activation decision.

## Why no analysis model is activated

| Candidate model | Evidence available | G0 outcome |
|---|---|---|
| Conventional rigid raft with planar pressure and whole-mat orthogonal sections | BIS scope preview and NPTEL method description | Best candidate, but held: no controlled IS 2950 source/amendment binding and no complete structural benchmark verifies pressure, action extraction, strength, or detailing. |
| Simplified flexible or elastic/Winkler/plate method | BIS scope preview acknowledges flexible methods; existing sources discuss elastic foundations | Excluded: materially broader soil-structure interaction, coefficient/subgrade inputs, and numerical analysis are not source-bound or benchmarked for this packet. |
| Reuse combined-footing or flat-slab workflow | Existing bounded rigid combined footing and regular interior flat slab | Rejected: neither supported family represents a many-column raft, soil-contact pressure/action extraction, settlement basis, or raft-specific boundary. |

The conventional rigid candidate remains frozen for future investigation, but
no pressure or strip/panel arithmetic is authorized now.

## Frozen candidate and caller-owned boundary

The future G0 candidate remains intentionally narrow:

- one rectangular constant-depth reinforced-concrete raft with no openings,
  steps, drops, beams, basement walls, or movement joints;
- a regular orthogonal grid of centred interior rectangular columns, symmetric
  vertical service and factored compression, and no lateral action or applied
  column moment;
- one explicitly selected conventional rigid-foundation model with planar
  compression-only pressure and whole-raft sections in both directions;
- explicit M30/Fe500 material, cover, reinforcement, and anchorage inputs; and
- caller-approved loads/combinations, raft geometry/depth, allowable bearing,
  no-tension pressure basis, rigidity criterion, soil profile, bearing
  capacity, total/differential settlement, groundwater/buoyancy, durability,
  construction suitability, and professional review.

G0 does not generate loads, combinations, column grid, raft size/depth,
pressure approval, soil stiffness/capacity/settlement, excavation compensation,
reinforcement, or approval references.

## Decision matrix retained while held

| Input/outcome class | Required future behavior | Current state |
|---|---|---|
| Frozen regular rigid-raft topology with complete approvals | Return source-bound `PASS` or valid `FAIL` only after the conventional method and benchmark are accepted | `HELD / NOT_IMPLEMENTED`; no calculation |
| Valid in-domain inadequate pressure, flexure, one-way/punching shear, reinforcement, spacing, cover, or anchorage | Return `FAIL` with the exact failed check, never an unsupported disposition | Contract cannot be frozen without source and benchmark |
| Alternate topology, soil model, load class, or missing prerequisite | Fail closed before calculation | Held cases include irregular grids/loads, eccentricity, tension/uplift, lateral/seismic action, basements, walls, openings, variable thickness, beams, flexible/Winkler/plate/FEM interaction, automatic settlement/sizing, and missing approval |

No `PASS`, `FAIL`, numeric pressure/action/capacity, or engineering
recommendation is emitted by this packet.

## Exact reactivation contract

A future `INDIA-2-FOUNDATION-RAFT-G0-REACTIVATION` may return `GO` only when
one fresh packet binds all of the following:

1. a repository-controlled, authenticated IS 2950 (Part 1) source and its
   applicable amendment with exact identities and SHA-256 values, plus any
   companion authority required for the chosen structural checks;
2. one accepted independent structural benchmark for the exact regular rigid-
   raft candidate, with enough inputs/intermediates to replay rigidity
   eligibility, pressure at governing locations, vertical and biaxial moment
   equilibrium, both-direction section/strip actions, flexure, one-way and
   punching shear, reinforcement/detailing, anchorage, and tolerance;
3. one analysis decision defining the planar-pressure, whole-raft/strip action
   extraction and explaining why flexible, Winkler, elastic-plate, and FEM
   alternatives are excluded;
4. explicit supported, valid-failure, and unsupported matrices, including
   topology, no-tension pressure, rigidity, soil/settlement ownership, and
   complete caller-approved geotechnical prerequisites; and
5. proposed A-D public signatures and capability wording that stays
   `HELD / NOT_IMPLEMENTED` through A-C and changes only after D acceptance.

Catalogue pages, previews, conceptual lecture notes, an unsolved question, or
reuse of combined-footing/flat-slab behavior do not satisfy this contract.

## Dormant packet shape after a future GO

The future file plan remains non-authorizing:

- A: `codes/is456/raft_foundation/models.py` and `analysis.py` for topology,
  rigidity/approval eligibility, planar pressure, equilibrium, and only the
  accepted whole-raft action extraction;
- B: `strength.py` for accepted raft flexure, one-way/punching shear,
  reinforcement, spacing, cover, anchorage, and composed disposition;
- C: `services/raft_foundation_api.py`, immutable public request/result/
  provenance types, canonical exports, and an executable benchmark;
- D: strict FastAPI request/response models, one route, exact OpenAPI update,
  semantic/capability truth, and deterministic manifest promotion; and
- acceptance: one non-frozen independent replay, valid failure, all fail-
  closed exclusions, exact-head audit, hosted checks, and no new behavior.

No file above is created by this HOLD packet.

## G0 acceptance and next boundary

The focused contract passes only when:

- the generated manifest has `raft_foundation` as `HELD / NOT_IMPLEMENTED`,
  with no workflow and this G0 evidence attached;
- the task board, completion plans, and compact brief all say `HOLD` and name
  `INDIA-2-CLOSEOUT` next;
- documentation metadata, indexes, internal links, token-efficiency checks,
  and the quick `10/10` repository gate pass; and
- the unchanged audited head passes every applicable hosted check and its
  merged tree matches the audited candidate tree.

Broad Python and the full 30-check repository gate remain deferred to the
fresh final INDIA-2 closeout lane. Raft or pile-cap calculation, cleanup/
deletion, React, release, package publication, and professional approval remain
outside this lane.
