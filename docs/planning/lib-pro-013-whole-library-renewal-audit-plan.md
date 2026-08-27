---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: spec
complexity: advanced
tags: [professional-readiness, whole-library, audit, usability, governance, efficiency]
---

# LIB-PRO-013 Whole-Library Professional Renewal Audit Plan

## 1. Decision and intended outcome

LIB-PRO-013 is the master plan for a fresh, evidence-bound review of the whole
library and its development system. It broadens the external-user work in
[LIB-PRO-011](../verification/lib-pro-011-external-api-readiness-audit.md) and
[LIB-PRO-012](lib-pro-012-external-api-remediation-plan.md) without replacing
their finding and implementation authority.

The outcome is not another general score or a promise that the library is
"perfect." The outcome is a complete, prioritized renewal portfolio in which:

1. every advertised user journey is safe, discoverable, and replayed from the
   installed artifact;
2. every engineering claim has an explicit supported-case and evidence basis;
3. package, API, result, error, documentation, and release contracts agree;
4. active code, compatibility, generated evidence, retained history, and local
   protected data have unambiguous owners and dispositions;
5. tests and gates prove user outcomes rather than only repository health;
6. agents, skills, automations, Git, CI, and documentation reduce repeated work
   without weakening structural-engineering or release controls; and
7. the final decision is `READY`, `PARTIAL`, or `HOLD` on an exact artifact,
   with unresolved findings visible and decisive.

This document is a planning authority only. It does not authorize formula
changes, public signature breaks, deletion, branch or worktree cleanup,
dependency additions, release, publication, or professional approval.

## 2. Relationship to immediate safety work

The whole-library audit must not become a reason to leave known fail-open
behavior in place.

- LIB-PRO-011 remains the evidence authority for reproduced invalid-input,
  downstream-propagation, API-consistency, discovery, and release-truth gaps.
- LIB-PRO-012 remains the implementation authority for immediate fail-closed
  safety, a curated family facade, compatibility, input/result/error contracts,
  examples, and advertised-surface gates.
- LIB-PRO-013 adds the audit lanes that LIB-PRO-012 intentionally does not own:
  engineering-evidence quality, all product transports, package and dependency
  policy, test architecture, performance, security, Git/CI/release operations,
  agents and skills, automation efficiency, historical material, and
  professional support.

After separate implementation authorization, LIB-PRO-012 Packets A and B may
proceed before the broader audit finishes because they close already-reproduced
P0 outcomes. Shared validation, facade, result, manifest, generated API, and
documentation owners remain single-writer surfaces.

## 3. Bound current baseline

The following is a planning snapshot, not a timeless repository claim. Every
audit packet must refresh the facts it consumes and bind them to an exact
commit, tree, artifact, dependency environment, and observation time.

| Surface | Observed planning baseline |
|---|---|
| Git lane | `codex/lib-pro-012-external-api-remediation-plan` at `0dd9d27b`; clean, five commits ahead of local `origin/main`, no upstream, remote freshness `NOT_CHECKED` |
| Worktrees | 15 retained worktrees including the current checkout; one detached lane is dirty and must be preserved |
| Public artifact | `structural-lib-is456==0.24.0a1`; LIB-PRO-011 binds the public wheel hash and tag |
| Product status | Alpha and qualified-review-required; stable, engineering-use, and professional-approval claims remain held |
| Product planes | Python package, CLI/batch/import/export, FastAPI REST/WebSocket/streaming, React workbench, Excel/ETABS integration |
| Python public root | 222 exports, including 100 functions in the LIB-PRO-011 inventory |
| Compatibility | 45 classified root stub modules, 620 facade projections, and 1,506 caller records in the current compatibility ledger |
| Code size signals | 247 Python package modules, 100 FastAPI Python modules, and 187 React source files |
| Test files | 226 Python, 43 FastAPI, and 52 React test files |
| Repository control | 115 active operations and 101/101 registered top-level scripts; current control validation passes |
| Agent system | 16 registered roles and 14 checked-in skill entrypoints |
| CI | Four executable workflows: PR validation, weekly verification, publication, and documentation deployment |
| Documentation | 1,195 tracked documentation files, including 334 verification files and 37 planning files |
| Package identity | Distribution `structural-lib-is456`, import namespace `structural_lib`, repository `structural_engineering_lib` |
| Python dependencies | Pydantic is the sole required runtime dependency; optional extras and development dependencies expand the supported matrix |
| Preservation | Protected standards, local Excel/VBA evidence, worktrees, archives, generated artifacts, and recovery data have separate retention rules |

### 3.1 Starting evidence carried into the audit

These are not substitutes for the complete audit, but they prevent the work
from pretending that known defects are merely hypotheses.

