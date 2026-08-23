---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: spec
complexity: advanced
tags: [maintenance, control-plane, scripts, indexes, scanners, ci]
---

# MAINT-012 Control-Plane Modernization

## Purpose

Modernize the old script, discovery, permission, index, scanner, and validation
control system as one planned program without a repository-wide rewrite in one
candidate. The program must reduce repeated AI inspection and redundant checks,
keep existing commands working during migration, and leave one obvious source
for each kind of truth.

This is not a cosmetic cleanup. The confirmed failure mode is duplicated and
partly implicit control metadata: agents repeatedly rediscover scripts, infer
permissions, reread generated indexes, and rerun broad checks because no
validated control contract explains what exists, what it may change, and which
evidence a change invalidates.

## Frozen packet sequence

| Packet | Outcome | Boundary |
|---|---|---|
| `MAINT-012A` | Canonical control registry, schema, loader, CLI, complete permissions, structured commands, and deterministic legacy projection | Complete through PR #840 |
| `MAINT-012B` | Replace broad generated folder-index dependence with small authoritative manifests and on-demand summaries; retain only indexes proven useful | Complete through PR #841 |
| `MAINT-012C` | Add content-addressed impact/evidence reuse and migrate quick/full/hosted validation scheduling to explicit change domains | Active isolated candidate; no safety gate may be skipped without a proved input identity |
| `MAINT-012D` | Consolidate scanners and retire/move obsolete scripts using live callers, ownership, runtime, and replacement evidence | Separate candidate; every deletion/move requires preservation-aware proof |

The order is deliberate: B-D consume the registry contract from A. They must not
invent another operation list, permission table, alias store, or script parser.

## MAINT-012A frozen scope

### Canonical files

- `scripts/control-plane.json` is the versioned source of truth for operation
  discovery, status, groups, aliases, display commands, structured command
  steps, default permissions, mode permissions, and context documents.
- `scripts/control-plane.schema.json` is the strict Draft 2020-12 shape
  contract. Unknown fields, absent permissions, invalid statuses, and malformed
  commands fail closed.
- `scripts/control_plane/` owns the validated Python loader and the control CLI.
  Its evaluator covers the exact schema keywords used here with the Python
  standard library, so minimal repository/control CI lanes need no optional
  validation extra.
- `scripts/automation-map.json` remains temporarily for compatibility, but it is
  generated deterministically from the canonical registry and must never be
  edited independently.

### Migration result

| Contract | Frozen value |
|---|---:|
| Total operations | 128 |
| Active operations | 125 |
| Deprecated compatibility operations | 3 |
| Active top-level Python/shell scripts represented | 113/113 |
| Active operations without a default permission | 0 |
| Canonical shell-chain commands | 0; the formatter is two structured steps |

The loader rejects duplicate JSON keys, schema violations, duplicate/colliding
aliases, invalid deprecation replacements, missing local command targets,
repository-escaping targets, unmapped scripts, and phantom scripts. Permission
resolution remains fail-closed for an unknown operation or mode.

### Compatibility and preserved commands

- `./run.sh find`, `./run.sh tools`, prompt routing, permission enforcement,
  permission audit, governance validation, and script coverage load the
  canonical registry.
- `./run.sh control validate` is the compact registry/parity verdict.
- `./run.sh control find|list|stats` exposes the canonical data directly.
- `./run.sh control export-legacy` checks the compatibility projection;
  `--write` is the only supported refresh path.
- Existing consumers that still inspect `automation-map.json` receive the same
  task-shaped compatibility data while later packets migrate or retire them.

## Explicit MAINT-012A exclusions

- No generic folder-index retirement or repository-wide index regeneration
  redesign.
- No result cache, test cache, evidence reuse policy, or CI/pre-commit topology
  change.
- No scanner rescheduling, scanner consolidation, script deletion, archive
  move, or command rename.
