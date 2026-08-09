# Professional Library Remediation Plan

**Task:** LIB-PRO-001
**Type:** Remediation evidence ledger
**Audience:** Maintainers, release owners, and final qualified reviewer
**Status:** Software remediation complete; retained as the LIB-PRO-001 evidence ledger
**Prepared:** 2026-08-09
**Scope:** Supported Python calculations, service/API contracts, React result truth, reports, units, release evidence, and the terminal control plane

## 1. Outcome and release decision

This document is no longer the active implementation plan. T0 and R1-R8 are
complete, and their findings, packet definitions, and verification remain here
as the durable remediation record. Active bounded-product closeout now follows
[is456-library-first-master-plan.md](is456-library-first-master-plan.md).

The repository is not ready to publish or describe v0.23.0 as released. The
software baseline is broad and well tested, but the audit confirmed failures
that can change a supported design outcome or misrepresent it to a user.

The release hold remains until all P0/P1 packets below are complete, the
contract/tooling packets are reconciled, an exact built wheel passes the
release gate, the owner declares the complete intended development scope
finished, and a qualified structural engineer then reviews the final affected
formula and supported-case evidence. Passing software tests is evidence of
software behavior; it is not formula certification or professional design
approval.

No professional review is scheduled during ongoing development. Until the
final review is recorded, this repository and every prepared artifact must be
described as development software that is **not approved or usable for
engineering decisions**. An AI review may improve software quality but cannot
satisfy or replace the final qualified-engineer gate.

No tag, PyPI upload, GitHub Release, merge, issue closure, or branch deletion is
authorized by this plan. Those remain owner-only actions requiring explicit
approval.

## 2. Audit basis and present state

The audit used the current `codex/release-v0.23.0` tree at release-preparation
commit `b1634a5f`, compared it with `main` at `cc99e610`, inspected all current
uncommitted paths, and traced relevant work back through repository history.
The current branch has no v0.23.0 tag, GitHub Release, or pull request.

The clean product baseline before remediation was:

- Python: 5,273 passed.
- FastAPI: 340 passed.
- React: 146 passed; lint and production build passed on Node 24.
- Quick gate: 9/9.
- Full gate: 29/29.
- Readiness audit: 19/19.

These green totals do not invalidate the findings. The confirmed defects sit
in negative paths, cross-layer status mapping, and contracts that the existing
positive-path suites did not exercise.

### 2.1 Working-tree ownership lanes

Keep these lanes separate so no worker overwrites or silently folds unrelated
work into a structural patch:

1. **Model-policy lane:** `.codex/config.toml`, `AGENTS.md`,
   `agents/model_policy.json`, and
   `docs/guidelines/ai-token-efficiency.md`. These changes implement the
   user's explicit request to allow delegated model choice.
2. **Terminal-control lane:** `run.sh`, `scripts/node_runtime.py`,
   `scripts/release.py`, `scripts/launch_stack.sh`, script indexes/registry,
   terminal guidance, the React validation skill, and focused runtime tests.
3. **Audit/governance lane:** this plan, `docs/TASKS.md`,
   `docs/planning/next-session-brief.md`, and the eventual audit evidence.
4. **Structural remediation lane:** T0 and R1-R8 are implemented in the current
   worktree. The changes remain unstaged so the owner can review them alongside
   the preserved model-policy, terminal-control, and governance lanes.

Before every packet, run `git status --short`, `git diff --stat`, and a targeted
`git diff -- <owned paths>`. Stop if another lane overlaps the packet.

## 3. Confirmed findings

