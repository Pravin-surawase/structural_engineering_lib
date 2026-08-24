# GitHub Workflows

MAINT-008 consolidates repository automation into four lanes. Codex owns scoped
maintenance, diagnosis, implementation, review, and GitHub operations; GitHub
Actions supplies independent, repeatable verification and controlled publication.

## Pull request gate

`fast-checks.yml` is the only workflow triggered by pull requests. It creates these
checks:

| Check | When it runs | Evidence |
|---|---|---|
| `Detect Changes` | Every PR | Loads the canonical seven-domain manifest; unknown impact selects all domains |
| `Repository Validation` | Repository-policy inputs | YAML, hygiene, and maintenance-script contracts |
| `Python Validation` | Python inputs | Format, lint, types, contracts, focused core tests, architecture policy |
| `FastAPI Validation` | API or deployment inputs | Format, lint, API tests, architecture, contracts, Docker/OpenAPI configuration |
| `React Validation` | React inputs | Lint, production build, and Vitest |
| `Excel Add-in Validation` | Excel add-in inputs | Complete dependency-free Node test suite |
| `Control Plane Validation` | Agent, script, session, Git, or workflow controls | Registries, CLI/reference policy, and exact control regression set |
| `Documentation Validation` | Documentation or imported API-doc inputs | Versions, task format, links, and strict MkDocs build |
| `PR Gate` | Every PR, with `if: always()` | Rejects any failed or cancelled applicable job |

Checks may be skipped only when the canonical impact plan marks their domain
unchanged. `scripts/verification-manifest.json` owns the path rules used by both
local commands and this workflow; there is no second YAML filter list. Unknown
paths or Git-query failures select all seven domains. `PR Gate` rejects missing
applicability values, partial fail-closed plans, and skipped applicable jobs.
The same rules also define each domain's fingerprint inputs, preventing a
scheduler/evidence ownership drift.

Every applicable job resolves its runtime and dependencies before computing an
evidence identity. An exact-key `actions/cache` entry may then skip only the
validation body, and only after the restored PASS receipt independently matches
the current command, runtime/dependency identity, and domain input bytes. Cache
misses, malformed receipts, partial keys, failed runs, and changed inputs execute
normally. The cache never uses prefix restore keys.

For example, `Excel Add-in Validation` is expected to show `skipped` when the
plan marks `excel` unchanged—normally when no `excel_addin/**`, `.nvmrc`, or
shared verification-control path changed. That is a successful classification
outcome, not missing validation: `PR Gate` verifies both the planner result and
the skip. A cross-product safety packet that relies on unchanged Excel behavior
still runs the complete local Excel suite when its acceptance contract requires
that evidence; the planned hosted job does not replace that local proof.

The active main-branch ruleset requires `PR Gate`. Do not rename that check without
updating and verifying the ruleset in the same approved operation.

## Retained lanes

| Workflow | Trigger | Responsibility |
|---|---|---|
| `fast-checks.yml` | Pull requests and short main-branch verification | Manifest-planned Python, FastAPI, React, Excel, control, docs, and repository validation with required `PR Gate` |
| `nightly.yml` | Weekly schedule and manual dispatch | Full Ubuntu verification, clean-wheel/CLI checks, dependency audits, Docker health, and optional manual cross-platform smoke |
| `publish.yml` | Version tag or manual dispatch | Build/install/SBOM verification; exact independent-review receipt or explicit repository-owner review waiver; manual TestPyPI publication; tag-only production PyPI and GitHub Release |
| `deploy-docs.yml` | Relevant main-branch documentation changes or manual dispatch | Strict MkDocs build validation; no public deployment until the owner enables and verifies GitHub Pages |

All workflows default to read-only repository contents. Only publication jobs
receive the narrower write permissions required for their specific operation.
The documentation workflow is build-only until GitHub Pages is explicitly
enabled and verified by the owner. Weekly verification cannot create or close
issues.

## Superseded workflow mapping

| Removed workflow | Essential signal retained or disposition |
|---|---|
| `auto-format.yml` | Black and Ruff checks run in `fast-checks.yml` and `nightly.yml` |
| `codeql.yml` | Standalone SAST lane parked; dependency audits and existing local security checks remain |
| `docker-build.yml` | Docker build, health, readiness, and Compose validation run weekly/manual in `nightly.yml` |
| `git-workflow-tests.yml` | Shell syntax and migration-script tests run in `fast-checks.yml` |
| `governance-health.yml` | No main-process gate; repository policy checks remain in `fast-checks.yml` |
| `leading-indicator-alerts.yml` | No main-process gate; issue and PR write automation removed |
| `link-check.yml` | Internal link validation runs in both verification lanes |
| `performance.yml` | Standalone baseline/comment reporting is parked; executable latency and degradation thresholds remain in `fastapi_app/tests/test_load.py` and run in the full FastAPI/Python verification surfaces |
| `python-tests.yml` | Full Python, FastAPI, React, coverage, drift, and clean-wheel checks run in `nightly.yml` |
| `root-file-limit.yml` | Repository hygiene remains in the local quick gate |
| `sbom.yml` | CycloneDX release asset is generated and attached by `publish.yml` |
| `scorecard.yml` | Standalone scorecard reporting parked |
| `security.yml` | Locked Python and production npm audits run in `nightly.yml` |

Use `./run.sh check --quick` before committing and the full `./run.sh check` once at
MAINT-008 closeout. Do not bypass a failing `PR Gate`.
