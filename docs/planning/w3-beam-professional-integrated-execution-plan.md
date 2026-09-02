---
owner: Main Agent
status: active
last_updated: 2026-09-02
doc_type: spec
complexity: advanced
tags: [beam, etabs, w3, api, safety, optimization, execution]
---

# W3 and professional beam integrated execution plan

## Decision

Continue W3 from accepted preflight PR #944 while separating three different owners:

1. **public beam safety and semantics** — effective-depth truth, supplied-beam
   check truth, REST/WebSocket parity and executable examples;
2. **ETABS host and state safety** — PID selection, live-session identity,
   session-versus-file freshness, getter-only state capture/compare and raw call
   records;
3. **candidate engineering feasibility** — signed row-bound actions, exact bar
   layers, supplied-reinforcement checks, serviceability, detailing, quantities,
   applicability and one common verdict for direct, cost and Pareto routes.

Use one writer and one milestone branch at a time. Read-only reviewers may run
in parallel, but overlapping code, task, session, generated-reference or
handoff writers may not. Sequential task IDs inside one milestone are internal
implementation units, not automatic branch/PR boundaries. A small live-route
gate goes first, then related units are grouped by common authority and safety
boundary. Use one dedicated Windows repository lane for the whole sequence so
milestone boundaries do not also become device handoffs. No ETABS,
COM, Excel, export, solver, analysis/design, save, unlock or model mutation is
authorized merely by this plan.

The 2026-09-01 long-term amendment adds the controls that were still narrative
rather than executable after PR #942: a getter-only attached-session boundary,
supervised STA COM execution and an OS-wide process lease, measured runtime and
result epochs, dedicated live-route authorization, one project criteria and
candidate-catalogue identity, complete-search semantics, a mutation dry run,
crash recovery and an explicit surrogate-versus-ETABS-first route decision.
These are extensions of the existing packets, not permission to open ETABS or
to replace missing project evidence with more solver complexity.

## Current authority and users

- PR #943 accepted this amended plan at merge commit
  `3b0d689dabddae7891758648b09acf9beef088ee`. The bounded G0 maintenance
  preflight fetched `origin/main`, verified that exact authority, and started an
  equal, clean Windows worktree from it. G0 must start from the exact accepted
  successor of that preflight rather than from the older PR #942 planning head.
- PR #946 accepted the public beam S0 plus beam-only D0/D1 milestone at merge
  `f2a5c6f158647a1d09fb4ff54f158d1734440fba`, with candidate/merge tree
  `d96a58edb53b853aa6447cb8b43404023945a822`. The offline-foundations branch
  starts from that exact merge. Its pre-A0 audit repaired transverse-grade
  propagation and React result-boundary validation without opening ETABS or
  Excel.
- PR #947 accepted the fake-only A0/B0/B1A/C0 foundation at merge
  `16be0db796dc85f0462a3a49a5990dc0232ef0b4`. PR #949 then accepted the
  reduced three-hook commit lane at `e6c684a580803a27cea9fc6e8cd25b0888795a2`.
  PR #950 accepted the B1B/B2 evaluator/search milestone at merge
  `742719dd3f6c1e30c023e7585e9ea00d13b60fc2`. No installed application
  evidence was part of either offline milestone.
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

### G0 maintenance preflight

The 2026-09-01 bounded preflight found the Python, pinned Node/npm, normal hook,
focused FastAPI/WebSocket, OpenAPI snapshot and checked-in client controls ready
without a runtime-code repair. It restored only the ignored lockfile-bound
`node_modules` tree in the fresh worktree; no dependency version changed. Two
older dirty worktrees are behind `origin/main`, have no commit ahead of main and
have no active repository process or Git operation; preserve their unknown
local changes and rebind/reconcile them before any future use.

The same preflight observed an already-running ETABS process and did not attach
to, close or inspect its model. Therefore G0 implementation remains on `HOLD`
until ETABS and Excel are closed and their absence is reverified. This is an
environmental start gate, not permission to perform any application operation.

## Device decision

Implement the next sequence on the Windows host because it is the only device
that can later produce installed ETABS/COM/SQLite and desktop Excel evidence.
Keep one Windows writer through `ETABS-LIVE-G0`, `BEAM-S0`, `W3-A0`, installed `W3-A1`, and the
offline `W3-B0/B1/B2` code packets instead of alternating devices.

- During `ETABS-LIVE-G0`, `BEAM-S0`, `W3-A0` and other offline packets, keep ETABS and Excel
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

At every new milestone, and again immediately before any installed internal
unit, refresh Git and verify the Windows repository, interpreter, ETABS version
and model/workbook identity appropriate to that work. A persistent device does
not mean a persistent unverified application session.

## Reduced-PR milestone map

The owner decision on 2026-09-01 replaces one-PR-per-task-ID execution with the
following seven publishable milestones. The detailed packet register below
remains the acceptance checklist and dependency truth; rows grouped into one
milestone are implemented sequentially on one branch and are not independently
pushed or reviewed.

| Milestone branch | Sequential internal units | Publication boundary |
|---|---|---|
| `codex/etabs-live-g0-route-gate` | `ETABS-LIVE-G0-ROUTE-GATE` plus this cadence amendment | urgent disabled-by-default live-route boundary; one PR |
| `codex/w3-public-beam-truth` | `LIB-BEAM-S0-CHECK-TRUTH`, `LIB-PRO-015-D0-D1-BEAM` | one public beam/API/OpenAPI/client/documentation candidate |
| `codex/w3-offline-etabs-foundations` | `ETABS-W3-A0-OFFLINE-SESSION-GUARD`, `ETABS-W3-B0-CANONICAL-PILOT`, `ETABS-W3-B1A-PROJECT-CRITERIA-CATALOGUE`, `ETABS-W3-C0-OFFLINE-ACQUISITION-CONTRACT` | one dependency-ordered offline fake/contract candidate; zero application calls |
| `codex/w3-installed-readonly-evidence` | `ETABS-W3-A1-INSTALLED-READONLY-ACCEPTANCE`, `ETABS-W3-C1-INSTALLED-DESIGN-EXPORT-INVENTORY` | one separately authorized installed read-only evidence session/PR |
| `codex/w3-offline-candidate-evaluator-search` | `ETABS-W3-B1B-CANDIDATE-EVALUATOR`, `ETABS-W3-B2-OPTIMIZER-CONVERGENCE` | one offline evaluator/search candidate; multiple commits, one PR |
| `codex/w3-offline-exact-schema-parser` | `ETABS-W3-C2-OFFLINE-EXACT-SCHEMA-PARSER` | one later offline parser candidate, created only from accepted C1 schema evidence |
| `codex/w3-screening-transaction-kernel` | `ETABS-W3-H0-ROUTE-DECISION`, `ETABS-W3-I-SCREENING`, `ETABS-W3-K0-OFFLINE-TRANSACTION-KERNEL` | one offline route/screen/dry-run candidate |
| `codex/w3-owned-copy-iteration` | `ETABS-W3-K1-INSTALLED-OWNED-COPY`, `ETABS-W3-L-BOUNDED-ITERATION` | one separately authorized installed mutation milestone and terminal evidence PR |