- No structural arithmetic, public API, FastAPI, React, Excel, ETABS, package,
  dependency, release, GitHub setting, or professional-approval change.

## MAINT-012B frozen scope

### Confirmed baseline

The live repository contained 70 generic `index.json` files, 70 paired
`index.md` files, and the separate `docs/docs-index.json` catalogue: 141
generated artifacts totalling 1,391,320 bytes and 43,141 lines. The canonical
`--all --check` route validated only 32 of the 70 folder JSON indexes. From
2026-05-01 through packet start, the most frequently changed parent projections
appeared in 80-95 commits, while a live targeted `rg --files` lookup completed
below the timer's 0.01-second resolution.

The prior logs also record cross-worktree timestamp drift, checkout-local hidden
artifact drift, accidental 31-file regeneration, leaf/global/parent ordering
errors, stale-parent CI failures, and commit-hook restarts after generated index
normalization. Those are architecture costs, not isolated formatting defects.

### Canonical replacement

- `scripts/context-manifest.json` is the small authoritative map from repository
  areas to roots, read-first sources, and canonical control-plane operations.
- `./run.sh context validate|list|show|summary` validates that map and produces
  bounded summaries from current worktree files. It never writes a projection.
- Operation, documentation-topic, agent, Git, task, and public-API truth remain
  with their existing specialized authorities. The context manifest points to
  them instead of duplicating their contents.
- Generic folder inventories and the global generated docs catalogue are
  retired. `docs/index.md` becomes a concise authored MkDocs home;
  `docs/api-reference/index.md` remains the API landing page; and
  `docs/git-automation/live-git-guidance-index.json` remains a separately
  validated policy manifest.
- Former generator commands stay as read-only compatibility bridges during this
  packet. They either validate or summarize live context and cannot recreate
  index topology. Physical script retirement remains MAINT-012D.
- Session closeout, agent orientation, maintenance, file-move, documentation,
  control coverage, nightly drift, and release-candidate guidance use the new
  read-only contract. There is no leaf/global/parent refresh or final index
  write.

### MAINT-012B exclusions

- No content-addressed test/evidence reuse, change-domain scheduler, quick/full
  profile redesign, pre-commit consolidation, or hosted CI topology redesign;
  those remain MAINT-012C.
- No scanner consolidation and no deletion/move of the compatibility generator
  scripts; those remain MAINT-012D.
- No structural calculation, public API, FastAPI, React, Excel, ETABS,
  dependency, package, release, GitHub-setting, or professional-approval change.

### MAINT-012B acceptance

1. The context manifest fails closed on duplicate keys, bad paths, unknown
   operations, unknown fields, and any unapproved generic index topology.
2. Live summaries are deterministic, bounded, current-worktree based, and
   contain no timestamps or repository writes.
3. All 141 generated artifacts are either deleted (140) or converted to the one
   authored docs home; only the three explicitly owned index-named surfaces
   remain.
4. Old generator routes cannot recreate indexes, while maintained discovery and
   direct callers receive a clear migration path.
5. Focused context/control/session/release tests, links, documentation,
   quick/full gates, normal hooks, and required hosted checks pass on one frozen
   candidate.

## MAINT-012C frozen scope

### Confirmed baseline

- Local `./run.sh check --changed` inspected only `HEAD~1..HEAD`, used a private
  prefix table, and treated an unmapped path or failed Git query as no work. A
  real candidate spanning multiple commits could therefore omit earlier impact,
  while a new root/path could produce a misleading green result.
- Hosted PR scheduling repeated a separate hand-authored path map inside YAML.
  Local and hosted ownership could drift without either validator knowing.
- Quick/full gates had no reusable result identity. The normal commit hook then
  invoked six controls through separate entry points; four duplicated the quick
  gate while two were legitimate commit-only controls.
- The parallel check runner's aggregate-timeout path could omit unfinished
  futures from its result set instead of failing them explicitly.
