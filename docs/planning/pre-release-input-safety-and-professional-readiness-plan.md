# Pre-Release Input Safety and Professional Readiness Plan

**Task:** LIB-PRO-002
**Type:** Decision
**Audience:** Maintainers
**Status:** In Progress
**Created:** 2026-08-17
**Last Updated:** 2026-08-17
**Importance:** Critical
**Prepared:** 2026-08-17
**Source base:** `origin/main` at `904a2f8cf0ea5d4595f57c46dac06e2e837bba45`
**Scope:** Public/project input, import accounting, orchestration, result truth,
API classification, evidence identity, documentation, and release gates
**Source bound:** `true`

## 1. Executive decision

The narrow one-storey pilot supports a useful but limited conclusion: for the
specific slab, beam, column, and footing cases exercised, the independently
recomputed arithmetic matched the library outputs. The footing dowel
development-length failure was also reproduced and is a legitimate failure,
not a software defect.

That evidence does **not** establish that the library is safe as a project or
whole-building workflow. Live code inspection confirms that multiple public
paths can replace missing or malformed structural values with plausible
defaults, discard recognized fields, select an unintended CSV adapter, drop
invalid rows, or manufacture zero forces before the calculation core runs. A
calculation can therefore be arithmetically correct for values the user did not
provide.

The decision is:

- Hold every next public package publication until the Alpha safety gate in
  Section 5 is complete and separately authorized by the owner.
- Continue describing the current release as Alpha/development software.
- Do not claim whole-building design, professional approval, codewide formula
  certification, or project fitness from the pilot.
- Repair the canonical input and accounting boundary before expanding formulas,
  load cases, structural systems, or UI capability.
- Preserve the completed `LIB-PRO-001` ledger. This is a new remediation
  program caused by new end-user workflow evidence, not a reopening or rewrite
  of the completed historical packet.

No tag, package upload, GitHub Release, professional approval, issue closure,
branch deletion, or retained-worktree cleanup is authorized by this plan.

## 2. What the pilot establishes—and what it does not

### 2.1 Accepted evidence

For the supplied synthetic one-storey assumptions, the reported slab load,
slab moment, slab steel, beam moment, beam shear, beam steel, column capacity,
column minimum moment, footing pressure, footing moment, punching utilization,
and dowel development length matched the independent calculations reported by
the audit. The match is useful regression evidence for those exact supported
cases.

The following behavior is also correct and must be retained:

- the footing calculation blocks when its required soil basis is honestly
  unapproved;
- with the synthetic approval flag, the footing still fails the insufficient
  dowel anchorage check;
- existing bounded slab inputs reject non-finite structural values;
- batch engineering status combines completed flexure and shear results rather
  than treating calculation completion as a PASS.

### 2.2 Claim limits

The pilot does not verify:

- all library functions, all clauses, or all supported geometries;
- gravity-load generation, load takedown, combinations, or member continuity;
- wind, earthquake, stability, robustness, serviceability, or global analysis;
- geotechnical suitability or the factual approval of a soil assumption;
- reinforcement constructability beyond the checks explicitly returned;
- package installation and every documented example from the exact wheel;
- a single controlled slab-to-beam-to-column-to-footing load path;
- professional engineering approval for a real project.

The `1.5` factor and soil pressure in the pilot remain user-supplied
assumptions. An approval flag records a workflow state; it cannot convert an
assumption into verified source data.

## 3. Confirmed root-cause map

The apparent list of many failures reduces to six root causes. Fixing symptoms
independently would create more formats and more drift.

