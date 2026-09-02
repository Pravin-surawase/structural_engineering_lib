---
owner: Main Agent
status: active
last_updated: 2026-09-02
doc_type: spec
complexity: advanced
tags: [maintenance, pre-commit, ci, git, developer-experience]
---

# Commit and PR Validation Consolidation Plan

## Decision

Ordinary commits will become cheap save points. Required quality evidence will
be produced once for the complete batch by the pull-request workflow.

The target commit lane has exactly three hooks:

1. `check-merge-conflict`;
2. `check-added-large-files --maxkb=500`; and
3. `git_state.py --guard operation --allow-operation-completion`.

The first two prevent avoidable history damage. The third is not a code-quality
check: it observes the live local Git mutation boundary and blocks locks,
unresolved paths, unknown state and unfinished operations while retaining the
already-proved resolved-merge exception. A hosted runner cannot observe a
developer's `MERGE_HEAD`, index lock or rebase/cherry-pick/revert state, so this
single approximately 0.75-second guard remains local.

Everything else moves out of `git commit`: formatting, linting, type checking,
security scanning, tests, generated-artifact checks, documentation checks, API
parity and the ten-check quick gate. Developers may run a narrow reproducer or
formatter while working, but no broad local gate is mandatory per commit.

## Implementation status

The plan was implemented as two coherent commits on one candidate branch. The
first establishes complete hosted ownership and its machine-readable 34-hook
coverage map before any local control is removed. The second reduces ordinary
commits to the exact three guards above, retains eight manual-stage integrity
checks for PR Repository Validation, removes the duplicate `main`-push trigger,
and updates executable topology tests and active guidance. PR #949 accepted the
unchanged batched head through strict `PR Gate`; its merge did not start a
second `fast-checks.yml` run. PR #950 then exercised the policy on a real
three-commit feature batch and merged through one required hosted cycle.

## Post-implementation workflow and urgent hygiene record (2026-09-02)

### Working decision

- Keep multiple coherent commits on a milestone branch and publish them in one
  PR only after the batch freezes. The commits preserve reviewable internal
  history; the PR supplies the one required hosted assurance cycle.
- Use squash merge as the normal repository default so `main` receives one
  atomic milestone commit. Retain merge commits only for a future case that
  genuinely needs branch topology. Changing the GitHub merge settings is not an
  urgent performance action and remains deferred.
- Keep formatting, linting, typing, security, generated-contract checks and
  tests in the PR lane. Removing formatting would save little: PR #950 spent
  about 12 seconds in Python format/lint inside an approximately 156-second
  hosted cycle, while FastAPI was the longest job at about 132 seconds.
- Do not replace Black with Ruff formatting as incidental cleanup. A direct
  `ruff format --check Python` sample completed in 1.828 seconds but would
  reformat 52 files, so any migration must be a deliberate, isolated batch.

### Urgent work completed

1. Revalidated all 45 registered worktrees against live Git status, operation
   markers and GitHub PR state. Removed exactly 40 clean worktrees whose branch
   had a merged PR by using normal `git worktree remove`; no force option was
   used and all 40 local branch refs remained present. The retained baseline is
   five worktrees: `main`, two dirty user-work lanes and two clean lanes without
   merged-PR evidence. The short-lived documentation lane for this record is
   excluded from that before/after count and must be removed after acceptance.
2. Revalidated all GitHub Actions cache IDs against current PR state. Deleted
   exactly 266 caches scoped to closed or merged PR refs, totaling
   2,054,176,530 bytes in the deletion set. The converged live inventory fell
   from 568 to 302 caches and now totals 8,491,048,437 bytes: 252 `main`, 32
   open-PR and 18 other-branch caches. Zero closed/merged-PR caches remain.
3. Fast-forwarded the clean local `main` checkout from `44ef7bc4` to current
   `origin/main` at `742719dd`; the checkout remains clean.
4. Rechecked background activity. No task-owned Python, pytest, dev-server,
   Git, ETABS or Excel process needed cleanup. Codex/MCP helpers and Chrome
   Remote Desktop were preserved because they are active platform/session
   infrastructure, not stale project work.

### Preserved boundary

- No branch, open PR, dirty file, stash, user cache, artifact, dependency or
  active desktop process was deleted.
- No ETABS, Excel, COM, model, workbook, release or deployment action occurred.
- Required `PR Gate`, strict branch protection and the three commit-safety hooks
  remain unchanged.

### Deferred optimization backlog

1. Add a narrowly scoped Actions cleanup on PR close so merge-ref caches cannot
   accumulate again; prove that `main` and open-PR caches are excluded.
2. Optimize the FastAPI PR lane first: tighten maintained path ownership and
   cheap-contract ordering, then reduce install/test fan-out without weakening
   the strict final gate.
