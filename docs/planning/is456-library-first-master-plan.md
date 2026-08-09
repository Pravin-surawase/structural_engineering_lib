---
task: LIB-IS456-V1
title: IS 456 Library-First Completion and PyPI Master Plan
status: active-closeout
owner: Main Agent and repository owner
created: 2026-08-09
last_updated: 2026-08-09
doc_type: spec
baseline_commit: d4eb9e9dda4a
release_decision: v0.21.7 deferred
target_version: v0.23.0 provisional
current_blocker: Run final product UAT and freeze exact artifact evidence
---

**Type:** Plan
**Audience:** All Agents
**Status:** In Progress
**Importance:** Critical
**Created:** 2026-08-09
**Last Updated:** 2026-08-09

---

# LIB-IS456-V1 — IS 456 Library-First Completion and PyPI Master Plan

## 1. Executive decision

The Python package is the product. FastAPI, React, command-line workflows,
reports, ETABS adapters, and future integrations are consumers of that product.

This program completes a bounded, publishable IS 456 reinforced-concrete core
before broad FastAPI or React feature work resumes. It does **not** claim to
implement every provision of IS 456 or every structural element covered by the
standard.

The target capability for this program is:

- beam analysis, design, checks, and detailing within the currently supported
  beam cases;
- column analysis, design, checks, and detailing within the currently supported
  rectangular/square and documented column cases;
- isolated square/rectangular concentric footing core, including the remaining
  dowel/bearing-transfer slice;
- solid one-way and two-way slab core for explicitly approved support and load
  cases;
- one stable, discoverable Python public API;
- explicit units, assumptions, limitations, source identity, and benchmark
  status at the public boundary;
- a clean wheel and source distribution suitable for PyPI;
- exact-artifact verification before and after publication.

The target is called **Supported IS 456 RC Core**, not “complete IS 456.” Walls,
stairs, deep beams, flat slabs, combined/strap/raft/pile-cap footings, specialist
structures, and other code families remain outside this program unless the
owner changes scope through a separate decision.

## 2. Relationship to current repository plans

This document is the immediate execution authority for the library-first IS 456
lane once activated by the owner.

It narrows the immediate IS 456 execution order in
`docs/planning/library-expansion-blueprint-v5.md`. It does not reverse that
document's code-first package architecture or decide later ACI/EC2 work.

The owner activated this plan on 2026-08-09 after the following sequence:

1. MAINT-008 Packet B was reviewed, repaired, and squash-merged as PR #691 at
   `056bfad77987ce513f6289fd0fee5068667d6f5d`.
2. v0.21.7 was explicitly deferred because its publication does not advance the
   library-first program and `clauses.json` remains under publication review.
3. `task/LIB-IS456-V1` was created from the exact merged main commit.
4. P1 and P2 began as read-only audits before calculation work.

No worker may mix library feature work into `task/MAINT-008-B`, merge PR #691,
publish v0.21.7, create tags, change GitHub settings, or close issues.

### 2.1 Post-remediation execution authority

The owner reconfirmed the finite completion horizon as the **bounded IS 456
product milestone**. This plan is the single active execution authority until
that milestone is frozen. The hierarchy is:

1. This plan controls the remaining bounded-product closeout.
2. `professional-library-remediation-plan.md` is a completed defect/evidence
   ledger; do not execute T0 or R1-R8 again.
3. `library-expansion-blueprint-v5.md` and architecture v0.24+ sections are
   future strategic roadmaps, not current execution authority.
4. `docs/TASKS.md` holds only the current packet and immediate successors.

The bounded milestone includes:

- the existing supported beam and rectangular/square column workflows;
- square/rectangular isolated-footing checks and bounded concentric
  bearing/dowel load transfer;
- the simply supported one-way slab strip;
- one interior, four-edge-continuous two-way flexure computation using
  explicitly accepted external coefficients;
- the stable Python facade and capability/semantic contract;
- thin maintained FastAPI consumers, truthful batch/report React behavior,
  and exact package/CLI evidence.

It explicitly excludes multi-code infrastructure, ACI 318, EC2, combined/
strap/raft/pile-cap footings, built-in protected two-way coefficient tables,
complete two-way strip/torsion/detailing design, flat slabs, and new slab React
feature work. Those items do not block this milestone and must not be pulled
into its closeout.

No qualified professional review is requested while implementation and
integration remain active. Until the final frozen-scope review is recorded,
the repository and every artifact remain development software that is not
approved or usable for engineering decisions.

### 2.2 Remaining closeout packets

| Packet | State | Objective | Exit condition |
|---|---|---|---|
| C0 — Plan truth | Complete | Reconcile active plans/tasks with the implemented bounded scope | One authority, no stale active v0.23 tasks, exact next packet |
| C1 — Git integration | Complete at `d4eb9e9d` | Checkpoint intended remediation/product lanes, preserve automation commit `f812eb3f`, and synchronize `origin/main` without rebase/reset/stash | Reviewable commits, clean worktree, no automation work lost |
| C2 — Final product UAT | Next | Exercise supported Python, FastAPI, React batch/report, footing/slab, and export paths including unsafe negatives | Source-tree and live consumer outcomes agree; all canonical gates green |
| C3 — Frozen artifact | After C2 | Build clean wheel/sdist, inspect contents, record hashes, clean-install supported workflows and CLI | Exact artifact evidence is reproducible and bound to the frozen commit |
| C4 — Evidence freeze | After C3 | Assemble source IDs, units, benchmarks, limitations, unsafe cases, and unresolved holds without requesting sign-off | Owner declares all intended bounded work complete and freezes the review scope |

Only after C0-C4 are complete does the final qualified-engineering review
begin. Merge, tag, TestPyPI/PyPI, GitHub Release, issue closure, and branch
deletion remain separate owner-only actions.

## 3. Why this plan exists

The original architecture direction was sound, but implementation and product
layers grew at the same time. The project now has strong code and test assets,
but several signals can be misread:

- a high parity score mainly demonstrates test, hook, and endpoint wiring;
- a large test count demonstrates software regression evidence, not complete
  engineering coverage;
- clause decorators and clause registries do not prove formula correctness;
- FastAPI and React coverage do not prove that the installed Python package has
  a coherent public contract;
- a source-checkout test does not prove that the built PyPI artifact works;
- existing benchmark material is not automatically independent or accepted
  engineering truth.

This plan repairs those boundaries without a rewrite and without adding a large
new process framework.

## 4. Current baseline

The 2026-08-09 read-only inventory established this starting point. Refresh the
facts at packet start if the baseline commit changes.

| Area | Current evidence | Program treatment |
|---|---|---|
| Architecture | Four-layer boundary scan reported 0 violations across 119 files; library import validation reported 0 broken internal imports | Preserve; rerun after cross-layer changes |
| Beam | Flexure, shear, torsion, detailing, deflection/crack serviceability implemented | Capability and evidence closure audit; no broad redesign |
| Column | Axial, uniaxial, biaxial, slender/long, helical, and detailing modules implemented | Publish the supported-case boundary; close only outcome-changing gaps |
| Footing | Isolated square/rectangular bearing, flexure, one-way shear, punching, and bearing enhancement implemented | Complete dowel/bearing-transfer slice; defer combined and other footing families |
| Slab | No dedicated `codes/is456/slab/` package | New bounded element program: types/classification, one-way, then two-way |
| Extended elements | Walls, stairs, and deep beams are planned/deferred | Excluded from LIB-IS456-V1 |
| Public library surface | Beam and column services exist; footing is exposed through broader services; compatibility shims exist | Audit and stabilize one intentional facade; no new duplicate shims |
| Package | `structural-lib-is456` v0.21.6 metadata; Python >=3.11; minimal base dependency; optional extras; wheel verification automation | Preserve the base dependency boundary; inspect distribution contents and claims |
| Release automation | Tag-only production PyPI, manual TestPyPI, OIDC, wheel build/install, SBOM | Reconcile docs, record exact hashes, add protected-content gate, verify exact public version |
| Source data | `clauses.json` is packaged and includes BIS-attributed `text` fields | Publication HOLD until owner/legal protected-content decision |