| ID | Priority | Outcome-changing defect | Primary locations |
|----|----------|-------------------------|-------------------|
| NUM-01 | P0 | Non-finite public beam inputs can pass range comparisons and reach calculations instead of failing closed. | `Python/structural_lib/services/common_api.py`, beam entry points |
| BATCH-01 | P0 | Batch status is based on flexure alone; an unsafe shear result can be returned and displayed/applied as PASS. Delivered and expected result field names also differ. | `Python/structural_lib/services/batch.py`, `react_app/src/hooks/useBatchDesign.ts`, `BatchDesignPage.tsx` |
| FOOT-01 | P1 | `check_bearing_pressure(..., fck=inf, ...)` can report an infinite capacity and `is_safe=True`. | `Python/structural_lib/codes/is456/footing/bearing.py` |
| FOOT-02 | P1 | Footing minimum flexural steel uses effective depth `d_mm`; the slab-type minimum percentage needs the total concrete cross-section/overall thickness contract. | `Python/structural_lib/codes/is456/footing/flexure.py` and public callers |
| FOOT-03 | P1 | Core load transfer accepts a fractional dowel count and can declare the physically impossible arrangement safe. | `Python/structural_lib/codes/is456/footing/load_transfer.py`, FastAPI request model |
| REPORT-01 | P1 | Report templates default missing sectional statuses to PASS and consume `is_ok`, while current result adapters commonly expose `is_safe`; a false section PASS is possible. | `Python/structural_lib/reports/generator.py`, `reports/templates/*.j2`, calculation-report adapter |
| RELEASE-01 | P1 | v0.23.0 is presented as current/released in some surfaces although no tag/release exists; the editable environment reports 0.21.6 while source/FastAPI report 0.23.0. | `CITATION.cff`, `Python/README.md`, package metadata, version helpers, release docs |
| SLAB-01 | P1 | The two-way result is a deliberately bounded two-coefficient flexure case, not a complete positive/negative strip design; naming and advertising must not imply a full two-way slab design. | `slab/external_coefficients.py`, `slab/two_way.py`, capabilities/docs |
| REVIEW-01 | P1 | A P9 record remains `review_required` while P10 also accepts a separate acknowledgement; consumers can misread acknowledgement as coefficient verification. | slab coefficient/result models and public docs |
| MANIFEST-01 | P2 | Two API manifest mechanisms disagree; `check_api_compat.py` reports false removals/additions against a stale private manifest. | `services/api_manifest.json`, `scripts/check_api_compat.py`, canonical docs manifest |
| MANIFEST-02 | P2 | `validate_api_contracts.py --manifest` reads the old `functions` shape, warns that current symbols are absent, and still exits successfully. | `scripts/validate_api_contracts.py`, `docs/reference/api-manifest.json` |
| API-01 | P2 | Pydantic 422 responses bypass the documented `{success,data,error}` envelope for the new library-core endpoints. | FastAPI exception setup, `routers/library_core.py`, response models |
| CAP-01 | P2 | `check_bearing_pressure` is a public standalone safety check but is absent from the footing capability registry. | `services/capabilities.py`, `services/api.py` |
| UNIT-01 | P2 | New APIs mostly use explicit suffixes, but older public DTOs, report adapters, and manifests mix `fck`, `fck_nmm2`, `tau_v`, `tv`, `is_ok`, and `is_safe`. This caused real cross-layer failures. | public DTOs, adapters, reports, API manifests |
| TERMINAL-01 | P2 | `./run.sh test` was described as all tests while it ran the Python package only; general React commands did not share the proven `.nvmrc` selector. | `run.sh`, runtime guidance, release/launcher helpers |

## 4. Recent-work reconciliation: do not repeat these projects

### 4.1 TASK-660 and TASK-660B: naming migration

Commits `f6a327b1` and `d249c01e` standardized many IS 456 variable names and
preserved deprecated aliases. Do not perform another repository-wide rename.
UNIT-01 is a boundary-contract repair: define canonical serialized field names,
normalize old aliases in one adapter, and preserve the already promised v0.24
deprecation schedule.

### 4.2 TASK-670: calculation-report field repair

Commit `839edab9` corrected four `ShearResult` attribute accesses in
`services/calculation_report.py` and added real-object coverage. REPORT-01 is
not a rerun of that work. It addresses the separate semantic mismatch between
`is_safe` and template `is_ok`, plus unsafe `get(..., True)` fallbacks across
the Jinja reports. Preserve TASK-670's corrected numeric fields.

### 4.3 TASK-729/730: plausibility and input validation

The earlier audit added Pydantic cross-field checks and 49 FastAPI tests. It
did not establish a shared finite-number invariant for direct Python public
entry points. NUM-01 and FOOT-01 must extend the canonical Python boundary,
then prove FastAPI behavior through delegation; do not add a second independent
web-only validator.

### 4.4 MAINT-004: canonical checks and manifests

