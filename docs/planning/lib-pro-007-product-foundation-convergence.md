---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: plan
complexity: advanced
tags: [product-foundation, optimization, detailing, etabs, excel, react, compatibility]
---

# LIB-PRO-007 Product Foundation Convergence

## Decision

Complete one bounded product-foundation milestone before resuming INDIA-3-G0.
The milestone converges the maintained beam/gravity product journey across the
Python package, REST API, React website, exported ETABS data, and Excel review
surface. It is not a repository-wide rewrite and does not require every
library-only helper to receive an HTTP endpoint.

The exact G0 baseline is fetched hosted `main` commit
`2d6df18efa9228afbf593f36fa95d2ce574977ac`. The implementation lane is a
source-bound linked worktree. The preserved INDIA-3 source-library candidate
`9c976b1f` and every dirty, detached, foreign, or uncertain worktree remain
unchanged.

## Packet status

- G0 merged through PR #852 at `a6d47a85` with exact product-contract and
  packet boundaries.
- P1 has an implementation/evidence candidate on
  `codex/lib-pro-007-p1-optimization-truth`; local and hosted acceptance remain
  pending until its immutable verification closes.
- P2-P7 and cumulative M0 remain held in the frozen sequence below.

## Why this precedes INDIA-3

The calculation library already has broad bounded capability, tested transport
surfaces, deterministic gravity results, and an installed Excel workbench. The
main-process gap is product-contract truth:

- the beam cost route accepts inputs that its core does not use;
- shear is described as an optimization constraint but is not evaluated by the
  current cost optimizer;
- the REST mapper emits assumed or zero engineering fields;
- the gravity example correctly holds supplied beam-bar and footing anchorage
  completion;
- exported ETABS data has maintained adapters but not one frozen, hash-bound
  product snapshot contract; and
- compatibility projections are numerous, but most delegate across the three
  intentional public facades and must not be mistaken for duplicate engines.

INDIA-3 formulas would inherit these product boundaries. This milestone fixes
the boundaries first without changing any IS 13920 engineering claim.

## Live G0 inventory

| Surface | Live count | G0 meaning |
|---|---:|---|
| Declared Indian-code families | 13 supported / 21 total | Bounded software scope; not whole-standard or professional completion |
| Public functions checked for router wiring | 97 | 52 directly wired; 45 intentionally library-only or pending product selection |
| FastAPI routes with direct tests | 89 / 89 | Transport coverage only; does not prove every response field is truthful |
| React hooks connected to APIs | 13 / 13 | Connection coverage only; no duplicate structural formulas are authorized |
| Component capability families in catalogue | 10 | Discoverability, separate from tool eligibility |
| Automation capabilities in catalogue | 1 | Beam remains the only approved automation capability |
| Composed workflows in catalogue | 1 | Gravity V1 is discoverable but not tool eligible |

The generated API classification contains 205 package-root exports, 182
service-facade exports, and the same 182 names on the legacy `structural_lib.api`
facade. Its 447 compatibility classifications are projection entries across
those surfaces, not 447 separately owned calculations.

## Frozen product-contract matrix

| Product contract | Canonical calculation authority | Product transports | G0 disposition | Owned repair |
|---|---|---|---|---|
| Ordinary rectangular beam design/check | `structural_lib.design_beam_is456` and maintained beam services | REST `/api/v1/design/beam`, batch/streaming, React, Excel | `ACCEPTED_BOUNDED`; supplied-bar completion remains separate | P2 |
| Solid slab design | Maintained IS 456 slab service workflows | REST slab routes; gravity composition | `ACCEPTED_BOUNDED`; no new slab system | parity only |
| Rectangular column design/check | `structural_lib.design_column_is456` and maintained column services | REST column routes; gravity composition | `ACCEPTED_BOUNDED`; no new column system | parity only |
| Concentric isolated footing | `structural_lib.design_concentric_isolated_footing_is456` and footing services | REST footing route; gravity composition; React | `ACCEPTED_WITH_DETAILING_HOLD` | P3 |
| Building Gravity V1 | `structural_lib.run_gravity_workflow_with_book_v1` | package, CLI, REST, React | `ACCEPTED_BOUNDED`; action families remain explicit and limited | P2-P4 |
| Beam cost optimization | Cost optimization service through stable beam service facade | REST `/api/v1/optimization/beam/cost`; React consumer | `HOLD_OUTCOME_CHANGING` | P1 |
| ETABS exported-data intake | Maintained import/adapters service; library remains calculator | REST import, React workspace | `FOUNDATION_EXISTS_NEEDS_CANONICAL_SNAPSHOT` | P5 |
| Excel Routine Workbench V1 | Excel mapping/review service; no formulas in Office.js | REST Excel workbench routes; installed Excel | `ACCEPTED_TRANSPORT` | P6 parity |
| React website workspace | REST clients plus `WorkspaceSnapshotV1`; no structural formulas | React workbench | `ACCEPTED_TRANSPORT` | P6 parity |

All other supported component families remain discoverable at their current
bounded capability. LIB-PRO-007 does not make stair, wall, deep-beam,
flat-slab, combined-footing, strap-footing, or current IS 13920 checks part of
the Excel/ETABS product slice.