| Root cause | Confirmed mechanism | Main-process consequence | Required correction |
|---|---|---|---|
| RC-1: no canonical project input | Service batch accepts several aliases, React emits another shape, imports define another row model, and columns have a separate defaulting route | The same project data can mean different values by entry path | One versioned, strict project schema shared by service and transports |
| RC-2: coercion is mixed with assumption | Missing, empty, or malformed values fall through `_to_float` or UI/Pydantic defaults | The software can calculate a default member and return a plausible PASS | Parsing must fail closed; structural defaults may exist only in explicitly named examples/templates |
| RC-3: import success does not account for every row and field | First-match adapter selection, invalid-row skips, invalid-force-to-zero behavior, and soft unmatched records | Source data can disappear without preventing a project verdict | Explicit/deterministic format selection plus a lossless row-and-field ledger |
| RC-4: orchestration is duplicated | Service batch, streaming, import batch design, React preparation, and column routes each normalize or derive values | Effective depth, materials, identity, and errors differ by route | Transports delegate to one service boundary and never derive structural values |
| RC-5: result/review semantics are not one contract | PASS/FAIL/HOLD, calculation success, review status, errors, and slab wording vary by element | A consumer can confuse software completion with engineering acceptance or professional review | One result envelope with orthogonal intake, calculation, engineering, and review states |
| RC-6: release truth tests happy paths, not the advertised product | Version surfaces, examples, export classifications, exact-wheel negative paths, and source identity are not one gate | Green CI can coexist with stale or unsafe published guidance | Machine-checked API inventory, executable documentation, negative UAT, and exact artifact evidence |

## 4. Outcome-changing issue register

Priority means publication impact, not code size. `P0` blocks the next public
package. `P1` blocks stable/professional-readiness claims or a claimed product
surface. `P2` is required before the related capability is advertised.