MAINT-004 made `run.sh check`, the documentation API manifest, indexes, and
scanners the supported truth sources. MANIFEST-01/02 should retire or redirect
the two legacy readers. Do not generate a third manifest or weaken failures to
warnings.

### 4.5 MAINT-005: Node/runtime and live browser workflow

Checkpoint `6f119132` repaired the dev launcher and verified the positive
153-beam browser/export path. Commit `78f1453c` added the same Node 24 logic to
release preflight. TERMINAL-01 extracts that proven selection into a reusable
helper and makes test scope truthful. BATCH-01 adds the missing unsafe-shear
negative path; it does not repeat the successful happy-path browser sweep.

### 4.6 LIB-IS456-V1: supported-core completion

The existing `is456-library-first-master-plan.md` and verification evidence
remain the source for supported cases, clause/source identities, packaging,
and benchmark provenance. This plan is a release-blocking defect program on
top of that work. It must not expand the supported engineering domain while
repairing it.

## 5. Dependency-ordered remediation packets

Only one packet is implemented at a time unless the owner explicitly approves
two non-overlapping branches. Each packet return must include: paths changed,
root cause, behavior before/after, tests and exact counts, remaining risks,
and `git status --short`.

### Packet T0 — Terminal control-plane root fix

**Objective:** make the repository root a reliable command boundary and make
test/runtime scope explicit.

**Owned paths:** `run.sh`, `scripts/node_runtime.py`, `scripts/release.py`,
`scripts/launch_stack.sh`, `scripts/automation-map.json`, script indexes,
`scripts/README.md`, terminal guidance, React validation skill, and
`Python/tests/test_release_environment.py`.

**Implementation:**

1. Use one Python runtime selector for `.nvmrc`, Homebrew versioned Node,
   current PATH, and installed nvm versions.
2. Make release preflight and the stack launcher consume it rather than carry
   divergent selection algorithms.
3. Add root-stable `./run.sh frontend runtime|lint|test|build|check|dev`.
4. Keep `./run.sh test` backward compatible but describe it truthfully as the
   Python suite; add explicit `--python`, `--fastapi`, `--react`, and `--all`.
5. Remove the stale fallback that kills an arbitrary listener with `kill -9`.
6. Remove dead VBA and Streamlit control paths whose target scripts no longer
   exist, and make executable missing-script references fail the validator.
7. Register and index the new helper and add focused runtime regression tests.

**Non-goals:** installing a different Node major; changing npm dependencies;
running a release; changing product calculations.

**Acceptance:** shell syntax passes; the selected Node major matches `.nvmrc`;
the helper rejects a missing npm or wrong Node major; test help and dispatch
are accurate; script inventory is 100%; React lint/test/build pass through the
new root command.

**Rollback:** revert only T0 paths. The pre-existing release and launcher
selectors remain recoverable from `78f1453c` and `6f119132`.

### Packet R1 — Shared finite numeric boundary

**Prerequisite:** T0 complete so commands are deterministic.

**Objective:** reject booleans, NaN, infinity, non-real values, and invalid
positive dimensions/actions before any supported calculation can report a
result.

**Owned paths:** `services/common_api.py`, the smallest shared footing validator
in `footing/_common.py`, `footing/bearing.py`, and directly affected tests.

**Implementation:**

1. Introduce one small explicit helper for optional/required real finite
   values. Keep exception types and public messages compatible where possible.
2. Apply it to every argument consumed by `design_beam_is456` and
   `check_beam_is456`, including actions, dimensions, material strengths,
   stirrup area, optional percentages, and optional steel area.
3. Apply the same invariant before footing geometry, pressure, bearing, shear,
   and flexure comparisons. Do not rely on `x <= 0`, because NaN makes that
   comparison false.
4. Confirm all calculated safety booleans are derived only from finite values.

**Tests:** extend the current plausibility/API entry-point tests and footing
tests with parameterized `nan`, `inf`, `-inf`, boolean, and a valid boundary.
Include the exact `fck=inf` bearing reproduction.

**Acceptance:** every public supported beam/footing entry point fails closed
before arithmetic; no error path serializes non-finite JSON; valid golden
vectors are unchanged.

**Non-goals:** changing IS 456 formulas, supported grades, or generous
unit-confusion upper bounds.

