---
owner: Main Agent
status: active
last_updated: 2026-08-31
doc_type: spec
complexity: advanced
tags: [etabs, beams, data-contracts, frame-analysis, optimization, provenance]
---

# W3 ETABS Data, Beam Analysis, and Optimization Master Plan

## Purpose and authority

This document converts the accepted W1/W2 ETABS work into the durable W3
programme for public data contracts, beam audit, local candidate screening,
and later ETABS-verified optimization. It is the planning authority for that
foundation only. The exact W3-readiness predecessor is PR #899 merge
`7af545ec0e239bac8fa6d480ecbb2b05a60aa40d`, with merged tree
`cc40650b7f6569227c880d61a9967ee3bbdfab31`. The owner subsequently accepted the
dependency-ordered W3 campaign and its bounded Windows execution. Current
continuations still require exact predecessor, scope and evidence checks.

W3A is intentionally the first bounded Mac read-only contract packet. No W3
packet in this plan authorizes opening ETABS or Excel, running ETABS analysis
or design, mutating a model or workbook, starting optimization, deleting a
public surface or retained evidence, publishing a release, or making an
engineering/professional claim. Each later installed or mutation packet needs
its own explicit authority and exact predecessor check.

Use the companion
[ETABS, Excel, Professional Attestation, and Surface Retirement Audit](etabs-excel-professional-surface-audit.md)
for professional-signature evidence, Excel review architecture, public API
retirement, React freeze/pruning, and repository compaction decisions.

The execution principle is:

```text
ETABS supplies exact model and global-analysis evidence
                         ->
the public library supplies typed data, beam checks, local screening, and
candidate ranking
                         ->
ETABS reanalyses only a bounded shortlist
                         ->
the public library verifies the fresh actions and records the comparison
```

The objective is fewer ETABS trips without pretending that a local beam model
has full 3D ETABS parity. Independent frame analysis remains exactly
`HELD_NOT_SUPPORTED` until a separately accepted solver packet and separately
accepted model-specific calibration evidence both exist. Even then, the local
solver remains a bounded surrogate and ETABS remains the global-analysis
authority.

## Exact audit boundary

The original audit was performed on 2026-08-29 from:

- local branch `codex/etabs-analysis-foundation-audit`;
- base and current `origin/main` `ee50aaa3cad619b41c6153f5f7970553ef65248c`;
- clean tree before documentation work;
- no current pull request for the planning branch; and
- a successful `git fetch origin` immediately before comparison, after which
  local `main` and the local `origin/main` ref both resolved to `ee50aaa3`.

The W3-readiness maintenance refreshed that boundary after a new fetch:

- PR #898 merged the exact reviewed W2C candidate `57f53d48...` as
  `f1873e7b...`, with candidate and merge tree both `bb20ba0c...`;
- direct service, REST, and all seven saved Excel tables reconcile baseline
  `d4c28586...`, 3,502 stations, and 3,626,096 canonical JSON bytes;
- model hash/size/mtime, locked state, units, and the active approved
  combination remained exact; and
- no ETABS analysis/design/save/write-back occurred, while independent frame
  analysis remains `HELD_NOT_SUPPORTED`.

This W3 planning audit refreshed the boundary again on 2026-08-30 before any
write:

- `git fetch origin main` completed successfully;
- `origin/main`, `FETCH_HEAD`, and the starting `HEAD` all resolved to exact
  PR #899 merge `7af545ec0e239bac8fa6d480ecbb2b05a60aa40d`;
- GitHub reported PR #899 `MERGED` into `main` with that merge commit;
- both `origin/main^{tree}` and `FETCH_HEAD^{tree}` resolved to exact tree
  `cc40650b7f6569227c880d61a9967ee3bbdfab31`;
- the starting linked worktree was clean, operation-free, lock-free, and
  detached at that exact predecessor; and
- sibling worktrees were retained unchanged. No clean/behind/detached state was
  treated as deletion, retirement, or mutation authority.

The earlier blocked retry and six-table JSON-write evidence remain retained as
historical fail-closed records. They no longer describe the current W2 state.

The historical session-timer issue recorded by the predecessor is closed. This
planning audit began exact task `W3-PLAN-AUDIT` through the maintained session
command and recorded no borrowed timing or installed-application evidence.

## Current capability truth

### Completion audit and active critical path (2026-08-31)

The owner requested a drift check and completion of W3 after reporting the Mac
fetch complete. Windows freshly fetched GitHub at PR #921 merge
`d6b7a105c22b7d6fde0d532bc1b5c375b43f6e2b`, tree
`dbdc261c45f150c3a99237d4bb70093b42b02f89`. The Mac observation is owner-reported,
not a Windows audit of the Mac checkout. Each new branch still has one writer.

| Packet | Accepted implementation/evidence | Remaining gate |
|---|---|---|
| W3A | Definition/demand contracts, PR #901, L1 | None within its bounded contract |
| W3B | Installed signatures, PR #902, L2 | New operations require a new signature audit |
| W3C | Catalogue adapter, PR #903 with #904/#905 repairs, L1 | None for the accepted getter subset |
| W3D | Complete installed catalogue/demand, PR #906, L3 | Current live state must be rechecked before a new installed task |
| W3R | Separate shear-feasibility repair, PR #907, L1 | Not a calibrated model optimizer |
| W3E | Same-row canonical strength audit, PR #908, L1 | Required serviceability and installed-rebar acceptance remain held |
| W3F | Contracts/signatures/readback, #909/#910/#913/#914, L1-L3 | Saved building spring/slab/support basis is incomplete for calibration |
| W3G | Bounded pure solver, PR #915, L1 | Always SURROGATE_ONLY; not general 3D analysis |
| W3H | Comparator #917 and recovery/feasibility/benchmarks #918-#921 | Actual-building L5 calibration NOT complete |
| W3I | Planned functions absent at the audited base | W3H plus explicit complete screening criteria |
| W3J | Dossier/review #922/#923; persistence #926 plus separate installed update-only rollback: sixteen tables/78 rows reconcile | Bounded fictional L4 software PASS; no actual-model calibration, L7 signature or professional approval |
| W3K | Planned functions absent at the audited base | Accepted W3I, guarded fresh-copy mutation and mandatory ETABS reanalysis |
| W3L | Not implemented | Accepted W3K, finite iteration and independent final baseline repeat |

The two installed authored benchmarks are useful W3G/H software evidence, but
additional benchmark passes alone do not clear the actual-building W3H gate.
Do not turn a sequence of benchmark receipts into a claim that W3 is finished.
The saved foundation covers only one frame and three joints; it explicitly
reports `calibration_fields_complete=false`. The shortest inspected member is
pinned at both ends on moving, unrestrained building joints. That does not rule
out every action-only comparison, but no complete independent load/support/slab
mapping or project criteria has yet been accepted. Hashing cannot fill that gap.

Advance independent dependencies instead of waiting for a professional
signature: W3J depends on W3D/W3E and provider-neutral review contracts, not W3H.
Its dossier foundation is ordinary software work. It cannot assert professional
eligibility, sign bytes or upgrade a supplied provider Boolean to trusted proof.
The bounded Excel projection is merged in #923. Its installed continuation
proved trusted HTTPS and exact source bytes, but Windows control could not
activate Excel after fresh discovery and one recovery. No workbook was created
or opened and no writer/rollback ran. See the
[installed receipt](../verification/etabs-w3j-installed-review-evidence.json).
Restore reliable host control or use owner-assisted UI steps before installed transaction/readback;
retain all building-calibration and downstream candidate holds. If the building
basis cannot be proved by bounded read-only discovery, report the exact missing
physical inputs; do not guess them or ask for blanket professional approval.

The integrated Windows Python run also reported 17 failures, including alias
ownership/registry expectations and Windows launcher/path/restore ordering.
Its exact diagnosis and remaining gate results are retained in the installed
receipt/session and external logs. Repair these in a separate bounded software
packet; do not label the integrated gate green or alter live evidence code.

The bounded Windows repair now corrects those confirmed software causes without
changing engineering math, public types, timing budgets or security settings.
Its [receipt](../verification/etabs-w3-validation-repair-evidence.json) binds the
diagnostics and final external gate observations. Owner-assisted disposable
Excel UI is the simpler installed route; it still requires the same atomic
publication/readback/rollback proof. No ETABS rerun is needed for that packet.