The parity dashboard's curated 15/17 clause-family result is useful as an
implementation navigation aid. It is not a whole-standard completion metric.

## 5. Program scope contract

### 5.1 Included library outcomes

#### Beam

- Preserve the existing beam subpackage as the canonical implementation.
- Publish a precise supported-case matrix for rectangular, doubly reinforced,
  flanged, shear, torsion, detailing, and serviceability behavior.
- Repair only confirmed gaps that change a supported main-process result.
- Retain compatibility shims only as delegating shims; no new math in shims.

#### Column

- Publish the exact geometry, reinforcement-layout, slenderness, load, and
  interaction assumptions supported by each public workflow.
- Preserve implemented short/long, axial/uniaxial/biaxial, helical, and
  detailing paths when source and benchmark evidence support the stated case.
- Do not silently expand to circular, asymmetric, arbitrary multilayer, or
  general interaction behavior when current functions exclude those cases.

#### Isolated footing

- Preserve square/rectangular isolated footing workflows for explicitly
  supported concentric/uniaxial loading.
- Add the approved dowel/bearing-transfer calculation slice.
- Preserve documented exclusions for combined, strap, raft, pile-cap, biaxial,
  lateral-stability, settlement, and geotechnical-design behavior.
- Do not extract a generic punching framework unless a separate owner decision
  and source-backed contract justify it.

#### Solid slabs

- Add slab types and validation before adding formulas.
- Add slab classification and the first supported one-way case.
- Add one-way coefficient, design, serviceability boundary, and detailing
  behavior only for approved cases.
- Add two-way coefficient and design behavior only after the one-way contract is
  stable and the relevant protected-table/source policy is approved.
- Keep flat slabs, drop panels, ribbed/waffle slabs, yield-line analysis,
  prestressed slabs, openings, irregular panels, and FEM behavior out of scope.

#### Public Python package

- Provide one canonical import path for every supported user workflow.
- Keep lower-level expert functions accessible only where intentional.
- Preserve a documented deprecation path for existing public compatibility
  imports.
- Keep FastAPI, React, filesystem access, environment access, and network access
  outside pure IS 456 calculations.
- Keep base installation dependencies minimal; optional features remain extras.

### 5.2 Explicit non-goals

- Literal whole-standard coverage.
- Exhaustive edge-case and adversarial test campaigns.
- A test-count or coverage-percentage target.
- React feature or visual-design work.
- Broad FastAPI endpoint expansion during calculation phases.
- Multi-code infrastructure, ACI 318, EC2, or new companion-code work.
- Rewriting stable beam or column modules for style consistency.
- Generic framework extraction that is not required by two completed callers.
- Performance optimization without a measured main-process blocker.
- Copying IS/SP clause wording, tables, figures, charts, scans, or protected
  source material into code, documentation, fixtures, or package data.
- Professional approval, certification, or a claim that the package replaces a
  qualified structural engineer.

## 6. Completion definitions

### 6.1 Function complete

A new or materially changed calculation is complete only when all of these are
recorded:

1. Exact user/calculation outcome in scope.
2. Design-code family, edition, amendment state, and clause/table/figure IDs.
3. Project-authored symbolic calculation and dimensional reasoning.
4. Inputs, outputs, and explicit units.
5. Supported domain and fail-closed unsupported conditions.
6. Independent benchmark source, inputs, expected result, and justified
   tolerance.
7. Pure implementation in the correct `codes/is456/<element>/` package.
8. One accepted benchmark test and the governing limit that changes the main
   result.
9. Intentional export/public-service decision.
10. Focused verification and architecture/import evidence.
11. Assumptions, limitations, and engineering-review status.

If the governing source, amendment impact, units, benchmark, or tolerance is
ambiguous, the packet returns `HOLD`; it does not invent a convenient answer.

### 6.2 Element complete

An element is complete for this program only when:

- every advertised main workflow is implemented through the pure library;
- each workflow has a supported-case and exclusion record;
- its public result shape is stable and uses explicit units;
- benchmark states are visible and are not circularly derived from the same
  production path;
- imports and architecture boundaries pass;
- public documentation makes no stronger claim than the evidence supports;
- a clean installed wheel can execute at least one main workflow for the
  element.

### 6.3 Library release candidate complete

The Python package becomes a release candidate when:

- the approved beam, column, isolated-footing, and slab capability matrix is
  complete;
- the stable public facade and deprecation decisions are implemented;
- source/provenance and protected-content reviews have no unresolved publication
  HOLD;
- wheel and sdist content match an approved allowlist;
- the current-commit `PR Gate` is green;
- one canonical full gate and one release preflight are green;
- the local prepublication wheel is accepted as rehearsal evidence, and the
  separate CI-built distribution intended for PyPI is identity-bound to its
  source commit/tag and accepted before protected production upload;
- package README, license/disclaimer, metadata, examples, and limitations match
  the artifact.

### 6.4 PyPI release complete

Publication is complete only after the owner-approved release is installed from
PyPI by exact version and passes the canonical installed-package/CLI verification.
A successful upload job alone is not completion.

## 7. Target architecture and dependency direction

```text
Core types
  Python/structural_lib/core/
      ↓
Pure IS 456 calculations
  Python/structural_lib/codes/is456/
      ↓
Library workflows and stable public facade
  Python/structural_lib/services/
      ↓
Transport and application consumers
  fastapi_app/ -> react_app/
```

Rules:

- Core contains code-agnostic types and primitives, not IS 456 formulas.
- `codes/is456/` contains deterministic math with no ordinary I/O.
- Services orchestrate calculations and adapters; they do not own formulas.
- FastAPI validates transport inputs, calls services/public APIs, and serializes
  results.
- React performs no structural calculations.
- Unit conversions occur only at explicit boundaries.
- The package is tested as an installed wheel, not only through repository
  imports.

## 8. Source, benchmark, and provenance foundation

### 8.1 Source hierarchy

Use the following order. A lower level cannot silently replace a higher level.

| Level | Source | Permitted use |
|---|---|---|
| S1 | Owner-controlled official IS 456 source basis with confirmed edition, reprint, reaffirmation, and amendment composition | Governing clause/table/figure identity and route-specific interpretation |
| S2 | Official BIS lifecycle/amendment metadata | Confirm source identity and amendment state; not a formula benchmark |
| S3 | Independently reviewed project-authored hand calculation or accepted worked example using the same assumptions | Expected result and tolerance for a narrow benchmark |
| S4 | Independent published design aid/textbook/software example with reviewed edition and assumptions | Candidate comparison or benchmark after acceptance review |
| S5 | Existing repository tests, golden vectors, legacy VBA, prior package, or StructProof route | Regression/comparison evidence only until independently promoted |

Current official public references to verify at source-intake time include:

- IS 456:2000 official BIS source/catalogue identity;
- BIS Amendment No. 6, June 2024:
  `https://www.services.bis.gov.in/tmp/CED19013804_03062024_1.pdf`;
- current BIS programme/catalogue metadata for revision and amendment state.

URLs and public metadata can change. The worker records the access date and does
not treat a search snippet as engineering evidence.

### 8.2 Protected-content rule

Repository artifacts may contain:

- source IDs;
- edition/amendment identifiers;
- clause, table, figure, and formula identifiers;
- project-authored summaries and symbolic transformations;
- benchmark IDs and evidence grades;
- input values and computed outputs;
- assumptions, limitations, and review state.

They must not contain copied standards wording, complete tables, charts,
figures, scans, or artifacts presented as official standards text.

`Python/structural_lib/codes/is456/clauses.json` is distributed in the wheel and
currently contains BIS-attributed `text` fields. Before the next public release,
PUB-003 must inventory this content and obtain an owner/legal decision. This
plan does not conclude whether the existing content is permissible.

### 8.3 Benchmark promotion

Use this evidence progression:

```text
CANDIDATE EXAMPLE
    -> independently replayed
    -> internal regression benchmark
    -> accepted narrow benchmark
    -> qualified review, when required for stronger claims
```

Rules:

- the governing code source is not itself an expected-value oracle;
- an implementation's own output cannot validate itself;
- existing tests and golden vectors remain comparison evidence until their
  derivation and assumptions are independently reviewed;
- tolerances come from the source method, rounding, and table/chart precision;
  no universal percentage is permitted;
- benchmark acceptance is route-specific and does not promote neighboring
  functions or a whole element;
- software verification never becomes professional design approval.

### 8.4 Reuse from StructProof

The other project at `/Users/pravinsurawase/Documents/Structautomate` may supply
patterns, not structural truth. Reusable patterns are:

- route cards separating work, evidence, claim, hold, and next action;
- source IDs with edition/amendment and review state;
- benchmark promotion stages;
- explicit proof/issues/assumptions/limitations;
- fail-closed unsupported conditions;
- private-source preparation outside pure math;
- binding controlled source/provenance identity to a run record.

Do not copy StructProof expected values, accepted states, private-source
contents, tolerances, or professional claims into this project. Treat the
legacy library and StructProof as comparison sources unless independently
reviewed for the exact route.

## 9. Agent operating model

### 9.1 Concurrency and ownership

- One parent task remains active.
- The parent/integrator owns scope, delegation, decisions, shared-file edits,
  integration, final review, and acceptance.
- Use no more than two concurrent workers.
- Workers receive only the relevant packet, exact paths, constraints, commands,
  and return format; never full conversation history.
- Read-only evidence audits may run in parallel when their questions are
  independent.
- Implementation workers may run in parallel only with exclusive file
  ownership and no shared public-export/core-type edits.
- The parent independently inspects every result and runs the appropriate gate.
- Workers cannot merge, tag, publish, release, close issues, delete remote
  branches, or change repository settings.

### 9.2 Role map

| Role | Primary responsibility | Mutation boundary |
|---|---|---|
| Main Agent / orchestrator | Scope, packet selection, dependency order, integration, decisions | Shared records only when authorized |
| `@library-expert` | Public API and source/capability audit | Read-only |
| `@structural-engineer` | Governing source, assumptions, exclusions, benchmark review questions | Read-only; no formula invention |
| `@structural-math` | Core types and deterministic IS 456 implementation | Approved core/element files only |
| `@backend` | Stable library facade and service orchestration | Services/public exports only |
| `@tester` | Narrow benchmark/regression evidence and installed-package checks | Test/evidence files only; does not choose formulas |
| `@reviewer` | Essential main-process and architecture review | Read-only; no speculative edge-case list |
| `@doc-master` | Capability, public API, limitations, task, and handoff records | Named documentation only |
| `@ops` | Safe branch/PR/gates/artifact/release workflow | No publish/merge/tag without owner approval |

### 9.3 Shared-file locks

The following paths are integrator-owned during parallel work:

| Path | Rule |
|---|---|
| `Python/structural_lib/core/data_types.py` | One structural-math owner at a time |
| `Python/structural_lib/core/errors.py` | One structural-math owner at a time |
| `Python/structural_lib/services/api.py` | Backend/integrator only |
| Any package `__init__.py` | Integrator adds exports after worker return |
| `Python/pyproject.toml` and `Python/MANIFEST.in` | Packaging/ops packet only |
| `.github/workflows/publish.yml` | Ops packet only |
| `docs/TASKS.md` | Parent/doc-master after accepted state change |
| `docs/planning/next-session-brief.md` | Parent/doc-master at real handoff only |
| This master plan's status/ledger | Parent/integrator only |

Workers must stop if they discover that their required fix touches a locked or
out-of-packet path. They return the dependency instead of editing it.

## 10. Verification and gate ladder

Use the project's existing skills and commands; do not create a second gate
system.

### During a calculation packet

1. Run the exact affected test module or keyword.
2. Independently compare the main result with the approved benchmark and units.
3. Run architecture/import validation if imports or layers changed.

Typical commands:

```bash
.venv/bin/pytest <exact-test-path> -q
.venv/bin/pytest Python/tests/ -q -k "<function-or-clause>"
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib
```

### Before one packet commit

```bash
./run.sh check --quick
# Return packet-owned paths and the suggested conventional commit to Codex.
# Codex stages only those paths and commits with standard validation enabled.
```

### At a stable integrated milestone

```bash
./run.sh check
```

Run the full gate once after the milestone is stable. After a failure, repair
with the narrow failing command and rerun the full gate only when needed to
establish the final green result.

### Release only

```bash
./run.sh release preflight <target-version>
.venv/bin/python -m build Python
./run.sh release verify --version <target-version> --source wheel
```

After owner-approved publication:

```bash
./run.sh release verify --version <target-version> --source pypi
```

Do not run release preflight, Docker preflight, or full UAT for ordinary
calculation packets.

## 11. Dependency graph

```text
Owner activation
  -> MAINT-008 complete
  -> v0.21.7 release-or-defer decision recorded
  -> clean LIB-IS456-V1 branch/PR
      -> P0 scope/source/claim decisions
          -> P1 capability/evidence audit
          -> P2 public API/package audit
          -> P3 beam closure audit
          -> P4 column closure audit
          -> P5 footing dowel implementation
              -> P6 slab types and classification
                  -> P7 one-way coefficients/design
                      -> P8 one-way detailing/serviceability boundary
                  -> P9 two-way coefficient contract
                      -> P10 two-way design/distribution
              -> P11 stable facade and capability registry
                  -> P12 evidence/public-claim/package-content closeout
                      -> P13 exact-artifact release candidate
                          -> owner TestPyPI/PyPI decision
                              -> FAPI-1 thin FastAPI consumer
                                  -> React product work
```

P3 and P4 may run in parallel. P7 and P9 may run in parallel only after P6 is
accepted and only when they edit separate modules/tests. P8 and P9 may also run
in parallel under exclusive file ownership. Public exports remain reserved for
P11.

## 12. Phase plan

### Phase 0 — Activate a clean lane

**Outcome:** no library feature work is mixed into maintenance or an unresolved
release lane.

Owner checkpoints:

1. Review PR #691 and its live `PR Gate`.
2. Approve or reject its merge through the native Codex Git/GitHub flow.
3. Decide whether to publish v0.21.7 or explicitly defer it.
4. Approve the Supported IS 456 RC Core definition in Section 5.
5. Approve a new task branch/PR for LIB-IS456-V1.

Recorded native branch command:

```bash
git switch -c task/LIB-IS456-V1 origin/main
```

**Exit:** clean task branch, baseline commit recorded, no unrelated changes,
task status activated.

Activation record:

| Decision | State | Evidence/owner | Next |
|---|---|---|---|
| Supported IS 456 RC Core in Section 5 | APPROVED | Repository owner activation request, 2026-08-09 | Enforce route-specific exclusions in P3-P12 |
| MAINT-008 Packet B | APPROVED/MERGED | PR #691, merge `056bfad7`, live `PR Gate` green after OpenAPI baseline repair | Keep control-plane work outside LIB commits |
| v0.21.7 | DEFERRED | Main Agent decision under the activated plan; no tag or upload | Target the complete library release instead |
| Governing source composition | APPROVED FOR INTERNAL ENGINEERING INTAKE | Controlled IS 456:2000 through Amendment 5/reaffirmation 2021, SHA-256 `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`; Amendment 6 June 2024, SHA-256 `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881` | Record route-specific amendment relevance without copying protected content |
| Benchmark acceptance | APPROVED PROCESS | Project-authored S3 hand calculations require independent replay; S4 public examples require assumption review; repository/StructProof outputs remain S5 unless promoted | Each calculation packet records expected result and justified tolerance |
| Public claims before qualified review | APPROVED WITH LIMITS | Software evidence only; case-qualified support and exclusions; no certification or professional-approval claim | P12 cross-checks every public claim |
| `clauses.json` publication | HOLD | Repository owner/legal-content decision; P12 must inventory/remove protected wording before release | P12 |
| Later library version | PROVISIONAL v0.23.0 | Main Agent; final version remains a P13 release decision | Confirm after P11/P12 |

### Phase 1 — Truth and contract baseline

Run two read-only workers concurrently:

- P1: capability/source/benchmark matrix for the existing elements;
- P2: public API, dependency, package-content, README, and release automation
  inventory.

The parent consolidates their results. No worker edits shared documentation.

**Exit:** one approved support matrix, public surface map, source HOLD list,
package allowlist draft, and exact implementation order.

### Phase 2 — Existing-element closure

Run beam and column audits concurrently. These are essential-only audits, not
requests to add tests or refactor code.

Only confirmed supported-main-path defects become implementation packets.
Documentation gaps are repaired when they make a public claim false.

**Exit:** beam and column supported-case matrices accepted; any blocking defect
has its own source-backed packet; no undefined “complete” claim remains.

### Phase 3 — Isolated-footing closure

Implement the dowel/bearing-transfer slice only after source and benchmark
intake. Normalize footing traceability and exports after the calculation is
accepted.

**Exit:** isolated-footing core supports its declared case end to end through
the Python package; excluded footing families remain explicit.

### Phase 4 — Slab foundation and one-way core

Sequence:

1. Types, errors, supported-case contract, and classification.
2. One-way coefficients/analysis contract.
3. One-way design.
4. Detailing and serviceability boundary.
5. Public export only after all preceding work is accepted.

**Exit:** one supported solid one-way slab workflow runs from public Python
input to structured result and matches its accepted benchmark.

### Phase 5 — Two-way slab core

Sequence:

1. Approve source/protected-table policy for the coefficient path.
2. Implement coefficient lookup/calculation contract.
3. Implement approved two-way design case.
4. Implement strip/torsion distribution only within the approved case.
5. Document unsupported panels, supports, load patterns, and geometry.

**Exit:** one supported solid two-way slab workflow runs from public Python
input to structured result and matches its accepted benchmark.

### Phase 6 — Stable Python surface

The backend/integrator consolidates the library-facing facade after core
behavior is stable. This phase does not add FastAPI routes.

**Exit:** public API manifest, imports, signatures, result types, explicit
units, capability discovery, deprecations, examples, and package metadata agree.

### Phase 7 — Publication evidence and package-content closeout

Resolve:

- `clauses.json` protected-content/publication decision;
- wheel/sdist allowlist;
- license and engineering-disclaimer inclusion;
- README claims against evidence states;
- release docs versus actual TestPyPI/PyPI workflow;
- exact-artifact evidence contract plus local prepublication filenames and
  SHA-256 record; the CI publication artifact is recorded in Phase 8;
- SBOM and package metadata evidence;
- exact clean-wheel user workflow.

**Exit:** no publication HOLD remains, but no external publication has occurred.

### Phase 8 — Release candidate and PyPI

This phase is separately owner-approved.

1. Run the current-commit PR Gate and canonical release preflight.
2. Prepare the exact version through the release workflow.
3. Build and clean-wheel-UAT one local candidate as pre-release evidence; label
   it `local-prepublication`, not the published artifact.
4. Optionally rehearse on TestPyPI through its owner-approved protected
   environment and trusted publisher.
5. Obtain explicit owner approval for the release PR/tag. The production `pypi`
   environment must remain protected so upload approval occurs only after the CI
   artifact evidence is available.
6. When the tag-triggered workflow builds the distributions, record the CI run,
   source commit/tag, wheel/sdist filenames, SHA-256 hashes, content-allowlist
   result, SBOM, and exact artifact-download identity.
7. Run the canonical installed-package/CLI UAT against the CI-built distribution
   before production upload, or first complete an approved workflow change that
   makes the publish job consume that already-UAT-tested artifact.
8. Obtain explicit owner approval for the protected production environment and
   publish only the recorded CI artifact through the tag-only OIDC workflow.
9. Install the exact public PyPI version, record its downloaded file identity,
   compare it with the CI artifact record, and run post-publication UAT.
10. Record the artifact and claim evidence; do not call upload success a release
    success without post-publication verification.

### Phase 9 — Thin FastAPI consumer

Begin only after the Python surface is accepted or intentionally frozen for the
release candidate.

- FastAPI imports only stable library/service functions.
- Routers contain no structural formulas.
- Add request/response models for the supported library cases only.
- Verify request -> service -> result -> response for one workflow per element.
- Do not begin React expansion until API schemas are stable.

## 13. Worker-ready packets

Every packet below is bounded. The parent supplies only this section and the
named files to the worker.

### P0 — Owner scope, source, and claim lock

**Owner:** repository owner + Main Agent

**Objective:** approve the exact library finish line and evidence boundaries
before calculations change.

**Inputs:** this plan; `docs/TASKS.md`; official source inventory; current
release/maintenance state.

**Decisions required:**

- supported beam, column, isolated-footing, one-way-slab, and two-way-slab cases;
- governing IS 456 source composition and amendment review owner;
- independent benchmark sources and who may accept them;
- public wording allowed before qualified review;
- `clauses.json` publication/legal review owner;
- v0.21.7 release or defer decision;
- target version for the later library release.

**Non-goals:** formula implementation, version bump, merge, tag, upload.

**Acceptance:** every unresolved engineering/legal/release decision is marked
`HOLD` with an owner; no worker needs to guess.

**Return:** decision table with `APPROVED`, `HOLD`, or `DEFERRED`, owner, and next
packet.

**Recorded outcome (2026-08-09):** P0 is complete. The activation table in
Phase 0 is authoritative. The only continuing P0 HOLD is public distribution of
`clauses.json`; it does not authorize copying private source content and blocks
publication until P12 resolves it.

### P1 — Capability, evidence, and claims matrix

**Role:** `@library-expert` or `@structural-engineer`, read-only first

**Objective:** create the truthful baseline for what the Python package supports.

**Paths:**

- `Python/structural_lib/codes/is456/`
- `Python/tests/`
- `docs/reference/clause-map.md`
- `docs/verification/`
- `scripts/parity_dashboard.py`
- `README.md`
- `Python/README.md`

**Questions:** for each advertised workflow, what geometry/load/material case is
supported, what source/benchmark state exists, what is excluded, and what public
wording is justified?

**Non-goals:** code changes, new tests, formula review without source, edge-case
list, test-count target.

**Commands:**

```bash
./run.sh parity
rg -n "@clause|Limitations|unsupported|NotImplemented" Python/structural_lib/codes/is456
rg --files Python/tests | rg "beam|column|footing|slab"
```

**Acceptance:** matrix covers every public beam/column/footing route and records
slab as planned; parity is not used as whole-code evidence.