| Evidence | Current disposition |
|---|---|
| Invalid beam, detailing, BBS, torsion, structured-input, smart-analysis, compliance, column, and REST inputs can produce safe-looking or partial outputs | Confirmed in LIB-PRO-011; P0/P1 remediation owned by LIB-PRO-012 |
| Advertised Python routes and gated routes are different sets | Confirmed root cause; generate the gate from advertised workflow ownership |
| The published `0.24.0a1` identity conflicts with active-looking unpublished-candidate prose | Confirmed in LIB-PRO-011; live artifact identity must decide the correction |
| The root namespace mixes canonical, advanced, compatibility, and held functions | Confirmed inventory; curate the recommended facade without destructive root shrinkage |
| `Python/tests/README.md` describes 59 files and old direct pytest commands while the live suite has 226 files | Confirmed documentation drift; audit test documentation and command ownership |
| `fastapi_app/tests/README.md` still points to a direct `.venv/bin/pytest` path | Confirmed instruction drift; use the worktree-bound runtime contract |
| Historical planning text contains older control-plane counts while the live authority reports 115/101 | Expected historical drift; never treat retained prose counts as current authority |
| Green control, context, health, or CI checks do not prove fail-closed external behavior | Confirmed by simultaneous green controls and LIB-PRO-011 reproductions |
| Detached and dirty worktrees, archives, and ignored protected data exist | Preservation constraint, not cleanup authorization |

## 4. Why earlier audits missed or underweighted these issues

The audit-of-audits lane must validate each cause against exact earlier reports,
but the current evidence already establishes the following systemic patterns.

### 4.1 Repository success was used as a proxy for installed-user success

Source-tree tests, import checks, route counts, coverage, and internal workflow
evidence can all pass while the published wheel exposes a different import,
dependency, signature, example, or validation experience. Earlier work already
named this pattern `Repo != Installed`, but it was not made a decisive rule for
every promoted workflow.

### 4.2 Audits counted guards and routes instead of proving full contracts

A function can call a finite validator and still omit sign, range, relation,
identity, enum, collection, topology, or downstream-consumability rules. The
static validation audit truthfully reported hundreds of `UNPROVEN` fields, but
the release decision did not require every advertised route to resolve them.

### 4.3 Hand-maintained test lists did not follow advertising automatically

The frozen public-route regression list was useful but incomplete. New and
compatibility workflows could be promoted in README or API documentation
without automatically entering the negative-input and exact-wheel matrices.

### 4.4 Compatibility classification was mistaken for lower user obligation

If a compatibility function remains publicly advertised, users reasonably
treat it as supported. Internal labels such as `compatibility` or `advanced`
do not reduce its safety, error, documentation, or migration obligations.

### 4.5 Aggregate scores obscured decisive unresolved outcomes

Large passing test counts, high coverage, capability breadth, and an A/A+
score can coexist with one route that returns `OK` from invalid structural
actions. A single safe-looking P0 outcome must override an aggregate score.

### 4.6 The API grew in generations rather than from one frozen user contract

Low-level helpers, early service functions, typed INDIA-family requests,
compatibility stubs, REST v1 models, CLI contracts, and UI adapters evolved at
different times. Each generation solved a local need, leaving mixed naming,
defaults, status types, enum discovery, validation, and composition.

### 4.7 Documentation and task status were maintained as prose snapshots

Counts, versions, commands, file layouts, and task states drift when they are
copied into several active-looking documents. One-time folder or agent audits
cannot prevent later drift unless claims are generated, artifact-bound, or
assigned an event-driven owner.

### 4.8 Test breadth was not always evidence independence

Regression vectors generated from the implementation under test are useful for
change detection but are not independent engineering validation. Generated
checks, broad coverage, and parity between wrappers can repeat the same wrong
assumption.

### 4.9 Audit completion and recurrence prevention were separated

Past audits often fixed the found list but did not always convert the discovery
method into a generated, recurring gate. The same class could therefore return
through a new route, nested input, downstream consumer, or documentation path.

### 4.10 Tooling accumulated faster than authority and retirement rules

Agents, skills, scripts, prompts, indexes, checks, and workflow helpers were
added to solve real problems. Later maintenance consolidated much of this into
the current control plane, but historical copies and old usage guidance remain
an audit risk unless current callers and authority are checked rather than
inferred from filenames.

## 5. Audit principles

1. **User outcome first.** A finding matters when it changes safety,
   correctness, traceability, usability, reproducibility, installation,
   support, or the main development/release process.
2. **Artifact before source claim.** Bind package observations to the exact
   wheel/sdist/tag and application observations to an exact source head.
3. **Invalid intake is not engineering failure.** Invalid requests raise one
   structured contract error; valid inadequate designs return typed `FAIL` or
   `HOLD`; internal/numerical failures stay distinct.
4. **Promoted means supported.** Any workflow advertised in maintained public
   documentation enters the contract, example, negative-input, and artifact
   matrices regardless of its internal classification.
5. **Current authority beats retained history.** Query live registries and
   generators; retain old evidence without using its counts as current truth.
6. **Preserve before disposition.** No file, branch, worktree, source,
   generated artifact, or archive is removed merely because it looks old.
7. **Root cause, not symptom count.** Duplicate manifestations share one cause
   and one systemic prevention measure, while retaining their route evidence.
8. **Independent evidence stays separate.** Wrapper parity, generated vectors,
   blind internal recomputation, external benchmark, and qualified review are
   distinct evidence classes.