The next bounded review packet fixes confirmed intrinsic-grid overflow and
proves native publication/readback plus comment retention and exact-successor
refresh on a separate disposable workbook: sixteen tables, 78 rows, 68,969
canonical bytes and both revision identities independently reconcile after save.
The earlier accepted workbook and all models remain unchanged. See the
[review-persistence receipt](../verification/etabs-w3j-review-completion-evidence.json).
That packet left installed update-only rollback unproved. Its separate
[native rollback successor](../verification/etabs-w3j-native-rollback-evidence.json)
now proves exact workbook identity after the user's DevTools safety hand-off,
one unchanged writer call, one labelled failure after native PENDING readback,
and exact restoration of all sixteen typed matrices/dimensions/positions.
Independent native and saved-copy verification reconcile 78 rows, 68,969 bytes,
both revisions and comments. All input/protected files remain unchanged and
owned services are stopped. This closes the bounded fictional L4 software row;
it is not a general fault-matrix, actual-building calibration, L7 or W3 claim.

Completion requires the remaining packet exits, one integrated broad
Python/FastAPI/React/Excel/full-gate run, exact final dossier and Mac integrated
review. Neither this audit nor the dossier contract is complete W3 acceptance.

The bounded [saved-building mapping assessment](../verification/etabs-w3h-building-mapping-evidence.json)
now verifies 127 retained files and all five canonical snapshot identities.
Its 153-beam/3,502-row profile proves complete force provenance but only one
normalized definition frame/three joints plus one other raw frame readback.
It records five ordered contributing cases, 132 beams with repeated object-
station coordinates and 153 with a nonzero excluded-action component. These
facts require exact factor/element/side mapping and explicit applicability
criteria; they are not engineering failure thresholds or new calibration.
The [installed mapping-signature audit](../verification/etabs-w3h-mapping-signatures-evidence.json)
now proves forty signatures and their installed help sources without application
calls. The interface is `cLineElm`, not `cFrameElm`; several element topics lack
the semantics needed for a physical interpretation. Area assignment loads are
not complete transferred beam actions. The documented table catalogue/schema
API is a narrower alternative: the next separate packet reads only available
keys and at most twelve field schemas, with exact copied-model and table-display
pre/post guards. It reads no model rows and makes no calibration claim. No new
analysis, solver extension, benchmark-only packet or W3I advance resolves the
remaining physical basis merely by producing more numerical agreement.

The [subsequent table metadata attempt](../verification/etabs-w3h-table-metadata-evidence.json)
stopped at its first table-display getter: CSI 1, count 0 and twelve null
entries. Exact model/file guards were preserved; no catalogue, schema or model
rows were read. This is not an accepted empty table selection. Next is a separate
static-first same-getter transport diagnosis, not selection recovery, analysis,
reinstall or optimization. The native cause remains unconfirmed, and actual-
building L5/W3I/K/L holds are unchanged.

The [transport successor](../verification/etabs-w3h-table-transport-evidence.json)
then stopped earlier: PowerShell could not bind a managed load-case guard call.
One attachment, zero table calls, no Python live comparison and no retries.
Saved-file identities and all 34 prior lanes are preserved; complete live model
guards were not obtained. The table-only offline stand-in missed the guard path.
Next batch must prove a complete typed compiled client offline, with every
argument explicit, before a separately frozen observation. Exact-default static
tests do not reproduce the COM binder error, so its internal cause and the
historical CSI 1 cause remain unconfirmed. No reanalysis/reinstall or model
change is justified, and W3H/I/K/L acceptance has not advanced.

### Owner-approved validation continuation (2026-08-30)

This successor decision supersedes the historical startup-only and capability
descriptions below where later accepted packets have implemented them. W3A-H
software checkpoints and installed evidence are recorded in the current
[calibration guide](../guides/beam-line-calibration.md). It does not change
public signatures, evidence levels, packet dependencies or professional holds.

The owner requested both controlled tests and comparison with the earlier real
building. Keep three separate acceptance tracks; none substitutes for another:

| Track | Reference and acceptance | Claim boundary |
|---|---|---|
| ETABS data transport | Exact saved revision, definitions, selection, units, every signed station row and canonical API/Excel bytes | Faithful transport of ETABS results, not independent analysis |
| Beam design checks | Accepted ETABS actions plus explicit materials/detailing/applicability; use the same code/preferences/overwrites for any ETABS-design comparison | Public section checks only; absent installed rebar or serviceability remains held |
| Independent force prediction | Authored benchmarks first, then physically supported building subcases with frozen mapping, scope and tolerances | Bounded numerical agreement; never arbitrary-model or whole-building parity |

The earlier W2C building acceptance covers 153 beam result sets and 3,502 force
stations with exact canonical JSON rejoin. The owner's subsequent save is a
distinct revision with fresh W3H reference evidence; do not reuse the old file
hash or relabel old results as current. Retain both revisions and their receipts.
Replay saved reference hashes/contracts without opening applications when that
answers the regression question; a replay is not fresh installed/Excel evidence.

Continue with one separately authored two-span, linear-elastic software
benchmark after the accepted single-span test. Freeze loads, connectivity,
support conditions, stiffness/shear-deformation basis, signs, station domain,
independent formulas and numerical tolerances before ETABS results exist.
Do not fit supports, signs or tolerances to obtain a match. A deliberately
Euler-Bernoulli-compatible benchmark does not validate native shear-flexible
building behaviour. Use only a new model/instance and preserve the owner files.

For later real models, first classify requested capabilities against observed
connectivity, supports, releases/offsets, stiffness, loads/combination families,
axes, slab participation and analysis settings. Unsupported or missing physical
inputs remain explicit; they do not become zero or a guessed support. A scoped
action-only study may be useful without proving displacements or full model
calibration. The moving joints in the inspected building subcase do not prove
that every member is unsuitable. Develop supported comparisons without asking
the owner to invent missing engineering facts or treating professional sign-off
as a blanket software-development prerequisite.

The next progression is two-span verification, then asymmetric/patterned-load
benchmarks and a bounded building capability/mapping assessment. No benchmark
alone unlocks W3I: model-specific calibration and required screening criteria
still govern candidate work. ETABS remains final global-analysis authority.
No construction, professional approval, release or model optimization is
authorized by this plan clarification. Windows owns this task branch; the Mac
must fetch the accepted GitHub boundary before further work.

### W2 beam baseline: useful and bounded

`ETABSBeamBaselineV1` already provides a strong read-only foundation:

- exact authorized model-file identity and before/after evidence;
- ETABS/library/runtime identity and getter-matrix digest;
- lock and temporary-unit restoration proof;
- story, point, frame, rectangular-section, local-axis, and endpoint topology;
- explicit requested result-selection evidence;
- every retained force-station row with member, source row, object/element
  stations, step identity, and signed `P`, `V2`, `V3`, `T`, `M2`, and `M3`;
- complete accepted/excluded/blocked dispositions; and
- deterministic canonical bytes and a baseline SHA-256.

Blocked inventory, topology, or result-selection conditions are resolved
before `FrameForce`. No partial accepted baseline is returned. These controls
should be extended by linked snapshots rather than weakened or silently
reinterpreted.

### W2 gaps that matter to later work

The current baseline inventories case and combination names only to validate
explicitly requested selections. It does not expose a complete typed catalogue
of:

- load patterns and self-weight multipliers;
- load-case types and relevant case parameters;
- case analysis status for the complete catalogue;
- response-combination type;
- ordered combination constituents and scale factors;
- nested combination relationships;
- design-combination ownership or purpose; or
- the exact definition digest used by a future local or ETABS reanalysis.

It also retains endpoint topology but does not yet interpret a beam line,
support condition, span continuity, releases, offsets, stiffness modifiers, or
slab participation. Those are engineering-model inputs, not safe inferences
from frame labels.

### Beam design and optimization truth

The canonical beam service is valuable but currently consumes one non-negative
factored `Mu/Vu/Tu` action triple. Its serviceability field is deliberately
held until strict typed serviceability models are frozen. A short provenance
string is not enough to bind a design decision to an ETABS baseline, member,
selection, station, step, and envelope rule.

The maintained single-objective cost optimizer:

- searches rectangular singly reinforced sections;
- evaluates flexure and shear for fixed caller-supplied actions;
- uses an explicit stirrup area for shear feasibility; and
- reports longitudinal-steel/concrete/formwork cost while explicitly excluding
  stirrup mass and cost.