3. Review changed-only repository-integrity routing, artifact retention and the
   nine open Dependabot PRs as separate maintenance work.
4. Remove tracked `.vite` cache-like files only in an explicit source-control
   cleanup with link/build verification.
5. Consider a dedicated Ruff-format migration and squash-only repository
   setting later. Neither is required for the current performance outcome.
6. Continue process hygiene by ownership proof only; never stop Codex/MCP or
   remote-desktop infrastructure merely because it is long-lived.

## Why this supersedes the current task text

The current `.pre-commit-config.yaml` defines 34 hook entries, 11 of them
unconditional. A cross-surface commit activates about 28 entries, and the
`verification-quick` entry expands into ten more checks. Recent successful
quick-hook telemetry has a 20.992-second median over 20 events; fresh quick
runs have taken roughly 97.5-105.8 seconds. Those local results cannot satisfy
hosted evidence because local and hosted receipts bind different commands,
profiles, runtimes and installed dependencies.

PR #947 showed the current remote shape: Detect Changes, seven domain jobs and
the required `PR Gate` all passed. The same workflow then ran again on the
`main` push, even though the active ruleset already requires a strict,
up-to-date PR and has no bypass actors. The consolidation therefore removes
both forms of needless repetition:

- no broad validation on every local commit; and
- no second `fast-checks.yml` run after the already-validated PR is merged.

`PR Gate` remains the sole required remote context. Nightly, release and
deployment workflows retain their distinct responsibilities.

## Exact current-hook disposition

Every current hook has one explicit destination. `Existing` means the present
PR workflow already has equivalent ownership; `add` means parity must be added
before the hook is removed. The warning-only metadata check is the only retired
required control.

| # | Current hook | Target | Required PR disposition |
|---:|---|---|---|
| 1 | `check-yaml` | PR Repository | Run the shared manual-stage hygiene profile on every PR; retain the `mkdocs.yml` exclusion. |
| 2 | `check-toml` | PR Repository | Add strict TOML parsing. |
| 3 | `check-json` | PR Repository | Add strict JSON parsing and retain the two intentional JSONC exclusions. |
| 4 | `end-of-file-fixer` | PR Repository | Detect drift with the existing preserved-artifact exclusions; do not rewrite the candidate silently. |
| 5 | `trailing-whitespace` | PR Repository | Detect drift with the same exclusions. |
| 6 | `mixed-line-ending` | PR Repository | Detect drift with the same exclusions. |
| 7 | `check-merge-conflict` | Commit + PR Repository | Intentional cheap duplication; local history and hookless contributors are both protected. |
| 8 | `check-added-large-files` | Commit + PR Repository | Intentional cheap duplication; preserve the 500 KB limit. |
| 9 | `black` (Python) | PR Python | Existing read-only `black --check`. |
| 10 | `black` (FastAPI) | PR FastAPI | Existing read-only `black --check`. |
| 11 | `ruff` (Python) | PR Python | Existing read-only `ruff check`; optional local formatter remains explicit. |
| 12 | `ruff` (FastAPI) | PR FastAPI | Existing read-only `ruff check`. |
| 13 | `mypy` | PR Python | Existing full configured type check. |
| 14 | `bandit` (Python) | PR Python | Add the current source scope and `B101` disposition. |
| 15 | `bandit` (FastAPI) | PR FastAPI | Add the current FastAPI scope and `B101` disposition. |
| 16 | `contract-tests` | PR Python | Existing contract suite; keep the broader hosted trigger. |
| 17 | `verification-quick` | Decompose | Keep hosted links, versions, hygiene, token, references and CLI coverage; add brief integrity and import validation; retain only the live operation guard locally. |
| 18 | `check-python-version` | PR Repository | Add exact version-consistency coverage. |
| 19 | `check-tasks-format` | PR Docs | Existing. |
| 20 | `check-docs-index` | PR Docs | Add exact index-structure coverage. |
| 21 | `check-release-docs` | PR Docs | Add release-document consistency. |
| 22 | `check-session-docs` | PR Docs/Control | Add tracked session/handoff consistency. |
| 23 | `check-api-docs-sync` | PR Docs | Add exact API documentation sync. |
| 24 | `check-pre-release-checklist` | PR Docs | Add checklist structure coverage. |
| 25 | `check-api-doc-signatures` | PR Docs | Add exact documented-signature coverage. |
| 26 | `check-api-manifest` | PR Python | Add manifest drift coverage. |
| 27 | `check-api-classification` | PR Docs | Existing. |
| 28 | `check-family-facade-docs` | PR Docs/Python | Add generated family-document drift coverage. |
| 29 | `check-beam-tool-manifest` | PR Docs/Python | Add generated beam-manifest drift coverage. |
| 30 | `check-cli-reference` | PR Docs | Add exact CLI-reference coverage. |
| 31 | `check-scripts-index` | PR Control Plane | Existing. |
| 32 | `check-docs-index-links` | PR Docs | Add the exact index-link contract once; do not infer equivalence from the general link checker. |
| 33 | `check-api-signatures` | PR FastAPI contract step | Add exact React/FastAPI parity and route relevant React API inputs to this owner. |
| 34 | `check-doc-metadata` | Retire as required | Warning mode cannot reject a candidate; retain only as an optional informational command if useful. |