9. **No hidden engineering convenience.** Defaults and builders may reduce
   syntax but may not invent topology, restraint, material, load basis, code
   edition, or approval evidence.
10. **One writer on shared truth.** Read-only research may run in parallel;
    validation, facade, result, manifest, generated API, task, and session
    owners are changed serially.

## 6. Evidence model and finding schema

### 6.1 Evidence states

Every audit statement uses one of these states:

| State | Meaning |
|---|---|
| `CONFIRMED` | Exact current code, configuration, documentation, or artifact evidence proves the statement |
| `REPRODUCED` | A bound invocation produces the stated outcome |
| `OBSERVED` | A current inventory fact is recorded but is not itself a defect |
| `HYPOTHESIS` | Plausible risk requiring a specified audit method |
| `HELD` | Decision or claim intentionally blocked pending authority/evidence |
| `NOT_APPLICABLE` | Audited dimension does not apply, with a reason |
| `SUPERSEDED` | Earlier statement is retained but replaced by an identified current authority |

`PASS`, `FAIL`, and `HOLD` remain engineering/result states and must not be
confused with these evidence states.

### 6.2 Required finding record

Each finding must contain:

- stable ID, domain, priority, and evidence state;
- exact artifact/head/environment identity;
- advertised user or operator journey;
- input, command, or reproduction fixture;
- expected contract and observed outcome;
- main-process impact and affected consumers;
- confirmed root cause or explicitly `unconfirmed`;
- current authority and owner paths;
- solution class, compatibility impact, and dependency order;
- focused regression and cumulative gate;
- source/provenance and review boundary;
- disposition: `FIX_NOW`, `PLAN`, `KEEP`, `CONSOLIDATE`, `MIGRATE`, `RETIRE`,
  `ACCEPT_WITH_LIMIT`, or `HOLD`.

No finding is closed by a prose claim alone. It needs a bound correction and
evidence that the user outcome changed.

## 7. Complete audit universe

The register below is the coverage checklist. A final audit cannot be declared
complete while a row lacks an owner, method, evidence artifact, and disposition.

