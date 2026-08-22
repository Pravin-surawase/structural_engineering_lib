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
| `MAINT-012A` | Canonical control registry, schema, loader, CLI, complete permissions, structured commands, and deterministic legacy projection | Active implementation packet |
| `MAINT-012B` | Replace broad generated folder-index dependence with small authoritative manifests and on-demand summaries; retain only indexes proven useful | Separate candidate after A is merged |
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