Do not create a planning-only PR between these milestones. Update this plan,
task/session evidence and the affected implementation on the active milestone
branch, then publish them together. A milestone must split only when an internal
unit discovers an outcome-changing dependency break, an accepted predecessor is
required by an installed run, or authorization/rollback scope changes.

The B1B/B2 implementation reached exactly that split condition for C2: C0
deliberately freezes only a generic export contract and makes no ETABS SQLite
schema claim, while C2 requires C1's actual accepted table/column inventory.
Inventing an allowlist before C1 would invalidate the parser's main outcome.
Therefore the candidate-data milestone is narrowed to B1B/B2, C2 remains held,
and the separately authorized A1/C1 evidence PR must precede its later offline
implementation. This is a dependency correction, not a return to one PR per
task.

## Confirmed issues added by this audit

| ID | Priority | Confirmed outcome problem | Root cause | Disposition |
|---|---|---|---|---|
| `BEAM-DEPTH-001` | P0 | The promoted compatibility design/detail path derives `d = D - clear_cover`. For the maintained 500/40/8/20 mm example this gives 460 mm instead of 442 mm and understates required steel by 5.44%. | Clear cover was reused as a complete centroid-depth basis. | `BEAM-S0`: require explicit `d_mm` or complete clear-cover/stirrup/main-bar basis; retain a fail-closed compatibility wrapper. |
| `BEAM-CHECK-002` | P0 | `/api/v1/design/beam/check` returns byte-identical adequacy results when supplied effective depth changes from 300 to 450 mm, `Asc` from 0 to 1500 mm2 and stirrup spacing from 300 to 50 mm. | The request advertises supplied-beam checking, but the handler ignores those fields and calls a required-design report with hidden depth/compression-depth assumptions. | `BEAM-S0`: consume a typed supplied-reinforcement evaluation or narrow the compatibility contract to explicit demand screening with `HOLD`; do not emit a false adequacy verdict. |
| `BEAM-WS-003` | P0 | WebSocket `check_beam` derives `d = D - cover - 8` without stirrup/main-bar inputs and emits a compliance result without supplied reinforcement. | A transport-specific shortcut became an engineering assumption and the route name overstates its boundary. | `BEAM-S0`: share the REST/canonical request owner and status semantics; incomplete supplied basis must hold. |
| `W3-FACE-004` | P0 | The legacy live pilot converts governing M3 to magnitude and omits `primary_tension_face`; top-face demand can be detailed as bottom-face demand. | The pilot owns a second beam calculation path outside the signed W3 audit. | `W3-B0`: preserve the old entry only as a delegating compatibility adapter to the row-bound canonical W3 audit. |
| `W3-FEAS-005` | P0 | Bar, cost and Pareto routes can disagree on whether the same candidate is feasible. | They use separate flexure/shear/quantity logic; exact layer centroid, spacing, anchorage, serviceability, torsion and applicability are not owned by one evaluator. | `W3-B1/B2`: one candidate definition/evaluator, then migrate every ranking adapter. Missing mandatory evidence is `HOLD`, never a pass. |
| `ETABS-FRESH-006` | P0 | An on-disk EDB hash cannot prove that an already-open ETABS session has no unsaved in-memory changes. | The proposed target contract combines persistent file identity and live-session identity without a freshness/cleanliness discriminator. | `W3-A0`: add `ETABSModelFreshnessV1`; unknown or unsaved session state cannot become hash-bound baseline evidence. |
| `PLAN-STATE-007` | P1 | The task row and next-session brief still describe PR #942's planning candidate as unmerged and the shared session timer retained an unmatched PR #941 predecessor. | The immutable candidate was merged without advancing every chronological owner and without a terminal shared usage checkpoint. | This amendment marks PR #942 accepted, supersedes the exact stale timer through the maintained command and refreshes the handoff without rewriting historical evidence. |
| `ETABS-ATTACHED-008` | P0 | A path described as read-only can still call `SetPresentUnits` or result-selection setters and briefly change the user's attached session. | State restoration was treated as equivalent to no mutation. | `W3-A0/A1`: attached access is getter-only. Normalize from observed units; if the required selection is not already active, return `HOLD`. Capture-and-compare replaces restore-on-exit for attached sessions. |
| `ETABS-EXEC-009` | P0 | The current Python `Lock` does not serialize another API worker process, CLI or Excel-launched bridge, and a hung COM call can hold it indefinitely. | Execution safety stops at one Python process and has no supervised COM deadline. | `W3-A0`: one dedicated STA broker process, OS-wide lease keyed by PID plus process start time, heartbeat/deadline and fenced recovery. Never terminate an attached ETABS process. |
| `ETABS-IDENTITY-010` | P0 | PID reuse, ETABS restart or installed binding drift can replace the process/runtime between discovery and execution. | Process start time and installed type-library/wrapper identities do not flow through every target and request. | `W3-A0/A1`: bind `ETABSProcessInstanceV1`, `ETABSRuntimeFingerprintV1` and a short-lived target observation to every live operation. |
| `ETABS-API-011` | P0 | The router is labelled localhost while maintained startup examples bind `0.0.0.0`, development auth defaults off and WebSocket auth accepts a missing token. | Optional global API auth and planning prose are not an executable ETABS operation authority. | `ETABS-LIVE-G0`, then A0: disable/unmount live routes by default, refuse non-loopback or unauthenticated live startup and require a server-issued short-lived capability bound to process, model, access and transaction. Mutation uses a separate single-use capability. |
| `ETABS-EPOCH-012` | P0 | A clean file, locked model or finished case status does not prove extracted analysis/design results belong to the current model/change set. | “Fresh result identity” is named but has no executable epoch contract. | `W3-A0/C/K`: add `ETABSResultEpochV1`; reconnect, timeout, unexpected run flags or pre-existing results cannot create fresh evidence. |
| `W3-CRITERIA-013` | P0 | Direct, cost, Pareto, surrogate and reanalysis evidence can use different project assumptions while each appears internally valid. | `project_criteria` is an unversioned parameter with no declaration chronology or digest. | `W3-B1A`: freeze `ProjectBeamCriteriaV1` and `ProjectBeamCandidateCatalogueV1`; every candidate, cache, shortlist, H decision and K/L receipt binds both digests. |
| `W3-APPLICATION-014` | P0 | W3I can rank an arbitrary section that the first `SetSection` transaction cannot apply, or a column change with no column-candidate engineering owner. | Candidate generation and mutation transport have different scopes. | First W3K accepts only verified existing beam properties with empty/explicitly supported auto-select state. New property definitions and column mutations remain separate held extensions. Columns/joints are safeguards only. |
| `W3-SEARCH-015` | P0 | A deterministic but truncated enumeration can be labelled optimal or Pareto-complete even when traversal order omitted better candidates. | Finite budget and deterministic ordering do not state search completeness. | `W3-B2`: record domain/traversal/pruning/counts; only complete enumeration or proved-safe pruning may claim optimal/Pareto. Budget truncation is provisional and cannot close W3I. |
| `ETABS-RECOVERY-016` | P1 | A crash between setter, readback, analysis, save and ledger persistence can leave an owned copy and process at an unknown stage. | Desired rollback is documented, but restart behavior and non-replay rules are not. | `W3-K0`: durable stage-before-call journal, read-only dry run, stable object-set digest and recovery that verifies or quarantines without replaying a non-idempotent call. |
| `ETABS-DESIGN-017` | P1 | ETABS and library steel results can be compared under different combinations, material values, auto-select resolution or overwrite-default meaning. | The design snapshot does not yet bind every comparison-bearing basis field or result epoch. | `W3-C0/C1/C2`: freeze the basis contract, acquire it in one uninterrupted result/design epoch, then compare offline. |
| `ETABS-SQLITE-018` | P1 | An allowlisted parser can still consume a changing, partial or version-drifted SQLite export. | Export acquisition, actual schema inventory and offline parsing are not separated or manifest-bound. | `W3-C0/C1/C2`: generic contract first, create-new installed export/schema inventory second, exact-schema read-only parser/comparison third; no pending WAL; enforce integrity/schema/table/field/row bounds. |
| `W3-ROUTE-019` | P0 | Actual-building H is currently not comparable, while I implicitly waits for accepted H and baseline calibration would not validate changed candidate stiffness. | The plan has no explicit surrogate-assisted versus ETABS-first decision. | `W3-H0`: choose a proved applicability envelope, an ETABS-first baseline-action screening route, or terminal `HOLD`; do not extend the solver merely to fill missing physical inputs. |

