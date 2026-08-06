---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: reference
complexity: advanced
tags: [maintenance, recovery, audit, mac-mini, v0.21.7]
---

# Maintenance Recovery Audit — 2026-08-07

## Outcome

The repository and product source survived the Mac laptop → Mac Mini transfer.
The main risk was not missing source code; it was a mixture of inherited
uncommitted work, stale local runtimes, transferred VM state, expired GitHub
credentials, dependency drift, and governance scanners that disagreed.

The inherited work is preserved on `task/MAINT-001`. Local application,
package, test, documentation, and maintenance gates are green. Two external
control-plane blockers remain: GitHub CLI authentication and Colima's
transferred VZ disk state.

## Audit scope

The audit used folder indexes and registries first, then inspected the source,
configuration, onboarding, agent instructions, skills, planning records, CI,
dependencies, test suites, generated manifests, schemas, sample data, Git
objects, symlinks, and migration records relevant to the current architecture.

| Surface | Evidence |
|---------|----------|
| Git and transfer | Reachable objects valid; local/remote `main` both `fa854e0f`; ETABS samples present; no broken symlinks or submodules |
| Python package | Editable source/module metadata agree at v0.21.6; clean Python 3.11 install works |
| Core tests | 5,146 collected; 5,138 passed, 8 skipped |
| FastAPI | 326 tests pass; 60 routes across 13 routers |
| React | 139 tests pass; lint has two pre-existing hook warnings; production build passes on Node 24 |
| Live data flow | 18/18 import E2E checks and 153/153 sample beams pass |
| Documentation | 1,059 internal links checked after archival; zero broken |
| Canonical maintenance | `run.sh check` 28/28; audit 22/22; health 100/100 |
| Parity | 15/17 curated clause areas; 52/60 direct route tests; 13/13 connected hooks; actionable score 92% |

## Completed maintenance

### MAINT-001 — preservation and environment recovery

- Preserved the inherited April worktree in pushed checkpoint `b28ee4e3`.
- Repaired editable package metadata and pinned Python 3.11.15/Node 24.
- Documented the Colima VZ disk blocker and prohibited destructive VM recovery
  until data is backed up or deletion is explicitly approved.

### MAINT-002 — nightly and import contracts

- Removed the unsupported nightly link-checker flag.
- Updated maintained E2E scripts for the standard `{success, data}` envelope.
- Archived the removed Streamlit import pipeline and repaired active references.
- Restored the quick gate to 8/8 and import validation to 3,248/3,248 imports.

### MAINT-003 — dependency and security baseline

- Rebuilt Python declarations and lock data from a clean environment.
- Raised vulnerable dependency floors and added the missing `pytest-asyncio`
  declaration; clean `pip check` and `pip-audit` pass.
- Reduced npm findings from 13 to one underlying React Router RSC-only
  advisory, recorded with an exact CI allowlist and removal condition.
- Expanded Dependabot and CI audits across root Python, package Python, npm,
  and GitHub Actions. See `docs/planning/dependency-security-baseline.md`.

### MAINT-004 — canonical truth and governance

- Repaired API introspection, manifests, schema snapshots, indexes, bootstrap
  counts, import/document/audit/health scanners, and `run.sh parity` routing.
- Corrected parity semantics: Python-only public functions are informational,
  parameterized routes match concrete test URLs, and slab/footing clauses are
  labeled accurately.
- Safely archived the historical agent audit and completed unified CLI plan.
- Resolved 13 historical feedback items with repository evidence; retained one
  tester-output recurrence watch at occurrence two of threshold three.
- Safely removed tracked placeholder `scripts/_tmp_write_days.py`; a recovery
  copy exists in ignored `tmp/deleted_backups/`.

## Open findings

| Priority | Finding | Decision / next action |
|----------|---------|------------------------|
| P0 external | GitHub CLI credentials expired | Rerun `gh auth login` and complete browser authorization; SSH push already works |
| P0 external | Colima VZ disk reports “in use” after orphan cleanup | Restart macOS, retry non-destructively, then back up VM data before considering recreation |
| P1 tests | Eight routes lack direct FastAPI tests | MAINT-005: six column routes plus `/rebar/validate` and `/rebar/apply` |
| P1 frontend | React statement coverage is 17.74% | Cover the critical import → design → 3D → export flow before broad percentage chasing |
| P1 release | v0.21.7 finish line is not approved | Define exit criteria from verified security, route, browser, and packaging evidence |
| P2 security | React Router RSC-only advisory remains | Keep exact CI exception only while the Vite browser app has no RSC; remove on patched release |
| P2 product | Slab design and Annex D remain planned | Keep outside stabilization unless the owner explicitly changes scope |
| P3 agent | Tester empty-output seen twice | Keep watch item open; update instructions on a third recurrence |

## Maintenance sequence

1. Preserve the current green local baseline and commit through
   `scripts/ai_commit.sh`.
2. Complete MAINT-005 route tests and the critical browser workflow.
3. Recover GitHub authentication and create the PR without bypassing checks.
4. Restart the Mac Mini and retry Colima; do not delete the transferred disk.
5. Approve an evidence-based v0.21.7 release scope before feature work resumes.

## Guardrails retained

- No manual Git commits, force pushes, CI bypasses, or destructive GitHub
  operations.
- No bulk formatting or cleanup of inherited work.
- No automatic dependency or health fixes without reviewing the proposed diff.
- No VM deletion without a backup and explicit owner approval.
- Keep `TASKS.md`, `WORKLOG.md`, `SESSION_LOG.md`, project memory, and the next
  session brief synchronized at each checkpoint.
