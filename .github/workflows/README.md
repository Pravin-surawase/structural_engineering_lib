# GitHub Workflows

This directory is being consolidated by MAINT-008. Codex owns scoped maintenance,
diagnosis, implementation, and review; GitHub Actions supplies the independent,
repeatable evidence required before a merge.

## Pull request gate

`fast-checks.yml` is the only workflow triggered by pull requests. It creates these
checks:

| Check | When it runs | Evidence |
|---|---|---|
| `Detect Changes` | Every PR | Classifies Python, FastAPI, and React inputs |
| `Repository Validation` | Every PR | YAML, docs, scripts, architecture, and agent-control policy |
| `Python Validation` | Python inputs | Format, lint, types, contracts, focused core tests, architecture policy |
| `FastAPI Validation` | API or deployment inputs | Format, lint, API tests, contracts, Docker/OpenAPI configuration |
| `React Validation` | React inputs | Lint, production build, and Vitest |
| `PR Gate` | Every PR, with `if: always()` | Rejects any failed or cancelled applicable job |

The component checks may be skipped when their layer is unchanged. `Repository
Validation` never skips, so a docs-only or control-plane PR still receives real
validation. `PR Gate` checks each component result against the detected paths; a
skipped applicable check cannot produce a green gate.

The active main-branch ruleset still requires `Quick Validation (Python 3.11 only)`
until the owner separately approves switching it to `PR Gate`. Do not rename the
new check after that switch.

## Legacy check mapping

Packet A removes duplicate pull-request triggers but does not delete workflows.
Packet B will consolidate the remaining scheduled, main-push, manual, and release
lanes.

| Previous PR workflow | Packet A disposition |
|---|---|
| `auto-format.yml` | Python format and Ruff checks retained in `Python Validation`; old workflow is manual only |
| `git-workflow-tests.yml` | Shell syntax and migration-script checks retained in `Repository Validation`; main-push lane remains for Packet B |
| `link-check.yml` | Internal link checks retained in `Repository Validation`; external link scan remains scheduled/main-push for Packet B |
| `root-file-limit.yml` | Parked from PRs; repository hygiene remains in the local/Codex quick gate |
| `codeql.yml` | Scheduled/main-push security analysis retained for Packet B |
| `docker-build.yml` | FastAPI configuration checks retained on PRs; full image build remains main-push/manual for Packet B |
| `performance.yml` | Expensive benchmark lane retained on main/schedule/manual for Packet B |
| `security.yml` | Dependency audits retained on main/schedule/manual for Packet B |
| `leading-indicator-alerts.yml` | Removed from PRs; governance signal remains scheduled/main/manual pending Packet B noise review |

## Current workflow inventory

There are 17 workflow files at the end of Packet A. Only `fast-checks.yml` handles
pull requests. The intended Packet B end state is four active lanes unless an
owner-approved main-process reason requires another:

1. pull-request validation;
2. scheduled and manual full verification;
3. approved release publication;
4. documentation deployment.

Use `./run.sh check --quick` before committing and the full `./run.sh check` once at
MAINT-008 closeout. Do not bypass a failing `PR Gate`.
