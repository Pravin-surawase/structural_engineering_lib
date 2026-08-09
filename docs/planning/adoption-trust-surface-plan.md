---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: spec
task: ADOPT-001
title: ADOPT-001 Adoption and Trust Surface Plan
---

# ADOPT-001 — Adoption and Trust Surface Plan

## 1. Outcome

Make the released Alpha straightforward to evaluate from four perspectives:

- a user can copy every public quick start and receive the documented result;
- an AI or generated client can discover supported cases, units, limitations, and
  response shapes without guessing;
- an interviewer can distinguish the calculation kernel, beam workbench, and
  engineering-approval boundary quickly;
- a company can run a pinned internal pilot without accidentally exposing an
  unauthenticated production API or losing calculation identity.

The finished work must improve the truth and usability of the existing product.
It must not add structural formulas, widen supported cases, or claim qualified
engineering approval.

## 2. Main-process contract

```text
public documentation or machine client
    -> Python / CLI / REST entrypoint
    -> declared IS 456 capability and units
    -> calculation and detailing result
    -> PASS / FAIL / HOLD plus governing check
    -> versioned evidence identity
    -> React review or exported artifact
```

A finding belongs in this plan only when fixing it changes the reliability,
interpretability, or safe adoption of that process.

## 3. Verified starting problems

1. `docs/reference/api-levels.md` contains a column call that the public v0.23.0
   package rejects, documents `.is_safe()` instead of `.is_ok`, and sends the
   wrong field names to the beam REST endpoint.
2. `docs/reference/fastapi-rest-api.md` documents beam response fields outside
   the maintained `success` / `data` envelope and contains stale version output.
3. README snippet tests cover only two examples and do not execute the public API
   selection guide or REST reference.
4. The FastAPI OpenAPI document has 62 HTTP operations, but most success
   responses do not identify a useful response schema for generated clients.
5. `get_supported_is456_capabilities()` is a strong semantic source, but it is
   not available as a stable JSON CLI/REST discovery contract and `llms.txt`
   still describes an older beam/VBA-centered product.
6. Local Python, CLI, REST, and UI surfaces use related but non-identical field,
   enum, and status representations. Consumers must infer conversions.
7. Docker requires a JWT secret but does not enable authentication or production
   mode, while application settings default to open local-development behavior.
8. The live bundled sample and an older durable record report different BOQ
   totals. The accepted value cannot be chosen without binding the dataset and
   calculation version that produced it.
9. Results and exports do not yet share one default evidence envelope containing
   artifact version, code edition, capability ID, input hash, units, and
   governing result identity.
10. GitHub Pages deployment can report a green workflow without a publicly
    enabled site. Repository release labels also distinguish the current Alpha
    inconsistently between PyPI and GitHub.

## 4. Recent-session incident review

The recent Codex tasks and repository history were checked before this plan:

| Incident | Current disposition |
|---|---|
| Agent brief used a mutable/stale handoff source | Fixed by PR #702; retain its regression |
| Health could not resolve Python in linked worktrees | Fixed by PR #703; retain its regression |
| Product-readiness work overlapped review sessions | PR #704 is merged; this work uses a new clean branch |
| A documented read-only closeout appeared to regenerate indexes | Reverify read-only behavior from a clean status before changing session tooling |
| A branch ref changed during a concurrent merge/push sequence | Avoid chained Git mutation; inspect status and ref before each Git action |
| zsh expanded unmatched globs and unquoted query strings | Use `rg --files` and quote literal `?`, backticks, and `$` patterns |
| Browser `networkidle` was unavailable in the selected control path | Use `domcontentloaded` plus an explicit settled-state assertion |
| `to_dict()` retained enum objects while `to_json()` worked | Normalize the public JSON contract; do not promise raw dict JSON safety meanwhile |

Only incidents that still reproduce in the main process will receive code
changes. Historical failures are not reopened merely to add hardening.

## 5. Protected areas and non-goals

Protected calculation paths:

```text
Python/structural_lib/core/
Python/structural_lib/codes/is456/
```

Non-goals:

- no formula, coefficient, benchmark, source-value, or unit-conversion changes;
- no new structural elements or supported engineering cases;
- no React redesign or adjacent UX cleanup;
- no migration to a new API version in this packet;
- no replacement of the maintained response envelope;
- no claim that passing software tests certifies IS 456 accuracy;
- no stable-release, engineering-use, or professional-approval claim;
- no issue closure, PR merge, release, tag, or publication without explicit owner
  approval;