| Domain | Required questions | Primary evidence and completion signal |
|---|---|---|
| Product purpose and personas | Who is the package for: library author, careful engineer, junior user, integrator, reviewer, or application operator? Which claims are credible for each? | Persona/journey matrix; no unsupported "ready" or professional-use wording |
| Supported engineering scope | Which members, code editions, cases, limits, and assumptions are implemented, held, or unsupported? | Capability and source-provenance reconciliation; unsupported cases fail closed |
| Formula and numerical evidence | Which claims have independent arithmetic, benchmark, sensitivity, limits, and qualified review? | Evidence-class matrix; generated parity never presented as independent proof |
| Public Python facade | Which imports are recommended, advanced, compatible, held, or internal? | 100% classified exports; curated beginner facade and explicit expert routes |
| Signatures and naming | Are units, identity, actions, axes, sign convention, optionality, positional use, aliases, and defaults predictable? | Installed-wheel signature inventory with one decision per field |
| Input construction | Can users discover enums, nested evidence, allowed values, builders, and templates without reading owner modules? | First-use fixtures and introspection tests for every promoted family |
| Validation | Are type, finite, range, relation, material, topology, identity, collection, and consumer rules complete and recursive? | Generated adversarial matrix for every public field and route |
| Errors and statuses | Can callers distinguish invalid intake, unsupported scope, `FAIL`, `HOLD`, non-convergence, and defect without parsing text? | Stable exception/issue codes and typed result-state tests |
| Results and provenance | Are result types finite, serializable, traceable, reviewable, and consistent across families? | Common result protocol and family-specific payload registry |
| Composition and downstream artifacts | Can design flow safely into detailing, BBS, reports, CAD, optimization, and quantities? | Invalid upstream state cannot produce a success artifact; identity survives the chain |
| CLI and batch | Do strict intake, stderr/stdout, exit codes, partial failures, reproducibility, and examples match Python? | Source-free job fixtures and machine-readable failure tests |
| FastAPI, WebSocket, and streaming | Do request strictness, versions, errors, statuses, defaults, and timeouts match canonical contracts? | OpenAPI-bound positive/negative route matrix and transport parity |
| Generated clients | Are schemas, package versions, enum discoverability, optionality, and error models usable? | Generated-client compile/import/run test against the exact API artifact |
| React workbench | Does UI prevent invalid intake, expose assumptions/status, handle failures, and match canonical quantities/results? | Browser journey matrix with API and artifact identity |
| Excel and ETABS | Are installed Windows behavior, import mappings, units, provenance, error handling, and write-back boundaries explicit? | Separate Windows evidence lane; no Mac-only inference |
| Reports, BBS, CAD, and exports | Are units, identities, statuses, totals, templates, and optional dependencies correct? | Exact artifact/fixture comparison and optional-extra install tests |
| Distribution/import/repository names | Is the `structural-lib-is456` / `structural_lib` / `structural_engineering_lib` distinction clear and searchable? | Naming decision with migration/SEO/install examples; rename only if benefit exceeds compatibility cost |
| Packaging and installation | Do wheel, sdist, editable, source-free, extras, Python/OS, and offline/Colab paths behave as claimed? | Clean install matrix; wheel and sdist contents/provenance verified |
| Versions and release truth | Do metadata, runtime, docs, API, clients, tag, assets, and PyPI agree? | One artifact-identity record and zero contradictory active claims |
| Dependencies | Why is each runtime/dev/optional/Node/system dependency present, pinned, supported, and owned? | Dependency purpose/support/security/license/update matrix |
| Runtime and platforms | Are Python, Node, browser, macOS, Windows, Docker/Colima, and architecture constraints explicit? | Supported environment matrix with tested and untested states |
| Architecture and ownership | Are Core <- IS 456 <- Services <- UI imports, formula ownership, and transport boundaries intact? | Caller-aware import graph; no upward calculation dependency |
| Data models and serialization | Are schemas versioned, finite, lossless, backward compatible, and migration-safe? | Round-trip/property tests and versioned migration fixtures |
| Compatibility and deprecation | Does every shim delegate, warn, name a replacement, and have a time/version policy? | Compatibility ledger with no independent formula path or orphan caller |
| Tests and fixtures | Are categories, markers, commands, ownership, isolation, determinism, and documentation current? | Live test inventory reconciled with READMEs and workflow callers |
| Engineering benchmark independence | Which golden fixtures come from standards, independent calculations, external software, or runtime generation? | Fixture provenance ledger and reviewer status per benchmark |
| Performance and resource use | Are import time, single/batch latency, memory, frontend rendering, API load, and large reports bounded? | Reproducible baselines with outcome-linked thresholds |
| Numerical robustness | Are overflow, underflow, `NaN`, infinities, convergence, rounding, tolerances, and serialization controlled? | Boundary/property matrix with explicit numerical-failure semantics |
| Security and privacy | Are auth, rate limits, input sizes, error leakage, secrets, logs, local files, and user data handled safely? | Threat-bound checks; findings limited to outcome-changing exposure |
| Supply chain and licensing | Are actions, images, packages, hashes, attestations, licenses, and vulnerability ownership credible? | Artifact/dependency provenance and response policy |
| Documentation and examples | Can a stranger install, choose a family, enter a valid case, interpret status, and find limits quickly? | Exact-wheel executable quickstart/cookbook and generated signatures |
| Accessibility and international use | Are keyboard, contrast, units, terminology, errors, and export readability usable by intended users? | Bounded accessibility/usability review; no claim beyond tested scope |
| Support and professional policy | Are issue templates, vulnerability reporting, deprecation, support versions, incident correction, citation, and disclaimer coherent? | Published policy matrix with realistic owner commitments |
| Git and worktrees | Are branch, upstream, active candidates, merge order, retained state, and cleanup authorization safe? | Live Git authority, predecessor comparison, and recovery-bound disposition |
| CI, hooks, and release workflows | Do changed-path routing, local checks, hosted gates, exact artifact tests, and publication authorization prove the right outcomes efficiently? | Caller-based domain map; unknown paths fail closed; no redundant broad run |
| Agents and instructions | Do AGENTS, platform entries, roles, prompts, permissions, and path rules compose without drift? | Authority map and semantic validation; no copied competing policy |
| Skills | Are all skills current, invoked for real workflows, bounded, testable, and worth their context/maintenance cost? | Use/caller/outcome inventory with KEEP/REPAIR/CONSOLIDATE/RETIRE disposition |
| Automations and tools | Do control-plane operations, aliases, scripts, sessions, pipelines, evolution, and generated projections have one owner and live caller? | 100% registered/current operations; no phantom or competing command authority |
| AI efficiency | Are model selection, delegation, context, evidence reuse, gate cadence, and timing reducing rework without skipping safety? | Task-level time/retry/rework evidence and policy conformance |
| Old, archived, generated, and local data | Is each surface authoritative, generated, historical, protected, recoverable, or disposable? | Preservation-first manifest with source, callers, size, backup, and authorized disposition |
| Early-project decisions and dead paths | Which assumptions were correct then but are unsuitable now: API growth, Streamlit, stubs, duplicated docs, package names, scripts, defaults? | Decision archaeology with current impact; no blame and no blind deletion |
| Peer comparison | Which professional practices should be adopted, adapted, or rejected for this product? | Source-backed comparison tied to an identified local outcome |

## 8. Peer-library and professional-practice baseline

Peer comparison is a design input, not a popularity contest. Structural analysis
systems, section-analysis tools, numerical libraries, and safety-sensitive
member-design software have different contracts.