- PR #841's unchanged hosted candidate spent 35-86 seconds in each applicable
  validation job after a 9-second classifier; retrying the same bytes could not
  reuse the earlier PASS result.

### Canonical contract

- `scripts/verification-manifest.json` is the single seven-domain map for
  `python`, `fastapi`, `react`, `excel`, `control_plane`, `docs`, and
  `repository`. Each path rule is used for both scheduling and evidence inputs,
  so there is no second fingerprint map to synchronize. Its strict schema and
  semantic validator cover every current tracked/untracked non-ignored path. A
  new/unmapped path, invalid base, or Git query failure selects every domain.
  An unmapped live path is also rejected by strict registry validation, so the
  all-domain run cannot turn missing ownership into a mergeable green result.
- `./run.sh verification validate|plan|fingerprint|probe` exposes the read-only
  schedule and evidence contract; `record` writes only to the Git-common or
  hosted runner evidence directory after PASS. Local candidate discovery compares
  the whole branch to `origin/main` plus staged, unstaged, and untracked work;
  hosted discovery uses the exact event base/head.
- A PASS identity binds the profile, normalized command, declared domain set,
  current input-file bytes (including deletions), verification implementation,
  platform/Python identity, installed distribution versions, and any supplied
  Node/runner identity. Failed, missing, malformed, partial, or non-matching
  receipts never skip execution.
- Local receipts live outside tracked content in the shared Git common
  directory. Quick and full profiles share receipts for the exact same check;
  Git-state checks remain fresh. `--no-reuse` forces a new execution.
- The normal pre-commit hook invokes the quick orchestrator once, so a prior
  frozen-candidate quick PASS is reused instead of rerunning four overlapping
  checks. Its two non-overlapping CLI/registry controls remain explicit, and
  merge-completion commits retain their prior Git-operation exception.
- Hosted jobs resolve their dependencies/runtime first, then use one exact
  `actions/cache@v6` key with no prefix restore through one small composite
  action. Only a separately verified PASS receipt skips the validation body; a
  cache miss executes and records evidence only after every job step succeeds.
- The previously unconditional repository bundle is split by ownership:
  documentation owns versions/tasks/links, Python/FastAPI own architecture,
  control owns registries/CLI policy, and repository owns YAML, hygiene, and
  maintenance-script checks. No validation is discarded merely to gain a skip.
- `test_changed.py` consumes the same whole-candidate plan, retains proved
  Python/FastAPI focused mappings, runs React/Excel when their domains change,
  and expands unclear ownership to the applicable full suite.

### MAINT-012C exclusions

- No scanner consolidation, compatibility-script deletion/move, or broad
  physical script retirement; those remain MAINT-012D.
- No dependency version, product calculation, public API, FastAPI behavior,
  React UI, Excel workflow, ETABS, package, release, GitHub-setting, or
  professional-approval change.
- No reuse across a runtime/dependency identity that has not been observed, no
  failed-result cache, no approximate/prefix cache key, and no calendar-only
  claim that evidence remains valid.

### MAINT-012C acceptance

1. The live manifest is strict, covers every current repository path, and maps
   unknown paths/query failures to all seven domains in local and hosted plans.
2. Relevant bytes, commands, domain ownership, runtime/dependencies, and
   verification-control changes alter the evidence fingerprint; irrelevant
   domain bytes do not.
3. Only an exact PASS receipt reuses a check/job. Malformed, failed, missing, or
   mismatched evidence executes normally, and `--no-reuse` proves the fresh path.
4. Local changed-test/check scheduling and hosted applicability use the same
   manifest; `PR Gate` rejects missing flags, partial fail-closed routing, and
   skipped applicable jobs.
5. The frozen candidate passes focused scheduler/cache/workflow/control tests,
   the quick and cumulative full gates, ordinary hooks, and every required
   hosted check without changing product behavior.

## MAINT-012D frozen scope

### Confirmed baseline

