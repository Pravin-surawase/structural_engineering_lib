---
owner: Main Agent
status: active
last_updated: 2026-09-01
doc_type: spec
complexity: advanced
tags: [beam, etabs, w3, api, safety, optimization, execution]
---

# W3 and professional beam integrated execution plan

## Decision

Continue W3 from merged PR #941 only after separating three different owners:

1. **public beam safety and semantics** — effective-depth truth, supplied-beam
   check truth, REST/WebSocket parity and executable examples;
2. **ETABS host and state safety** — PID selection, live-session identity,
   session-versus-file freshness, guarded state restoration and raw call records;
3. **candidate engineering feasibility** — signed row-bound actions, exact bar
   layers, supplied-reinforcement checks, serviceability, detailing, quantities,
   applicability and one common verdict for direct, cost and Pareto routes.

Use one writer and one implementation packet at a time. Read-only reviewers may
run in parallel, but overlapping code, task, session, generated-reference or
handoff writers may not. The urgent public beam safety packet goes first; the
offline W3 PID/state packet follows from the exact accepted head. Use one
dedicated Windows worktree as the primary writer for the whole implementation
sequence so packet boundaries do not also become device handoffs. No ETABS,
COM, Excel, export, solver, analysis/design, save, unlock or model mutation is
authorized merely by this plan.

## Current authority and users

- `origin/main` was fetched and observed at merged PR #941 commit
  `5aad93b8f3dc5e6f9ca916350bf0276c51ad683d`.
- The [W3 COM/VBA/reanalysis plan](etabs-w3-com-vba-and-reanalysis-plan.md)
  remains the ETABS host, transaction and reanalysis owner.
- The [professional API renewal plan](lib-pro-015-professional-api-and-documentation-renewal-plan.md)
  remains the public facade, signature, example and documentation owner.
- The [whole-W3 foundation](etabs-data-analysis-optimization-foundation-plan.md)
  remains the accepted A-L capability/evidence sequence.
- Sourcebook and StructProof remain independent example/evidence inputs. They do
  not become runtime dependencies, approval authorities or automatic validation.

Primary users are library/API consumers, W3 audit and screening services,
Windows ETABS evidence operators, and qualified reviewers. The goal is one
truthful beam result path from explicit input through calculation, supplied-bar
evaluation, detailing, screening and later copied-model reanalysis.

## Device decision

Implement the next sequence on the Windows host because it is the only device
that can later produce installed ETABS/COM/SQLite and desktop Excel evidence.
Keep one Windows writer through `BEAM-S0`, `W3-A0`, installed `W3-A1`, and the
offline `W3-B0/B1/B2` code packets instead of alternating devices.

- During `BEAM-S0`, `W3-A0` and other offline packets, keep ETABS and Excel
  closed and prove zero application calls. Their acceptance remains ordinary
  repository code/tests, not installed-software evidence.
- Open or attach to ETABS only in a separately authorized installed packet.
  `W3-A1` is read-only against the exact selected PID/model. `W3-K/L` later use
  an agent-owned ETABS process and a hash-bound copied model; neither may mutate
  the user's attached session or original model.
- Excel is an optional evidence/review projection. It is not the beam
  calculation, feasibility or optimization owner.
- Create the Windows worktree from the exact accepted predecessor and keep it
  bound to its own branch/interpreter. Transfer source only through GitHub.
- Use Mac only for bounded read-only milestone review or final integration when
  useful. It is not an alternating implementation lane, so normal progress does
  not require changing devices after every packet.

At every new packet, still refresh Git and verify the Windows repository,
interpreter, ETABS version and model/workbook identity appropriate to that
packet. A persistent device does not mean a persistent unverified application
session.

## Confirmed issues added by this audit