| ID | Pri | Confirmed issue | Evidence location | Exit condition |
|---|---:|---|---|---|
| INPUT-01 | P0 | Batch aliases omit ordinary headings such as `BeamID`, `Mu (kN-m)`, and `Cover (mm)` and silently substitute dimensions, actions, materials, cover, and identity | `Python/structural_lib/services/batch.py` | Missing, unknown, malformed, empty, and non-finite project inputs produce stable blocking errors; no calculation is invoked |
| CLIENT-01 | P0 | React replaces absent moment/shear with zero and materials/cover with 25/500/40 before transport | `react_app/src/hooks/useBatchDesign.ts` | Client sends only source-derived canonical values; missing fields remain missing and block at the shared boundary |
| ROUTE-01 | P0 | Service batch and import batch-design routes independently build inputs and derive effective depth | `services/batch.py`, `fastapi_app/routers/imports.py`, `routers/streaming.py` | Every project design route delegates to the same validated service command; route-level structural derivation is absent |
| DEPTH-01 | P0 | Effective depth is approximated inconsistently (`D-cover-8`, `D-cover-25`, or section-model recomputation); a recognized explicit depth can be discarded | batch, imports, adapters, section models | Input uses one mutually exclusive explicit-depth or auditable derivation-basis contract; conflicts block |
| FIELD-01 | P0 | Unknown or recognized-but-unconsumed schedule fields do not prevent a calculation | batch and generic adapter | Every source field is accepted and recorded, explicitly metadata-only, or rejected; no silent ignore |
| IMPORT-01 | P0 | Adapter discovery is first-match and can select ETABS for a file also accepted by Generic | `services/imports.py`, `services/adapters.py` | Explicit format wins; auto-detection requires one unambiguous match or blocks with all candidates listed |
| IMPORT-02 | P0 | Invalid rows can be skipped and malformed forces can become zero | adapter parsers and import router | `source_rows = accepted_rows + blocked_rows` and every blocked row has a stable reason; zero is accepted only when explicitly present and valid |
| IMPORT-03 | P0 | Unmatched geometry/force records can remain warnings while validation reports success | import matching/validation | Every unmatched design-bearing record is a blocking ledger entry unless an explicit, source-recorded exclusion policy covers it |
| EMPTY-01 | P0 | Empty or fully filtered work can produce a completed-looking summary in some layers | batch/UI aggregation | Zero evaluated members can never be PASS; envelope reports BLOCKED/NOT_EVALUATED |
| COLUMN-01 | P0 | Unified column design can supply 25/415 when project materials are absent | column service/transport boundary | Project-mode column materials are explicit finite inputs or intake blocks |
| REVIEW-01 | P0 | Slab detailing emits `no_qualified_review_required`, and a maintained test encodes that phrase | slab detailing result and tests | All structural results retain `qualified_review_required=true`; serviceability escalation is a separate field |
| RESULT-01 | P0 | Elements and transports use incompatible success, result, error, and review shapes | service and transport result models | One versioned envelope separates intake, calculation, engineering, and review states; adapters cannot infer PASS from missing fields |
| ASSUME-01 | P1 | An approval boolean can be read as if assumed soil/load data became verified | footing/project input provenance | Basis origin (`provided`, `assumed`, `verified`) and approval are separate, immutable fields displayed in results |
| PROV-01 | P0 | Evidence does not uniformly bind exact input artifact, normalization ledger, library/tree identity, controlled source, and amendment applicability | evidence envelope and source registry | Each result carries hashes/identities sufficient to replay exact input and source basis; unknown amendment applicability remains UNKNOWN/HOLD |
| API-CLASS-01 | P1 | Public manifests enumerate many symbols without a complete stable/preview/compatibility/internal classification | API manifest, `api-levels.md`, `api-stability.md` | Every exported symbol has an owner-reviewed class; undeclared exports and callable leakage fail CI |
| API-DOC-01 | P1 | `api-stability.md` says Production Ready while the released library is Alpha and professional approval is held | API reference docs | Alpha, stable API, engineering support, evidence, and professional approval claims are stated independently and consistently |
| REL-TRUTH-01 | P0 | Root README still advertises 0.23.0 while package docs advertise 0.23.1a1; release version checks omit these README surfaces | READMEs and `scripts/release.py` | All maintained current-version surfaces are checked against the candidate version or explicitly historical |
| REL-EXAMPLE-01 | P0 | The Python README batch example uses fields not returned by the shown import result; public examples are not executed from the exact wheel | `Python/README.md`, publish workflow | Every advertised quickstart/example runs in a source-free temporary environment against the exact built wheel |
| REL-UAT-01 | P0 | Exact-wheel UAT covers happy paths but not silent-default, row-loss, empty, unknown-field, or review-language cases | `.github/workflows/publish.yml`, release checks | Candidate wheel passes the negative acceptance matrix in Section 7 and the supported end-to-end workflows |
| INSTALL-01 | P1 | Repository operation depends on the selected `.venv`, while beginner guidance does not provide one decisive preflight and repair path | setup docs/runtime guidance | One documented command reports interpreter, installed extras, package origin/version, and a clear install command without repository-only assumptions |
| CLAIM-01 | P0 | A 12-value pilot match can be overgeneralized into “library formulas are accurate” | publication language | Claims name exact cases, evidence, exclusions, and independent-review status; codewide/professional claims are prohibited without their own evidence |
| BUILDING-01 | P2 | There is no controlled slab-to-foundation project orchestration or load-path reconciliation | service/product architecture | Separate owner-approved packet defines model, load provenance, combinations, equilibrium checks, supported systems, and review dossier before implementation |

The footing dowel failure is intentionally absent from the defect register: it
is a correct engineering failure. It becomes a regression case in RESULT-01
and the later project workflow.

## 5. Publication gates

### 5.1 Next Alpha publication gate

All of the following are mandatory before requesting separate owner permission
for another public Alpha:

1. INPUT-01, CLIENT-01, ROUTE-01, DEPTH-01, FIELD-01, IMPORT-01 through
   IMPORT-03, EMPTY-01, COLUMN-01, REVIEW-01, RESULT-01, and PROV-01 are
   accepted.
2. REL-TRUTH-01, REL-EXAMPLE-01, REL-UAT-01, and CLAIM-01 are accepted against
   the exact candidate wheel in a source-free environment.
3. The candidate describes only its bounded component capabilities. A missing
   whole-building workflow is an explicit limitation, not an implied feature.
4. Focused, quick, cumulative Python/FastAPI/React, packaging, protected-source,
   and all required hosted checks pass on one immutable reviewed head.