| Source-backed pattern | Local decision to test |
|---|---|
| [NumPy public module structure](https://numpy.org/doc/stable/reference/module_structure.html) distinguishes recommended and legacy namespaces | Keep a small recommended facade and label expert/compatibility locations explicitly |
| [NumPy downstream guidance](https://numpy.org/doc/1.26/dev/depending_on_numpy.html) uses explicit version/deprecation policy | Give each public compatibility route a warning, replacement, and earliest removal policy |
| [NumPy testing guidance](https://numpy.org/doc/2.0/reference/testing.html) treats bad-input and bug-regression tests as core | Convert every confirmed defect into a route- and artifact-bound regression |
| [PyPA packaging flow](https://packaging.python.org/en/latest/flow/) distinguishes source distributions and wheels | Test the artifacts users install, not only the source checkout |
| [Pint dimensional checking](https://pint.readthedocs.io/en/latest/advanced/wrapping.html) proves dimension-aware boundary validation | Keep explicit suffix units now; assess an optional quantity adapter only with a demonstrated benefit and serialization/provenance plan |
| [Hypothesis](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html) complements examples with properties | Add finite, round-trip, equivalence, monotonicity, and validation invariants where engineering meaning supports them |
| [StructuralCodes architecture](https://fib-international.github.io/structuralcodes/api/library_structure.html) separates equations, materials, geometry, and calculators | Test the existing four-layer rule and prevent ambient code-selection state |
| [StructuralCodes section results](https://fib-international.github.io/structuralcodes/usage/sections/index.html) pair typed results with theory and conventions | Pair family results with assumptions, sign conventions, provenance, and limitations |
| [concreteproperties API](https://concrete-properties.readthedocs.io/en/latest/api.html) groups APIs by engineering concept and returns analysis-specific results | Prefer family-oriented discoverability over one root namespace containing every helper |
| [anaStruct examples](https://anastruct.readthedocs.io/en/latest/examples.html) and [OpenSeesPy documentation](https://openseespydoc.readthedocs.io/en/latest/) offer short modelling journeys | Learn from their discovery, but do not copy mutable global state or numerical defaults into safety-sensitive design intake |

The detailed comparison packet must add release/support/security documentation,
measure comparable first-use journeys, and state where a peer is not a valid
template. No dependency or API style is adopted merely because another library
uses it.

## 9. Work programme

### Track 0 — truth freeze and audit authority

#### Packet G0 — exact baseline and preservation freeze

**Objective:** bind the audit to the correct source, artifacts, current
authorities, active candidates, dependencies, and retained data.

**Work:**

- record exact Git head/tree, upstream, remote freshness, PR, worktrees, locks,
  and task-owned candidate ordering;
- bind public wheel/sdist/tag/hash and application source identity;
- inventory active authority, generated projections, archives, ignored/local
  preservation roots, and recovery status;
- query live control, context, agent, skill, API, capability, workflow, and test
  owners instead of copying historical counts; and
- freeze one audit scope and finding schema.

**Acceptance:** every later finding names its source/artifact identity; no
destructive operation is authorized; ambiguous identity stops the affected
packet.

#### Packet G1 — audit-of-audits and recurrence analysis

**Objective:** explain what earlier audits proved, what they did not test, why
later external use found additional defects, and which recurrence control was
missing.

**Work:** build a matrix of prior audit, artifact, claimed scope, methods,
completion rule, decisive vs advisory findings, later counterexample, root
cause, and prevention. Include professional-library, input-safety, folder,
agent/efficiency, control-plane, release, and external-user audits.

**Acceptance:** each known LIB-PRO-011 issue maps to the exact mechanism that
missed it and a recurring prevention gate; no earlier result is rewritten or
mocked for exceeding its original scope.

### Track 1 — external-user safety and API product

#### Packet U1 — package identity and first-30-minute journeys

Audit installation, import naming, version truth, quickstart, discovery,
capabilities, first valid result, first invalid result, help, and upgrade path
for a new developer and a careful structural engineer.

**Acceptance:** a clean environment can select the correct artifact and finish
each promoted starter journey without repository source, guessed enums, or
message-text parsing.

#### Packet U2 — complete public contract and signature census

Extend the existing API classification and compatibility ledger with import
path, signature, keyword policy, unit, field meaning, allowed range, sign/axis,
default policy, input/result/error types, stability, replacement, example, and
artifact-test ownership for every promoted route.

**Acceptance:** 100% of promoted Python functions and request-object fields
have a decision; no third API manifest is invented.

#### Packet U3 — validation, errors, results, and composition

Replay the declarative adversarial matrix across canonical, advanced,
compatibility, nested, direct, and downstream routes. Trace design through
detailing, BBS, reports, CAD, quantities, and optimization.

**Acceptance:** invalid intake never creates a calculation or artifact;
engineering `FAIL`/`HOLD` remains a normal typed result; numerical/internal
failure is distinct and finite-serializable.

**Implementation relationship:** known corrections remain LIB-PRO-012 Packets
A-E. This packet discovers additional routes and verifies systemic closure.

#### Packet U4 — family construction and documentation usability

Audit beam, torsion, column, slabs, wall, staircase, deep beam, flat slab, and
footing families for exact enums, evidence fields, builders, examples,
assumptions, status interpretation, and next-step guidance.

**Acceptance:** one exact-wheel executable recipe per promoted family; builders
group evidence without guessing it; errors list valid choices and field paths.

### Track 2 — engineering truth and evidence

#### Packet E1 — supported-case and source-provenance reconciliation

Reconcile capabilities, code editions, clauses/tables/figures, normalized data,
applicability, assumptions, unsupported cases, qualified-review flags, and
public wording.

**Acceptance:** every calculation claim is `SUPPORTED`, `BOUNDED`, `HELD`, or
`UNSUPPORTED` with source/evidence identity; no protected prose or source image
is copied.

#### Packet E2 — benchmark independence and numerical robustness

Classify fixtures as independent arithmetic, source example, external-software
comparison, blind internal recomputation, wrapper parity, generated regression,
or UI projection. Audit tolerances, discontinuities, extremes, convergence,
rounding, and finite serialization.

**Acceptance:** every promoted engineering workflow has the evidence classes
required for its claim; no generated parity is represented as independent
validation; boundary behavior has explicit semantics.

#### Packet E3 — qualified review and professional-use boundary

Define what must be reviewed by a practicing structural engineer, what can be
released as Alpha, what remains diagnostic, and what evidence a stable or
engineering-use claim would require.

**Acceptance:** software acceptance, benchmark replay, qualified review,
publication, and professional approval remain separate decisions.

### Track 3 — application and transport parity

#### Packet P1 — CLI, batch, import, and export chain

Audit file schemas, unit mapping, partial failures, exit codes, stdout/stderr,
identity, reproducibility, ETABS/SAFE/STAAD adapters, reports, BBS, DXF/PDF, and
optional extras.

**Acceptance:** source-free fixtures prove each promoted chain and invalid rows
cannot silently create partial-success deliverables.

#### Packet P2 — REST, WebSocket, OpenAPI, and generated clients

Inventory every operation, request, response, default, error, status, version,
client generator, and deprecation route against canonical Python ownership.

**Acceptance:** promoted transports preserve validation, identity, status,
provenance, and finite serialization; the OpenAPI/client build is exact-head
and drift-controlled.

#### Packet P3 — React workbench and installed desktop/browser journey

Test import, input, design, 3D review, status, dashboard, error recovery, and
exports with keyboard/accessibility and large-batch behavior in scope.

**Acceptance:** UI values match the bound API result; no invalid or held result
is presented as approved; browser evidence records exact build and dataset.

#### Packet P4 — Excel and ETABS installed evidence

Keep Windows Excel/ETABS as a separate evidence lane. Audit UDF/add-in names,
units, selected-table imports, error cells, refresh/write-back behavior, and
evidence identity.

**Acceptance:** installed Windows evidence or an explicit `NOT_TESTED` state;
Mac/source tests cannot silently satisfy this lane.

### Track 4 — package and repository professionalism

#### Packet R1 — packaging, dependencies, runtime, and supply chain

Inventory Python runtime/dev/optional dependencies, Node dependencies, system
tools, images, actions, licenses, vulnerabilities, version bounds, update
owners, import cost, extras, wheel/sdist contents, and supported platforms.

**Acceptance:** each dependency has a purpose and owner; supported combinations
are tested or explicitly untested; artifact provenance and vulnerability
response are defined. Adding Pint or another major dependency requires a
separate benefit/cost decision.

#### Packet R2 — architecture, data, compatibility, and generated surfaces

Build a caller-aware import/ownership graph; audit formula placement,
serialization schemas, migrations, root stubs, manifests, OpenAPI baseline,
generated clients, workbooks, and source hashes.

**Acceptance:** architecture direction passes, wrappers are formula-free
delegates, every generated artifact names its source/generator/verification,
and no public caller is orphaned.

#### Packet R3 — test architecture and evidence gates

Reconcile test files, markers, READMEs, fixtures, property tests, golden tests,
benchmarks, FastAPI, React, browser, wheel, Windows, Docker, and release tests
with maintained callers and advertised workflows.

**Acceptance:** one current test taxonomy and command owner; every promoted
workflow has applicable unit, boundary, property, benchmark, compatibility,
transport, and artifact evidence; duplicate tests are consolidated only after
proving they do not own distinct outcomes.

#### Packet R4 — documentation, discovery, support, and naming

Audit README, quickstarts, API docs, cookbooks, architecture, task/status docs,
examples, changelog, citation, contribution, security reporting, support
versions, package/import/repository names, searchability, and accessibility.

**Acceptance:** active docs agree with live authorities and artifacts; generated
facts are generated; retained snapshots are clearly historical; a stranger can
find the supported path and limitations quickly.

#### Packet R5 — Git, worktrees, CI, hooks, release, and recovery

Audit current Git authority, candidate ordering, branch/upstream rules,
worktrees, hooks, changed-path mapping, receipt reuse, hosted checks, TestPyPI,
publication authorization, artifact identity, rollback/revocation, and backup
recovery.

**Acceptance:** no clean-tree shortcut; unknown impact fails closed; one frozen
candidate receives one appropriate local/hosted sequence; deletion remains
separately authorized and recovery-proven.

### Track 5 — agent system, automation, and retained history

#### Packet A1 — AGENTS, platform instructions, roles, prompts, and permissions

Audit semantic composition and live use of `AGENTS.md`, platform entrypoints,
path-scoped rules, the agent registry, prompts, role documents, and permission
enforcement.

**Acceptance:** one owner per policy class, no weaker copy, registry metadata
matches live entrypoints, and permissions fail closed.

#### Packet A2 — skills, control plane, scripts, automations, and evolution

For every active skill and operation, record purpose, caller, inputs, outputs,
permission, replacement/deprecation state, execution evidence, maintenance
cost, and user outcome. Audit session, pipeline, routing, tool discovery,
feedback, evolution, and generated compatibility projections.

**Acceptance:** every active entry has a real caller or documented operator
journey; phantom/duplicate paths are proposed for later disposition; the live
control registry remains the command authority.

#### Packet A3 — AI and verification efficiency

Measure orientation time, context loaded, agent fan-out, candidate count,
focused retries, broad runs, hosted runs, rework, and network wait for sampled
tasks. Trace whether each gate prevented a real recurrence or merely repeated
unchanged work.

**Acceptance:** recommendations retain all outcome-changing gates while reducing
repeated discovery, broad reruns, copied context, concurrent writers, and stale
status work. Provider token/cost claims use provider evidence only.

#### Packet A4 — archives, old data, early decisions, and retention

Classify tracked archives, legacy code, historical agent material, generated
evidence, caches/builds, vendor references, ignored local data, protected
standards, branches, refs, and worktrees by authority, caller, provenance,
size, recovery, and legal/source boundary.

**Acceptance:** a `KEEP`, `MOVE`, `CONSOLIDATE`, `RETIRE`, or `HOLD` proposal
for each reviewed class. No move/delete occurs in this packet. Early decisions
are judged against current impact, not blamed retrospectively.

### Track 6 — external comparison and synthesis

#### Packet C1 — peer and professional-practice comparison

Deepen the baseline in section 8 with official sources, comparable journey
tests, and a local fit/cost analysis. Include scientific Python, structural
analysis/design peers, packaging, documentation, security, accessibility, and
support policy.

**Acceptance:** every recommended adoption names a local finding, benefit,
compatibility/dependency cost, owner, and gate; inapplicable peer patterns are
explicitly rejected.

#### Packet C2 — cumulative finding and solution portfolio

Deduplicate findings by root cause, retain route-level evidence, prioritize by
safety/user outcome, and map each to `FIX_NOW`, planned migration, retained
limit, or held decision.

**Acceptance:** no unresolved P0; every P1/P2 has an owner, dependency, effort
class, compatibility plan, and acceptance evidence; the portfolio does not
silently expand supported engineering scope.

#### Packet C3 — exact-artifact independent audit decision

Freeze the integrated candidate, run the complete applicable evidence matrix,
and obtain an independent read-only audit before hosted publication gates.

**Acceptance:** one exact-head/artifact verdict. `PARTIAL` or `HOLD` exits
non-success for professional/stable claims. Publication authorization and
qualified engineering review remain separate.

## 10. Dependency order and parallelism

```text
G0 exact truth freeze
  -> G1 audit-of-audits
  -> U1/U2 + E1 + R1/R2 + A1/A2/A4 + C1 (read-only lanes)
  -> U3/U4 + E2/E3 + P1/P2/P3/P4 + R3/R4/R5 + A3
  -> C2 integrated remediation portfolio
  -> separately authorized implementation packets
  -> C3 exact-artifact independent audit
  -> separately authorized release / qualified-review decisions
```

Rules:

- use at most two concurrent bounded research/review agents plus the parent,
  following the repository limit;
- pass compact task packets, never full conversation history;
- keep read-only inventories disjoint and return file/source evidence rather
  than raw logs;
- one parent writer owns task/status/session and cumulative evidence;
- never parallel-write `core/validation.py`, service API/facade owners, common
  results/errors, API classification/compatibility, workflow catalog, OpenAPI
  baseline/client output, planning index, task board, or session log; and
- stop if an active candidate overlaps shared generated owners until merge
  ordering is reconciled.

## 11. Efficiency controls

1. Start each packet from the G0 evidence bundle; refresh only drift-prone facts.
2. Use `git_state.py`, the control registry, context manifest, API
   classification, compatibility ledger, workflow catalog, verification plan,
   and package metadata as maintained owners.
3. Run targeted inventories and reproducers during audit; do not run broad
   suites to discover what a bounded command can answer.
4. Key reusable evidence by command, declared domain, source bytes, runtime,
   platform, dependencies, and verification contract.
5. Sample every route class, then expand automatically from the public contract
   inventory when a class fails; do not rely on hand-picked happy paths.
6. Deduplicate issues by root cause while preserving every affected journey.
7. Ignore cosmetic or speculative concerns that do not change a user or main
   development/release outcome.
8. Run focused checks together after a packet freezes, the quick gate once for
   its immutable candidate, and the broad/full matrix once at cumulative
   integration unless an outcome-changing repair invalidates it.
9. Record non-overlapping time for intake, research, implementation, audit,
   rework, local closeout, hosted wait, and merge verification.
10. Measure efficiency by avoided rework and correct outcomes, not by deleting
    controls or estimating provider tokens locally.

## 12. Durable audit outputs

The programme produces the following without creating competing authorities:

| Output | Owner/disposition |
|---|---|
| Whole-library finding register | One versioned LIB-PRO-013 evidence document with stable IDs and reproductions |
| Audit-of-audits matrix | Section/evidence attachment to the LIB-PRO-013 register |
| Public contract inventory | Extend existing API classification, compatibility ledger, and workflow catalogue |
| Advertised workflow inventory | Derived from maintained public docs and linked to existing workflow ownership |
| Engineering evidence-class matrix | Verification artifact cross-linking sources, fixtures, review, and limitations |
| Package/dependency/platform matrix | Versioned evidence tied to package and lock authorities |
| Test/evidence architecture | Maintained testing guide plus generated live counts/commands |
| Retention/disposition proposal | Preservation-first manifest; no destructive action |
| Peer comparison | Source-backed evidence attachment with adopt/adapt/reject decisions |
| Remediation portfolio | Dependency-ordered successor plan that incorporates rather than duplicates LIB-PRO-012 |
| Cumulative verdict | Exact-head/artifact machine-readable evidence with `READY`, `PARTIAL`, or `HOLD` |

## 13. Severity and scheduling

| Priority | Meaning | Scheduling rule |
|---|---|---|
| P0 | Invalid or unsupported input can produce a safe-looking calculation/artifact, or engineering truth is materially wrong | Contain and repair before other product enhancement; no release readiness |
| P1 | Contract, identity, provenance, transport, install, or release behavior prevents dependable use | Own in the same renewal milestone before outsider/stability claim |
| P2 | Material discoverability, consistency, documentation, performance, or maintenance defect | Plan with owner and gate; may follow P0/P1 if limitations are explicit |
| P3 | Improvement without a demonstrated main-process outcome | Exclude or park outside this programme |

The initial audit is estimated at 15-24 engineer-days because it spans source,
installed artifacts, browser/application transports, Windows evidence,
governance, and external comparison. Known LIB-PRO-012 implementation remains
its separately estimated 44-73 engineer-days. Additional remediation is not
estimated until C2 has evidence; assigning a fixed whole-program duration now
would hide uncertainty rather than improve planning.

## 14. Programme gates

### Audit-completeness gate

- every section 7 domain has an owner, method, artifact, and disposition;
- every advertised journey appears in the public-contract and artifact matrix;
- every prior audit in scope is reconciled without overwriting history;
- every finding has exact identity, reproduction, impact, cause state,
  solution, and acceptance evidence; and
- no unresolved identity, preservation, or shared-owner ambiguity is hidden.

### Remediation-design gate

- all P0/P1 findings map to dependency-ordered packets;
- compatibility and migration are explicit for signature/result/error changes;
- dependencies are added only after benefit/cost/support review;
- documentation, tests, generated surfaces, and release controls are part of
  the same solution, not follow-up polish; and
- the supported engineering scope is unchanged unless separately approved.

### Candidate gate

- invalid public inputs fail closed across direct and composed routes;
- promoted family examples run from the built wheel;
- Python, CLI, REST/client, React, and applicable Excel evidence agree;
- benchmark and provenance requirements match the claim;
- focused, quick, full, hosted, package, security, documentation, and browser
  gates pass for the exact candidate as applicable; and
- compatibility wrappers delegate to the same canonical implementation.

### Professional/release gate

- no unresolved P0/P1 finding;
- `PARTIAL` is a non-success verdict for stable/professional claims;
- qualified review, release authorization, public artifact identity, support,
  and incident-response policy are independently satisfied; and
- no Alpha disclaimer is removed merely because software CI is green.

## 15. Stop conditions and non-goals

Stop and replan when:

- the source or installed artifact cannot be identified exactly;
- a packet overlaps an active unmerged candidate on shared owners;
- a proposed convenience default would invent engineering evidence;
- a signature migration lacks a valid-caller and compatibility inventory;
- an archive/data disposition lacks callers, provenance, and recovery proof;
- a dependency proposal lacks an owner and supported-version policy;
- a generated artifact lacks a discoverable source or rebuild path;
- a result would require protected source content to be copied; or
- professional/publication wording requires authority not yet granted.

Explicit non-goals for the audit phase:

- no new member family or design-code scope;
- no formula implementation or mass refactor;
- no signature rename, compatibility removal, or package rename;
- no dependency upgrade/addition;
- no branch, worktree, archive, source, cache, or data deletion;
- no release/tag/PyPI/GitHub publication;
- no replacement of qualified engineering review with automated evidence; and
- no rewrite of historical records merely because current counts differ.

## 16. Immediate next action after plan approval

Start LIB-PRO-013-G0 as a read-only exact-baseline packet and produce the
audit register skeleton plus prior-audit matrix. In parallel, prepare the
separately authorized LIB-PRO-012 Packet A implementation boundary so the
known beam/detailing/BBS P0 corrections are not delayed. Do not edit runtime
code until that implementation packet is explicitly started and its shared
owners are confirmed free.