**Return format:** capability -> source state -> benchmark state -> claim state
-> limitations -> blocking packet. Report only confirmed outcome-changing gaps.

### P2 — Public API and packaging inventory

**Role:** `@backend` or `@library-expert`, read-only first

**Objective:** identify the intended public package contract and distribution
contents before adding new functions.

**Paths:**

- `Python/structural_lib/__init__.py`
- `Python/structural_lib/api.py`
- `Python/structural_lib/services/api.py`
- `Python/structural_lib/services/beam_api.py`
- `Python/structural_lib/services/column_api.py`
- all current IS 456 package `__init__.py` files
- `docs/reference/api-manifest.json`
- `docs/reference/api-stability.md`
- `docs/reference/deprecation-policy.md`
- `Python/pyproject.toml`
- `Python/MANIFEST.in`

**Non-goals:** rename functions, remove shims, edit metadata, add slab facade,
FastAPI work.

**Commands:**

```bash
./run.sh find --api <representative-public-function>
.venv/bin/python scripts/discover_api_signatures.py <representative-public-function>
rg -n "__all__|from structural_lib|def design_" Python/structural_lib
```

**Acceptance:** one map of canonical, compatibility, internal, and accidental
exports; one distribution allowlist draft; base versus optional dependencies
identified.

**Return format:** symbol/path -> current status -> proposed status -> consumers
-> compatibility risk -> owner decision.

### P3 — Beam closure audit

**Role:** `@structural-engineer`, read-only

**Objective:** determine whether any confirmed defect blocks the declared beam
scope.

**Paths:**

- `Python/structural_lib/codes/is456/beam/`
- matching beam tests and approved benchmark records
- current public beam facade and documentation

**Non-goals:** redesign, new beam cases, new tests, style cleanup, compatibility
removal.

**Acceptance:** supported-case matrix and only outcome-changing blockers; every
formula concern names the required source and benchmark evidence.

**Return:** `PASS FOR STATED SCOPE` or bounded follow-up packets with exact paths,
source question, test command, and acceptance result.

**Recorded outcome (2026-08-09):** `PASS FOR STATED COMPUTATION SCOPE`, with
public claims narrowed. The primary combined route is rectangular flexure and
shear plus optional serviceability; torsion, flanged, doubly reinforced,
detailing, and other specialist paths are separate bounded utilities. Existing
tests are regression evidence, not accepted independent engineering benchmarks.

### P4 — Column closure audit

**Role:** `@structural-engineer`, read-only

**Objective:** establish the exact supported column boundary and confirmed
blockers for release claims.

**Paths:**

- `Python/structural_lib/codes/is456/column/`
- `Python/tests/test_column_*.py`
- `Python/tests/codes/is456/column/`
- current column service/public documentation

**Non-goals:** circular/asymmetric/arbitrary-multilayer expansion, new
interaction models, edge-case campaign.

**Acceptance:** geometry, reinforcement layout, axial/uniaxial/biaxial,
short/slender, helical, and detailing boundaries are explicit.

**Return:** `PASS FOR STATED SCOPE` or bounded blockers, plus public wording and
unsupported-case text.

**Recorded outcome (2026-08-09):** bounded rectangular/square symmetric
two-face column utilities accepted after two outcome repairs: the direct
biaxial route now checks slenderness about both axes and fails closed, while the
long-column route requires unsupported length and enforces minimum eccentricity
about both axes. Helical support is documented as an adequacy/capacity-multiplier
utility, not circular-column design. Independent route benchmarks remain future
claim evidence, so no professional or general-design claim is authorized.

### P5 — Isolated-footing dowel/bearing-transfer slice

**Role:** `@structural-math`

**Prerequisites:** P0 source/benchmark approval; a parent-integrator-approved
reuse/new core-type decision informed by P1/P2 findings.

**Objective:** implement the approved Cl. 34.4 bearing/reinforcement/dowel
transfer result for the existing isolated-footing supported case.

**Initial paths:**

- `Python/structural_lib/codes/is456/footing/`
- `Python/structural_lib/core/data_types.py` only if P1 proves necessary
- `Python/tests/test_footing.py` or a new exact footing test module

**Non-goals:** footing endpoint, combined/strap/raft/pile-cap footing,
settlement, lateral stability, broad footing refactor.

**Pitfalls:** mixing service and factored actions; hidden N/kN or mm/mm2
conversion; copying clause wording; choosing development-length policy without
source; silently accepting unsupported column/footing geometry.

**Narrow checks:**

```bash
.venv/bin/pytest Python/tests/test_footing.py -q
.venv/bin/pytest Python/tests/ -q -k "footing or dowel"
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib
```

**Acceptance:** pure function, explicit units, source IDs, accepted benchmark and
governing limit, structured result/failure, canonical element export, stated
exclusions.

**Return:** supported case; formula/source IDs; benchmark actual/expected with
units; changed files; checks; limitations; owner/engineer decisions remaining.

**Recorded outcome (2026-08-09):** accepted for concentric square/rectangular
isolated footings with explicit approved effective A1 and dowels. The result
governs supported/supporting concrete, excess/minimum transfer steel, bar count,
diameter, and development into both members. The legacy bearing helper now
defaults conservatively to no enhancement unless approved A1 is supplied.

### P6 — Slab contracts and classification

**Role:** `@structural-math`

**Prerequisites:** P0 approved first slab case; a parent-integrator-approved
reuse/new core-type decision informed by P1/P2 findings.

**Objective:** establish the smallest stable slab type/error contract and
classify the approved solid slab geometry without implementing full design.

**Initial paths:**

- `Python/structural_lib/core/data_types.py`
- `Python/structural_lib/core/errors.py`
- new `Python/structural_lib/codes/is456/slab/`
- new focused slab tests

**Non-goals:** one-way design, two-way coefficients, flat slab, API, UI,
generic element framework.

**Pitfalls:** selecting a design path before validating span/support inputs;
overloading beam result types; creating result shapes that cannot carry
assumptions/limitations; editing shared exports during worker execution.

**Acceptance:** supported geometry contract, explicit span/width/thickness
units, classification result, fail-closed unsupported inputs, focused test,
architecture/import pass.

**Return:** type map, public-intent recommendation, changed paths, focused
evidence, exclusions, dependency for P7/P9.

**Recorded outcome (2026-08-09):** accepted package-local frozen geometry,
classification, result, and error contracts. Effective spans are explicit and
normalized; `Ly/Lx > 2` is one-way and `<= 2` is two-way. No support condition,
load, coefficient, or design behavior is inferred. Public export remains P11.

### P7 — One-way slab coefficient and design slice

**Role:** `@structural-math`

**Prerequisites:** P6 accepted; source/table policy and benchmark approved.

**Objective:** deliver one independently verifiable solid one-way slab design
workflow for the owner-approved support/load case.

**Paths:** new slab modules and exact slab tests; no shared export edits.

**Non-goals:** two-way slabs, flat slabs, general load analysis, punching,
optimization, API/UI.

**Pitfalls:** protected table reproduction; effective-span assumption drift;
mixing service and factored loads; beam helper reuse with incompatible slab
assumptions; universal tolerances.

**Acceptance:** source-backed coefficients/formulas, dimensional reasoning,
accepted benchmark, governing limit, explicit assumptions, structured result,
focused tests.

**Return:** public workflow candidate signature, actual/expected result with
units, limitations, files, checks, HOLD items.

**Recorded outcome (2026-08-09):** accepted the simply supported one-way
flexure slice. The 3.0 m benchmark gives 11.25 kN m and 260.7266 mm2 required
steel for the 1 m strip. Continuity, shear and serviceability completion remain
explicitly outside this slice.

### P8 — One-way slab detailing and serviceability boundary