5. The exact wheel hash, source tree, test results, known holds, and independent
   exact-head software/release-evidence review receipt are bound in release
   evidence. This Alpha review is not qualified structural-engineering review
   or professional approval.
6. The repository owner separately authorizes the exact version/tag/package
   publication. This plan is not that authorization.

### 5.2 Stable or engineering-use gate

In addition to the Alpha gate, stable or engineering-use language requires:

- API-CLASS-01, API-DOC-01, ASSUME-01, and INSTALL-01 acceptance;
- cumulative independent numerical benchmarks for every claimed supported
  family, not extrapolation from this pilot;
- explicit serviceability, detailing, load-combination, and applicability
  limits for the claimed surface;
- a qualified structural engineer's cumulative review of the exact candidate;
- a separate owner decision approving the stable/engineering-use claim.

BUILDING-01 is required only before advertising a whole-building capability.
Wind, earthquake, geotechnical design, and additional systems remain separate
source-backed feature packets rather than hidden additions to this remediation.

## 6. Frozen target contracts from G0

These decisions prevent each packet from inventing a local fix. A later change
requires updating this plan and its contract tests before implementation.

### 6.1 Project input contract

Create a versioned `ProjectBeamDesignInputV1` (name may change once, before its
first public exposure) with canonical explicit-unit fields:

- `schema_version`, `member_id`;
- `b_mm`, `D_mm`;
- exactly one of `d_mm` or an `effective_depth_basis` object containing all
  values used in the derivation, including cover and reinforcement diameters;
- `mu_knm`, `vu_kn`, `fck_nmm2`, `fy_nmm2`;
- optional namespaced `source_metadata` that cannot affect calculations.

Rules:

- all calculation-bearing fields are required, finite, and range validated;
- missing, empty, malformed, duplicate, conflicting, and unknown fields block;
- units are part of field names or a validated explicit unit object—never
  inferred from a spreadsheet heading after normalization;
- aliases exist only inside a named, versioned import adapter and are recorded
  in the normalization ledger;
- production/project routes have no structural defaults;
- examples/templates may provide visible example values only through functions
  named as examples/templates, and the returned provenance marks them assumed;
- transports do not calculate effective depth, choose materials, or fill loads;
- duplicate `member_id` values block unless a documented composite source key
  is normalized to unique member identities.

The same pattern will be applied to slab, column, and footing project commands
without forcing unlike elements into one oversized model.

### 6.2 Import and normalization ledger

Every imported artifact returns:

- artifact name/type/hash and declared or detected format/version;
- adapter candidates and the final selection reason;
- source row number and stable source-record identity;
- for every source header: raw header, canonical field or metadata disposition,
  raw value, parsed value, units, and action;
- row status `ACCEPTED` or `BLOCKED` with stable issue code(s);
- totals satisfying `source_rows = accepted_rows + blocked_rows`;
- matching totals for geometry, actions, exclusions, and unresolved records.

Warnings may describe non-calculation metadata. They may not downgrade a
missing or malformed calculation-bearing value from BLOCKED to ACCEPTED.

### 6.3 Result envelope

Use orthogonal state instead of one overloaded status:

| Axis | Allowed meaning |
|---|---|
| Intake | `VALID` or `BLOCKED` |
| Calculation | `NOT_EVALUATED`, `COMPLETED`, or `ERROR` |
| Engineering | `NOT_EVALUATED`, `PASS`, `FAIL`, or `HOLD` |
| Review | always includes `QUALIFIED_REVIEW_REQUIRED`; optional escalation is separate |
| Overall | deterministically derived; never supplied independently by a client |

An engineering PASS requires valid intake, completed calculations, all
requested supported checks passing, no unresolved blocking provenance, and at
least one evaluated member. Professional review remains required even then.

Errors use stable codes plus field/row paths. Human messages may improve
without breaking consumers. Raw exception strings are not the public contract.

### 6.4 Compatibility policy

Because the public package is Alpha, confirmed unsafe behavior is corrected
even when permissive callers relied on it. Compatibility is preserved only
where it does not preserve the hazard:

