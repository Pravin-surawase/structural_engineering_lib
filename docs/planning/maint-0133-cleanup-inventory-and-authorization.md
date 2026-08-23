---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: spec
complexity: intermediate
tags: [maintenance, cleanup, safe-file-ops, authorization]
---

# MAINT-0133 Cleanup Inventory and Authorization Plan

## Decision

MAINT-0133 completes the read-only classification prerequisite for repository
file cleanup. It does not move, delete, archive, clean, reset, or retire any
file, branch, or worktree.

The inventory baseline is merged `origin/main` commit
`60e95bbe52575d3335e7195db944b2c82630ed2e`. The machine-readable inventory is
[`maint-0133-cleanup-inventory.json`](../verification/maint-0133-cleanup-inventory.json),
and the two-operation future batch is
[`maint-0133-cleanup-batch.json`](../verification/maint-0133-cleanup-batch.json).

MAINT-0133 was integrated through PR #847 at
`417a16590892d176ea288bbda93ad4d48b4603c4`. The owner then explicitly
authorized completion of the exact two-move packet. MAINT-0133B rebound that
packet to this merged commit and executed no other cleanup operation.

## Discovery contract

The inventory includes only evidence-bearing classes:

1. tracked artifacts rejected by repository hygiene;
2. exact duplicate Git blobs;
3. documents explicitly marked `deprecated` or `archived` outside archive
   roots;
4. active top-level scripts not covered by the canonical control registry; and
5. exact safe-file reference previews.

File age, a suggestive filename, or an unreferenced-name scan is insufficient.
Historical archives, vendor references, and branch/worktree cleanup remain
preserved or separately held.

## Result

| Disposition | Count | Meaning |
|---|---:|---|
| `MOVE_READY_NOT_AUTHORIZED` | 2 | Exact dry-run succeeds with zero unresolved references |
| `HOLD_UNRESOLVED` | 4 | The transactional mover correctly blocks the operation |
| `DELETE_READY` | 0 | No deletion has replacement, reference, and retention proof |
| `KEEP` duplicate group | 1 | Four empty Python test-package markers have distinct ownership |

The maintained baseline is clean: 4,106 tracked files, 478 maintained Markdown
files, 1,013 local links, six local images, zero broken links, 115 active
operations, and 101/101 active top-level scripts covered. Repository hygiene
passes.

### Packet A execution — two completed planning moves

The exact authorized moves completed as follows:

| Original source | Current destination | Updateable | Preserved | Unresolved |
|---|---|---:|---:|---:|
| `docs/planning/india-2-remaining-is456-elements-plan.md` | `docs/_archive/planning/india-2-remaining-is456-elements-plan.md` | 3 | 46 | 0 |
| `docs/planning/india-2-next-session-publication-and-closeout-plan.md` | `docs/_archive/planning/india-2-next-session-publication-and-closeout-plan.md` | 2 | 25 | 0 |

The reviewed batch retains its publication-time
`NOT_AUTHORIZED_FOR_LIVE_EXECUTION` status as immutable historical evidence.
The later owner authorization and live result are recorded separately in
[`maint-0133b-execution-evidence.json`](../verification/maint-0133b-execution-evidence.json).
Both exact source blobs matched, both destinations were absent, both repeated
previews had zero unresolved references, the two transactional moves succeeded
without rollback, and the seven-path live result matched the frozen prediction.

### Held candidates

| Source | Unresolved | Hold reason |
|---|---:|---|
| `docs/agents/guides/README.md` | 279 | Generic `README.md` basename matches are ambiguous; no force or manual move is allowed |
| `docs/agents/guides/agent-quick-reference.md` | 2 | Maintained governance checks still name the file |
| `docs/agents/guides/agent-workflow-master-guide.md` | 2 | Maintained governance checks still name the file |
| `docs/planning/is456-library-first-master-plan.md` | 3 | Current planning documents still require successor-aware reference repairs |

These holds are not failures to clean. They are the intended fail-closed result
of the safe-file contract. Each requires a separately reviewed reference repair
before another preview.

## Preserved surfaces

- 507 files under `docs/_archive/**` remain historical evidence.
- 119 files under `scripts/_archive/**` remain inactive audit/recovery content.
- 1,760 files under `docs/reference/vendor/**` remain protected reference
  material.
- All 48 observed worktrees remain outside this file-cleanup authority,
  including dirty, detached, foreign, and uncertain lanes.

## Acceptance and stop conditions

MAINT-0133 is complete when:

- every candidate is bound to an exact source blob and destination;
- the future two-operation batch passes a complete dry-run;
- every unresolved reference remains held;
- zero live moves and zero deletes occurred;
- maintained links, control coverage, context, focused migration tests, quick,
  full, normal hooks, and hosted checks pass on the immutable candidate; and
- post-merge external closeout removes the frozen task row from future session
  orientation.

Stop MAINT-0133B if a destination appears, a source blob changes, the predicted
path set changes, any unresolved reference appears, or any validator fails.

MAINT-0133B satisfies those conditions on its frozen candidate when the two
destination blobs equal the original source blobs, both sources are absent,
maintained links and focused migration tests pass, and local plus hosted gates
accept the unchanged candidate. The four unresolved candidates, all deletes,
and all branch/worktree cleanup remain outside this completion packet.
