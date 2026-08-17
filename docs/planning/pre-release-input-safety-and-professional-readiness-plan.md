# Pre-Release Input Safety and Professional Readiness Plan

**Task:** LIB-PRO-002
**Type:** Decision
**Audience:** Maintainers
**Status:** In Progress
**Created:** 2026-08-17
**Last Updated:** 2026-08-17
**Importance:** Critical
**Prepared:** 2026-08-17
**Planning source base:** `origin/main` at `904a2f8cf0ea5d4595f57c46dac06e2e837bba45`
**Cumulative implementation base:** `origin/main` at
`fe4ab025419b834c6d0f840e9492c0604ae74201` after Packets A-G merged through
PR #815
**Scope:** Public/project input, import accounting, orchestration, result truth,
API classification, evidence identity, documentation, and release gates
**Source bound:** `true`

## 1. Executive decision

The narrow one-storey pilot supports a useful but limited conclusion: for the
specific slab, beam, column, and footing cases exercised, the independently
recomputed arithmetic matched the library outputs. The footing dowel
development-length failure was also reproduced and is a legitimate failure,
not a software defect.

The A-G remediation merged through PR #815 materially improved the library.
The strict service, named lossless import, HTTP/SSE/React, result/review,
evidence, API-classification, and release-authorization paths now fail closed
for the original reproduced cases. Those corrections are real and the
one-storey member arithmetic remains unchanged.

The post-fix user replay nevertheless found one advertised path outside that
accepted boundary. `python -m structural_lib design` still uses the historical
Excel/CSV reader. In a two-row file containing one valid beam and one malformed
beam, it skipped the malformed row, exited `0`, and wrote a summary saying the
one remaining beam passed. The exact-wheel negative UAT passed all 19 of its
declared cases because it does not execute this CLI path. The current PyPI
`0.23.1a1` artifact also predates A-G and still carries the old incorrect pin
and non-executable batch example. Therefore the current source is much safer,
but the advertised package surface is not yet publication-ready.

A subsequent publication-readiness replay found two independent release-signal
defects. The scheduled full verification at A-G merge `fe4ab025...` failed six
governance/session tests because `actions/setup-python` installs an interpreter
without creating the `.venv` or `VIRTUAL_ENV` contract required by
`scripts/python_runtime.sh`; the workflow did not export the already-supported
`STRUCTURAL_LIB_PYTHON` path. The provisional next-Alpha command
`./run.sh release preflight 0.23.1a2` then passed 6,387 Python tests, 446 FastAPI
tests, and the React build, yet printed `READY TO RELEASE` while also reporting
that no exact wheel was supplied. It does not evaluate the separate
authorization record, which remains `HOLD`, or the omitted CLI negative. Local
pre-bump health is therefore green, but the release verdict is not.

The decision is:

- Hold every next public package publication until the Alpha safety gate in
  Section 5 is complete and separately authorized by the owner.
- Continue describing the current release as Alpha/development software.
- Do not claim whole-building design, professional approval, codewide formula
  certification, or project fitness from the pilot.
- Complete Packet I CLI convergence and expand exact-wheel UAT to every
  advertised calculation entry point.
- Complete Packet J release-signal convergence so scheduled/tag workflows use
  the selected interpreter and preflight reports mode-accurate readiness.
- Finish I-J before expanding formulas, load cases, structural systems, or UI
  capability.
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

### 2.3 Post-fix recheck at `fe4ab025…`

The following classifications distinguish a real correction from a test-only
or partial improvement.