- old aliases may be accepted through an explicit compatibility adapter;
- missing or malformed structural values still block in compatibility mode;
- deprecated routes delegate to the canonical boundary and emit a documented
  deprecation signal; they do not keep a second calculation path;
- no compatibility mode may silently default a project value or return PASS
  after data loss.

## 7. Mandatory negative acceptance matrix

Each applicable service, FastAPI, React, import, CLI, and exact-wheel path must
prove the same outcome. The matrix is maintained as data so new public routes
cannot omit cases.

| Case | Expected intake | Calculation | Engineering/summary |
|---|---|---|---|
| Complete canonical row | VALID | COMPLETED | PASS/FAIL from requested checks |
| Ordinary supported alias through named adapter | VALID with ledger mapping | COMPLETED | PASS/FAIL |
| Unknown calculation-looking header | BLOCKED | NOT_EVALUATED | never PASS |
| Missing required value | BLOCKED | NOT_EVALUATED | never PASS |
| Empty string or whitespace | BLOCKED | NOT_EVALUATED | never PASS |
| Malformed numeric value | BLOCKED | NOT_EVALUATED | never PASS |
| `NaN`, `+/-inf`, or non-finite derived value | BLOCKED | NOT_EVALUATED | never PASS |
| Conflicting aliases or explicit/derived depth | BLOCKED | NOT_EVALUATED | never PASS |
| Duplicate member identity | BLOCKED | NOT_EVALUATED | never PASS |
| Zero explicitly supplied and valid | VALID only where domain permits | COMPLETED | normal engineering result |
| Empty batch or all rows blocked | BLOCKED | NOT_EVALUATED | zero PASS; summary HOLD/BLOCKED |
| Ambiguous adapter detection | BLOCKED | NOT_EVALUATED | candidates reported |
| Invalid import row | row BLOCKED and accounted | no calculation for row | batch cannot hide loss |
| Geometry without forces / forces without geometry | BLOCKED unless explicit exclusion | NOT_EVALUATED | unresolved identity listed |
| Unapproved footing basis | BLOCKED/HOLD | per bounded contract | never promoted by a flag alone |
| Insufficient footing dowel length | VALID | COMPLETED | FAIL retained |
| Safe supported calculation | VALID | COMPLETED | PASS plus qualified review required |

## 8. Dependency-ordered implementation packets

WIP remains at most two, but these packets are implemented by one writer in
dependency order wherever files overlap. Parallel agents are most useful for
read-only audit and immutable review, not competing edits.

### G0 — Contract and claim freeze (`LIB-PRO-002-G0`, S)

**Status:** completed by this plan candidate; acceptance still requires the
repository gates and independent exact-head review.

**Owns:** this plan, task board, planning index, session log, next-session
brief.
**Deliver:** root-cause reconciliation, issue IDs, target contracts, release
holds, acceptance matrix, packet dependencies, and non-goals.
**Accept:** no contradiction with completed `LIB-PRO-001`; all live confirmed
paths are assigned once; the pilot claims are bounded; release authorization
remains held.
**Rollback:** documentation-only commit can be reverted without runtime impact.

### A — Strict service intake (`LIB-PRO-002-A`, M)

**Depends on:** G0.
**Owns:** new project input/result types, `services/batch.py`, focused service
tests.
**Deliver:** canonical strict beam command, stable validation issues, explicit
depth basis, no project defaults, non-empty/accounted batch summary. Preserve
the legacy function only as a delegating compatibility surface.
**Focused proof:** table-driven Section 7 service cases; calculation spy proves
blocked inputs never call the core; valid pilot beam remains numerically equal.
**Accept:** INPUT-01, DEPTH-01, FIELD-01, EMPTY-01 service portions closed.
**Rollback:** revert one packet; no transport migration occurs in A.

### B — Lossless import boundary (`LIB-PRO-002-B`, L)