- The active surface contained 130 registered operations (124 active and six
  deprecated) and 115 top-level scripts. Fifteen registry entries represented
  duplicate modes, duplicate commands, obsolete bridges, or unsupported
  writers rather than independent outcomes.
- The nightly OpenAPI drift script compared only endpoints and component-schema
  names while the maintained snapshot checker also had only summary-level
  reporting. Either route could miss a changed method body, parameter, response,
  or schema field.
- Three Git wrapper files delegated to `git_state.py`; three index generator
  bridges delegated to the MAINT-012B context system. Their compatibility period
  had ended, but their executable files, CI syntax checks, tests, and deprecated
  operations kept the old paths looking current.
- `governance_health_score.py` hard-coded `.venv/bin/python` and failed in a
  source-bound linked worktree. `repo_health_check.sh` assumed `.git/` was a
  directory and failed in a linked worktree where `.git` is a file. Both
  overlapped the maintained `project_health.py` and repository diagnostics.
- `collect_metrics.sh` reran pytest/coverage through a hard-coded environment and
  wrote metrics without a maintained caller. `export_paper_data.py` was absent
  from the current agent-evolution skill workflow and had no supported consumer.
- Deep agent startup reran the full project-health scanner merely to display a
  score, and ordinary `project_health.py --score/--json` calls persisted a report
  despite being registered as read-only.
- The non-Git `scripts/hooks/` prototype had no runtime caller; prompt routing
  already performed registry lookup and permission enforcement directly.
- The retained readiness aggregator resolved most evidence paths from process
  cwd. Its performance authority passed in a focused root invocation but became
  WARN when the broad Python suite exercised it after cwd had changed.
- The safe move helper would automatically rewrite old session logs, audit
  reports, research, and immutable verification receipts when archiving a
  referenced path, changing historical evidence merely to follow a live move.

### Disposition and canonical owners

| Action | Former surface | Canonical outcome owner |
|---|---|---|
| Consolidate | `check_openapi_drift.py` | `check_openapi_snapshot.py`, now a full-spec deep comparison that ignores only `info.version` |
| Consolidate | `governance_health_score.py`, `repo_health_check.sh` | `project_health.py`; diagnostics remain `collect_diagnostics.py` and hygiene remains `check_repo_hygiene.py` |
| Consolidate | `fix_broken_links.py` and two registry operations | One `check markdown links` operation; `check_links.py` is read-only by default and writes only with `--fix` |
| Consolidate | `check_wip_limits.sh` | `check_tasks_format.py` owns declared task-board WIP; task intake separately inspects typed worktree state and current PR evidence |
| Retire bridge | Three Git wrapper scripts | `git_state.py` plus three searchable legacy aliases and retirement sentinels |
| Retire bridge | Three generated-index scripts and `run.sh generate` routes | `./run.sh context`; old script names remain discovery aliases only |
| Retire duplicate | `test import 3d pipeline` operation | Alias of the single `test import pipeline` operation |
| Retire dormant/unsupported | `collect_metrics.sh`, `export_paper_data.py`, `scripts/hooks/` | Current session usage, project health, agent evolution, prompt routing, and permission controls |

The archived files remain reference-only under `scripts/_archive/`; no redirect
stub remains in the active tree. The canonical registry has 115 active
operations, no deprecated executable bridge operations, and complete ownership
of all 102 active top-level scripts. Agent startup reads the latest recorded
health receipt instead of scanning, while project health is read-only unless
`--write` or `--fix` is explicit.

### Safety holds and exclusions

- `audit_readiness_report.py`, `audit_error_handling.py`,
  `audit_input_validation.py`, `check_function_quality.py`, and
  `check_public_route_safety.py` remain separate. They aggregate different
  evidence or validate different engineering/public-boundary contracts, so
  merging them would weaken failure meaning rather than reduce repetition.
- Agent scoring, drift, compliance, trends, instruction evolution, and session
  collection remain the maintained agent-evolution workflow.