These findings change promoted beam-check outcomes or the future ETABS target,
candidate and reanalysis outcome. Cosmetic documentation and unrelated feature
ideas remain outside this plan.

## Dependency graph

```text
PLAN-1 long-term authority and execution freeze
  |
  +--> ETABS-LIVE-G0 disabled-by-default route/auth gate
  |      |
  |      +--> BEAM-S0 public depth/check truth
  |      |
  |      +--> BEAM-D0/D1 exact-wheel examples and professional facade docs
  |
  +--> W3-A0 offline target/runtime/lease/broker/freshness/state/call contracts
         |
         +--> W3-A1 separately authorized installed getter-only acceptance
         |
         +--> W3-B0 canonical signed-face pilot convergence
                |
                +--> W3-B1A project criteria and candidate catalogue
                       |
                       +--> W3-B1B common candidate evaluator
                              |
                              +--> W3-B2 complete-search optimizer convergence

  W3-A0 --> W3-C0 offline acquisition/design contracts and generic fixtures
  W3-A1 + W3-C0 --> W3-C1 installed design/export/schema inventory
  W3-C1 --> W3-C2 exact-schema offline parser and matched comparison

  W3-B2 + W3-C2 + accepted project criteria/catalogue instance
      --> W3-H0 route decision --> W3-I screening
      --> W3-K0 offline transaction/recovery kernel
      --> W3-K1 installed owned-copy reanalysis --> W3-L bounded iteration
```

`ETABS-LIVE-G0` is intentionally first because the current router can expose a
live surface before later target/session controls exist. `BEAM-S0` and `W3-A0`
do not share production files, but they both touch
session/task/reference surfaces. They are therefore sequenced rather than
implemented by parallel writers. `W3-A0` does not wait for facade documentation.
`W3-B1B` may reuse the existing supplied-reinforcement service before its public
facade projection, but it may not duplicate that service's calculations. B1A
can freeze the schema with authored fixtures while the actual-building criteria
instance remains held; H0/I cannot proceed until that instance is complete and
declared before candidate inspection.

## Packet register