**Depends on:** A.
**Owns:** import models, adapter selection, adapter parsers, matching/accounting,
focused import tests and fixtures.
**Deliver:** explicit/unique adapter selection, field normalization ledger,
row conservation, blocking invalid/missing/mismatched records, and preserved
valid ETABS/SAFE/STAAD/Generic cases.
**Focused proof:** ambiguous detection, normal Excel headings, malformed values,
row loss, duplicate IDs, unmatched pairs, and exact accepted/blocked totals.
**Accept:** IMPORT-01 through IMPORT-03 and import portions of FIELD-01 close.
**Rollback:** compatibility adapters remain selectable explicitly; revert the
packet rather than restoring implicit first-match behavior.

### C — Transport and client convergence (`LIB-PRO-002-C`, L)

**Depends on:** A and B.
**Owns:** streaming/import batch endpoints, OpenAPI, React batch hook, focused
FastAPI/React tests.
**Deliver:** one POST-oriented project command for large payloads; GET/SSE and
old import endpoints delegate or deprecate; React sends canonical values and no
structural defaults; cancellation/supersession preserves evidence semantics.
**Focused proof:** identical canonical request has identical normalized input,
issue codes, and engineering outcome through service, HTTP, SSE, and React.
**Accept:** CLIENT-01 and ROUTE-01 close.
**Rollback:** revert transport migration as one packet; do not retain duplicate
normalization to keep an endpoint alive.

### D — Cross-element result and review truth (`LIB-PRO-002-D`, M)

**Depends on:** A. May be developed after A while B is under independent
review, provided owned files do not overlap.
**Owns:** shared result envelope, slab review wording, column project input,
adapters and focused tests.
**Deliver:** orthogonal statuses, required qualified-review flag, separate
serviceability escalation, explicit column materials, retained footing FAIL.
**Focused proof:** safe slab still requires qualified review; missing column
materials block; footing dowel example remains FAIL; no missing status becomes
PASS.
**Accept:** COLUMN-01, REVIEW-01, RESULT-01 close.
**Rollback:** one result-contract compatibility adapter may translate old
field names, but missing status always maps to HOLD—not PASS.

### E — Evidence and assumption identity (`LIB-PRO-002-E`, M)

**Depends on:** A, B, and D.
**Owns:** evidence envelopes, project provenance models, controlled-source
identity links, focused replay tests.
**Deliver:** artifact and normalization hashes, calculation/library identity,
source/amendment identity, separate assumption origin and approval, deterministic
replay receipt.
**Focused proof:** changing any calculation-bearing input changes identity;
metadata-only change is recorded without changing arithmetic identity; unknown
amendment state remains UNKNOWN/HOLD.
**Accept:** ASSUME-01 and PROV-01 close.

### F — Public API and documentation truth (`LIB-PRO-002-F`, M)

**Depends on:** A and D; can inventory in read-only mode earlier.
**Owns:** API classification registry/generator, API reference docs, README
version/examples, discovery tests.
**Deliver:** complete stable/preview/compatibility/internal inventory; declared
exports only; consistent Alpha and approval language; corrected executable
examples; visible install preflight.
**Focused proof:** every discovered/exported symbol classified; no callable
leakage; docs version matches candidate; examples share the canonical schema.
**Accept:** API-CLASS-01, API-DOC-01, REL-TRUTH-01, INSTALL-01, and CLAIM-01
documentation portions close.

### G — Exact-wheel negative UAT and publication policy (`LIB-PRO-002-G`, L)

**Depends on:** A through F.
**Owns:** release preflight, publish workflow, source-free example runner,
release evidence schema, policy tests.
**Deliver:** exact-wheel execution of advertised examples and Section 7; split
Alpha versus stable gates; immutable artifact/source/test receipts; explicit
owner authorization stop.
**Focused proof:** intentionally unsafe fixture fails preflight; exact candidate
wheel passes public examples and supported end-to-end workflows without source
checkout imports.
**Accept:** REL-EXAMPLE-01, REL-UAT-01, remaining REL-TRUTH-01 close. Run broad
Python, complete FastAPI/React, full canonical, packaging, protected-source,
hosted checks, and immutable independent review once at this cumulative
boundary.
**Rollback:** release remains held; never weaken the negative matrix to make a
candidate pass.