**Role:** `@structural-math`

**Prerequisites:** stable P7 result contract.

**Objective:** add the minimum reinforcement/spacing/detailing and approved
serviceability behavior needed to finish the supported one-way workflow.

**Non-goals:** IS 13920 slab behavior, direct-deflection models without approved
source/benchmark, arbitrary bar optimization, two-way detailing.

**Acceptance:** main reinforcement, distribution reinforcement, spacing,
diameter, and serviceability outcome are explicit for the supported case;
unsupported numerical serviceability behavior fails closed or returns a review
state as approved by P0.

**Return:** changed files, result fields/units, benchmark/limit evidence,
warnings/limitations, exact checks.

**Recorded outcome (2026-08-09):** accepted minimum steel, bar diameter,
provided-bar spacing and the basic `Lx/d` review boundary. The benchmark
provided main/distribution steel is adequate; `Lx/d = 24` returns qualified
review because modification factors/direct deflection are not implemented.

### P9 — Two-way coefficient contract

**Role:** `@structural-math`

**Prerequisites:** P6 accepted; protected-table and interpolation/exact-match
policy approved.

**Objective:** implement the approved two-way coefficient lookup/calculation
contract without the full design workflow.

**Non-goals:** full two-way design, flat slabs, uncontrolled interpolation,
copying full tables, public exports.

**Acceptance:** source identity, panel/support/load classification, lookup
behavior, bounds, unsupported conditions, and benchmark evidence are explicit.

**Return:** supported coefficient cases, source/provenance handling, files,
tests, HOLD cases, dependency for P10.

**Recorded outcome (2026-08-09):** accepted a caller-supplied external
coefficient record with explicit source, approval acknowledgement and
`review_required` state. No protected table, lookup or interpolation ships.

### P10 — Two-way slab design and distribution

**Role:** `@structural-math`

**Prerequisites:** P7 and P9 accepted.

**Objective:** complete one owner-approved solid two-way slab workflow,
including only the required distribution/torsion behavior.

**Non-goals:** flat/drop/ribbed slabs, irregular panels, openings, FEM, broad
punching extraction, API/UI.

**Acceptance:** end-to-end pure-library result matches the approved independent
benchmark; units, assumptions, strips, torsion conditions, limitations, and
fail-closed cases are explicit.

**Return:** supported case, benchmark result, changed files, exact tests,
remaining held cases.

**Recorded outcome (2026-08-09):** accepted the sole interior solid
rectangular panel with all four edges continuous. For `Lx=4 m`, `Ly=6 m`,
`wu=10 kN/m2`, `alpha_x=.08` and `alpha_y=.06`, the moments are 12.8 and
9.6 kN m and the required steel is 244.7591 and 195.6828 mm2. Edge/corner
panels and full detailing remain held.

### P11 — Stable Python facade and capability discovery

**Role:** `@backend` with parent integration

**Prerequisites:** selected beam, column, footing, and slab cores accepted.

**Objective:** expose one intentional library contract without transport logic
or duplicate calculations.

**Paths:**

- `Python/structural_lib/services/`
- intentional package `__init__.py` files
- API manifest/contract tests
- public API/deprecation documentation

**Non-goals:** FastAPI routers, React hooks, formula changes, removing a public
shim without approved deprecation.

**Commands:**

```bash
./run.sh find --api <each-approved-public-function>
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib
.venv/bin/pytest Python/tests/integration/test_api_entrypoints_is456.py -q
```

Use the live matching integration path if that exact test filename changes.

**Acceptance:** canonical imports and signatures are discoverable; services only
delegate/orchestrate; explicit units and result mappings are stable; accidental
exports are documented or removed through policy.

**Return:** public symbol table, deprecation decisions, consumers, compatibility
risks, files, tests.

**Recorded outcome (2026-08-09):** the canonical service facade now contains
116 intentional symbols, with package-root and `structural_lib.api`
compatibility paths delegating to the same objects. Footing transfer, bounded
slab workflows and capability discovery are public. The missing
development-length service adapter was restored, eliminating FastAPI fallback
arithmetic. Integrated facade tests, architecture and import validation pass.

### P12 — Publication content, evidence, and claims closeout

**Roles:** `@library-expert`/`@reviewer` read-only audit, then `@doc-master` or
`@ops` for approved edits

**Objective:** remove publication ambiguity without changing engineering math.

**Paths:**

- `Python/pyproject.toml`
- `Python/MANIFEST.in`
- `Python/structural_lib/codes/is456/clauses.json`
- `Python/structural_lib/codes/is456/traceability.py`
- `README.md`, `Python/README.md`
- `LICENSE`, `Python/LICENSE`, `LICENSE_ENGINEERING.md`
- `docs/legal/`
- `docs/verification/`
- `docs/planning/pre-release-checklist.md`
- `.github/workflows/publish.yml`
- `scripts/release.py`

**Non-goals:** formula review, version bump, upload, tag, merge.

**Acceptance:** approved wheel/sdist allowlist; protected-content decision;
engineering disclaimer decision; claim-to-evidence crosswalk; release docs match
actual commands; exact-artifact evidence template exists; the CI build intended
for PyPI records artifact identity and passes the canonical installed-package/CLI
UAT before the protected production upload can be approved.

**Return:** confirmed changes, unresolved owner decisions, and `READY` or
`PUBLICATION HOLD`.

**Recorded outcome (2026-08-09):** `READY` for owner/CI review. The public
package has an explicit content allowlist, `clauses.json` is metadata-only, and
the 130-page source/extraction corpus is retained only in the Git-ignored
`private_sources/` boundary. Public claims are case-qualified. A clean local
wheel/sdist rehearsal passed installed-package and CLI UAT, and the integrated
repository gate passed 29/29. Exact CI artifact identity, final version,
TestPyPI/PyPI, tag and release approval remain P13 owner decisions.

### P13 — Local prepublication and CI exact-artifact release candidate

**Role:** `@ops`, with `@tester` and `@reviewer`

**Prerequisites:** P12 READY; owner authorizes release preparation; clean tree;
current-commit PR Gate green; exact target version selected.

**Objective:** use a local wheel as prepublication rehearsal, then prove that the
separate CI-built distribution intended for PyPI is identity-bound, UAT-tested,
and releasable while preserving publication approval boundaries.

**Commands:**

```bash
./run.sh release preflight <target-version>
.venv/bin/python -m build Python
./run.sh release verify --version <target-version> --source wheel
```

**Required evidence:** local prepublication wheel identity/UAT; release commit,
PR, version, and tag; CI workflow run; CI wheel/sdist filenames and SHA-256;
content allowlist result; metadata/readme/license result; SBOM; canonical UAT on
the CI-built distribution; protected-environment state; limitations/claim state;
approvals outstanding.

**Non-goals:** production tag/upload/GitHub Release without explicit approval.

**Acceptance:** the local candidate is clearly labeled prepublication; the
CI-built distribution that the publish job will download is UAT-tested and
recorded; production upload remains paused for owner approval. Return `READY FOR
OWNER RELEASE DECISION`, never `RELEASED`.

**Return:** release-preflight report in the maintained skill format plus artifact
identity and owner-only actions.

### FAPI-1 — Thin FastAPI adoption

**Role:** `@api-developer`

**Prerequisites:** stable P11 contract; library release candidate or deliberately
frozen library commit.

**Objective:** make FastAPI consume the library contract for the supported
beam/column/footing/slab workflows.

**Non-goals:** UI work, structural calculations in routers, speculative endpoint
families, backward-incompatible response redesign without approval.

**Acceptance:** request validation -> public/service call -> structured response
works for one representative path per supported element; no upward import or
formula duplication.