| Order | Task ID | Work | Hard dependency | Measurable exit | Effort |
|---:|---|---|---|---|---:|
| 0 | `W3-BEAM-INTEGRATED-PLAN` | Initial authority/finding/dependency freeze | PR #941 | Accepted through PR #942 at `35ea6b89`; plan exists at exact merged head | complete |
| 0A | `W3-BEAM-LONG-TERM-PLAN-AMENDMENT` | Close runtime, criteria, search, acquisition, recovery and route gaps found after merge | accepted PR #942 | Accepted through PR #943 at `3b0d689d`; plans, tasks, continuation and evidence owners agree; no application call | complete |
| 1 | `ETABS-LIVE-G0-ROUTE-GATE` | Disable live routes by default; enforce loopback bind, HTTP/WebSocket authentication and operation classification before any COM import/attach | accepted PR #943 plus bounded preflight | Disabled/denied requests prove zero COM creation or attachment; missing WebSocket token is rejected before accept; OpenAPI security and startup checks match runtime | accepted through PR #945 |
| 2 | `LIB-BEAM-S0-CHECK-TRUTH` | Effective-depth safety plus truthful, versioned REST/WebSocket supplied-beam checking | accepted G0 | No hidden depth or ignored field; one terminal status vocabulary; REST/WebSocket/OpenAPI/client and compatibility ledger agree | accepted through PR #946; successor audit repairs included here |
| 3 | `ETABS-W3-A0-OFFLINE-SESSION-GUARD` | Offline process-instance/target/runtime fingerprint, getter-only attached policy, live-route capability, OS lease, supervised STA broker, freshness/result-epoch/state/call contracts and fakes | accepted `LIB-BEAM-S0` head for single-writer order only | PID reuse/runtime drift/second process/hung call fail deterministically; attached path invokes no setter; uncertain restoration fences reuse; durable ledger verifies; zero COM/application calls | accepted through PR #947 |
| 4 | `ETABS-W3-A1-INSTALLED-READONLY-ACCEPTANCE` | Prove exact getter-only attachment on the Windows/ETABS authority | accepted A0 plus separate user authorization | Process instance, target observation, runtime fingerprint and model shown; no setter; pre/post state/file equal; unknown model/result freshness cannot become baseline/comparison proof | active; offline transport accepted locally, live HOLD because no ETABS process/model is running |
| 5 | `ETABS-W3-B0-CANONICAL-PILOT` | Deprecate live-pilot calculation ownership and delegate to signed row-bound W3 audit | A0; installed run not required | Positive/negative M3 preserve physical face; missing face provenance holds; compatibility result declares delegation/limitations | accepted through PR #947 |
| 6 | `ETABS-W3-B1A-PROJECT-CRITERIA-CATALOGUE` | Freeze criteria, permitted existing ETABS beam properties, materials/bar stock, reinforcement schedule scope, scenarios, objectives and digests | BEAM-S0, B0 and accepted W3A demand contracts | Strict canonical hashes and declaration chronology; no hidden fallback; any change invalidates downstream identities; actual instance may remain `HOLD` | accepted through PR #947 |
| 7 | `ETABS-W3-B1B-CANDIDATE-EVALUATOR` | Freeze exact signed-action, row-bound, layer-aware candidate request/result and one feasibility owner | B1A | Effective depth is recomputed from serialized layers; every mandatory row/scenario/check is accepted or held; independent composition checks pass | accepted through PR #950 |
| 8 | `LIB-PRO-015-D0-D1-BEAM` | Exact-wheel documentation gate and complete beam facade reference/examples | BEAM-S0 semantic freeze | Valid/invalid/FAIL/HOLD examples execute from built wheel; signatures, units, defaults, errors, limitations and provenance match runtime | 4-7 focused days |
| 9 | `ETABS-W3-B2-OPTIMIZER-CONVERGENCE` | Route bar, cost and Pareto through B1B; freeze complete search and quantity/cost basis | B1B | One evaluation hash across routes; complete domain/counts/tie-breaks; incomplete search cannot claim optimum/Pareto/infeasible; exact serialized schedule owns quantities | accepted through PR #950 |
| 10 | `ETABS-W3-C0-OFFLINE-ACQUISITION-CONTRACT` | Freeze matched-design and export-manifest contracts plus generic bounded fixture/scaffolding; make no ETABS schema-support claim | A0 | Synthetic generic fixtures prove contract, limits and zero ETABS/UI call; exact ETABS tables/columns remain unresolved | accepted through PR #947 |
| 11 | `ETABS-W3-C1-INSTALLED-DESIGN-EXPORT-INVENTORY` | Acquire one target/runtime/epoch-bound design snapshot, named export manifest and actual SQLite schema inventory | A1 and C0 plus separate authorization | Every requested field/table closes a named row or is rejected; acquisition mode explicit; artifact complete/hash-bound; state/file preservation passes | active; offline inventory accepted locally, installed design/export evidence held with A1 |
| 12 | `ETABS-W3-C2-OFFLINE-EXACT-SCHEMA-PARSER` | Implement the parser and matched comparison against the acquired exact schema | accepted C1 artifact | Frozen export passes integrity/schema/row bounds; canonical evidence and diagnostic comparison are reproducible; no ETABS/UI call | held pending separately authorized A1/C1 evidence |
| 13 | `ETABS-W3-H0-ROUTE-DECISION` | Select `SURROGATE_ASSISTED`, `ETABS_FIRST` or terminal `HOLD` | B2, C2 and accepted project criteria/catalogue instance | Surrogate envelope covers the candidate domain, or ETABS-first admits only mutation-ready baseline-action proposals; baseline calibration is not candidate-range validity | 1-2 days for ETABS-first decision; separately cost a surrogate campaign |
| 14 | `ETABS-W3-I-SCREENING` | Complete deterministic screening under the H0 route | B2 and H0 | No held mandatory check; explicit screening mode; `SCREENED_ONLY`; no changed-model feasibility claim | 5-10 focused days |
| 15 | `ETABS-W3-K0-OFFLINE-TRANSACTION-KERNEL` | Dry-run change set, object/copy identities, durable stage journal, result epoch, recovery and failure injection | A0 and accepted W3I | No non-idempotent replay; crash/timeout states verify or quarantine; only existing beam properties allowed; no COM/application call | 5-8 focused days |
| 16 | `ETABS-W3-K1-INSTALLED-OWNED-COPY` | Apply one exact candidate in an owned ETABS process and rebuild fresh demand/evaluation | K0 plus separate authorization | Original and attached session unchanged; exact readback/result epoch/global safeguards; deterministic terminal disposition | 7-12 focused days plus ETABS run/review time |
| 17 | `ETABS-W3-L-BOUNDED-ITERATION` | Budgeted clean-copy iteration and independent final repeat | accepted K transaction machinery plus one complete K1 attempt | Exact run/retry/correction budgets; accepted-and-repeated candidate or explicit no-solution/budget/external/safety terminal outcome | 4-8 focused days plus candidate cycles |