It does not evaluate torsion, serviceability, continuity, stiffness
redistribution, model provenance, beam families, or whole-model constraints.
Its result is therefore a fixed-action screening result.

The current Pareto optimizer has an outcome-changing defect: it accepts
`vu_kn` but its candidate path performs flexure only and marks candidates safe
without a shear check. It must remain held from engineering or ETABS candidate
selection until shear participates in feasibility and reported utilization.

The rebar optimizer is a useful deterministic bar-arrangement helper for a
known required steel area. It is not a frame solver, action generator,
torsion/shear design, or complete constructability optimizer.

### Independent analysis truth

There is no accepted direct-stiffness or continuous-beam solver in the current
library. The gravity workflow is solver-free, and the serviceability module
explicitly limits its continuous-beam approximation. The older Project BHEEM
masterplan contains a broad future FEM vision; it is not current capability,
acceptance evidence, or the execution plan for this bounded programme.

## Architecture decision

Use four explicit layers and never pass vendor-shaped COM arrays into the
engineering API:

```text
ETABS adapter and evidence
  - attach/read/verify, normalize units, retain vendor identities
                     |
                     v
Versioned public data contracts
  - immutable model context, definitions, demands, scenarios, provenance
                     |
                     v
Pure library analysis and design
  - beam-line surrogate, beam checks, serviceability, constructability
                     |
                     v
Optimization and verification orchestration
  - propose, rank, compare, shortlist; ETABS mutation remains a guarded adapter
```

ETABS remains the final global-analysis authority. The local solver is a
surrogate for gravity-dominated beam-line screening and sensitivity studies.

### Architecture ownership and allowed dependencies

| Owner | Planned paths | Responsibility | Must not own |
|---|---|---|---|
| Core contracts | `Python/structural_lib/core/analysis_contracts.py`, later `core/beam_line.py` | Vendor-neutral immutable states, definitions, action rows, scenarios, governing references, beam-line requests/results | COM objects, ETABS enum decoding, I/O, IS 456 calculations |
| IS 456 calculations | Existing `Python/structural_lib/codes/is456/` modules | Pure code checks over explicit units and accepted demand/design inputs | ETABS access, Excel transport, optimization orchestration |
| Services/contracts | `Python/structural_lib/services/contracts/etabs_w3.py` | ETABS identity wrappers, catalogue/snapshot build requests and results, hash-link contracts | Raw vendor arrays in public values, hidden engineering defaults |
| ETABS adapter | Later `Python/structural_lib/services/etabs_w3_adapter.py` | Decode reviewed getters, normalize units, enforce model/runtime/getter identity, produce normalized build requests | Analysis/design/setters except a separately approved future mutation adapter |
| Demand and audit services | Later `Python/structural_lib/services/beam_demand.py`, `beam_audit.py` | Pure derivation, paging, audit composition, evidence/status propagation | COM access or Excel writes |
| Optimization orchestration | Existing optimizer services plus later candidate services | Feasibility-first generation, deterministic ranking, shortlist and comparison | Global-analysis acceptance or bypass of ETABS reanalysis |
| UI/transport | `fastapi_app/`, `excel_addin/`, narrow React review surfaces | Versioned request/response projection, formula-free workbook review, explicit evidence display | Structural recomputation or silent state coercion |

The dependency direction remains Core -> IS 456 -> Services -> UI/IO. A
vendor-neutral core contract may be used by an ETABS, CSV, Excel, SAFE, or
future solver adapter; a core or IS 456 module may never import an ETABS service
or transport model. W3A must either root-export each accepted public symbol
through the maintained service facade and `structural_lib` facade or record it
as intentionally adapter-internal. It may not create an undocumented third
public surface.

## Data foundation

### Snapshot set

Do not create one unbounded “all ETABS data” object. Use immutable, hash-linked
snapshots with explicit scope:

| Snapshot | Required content | Normal size/use |
|---|---|---|
| `ETABSModelContextV1` | File/hash/version, lock, units, runtime/getter identity, analysis state, active output selections | Small preflight identity |
| `ETABSModelDefinitionSnapshotV1` | Stories, points, frames, sections/material labels, axes, connectivity, assignments, releases, offsets, modifiers, supports and explicitly captured area/diaphragm context | Broad model semantics |
| `ETABSResultCatalogueV1` | Load patterns, cases, case status, combinations, ordered/nested components, scale factors, output-selection state and catalogue digest | Definition authority |
| Existing `ETABSBeamBaselineV1` | Complete bounded beam topology and same-row signed force stations for requested selections | Heavy immutable W2 evidence |
| `ETABSDisplacementSnapshotV1` | Joint/member displacement rows for explicit selections, with node, step, units, source row and catalogue/baseline identity | Optional calibration evidence; new getter scope |
| `BeamDemandSnapshotV1` | Compact member/scenario demand records with references to exact baseline station IDs | W3 design/audit input |
| `ETABSReanalysisEvidenceV1` | Pre/post model identity, approved change plan, run status, fresh result identity, comparison and abort/revert evidence | Future W6 only |

The existing exported-file `ETABSCanonicalSnapshotV1` remains a useful
export-first path, but its old `ProjectBeamDesignInputV1` projection must not be
treated as the live W3 successor. It reduces forces to fixed `mu_knm/vu_kn` and
uses generic metadata; W3 should instead link to exact demand scenarios and the
strict current beam contract.

### Required model fields

Fields are required when their absence would change analysis, design, or the
ability to reproduce a decision:

- saved model path/name and SHA-256, ETABS version, library/adapter identity;
- model lock, present/database units, analysis completion/freshness evidence;
- stories, coordinates, stable object names, labels and story assignments;
- frame connectivity, local axes, end releases, offsets/insertion points;
- assigned section, material property, auto-select state and stiffness/mass/
  weight modifiers;
- support/restraint/spring data used by the bounded beam-line model;
- load-pattern type and self-weight multiplier;
- load-case type, relevant parameters and analysis status;
- combination type, ordered constituents, scale factors and nested references;
- exact cases/combinations selected for output;
- member, station, output case, step type/number and signed six-component
  action row; and
- design preferences/overwrites only when a comparison claims to reproduce
  ETABS design behavior.

Concrete grade, reinforcement grade, cover, bar sizes, detailing standard,
cracked-stiffness basis, support interpretation, slab participation and seismic
applicability must remain explicit caller-owned engineering inputs unless an
exact typed ETABS getter contract proves them.

### Optional-field policy

Optional must mean one of:

1. a read-only filter that narrows an otherwise defined query;
2. one of several explicit alternative representations;
3. an opt-in module whose omission visibly holds that check; or
4. an expected-state guard used only for a future mutation request.

Every calculation-bearing value that can be absent uses one exact public state:

| State | Meaning | Value rule |
|---|---|---|
| `PRESENT` | Getter/caller supplied and validated the value | `value` is present; zero, `false`, and an empty bounded collection remain valid values |
| `UNAVAILABLE` | The approved source cannot provide the value in this evidence packet | `value` is absent; stable reason and source evidence are required |
| `NOT_REQUESTED` | The approved query deliberately omitted an opt-in module | `value` is absent; the dependent check remains visibly held |
| `NOT_APPLICABLE` | The field cannot apply to the declared type/scenario | `value` is absent; applicability basis is required |
| `BLOCKED` | The value is required for the requested outcome but failed validation or is missing | `value` is absent; no accepted parent result may be returned |

The exact reusable contract is `EvidenceValueV1[T]` with `state`, `value`,
`reason_code`, `message`, and `source_references`. `PRESENT` requires a non-null
typed value and forbids a blocking reason. Every other state requires a null
value and a stable reason. `None` by itself is never a public semantic state.
An omitted JSON key is accepted only for a read filter or backward-compatible
request default whose omission cannot change an engineering conclusion.

Do not substitute hidden engineering defaults and do not copy COM by-reference
output arrays into the public API. Unsupported selected-case parameters,
missing combination factors, an unfinished selected case, or an absent action
row must become `BLOCKED`, not `UNAVAILABLE` or zero.

### Result volume and access

Keep the W2 capacity limits and fail on overflow rather than truncating. Build
member/scenario envelopes lazily from the immutable station inventory. Normal
W3 results should return compact governing references; raw stations should be
available through an explicit read-only paged/detail query. This avoids a
second unbounded transport while retaining lossless evidence.

## Demand and envelope foundation