**Return:** endpoint/contract map, exact request/response evidence, changed files,
tests, compatibility risks.

## 14. Safe parallel execution schedule

| Wave | Worker A | Worker B | Parent action after return |
|---|---|---|---|
| 0 | No worker | No worker | Owner resolves MAINT-008 and v0.21.7 decision |
| 1 | P1 capability/evidence audit | P2 public API/package audit | Consolidate baseline and lock shared types/API decisions |
| 2 | P3 beam closure audit | P4 column closure audit | Accept supported matrices; create only confirmed fix packets |
| 3 | P5 footing source/readiness or implementation | P6 slab readiness audit only if it does not edit shared core | Integrate footing first; lock slab types |
| 4 | P7 one-way implementation | P9 two-way coefficient preparation/read-only | Accept one-way core; decide protected-table path |
| 5 | P8 one-way detailing | P9 two-way coefficient implementation, separate files | Integrate exports only after both return |
| 6 | P10 two-way design | P12 package/source audit, read-only | Integrate library; resolve publication HOLDs |
| 7 | P11 stable facade | No second editor | Freeze public contract and run integrated gate |
| 8 | P12 approved documentation/package edits | No second editor | Establish release-candidate readiness |
| 9 | P13 local/CI artifact evidence | Reviewer verifies exact commit, CI artifact, and UAT binding | Ask owner for protected TestPyPI/PyPI approval |

Never run two implementation workers that both touch `core/`, `services/api.py`,
package exports, the same test module, packaging metadata, or canonical planning
records.

## 15. Worker packet prompt template

Use this template verbatim and fill every bracket. Lower-context workers should
not need this entire plan.

```text
Packet: [ID and name]
Role: [project role]

Objective:
[One measurable outcome.]

Prerequisites and accepted decisions:
[Source/benchmark/public-contract decisions already approved.]

Exact files/directories in scope:
- [path]
- [path]

Read first:
- AGENTS.md
- [relevant folder index]
- [one or more exact skills]
- [source/evidence packet]

Non-goals:
- [explicit adjacent work]
- No merge, tag, publish, issue closure, remote-branch deletion, or settings change.

Constraints:
- Preserve Core -> IS 456 -> Services -> UI.
- Explicit units: mm, mm2, N/mm2, kN, kNm as appropriate.
- Do not copy protected standards text/tables/figures.
- Return HOLD rather than choosing a formula, value, tolerance, or claim.
- Do not edit locked/shared files without parent approval.

Likely pitfalls:
- [specific unit/assumption/import/compatibility risks]

Required commands:
- [targeted command]
- [architecture/import command when relevant]

Acceptance criteria:
1. [observable outcome]
2. [source/benchmark evidence]
3. [supported/unsupported behavior]
4. [tests/checks]

Return format:
- Outcome: COMPLETE / HOLD / BLOCKED
- Supported case and exclusions
- Files read/changed
- Source and benchmark IDs used
- Actual versus expected result with units, when applicable
- Commands and exact results
- Assumptions and limitations
- Shared-file dependencies discovered
- Owner/qualified-review decisions remaining
- Terminal issues in the required format
```

## 16. Logs and durable state

Use existing canonical records. Do not create one log per agent.

| Record | Update rule |
|---|---|
| This plan | Parent updates packet state and execution ledger after accepted work |
| `docs/TASKS.md` | Update when a packet starts, completes, is held, or priority changes |
| `docs/WORKLOG.md` | Add a compact completed-outcome entry after accepted work |
| `docs/planning/next-session-brief.md` | Update only at a real handoff/task switch or when the next action changes |
| `docs/SESSION_LOG.md` | Update only when a durable session record is required by the task |
| PR/commit evidence | Record exact commit and current PR Gate in the packet closeout |

### Execution ledger template

| Date | Packet | Agent/role | Outcome | Branch/commit | Files | Focused evidence | Gate | Holds/owner decisions | Next |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-09 | P0 | Main Agent/owner | COMPLETE | `task/LIB-IS456-V1` at `056bfad7` | This plan | Controlled-source identity/hash and visual amendment review; owner activation | Phase 0 only | `clauses.json` publication HOLD; v0.23.0 provisional | P1/P2 |
| 2026-08-09 | P1 | library-expert/structural-engineer | COMPLETE | Read-only | Beam/column/footing code, tests, docs, parity | Capability/source/benchmark/claim matrix; parity 96% treated only as wiring evidence | Not applicable | Route-specific independent benchmark acceptance remains | P3/P4/P5 |
| 2026-08-09 | P2 | backend/library-expert | COMPLETE WITH PUBLICATION HOLD | Read-only | Facades, manifest, packaging, release workflow | 108-symbol service manifest match; wheel/sdist inventory; dependency/public-export map | Not applicable | Canonical facade, protected content, artifact hash/allowlist/UAT | P11/P12/P13 |
| 2026-08-09 | P3 | structural-engineer | COMPLETE | Read-only plus parent docs | Beam code/tests and public claims | Focused beam suites green; route-specific matrix accepted | Focused | Independent beam benchmarks remain claim-limited | P12 |
| 2026-08-09 | P4 | structural-engineer + Main Agent | COMPLETE | Working tree | Column core/service/FastAPI/tests/docs | Two-axis slenderness fail-close; long-column minimum eccentricity; full focused column/API slice green | Focused | Independent route benchmarks remain claim-limited | P11/P12 |
| 2026-08-09 | P5 | structural-math + Main Agent | COMPLETE | Working tree | Footing transfer, legacy bearing helper, focused tests | Independent 3000 kN hand calculation; both-member development checks; footing suite green | Focused | Public facade waits for P11 | P11 |
| 2026-08-09 | P6 | structural-math + Main Agent | COMPLETE | Working tree | Slab-local contracts/classification/tests | 13 focused tests; architecture/import checks green | Focused | Public facade waits for P11 | P7/P9 |
| 2026-08-09 | P7 | structural-math + Main Agent | COMPLETE | Working tree | One-way slab flexure/tests | Independent 11.25 kN m and 260.7266 mm2 benchmark | Focused | Continuity/shear/detailing held for later packets | P8 |
| 2026-08-09 | P8 | structural-math + Main Agent | COMPLETE | Working tree | One-way slab detailing/tests | Provided-bar, spacing, diameter and basic Lx/d evidence | Focused | Modification factors/direct deflection require review | P11 |
| 2026-08-09 | P9 | structural-math + Main Agent | COMPLETE | Working tree | External coefficient contract/tests | Explicit source/approval/review state; no built-in protected values | Focused | Coefficient correctness remains qualified input | P10 |
| 2026-08-09 | P10 | structural-math + Main Agent | COMPLETE | Working tree | Two-way slab flexure/tests | Independent 12.8/9.6 kN m benchmark; 70 slab tests green | Focused | Edge/corner panels and detailing held | P11 |
| 2026-08-09 | P11 | backend + Main Agent | COMPLETE | Working tree | Service facade, package exports, manifest, integration tests | 116-symbol manifest; canonical/compatibility identity; architecture/import green | Focused | Stable-version promise remains owner release decision | P12/FAPI-1 |
| 2026-08-09 | FAPI-1 | api-developer + Main Agent | COMPLETE | Working tree | Development-length fix; footing/slab router/models/tests | Representative beam/column/footing/slab request-to-service evidence | Focused | No UI expansion | P12 |
| 2026-08-09 | P12 | Main Agent | COMPLETE / READY | `task/LIB-IS456-V1` at `301ddec7`; draft PR #693 | Package allowlist, protected-source boundary, claims, publish workflow | Public clause data sanitized; private 130-page corpus ignored; clean local artifact UAT; quick gate 9/9; full gate 29/29; PR run `31321772342` green | Full + PR | Exact CI publication-artifact identity and owner release decision remain | P13 |