The current rectangular/single-layer W3 scope does not require canonical
curtailment, continuous deep beams, full direct/long-term deflection, flanged
torsion, wider/multilayer torsion or full IS 13920 capacity design. Keep those
held unless the selected project/candidate scope proves they are mandatory.

## Packet 1 — live-route gate

`ETABS-LIVE-G0-ROUTE-GATE` is a small security and side-effect boundary that
lands before any other public API work:

1. classify each ETABS operation as `OFFLINE`, `LIVE_READ` or `LIVE_MUTATION`;
2. do not register live routes unless `ETABS_LIVE_BRIDGE_ENABLED=true`, refuse
   live startup on a non-loopback bind and keep mutation separately disabled;
3. require non-default server authentication and operation scope for HTTP, and
   authenticate WebSocket requests before accepting the connection;
4. create `ETABSLiveRoutePolicyV1`, owned by server configuration. A request
   cannot set an `authorized=true` field or otherwise grant itself live access;
5. reject disabled, remote, missing/invalid-token and wrong-scope requests before
   importing a COM binding, constructing a session or calling attach;
6. keep `/status` nonattaching and safe. Publish the gate and HTTP/WebSocket
   security requirements in the actual OpenAPI/runtime documentation.

A0 later adds the exact PID/model/runtime-bound short-lived capability and OS
lease. G0 does not claim safe attachment; it removes the current route-exposure
gap and proves rejected traffic has zero COM side effects.

## Packet 2 — beam safety contract

### Required implementation

1. Remove every public derivation that treats clear cover as `D - d`.
2. Preserve the existing compatibility function names, but require either
   explicit effective depth or a complete typed centroid basis.
3. Introduce exact versioned `BeamSuppliedCheckRequestV2` and
   `BeamSuppliedCheckResultV2` owners. Decide the existing REST `/beam/check`
   compatibility boundary explicitly:
   consume all supported supplied fields through the supplied-reinforcement
   evaluator, or return `HOLD` for fields outside its proved scope. Do not keep
   accepted-but-ignored engineering fields.
4. Give WebSocket `check_beam` the same request/result semantics as REST, or
   rename/project it as limited demand screening without an adequacy claim.
5. Freeze one versioned REST/WebSocket result envelope and terminal outcome
   vocabulary: `PASS`, `FAIL`, `HOLD` and
   `ERROR`. Streaming may emit progress, but it cannot emit `PASS` before one
   final result. Carry request/correlation identity through REST and WebSocket.
6. Publish a field-by-field V1 migration table. Every accepted field is marked
   `CONSUMED`, `REJECTED` or `DEPRECATED`; no field silently disappears. Preserve
   the existing operation/path identity through a typed adapter or publish an
   explicit migration. A legacy Boolean must never map `HOLD` to adequate.
7. Reject an incompatible legacy payload before calculation or route it through
   an explicit compatibility adapter with a limitation/deprecation result.
   Regenerate and review the live OpenAPI, Python/TypeScript clients, React
   caller, versioned WebSocket machine schema and compatibility ledger in the
   same candidate. A manual fallback client passes only when the touched
   operation proves exact request/result parity.
8. Add a release-parity assertion across package/runtime build, OpenAPI
   `info.version`, root/health metadata and maintained clients. Do not let an
   OpenAPI structural comparator silently ignore the advertised version.
9. Repair the README, cookbook, manual API snippets and executable REST payloads
   only after runtime semantics freeze.

### Focused acceptance

- the 500/40/8/20 mm depth basis resolves to 442 mm;
- omission of both explicit depth and complete basis fails before calculation;
- effective depth, supplied compression steel and stirrup spacing are either
  consumed and affect the relevant result or produce a typed hold;
- REST and WebSocket agree on the V2 schema version, intake, correlation, terminal
  engineering status and limitations; no partial message overstates success;
- generated OpenAPI/client/React artifacts, WebSocket schema, compatibility
  evidence and advertised versions match the exact runtime candidate;
- top/bottom signed-face, torsion/detailing and BBS regressions stay unchanged.

## Packet 3 — offline ETABS runtime and session guard

### Two-phase target handshake

1. `discover_etabs_processes_v1()` returns deterministic
   `ETABSProcessInstanceV1` values: PID, process start time, canonical
   executable path, executable version/hash, architecture, observation time and
   instance digest, without creating COM.
2. The operator selects one process instance plus expected model/version/path
   intent. `build_etabs_runtime_fingerprint_v1()` binds the bridge/library,
   Python executable/version/architecture, COM-shape runtime, `comtypes`, ETABS
   executable, registered ETABSv1 type library, generated wrapper/managed
   assembly where used and installed CHM identities.
3. A separately invoked identity probe creates a short-lived
   `ETABSTargetObservationV1` with process instance, visible model/path/version,
   runtime fingerprint, observation/expiry times and allowed access. Revalidate
   all fields immediately before and after every live operation; PID alone is
   never reusable authority.
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
6. `ETABSResultEpochV1` separately binds result evidence to model/copy,
   transaction/change set, uninterrupted process/runtime, authorized cases and
   run flags, pre/post statuses, analysis/design call evidence, selection and
   result digest. A clean file or `FINISHED` status alone is not result freshness.

### Live-route and execution boundary

- default `ETABS_LIVE_BRIDGE_ENABLED=false` and
  `ETABS_MUTATION_ENABLED=false`; do not register/serve live operations unless
  explicitly enabled, and refuse live-bridge startup on a non-loopback bind;
- pure retained-evidence calculations remain separate from live COM routes;
  optional global JWT/CORS settings do not grant ETABS authority;
- every attach/read/export request carries a short-lived capability bound to
  process instance, target observation, model intent, access and transaction;
  mutation later requires a separate single-use capability;
- acquire an OS-wide `ETABSOperationLeaseV1` keyed by PID plus process start
  time. One API worker, CLI or Excel-launched bridge cannot overlap another;