The current live pilot independently chooses absolute maxima for `V2`, `T`,
and `M3`; those extrema can come from different rows. That is acceptable only
as explicitly labelled independent-component screening. It must not be called
a concurrent load state.

W3A freezes the following transport-neutral public contracts before any ETABS
getter is added.

### Definition catalogue contracts

| Contract | Required semantics |
|---|---|
| `LoadPatternDefinitionV1` | Stable ID/name, raw and normalized type, exact self-weight multiplier, source ordinal and evidence reference |
| `LoadCaseParameterSetV1` | Discriminated case-family union; selected supported families require typed parameters, while unsupported families retain identity plus an explicit non-`PRESENT` evidence state |
| `LoadCaseDefinitionV1` | Stable ID/name, raw type/subtype/design type, auto flag, typed parameter set, analysis-status reference and definition digest |
| `AnalysisStatusIdentityV1` | Case ID, raw installed status code, normalized state, getter/signature identity, model/catalogue observation bracket and evidence time |
| `ResponseCombinationFactorV1` | Zero-based ordinal, source kind (`CASE` or `COMBINATION`), exact source ID/name and signed scale factor |
| `ResponseCombinationDefinitionV1` | Stable ID/name, raw and normalized combination type, ordered factor tuple, definition digest and design-purpose evidence |
| `ResultSelectionIdentityV1` | Selection ID/kind/name, selected-for-output state, linked case status or combination definition, model/runtime/getter identity and observation bracket |
| `ETABSResultCatalogueV1` | Model/runtime identity, complete pattern/case/combination inventories, selection identities, getter-matrix digest, capacity counts and catalogue SHA-256 |

The initial `LoadCaseParameterSetV1` discriminated union contains
`LinearStaticCaseParametersV1` with ordered `LinearStaticLoadItemV1` values and
`UnsupportedCaseParametersV1` with retained raw type/subtype plus a non-
`PRESENT` evidence state. Additional modal, response-spectrum, nonlinear or
other family parameter types require their own later versioned contract and
installed getter packet; W3A does not stuff arbitrary mappings into the union.

Combination factors remain ordered and lossless. Repeated factors are not
coalesced, signed factors are not converted to absolute values, and nested
combinations reference exact combination IDs. Catalogue validation rejects a
missing factor target, duplicate stable ID, cycle in the nested-combination
graph, unproved selected definition, unfinished selected case, or digest
mismatch. Names alone are never definition identity.

W3A does not pretend to know every ETABS case-family getter. It freezes the
discriminated union and fail-closed unsupported-family state; W3B then proves
the installed 23.3.1 getter/signature surface, and a later Mac adapter packet
implements only the accepted subset. A case used by an accepted scenario must
have `PRESENT` parameters sufficient for that scenario.

### Same-row action, scenario, envelope, and governing contracts

`BeamActionRowV1` is a lossless design-facing projection of one retained W2
force row. It requires the model, W2 baseline and catalogue digests; member,
source frame and stable station IDs; selection ID/kind/name; exact output-case
name; object/element names and stations; step type/number; source row index;
signed `P`, `V2`, `V3`, `T`, `M2`, and `M3`; unit and local-axis basis; and a
row digest. All six actions always travel together. An action component may not
be copied into a different row or stripped of its sign.

`BeamDemandScenarioV1` requires scenario ID/revision, purpose (`STRENGTH`,
`SERVICE`, or `COMPARISON`), catalogue and baseline digests, included selection
IDs, member/station domain, component requirements, rule IDs, deterministic
tie-break policy, and explicit held checks.

`BeamDemandEnvelopeRuleV1` declares exactly one mode:

- `SAME_ROW_CONCURRENT`: one retained row supplies every reported component;
- `SIGNED_COMPONENT_EXTREMA`: positive and negative extrema are separate
  governing references and are not called one concurrent state;
- `INDEPENDENT_ABSOLUTE_COMPONENTS`: each absolute component may cite a
  different row and the result is labelled screening-only; or
- `CALLER_DEFINED_CODE_ENVELOPE`: the caller supplies a typed rule/basis and
  every contributing row remains referenced.

`BeamGoverningReferenceV1` binds scenario, member, component/sign, rule,
governing value, action-row ID(s), selection and deterministic tie-break. A
concurrent reference must cite exactly one row. A multi-row reference must
declare itself non-concurrent. `BeamDemandSnapshotV1` contains compact
governing references plus hashes/counts; `BeamActionPageV1` provides explicit
bounded access to raw rows without duplicating or truncating evidence.

### Exact W3A public function signatures

The W3A implementation packet must use these signatures or stop and update the
accepted plan before changing them:

```python
def build_etabs_result_catalogue_v1(
    request: ETABSResultCatalogueBuildRequestV1, /
) -> ETABSResultCatalogueBuildResultV1: ...

def canonical_etabs_result_catalogue_hash_basis_json_v1(
    catalogue: ETABSResultCatalogueV1, /
) -> str: ...

def verify_etabs_result_catalogue_hash_v1(
    catalogue: ETABSResultCatalogueV1, /
) -> bool: ...

def derive_beam_demand_snapshot_v1(
    request: BeamDemandDerivationRequestV1, /
) -> BeamDemandBuildResultV1: ...

def canonical_beam_demand_snapshot_hash_basis_json_v1(
    snapshot: BeamDemandSnapshotV1, /
) -> str: ...

def verify_beam_demand_snapshot_hash_v1(
    snapshot: BeamDemandSnapshotV1, /
) -> bool: ...

def query_beam_action_rows_v1(
    baseline: ETABSBeamBaselineV1,
    *,
    member_ids: tuple[str, ...] = (),
    selection_ids: tuple[str, ...] = (),
    cursor: str | None = None,
    limit: int = 1000,
) -> BeamActionPageV1: ...
```

Build functions return `ACCEPTED` with one complete immutable value and no
issues, or `BLOCKED` with stable issues and no partial value. The ETABS-named
builder owns identity/provenance validation over normalized inputs; W3A does
not accept `sap_model: Any` as a root public parameter. Installed COM decoding
stays in the later adapter. Demand derivation remains adapter-neutral and
reusable by CSV, Excel, SAFE, or future analysis sources.

### Later public snapshots and functions needed for calibration

The following are planned after W3A and the installed getter audit:

```python
def build_etabs_model_definition_snapshot_v1(
    request: ETABSModelDefinitionBuildRequestV1, /
) -> ETABSModelDefinitionBuildResultV1: ...

def build_etabs_displacement_snapshot_v1(
    request: ETABSDisplacementBuildRequestV1, /
) -> ETABSDisplacementBuildResultV1: ...

def build_etabs_reaction_snapshot_v1(
    request: ETABSReactionBuildRequestV1, /
) -> ETABSReactionBuildResultV1: ...

def verify_etabs_model_definition_snapshot_hash_v1(
    snapshot: ETABSModelDefinitionSnapshotV1, /
) -> bool: ...

def verify_etabs_displacement_snapshot_hash_v1(
    snapshot: ETABSDisplacementSnapshotV1, /
) -> bool: ...

def verify_etabs_reaction_snapshot_hash_v1(
    snapshot: ETABSReactionSnapshotV1, /
) -> bool: ...
```

The model-definition snapshot must capture exact beam-line connectivity,
coordinates, local axes, sections/material labels, end releases, end offsets/
insertion points, stiffness/mass/weight modifiers, restraints, springs,
assigned loads and explicitly supplied diaphragm/slab context. Displacement
rows retain joint/object/element identity, selection, step, six signed degrees
of freedom, source row, units and model/catalogue digests. Reaction rows retain
support/joint identity, selection, step, six signed components, source row,
units and the same digests. Missing displacement evidence permits an explicit
action-only comparison; missing required topology or reaction evidence blocks
the calibration mode that depends on it.

## Local beam-line surrogate

### Bounded scope

Implement a public, transport-neutral, 2D linear-elastic Euler-Bernoulli
continuous-beam solver using the direct-stiffness method. Its first accepted
scope is:

- one horizontal beam line with one to five prismatic spans;
- vertical translation and nodal rotation degrees of freedom;
- explicit simple/fixed/rotational-spring support conditions;
- bounded end releases and rigid/end offsets only after their contract freezes;
- uniform and point loads;
- explicit factored and service load scenarios;
- section `E`, `I`, density/self-weight basis and stiffness modifier;
- nodal displacements/rotations, reactions, member-end actions, station
  diagrams and equilibrium residuals; and