### Packet R2 — Truthful batch result contract

**Prerequisite:** R1, because the batch path calls the public beam entry point.

**Objective:** one canonical result controls server status, SSE payload,
React display, CSV export, and apply-to-store behavior.

**Owned paths:** `services/batch.py`, FastAPI streaming adapter/tests,
`useBatchDesign.ts`, `useBatchDesign.test.ts`, `BatchDesignPage.tsx`, and its
focused component tests.

**Implementation:**

1. Define `design_succeeded` separately from `design_is_safe`.
2. Set overall engineering pass only when all required checks, including
   flexure and shear, pass. Do not treat “calculation completed” as PASS.
3. Emit canonical names matching the maintained REST contract:
   `tau_v`, `tau_c`, `tau_c_max`, `stirrup_spacing`, capacity/utilization, and
   explicit `is_safe`/overall status.
4. Preserve legacy fields only in a documented adapter if an existing consumer
   requires them.
5. Make the hook read the server status rather than forcing `success: true`.
6. Prevent unsafe or failed results from being applied as valid beams. Export
   the same status displayed on screen.

**Required reproductions:** 300 x 500 mm, Mu 100 kNm, Vu 600 kN must complete
the calculation but return/display FAIL because shear is unsafe. A normal safe
case must still display and apply PASS.

**Tests:** `Python/tests/unit/test_batch.py`, FastAPI streaming negative and
safe cases, hook event mapping, page summary/export/apply behavior.

**Acceptance:** server, SSE, React table, summary, CSV, and store agree for safe,
unsafe, and exception outcomes; no undefined shear fields in the supported
flow.

### Packet R3 — Canonical report status adapter

**Prerequisite:** R2 establishes status semantics.

**Objective:** reports never invent PASS from a missing or mismatched field.

**Owned paths:** report generator/adapter, `services/calculation_report.py` only
where needed, active Jinja templates, and focused report/golden tests.

**Implementation:**

1. Add one adapter that converts current result objects/dicts into a versioned
   report context with explicit section status.
2. Map `is_safe` and supported legacy `is_ok` deliberately. Missing required
   status becomes `UNKNOWN/NOT EVALUATED` or a generation error, never PASS.
3. Replace every safety-sensitive `get('is_ok', True)` in active templates.
4. Keep TASK-670 numeric field corrections; do not rename the raw dataclasses.
5. Put overall PASS behind all required evaluated section statuses.

**Tests:** real safe and unsafe result objects, missing-status input, summary,
detailed, and beam-design templates, fallback HTML, and report golden files.

**Acceptance:** an unsafe shear object renders FAIL in every section/summary;
missing status cannot render a green check; existing approved text/layout
changes only where status truth requires it.

### Packet R4 — Footing physical and reinforcement contract

**Prerequisite:** R1.

**Objective:** correct the minimum-steel area basis and reject impossible dowel
counts without expanding the supported footing case.

**Owned paths:** `footing/flexure.py`, `footing/load_transfer.py`, public facade
signatures/adapters, `fastapi_app/models/library_core.py`, related schemas and
footing tests.

**Implementation:**

1. Record the minimum-steel clause basis and controlled-source identity in the
   final-review packet without copying protected table text. Qualified-owner
   confirmation is deliberately deferred until the complete intended
   development scope is finished.
2. Add an explicit overall thickness input where the minimum percentage needs
   gross cross-sectional area. Validate `0 < d_mm < overall_thickness_mm`.
3. Decide compatibility deliberately: either a new keyword-only argument with
   a deprecation path or a versioned function. Never infer total thickness from
   effective depth.
4. Require `dowel_count` to be a non-boolean integral value before area math.
   Match the FastAPI strict integer contract to the Python core.
5. Recheck development-length direction names and bond-stress material sides;
   change only if source review confirms an outcome defect.

**Tests:** minimum steel with equal `d` but different overall thickness,
invalid depth/thickness ordering, `6.8` dowels, booleans, four bars, benchmark
safe/unsafe load-transfer cases, facade and FastAPI parity.

**Acceptance:** no fractional count can enter a result; minimum steel uses the
source-approved physical area; old callers receive a clear compatibility path;
golden footing actions/capacities remain unchanged except the confirmed steel
correction.