- perform COM only in a supervised worker process whose apartment is
  initialized, used and uninitialized on one dedicated STA thread. The parent
  retains the lease, heartbeat, deadline and durable call-stage journal;
- on deadline expiry, terminate only the broker. Never terminate an attached
  ETABS process. Fence that process instance as `RESTORATION_UNVERIFIED`; an
  owned transaction becomes `TRANSACTION_UNCERTAIN` and enters recovery.

### State and failure behavior

- `ATTACHED_OBSERVE` is getter-only, including no `SetPresentUnits`, output-
  selection setter, run flag, unlock, save, analysis/design or exit call. Read
  the current units and normalize offline. If a required result is not already
  selected and finished, return `HOLD` instead of changing the user's session;
- attached observation captures and compares declared state before/after. It
  does not use restoration setters. Any drift or incomplete postflight fences
  the process instance for operator verification;
- owned-copy operations capture only their declared mutable state, persist the
  next stage before each non-idempotent call, restore in `finally` where safe,
  and verify exact equality/declared successor state;
- write a bounded `STARTED` record before invocation and `RETURNED` raw
  method/signature/arguments/shape/status record before strict decoding. Use an
  exclusive append-only ledger with monotonic sequence, previous-record hash and
  durable flush at both boundaries. Bind redaction, storage and transaction
  identities; a timeout retains the unmatched `STARTED` record;
- finalize successful evidence through an atomic `ETABSEvidenceBundleV1`
  manifest that binds the ledger head, call count, target/runtime/model/result
  identities and retained artifacts. Its verifier rejects gaps, truncation,
  hash-chain mismatch, missing files and unfinalized transactions. Proprietary
  raw evidence stays in the approved local store; Git receives only reviewed
  safe projections, digests, counts and retention metadata;
- inject target drift, lease contention/loss, broker hang, capture, operation,
  decode, restore, verification and journal failures. No automatic reconnect or
  replay may repeat a setter, analysis, design, save or exit call.

Offline A0 acceptance uses fakes only. Installed PID attachment is A1 and needs
separate authorization; A0 passing is not installed-software evidence.

## Packets 5-9 — criteria, calculation and optimizer convergence

- `ProjectBeamCriteriaV1` binds code/source identities, complete strength and
  service action/scenario domains, signed-face and P/V3/M2 applicability,
  torsion/excluded-effect dispositions, mandatory serviceability, detailing,
  anchorage/lap/support/aggregate/constructability scope, deterministic
  sensitivity scenarios, objectives, tie-breaks, stop policy, declaration time
  and `criteria_sha256`. It must be declared before candidate inspection.
- `ProjectBeamCandidateCatalogueV1` binds permitted existing ETABS beam
  property IDs and digests, resolved dimensions/materials/modifiers/rebar type,
  separate longitudinal/transverse grades, bar/stirrup availability and
  revision, cost basis/exclusions and `catalogue_sha256`.
- `BeamMemberReinforcementScheduleV1` first supports explicit full-span
  TOP/BOTTOM single-layer groups plus exact transverse-zone intervals. Every
  retained strength/service/detailing/quantity row maps to the same schedule
  revision. Curtailment, mixed diameters and wider/multilayer torsion remain
  held until typed separately.
- The live-pilot adapter consumes the same signed station/action identity as
  `beam_audit.py`; it never applies `abs(M3)` as the physical-face decision.
- `BeamCandidateDefinitionV2` carries the signed `BeamActionsV1` or equivalent
  row-bound source identity, `primary_tension_face`, exact longitudinal layers,
  transverse and side-face reinforcement, effective-depth identity, service
  scenarios, applicability, mutation-ready existing property identity and the
  criteria/catalogue/schedule digests.
- `evaluate_beam_candidate_v2` composes maintained canonical design,
  supplied-reinforcement, serviceability and detailing owners. It does not copy
  IS 456 equations into an optimizer or COM adapter. It recomputes effective
  depth from the serialized layer centroid and reruns strength; a nominal depth
  that disagrees with the chosen bars cannot survive as candidate truth.
- Candidate generators may be incomplete recommendations. Only the evaluator
  emits feasibility, and missing mandatory layers/evidence yield `HOLD`.
- Mirrored TOP/BOTTOM rows must retain the same logical capacity/utilization
  while mapping primary/opposite steel to the correct physical faces through
  direct, cost and Pareto projections.
- `OptimizationSearchBudgetV1` records canonical domain digest, deterministic
  traversal, permitted pruning rules, tie-breaks and generated/pruned/evaluated/
  accepted/ranked counts. Wall-clock time never governs engineering membership
  or canonical hashes. Terminal search states are `COMPLETE_ENUMERATION`,
  `BUDGET_EXHAUSTED_INCOMPLETE`, `NO_FEASIBLE_CANDIDATE` and
  `BLOCKED_MANDATORY_CHECK`.
- Only complete enumeration or pruning with a recorded correctness proof may
  claim optimality or a Pareto front. A truncated nondominated set is a
  provisional shortlist and cannot satisfy W3I.
- An independent composition checker, which does not call the evaluator or
  optimizer, recomputes longitudinal area/layer centroid, clear spacing,
  transverse/longitudinal mass, zone quantities/cost and face mirroring from
  the serialized candidate. Direct, cost and Pareto projections of one identity
  must have byte-identical evaluation hashes and verdicts.
- Run the documentation/signature vertical slice after these public semantics
  freeze; do not document a route whose accepted fields are ignored.

An actual-building criteria/catalogue instance may remain `HOLD` while B1A/B1B
software is built with authored fixtures. W3H0/I/K/L cannot use those fixtures
as project evidence. Changing either digest invalidates evaluations, caches,
shortlists, route decisions and reanalysis receipts.

## Packets 10-12 — matched design and named SQLite evidence

Split generic contract/scaffolding, installed acquisition/schema inventory and
exact-schema parsing into three packets. C0 cannot claim support for an ETABS
SQLite schema it has not observed. C1 is the one installed session that creates
and freezes the actual artifact. C2 then implements and verifies the parser
offline against that accepted schema:

- `ETABSConcreteDesignBasisV1` binds code/build, exact design-combination set,
  preferences, explicit/default overwrite semantics, object design procedure,
  resolved assigned section and auto-select state, section rebar definition,
  concrete and longitudinal/transverse rebar material values, item type,
  warnings and `ETABSResultEpochV1`;