- mandatory `SURROGATE_ONLY` capability status.

Do not include 3D framing, diaphragms, shell/slab elements, lateral/seismic or
wind analysis, modal response, P-Delta, material nonlinearity, staged
construction, soil-structure interaction, or ETABS-parity claims.

### Proposed public contracts and functions

- `BeamLineNodeV1`, `BeamLineSpanV1`, `BeamLineSupportV1` and
  `BeamLineSupportSpringV1` freeze geometry, degrees of freedom, releases,
  offsets and support stiffness without inferring them from ETABS labels.
- `BeamLineLoadCaseV1`, `BeamLineCombinationV1` and `BeamLineScenarioV1`
  freeze UDL/point/self-weight loads, signed factors, service/factored purpose,
  patterned loading and deterministic uncertainty assumptions.
- `BeamLineAnalysisRequestV1` binds model-definition, catalogue and scenario
  digests, explicit `E`, `I`, density and stiffness modifier, unit basis,
  station sampling and finite limits.
- `BeamLineAnalysisResultV1` retains nodal translations/rotations, reactions,
  member-end actions, signed station diagrams, equilibrium residuals,
  deterministic hash and mandatory `SURROGATE_ONLY` status.

```python
def solve_beam_line_linear_v1(
    request: BeamLineAnalysisRequestV1, /
) -> BeamLineAnalysisBuildResultV1: ...

def compare_beam_line_to_reference_v1(
    request: BeamLineComparisonRequestV1, /
) -> BeamLineCalibrationV1: ...
```

Torsion cannot be derived by the first 2D solver. It must be supplied from an
ETABS demand scenario or reported as `HELD_NOT_DERIVED`.

An accepted numerical solver does not by itself clear independent-frame-
analysis status. `HELD_NOT_SUPPORTED` remains on the existing ETABS baseline
and public capability until the solver has passed its own acceptance packet
and an independently accepted calibration packet binds it to the exact model,
definitions, selections, actions and required displacement/reaction evidence.
Calibration clears only the declared model/scenarios/components; it never
establishes general ETABS parity.

### Scenario and uncertainty model

Use named deterministic scenarios rather than an unsupported reliability
claim:

- nominal extracted geometry/stiffness/load basis;
- lower and upper effective `EI`;
- lower and upper support rotational stiffness;
- patterned service/live loads;
- explicit slab-participation alternatives where supplied; and
- any engineer-approved conservative scenario.

Produce the best candidate per scenario, a Pareto shortlist, and one robust
candidate that passes every mandatory scenario. Do not select only the optimum
under an optimistic assumption.

### Calibration boundary

`BeamLineCalibrationV1` must bind:

- ETABS model/baseline/catalogue digests;
- exact member/span/station/result selection mapping;
- compared action/displacement components;
- predeclared absolute and relative tolerances;
- local assumptions; and
- `CALIBRATED`, `OUT_OF_BAND`, or `NOT_COMPARABLE` status.

Calibration is model/version specific and invalidates when geometry, loads,
combination definitions, releases, modifiers, supports, analysis settings, or
the ETABS file digest changes. It improves local screening; it does not promote
the local solver to final authority.

## Optimization and ETABS verification loop

The target loop is:

```text
accepted baseline and definitions
  -> group constructible beam families
  -> generate bounded section/rebar candidates
  -> solve local factored and service scenarios
  -> run canonical strength/serviceability/constructability checks
  -> reject held or unsafe candidates
  -> rank a small robust shortlist
  -> apply one candidate plan to an authorized copied ETABS model
  -> run only approved analysis cases
  -> extract a fresh hash-bound demand snapshot
  -> redesign and compare all affected constraints
  -> accept, revise, or reject with a finite stopping rule
```

The original model remains untouched. Every future ETABS candidate starts from
the same approved baseline copy, not from cumulative unverified mutations.

Future public orchestration types:

- `BeamFamilyDefinitionV1`
- `CandidateSectionPlanV1`
- `CandidateScreeningResultV1`
- `CandidateShortlistV1`
- `ETABSReanalysisPlanV1`
- `ETABSReanalysisEvidenceV1`
- `AnalysisIterationComparisonV1`

Planned orchestration signatures are:

```python
def screen_beam_family_candidates_v1(
    request: CandidateScreeningRequestV1, /
) -> CandidateScreeningBatchResultV1: ...

def build_candidate_shortlist_v1(
    request: CandidateShortlistRequestV1, /
) -> CandidateShortlistV1: ...

def build_etabs_reanalysis_plan_v1(
    request: ETABSReanalysisPlanRequestV1, /
) -> ETABSReanalysisPlanBuildResultV1: ...

def compare_etabs_reanalysis_v1(
    request: ETABSReanalysisComparisonRequestV1, /
) -> AnalysisIterationComparisonV1: ...
```

`ETABSReanalysisPlanV1` must include an allowlisted copy, baseline hash,
expected old assignments, proposed new definitions/assignments, approved cases,
combination/catalogue digest, backup identity, unit/lock policy, save target,
abort policy and finite evaluation budget. This is a future separately reviewed
mutation contract, not part of the initial solver.

Local screening may reject candidates and may rank a bounded shortlist. It may
not declare a changed section/family accepted for the ETABS model. Every
shortlisted candidate that remains under consideration requires fresh ETABS
reanalysis on an authorized recoverable copy before any final selection, and
the chosen final candidate requires one independent repeat from the clean
approved baseline. Fresh force results, displacements/reactions and every
predeclared whole-model safeguard are compared against their exact prior
identities. A locally feasible candidate that lacks successful ETABS
reanalysis is `SCREENED_ONLY`, never approved.

## Evidence levels

Evidence levels are cumulative only when every predecessor identity remains
exact. One level must never be described as a higher level:

| Level | Evidence | Permitted claim |
|---|---|---|
| `L0_PLAN` | Reviewed plan, repository/Git authority and frozen boundaries | Scope and sequence only |
| `L1_LOCAL_SOFTWARE` | Mac types, validators, hashes, fakes, pure functions and maintained tests | Local software behavior only |
| `L2_INSTALLED_SIGNATURE` | Installed ETABS 23.3.1 assembly/type-library/generated-wrapper identities and exact getter signatures/shapes | Compatibility of the frozen adapter surface; no model value or live result claim |
| `L3_INSTALLED_READ_ONLY` | Exact authorized copied model, live getter return codes/shapes/data, unchanged file/lock/units and hash-linked snapshots | Bounded read-only installed evidence for that model/version |
| `L4_INSTALLED_EXCEL_REVIEW` | Saved workbook typed-cell readback, all-table transaction/rollback and exact canonical rejoin/hash | Bounded Excel transport/review evidence |
| `L5_SOLVER_CALIBRATION` | Accepted solver benchmarks plus model-specific action/displacement/reaction comparison under frozen tolerances | `SURROGATE_ONLY` screening for declared model/scenarios/components |
| `L6_CONTROLLED_REANALYSIS` | Authorized copied-model mutation, approved ETABS analysis, fresh snapshots, restore/save and whole-model comparison | One bounded ETABS-verified candidate result; no professional approval |
| `L7_QUALIFIED_REVIEW` | Immutable dossier, in-scope qualified review and independently verified external signature evidence | The recorded professional decision only, subject to jurisdiction/project scope |

`HELD_NOT_SUPPORTED` remains the independent frame-analysis verdict through
`L0`-`L4`. `L5` adds a bounded `SURROGATE_ONLY` capability; it does not rename
or erase the existing verdict or establish general solver parity.

## Dependency-ordered execution packets

### P0 — Complete predecessor: PR #899 integrated

PR #899 merged as exact commit `7af545ec0e239bac8fa6d480ecbb2b05a60aa40d`
with tree `cc40650b7f6569227c880d61a9967ee3bbdfab31`. It contains the accepted W2C
foundation and W3-readiness maintenance. This is software/evidence readiness,
not solver, mutation, optimization or professional acceptance.

### W3A — Mac read-only definition and demand contracts (`L1`)

Owner: Mac. Dependency: accepted plan and exact P0 predecessor. Indicative
effort: 8-15 focused engineer-days.

- Add the frozen availability, definition/catalogue, analysis-status,
  selection, same-row action, scenario, envelope, governing-reference, page and
  build-result contracts.
- Add the exact public functions listed above, deterministic canonical hashes,
  root/service exports and caller/API ledger registration.