### Packet R5 — Slab support and review semantics

**Prerequisite:** R1; may follow R4.

**Objective:** make the intentionally bounded two-way workflow impossible to
mistake for complete two-way slab design or verified coefficient truth.

**Owned paths:** slab coefficient/two-way models, slab service facade,
capabilities, CLI/API serialization, tests, and supported-case docs.

**Implementation:**

1. Keep the current two-coefficient, interior, all-edges-continuous flexure
   case bounded. Do not add tables or extra coefficients without separately
   approved source/benchmark work.
2. Rename public capability/status text to “externally accepted coefficient,
   flexure-only supported case” while preserving Python compatibility aliases
   if required.
3. Separate `coefficient_review_status`, `qualified_acceptance_recorded`, and
   `coefficient_correctness_verified_by_library`. The last remains false.
4. Return explicit incomplete-design dependencies for detailing,
   serviceability, shear/punching, load combinations/patterning, and other
   panel cases.
5. Ensure no UI/report translates `is_supported=True` into “design safe”.

**Acceptance:** consumers can distinguish supported computation, coefficient
provenance, qualified acceptance, and complete engineering approval; current
11.25/12.8/9.6 kN m benchmark arithmetic is unchanged.

### Packet R6 — Capability, units, and serialized names

**Prerequisite:** R2-R5 establish canonical semantics.

**Objective:** publish one machine-readable contract for supported functions,
units, aliases, result status, and limitations.

**Implementation:**

1. Add/classify `check_bearing_pressure` in the footing capability record.
2. Inventory only supported public workflows, not every expert helper.
3. For each input/output record field name, quantity, unit, required/optional,
   aliases, deprecation version, and finite/physical domain.
4. Canonicalize serialized fields at adapters, not by another broad TASK-660
   source rename. Prefer explicit suffixes such as `_mm`, `_mm2`, `_kn`,
   `_knm`, and `_nmm2` where compatibility permits.
5. Add contract tests that compare capability records, facade exports, FastAPI
   schemas, report adapters, and TypeScript types for the supported subset.

**Acceptance:** there is one canonical serialized name per quantity; legacy
aliases are intentional and tested; all supported safety checks appear in
capabilities with limitations and qualified-review requirements.

### Packet R7 — One API manifest and one validation envelope

**Prerequisite:** R6.

**Objective:** eliminate conflicting compatibility evidence and return one
documented FastAPI error shape.

**Implementation:**

1. Declare `docs/reference/api-manifest.json` the only compatibility manifest.
2. Redirect or retire `services/api_manifest.json` and
   `scripts/check_api_compat.py`; update references and CI rather than silently
   keeping both.
3. Update `validate_api_contracts.py` to the current `symbols` schema and make
   real removals/signature drift exit nonzero.
4. Register a request-validation exception handler that maps Pydantic 422
   failures into the maintained error envelope without losing field detail.
5. Update OpenAPI baseline and clients only after handler tests pass.

**Acceptance:** all manifest tools read the same file and fail closed; a
deliberate missing symbol makes the gate fail; both library-core endpoints and
existing endpoints return one tested 422 envelope.

### Packet R8 — Version and release truth

**Prerequisite:** all P0/P1 packets and R7.

**Objective:** ensure source, editable development, built wheel, API health,
docs, citation metadata, tag, and release status cannot contradict one another.

**Implementation:**

1. Revert “released” wording until publication actually completes. Distinguish
   source version, prepared version, and published version.
2. Add a release-preflight check comparing `pyproject.toml`, wheel metadata,
   imported package version in a clean environment, FastAPI version, React
   package version, citation metadata, changelog, and release docs.
3. Treat editable-environment metadata as rebuildable local state, not release
   evidence. Recreate/reinstall the environment when exact installed metadata
   is required.
4. Build one exact wheel, record its SHA-256, inspect contents, install it into
   a clean environment, and run the supported library/CLI UAT.
5. Only after all evidence and owner approvals may the owner authorize tag,
   TestPyPI/PyPI, GitHub Release, and final released wording.

**Acceptance:** every inspected version surface agrees for the exact artifact;
the tag-install URL exists before docs advertise it; no local editable checkout
is used as publication proof.