## Packet sequence

### P1 - Optimization truth

Repair the canonical service before the transport:

- make concrete grade, steel grade, cover, dimensional bounds, steps, and cost
  profile explicit candidate inputs;
- apply the factored shear through a maintained IS 456 shear check or return a
  non-success engineering status;
- restrict the cost endpoint to the cost objective unless another objective is
  delegated to a separately accepted optimizer;
- derive required steel, steel weight, utilization, and material identity from
  the real candidate;
- remove assumed `0.90`/`0.85` utilization and zero-value engineering fields;
- keep the optimizer result transport-neutral and the FastAPI router a mapper;
  and
- prove sensitivity or explicit rejection for every accepted request field.

Likely owned paths:

- `Python/structural_lib/services/optimization.py`
- `Python/structural_lib/services/costing.py`
- `Python/structural_lib/services/api_results.py`
- `Python/structural_lib/services/beam_api.py`
- `fastapi_app/models/optimization.py`
- `fastapi_app/routers/optimization.py`
- focused Python/FastAPI/React contract tests

### P2 - Supplied beam reinforcement

Reuse the maintained bar-selection, spacing, and anchorage services. Separate
required reinforcement from supplied-arrangement evaluation. Missing supplied
bars may leave design demand calculated, but never become a fully detailed
beam `PASS`.

### P3 - Footing hooks and bends

Extend the current straight-bar footing contract with explicit supported
hook/bend arrangements. Reuse or factor existing maintained anchorage
primitives, retain exact source/clause provenance, and prove required length,
available length, bend geometry, constructability, `PASS`, `FAIL`, and
unsupported `HOLD` vectors.

### P4 - Explicit practical actions

Remain one-storey, one-bay, and solver-free. Add only caller-assigned wall line,
beam line/point, and supported slab-area actions with stable source identity,
load case, units, destination, basis, ledger entry, and exact reconciliation.
Do not infer distribution or generate IS 875 loads.

### P5 - ETABS read-only snapshot

Converge existing exported-file paths on one deterministic snapshot containing
project/export identity, source hashes, units, local-axis mapping, combination
or envelope identity, stable member IDs, complete row accounting, exclusions,
ambiguities, and a snapshot hash. The packet ends at:

`ETABS exported files -> canonical snapshot -> canonical beam request`

Live ETABS automation, analysis control, write-back, and model saves remain
excluded. The existing lossless single/dual CSV import services are the
canonical intake candidates. Package exports such as `normalize_etabs_forces`,
`load_etabs_csv`, and `create_job_from_etabs` remain held or compatibility
surfaces until P5 proves whether each delegates, migrates, or stays held.

### P6 - Cross-surface parity

For one frozen ETABS-exported beam dataset and the maintained gravity example,
prove identical normalized request identity, result identity, governing status,
and issues through Python, REST, React, and Excel. Source changes must mark
retained results stale and block current export until recalculation. Excel and
React contain no structural formulas.

### P7 - Compatibility convergence

Use the G0 matrix after canonical destinations work:

1. migrate maintained callers;
2. retain facade shims that delegate to the same objects;
3. add current deprecation metadata and migration examples;
4. retire only second calculation paths or unsafe contracts; and
5. delete only with caller, replacement, reference, retention, and explicit
   authorization evidence.

Historical archives, Streamlit reference material, vendor sources, branches,
and worktrees are outside this packet.

## Verification cadence

For each packet, finish intended code, tests, documentation, and evidence
before the routine verification batch. Run affected focused checks together,
`./run.sh check --quick` once, normal staged hooks once, then every required
hosted check on the immutable candidate. An outcome-changing repair reruns only
its affected focused evidence and the consolidated gate once.

After all packets integrate, run the broad Python/FastAPI/React suites and
`./run.sh check` once, plus architecture/import validation, parity, exact-wheel
product vectors, the website production journey, and installed Windows Excel
G3 only when the Excel surface changes.

## Milestone acceptance

LIB-PRO-007 is complete only when:

- no active product route returns fabricated engineering data;
- every accepted optimization input is applied or rejected explicitly;
- active product requests contain no hidden project-value defaults;
- supplied beam bars and supported footing anchorage have truthful outcomes;
- practical actions reconcile without silent loss;
- ETABS exported data has deterministic identity and complete row accounting;
- Python, REST, React, and Excel share one calculation authority;
- compatibility routes delegate and no maintained caller uses a retired second
  calculation path;
- cumulative local and hosted software gates pass; and
- release, professional use, live ETABS, write-back, and all new IS 13920 claims
  remain held.

## INDIA-3 handoff

After the unchanged green milestone merges, create a fresh INDIA-3-G0 lane
from exact new hosted `main`. Compare and transplant only reviewed task-owned
changes from preserved candidate `9c976b1f`; do not rewrite or clean the
original lane. Reconcile shared `SESSION_LOG`, task, and next-session documents
on the fresh lane, then resume the bounded source/amendment truth audit. No new
IS 13920 formula is authorized by this plan.