- Use normalized fake-adapter fixtures only. Do not add a COM dependency,
  FastAPI operation, Excel write, beam design call, solver or optimizer call.
- Keep the existing W2 types byte-compatible; link rather than reinterpret
  `ETABSBeamBaselineV1`.

Focused acceptance: strict unknown-field rejection; all five evidence-value
states including valid zero/false `PRESENT`; ordered/nested factors; missing
target and cycle rejection; finished/selected identity; same-row concurrency;
cross-row concurrency rejection; deterministic tie-breaking; canonical hash
round-trip/tamper rejection; lossless paging/capacity failure; architecture and
public-export/ledger checks. Accepted builds expose one complete value and no
issues; blocked builds expose issues and no partial value.

### W3B — Windows installed 23.3.1 getter/signature audit (`L2`)

Owner: Windows evidence laptop. Dependencies: accepted and merged W3A contract,
exact W3A commit/tree supplied in the handoff, and separate user authorization
to start the laptop task. Indicative effort: 2-4 focused days.

This is metadata/signature evidence first. It must not create a COM object,
attach to ETABS, open a model/workbook, or call a getter. Reprove the exact
installed ETABS `23.3.1.4563`/x64 type-library/generated-wrapper/runtime
identity and audit the W3A-required getter candidates:

- `LoadPatterns.GetNameList`, `GetLoadType`, `GetSelfWTMultiplier`;
- `LoadCases.GetNameList`, `GetTypeOAPI`, and only the case-family definition
  getters selected by the accepted W3A union/inventory policy;
- `RespCombo.GetNameList`, `GetTypeOAPI`, `GetCaseList`/installed overload;
- `Analyze.GetCaseStatus`, `Results.Setup.GetCaseSelectedForOutput`, and
  `GetComboSelectedForOutput`; and
- the existing `Results.FrameForce` contract only to bind retained W2 row
  provenance to the same installed source identity.

For every operation record the managed signature, argument/output order and
types, optional/default inputs, enum identity, CSI return-code form, generated
Python call signature, outer/SAFEARRAY container expectations, source file
hash and verdict. Unknown overloads or version drift are `BLOCKED`, not guessed.

### W3C — Mac ETABS catalogue adapter and transport-neutral integration (`L1`)

Owner: Mac. Dependencies: accepted W3A and W3B. Indicative effort: 5-10 focused
days.

- Implement only the `PROVED` getter decoders behind the ETABS service boundary.
- Convert reviewed COM shapes to normalized W3A build requests and retain every
  operation verdict/source identity.
- Use list/tuple/scalar fake shapes and nonzero return-code fixtures; no installed
  application access occurs on Mac.
- Add a versioned service/REST surface only if the accepted user journey needs
  it; otherwise keep the builder as the public library surface.

Exit: every approved fake inventory is complete and deterministic; any missing
definition, unsupported selected case family, getter drift, nonzero return,
capacity overflow or identity mismatch blocks before an accepted catalogue.

W3D live evidence later established one narrow installed-sentinel correction:
`LoadCases.StaticLinear.GetInitialCase` may return blank or the literal `None`
for zero unstressed initial conditions. `LinearStaticInitialConditionV1`
retains that raw value and normalizes only those two forms to
`ZERO_UNSTRESSED`; any actual prior-case name remains blocked until its
nonlinear stiffness semantics and target identity have a separately accepted
contract. This correction does not authorize a setter, analysis or model
mutation.

The first clean continuation from accepted R1 exposed a second narrow installed
value-domain correction. ETABS 23.3.1 returned exact `Auto=5` from
`LoadCases.GetTypeOAPI_1` for an internal case, while CSI's published 0/1
mapping does not define that value. `LoadCaseDefinitionV1` therefore retains
`raw_auto_flag` exactly and represents `is_auto` as an `EvidenceValueV1[bool]`:
documented 0/1 values are `PRESENT`, while any other exact integer is
`UNAVAILABLE` with a stable reason. The adapter must not coerce a nonzero value
to `true`, drop the case, or reject an otherwise complete catalogue solely
because the Boolean interpretation is undocumented.

### W3D — Windows live read-only catalogue acceptance (`L3`)

Owner: Windows evidence laptop. Dependencies: accepted W3C, a separately
authorized exact copied model and explicit permission to open/attach ETABS.
Indicative effort: 3-7 focused days.

Run getter-only preflight, compare the exact model/runtime/getter identity with
the approved handoff, then extract one complete catalogue and the linked
same-row demand snapshot. Do not select outputs, run analysis/design, unlock,
save, or write Excel. Reconcile direct and source-bound REST canonical hashes;
postflight must prove file/hash/size/mtime, lock, units and output-selection
state unchanged.

Windows acceptance on 2026-08-30 completed this boundary after the separately
reviewed R1/R2 installed-sentinel repairs. The complete catalogue contains 12
patterns, 15 cases, 62 combinations and 254 ordered factors; its direct and
localhost REST canonical identity is `d44e6b89...`. The linked 153-member,
3,502-row same-row demand snapshot reconciles at `7c1a4e21...`. The copied
model identity, lock, units, all case statuses and all 77 output-selection
states remained unchanged. This is installed-software evidence only: ETABS
remains global-analysis authority, and independent frame analysis plus
professional approval remain held.

### W3R — Separate Pareto shear-feasibility repair (`L1`)

Owner: Mac. Dependency: it does not block W3A-W3D, but it blocks all reuse of
the Pareto optimizer for candidate selection. Indicative effort: 2-5 focused
days. It must remain a separate candidate/PR from W3A.

Confirmed defect: public `optimize_pareto_front(span_mm, mu_knm, vu_kn, ...)`
accepts `vu_kn`, imports only flexure in its candidate path, sets
`is_safe=True`, and reports flexural utilization without a shear check.

- Route candidate feasibility through the maintained shear design/check with
  explicit stirrup inputs, or fail closed on nonzero shear until a compatible
  typed contract is accepted.
- Report flexure and shear utilization/check evidence separately and compute a
  truthful governing feasibility status.
- Reject unknown objective names rather than silently treating them as cost.
- Preserve explicit holds for torsion, serviceability, stirrup cost and
  fixed-action/global-analysis limitations.

Focused acceptance: a deliberately high-shear demand cannot return any safe or
best Pareto candidate; changing `vu_kn` changes feasibility/results; safe
fixtures reconcile the maintained shear service; unknown objectives fail;
public Python, FastAPI response and compatibility surfaces remain coherent.

Windows implementation acceptance on 2026-08-30 routes every retained
candidate through the maintained IS 456 shear design using explicit
`asv_mm2` (default two-legged 8 mm), reports flexure, maximum-shear-stress and
stirrup utilization separately, and uses their maximum as the compatibility
`utilization` value. Demands of 60 and 200 kN produce different Pareto
membership, while the deliberately infeasible 500 kN fixture returns no safe
or best candidate. Unknown objective names fail before search. Python,
FastAPI/OpenAPI and the maintained React client expose the same evidence and
retain explicit holds for torsion, serviceability, stirrup cost, and
fixed-action/global-analysis limitations. This is local software-contract
acceptance pending the packet's normal immutable review; it is not ETABS,
engineering, professional, construction or release approval.

### W3E — Beam audit evaluator (`L1`, later `L3` evidence)

Owner: Mac implementation; Windows supplies no new evidence unless an accepted
W3D snapshot is exercised. Dependencies: W3A/W3D. Indicative effort: 10-20
focused days.

Build strict beam-audit inputs from accepted scenarios and explicit materials,
detailing, serviceability and applicability bases. Every flexure, shear,
torsion, serviceability or held outcome cites its scenario, governing action
row(s), assumptions and clause evidence. Missing design-bearing inputs remain
`BLOCKED`/held, not assumed.

```python
def build_beam_audit_inputs_v1(
    request: BeamAuditInputBuildRequestV1, /
) -> BeamAuditInputBuildResultV1: ...

def evaluate_beam_audit_v1(
    request: BeamAuditEvaluationRequestV1, /
) -> BeamAuditEvaluationResultV1: ...
```

