---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: GIT-001
phase: 7D1
---

# GIT-001 Phase 7D1 — Targeted Index Generation

## Scope and confirmed defect

GIT-7D is split so the incident-producing generator route can be corrected
without combining it with branch/worktree disposition logic. This packet owns
only the preferred index-generator contract. GIT-7D2 remains an
inspection-only classifier packet; deletion and cleanup remain outside both.

From a fresh current-main lane, this command was expected to preview one owned
folder:

```text
./run.sh generate indexes docs/research/git-governance --dry-run
```

Instead it reported `Mode: LIVE`, processed the legacy global list, and changed
31 unrelated maintained index files. The exact generator-created drift was
enumerated and reversed with an inspected reverse patch; the task-owned
`docs/SESSION_LOG.md` change was preserved. Verification reported all 31
generated paths restored and only the session record remaining dirty.

The confirmed root cause was the `run.sh` dispatcher: every `indexes` call
invoked `scripts/generate_all_indexes.sh`, whose hard-coded loop consumes no
arguments. The already-maintained Python generator supports a positional
folder, `--dry-run`, explicit `--all`, checks, output selection, recursion, and
new-topology opt-in, but the preferred command discarded that contract.

## Implemented contract

The canonical entrypoint now routes non-help arguments directly through the
invoking worktree's `scripts/python_runtime.sh` to
`generate_enhanced_index.py`:

```text
./run.sh generate indexes <owned-folder> --dry-run
./run.sh generate indexes <owned-folder>
./run.sh generate indexes --all --dry-run
./run.sh generate indexes --all
```

No arguments and `--help` show non-writing help. Folder scope is the default;
all-folder generation requires explicit `--all`. Existing index ownership and
the separate `--allow-new-index` opt-in continue to prevent accidental new
topology during live generation.

The legacy all-folder shell launcher remains available to its existing direct
callers in this bounded packet, but it is no longer the canonical `run.sh`
route. Migrating or retiring those direct callers is separate work if live
evidence shows a main-process need.

## Acceptance evidence

| GIT-7D scenario | Result in GIT-7D1 |
|---|---|
| No-argument preferred generator is non-writing help | passed; status byte-for-byte unchanged |
| One-folder dry-run affects only expected maintained paths | passed; one folder and its two index paths reported, no write |
| One-folder live write changes only expected indexes | passed in an isolated temporary project |
| `--all` is explicit and previews the full target set | passed; 32 canonical existing folders previewed, no write |
| Unexpected new topology fails without opt-in | passed; existing regression exits 2 and creates no index |
| Branch classifier is mutation-free and fail-closed | held for GIT-7D2 |
| Cleanup or deletion | prohibited and not performed |

Focused `Python/tests/test_session_automation.py` verification passes 45 tests.
The exact previously failing preferred command now reports one dry-run target
and leaves Git status unchanged.

## Timing experiment

This packet is measurement run 1 for the owner's Git-process efficiency
question. The clock starts only after implementation and local verification,
at the first commit/publication action, and ends after exact-head checks,
integration, and post-merge verification. The receipt separates local Git,
GitHub/PR operations, CI wait, retry/rollback time, and total wall time so
additional safeguards can be judged against prevented rework rather than raw
step count alone.

## Non-goals and next gate

No classifier, branch/worktree disposition, deletion, cleanup, release,
product code, GitHub setting, bypass, or adjacent hardening is included. The
next gate is exact-head required CI and normal PR integration of this packet;
GIT-7D2 remains separate.