## 6. Verification ladder

Use focused tests during a packet. Run the quick gate once before a packet
commit. Run the full gate once after all stable remediation packets are
integrated; do not duplicate the full gate after every small edit.

### Focused software gates

```bash
./run.sh frontend runtime
.venv/bin/pytest Python/tests/test_release_environment.py -q
.venv/bin/pytest Python/tests/unit/test_batch.py -q
.venv/bin/pytest Python/tests/test_footing.py \
  Python/tests/test_footing_load_transfer.py -q
.venv/bin/pytest Python/tests/test_reports.py \
  Python/tests/test_calculation_report.py -q
.venv/bin/pytest Python/tests/codes/is456/slab -q
.venv/bin/pytest fastapi_app/tests/test_streaming.py \
  fastapi_app/tests/test_library_core.py -q
./run.sh frontend test useBatchDesign
```

### Integration closeout

```bash
./run.sh check --quick
./run.sh test --all
./run.sh frontend check
./run.sh check
./run.sh audit
./run.sh health
./run.sh parity
./run.sh release preflight 0.23.0
```

The release preflight command is validation only. It does not authorize or
perform publication.

### Engineering evidence gate

For every changed formula or safety condition, record:

- controlled source identifier and clause reference;
- units and conversion chain;
- hand calculation or independent trusted benchmark;
- boundary/unsafe case and expected failure mode;
- software result and tolerance;
- reviewer identity, review date, scope, and unresolved limitations.

Protected standards must not be copied into public fixtures or documentation.

## 7. Stop conditions and escalation

Stop the packet and return to the owner if:

- a source interpretation changes the supported engineering domain;
- backward compatibility requires silently guessing a unit or thickness;
- a proposed fix changes a golden vector without independent calculation;
- another working-tree lane overlaps the owned paths;
- the branch is behind/diverged/conflicted or publication state changes;
- a test only passes by weakening an assertion, suppressing a warning, or
  defaulting missing safety state to PASS.

## 8. Definition of done

LIB-PRO-001 is complete only when:

1. NUM-01, BATCH-01, FOOT-01/02/03, REPORT-01, RELEASE-01, SLAB-01, and
   REVIEW-01 are closed with reviewed evidence.
2. MANIFEST-01/02, API-01, CAP-01, UNIT-01, and TERMINAL-01 have one canonical
   contract each and fail-closed regression coverage.
3. No active task/handoff claims superseded MAINT-008 or v0.21.7 work is still
   pending.
4. The exact v0.23.0 candidate wheel passes clean-environment UAT and all
   canonical repository gates.
5. The owner explicitly declares the complete intended library/product work
   scope finished and freezes it for final review.
6. Qualified engineering review of that final frozen scope is recorded for
   affected calculations.
7. The owner explicitly approves any subsequent merge and, separately, any
   tag or publication operation.

## 9. Software remediation checkpoint — 2026-08-09

T0 and R1-R8 are implemented and independently integrated. The confirmed
software defects are closed with fail-closed input handling, truthful batch
and report status, explicit footing thickness and dowel contracts, bounded
slab review semantics, one semantic capability contract, one API manifest,
one raw OpenAPI baseline, a maintained 422 envelope, and exact candidate-wheel
evidence.

Closeout evidence:

- Python: 5,445 passed, 3 skipped, 6 deselected.
- FastAPI: 349 passed.
- React: 147 passed; lint and production build passed on Node 24.
- Quick gate: 9/9; full gate: 29/29.
- Readiness audit: 19/19; project health: 100/100; parity: 93%.
- Public API manifest: 73/73 functions compatible; OpenAPI: 62 endpoints and
  65 schemas with no snapshot drift.
- Clean-source v0.23.0 wheel: 181 members, zero excluded migration/research/
  ACI/EC2 namespaces, clean import and CLI help passed; SHA-256
  `1414a06acbac36f503c9e18c11461a10d02f722f87f78c95a530336f35063770`.

LIB-PRO-001 is not professionally closed. Development may continue under the
release hold, but no professional review is requested yet and no engineering-
usability claim is permitted. After the owner declares the entire intended
work scope complete, the final frozen scope must receive qualified structural-
engineering review; merge and publication remain separate owner decisions.
No release action was performed.