### H — Whole-building workflow decision (`LIB-PRO-002-H`, planning only, L)

**Depends on:** G and separate owner activation.
**Owns:** a new source-backed plan—not calculation code.
**Deliver:** supported structural model, load provenance/takedown, combinations,
equilibrium/load-path checks, element result aggregation, detailing/review
dossier, exclusions, and benchmarks.
**Accept:** BUILDING-01 becomes an implementation-ready, owner-approved program.
Wind, earthquake, soil design, continuity, and other structural systems remain
separate source packets unless expressly selected.
**Rollback:** retain component-only claim; do not simulate building support by
chaining unrelated examples.

## 9. Efficient execution controls

The fastest safe path is contract-first and evidence-last:

1. Keep a single active writer packet and at most one independent read-only
   reviewer. WIP=2 is a ceiling, not a target.
2. Use the fresh `codex/<packet>` lane from fetched `origin/main`; require
   `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
   equality before edits.
3. Before each packet, inspect only folder indexes, exact owned paths, callers,
   and focused tests. Do not reload full historic plans or large logs.
4. Freeze schemas and expected outcomes before implementation. Add tests only
   for behavior the packet changes; avoid generic hardening.
5. Run focused tests while editing. Run architecture/import checks when a layer
   boundary changes, then quick once on the frozen candidate.
6. Reserve broad Python/FastAPI/React and full canonical gates for cumulative
   Packet G unless a packet exposes repository-wide risk.
7. Use one candidate and at most one repair candidate. A material post-push
   defect creates a new reviewed candidate; status prose does not mutate the
   immutable head.
8. Finish task, session, handoff, evidence, and pre-commit receipt first. Write
   affected indexes last, then validate without rewriting them.
9. Independently review exact commit/tree and bind hosted checks before merge.
10. Report total wall time including CI and closeout so later estimates improve.

### Packet handoff template

Every worker receives: objective, owned files, non-goals, confirmed root cause,
likely pitfalls, acceptance rows, narrow commands, rollback boundary, and this
return format:

- outcome and exact files changed;
- issue/root cause/resolution/evidence;
- tests and observed counts;
- remaining holds;
- exact commit/tree and source binding;
- no release/professional-approval claim.

## 10. Non-goals and parking lot

Do not add these while repairing input safety:

- new IS 456 formulas, member families, wind/seismic analysis, or soil design;
- a generic all-elements mega-schema;
- automatic unit guessing or AI-assisted header inference in the trusted path;
- database/Redis/job persistence unrelated to input/result truth;
- UI redesign, visualization enhancements, performance tuning, or broad
  refactors;
- branch/worktree cleanup, issue closure, dependency upgrades, or release
  execution;
- rewriting historical `LIB-PRO-001` evidence;
- declaring the library professionally approved because software tests pass.

Potential enhancements such as interactive mapping previews, richer import
diagnostics, or additional adapters enter the backlog only after the canonical
ledger and blocking rules are accepted.

## 11. G0 acceptance record and exact next step

G0 has now frozen:

- the bounded interpretation of the one-storey pilot;
- six root causes and an outcome-changing issue register;
- canonical input, import-ledger, result, and compatibility contracts;
- Alpha/stable/whole-building release boundaries;
- an eight-packet dependency order and cumulative test cadence.

The exact next implementation packet is `LIB-PRO-002-A`: strict service intake.
It starts only in a fresh source-bound lane from the then-fetched `origin/main`.
Its first change is the table-driven Section 7 service contract plus a
calculation-call spy; behavior then changes until those tests pass. It must not
edit import adapters, FastAPI/React transports, release automation, or generated
indexes except in its own final closeout.

Until Packet G is accepted, the release state is:

`NEXT_PUBLICATION = HOLD_INPUT_AND_RELEASE_TRUTH`