- `ETABSSQLiteExportManifestV1` binds acquisition mode, target/runtime/model/
  result epoch, requested table keys/fields, filter/selection state, create-new
  destination, start/end/completion evidence, bytes/hash and pre/post state;
- acquisition is `OPERATOR_UI_EXPORT` unless an exact installed API signature
  is separately proved. Current product availability does not by itself prove
  an OAPI export method;
- C0 defines bounded generic fixtures, limits and the manifest/design contracts;
- C1 records the actual tables, columns, declared types, row/key/null patterns
  and version/build identity without interpreting them as accepted canonical
  values;
- C2 implements `parse_etabs_sqlite_export_v1()` for that exact accepted schema
  and ingests a completed ETABS export into
  canonical evidence offline. It never imports or updates data in ETABS;
- copy/freeze and hash the completed export before parsing. Reject a pending
  WAL/SHM or changing source. Open the frozen copy with SQLite `mode=ro` and a
  private cache, disable extension loading/attachment and arbitrary SQL, run an
  integrity check and enforce file/table/field/type/row/null/key/duplicate and
  schema/version bounds. Use `immutable=1` only after verified immutability;
- every requested field must close one named W3 comparison row or be rejected.
  Do not reopen the broad table-COM route.

The ETABS design comparison remains diagnostic. It cannot become approval and
cannot compare steel areas until every comparison-bearing basis and result
epoch matches.

## Packet 13 — actual-building route decision

`W3-H0-ROUTE-DECISION` has only three outcomes:

1. `SURROGATE_ASSISTED`: `SurrogateApplicabilityEnvelopeV1` binds exact members,
   scenarios/components, physical reduction, support/load/slab assumptions,
   E/I, self-weight and support-stiffness ranges, deterministic alternatives,
   validation points and invalidation rules. Every W3I candidate lies inside it.
2. `ETABS_FIRST`: preferred when the retained building's physical reduction is
   still unproved. Generate only criteria-complete, mutation-ready proposals
   from exact baseline actions, label them `SCREENED_ONLY` with
   `screening_mode=BASELINE_ACTION_ETABS_FIRST`, and establish changed-model
   feasibility only through clean-copy W3K reanalysis plus the common evaluator.
3. `HOLD`: neither route has complete inputs or authority. Stop without fitting
   supports/loads after seeing results or adding a general solver.

No new solver physics is scheduled. A future extension is considered only for
one named unsupported behavior with complete independent inputs, immutable
applicability, independent reference cases, equilibrium/convergence acceptance
and a demonstrated benefit over bounded copied-model ETABS evaluation. The
existing W3G Euler-Bernoulli solver remains `SURROGATE_ONLY`.

## Packets 15-17 — owned-copy transaction and bounded iteration

- `plan_etabs_change_set_v1()` is getter-only and produces a reviewable dry-run
  digest before any setter. `ETABSObjectIdentityV1` binds source unique name,
  label/story, endpoints/geometry, current/resolved section, auto-select state,
  design procedure/type and a proved vendor GUID only when available.
- The first programme assigns only verified existing beam properties. It does
  not create/modify section definitions and does not mutate columns. Columns,
  joints, reactions, displacements/drifts and other declared objects are
  whole-model safeguards. A future column or section-definition programme needs
  separate candidate engineering, mutation operations and acceptance.
- Build every candidate from the same clean baseline into a new non-existing
  local NTFS directory outside OneDrive/cloud sync. Verify disk capacity,
  baseline pre/post identity and copied bytes before opening. Never overwrite
  the baseline or reuse a failed copy.
- `ETABSTransactionJournalV1` persists transaction and next intended stage
  before each non-idempotent call. Startup recovery may verify an already
  completed stage or quarantine/close the exact owned process/copy; it cannot
  replay a setter, `RunAnalysis`, design, save or exit call.
- Run flags include the complete dependency closure for every result and design
  comparison. After the first setter, accept results only from the exact
  uninterrupted `ETABSResultEpochV1`; reconnect, pre-existing finished status,
  timeout or broker restart quarantines the copy.
- W3L freezes maximum candidate attempts, ETABS analyses, correction cycles,
  stage retries and final repeats before the first run. Failed/aborted runs
  consume budget; retry uses a fresh copy and a changed reviewed cause.
- Terminal iteration outcomes are `ACCEPTED_AND_REPEATED`,
  `NO_FEASIBLE_CANDIDATE`, `BUDGET_EXHAUSTED`,
  `BLOCKED_EXTERNAL_EVIDENCE` and `ABORTED_SAFETY`. “Best available” is never a
  substitute for accepted and independently repeated.
- Cache keys bind baseline, demand, result epoch, criteria, catalogue,
  candidate, route and analysis-setting digests.

The offline K0 packet proves target drift, crash and failure injection without
COM. K1 and every later installed run remain separately authorized.

## Decision milestones and remaining effort

These are focused engineering-work ranges, not calendar promises. Installed
runtime, project evidence, review and hosted CI can dominate elapsed time.

| Milestone | Remaining focused work from the amended plan | External/runtime dependency |
|---|---:|---|
| Closed live-route exposure plus truthful public beam check | 4-7 days | normal review/CI only; ETABS closed |
| First safe installed getter-only A1 | another 8-12 days plus one evidence session | exact Windows/ETABS target and separate installed authorization |
| Criteria/evaluator/search and offline C0 ready | another 20-35 days | actual project criteria instance may still be held |
| Installed C1, offline C2 and H0 route decision | another 7-12 days plus one evidence session | named export/design evidence and accepted criteria/catalogue instance |
| Complete W3I screening | another 5-10 days | accepted H0 route; no mandatory hold |
| K0/K1/L copied-model programme | another 16-28 days plus ETABS cycles | separate mutation authorization, owned process/copies and review time |

The ranges intentionally include the controls added by this amendment. Reuse
accepted evidence and implementation when an exit is already satisfied; do not
create a packet merely to consume its range. Re-estimate at A1, H0 and the first
complete K1 attempt because those are the highest-information decision points.