- No structural calculation, public API behavior, FastAPI route, React UI,
  Excel/ETABS workflow, dependency, package, release, branch deletion,
  GitHub-setting, or professional-approval change is included.
- Historical evidence and retirement sentinels keep their original path text.
  The safe move helper may rewrite maintained live callers but skips immutable
  evidence and explicit absence assertions.
- The retained readiness aggregator resolves repository evidence from its own
  source root while keeping concise repository-relative command paths, so its
  verdict no longer depends on prior test/process cwd.

### MAINT-012D acceptance

1. Every archived path has a live-caller, runtime, ownership, and replacement
   disposition; no active CI, `run.sh`, agent, registry command, or current guide
   executes an archived file.
2. OpenAPI method/body/schema drift is detected while a version-only change is
   ignored; the nightly and local paths call the same checker.
3. Legacy intent remains discoverable through one canonical alias owner, while
   retired Git/index executable paths are absent and guarded against return.
4. The control projection is regenerated once and validates exactly 115 active
   operations and 102/102 active scripts; context and verification manifests
   remain fail closed.
5. Historical logs, audits, research, and receipts are not rewritten by the
   moves. Focused contract tests, broad Python, quick/full gates, ordinary hooks,
   and every required hosted check pass on one frozen candidate.

## Efficient operating contract

For an operation-metadata change, edit only `control-plane.json`, run
`./run.sh control export-legacy --write`, then run
`./run.sh control validate`. Discovery and permission consumers do not require
separate synchronized edits. The compatibility check fails if either source
drifts, so an AI does not need to compare the two files manually.

Routine code work must continue to use the repository impact and verification
rules. MAINT-012A makes control metadata cheap and deterministic; it does not
claim that test results are reusable before MAINT-012C supplies content-bound
evidence identities.

## Future maintenance policy

There is no calendar-based rewrite after “a few months.” Update the registry
transactionally whenever an operation is added, removed, renamed, moved, or
changes permission/execution behavior. Increment `schema_version` only for a
breaking registry contract and provide a migration/projection path. A bounded
quarterly review may look for obsolete operations, slow checks, and recurring
fallbacks, but it should create work only from measured drift or repeated cost.

Each successor packet must publish before/after evidence for AI orientation
reads, affected-check time, full-gate time, generated churn, and false/stale
scanner findings. If a proposed abstraction does not materially reduce one of
those outcomes, it does not belong in MAINT-012.

MAINT-012B's context manifest is event-driven: update it only when an area's
root, read-first authority, retained index-named surface, or canonical operation
changes. It does not require a calendar refresh. A bounded quarterly review may
measure whether routing is still useful, but unchanged live summaries never
need regeneration.

MAINT-012C's verification manifest is also event-driven: update its rules
whenever a path owner, validation job, check command, dependency boundary, or
verification implementation changes. The same rule changes scheduling and
fingerprint inputs. Receipts need no manual refresh because their content
address invalidates automatically; cache eviction only causes fresh execution.
A quarterly review may compare observed job/check time and unknown-path events,
but unchanged contracts need no rewrite.

MAINT-012D retirement is event-driven too. Reassess a scanner or script only
when a new duplicate caller appears, a canonical owner changes, an archived
capability is requested, a check repeatedly produces stale/false results, or
measured runtime becomes material. A quarterly inventory may detect those
events, but elapsed months alone do not justify regenerating aliases, moving
files, or rerunning broad evidence.

## MAINT-012A acceptance

1. Schema, semantic, duplicate, alias, target, coverage, permission, and
   determinism regressions pass.
2. Exactly 125 active operations and 113 top-level scripts are represented; no
   active permission is implicit.
3. Existing discovery, routing, tool, and permission interfaces preserve their
   user-facing commands.
4. The compatibility projection is byte-deterministic and clearly generated.
5. Focused tests, quick gate, full gate, ordinary commit hooks, and all required
   hosted checks pass on one frozen candidate.