| ID | Priority | Confirmed outcome problem | Root cause | Disposition |
|---|---|---|---|---|
| `BEAM-DEPTH-001` | P0 | The promoted compatibility design/detail path derives `d = D - clear_cover`. For the maintained 500/40/8/20 mm example this gives 460 mm instead of 442 mm and understates required steel by 5.44%. | Clear cover was reused as a complete centroid-depth basis. | `BEAM-S0`: require explicit `d_mm` or complete clear-cover/stirrup/main-bar basis; retain a fail-closed compatibility wrapper. |
| `BEAM-CHECK-002` | P0 | `/api/v1/design/beam/check` returns byte-identical adequacy results when supplied effective depth changes from 300 to 450 mm, `Asc` from 0 to 1500 mm2 and stirrup spacing from 300 to 50 mm. | The request advertises supplied-beam checking, but the handler ignores those fields and calls a required-design report with hidden depth/compression-depth assumptions. | `BEAM-S0`: consume a typed supplied-reinforcement evaluation or narrow the compatibility contract to explicit demand screening with `HOLD`; do not emit a false adequacy verdict. |
| `BEAM-WS-003` | P0 | WebSocket `check_beam` derives `d = D - cover - 8` without stirrup/main-bar inputs and emits a compliance result without supplied reinforcement. | A transport-specific shortcut became an engineering assumption and the route name overstates its boundary. | `BEAM-S0`: share the REST/canonical request owner and status semantics; incomplete supplied basis must hold. |
| `W3-FACE-004` | P0 | The legacy live pilot converts governing M3 to magnitude and omits `primary_tension_face`; top-face demand can be detailed as bottom-face demand. | The pilot owns a second beam calculation path outside the signed W3 audit. | `W3-B0`: preserve the old entry only as a delegating compatibility adapter to the row-bound canonical W3 audit. |
| `W3-FEAS-005` | P0 | Bar, cost and Pareto routes can disagree on whether the same candidate is feasible. | They use separate flexure/shear/quantity logic; exact layer centroid, spacing, anchorage, serviceability, torsion and applicability are not owned by one evaluator. | `W3-B1/B2`: one candidate definition/evaluator, then migrate every ranking adapter. Missing mandatory evidence is `HOLD`, never a pass. |
| `ETABS-FRESH-006` | P0 | An on-disk EDB hash cannot prove that an already-open ETABS session has no unsaved in-memory changes. | The proposed target contract combines persistent file identity and live-session identity without a freshness/cleanliness discriminator. | `W3-A0`: add `ETABSModelFreshnessV1`; unknown or unsaved session state cannot become hash-bound baseline evidence. |
| `PLAN-STATE-007` | P1 | The task row, next-session brief and the foundation plan's final continuation still contain pre-merge or pre-serviceability/detailing instructions. | Chronological status owners were not all advanced when PRs #937-#941 closed later packets. | Reconcile these maintained entry surfaces in this planning candidate; immutable evidence remains unchanged. |

These findings change promoted beam-check outcomes or the future ETABS target,
candidate and reanalysis outcome. Cosmetic documentation and unrelated feature
ideas remain outside this plan.

## Dependency graph

```text
PLAN-0 current authority and execution freeze
  |
  +--> BEAM-S0 public depth/check truth
  |      |
  |      +--> BEAM-D0/D1 exact-wheel examples and professional facade docs
  |
  +--> W3-A0 offline PID/identity/freshness/state/call-ledger contracts
         |
         +--> W3-A1 separately authorized installed read-only acceptance
         |
         +--> W3-B0 canonical signed-face pilot convergence
                |
                +--> W3-B1 common candidate evaluator
                       |
                       +--> W3-B2 optimizer/cost/quantity convergence
                              |
                              +--> W3-C matched design/named SQLite evidence
                                     |
                                     +--> actual-building W3H decision
                                            |
                                            +--> W3I -> W3K -> W3L
```

`BEAM-S0` and `W3-A0` do not share production files, but they both touch
session/task/reference surfaces. They are therefore sequenced rather than
implemented by parallel writers. `W3-A0` does not wait for facade documentation.
`W3-B1` may reuse the existing supplied-reinforcement service before its public
facade projection, but it may not duplicate that service's calculations.

## Packet register