- no rewriting Git history or automatic recovery from concurrent branch changes.

If implementation appears to require a protected calculation edit, stop that
packet and return to the plan.

## 6. Execution rules

1. Execute packets in dependency order. Packet A must pass before machine-facing
   contracts are generated from the same truth.
2. Keep one parent task active. Use no subagents unless a later packet is both
   independent and explicitly delegated.
3. Inspect folder indexes and use targeted `rg` before opening large files.
4. Fix the root contract source, then add the narrow regression that proves the
   public behavior.
5. During iteration run focused tests only. Run `./run.sh check --quick` before a
   commit and the full gate once at closeout.
6. Never update the OpenAPI baseline until the current schema diff has been
   reviewed and the intended response-schema additions are understood.
7. Preserve the existing `success` / `data` / `error` envelope and
   `PASS` / `FAIL` / `HOLD` semantics.
8. Git actions are separate commands with a fresh status/ref inspection. Do not
   chain merge, validation, push, and cleanup.
9. Record terminal failures in the handoff as
   `WARNING TERMINAL ISSUE: failure -> working fallback`.

## 7. Dependency-ordered packets

### Packet A — Executable public truth

**Objective:** every high-traffic Python and REST example executes against the
current public contract.

**Primary files:**

- `docs/reference/api-levels.md`
- `docs/reference/fastapi-rest-api.md`
- `Python/tests/test_packaging.py`
- `fastapi_app/tests/test_public_documentation_contract.py` (new if needed)

**Implementation:**

1. Replace the rejected column example with the actual axial-capacity signature,
   or use the maintained full-column endpoint when geometry/slenderness is the
   intended workflow.
2. Document `.is_ok`, `.to_dict()`, `.to_json()`, and `.summary()` accurately.
3. Use `width`, `depth`, `moment`, `shear`, `fck`, and `fy` in the beam REST
   example.
4. Document the response envelope and access beam data through `result["data"]`.
5. Refresh health/version examples from the application schema, not memory.
6. Add focused tests that execute the exact documented payloads and assert the
   documented keys.

**Narrow verification:**

```bash
.venv/bin/pytest Python/tests/test_packaging.py -k README -q
.venv/bin/pytest fastapi_app/tests/test_public_documentation_contract.py -q
.venv/bin/python scripts/validate_api_contracts.py
```

**Acceptance:** no copied public example raises, returns 422 unexpectedly, or
uses a response path absent from the real JSON.

**Rollback:** revert only the guide/test packet. No runtime response shape changes
belong in Packet A.

### Packet B — Canonical capability discovery

**Objective:** expose the existing supported/held semantic contract without
duplicating structural truth.

**Primary files:**

- `Python/structural_lib/services/capabilities.py`
- `Python/structural_lib/services/api.py`
- the existing CLI command registry under `Python/structural_lib/cli/`
- `fastapi_app/models/capabilities.py` (new if required)
- `fastapi_app/routers/library_core.py`
- `llms.txt`
- `docs/reference/api-manifest.json` generation path

**Implementation:**

1. Add one explicit JSON serialization method/model for capability records.
2. Add `python -m structural_lib capabilities --json`.
3. Add `GET /api/v1/library/capabilities` with a typed response envelope.
4. Generate or validate `llms.txt` and manifest claims from the same capability
   source where practical.
5. Include units, limitations, held cases, code edition, and qualified-review
   requirement.

**Acceptance:** Python, CLI, and REST return semantically identical capability
IDs and supported/held boundaries; no formula module imports UI/I/O code.

### Packet C — Typed REST success contracts

**Objective:** generated clients can model maintained success responses.

**Primary files:**

- `fastapi_app/models/response.py`
- `fastapi_app/models/common.py`
- router and model files selected per bounded batch
- `fastapi_app/openapi_baseline.json`
- `scripts/check_fastapi_issues.py`
- `scripts/validate_api_contracts.py`

**Implementation:**

1. Remove or reconcile duplicate generic response model definitions.
2. Preserve the runtime envelope while declaring `APIResponse[PayloadModel]` as
   `response_model`.
3. Start with health, beam design, library capability, and column axial routes.
4. Inspect the OpenAPI diff, then repeat in router batches until all maintained
   JSON routes have a useful 2xx schema or an explicit documented exemption.