| Area rechecked | Post-fix observation | Classification |
|---|---|---|
| Canonical beam batch | Complete explicit-unit input evaluated; malformed numeric input blocked with `PROJECT_BEAM_INVALID_NUMBER`; empty input blocked and evaluated zero members | **Fixed for this service** |
| Compatibility beam batch | Malformed width returned a structured error and did not call the calculation core | **Fixed for this service** |
| Direct Excel-style headings | The strict service rejected them with named unknown/missing-field issues instead of guessing | **Fixed behavior**; use a named adapter |
| Named Generic CSV import | Ordinary headings were accepted with one accounted source row and a normalization ledger | **Fixed for the tested adapter case** |
| Adapter ambiguity and row loss | Ambiguity, malformed rows, unmatched records, and injected row loss block in the 19-case UAT | **Fixed for covered routes** |
| Column materials | Omitting `fck_nmm2` or `fy_nmm2` blocks instead of supplying 25/415 | **Fixed** |
| Result/review truth | Beam, slab, column, and footing results retain `QUALIFIED_REVIEW_REQUIRED`; assumed footing bases remain assumed | **Fixed for covered results** |
| API inventory | 187 root exports and 168 service-facade exports are machine-classified; no callable leakage is accepted | **Improved substantially** |
| Exact-wheel negative UAT | A clean temporary environment installed the current built wheel and passed all 19 declared cases | **Improved but incomplete**; CLI is absent |
| Advertised `design` CLI | One malformed row was skipped; warning text contaminated stdout; process exited `0`; output reported one of one beams passed | **Still blocking** |
| Scheduled full verification | Weekly run `31988837003` on `fe4ab025...` failed six launcher-dependent tests because the workflow did not export the selected setup-python executable | **Still blocking**; PR checks alone are insufficient |
| Pre-bump release verdict | Provisional `0.23.1a2` local tests/build passed, but preflight printed `READY TO RELEASE` with no exact wheel and while authorization remained `HOLD` | **Still blocking**; verdict conflates preparation with publication |
| Published PyPI `0.23.1a1` | [Published on 2026-08-11](https://pypi.org/project/structural-lib-is456/0.23.1a1/) before A-G; page still says pin `0.23.0`, and its batch example raises `AttributeError` against the installed wheel | **Known old artifact; not fixed retroactively** |
| Whole-building workflow | No controlled model generates or reconciles the complete slab-to-foundation load path | **Still not implemented** |

### 2.4 One-storey load-path and manual side calculation

This is a synthetic regression model, not a real design: one 2.5 m by 5.5 m
one-way slab panel, one exterior simply supported 5.5 m beam taking a 1.25 m
tributary width, one 400 mm square 3 m column, and one concentric square
footing. Materials are M25 and Fe415. Loads, support conditions, soil pressure,
and the `1.5` factor are declared test assumptions rather than generated or
verified project facts.

| Check | Hand calculation and maintained clause/formula basis | Library | Result |
|---|---|---:|---|
| Slab factored load | `1.5 × (0.15×25 + 1.0 + 3.0) = 11.625 kN/m²` | 11.625 | Match |
| Slab moment | `wu L²/8 = 11.625×2.5²/8 = 9.082031 kN·m/m`; rectangular equilibrium `C=0.36 fck b xu`, `z=d-0.42xu` | 9.082031 | Match |
| Slab steel | Exact Cl. 38.1/Annex-G equilibrium at `b=1000 mm`, `d=125 mm` gives `Ast=207.012 mm²/m` | 207.012 | Match |
| Slab supplied bars | 10 mm at 250 mm gives 314.159 mm²/m; 8 mm distribution at 250 mm gives 201.062 mm²/m against 180 mm²/m minimum | Adequate; qualified review required | Match |
| Beam line load | `1.5 × [7.75×1.25 + 0.30×(0.50-0.15)×25] = 18.46875 kN/m` | caller input | Match |
| Beam actions | `Mu=wuL²/8=69.834961 kN·m`; `Vu=wuL/2=50.789063 kN` | same | Match |
| Beam flexure/shear | Cl. 38.1/Annex G gives `Ast=465.092 mm²`; Cl. 40.1 gives `tau_v=Vu/(bd)=0.383025 N/mm²` | same | Match |
| Column factored load | Beam reaction 50.789063 + `1.5×0.4×0.4×3×25` column self-weight = 68.789063 kN | 68.789063 | Match |
| Column axial capacity | Cl. 39.3: `0.4 fck Ac + 0.67 fy Asc = 2031.157 kN` for eight 16 mm bars | 2031.157 | Match |
| Column minimum moment | Cl. 25.4: `e_min=max(l/500+D/30,20)=20 mm`; `Pu e=1.375781 kN·m` | 1.375781 in each axis | Match |
| Linked footing service load | Beam reaction 33.859375 + column self-weight 12.0 + 750×750×300 mm footing self-weight 4.21875 = 50.078125 kN | caller input, marked assumed | Reconciled test load |
| Footing sizing/pressure | Cl. 34.1 basis: 750×750 mm gives `q=50.078125/0.75²=89.027778 kPa < 100 kPa` | 750×750; 89.027778 | Match |
| Footing moment | Cl. 34.2.3.1/34.3.1 basis: `qu=133.541667 kPa`, projection 0.175 m, `Mu=qu×0.75×0.175²/2=1.533643 kN·m` | 1.533643 | Match |
| Footing punching | Cl. 31.6.1/34.2.4.1(b): at `d/2`, `b0=4×(400+250)=2600 mm`; `tau_v=0.028763 N/mm²`, `tau_c=0.25√25=1.25 N/mm²`, utilization 0.023010 | 0.023010 | Match |
| Footing dowel anchorage | Cl. 26.2.1: `Ld=16×(0.87×415)/(4×2.24)=644.732 mm`; only 300/600 mm supplied | 644.732; aggregate `FAIL` | Correct failure |

The chained loads now reconcile for this narrow gravity example, which is an
improvement over the earlier unrelated 60/90 kN footing probe. It still does
not provide analysis, combinations, continuity, direct slab deflection/crack
checks, lateral loads, geotechnical verification, or professional approval.

## 3. Confirmed root-cause map

The apparent list of many failures reduces to nine root causes. Fixing symptoms
independently would create more formats and more drift.

| Root cause | Confirmed mechanism | Main-process consequence | Required correction |
|---|---|---|---|
| RC-1: no canonical project input | Service batch accepts several aliases, React emits another shape, imports define another row model, and columns have a separate defaulting route | The same project data can mean different values by entry path | One versioned, strict project schema shared by service and transports |
| RC-2: coercion is mixed with assumption | Missing, empty, or malformed values fall through `_to_float` or UI/Pydantic defaults | The software can calculate a default member and return a plausible PASS | Parsing must fail closed; structural defaults may exist only in explicitly named examples/templates |
| RC-3: import success does not account for every row and field | First-match adapter selection, invalid-row skips, invalid-force-to-zero behavior, and soft unmatched records | Source data can disappear without preventing a project verdict | Explicit/deterministic format selection plus a lossless row-and-field ledger |
| RC-4: orchestration is duplicated | Service batch, streaming, import batch design, React preparation, and column routes each normalize or derive values | Effective depth, materials, identity, and errors differ by route | Transports delegate to one service boundary and never derive structural values |
| RC-5: result/review semantics are not one contract | PASS/FAIL/HOLD, calculation success, review status, errors, and slab wording vary by element | A consumer can confuse software completion with engineering acceptance or professional review | One result envelope with orthogonal intake, calculation, engineering, and review states |
| RC-6: release truth tests happy paths, not the advertised product | Version surfaces, examples, export classifications, exact-wheel negative paths, and source identity are not one gate | Green CI can coexist with stale or unsafe published guidance | Machine-checked API inventory, executable documentation, negative UAT, and exact artifact evidence |
| RC-7: advertised-entry-point inventory was incomplete | A-G covered service, imports, HTTP/SSE/React, and selected exact-wheel examples but did not bind `python -m structural_lib design` to the same acceptance matrix | A public CLI can retain the original row-loss/defaulting hazard while all declared A-G checks pass | Generate the advertised entry-point inventory from docs/CLI/API surfaces and require every calculation-bearing entry point to delegate to the canonical boundary or be explicitly held |
| RC-8: workflow interpreter identity was implicit | Full scheduled/tag suites invoke tests that recursively call `run.sh`/`python_runtime.sh`, but `actions/setup-python` creates neither a repository `.venv` nor `VIRTUAL_ENV`; the affected workflows omit the supported `STRUCTURAL_LIB_PYTHON` binding | Exact source can pass PR checks while the broader scheduled or publication suite deterministically fails before exercising its intended controls | Export the exact `command -v python` path for every full-suite workflow step that can invoke repository launchers; retain fail-closed launcher behavior and enforce the workflow contract in tests |
| RC-9: release modes share one verdict label | Pre-bump validation may have no wheel, exact review, hosted receipt, or authorization, yet zero local test errors prints `READY TO RELEASE` | A maintainer can mistake permission to prepare a candidate for permission to publish | Give pre-bump, exact-candidate, and publication modes distinct machine-readable verdicts; only the final mode may report publication readiness |

## 4. Outcome-changing issue register

Priority means publication impact, not code size. `P0` blocks the next public
package. `P1` blocks stable/professional-readiness claims or a claimed product
surface. `P2` is required before the related capability is advertised.
Rows from G0 preserve the original defect wording; Section 2.3 and each packet's
`State` line own the current post-fix classification.

| ID | Pri | Original or current confirmed issue | Evidence location | Exit condition |
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
| CLI-01 | P0 | Advertised `python -m structural_lib design` bypasses the lossless import and strict project command; its CSV reader applies hidden cover/depth assumptions and skips malformed rows | `Python/structural_lib/__main__.py`, `services/excel_integration.py` | CLI delegates to the lossless ledger plus strict project command; every source row is accepted or blocked, hidden structural defaults are absent, and any blocked row makes the command non-zero with no PASS summary |
| CLI-02 | P0 | The current `design` CLI writes a `beams` artifact consumed by `bbs`, `detail`, and `dxf`, while the strict project service returns a different `members` envelope; warnings also contaminate stdout | `Python/structural_lib/__main__.py` and downstream CLI commands | Freeze a versioned CLI output/compatibility contract; diagnostics use stderr; valid JSON remains machine-readable; blocked input emits no partial-success artifact; exact-wheel tests prove advertised downstream consumers or explicitly deprecate/hold them |
| REL-UAT-02 | P0 | The 19-case matrix passes without executing the advertised design CLI, so it cannot detect CLI-01 | `services/release_uat.py`, packaged matrix, publish workflow | Exact-wheel UAT discovers all advertised calculation entry points and runs valid, malformed, mixed-validity, empty, and unknown-field CLI cases in a source-free environment |
| REL-CI-01 | P0 | Weekly Verification run `31988837003` failed six full-suite tests at A-G merge `fe4ab025...`: repository subprocesses could not find a project interpreter because the workflow did not export `STRUCTURAL_LIB_PYTHON`; the publish workflow has the same full-suite environment gap | `.github/workflows/nightly.yml`, `.github/workflows/publish.yml`, `scripts/python_runtime.sh`, workflow-contract tests | Scheduled and tag-publication full suites inherit the exact setup-python executable through the supported environment contract; no `.venv` assumption is introduced; workflow-contract tests and a fresh hosted full run pass |
| REL-PREFLIGHT-01 | P0 | Pre-bump `release preflight 0.23.1a2` printed `READY TO RELEASE` with no exact wheel while exact authorization remained `HOLD` and the CLI negative was outside UAT | `scripts/release.py`, release-script tests, release-preflight skill | Pre-bump success says only `READY_TO_PREPARE_CANDIDATE`; exact-wheel success says `CANDIDATE_TECHNICALLY_READY` plus explicit remaining holds; `READY_TO_PUBLISH` requires exact wheel/UAT, immutable review and hosted receipts, and exact target authorization |
| PUBLISHED-01 | P0 | PyPI `0.23.1a1` predates A-G, displays the wrong exact pin, and advertises a batch example that fails against its own wheel | [live PyPI 0.23.1a1 page](https://pypi.org/project/structural-lib-is456/0.23.1a1/) and installed-wheel replay | Do not imply A-G fixed the old artifact; the next separately authorized version must publish the corrected executable description and pass exact-wheel examples before upload |
| INSTALL-01 | P1 | Repository operation depends on the selected `.venv`, while beginner guidance does not provide one decisive preflight and repair path | setup docs/runtime guidance | One documented command reports interpreter, installed extras, package origin/version, and a clear install command without repository-only assumptions |
| API-NAME-01 | P1 | The 168-symbol service facade still includes 28 functions with unit-ambiguous parameter names such as `b`, `d`, `fck`, `fy`, `cover`, or `span`; several are compatibility aliases mixed into recommended functions | installed-facade signature audit | Each symbol is classified as canonical explicit-unit, compatibility-only, or internal; recommended APIs use unit-bearing names and compatibility aliases have a removal/migration policy |
| RETURN-01 | P1 | Several recommended exports still return generic dictionaries or positional tuples, including the unified column workflow | installed-facade signature audit and `api-levels.md` | Public workflow results use named typed contracts with schema/version/issue/review metadata; compatibility shapes are isolated and documented |
| SERVICE-01 | P1 | The tested slab result passes only the basic span/depth screen and explicitly holds direct deflection, cracking, shear, load combinations, continuity, cantilevers, and patterns | one-way slab result limitations | Stable/engineering-use claims name these holds prominently or add separately source-backed implementations and benchmarks |
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
2. REL-TRUTH-01, REL-EXAMPLE-01, REL-UAT-01, CLI-01, CLI-02, REL-UAT-02,
   REL-CI-01, REL-PREFLIGHT-01, PUBLISHED-01, and CLAIM-01 are accepted against
   the exact candidate wheel in a source-free environment and the matching
   hosted source commit.
3. The candidate describes only its bounded component capabilities. A missing
   whole-building workflow is an explicit limitation, not an implied feature.
4. Focused, quick, cumulative Python/FastAPI/React, packaging, protected-source,
   and all required hosted checks pass on one immutable reviewed head.
5. The exact wheel hash, source tree, test results, known holds, and independent
   exact-head software/release-evidence review receipt are bound in release
   evidence. This Alpha review is not qualified structural-engineering review
   or professional approval.
6. Pre-bump validation reports only readiness to prepare a candidate. Exact-
   wheel validation reports technical candidate readiness and every remaining
   hold. Neither state is publication readiness.
7. The repository owner separately authorizes the exact version/tag/package
   publication after immutable review. Only then may the final gate report
   `READY_TO_PUBLISH`. This plan is not that authorization.

### 5.2 Stable or engineering-use gate

In addition to the Alpha gate, stable or engineering-use language requires:

- API-CLASS-01, API-DOC-01, ASSUME-01, INSTALL-01, API-NAME-01, RETURN-01,
  and SERVICE-01 acceptance;
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
| CLI file with one valid and one invalid row | file BLOCKED and both rows accounted | no project verdict is emitted | non-zero exit; never a partial PASS summary |
| CLI file missing cover or effective-depth basis | BLOCKED | NOT_EVALUATED | no hidden 40 mm cover or `D-cover` depth |
| Valid CLI `design` artifact | VALID and versioned | COMPLETED | JSON is parseable and accepted by each advertised downstream command, or that command is explicitly held/deprecated |
| Geometry without forces / forces without geometry | BLOCKED unless explicit exclusion | NOT_EVALUATED | unresolved identity listed |
| Unapproved footing basis | BLOCKED/HOLD | per bounded contract | never promoted by a flag alone |
| Insufficient footing dowel length | VALID | COMPLETED | FAIL retained |
| Safe supported calculation | VALID | COMPLETED | PASS plus qualified review required |

Release-control cases are orthogonal to structural input cases and must also
fail closed:

| Release-control case | Required verdict | Required evidence |
|---|---|---|
| Pre-bump checks, no exact wheel | `READY_TO_PREPARE_CANDIDATE` | Valid version upgrade and green affected local suites; wheel/review/hosted/authorization explicitly pending |
| Exact wheel, UAT or public example fails | `NOT_READY` | Exact failing artifact and case; no publication action |
| Exact wheel passes, authorization absent or `HOLD` | `CANDIDATE_TECHNICALLY_READY` plus `PUBLICATION_HOLD` | Wheel/source identities, exact UAT, independent receipt, hosted receipts, and missing authorization fields |
| Scheduled/full hosted interpreter unresolved | `NOT_READY` | Failing workflow/job and interpreter-resolution diagnostic |
| Exact version/tag/targets authorized after immutable review | `READY_TO_PUBLISH` | Authorization JSON and SHA-bound review receipt match version, tag, targets, source/Python trees, reviewer, chronology, and hosted checks |

## 8. Dependency-ordered implementation packets

WIP remains at most two, but these packets are implemented by one writer in
dependency order wherever files overlap. Parallel agents are most useful for
read-only audit and immutable review, not competing edits.
Packet H was already reserved for the whole-building decision. Newly found
Packets I and J are listed before H because both are publication prerequisites;
J also becomes H's immediate predecessor.

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

**State:** merged through PR #814 and retained in the A-G merge at PR #815.

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

**State:** merged through PR #815; post-fix replay accepted the covered import
cases.

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

**State:** merged through PR #815 for HTTP/SSE/React. The advertised CLI was
outside Packet C and is now assigned to Packet I.

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

**State:** merged through PR #815; post-fix slab, column, beam, and footing
replays retained required-review and fail-closed semantics.

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

**State:** merged through PR #815; post-fix replay retained assumed basis and
identity separation.

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

**State:** merged through PR #815. Export classification is substantially
better; API naming and typed-return closure remain stable-release work.

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

**State:** merged through PR #815 after the exact-review-receipt repair. The
post-fix replay found a separate scope gap: the 19-case matrix does not execute
the advertised design CLI.

**Depends on:** A through F.
**Owns:** release preflight, publish workflow, source-free example runner,
release evidence schema, policy tests.
**Deliver:** exact-wheel execution of advertised examples and Section 7; split
Alpha versus stable gates; immutable artifact/source/test receipts; explicit
owner authorization stop. The authorization record must resolve a JSON review
receipt under `docs/verification`, verify its SHA-256, reviewed head/tree and
Python package tree, version/tag/targets, reviewer independence, ancestry, and
an evidence-only post-review delta before any publication target can run.
**Focused proof:** intentionally unsafe fixture fails preflight; exact candidate
wheel passes public examples and supported end-to-end workflows without source
checkout imports.
**Accept:** REL-EXAMPLE-01, REL-UAT-01, remaining REL-TRUTH-01 close. Run broad
Python, complete FastAPI/React, full canonical, packaging, protected-source,
hosted checks, and immutable independent review once at this cumulative
boundary.
**Rollback:** release remains held; never weaken the negative matrix to make a
candidate pass.

### I — Advertised CLI convergence (`LIB-PRO-002-I`, M)

**State:** implemented on the Packet I candidate from `b3a9c367`; 150 focused
CLI/import/batch/UAT tests pass. Immutable review, hosted checks, and unchanged-
head merge remain before Packet J starts.

**Depends on:** A through G.
**Owns:** the `design` CLI intake/orchestration path, its CSV/JSON compatibility
boundary, packaged negative-UAT entry-point inventory, focused CLI tests, and
directly affected documentation.
**Deliver:** `python -m structural_lib design` delegates to the lossless import
ledger and strict project command; every row and calculation-bearing field is
accounted; no cover, effective depth, material, load, or identity is silently
created; mixed-validity and empty files return non-zero without a partial PASS
summary. Freeze a versioned CLI output/compatibility contract before changing
orchestration: JSON output remains machine-readable, diagnostics go only to
stderr, and valid `design` artifacts remain consumable by advertised `bbs`,
`detail`, and `dxf` commands unless a command is explicitly deprecated and held.
Generate or validate one advertised calculation-entry-point inventory so future
CLI/API/transport additions cannot be omitted from exact-wheel UAT.
**Focused proof:** canonical valid CLI input preserves the one-storey beam
result; malformed-only, mixed valid/invalid, empty, missing-cover/depth,
non-finite, unknown-field, duplicate-ID, and ambiguous-format files block in
source and exact-wheel environments. The old PyPI batch example is explicitly
recorded as historical/broken; stdout JSON is parsed; valid `design` output is
passed through every retained downstream command; and the next package
description is executed from the candidate wheel.
**Accept:** CLI-01, CLI-02, REL-UAT-02, and PUBLISHED-01 close. Run the affected
CLI/import/service/downstream tests together, the expanded matrix, quick gate,
normal hooks, immutable review, and required hosted PR checks on the frozen
Packet I head. Defer the next broad Python/FastAPI/React and full canonical run
to the Packet J cumulative boundary. Publication still requires J and separate
owner authorization.
**Rollback:** retain publication HOLD; do not restore row skipping or hidden
defaults for compatibility.

### J — Release signal convergence (`LIB-PRO-002-J`, S)

**State:** required after Packet I because live hosted and local preflight
evidence currently disagree about publication readiness.

**Depends on:** I.
**Owns:** full-suite interpreter binding in scheduled/tag workflows,
mode-specific release-preflight verdicts, workflow/release-script contract
tests, and directly affected release guidance.
**Deliver:** reuse the already-supported
`STRUCTURAL_LIB_PYTHON="$(command -v python)"` contract in every hosted full-
suite step that can recursively invoke repository launchers, including Weekly
Verification and publish validation. Do not weaken `python_runtime.sh` to trust
an arbitrary system interpreter. Split pre-bump, exact-wheel, and final
publication states: pre-bump may report only `READY_TO_PREPARE_CANDIDATE`;
exact-wheel success reports `CANDIDATE_TECHNICALLY_READY` and explicit holds;
only exact authorization after immutable review can report
`READY_TO_PUBLISH`.
**Focused proof:** workflow-contract tests fail if a full suite lacks the
interpreter binding; release-script tests cover every verdict/exit-code
combination for missing wheel, failed UAT, absent review, `HOLD` authorization,
wrong version/tag/target, and complete exact authorization. Run Weekly
Verification by manual dispatch on the exact remote Packet J head and require
the full Python, FastAPI, React, documentation, and summary jobs to pass.
**Accept:** REL-CI-01 and REL-PREFLIGHT-01 close. After focused evidence freezes,
run quick, hooks, broad Python, complete FastAPI/React, full canonical,
packaging, protected-source, expanded exact-wheel UAT/public examples,
immutable review, all required hosted PR checks, and the manually dispatched
full workflow. Publication remains `HOLD` until an exact release candidate and
separate owner authorization exist.
**Rollback:** keep the strict launcher and publication HOLD; never recover a
green label by bypassing interpreter identity, wheel evidence, review, hosted
checks, or authorization.

### H — Whole-building workflow decision (`LIB-PRO-002-H`, planning only, L)

**State:** not activated. Completing A-J does not activate this packet or
authorize whole-building implementation.

**Depends on:** J and separate owner activation.
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
6. Packet I runs its focused/quick/hosted packet gates after content freeze.
   Reserve the next broad Python/FastAPI/React and full canonical gates for the
   frozen Packet J cumulative boundary unless an outcome-changing failure
   proves repository-wide risk earlier.
7. Use one candidate and at most one repair candidate. A material post-push
   defect creates a new reviewed candidate; status prose does not mutate the
   immutable head.
8. Finish task, session, handoff, evidence, and pre-commit receipt first. Write
   affected indexes last, then validate without rewriting them.
9. Independently review each exact commit/tree and bind hosted checks before
   merge. For J, manually dispatch Weekly Verification on the exact remote head
   and bind that full-workflow receipt as well.
10. Report total wall time including CI and closeout so later estimates improve.

For a future publication, review the complete package candidate first. The
owner may then add the authorization and exact-review receipt in one descendant
evidence commit, but only the authorization/receipt and their maintained
`docs`/`docs/verification` indexes may differ. The release gate proves the
reviewed Python tree is unchanged; any other post-review path change blocks.

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

## 11. Cumulative candidate record and exact next step

G0 has now frozen:

- the bounded interpretation of the one-storey pilot;
- nine root causes and an outcome-changing issue register;
- canonical input, import-ledger, result, and compatibility contracts;
- Alpha/stable/whole-building release boundaries;
- an implementation order through Packet J followed by the held Packet H
  decision, with an implementation-first cumulative test cadence.

Packet A merged through PR #814 and Packets B-G merged through PR #815 at
`fe4ab025419b834c6d0f840e9492c0604ae74201`. The post-fix replay accepts the
original covered service/import/transport/result/evidence/API cases and the
one-storey arithmetic, but it rejects publication readiness because the public
design CLI still skips malformed rows and the exact-wheel matrix omits that
entry point.

The exact next implementation sequence is `LIB-PRO-002-I` followed by
`LIB-PRO-002-J`. Packet I converges the advertised CLI on the lossless/strict
boundary, adds CLI cases to source-free exact-wheel UAT, and proves the
candidate package description. Packet J binds the selected interpreter in
scheduled/tag full suites and makes release-preflight verdicts accurately name
pre-bump, technical-candidate, and authorized-publication states. These repair
acceptance and release-signal scope; they do not imply A-G failed everywhere.

Packet H remains inactive because the owner has not separately activated a
whole-building planning program. Even after Packets I-J are accepted, publication
remains blocked until the owner separately authorizes the exact future version,
tag, and publication targets recorded by
`docs/verification/release-publication-authorization.json`.

While Packets I-J are unresolved, the release state is:

`NEXT_PUBLICATION = HOLD_ADVERTISED_CLI_HOSTED_SIGNAL_AND_OWNER_AUTHORIZATION`