| Order | Task ID | Work | Hard dependency | Measurable exit | Effort |
|---:|---|---|---|---|---:|
| 0 | `W3-BEAM-INTEGRATED-PLAN` | This authority/finding/dependency freeze | PR #941 | Plan, task and continuation owners agree at exact Git head; docs/quick/hooks pass | current packet |
| 1 | `LIB-BEAM-S0-CHECK-TRUTH` | Effective-depth safety plus truthful REST/WebSocket supplied-beam checking | accepted plan | No hidden depth; changing consumed supplied inputs changes the check, or unsupported inputs yield explicit `HOLD`; canonical valid outcomes unchanged | 2-4 focused days |
| 2 | `ETABS-W3-A0-OFFLINE-SESSION-GUARD` | Offline PID candidates, two-phase target confirmation, model freshness, state guard and call record contracts/fakes | accepted `LIB-BEAM-S0` head for single-writer order only | Multiple-session ambiguity fails; clean/unknown/drift freshness states are distinct; pre/post state is equal after success and injected failures; zero COM/application calls | 3-5 focused days |
| 3 | `ETABS-W3-A1-INSTALLED-READONLY-ACCEPTANCE` | Prove PID attachment and state preservation on the exact Windows/ETABS authority | accepted A0 plus separate user authorization | Exact selected PID/model shown; user session remains read-only; units, lock, cases/combos, statuses and file identity unchanged; unknown in-memory freshness does not become saved-baseline proof | one bounded evidence session |
| 4 | `ETABS-W3-B0-CANONICAL-PILOT` | Deprecate live-pilot calculation ownership and delegate to signed row-bound W3 audit | A0; installed run not required | Positive/negative M3 preserve physical face; missing face provenance holds; compatibility result declares delegation/limitations | 2-4 focused days |
| 5 | `ETABS-W3-B1-CANDIDATE-EVALUATOR` | Freeze exact signed-action, row-bound, layer-aware candidate request/result and one feasibility owner | BEAM-S0 and B0 | Row/source identity and physical TOP/BOTTOM face are preserved; required/supplied strength, layer geometry, serviceability, torsion, detailing, quantities and applicability are accepted or visibly held; direct evaluation is deterministic | 4-7 focused days |
| 6 | `LIB-PRO-015-D0-D1-BEAM` | Exact-wheel documentation gate and complete beam facade reference/examples | BEAM-S0 semantic freeze | Valid/invalid/FAIL/HOLD examples execute from built wheel; signatures, units, defaults, errors, limitations and provenance match runtime | 4-7 focused days |
| 7 | `ETABS-W3-B2-OPTIMIZER-CONVERGENCE` | Route bar, cost and Pareto generation through B1; version cost/quantity basis | B1 | Same candidate has one verdict in direct/cost/Pareto routes; only accepted candidates rank; transverse/side-face/lap/anchorage quantities and exclusions are explicit | 4-7 focused days |
| 8 | `ETABS-W3-C-DESIGN-AND-NAMED-DATA` | Matched ETABS concrete-design snapshot and allowlisted SQLite importer | A1 for installed calls; offline importer may start after A0 | Every field/table closes a named comparison row or is rejected; no broad table-COM retry | 3-6 focused days plus evidence session |
| 9 | `ETABS-W3-H-I-K-L` | Physical comparability, screening, owned-copy reanalysis and bounded iteration | Existing whole-W3 gates plus A-C | Explicit W3H acceptance/no-go, then `SCREENED_ONLY`, then authorized copied-model ETABS evidence; professional approval remains separate | re-estimate after H |

The current rectangular/single-layer W3 scope does not require canonical
curtailment, continuous deep beams, full direct/long-term deflection, flanged
torsion, wider/multilayer torsion or full IS 13920 capacity design. Keep those
held unless the selected project/candidate scope proves they are mandatory.

## Packet 1 — beam safety contract

### Required implementation

1. Remove every public derivation that treats clear cover as `D - d`.
2. Preserve the existing compatibility function names, but require either
   explicit effective depth or a complete typed centroid basis.
3. Decide the existing REST `/beam/check` compatibility boundary explicitly:
   consume all supported supplied fields through the supplied-reinforcement
   evaluator, or return `HOLD` for fields outside its proved scope. Do not keep
   accepted-but-ignored engineering fields.
4. Give WebSocket `check_beam` the same request/result semantics as REST, or
   rename/project it as limited demand screening without an adequacy claim.
5. Repair the README, cookbook, manual API snippets and executable REST payloads
   only after runtime semantics freeze.

### Focused acceptance

- the 500/40/8/20 mm depth basis resolves to 442 mm;
- omission of both explicit depth and complete basis fails before calculation;
- effective depth, supplied compression steel and stirrup spacing are either
  consumed and affect the relevant result or produce a typed hold;
- REST and WebSocket agree on intake, engineering and limitation states;
- top/bottom signed-face, torsion/detailing and BBS regressions stay unchanged.

## Packet 2 — offline ETABS target and state guard

### Two-phase target handshake

1. `discover_etabs_processes_v1()` returns deterministic OS-level PID,
   executable/version/start-time candidates without creating COM.
2. The operator selects a candidate PID plus expected version/path intent.
3. A separately invoked identity probe reads the visible model/path/version and
   returns a session-bound observation. It does not yet prove saved-file parity.
