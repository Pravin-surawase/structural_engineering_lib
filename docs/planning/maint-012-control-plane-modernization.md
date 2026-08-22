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
| `MAINT-012B` | Replace broad generated folder-index dependence with small authoritative manifests and on-demand summaries; retain only indexes proven useful | Active isolated candidate after A |
| `MAINT-012C` | Add content-addressed impact/evidence reuse and migrate quick/full/hosted validation scheduling to explicit change domains | Separate candidate; no safety gate may be skipped without a proved input identity |
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