W3E implementation evidence is recorded in
`../verification/etabs-w3e-beam-audit-evidence.json`. The two planned public
functions are owned by `services/beam_audit.py` and exported from
`structural_lib`. Inputs bind the accepted demand derivation and snapshot,
explicit per-member evidence, serviceability requirement and a finite complete
row bound. All retained rows—not an independently maximized action triple—are
checked through `canonical_beam.check`. Results retain signed row identity,
face mapping, complete canonical JSON/hash, clauses and per-check governors.
The caller supplies applicability limits and factored/material/detailing bases;
these are never derived from an ETABS material label or chosen by the library.
The existing canonical serviceability scope hold remains explicit. W3E does
not return an accepted parent when serviceability is required but unevaluable,
or when any requested basis/scenario check is explicitly BLOCKED. Optional
unevaluated serviceability remains UNAVAILABLE/NOT_REQUESTED/NOT_APPLICABLE.
W3E does
not claim supplied/installed reinforcement adequacy, serviceability, global
analysis, or professional approval. This is L1 synthetic software evidence,
not new installed W3D evidence.

### W3F — Model/topology/displacement/reaction foundation (`L1` then `L2/L3`)

Owner: Mac contracts/adapter; Windows static and live evidence are separately
bounded continuations. Dependencies: W3A-W3D. Indicative effort: 10-25 Mac days
plus 3-7 Windows evidence days.

Freeze the model-definition, displacement and reaction contracts/functions
listed above. Then audit installed signatures for exact release, offset,
modifier, restraint/spring, displacement and reaction getters before any live
call. Live acceptance uses explicit node/member/selection limits and unchanged
model-state proof. An action-only dataset may be accepted as such but cannot
support displacement/reaction calibration claims.

The W3F L1 implementation freezes the six signatures above in the maintained
ETABS service-contract owner, with vendor-neutral definitions/results in
`core/analysis_contracts.py`. Its evidence is recorded in
`docs/verification/etabs-w3f-foundation-evidence.json`: explicit frame and
nodal loads, complete source-row counts, exact saved/version/state identity,
five-state evidence propagation and deterministic separate snapshots. This
does not prove installed signatures, live extraction, a numerical solver or
calibration. Those retain the separate L2/L3 and W3G/H acceptance gates.

The bounded W3F readback adapter consumes caller-recorded getter outputs; it
does not attach to COM. Installed ETABS 23.3.1 metadata and help bind its exact
shapes and semantics in
`docs/verification/etabs-w3f-installed-signature-evidence.json`. It retains
joint-local signed results, both insertion mirrors and explicit missing states.
Its initial normalization is explicitly kN/m/C only, with at most five frames,
sixteen joints and 2,000 total returned rows. Unproved spring/step forms do not
become defaults. Missing a requested joint-result group makes the entire
requested displacement or reaction snapshot UNAVAILABLE, not a partial value.
None of these software bounds declares a calibrated beam line or model-specific
engineering assumptions. The owner requested a session stop after W3F on
2026-08-30; W3G and later packets resume only in the next chat.

The installed spring diagnostic exposed one narrow W3F contract correction:
`ModelFrameDefinitionV1.line_spring_assignment` now retains five-state string
evidence. Omitted input is explicitly NOT_REQUESTED, not a no-spring assumption.
An unsuccessful, shape-valid point/frame assignment query is UNAVAILABLE in a
non-calibration read. Required calibration still blocks, as does malformed
readback; named line-spring properties remain outside the bounded decoder.
Calibration completeness requires PRESENT empty line-assignment evidence and
all other required physical fields. A property name is not a stiffness model.
This additive representation and its new canonical bytes do not change the six
public function signatures or certify prior snapshots that lacked this field.
The original blocked raw evidence remains immutable. PR #913 accepted the repair;
its exact merged source completed 40 installed getter records with unchanged
file/state, three displacement rows, one reaction row and all 24 signed components
reconciled. See `../verification/etabs-w3f-spring-live-evidence.json`. Springs and
diaphragm/slab context remain UNAVAILABLE; required-calibration mode still blocks.
This W3F read-only checkpoint does not start W3G or accept model-specific calibration.

### W3G — Bounded 2D beam-line surrogate (`L1`; verdict still held)

Owner: Mac. Dependencies: accepted W3F contracts; no installed application
dependency for the pure kernel. Indicative effort: 20-40 focused days.

Implement the one-to-five-span Euler-Bernoulli scope and exact signatures above.
Acceptance requires simply supported UDL/point-load closed forms, symmetric
continuous-beam cases, support/release behavior, unit-aware absolute-plus-
relative tolerances, equilibrium residual at most `1e-8` of nonzero applied-load
norm with an absolute floor, deterministic serialization, and typed failure for
singular/unstable systems. Torsion and all excluded 3D/nonlinear effects remain
held. Passing W3G produces `SURROGATE_ONLY`; it does not clear
`HELD_NOT_SUPPORTED` without W3H.

The owner resumed W3G on the Windows campaign task on 2026-08-30. This bounded
pure-kernel packet uses `core/beam_line.py` for immutable inputs/results and
`services/beam_line.py` for `solve_beam_line_linear_v1(request, /)`, with root
facade exports. No installed application is needed or called. The planned
`compare_beam_line_to_reference_v1` and calibration contracts remain W3H work;
W3G does not export a placeholder or imply model-specific calibration.

The explicit V1 convention is x right, vertical displacement/load up, nodal
rotation/couple counterclockwise, sagging-positive internal moment and shear
`dM/dx`. `E` in N/mm2 and `I` in mm4 become `EI` in kN.m2 using `1e-9`.
Only unloaded horizontal rigid end arms are supported; member UDL/point loads
and explicit density/area/gravity self-weight act on the flexible length.
Perfect end hinges have independent rotations; disconnected nodal rotation is
NOT_APPLICABLE, never a measured zero. Vertical supports are fixed/free at zero
settlement; rotational supports are fixed/free or an explicitly evidenced
nonnegative spring. No vertical spring, settlement or load on a rigid arm is
implemented. Negative reactions retain uplift and do not certify contact.

Consistent loads, diagonal-scaled Cholesky and exact piecewise station
integration are checked against simply supported UDL/point closed forms,
cantilever/fixed/continuous beams, spring compatibility, releases and offsets.
Point-load stations retain both sides of shear jumps. Signed ordered nested
linear combinations preserve the full request; overflow blocks, never truncates.
Numerical residual limits are at most `1e-8` of applied-load norm plus explicit
force/moment floors. These are numerical tolerances, not W3H engineering criteria.
No ETABS force mapping, calibration, torsion derivation, optimizer or professional
approval follows. See `../verification/etabs-w3g-beam-line-evidence.json`.

### W3H — Model-specific calibration (`L5`)

Owner: Mac comparison implementation; Windows supplies accepted W3D/W3F
reference evidence. Dependencies: W3D, W3F and W3G. Indicative effort: 10-20
focused days plus bounded Windows extraction.

Bind exact model/baseline/catalogue/topology/scenario/station digests and
predeclared action/displacement/reaction tolerances. Missing mappings are
`NOT_COMPARABLE`; any declared component outside tolerance is `OUT_OF_BAND`.
Calibration invalidates on any relevant model, load, support, stiffness,
definition, selection, analysis-setting, ETABS-version or file-digest change.

The owner-resumed Windows campaign now has a bounded W3H **L1 software
comparison checkpoint**, not completed L5 calibration. The exact planned
`compare_beam_line_to_reference_v1(request, /)` signature is implemented with
immutable `core/beam_line_calibration.py` contracts and a pure service, exported
through `structural_lib`. It consumes independently normalized, hash-bound
reference rows and caller-reviewed mappings/criteria; it does not extract or
certify them. Every retained action row, declared component and requested joint
domain must reconcile. Same-plane axes, signs, station sides/origins, distinct
file/model hashes and explicit local-to-reference scenario IDs are preserved.
Missing evidence is `NOT_COMPARABLE` with no partial comparison. See
[the comparison guide](../guides/beam-line-calibration.md) and
[software receipt](../verification/etabs-w3h-comparison-evidence.json).

`CALIBRATED` from this pure function means only scoped numerical agreement with
supplied tolerances; independent acceptance of model assumptions, mappings,
reference completeness and predeclared engineering criteria remains required
for L5. Existing capability stays `HELD_NOT_SUPPORTED` and `SURROGATE_ONLY`.
The current project lacks that complete input basis. The owner-reported saved
copy is a new revision, while an existing backup still matches the accepted
old model bytes. Neither is altered or promoted by this software checkpoint.
Do not begin W3I until the separate model-specific W3H acceptance passes.