## Target PR architecture

Keep the current visible job topology instead of adding another required or
path-filtered check:

| Existing job | Target responsibility |
|---|---|
| Detect Changes | Canonical fail-closed impact plan. Unknown paths or Git-query failures select every domain. |
| Repository Validation | Run on every PR. Execute the shared eight-hook manual hygiene profile, version consistency, repository hygiene and maintenance-script contracts. |
| Python Validation | Black, Ruff, mypy, Bandit, imports, contracts/core tests, API manifest, architecture, circular-import and governance checks. |
| FastAPI Validation | Cheap API/OpenAPI/Docker contracts first, then Black, Ruff, Bandit and the FastAPI suite. Own React/FastAPI signature parity for API-relevant React inputs. |
| React Validation | Probe exact reusable evidence before `npm ci`, then lint, build and Vitest when evidence is absent. |
| Excel Add-in Validation | Complete add-in test suite for affected inputs. |
| Control Plane Validation | Git/session/control contracts, scripts index/references, CLI smoke, token policy and exact regression tests. |
| Documentation Validation | Task, brief, session, release, API, generated-doc, index/link and strict MkDocs contracts. |
| PR Gate | `always()` aggregate that rejects failed, cancelled or skipped applicable jobs, missing applicability and partial fail-closed plans. |

The repository domain becomes universally applicable because candidate
integrity is universal. This avoids a new `Candidate Integrity` context and
keeps the maximum visible workflow at the current nine jobs. A separate
cross-surface job is also unnecessary: route only API-relevant React paths to
the FastAPI contract owner instead of running the entire FastAPI lane for every
React edit.

The implementation must update `scripts/verification-manifest.json` for every
new command input. A hosted command may not read a generator, registry or
artifact that does not select its owning domain. Unknown inputs continue to
fail closed.

## One configuration, two stages

Do not maintain a second hygiene configuration. In
`.pre-commit-config.yaml`:

- YAML, TOML, JSON, EOF, whitespace and line-ending hooks use `stages:
  [manual]`;
- merge-conflict and large-file hooks use `stages: [pre-commit, manual]`;
- the live Git-operation guard uses `stages: [pre-commit]` and
  `always_run: true`.

The PR Repository job runs:

```bash
./scripts/python_runtime.sh -m pre_commit run --hook-stage manual --all-files
```

An ordinary `git commit` therefore executes exactly three hook IDs, only one
of them unconditional. PR validation independently rechecks the eight content
guards so contributors without installed hooks cannot bypass them.

## Batch, commit and PR cadence

Use multiple coherent commits and one PR per accepted batch. Commits are for
reviewable dependency boundaries, not validation checkpoints. There is no line
count or file-count threshold.

For the migration itself, use two commits on one branch:

1. `ci(validation): establish complete hosted parity` - workflow, manifest and
   negative contract tests while the old hooks still exist; this is the final
   intentional expensive commit-hook run.
2. `chore(validation): reduce commits to safety guards` - staged hook topology,
   workflow guidance, active instructions and task/session/handoff truth.

Freeze both commits locally, then push once and open one PR. Do not push each
commit separately because every PR push starts another hosted cycle. If hosted
validation finds a real defect, reproduce only the failed owner locally, make
one consolidated repair commit and push once more.

After migration, a normal feature batch will usually contain two to four
logical commits, but this is guidance rather than a hard cap. Split into
another PR only when authority, installed-application access, mutation
permission, release/publication, external artifact or independently reversible
deployment boundaries differ. Do not create empty checkpoint commits, per-unit
PRs or repeated quick/full gates.

## Implementation sequence

### Phase 0 - freeze evidence

1. Record the exact 34-hook inventory, per-hook baseline and representative
   staged packets. Do not use quick-hook telemetry as a proxy for the complete
   hook wall time.
2. Encode a machine-readable hook-to-PR coverage matrix and a regression that
   fails when a hook disappears without a hosted owner or explicit retirement.
3. Assert the active `main_branch_rule1` still requires strict, up-to-date
   `PR Gate`, requires a PR and exposes no bypass actor before removing the
   post-merge `push: main` run.

### Phase 1 - add hosted parity

1. Add Repository manual-stage hygiene and make the repository domain apply to
   every candidate.
2. Add both Bandit scopes and import/API-manifest checks to the natural Python
   and FastAPI owners.
