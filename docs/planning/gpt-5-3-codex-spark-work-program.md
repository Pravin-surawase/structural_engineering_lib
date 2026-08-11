---
owner: Main Agent and repository owner
status: draft
created: 2026-08-11
last_updated: 2026-08-11
doc_type: spec
task: SPARK-001
title: GPT-5.3-Codex-Spark Work Program
branch: codex/gpt-5-3-spark-work-program
baseline_commit: a0e115e17009cc14b3d883e3c291d47c32f7ca4e
model: gpt-5.3-codex-spark
implementation_authorized: false
max_concurrent_workers: 2
---

# SPARK-001 — GPT-5.3-Codex-Spark Work Program

## 1. Executive decision

Use GPT-5.3-Codex-Spark as a high-throughput implementation lane for small,
explicit, rapidly verifiable tasks. The program targets truthful documentation,
automation contracts, API examples and schemas, runnable examples, bounded React
product polish, and deterministic verification work.

Spark is not the engineering authority for IS 456 calculations, public supported-
case expansion, security architecture, cross-worktree conflict resolution, or
release and professional-use approval. It may collect evidence for those areas,
but a stronger model, the main orchestrator, and when required a qualified
structural engineer must accept the result.

The initial branch is:

```text
codex/gpt-5-3-spark-work-program
```

This branch currently owns planning and program-control changes only. All
implementation packets remain paused until the repository owner reviews and
accepts this plan. After acceptance, work proceeds in dependency order with a
reviewable checkpoint at the end of every wave. The program must never become a
single unreviewable bulk rewrite.

## 2. Authority, status, and relationship to other work

This plan is the proposed execution authority for SPARK-001. It does not override:

1. `AGENTS.md` and its architecture, Git, session, and root-cause requirements;
2. `docs/guidelines/ai-token-efficiency.md`;
3. `docs/TASKS.md` as the active-task truth source;
4. `Python/structural_lib/services/capabilities.py` for supported and held cases;
5. existing task-specific plans for active element, UI, Excel, or workflow lanes;
6. qualified structural-engineering review requirements.

The owner-selected planning packet is active. Implementation authorization is
`false` until the owner reviews this document. Acceptance of the plan authorizes
only the first approved wave, not every later wave automatically.

### Phase 2 recovery record

The repository owner explicitly authorized dirty-lane recovery and Phase 1 gap
closure on 2026-08-11. That recovery preserved the inherited control-plane draft
at `47fce48e`, merged current `origin/main` without rewriting history, completed
the missing S0-02 picker behavior and real CLI regression, and verified the
integrated repository. This records what now exists; it is not G0 acceptance and
does not authorize Wave 1 or later implementation.

## 3. Verified model facts and planning assumptions

The program uses only facts currently stated by OpenAI:

| Property | Verified fact | Program consequence |
|---|---|---|
| Product status | Research preview | Treat availability, rate limits, and pricing as changeable |
| Intended mode | Real-time interactive coding | Prefer short feedback loops and bounded edits |
| Model size | Smaller GPT-5.3-Codex variant | Do not assume frontier-model judgment on ambiguous work |
| Context | 128k tokens | Keep packets compact; do not fill the context merely because it is available |
| Modality | Text-only | Do not assign visual acceptance or screenshot interpretation |
| Default behavior | Minimal targeted edits; tests are not automatic | Every packet must name and require its tests |
| Serving | More than 1,000 tokens per second on the preview path | Optimize for iteration speed, not autonomous task duration |
| Usage | Separate preview rate limit; standard-limit exclusion stated for the preview | Measure actual account usage; do not claim a permanent discount |
| Pricing | Preview credit rate not final | No fixed savings percentage or accounting rate may be checked in |

Official references, verified on 2026-08-11:

- [Introducing GPT-5.3-Codex-Spark](https://openai.com/index/introducing-gpt-5-3-codex-spark/)
- [Codex model selection](https://learn.chatgpt.com/docs/models)
- [Codex rate card](https://help.openai.com/en/articles/20001106-codex-rate-card)

The official sources do not publish a reliable project-specific quality score,
fixed preview price, guaranteed capacity, or guaranteed long-term availability.
This plan therefore uses local acceptance evidence rather than assumed model
equivalence or marketing claims.

## 4. Repository baseline

The planning branch starts at commit
`a0e115e17009cc14b3d883e3c291d47c32f7ca4e` with these verified facts:

| Surface | Baseline |
|---|---:|
| Branch state | Clean `main` before branch creation |
| Repository health | 100 / 100 |
| Readiness audit | 19 / 19 |
| FastAPI endpoints | 69 |
| Test functions reported by session brief | 3,671 |
| Non-archive Markdown documents | 316 |
| Non-archive Python/shell scripts | 116 |
| Automation-map task entries | 115 |
| React non-test TypeScript/TSX files | 110 |
| FastAPI router/model Python files | 33 |
| Public Python example files | 10 |
| Active-code TODO/FIXME/HACK markers found in the initial scan | 44 |

Baseline counts are orientation evidence, not permanent completion targets. A
packet may update a count only through the canonical generator or scanner that
owns it.

## 5. Existing lane protection

The following branches/worktrees existed when this program was created and are
outside Spark ownership unless their owner explicitly hands them off:

| Lane | Protected concern |
|---|---|
| `codex/is456-slabs-closeout` | Slab calculation/API/UI closeout |
| `codex/footing-isolated-v1` | Isolated-footing calculation/API/UI workflow |
| `codex/column-rectangular-e2e` | Rectangular-column review workflow |
| `codex/is456-beam-primary-route` | Primary beam/torsion route integration |
| `codex/column-pmm-experimental` | Experimental generalized PMM solver |
| `codex/excel-product-planning` | Online Excel product planning |
| `codex/parallel-task-policy` | Parallel-task and worktree workflow policy |

Before every implementation packet, the parent must re-run:

```bash
git status --short --branch
git worktree list --porcelain
git diff --name-only main...<protected-branch>
```

If a packet overlaps an active lane, pause it. Do not edit around the collision,
copy another lane's unmerged code, or resolve ownership by rebasing, stashing,
resetting, or deleting worktrees.

## 6. Program outcome and definition of done

SPARK-001 succeeds when the project has a measured, repeatable, and safe Spark
lane that completes useful work at lower practical usage without lowering the
accepted result.

Program completion requires:

- a current Spark profile and packet template in the repository control plane;
- a calibration record based on actual usage and rework, not an assumed price;
- every accepted packet to have an exact objective, owned paths, non-goals,
  acceptance criteria, test commands, and return evidence;
- documentation, automation, API, examples, and UI findings to be dispositioned
  without generic cleanup expansion;
- outcome-changing defects to be fixed at their confirmed root cause;
- generated files to be changed only through their canonical generators;
- no accepted packet to weaken supported-case wording, units, provenance,
  authentication, stale-result protection, or release controls;
- targeted checks during work, a quick gate before each accepted commit, and one
  full integrated gate at stable wave boundaries;
- the final branch to be reviewed by a non-Spark parent before merge;
- stable-release and engineering-use holds to remain intact.

High task volume is not itself success. Accepted outcomes, low rework, and
preserved truth are the measures that matter.

## 7. Main-process and architecture contract

Every packet is evaluated against the maintained product process:

```text
ETABS/CSV or direct input
  -> adapters and validation
  -> Python services
  -> pure IS 456 calculations
  -> FastAPI REST/WebSocket transport
  -> React/R3F workbench
  -> revision-bound results and exports
  -> exact package/release evidence
```

The dependency direction remains:

```text
core types -> codes/is456 pure math -> services -> FastAPI/React
```

Spark must not move I/O or UI state into the calculation layers, guess units,
duplicate capability truth, or create a second source of public API metadata.

## 8. Protected areas and non-goals

### 8.1 Protected without explicit escalation

```text
Python/structural_lib/core/
Python/structural_lib/codes/is456/
Python/structural_lib/services/capabilities.py
docs/verification/is456-library-first-evidence.md
fastapi_app/config.py
.github/workflows/
```

Read-only inspection is allowed when required by a packet. Any proposed edit to
these paths stops the packet and returns an escalation note unless the owner has
approved that exact path and acceptance method.

### 8.2 Program non-goals

- new IS 456 formulas, coefficients, clause interpretations, or benchmark truth;
- generalized PMM, wall, stair, deep-beam, seismic, FEM, or multi-code work;
- changing supported or held cases merely to improve presentation;
- professional validation or engineering-use approval;
- security architecture, auth-policy redesign, secret provisioning, or OWASP signoff;
- dependency-major migrations such as coordinated Vite or ESLint upgrades;
- arbitrary test-coverage expansion or tests that do not change acceptance;
- image/screenshot-based visual approval;
- Git conflict recovery, rebase, force push, branch deletion, or worktree cleanup;
- GitHub ruleset changes, merges, releases, package publication, or issue closure;
- speculative hardening, comment cleanup, formatting churn, or adjacent refactors.

## 9. Spark suitability and escalation matrix

| Work type | Spark role | Required acceptance |
|---|---|---|
| Search, inventory, extraction, classification | Owner | Parent checks sample and totals |
| Documentation truth repair | Owner | Canonical source and link checks agree |
| Generated index/manifest refresh | Owner | Generator and drift check pass |
| Small existing-pattern code change | Owner with narrow scope | Focused test plus parent diff review |
| Pydantic/OpenAPI examples | Owner with schema guard | Schema snapshot and OpenAPI checks pass |
| Bounded React wiring | Owner with behavior contract | Focused component test and frontend check |
| Deterministic test failure with obvious cause | First responder | Root cause demonstrated; narrow test passes |
| Ambiguous cross-layer defect | Evidence collector only | Escalate to Terra or stronger parent |
| Architecture, auth, release, IS 456 math | Not owner | Stronger model and relevant human gate |
| Visual design judgment | Not owner | Multimodal review required |

Escalate immediately when:

1. the packet needs an unlisted file outside its owned paths;
2. two plausible root causes remain after targeted inspection;
3. the same focused test fails after two evidence-based corrections;
4. a public calculation value, supported case, unit, or provenance would change;
5. a protected worktree or shared generated file overlaps;
6. acceptance depends on visual judgment, security judgment, or professional
   structural-engineering judgment;
7. the change would require a new architecture pattern rather than reuse an
   existing one.

## 10. Worker packet contract

Every Spark task must use this structure:

```text
Task ID and title:
One objective:
Why it changes the main outcome:
Owned paths:
Read-only reference paths:
Explicit non-goals:
Existing pattern to reuse:
Likely pitfalls:
Acceptance criteria:
Targeted commands:
Quick gate required: yes/no
Expected return:
  - findings or files changed
  - confirmed root cause, or none
  - command/test evidence
  - unresolved risks
  - exact paths touched
Stop conditions:
```

Spark must be told to run tests. “Make the change” is not a sufficient packet.

## 11. Git, context, and concurrency rules

1. Keep one parent program task active.
2. Default to one Spark worker. At most two may run when paths and generated
   outputs are disjoint and the owner explicitly approves parallel execution.
3. Do not pass the full conversation. Supply the packet, exact files, relevant
   index, baseline commit, and commands only.
4. Keep implementation packets small enough for one coherent review. Prefer
   fewer than 20 edited files; generated snapshots are counted separately but
   must be called out.
5. Commit only after parent review and the packet gate. Use one conventional
   commit per accepted packet or tightly coupled pair.
6. Never combine documentation truth repair, API behavior change, and UI feature
   work in one commit merely to reduce commit count.
7. Recheck branch, upstream, diff, worktrees, and active PR before Git mutation.
8. Preserve unrelated staged, unstaged, untracked, and stashed work.
9. Push and PR actions require the parent to recheck the reviewed head and live
   checks. Merge and release remain separate decisions.

## 12. Verification ladder

| Level | Evidence | Frequency |
|---|---|---|
| V0 Inspect | Folder index, targeted `rg`, current Git/worktree state | Every packet |
| V1 Narrow | Exact script, unit test, component test, or docs check | During iteration |
| V2 Packet | Affected-domain check plus parent diff review | Before acceptance |
| V3 Commit | `./run.sh check --quick` | Before each accepted commit |
| V4 Wave | `./run.sh check`, `./run.sh audit`, `./run.sh health`, `./run.sh efficiency check` | Once per stable wave |
| V5 Product | Maintained live import/design/review/export path | After product-affecting waves |
| V6 Release | Release preflight and exact-artifact verification | Only after separate approval |

Do not run the full gate after every small packet. Do not accept a confident
report without reviewing the diff and evidence.

## 13. Measurement and cost-learning plan

The purpose is to learn whether Spark is cheaper in practice for this repository,
not to assume that speed equals savings.

For the first ten accepted packets, record:

| Field | Source |
|---|---|
| Task ID and category | Packet |
| Start/end time | Session checkpoint |
| Files inspected and changed | Git evidence |
| Targeted commands run | Worker return |
| First-pass acceptance | Parent review |
| Correction turns | Parent/worker history |
| Final verification | Gate output |
| Visible usage/credits, if available | Settings > Usage or task usage UI |
| Queueing or availability interruption | Observed client state |
| Escalation model and reason | Parent decision |

Use `./run.sh session usage` for repository-side checkpoints, but do not treat
its empty token fields as billing evidence. Do not enter an estimated credit
rate for Spark. After ten packets, compare:

- accepted outcomes per task;
- median correction turns;
- median elapsed time;
- percentage requiring escalation;
- regressions found by parent review;
- visible provider usage when available.

Continue the program only if the quality-adjusted result is favorable.

## 14. Program sequence

```text
Wave 0: control plane and calibration
  -> Wave 1: truth and documentation
  -> Wave 2: automation contracts
  -> Wave 3: API contracts and examples
  -> Wave 4: bounded React product polish
  -> Wave 5: runnable examples and package UAT
  -> Wave 6: verification and evidence operations
  -> Wave 7: post-merge integration and closeout
```

Waves 1 and 2 may overlap only after Wave 0 is accepted and only when they do not
touch shared indexes, `docs/TASKS.md`, `next-session-brief.md`, or session logs.
Waves 3–5 remain sequential when they share API manifests, OpenAPI snapshots, or
React navigation. Wave 7 waits until the protected element lanes reach an owner-
approved integration state.

## 15. Wave 0 — Control plane and calibration

### S0-01 — Add truthful Spark policy support

**Objective:** Represent Spark's verified preview properties without replacing
the user's model selection or inventing a fixed token rate.

**Likely paths:** `agents/model_policy.json`,
`docs/guidelines/ai-token-efficiency.md`, focused policy tests.

**Acceptance:** Picker/policy validation passes; Spark is marked preview,
text-only, separately rate-limited, and unpriced; Luna remains unavailable and
Sol remains approval-gated.

### S0-02 — Extend the task-aware picker

**Objective:** Recommend Spark only for suitable bounded tasks and emit an
explicit escalation trigger for ambiguous or high-risk work.

**Likely paths:** model picker implementation, its focused tests, generated help.

**Acceptance:** Deterministic examples distinguish Spark, Terra, and Sol; an
explicit user selection still overrides the picker.

### S0-03 — Add the Spark packet template

**Objective:** Make objective, owned paths, non-goals, pitfalls, acceptance,
tests, return format, and stop conditions mandatory.

**Acceptance:** The template is discoverable through the existing agent/tool
entry path and does not duplicate all of `AGENTS.md`.

### S0-04 — Add preview-safe usage checkpoints

**Objective:** Record actual visible usage and rework without estimating Spark
credits.

**Acceptance:** Existing usage-ledger validation passes; blank provider fields
remain valid; documentation states the source and limitations of each metric.

### S0-05 — Five-packet calibration trial

**Objective:** Run one documentation, automation, API-example, React-inventory,
and example-UAT packet before authorizing the remaining program.

**Acceptance:** Parent records first-pass acceptance, corrections, elapsed time,
visible usage if available, and any escalation. The owner makes a continue,
adjust, or stop decision.

## 16. Wave 1 — Truth and documentation program

Spark performs findings-first audits. A packet edits only confirmed stale truth
whose correction changes onboarding, API use, supported-scope understanding, or
verification reliability.

| ID | Packet | Primary acceptance |
|---|---|---|
| S1-01 | Reconcile `docs/TASKS.md` against current code and accepted plans | No open item is already complete or contradicted by current evidence |
| S1-02 | Audit `next-session-brief.md` and required-reading links | One current handoff, correct branch/base, no stale lane instruction |
| S1-03 | Audit root README, Python README, FastAPI README, React README, and `llms.txt` | Install/run/examples and Alpha wording agree |
| S1-04 | Audit getting-started and release documentation | Current commands, Node/Python versions, release holds, and artifact wording agree |
| S1-05 | Audit public API reference for exposed services | Signatures, units, response types, and exposure claims match code |
| S1-06 | Resolve the stale footing documentation/backlog contradiction | `DOC-4` disposition and service-exposure wording are evidence-backed |
| S1-07 | Generate or repair the clause-to-public-function mapping | Mapping comes from canonical metadata; missing clauses remain explicit |
| S1-08 | Audit capability and limitation wording | Beam/column/footing/slab supported and held cases match `capabilities.py` |
| S1-09 | Audit cookbook and public worked examples | Every advertised example is runnable or explicitly held |
| S1-10 | Audit developer and contributor documentation | Commands and architecture paths are current and non-destructive |
| S1-11 | Separate active authority from historical/migration documents | Historical plans are not presented as current implementation truth |
| S1-12 | Run link, version, bootstrap-freshness, and docs-index closeout | All canonical documentation checks pass |

Do not rewrite prose merely for style. Do not convert qualified-review holds into
software completion claims.

## 17. Wave 2 — Automation and script contract program

The automation map contains 115 task entries and the non-archive script surface
contains 116 Python/shell files at baseline. Audit them in bounded functional
groups, not arbitrary alphabetical chunks.

| ID | Packet | Required evidence |
|---|---|---|
| S2-01 | Registry-to-file physical coverage | Every active mapping resolves to one maintained target |
| S2-02 | Help and usage contracts | `--help`/usage paths exit predictably without mutation |
| S2-03 | Python runtime and cwd assumptions | Root/worktree execution uses the canonical runtime |
| S2-04 | Read-only command behavior | Status, audit, summary, and dry-run modes do not write |
| S2-05 | Explicit mutation modes | Stateful commands require documented `--fix`, `--write`, or equivalent |
| S2-06 | Safe file operations | Move/delete routes use maintained safe-file tools and bounded targets |
| S2-07 | Index and manifest generators | One canonical generator owns each generated output |
| S2-08 | API/schema/OpenAPI discovery tools | Fail-closed signatures and drift checks agree |
| S2-09 | Test and live-UAT launchers | Commands select correct environments and propagate failures |
| S2-10 | Session, governance, and feedback tools | Current required sections and recurrence handling agree |
| S2-11 | Package, release, and deployment scripts | Inspection only unless separately approved; no release mutation |
| S2-12 | Active/archive disposition ledger | Keep/update/review/archive disposition for every audited script |

For each material defect record symptom, impact, confirmed root cause, minimal
solution, and command evidence. Ignore generic hardening that does not change the
main process.

## 18. Wave 3 — FastAPI contracts and examples

| ID | Packet | Primary acceptance |
|---|---|---|
| S3-01 | Build the 69-endpoint route/model/service matrix | Every endpoint has owner, request, service, response, and tests |
| S3-02 | Inventory OpenAPI example coverage | Missing examples are listed by public importance, not guessed |
| S3-03 | Add beam/import/export examples in one existing pattern | Schema snapshot and OpenAPI drift checks pass |
| S3-04 | Add column/footing/slab examples after lane integration | Units and supported-case limitations are explicit |
| S3-05 | Verify Pydantic ranges, aliases, and unit suffixes | Models agree with service signatures; no hidden conversion |
| S3-06 | Verify success and error envelopes | Documented behavior matches maintained handlers, including 422 |
| S3-07 | Reconcile OpenAPI baseline, API manifest, and reference docs | Generated artifacts have one canonical source and no drift |
| S3-08 | Execute public curl/request examples | Representative examples pass against the maintained app |

Spark may add examples and repair obvious adapter/schema mismatches. It must
escalate any calculation-semantic, auth-policy, or public-versioning decision.

## 19. Wave 4 — Bounded React product polish

This is text/code-based behavior work, not visual-design acceptance.

| ID | Packet | Primary acceptance |
|---|---|---|
| S4-01 | Route and navigation reachability inventory | Every exposed route has a useful entry and exit or a retire decision |
| S4-02 | Command palette disposition | Six inert defaults are either wired through existing actions or the unmounted surface is safely retired |
| S4-03 | Building Editor Cost tab wiring audit | Placeholder behavior is connected to canonical existing data or explicitly removed |
| S4-04 | Keyboard command ownership | Shortcuts invoke real actions without duplicating global handlers |
| S4-05 | Loading, empty, and error-state audit | Main journeys do not silently stall or expose dead actions |
| S4-06 | Revision/stale-result presentation audit | Old results and exports cannot appear current after input changes |
| S4-07 | React request/response type audit | Types match maintained API contracts or generated source |
| S4-08 | Outcome-changing accessibility audit | Keyboard/focus/name defects blocking the main journey are fixed |
| S4-09 | Dormant component and hook disposition | Each unused surface is keep/wire/retire with reachability evidence |
| S4-10 | Focused frontend closeout | Targeted tests, lint, type-check, production build, and parent review pass |

Do not approve spacing, color, hierarchy, or responsive visuals from text alone.
Use a multimodal reviewer for any visual acceptance gate.

## 20. Wave 5 — Runnable examples and package UAT

| ID | Packet | Primary acceptance |
|---|---|---|
| S5-01 | Run and repair the ten public Python example files | Examples use public APIs and current signatures |
| S5-02 | Validate the maintained notebook | Clean execution or an explicit documented environment hold |
| S5-03 | Validate direct-design and capability-discovery quickstarts | Outputs and limitations match current package behavior |
| S5-04 | Validate bundled CSV/ETABS sample walkthrough | Canonical tracked data and identity-bound results are used |
| S5-05 | Validate FastAPI curl examples | Requests succeed with documented envelopes and units |
| S5-06 | Validate wheel/sdist file contents and installed examples | Exact artifact inventory and isolated UAT agree |
| S5-07 | Reconcile onboarding evidence | README, docs, examples, and package metadata describe one truth |

No example may imply whole-standard completion or professional approval.

## 21. Wave 6 — Verification and evidence operations

| ID | Packet | Primary acceptance |
|---|---|---|
| S6-01 | Map maintained tests to product surfaces | Commands and ownership are current; no coverage inflation |
| S6-02 | Audit markers, deselections, and skip reasons | Every maintained skip is intentional and discoverable |
| S6-03 | Triage deterministic or recurring failures | Confirmed root cause and narrow corrected outcome |
| S6-04 | Validate Python package test entry paths | Root and isolated-wheel commands agree |
| S6-05 | Validate FastAPI test entry paths | Full router contract suite is reproducible |
| S6-06 | Validate React test/lint/build entry paths | Pinned Node runtime and commands agree |
| S6-07 | Validate maintained live browser/UAT commands | Main path is reproducible; observer limits are not product failures |
| S6-08 | Produce wave evidence ledger | Commit, commands, outputs, risks, and claims are traceable |

Do not add tests merely because a line is uncovered. Add or change a test only
when it is necessary to prove an outcome-changing fix and the packet authorizes it.

## 22. Wave 7 — Post-merge integration and program closeout

Wave 7 starts only after the owners of the protected beam, column, footing, slab,
Excel, and policy lanes provide explicit integration status.

| ID | Packet | Primary acceptance |
|---|---|---|
| S7-01 | Re-audit branch/worktree/PR ownership | No integration begins from stale or conflicting state |
| S7-02 | Reconcile route and navigation additions | One coherent workbench map; no lost or duplicate entry points |
| S7-03 | Reconcile OpenAPI, API manifest, indexes, and route counts | Canonical generators pass without hand-edited snapshots |
| S7-04 | Reconcile capability discovery and public wording | New surfaces remain bounded and truthfully held |
| S7-05 | Run cross-element API/React focused tests | Beam/column/footing/slab routes coexist without regression |
| S7-06 | Run maintained live end-to-end UAT | Import/direct input through current review/export paths passes |
| S7-07 | Run full repository and evidence gates | Full, audit, health, efficiency, and required live checks pass |
| S7-08 | Independent non-Spark final review | Diff, evidence, usage results, and unresolved risks are accepted |

Release, stable claims, and qualified review remain outside SPARK-001 closeout.

## 23. Review gates and owner decisions

| Gate | Decision required |
|---|---|
| G0 Plan review | Accept, revise, or reject this plan |
| G1 Calibration review | Continue, adjust packet size, change model mix, or stop |
| G2 Truth/automation review | Approve the first implementation-wave commits |
| G3 API/UI review | Confirm product work remains bounded and non-overlapping |
| G4 Integration review | Authorize post-merge reconciliation |
| G5 Final review | Accept branch for PR, request corrections, or archive the experiment |

No later gate is implied by an earlier acceptance.

## 24. Risk register

| Risk | Impact | Control |
|---|---|---|
| Preview pricing or limits change | Savings assumptions become stale | Record live usage; no fixed checked-in price |
| Speed encourages oversized scope | Large shallow diff and rework | Small packets, wave caps, parent acceptance |
| Tests are omitted | Incorrect changes appear complete | Exact mandatory command in every packet |
| Text-only model judges visual quality | UI regressions escape | Multimodal visual acceptance outside Spark |
| Active worktree overlap | Lost or conflicting work | Recheck ownership and diff before every packet |
| Documentation polishing changes claims | Product overstatement | Capability source and qualified-review holds govern |
| Generated files are hand edited | Drift returns | Generator-only ownership and drift checks |
| Small model guesses an architectural solution | Structural/API inconsistency | Existing-pattern rule and immediate escalation |
| High task count creates low-value churn | Time spent without main-process benefit | Essential-only finding gate and parent rejection |
| Separate preview limit causes queuing | Work stalls unpredictably | Pause cleanly; do not route around controls |

## 25. Required worker return format

```text
Packet:
Baseline branch and commit:
Files inspected:
Files changed:
Outcome:
Material issues encountered:
Root causes and resolutions:
Targeted verification:
Quick gate:
Unresolved risks:
Protected paths unchanged:
Suggested conventional commit:
Escalation required: yes/no and why
```

The parent independently verifies this return. A return is evidence input, not
automatic acceptance.

## 26. Initial review checklist

- [x] Isolated branch created from the clean main baseline.
- [x] Existing worktrees and ownership boundaries recorded.
- [x] Official Spark facts separated from assumptions.
- [x] Pricing and rate-limit uncertainty recorded.
- [x] Structural math, security, release, and visual gates excluded.
- [x] Worker packet, verification ladder, escalation rules, and return format defined.
- [x] Program decomposed into bounded dependency-ordered packets.
- [ ] Repository owner reviews packet scope and ordering.
- [ ] Repository owner accepts, revises, or rejects Wave 0.
- [ ] `implementation_authorized` changes only after explicit acceptance.

## 27. Immediate next action

Review this plan before implementation. If accepted, authorize Wave 0 only,
starting with S0-01 and S0-03. Do not begin the 70-packet program in bulk.