W3 is complete only when all intended packet implementations are merged at
exact accepted commits, the project criteria/catalogue instance has no mandatory
hold, H0 selects a supported route, W3I reports a complete deterministic
shortlist, K1 rebuilds fresh whole-model evidence on an owned clean copy, W3L
independently repeats the accepted candidate or records a truthful terminal
no-solution/budget/block outcome, and the final dossier reconciles every digest.
That remains software and evidence completion; professional approval and release
authorization are separate.

## Efficient verification and Git sequence

For each milestone, finish all sequential internal units, tests, documentation
and task/session evidence before the normal consolidated checks. During an
internal unit, run only its affected focused tests or a narrow reproducer needed
to guide a repair; do not run quick, hooks, push, PR or hosted CI at that
checkpoint.

Use coherent sequential Git commits for internal implementation units so review
and recovery retain their logical boundaries. Each ordinary commit runs only
the three accepted mutation-safety hooks; do not run broad validation, push, or
open a PR for each unit. Freeze the complete milestone after all units converge,
then run the union of affected focused evidence, push the commits together once,
and use one PR validation cycle for the safety boundary.

After the complete milestone content freezes, run exactly one publication
sequence:

1. the union of affected focused tests and independent arithmetic/evidence checks;
2. architecture/import/API-client checks for all changed public surfaces;
3. `./run.sh check --quick` once;
4. normal commit hooks once, one push, one PR and one required hosted cycle;
5. the broad Python/FastAPI/React gate once after the candidate/data-convergence
   milestone, unless an
   outcome-changing earlier failure proves repository-wide impact.

Create every successor from the exact accepted predecessor. Before publishing,
inspect active candidate worktrees and shared/generated paths. Do not stack two
unmerged writers on `docs/SESSION_LOG.md`, `docs/TASKS.md`, generated API/OpenAPI
artifacts or next-session handoff owners.

### Commit-gate follow-up

The offline A0/B0/B1A/C0 milestone is accepted through PR #947. Its measured
34-hook, 11-unconditional commit lane is superseded by the separate
[commit and PR validation consolidation plan](commit-pr-validation-consolidation-plan.md).
That maintenance packet adds complete hosted parity before reducing ordinary
commits to three mutation-safety hooks. Formatting, linting, typing, security,
tests and governance move to one batched PR; the live resolved-merge operation
guard remains local because a hosted checkout cannot observe the developer's
Git operation state. The maintenance packet remains separate from A1/C1
installed evidence.

## Stop conditions

Stop the active packet when:

- Git authority is behind, diverged, conflicted, dirty in an unknown path or the
  required predecessor cannot be proved;
- a public beam check would need an ignored field or hidden effective-depth,
  reinforcement, service or applicability default;
- a target PID/model does not resolve exactly, session freshness is unknown but
  hash-bound baseline evidence is requested, runtime/result epoch drifts, an
  attached operation needs a setter, or postflight is unproved;
- the live bridge is exposed beyond loopback, lacks an exact capability/lease,
  or a broker timeout/process restart is being treated as safe to retry;
- a live action is requested before A0 acceptance and separate installed
  authorization;
- project criteria/catalogue is absent, changed, declared after candidate
  inspection, or fails its digest; authored fixtures are being used as project
  evidence;
- a candidate omits a mandatory action/scenario/reinforcement zone/material/bar
  or verified existing ETABS property mapping, or the evaluator cannot prove
  every mandatory check;
- a search is incomplete but represented as optimal, Pareto-complete or proof
  of infeasibility;
- named saved/getter/SQLite evidence cannot resolve the W3H physical question;
- a SQLite source is changing, has a pending WAL/SHM, fails integrity/schema
  bounds or lacks a target/runtime/result-epoch export manifest;
- neither H0 route is accepted, a surrogate candidate lies outside its envelope,
  or a local solver extension is proposed merely to replace missing evidence;
- a W3K proposal needs a new ETABS property or column mutation, cannot preserve
  an exact existing beam-property mapping, or would reuse/replay a failed copy;
- a run/retry budget is exhausted or a result lacks an uninterrupted fresh
  epoch and same criteria/catalogue identity;
- software, installed ETABS behavior, a screened candidate or copied-model run
  is being represented as professional or construction approval.

## Exact next action

A0/B0/B1A/C0 is accepted through PR #947 and B1B/B2 through PR #950. The next
branch is `codex/w3-installed-readonly-evidence` for A1 plus C1. The owner's
2026-09-02 instruction to start the next work authorizes only this bounded
getter-only installed observation and create-new operator-UI export milestone;
it does not authorize setters, save, unlock, analysis/design, application exit,
model mutation, Excel automation, or changes to the original model.

Refresh Git, installed runtime and running-process identity immediately before
each installed step. Require one operator-selected PID plus start time and exact
model intent. If that process/model is absent or ambiguous, stop at `HOLD`
without constructing COM. C1 acquisition remains `OPERATOR_UI_EXPORT` unless a
separate exact installed API signature is proved. C2 remains held until C1
freezes an accepted complete hash-bound export and exact schema inventory.

## Long-term amendment sources

- Installed `docs/reference/CSI API ETABS v1.chm`, SHA-256
  `a730756ccd283ffc17f592a2e21c973d50b5a14ed3489244fca1524e58f3a700`, and
  the retained installed-signature evidence remain authoritative for exact
  ETABS method shapes.
- [CSI ETABS enhancements](https://www.csiamerica.com/products/etabs/enhancements)
  and [CSI OAPI FAQ](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2000456/OAPI%2BFAQ)
  support product capability/concept review; they do not replace the installed
  CHM or prove an unobserved export method.
- [Microsoft COM apartment guidance](https://learn.microsoft.com/en-us/windows/win32/com/processes--threads--and-apartments)
  and [COM call cancellation limits](https://learn.microsoft.com/en-us/windows/win32/com/canceling-method-calls)
  support a dedicated STA broker and the rule that cancellation does not prove
  the ETABS server stopped processing.
- [SQLite URI filename guidance](https://www.sqlite.org/uri.html) supports
  `mode=ro`/private-cache parsing and warns that `immutable=1` is safe only when
  the file truly cannot change.