### Required handoff content

- completed outcome;
- current branch and commit;
- exact remaining packet;
- files changed;
- focused and gate commands already run;
- source/benchmark evidence used;
- assumptions, limitations, and unsupported cases;
- owner/qualified-review decisions;
- checks intentionally not repeated;
- `⚠️ TERMINAL ISSUE: [what happened] -> [what worked instead]`, when applicable.

## 17. Public API and version policy

- Keep pre-1.0 versions while the library surface is still settling.
- Do not delay all useful releases until literal whole-standard coverage.
- A major version promises public API stability, not support for every IS 456
  clause.
- Add new supported workflows through intentional public exports.
- Internal helpers may change without deprecation only when they were never
  public/advertised.
- Existing public behavior follows the repository deprecation policy.
- The package description and README list supported elements and limitations;
  they do not use an unqualified “IS 456 complete” claim.
- Base dependencies remain limited to what every package user needs. FastAPI,
  React, CAD, reporting, PDF, and development tools remain outside the base
  install or in explicit optional extras.

Recommended release decision sequence, subject to owner approval:

1. v0.21.7: release the already-prepared maintenance/security baseline, or
   explicitly record its deferral.
2. v0.22.x: stabilize public contract, source/provenance boundaries, and package
   claims.
3. v0.23.0: publish the supported slab plus isolated-footing completion scope.
4. v1.0 later: stable API and qualified/accepted evidence for every advertised
   production-supported route, not every clause in the standard.

## 18. PyPI release control

The project already uses modern `[project]` metadata in `Python/pyproject.toml`
and a Trusted Publishing-style OIDC workflow. Preserve these foundations.

Official packaging/release references:

- Python packaging flow:
  `https://packaging.python.org/en/latest/flow/`
- `pyproject.toml` specification:
  `https://packaging.python.org/en/latest/specifications/pyproject-toml/`
- Building and publishing guidance:
  `https://packaging.python.org/en/latest/guides/section-build-and-publish/`
- PyPI Trusted Publishers:
  `https://docs.pypi.org/trusted-publishers/`
- Trusted Publisher security model:
  `https://docs.pypi.org/trusted-publishers/security-model/`

Release rules:

- The publication job receives job-level `id-token: write`; other jobs do not.
- Production publication remains tag-only.
- The PyPI environment should retain required owner approval.
- The publish job downloads the CI-built distribution artifact. The release
  record distinguishes it from any locally built prepublication candidate and
  binds the published artifact to the CI run, commit/tag, filename, SHA-256,
  SBOM, allowlist result, and UAT evidence.
- The CI-built distribution intended for PyPI must complete the canonical
  installed-package/CLI UAT before the protected production upload is approved.
- Inspect wheel and sdist contents for private/protected/unintended files.
- Treat attestations and OIDC as supply-chain identity evidence, not structural
  correctness evidence.
- TestPyPI is a rehearsal and requires owner approval because it is an external
  upload.
- PyPI releases are immutable; if a published release is defective, the owner
  decides whether to yank it and publishes a corrected higher version.

## 19. Risk register and containment

| Risk | Prevention | Stop/rollback |
|---|---|---|
| False “complete IS 456” claim | Supported-capability matrix and claim states | Block release wording until corrected |
| Wrong amendment/source basis | P0 source lock and route-specific amendment review | Return HOLD; no formula edit |
| Circular benchmark | Independent benchmark acceptance | Demote to comparison; do not loosen tolerance |
| Protected source text/table ships | P12 allowlist and `clauses.json` review | PUBLICATION HOLD; remove/replace only after owner/legal decision |
| Units drift | Explicit suffixes and dimensional intake | Stop on unreconciled conversion |
| Agent edit collision | Max two workers, shared-file locks, parent-only exports | Stop worker; parent resolves on one branch |
| Rewrite expands scope | Essential-only outcome test | Revert/split unaccepted adjacent edits before commit |
| Accidental API break | P2 map, P11 facade, deprecation policy | Restore compatibility or obtain owner version decision |
| Package contains wrong files | Wheel/sdist allowlist and archive inspection | Rebuild before any upload |
| Tested artifact differs from published artifact | Distinguish local rehearsal from CI build; UAT and hash the CI artifact before protected upload; exact-version post-PyPI UAT | Owner evaluates yank/new version; never overwrite |
| Maintenance/release branch contamination | Phase 0 clean-lane gate | Do not commit library work on MAINT-008-B |
| Full gates waste the day | Targeted checks, one quick gate, one milestone full gate | Do not repeat unchanged evidence |
| FastAPI/UI reintroduces math | Architecture checker and thin consumer contract | Move root calculation back to library before acceptance |

## 20. Immediate kickoff checklist

The first implementation session begins only after the owner clears Phase 0.

### Current execution checkpoint

P0-P12, FAPI-1, and remediation packets T0/R1-R8 are implemented. The latest
software checkpoint passes 5,445 Python tests (3 skipped, 6 deselected), 349
FastAPI tests, 147 React tests, frontend lint/build, quick 9/9, full 29/29,
audit 19/19, and health 100/100. A clean-source v0.23.0 wheel passed package
version and CLI checks with excluded namespaces absent.

C0 and C1 are complete. Product remediation is checkpointed at `2ff5a42a`,
bounded closeout truth at `fbd24350`, and the separately landed automation
commit `f812eb3f` is integrated without history rewriting at `d4eb9e9d`. The
worktree is clean and both Node and Python runtime selectors are retained.

C2 final product UAT is the next and only active packet, followed by C3 exact
artifact freeze and C4 evidence freeze. Do not begin new calculation,
multi-code, or excluded structural-system work. Professional review and
publication actions remain deferred.

## 21. Final program acceptance checklist

- [x] MAINT-008 is resolved without library scope contamination.
- [x] v0.21.7 has an explicit release/defer decision.
- [x] Supported IS 456 RC Core scope is owner-approved.
- [x] Official source composition and amendment state are recorded.
- [x] Public/protected-source handling is approved.
- [x] Beam supported-case and evidence matrix is accepted.
- [x] Column supported-case and evidence matrix is accepted.
- [x] Isolated-footing core, including dowel/bearing transfer, is accepted.
- [x] One-way slab supported workflow is accepted.
- [x] Two-way slab supported workflow is accepted.
- [x] Unsupported elements/cases fail closed or are not advertised.
- [x] Stable Python public facade and deprecation decisions are documented.
- [x] Base and optional dependency boundaries are intentional.
- [x] Wheel/sdist contents match the approved allowlist.
- [x] Public README, license/disclaimer, examples, and claims match the artifact.
- [x] Targeted checks and architecture/import checks are green per packet.
- [x] Quick gate is green before each accepted commit.
- [x] One integrated full gate is green for each stable milestone.
- [x] Current release-candidate PR Gate is green.
- [ ] Canonical release preflight is green.
- [ ] Local prepublication and CI publication-artifact filenames/SHA-256 values
      are separately recorded.
- [ ] Local rehearsal UAT and CI publication-artifact clean-install/CLI UAT are
      green.
- [ ] Owner has separately approved any TestPyPI/PyPI/tag/GitHub Release action.
- [ ] Exact published PyPI version passes post-publication UAT.
- [ ] Handoff and execution ledger identify remaining limitations and review
      boundaries.

## 22. Program closeout statement

When this checklist is complete, the project may state that the package supports
the documented beam, column, isolated-footing, and solid-slab cases under IS
456:2000 and the recorded amendment basis.

It may not state that all of IS 456 is implemented, that every structural system
is supported, that passing software tests certifies formula correctness, or that
the package replaces qualified structural-engineering review.