5. Generate the frontend client only after the schema is stable.

**Acceptance:** all maintained JSON 2xx operations have a useful schema or a
reviewed exception; current React payload unwrapping and all endpoint tests pass.

**Pitfall:** FastAPI response filtering can remove undeclared fields. Tests must
prove the runtime JSON is unchanged before accepting each batch.

### Packet D — Production deployment fails closed

**Objective:** preserve convenient local development while preventing an
accidental public unauthenticated container deployment.

**Primary files:**

- `fastapi_app/config.py`
- `fastapi_app/main.py`
- `docker-compose.yml`
- `.env.example`
- `fastapi_app/tests/test_security.py`
- deployment documentation

**Implementation:**

1. Add an explicit environment/profile distinction.
2. Require `AUTH_ENABLED=true` for the production Compose profile or refuse
   production startup when authentication is disabled.
3. Keep loopback/local development behavior unchanged.
4. Document token provisioning and the local-evaluation profile.

**Acceptance:** local TestClient/dev startup still works; production-profile
startup without authentication fails with an actionable message; the configured
production profile starts only with auth and a non-default secret.

### Packet E — Evidence identity and serialization normalization

**Objective:** every consumable result can identify what produced it and whether
it is supported for the submitted case.

**Primary files:** existing calculation hash, certificate, provenance, result
serialization, report, and export modules discovered during packet intake.

**Required envelope fields:**

- package/artifact version;
- code edition and amendment identity;
- capability ID and supported/held status;
- explicit unit system;
- input/calculation hash;
- governing check and exact utilization;
- PASS/FAIL/HOLD;
- generated timestamp;
- qualified-review requirement.

**Acceptance:** Python JSON, REST JSON, and exported report metadata agree for one
safe and one unsafe beam without changing their calculations.

### Packet F — UI trust presentation and BOQ reconciliation

**Objective:** reviewers see exact safety margins and evidence identity, and the
bundled sample has one reproducible quantity record.

**Primary files:** current dashboard/result components and hooks found by
`rg`/folder indexes, bundled sample inputs, `docs/TASKS.md`, and evidence records.

**Implementation:**

1. Show unrounded governing utilization, margin, and check beside rounded status.
2. Prevent or visibly quarantine detailing/export actions when the outer result
   is FAIL/HOLD.
3. Re-run the canonical bundled sample from a clean state.
4. Record dataset hash, version, and calculation identity with the accepted BOQ
   totals; update durable evidence only after the discrepancy is explained.

**Acceptance:** a reviewer can trace dashboard totals and status back to the
exact sample and calculation identity; no green rounded `100%` obscures a limit.

### Packet G — Public repository/release coherence

**Objective:** public metadata describes one current Alpha accurately.

**Primary surfaces:** GitHub Pages settings/workflow, repository homepage,
release metadata, PyPI classification/versioning policy, and public docs.

**Implementation:**

1. Enable and verify GitHub Pages or remove the implication that the green deploy
   workflow publishes a usable site.
2. Adopt one prerelease convention: PEP 440 Alpha identifiers or ordinary stable
   releases, documented before the next version.
3. Keep qualified-review and stable-engineering-use approval separate.

**Owner-only actions:** Pages settings, release/tag/publication decisions, and PR
merge require owner confirmation.

## 8. Gate ladder

| Stage | Verification |
|---|---|
| Packet iteration | exact focused tests named in that packet |
| Before commit | `./run.sh check --quick` |
| PR | required `PR Gate` and relevant component lanes |
| Final code closeout | `./run.sh check`, `./run.sh audit`, `./run.sh health`, `./run.sh efficiency check` |
| User flow | clean wheel + CLI + TestClient + live React safe/unsafe paths |
| Release | separately authorized preflight only |

## 9. Stop conditions

Stop and return to the owner when:

- a packet needs a formula or benchmark change;
- API response filtering changes a production payload unexpectedly;
- the BOQ discrepancy cannot be tied to different input/version identity;
- a qualified-review claim would be required;
- Git state becomes conflicted, detached, behind/diverged, or changes during a
  mutation;
- a GitHub setting, merge, release, or publication action is required.

## 10. Initial branch and first deliverable

- Branch: `codex/trust-surface-foundation`
- Base: merged `main` commit `44e85587`
- First deliverable: Packet A plus this durable plan
- First commit intent: `fix(docs): make public API examples executable`
- No PR merge or release is authorized by this plan.