### W3I — Scenario/family candidate screening (`L5`)

Owner: Mac. Dependencies: W3E, W3H and W3R. Indicative effort: 15-30 focused
days.

Generate bounded engineer-editable families, couple candidate `E/I` and
self-weight to every mandatory scenario, run strength/serviceability/
constructability checks, reject every unsafe or held mandatory outcome, and
return deterministic robust/Pareto shortlists. A target benchmark of 100
sections over five spans and five scenarios in two seconds may guide
implementation, but performance never relaxes engineering checks. Every result
remains `SCREENED_ONLY` pending W3K.

### W3J — Excel review and professional dossier (`L4`, optionally `L7` later)

Owner: Mac contracts/transport tests; Windows installed Excel evidence;
qualified reviewer/signature provider remains external. Dependencies: W3D for
catalogue/demand review, W3E for calculations, and the separate professional
contracts in the companion audit. Indicative effort: 10-20 Mac days plus 3-7
Windows evidence days; provider/jurisdiction work is separately estimated.

Project formula-free, controlled tables for identity, patterns, cases,
combination definitions/factors, selection/status, scenarios, governing rows,
held checks, comments/revisions and dossier/signature verification. Preserve
lossless detail through bounded pages and canonical JSON, typed literal cells,
all-table preflight/transaction/rollback, installed readback and exact hash
rejoin. Excel never becomes the structural calculator or private-key store.

The completion-audit successor implements the four exact provider-neutral
dossier signatures in `services/calculation_dossier.py`, with immutable types
in `core/calculation_dossier.py` and root exports. It binds source Git/library/
ETABS identities, model/catalogue/demand/calculation/report hashes and explicit
five-state workbook/surrogate/calibration/optimization/governing identities.
Review scope, append-only attestation history and the separately signed
attested artifact are hash-bound. Unknown provider trust remains UNAVAILABLE;
verification reports supplied evidence separately and never produces
`SIGNED_VERIFIED` in this provider-neutral packet. This is an L1 prerequisite,
not installed Excel, a signed professional dossier or W3J completion.

The R4 implementation adds an offline saved-dossier route, Python-owned
catalogue/demand replay, sixteen controlled review tables, canonical JSON
transport, separate user comments, hash-bound append-only revision history,
all-table preflight/snapshot/typed publication/readback/rollback, and a
post-verification commit marker. Its software fixture is explicitly fictional;
installed Excel acceptance remains a separate exact-source continuation. The
first attempt from #923 stopped at host-control activation, before workbook or
table operations; this is not evidence of an Office.js writer defect or an L4
pass. The existing certificate/catalog and all model/evidence files were kept.
`scripts/export_calculation_review.py` is the maintained carrier entry point;
see `excel_addin/README.md`. No new model extraction or ETABS state change is
needed to review existing saved evidence. This does not clear W3H/I/K/L.

The installed successor now supplies publication, comment/history persistence
and one native update-only rollback after PENDING verification. It uses the
existing hash-provider parameter without changing writer code. Complete
before/after typed state and unchanged saved bytes reconcile independently;
see the native rollback receipt above. Evidence remains fictional software
acceptance, not a supplied professional signature or calibrated building dossier.

### W3K — Controlled candidate ETABS reanalysis (`L6`)

Owner: Mac freezes/reviews the mutation and comparison contract; Windows alone
executes a separately authorized installed packet. Dependencies: accepted W3I,
explicit owner authorization, allowlisted recoverable copy and approved
analysis cases. Indicative effort: 20-40 focused days plus installed evidence.

Apply one candidate plan to a fresh approved baseline copy, run only approved
cases, capture fresh result/catalogue/model identities, and compare affected
beams, columns, joints, reactions, displacements/drifts and other predeclared
whole-model safeguards. Unexpected dialogs, stale results, model drift,
analysis failure, out-of-scope effects or restore/save mismatch reject the
candidate. The chosen final candidate is independently repeated from the clean
baseline. No local shortlist can bypass this mandatory ETABS reanalysis.

### W3L — Bounded iteration and review

Owner: Mac orchestration plus Windows W3K evidence cycles. Dependency: accepted
W3K. Use a finite evaluation budget, deterministic stop rules and cache keys
bound to baseline/scenario/candidate digests. Budget exhaustion is explicit;
there is no infinite overnight loop or silent “best available” acceptance.

## Work sizing and critical path

The packet estimates above are planning ranges for one experienced developer,
not delivery promises. W3A-W3D form the first contract/evidence milestone.
W3E and W3F can be planned after W3D, but W3G depends on accepted topology/load
contracts, W3H depends on both the solver and installed reference evidence, and
W3I depends on the separate Pareto repair. W3K is the first packet allowed to
produce a freshly ETABS-reanalysed candidate, and only under new authority.

A dependable public beam-line screening programme remains a multi-month effort.
A general 2D/3D building FEM engine is a separate, much larger programme and is
not required to reduce ETABS trips.

## Expected time saving

The target operating pattern is:

1. one baseline ETABS extraction;
2. many local candidate and assumption runs;
3. a bounded ETABS shortlist verification;
4. at most a small number of correction cycles; and
5. one independent final ETABS run.

No trip-reduction percentage or force-accuracy percentage may be claimed until
W3H benchmarks representative models. The main success metrics are fewer ETABS
analysis cycles, zero unsafe screened recommendations, explicit held checks,
stable candidate ranking, and improving model-specific prediction error.

## Verification matrix

| Boundary | Required evidence |
|---|---|
| Data identity | Canonical hashes, exact units, source/runtime identity, no partial accepted snapshot |
| Case/combo semantics | Complete typed inventory, constituents/factors, nested references, finished/selected status |
| Demand concurrency | Exact same-row references; independent extrema labelled as such |
| Solver math | Closed-form, equilibrium, symmetry, singularity and deterministic serialization tests |
| Beam checks | Flexure, shear, torsion/service holds, service scenario and detailing evidence |
| Optimization | Feasibility before ranking, deterministic objectives, held-check ledger, bounded budget |
| Model/calibration inputs | Releases, offsets, modifiers, supports, assigned loads, displacement/reaction identities and explicit missing states |
| Calibration | Predeclared tolerances, exact reference mapping, invalidation on model drift |
| ETABS iteration | Authorized copy, expected-state guards, analysis success, fresh results, restore/save proof |
| Whole-model review | Affected beams, columns, reactions, drifts and other explicitly governed metrics |

## Stop conditions

Stop and request direction when:

- the exact integrated W3-readiness predecessor no longer matches PR #899 merge
  `7af545ec0e239bac8fa6d480ecbb2b05a60aa40d` and tree
  `cc40650b7f6569227c880d61a9967ee3bbdfab31` before W3A branches;
- an accepted packet's exact merge/tree or hash-linked predecessor cannot be
  verified before its successor begins;
- the authorized model file, hash, ETABS version or result definitions change;
- analysis results are stale, incomplete, inactive or not traceable;
- a required getter/setter is outside the reviewed matrix;
- a catalogue has missing/nested-cycle definitions or a selected case is not
  finished under its exact observed analysis status;
- an envelope would call cross-row components concurrent or drop signed
  same-row provenance;
- a calculation-bearing optional value would require a hidden default;
- a local scenario requires an unsupported 3D/nonlinear behavior;
- an optimizer cannot prove all declared feasibility checks;
- a future ETABS mutation cannot guarantee an allowlisted copy and recovery;
- an unexpected ETABS/license/abnormal-condition dialog appears; or
- software, signature or installed evidence is being represented as broader
  engineering, professional or construction approval.

## Current continuation

Do not restart accepted W3A-G work or request plan acceptance again. Follow the
owner-approved three-track validation continuation above and the exact current
[session brief](next-session-brief.md). The two-span EB-compatible benchmark
now passes 112 comparisons after one installed analysis; saved-building
baseline/catalogue/foundation regression also passes. See the
[successor receipt](../verification/etabs-w3h-two-span-evidence.json).

Follow the completion audit above: retain the bounded W3J review/rollback
acceptance and address only the precise missing building mapping/criteria
needed for W3H. Do not schedule another benchmark-only
packet unless its result can resolve a declared acceptance row. Keep data
transport, design checks and independent analysis distinct. Do not repeat the
passed installed benchmarks, reopen building recovery, unlock W3I prematurely
or claim model-specific calibration. No broad FEM, release or professional
approval follows from a software checkpoint.