3. Add missing brief/session/release/API/generated/index/CLI controls to Docs
   or Control Plane exactly once.
4. Extend path ownership and workflow-contract tests before relying on the new
   commands.
5. Order cheap contract checks before expensive test suites so failures return
   early without weakening exact evidence.

### Phase 2 - shrink the commit lane

1. Change the shared pre-commit stages so ordinary commits run exactly the
   three safety hooks.
2. Remove `verification-quick` and every formatting/test/governance hook from
   the commit stage; remove its hard-coded completion expectation from
   `check_codex_git_workflow.py`.
3. Update the real resolved-merge regression to invoke the exact configured
   single operation guard. Preserve locks, conflicts, unknown queries,
   unrelated refs and non-merge operation failures.
4. Keep `session begin` verification of the standard pre-commit framework; it
   checks installation integrity, not the old 34-hook inventory.

### Phase 3 - remove remote repetition and publish once

1. Remove `push: main` from `fast-checks.yml`; strict PR Gate remains the merge
   authority. Do not change nightly, release or actual deployment ownership.
2. Update active workflow guidance, testing strategy, agent instructions and
   the W3 cadence note only after the executable topology is final.
3. Push the two-commit batch once, run one hosted PR cycle and merge only the
   unchanged successful head.
4. Observe the next 5-10 PRs for routing misses, false failures, wall time and
   receipt behavior. Any rollback is one maintenance-PR revert, not a partial
   return of individual commit hooks.

## Fault-injection acceptance matrix

Before removing a local capability, prove its hosted owner rejects the
corresponding defect and that `PR Gate` rejects the failed owner:

- invalid YAML, TOML and strict JSON, while the two JSONC files remain valid;
- missing final newline, trailing whitespace and mixed line endings outside
  preserved artifacts;
- conflict marker and an added file above 500 KB;
- Black, Ruff, mypy and both Bandit failures;
- contract-test and import-validation failures;
- stale API manifest, OpenAPI snapshot, family docs and beam manifest;
- API sync/docs and React/FastAPI signature mismatch;
- broken task, brief, session, release, index/link, CLI and script-reference
  contracts;
- an unknown path selecting every domain;
- missing applicability or an applicable skipped job failing `PR Gate`;
- malformed/tampered receipts causing normal execution rather than a skip; and
- a real unresolved merge blocked locally, a fully resolved authorized merge
  accepted, and locks/unknown/other operations still blocked.

## Quantitative exit criteria

The packet is complete only when all of the following are true:

1. Ordinary commits invoke exactly 3 hook IDs, with exactly 1 `always_run` hook
   and zero formatters, linters, type checkers, security scanners, tests,
   generators, documentation checks or quick/full gates.
2. Warm representative commit-hook p50 is at most 5 seconds and p95 at most 7
   seconds on Windows; the POSIX target remains p50 at most 2 seconds and p95
   at most 5 seconds. Cold execution after dependencies are already installed
   is at most 15 seconds. Record platforms without conflating them. The Windows
   floor was corrected after direct profiling showed the `pre_commit` framework
   startup alone takes 2.4-2.9 seconds per one-hook invocation.
3. Every one of the 34 current hook capabilities maps to a required hosted
   owner, one of the three intentional commit guards, or the explicit
   warning-only retirement.
4. The complete fault-injection matrix and workflow-contract suite pass.
5. The final branch is pushed once for the normal path, `PR Gate` is green on
   the unchanged head, and `fast-checks.yml` does not run again on the merge
   push.
6. No direct-to-main, `--no-verify`, force, admin bypass, pre-push hook, local
   full-suite-per-commit or per-commit PR path is introduced.

## Non-goals

- No ETABS, Excel, COM, model, workbook or installed-application action.
- No weakening of branch protection, required `PR Gate`, nightly, release or
  publication evidence.
- No use of local receipts to skip hosted checks.
- No formatter or generator that silently mutates a hosted checkout and then
  reports success.
- No cleanup of unrelated historical worktrees, branches or pytest caches.
- No implementation in this planning packet.

## Planned implementation files

At minimum inspect and change together:

- `.pre-commit-config.yaml`;
- `.github/workflows/fast-checks.yml` and its README;
- `scripts/verification-manifest.json`, `scripts/check_all.py` and
  `scripts/check_codex_git_workflow.py`;
- `Python/tests/test_ci_workflow_contract.py`,
  `Python/tests/test_verification_control.py`, `Python/tests/test_git_state.py`
  and the existing session/governance hook assertions;
- `AGENTS.md`, `docs/guidelines/ai-token-efficiency.md`,
  `docs/git-automation/git-workflow-single-source.md`, contributor/testing
  guidance and the W3 integrated cadence note; and
- normal task, session and handoff records.