4. `classify_etabs_model_freshness_v1()` distinguishes:
   `SAVED_CLEAN_CONFIRMED`, `SESSION_UNSAVED_OR_UNKNOWN`, `FILE_DRIFT` and
   `FILE_UNAVAILABLE` with evidence/limitation fields.
   Every attached session defaults to `SESSION_UNSAVED_OR_UNKNOWN`.
   `SAVED_CLEAN_CONFIRMED` requires A1 evidence from either a reviewed installed
   API cleanliness signal or an explicit operator-saved checkpoint whose
   PID/path/hash/mtime and observation timing are bound and after which no edit
   is permitted before the identity observation.
5. Only that evidenced saved checkpoint may build a hash-bound baseline/copy
   contract. An unknown open session remains usable for bounded read-only
   observation but not as persistent baseline truth.

### State and failure behavior

- capture only the operation's declared mutable global state, including units,
  output case/combo selections and any run flags/table selections it may touch;
- restore in `finally`, verify exact equality and retain both predecessor and
  postflight states;
- inject capture, operation, decode, restore and verification failures;
- if restoration cannot be verified, return a blocking disposition and require
  operator verification before any later attached-session operation;
- record raw method/signature/arguments/shape/status before strict decoding;
  bind redaction, storage identity and call ordering to a transaction ID.

Offline A0 acceptance uses fakes only. Installed PID attachment is A1 and needs
separate authorization; A0 passing is not installed-software evidence.

## Packets 4-7 — calculation and optimizer convergence

- The live-pilot adapter consumes the same signed station/action identity as
  `beam_audit.py`; it never applies `abs(M3)` as the physical-face decision.
- `BeamCandidateDefinitionV2` carries the signed `BeamActionsV1` or equivalent
  row-bound source identity, `primary_tension_face`, exact longitudinal layers,
  transverse and side-face reinforcement, effective-depth identity, service
  scenarios, applicability and versioned objective/cost inputs.
- `evaluate_beam_candidate_v2` composes maintained canonical design,
  supplied-reinforcement, serviceability and detailing owners. It does not copy
  IS 456 equations into an optimizer or COM adapter.
- Candidate generators may be incomplete recommendations. Only the evaluator
  emits feasibility, and missing mandatory layers/evidence yield `HOLD`.
- Mirrored TOP/BOTTOM rows must retain the same logical capacity/utilization
  while mapping primary/opposite steel to the correct physical faces through
  direct, cost and Pareto projections.
- Run the documentation/signature vertical slice after these public semantics
  freeze; do not document a route whose accepted fields are ignored.

## Efficient verification and Git sequence

For each packet, finish implementation, tests, documentation and task/session
evidence before the normal consolidated checks:

1. affected focused tests and independent arithmetic/evidence checks;
2. architecture/import/API-client checks for changed public surfaces;
3. `./run.sh check --quick` once after content freeze;
4. normal commit hooks and required hosted checks;
5. broad Python/FastAPI/React gate once after the B1/B2 milestone, unless an
   outcome-changing earlier failure proves repository-wide impact.

Create every successor from the exact accepted predecessor. Before publishing,
inspect active candidate worktrees and shared/generated paths. Do not stack two
unmerged writers on `docs/SESSION_LOG.md`, `docs/TASKS.md`, generated API/OpenAPI
artifacts or next-session handoff owners.

## Stop conditions

Stop the active packet when:

- Git authority is behind, diverged, conflicted, dirty in an unknown path or the
  required predecessor cannot be proved;
- a public beam check would need an ignored field or hidden effective-depth,
  reinforcement, service or applicability default;
- a target PID/model does not resolve exactly, session freshness is unknown but
  hash-bound baseline evidence is requested, or state restoration is unproved;
- a live action is requested before A0 acceptance and separate installed
  authorization;
- the candidate evaluator cannot prove every mandatory check for the declared
  scope;
- named saved/getter/SQLite evidence cannot resolve the W3H physical question;
- a local solver extension is proposed merely to replace missing evidence;
- software, installed ETABS behavior, a screened candidate or copied-model run
  is being represented as professional or construction approval.

## Exact next action

After this plan is accepted, start only
`LIB-BEAM-S0-CHECK-TRUTH` on the Windows host from the plan's exact merge
commit. Keep ETABS and Excel closed. Do not start W3-A0 in the same task. When
BEAM-S0 is accepted, create the next exact task/branch in the same dedicated
Windows repository lane for `ETABS-W3-A0-OFFLINE-SESSION-GUARD`; that packet
remains offline and fake-adapter-only.
