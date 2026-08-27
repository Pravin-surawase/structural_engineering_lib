---
owner: Main Agent
status: archived
last_updated: 2026-08-26
doc_type: spec
complexity: intermediate
tags: [maintenance, cleanup, recovery, worktrees, backup]
---

# MAINT-0136 Phase 2B-R Recovery Preparation

## Outcome

Phase 2B-R preparation completed under the
[recovery preparation manifest](../verification/maint-0136-phase-2b-r-recovery-preparation-manifest.json),
whose status is `PHASE_2B_R_PREPARED_DESTINATION_HOLD`. Google Drive backup and
authenticated restore subsequently passed under the
[backup closeout](maint-0136-phase-2b-r-google-drive-backup-closeout.md).

The preparation packet itself performed no backup or cleanup mutation. The
later backup packet created the exact archive, uploaded it and its private
receipt, and restore-tested the downloaded remote bytes. It still performed no
source deletion, cache cleanup, worktree removal, branch/ref operation,
pull-request action, protected-source change, or shared-`.venv` change.

## Exact recovery boundary

The 64 retirement-review worktrees contain 103,950 ignored regular files. The
collector classifies only proven build, test, and tool output as regenerable;
all other ignored state fails closed to preservation.

| Recovery component | Files | Bytes | Disposition |
|---|---:|---:|---|
| Worktree ignored state to preserve | 7,558 | 8,209,256 | Back up and restore-test |
| Existing all-ref Git bundle | 1 | 42,922,979 | Reverify and copy |
| Existing dirty-worktree patch | 1 | 7,146 | Reverify and copy |
| Protected local sources | 42 | 72,025,193 | Encrypted backup; never track |
| **Total source** | — | **123,164,574** | Exact copy source ceiling |
| Proven regenerable ignored output | 96,392 | 2,962,551,202 | Excluded from backup |

The preserved ignored state consists of:

- 7,334 Hypothesis reproduction files / 5,045,453 bytes;
- 202 session, pipeline, and trust-state files / 145,161 bytes;
- 18 safe-delete recovery files / 372,793 bytes; and
- four built release artifacts / 2,645,849 bytes.

The manifest records counts, byte totals, and content aggregates without
recording ignored or protected filenames or contents.

## Destination gate

The exact destination must be a separate physical or off-device failure domain,
have proven encryption and write access, and expose at least **313,438,012
bytes** free. This is `2 × 123,164,574 source bytes + 64 MiB restore reserve`.

At freeze time, Time Machine reported no available destination and `/Volumes`
contained no external candidate. A same-disk directory or the Git remote does
not satisfy this gate.

## Later backup packet

After the owner mounts or identifies one exact encrypted off-device
destination, a separate authorization may permit only the recovery copy and
managed restore test. That packet must:

1. requery current topology, open pull requests, exact heads, and source
   aggregates;
2. reject any symlink, special file, disappearing source, or digest drift;
3. create destination-owned archives without exposing protected filenames in
   tracked evidence;
4. verify copied artifact hashes and restore the ignored-state archive into a
   managed empty directory;
5. compare restored count, byte total, and aggregate SHA-256 to the source;
6. retain every source and perform zero cleanup; and
7. produce a new immutable backup-evidence record.

Suggested authorization after the destination is mounted:

> I authorize Phase 2B-R backup execution to the exact encrypted off-device
> destination you verify and present. Copy and restore-test only the frozen
> recovery sources. Do not remove any cache, worktree, branch, ref, pull
> request, archive, protected source, or shared `.venv`.

This wording is not current authorization. Phase 2B-W worktree retirement
remains a later, separately frozen and authorized packet even after backup
passes.

## Stop conditions

Stop without copying or cleanup if the destination is unavailable, same-disk,
unencrypted, not writable, or too small; if any source identity, digest,
topology, head, dirty state, operation, or pull-request status drifts; if a
source is a symlink or non-regular file; or if the managed restore aggregate
does not match exactly.

## Validation contract

- four focused recovery-preparation regressions cover classification,
  preservation, archive/restore equivalence, and destination hold;
- inherited Phase 2B, Phase 2A, and cleanup-preservation regressions must pass
  together after content freeze;
- Ruff, Black, documentation, context, control, efficiency, quick, normal hook,
  and full repository gates must pass before the local preparation commit; and
- publication remains held behind the unresolved predecessor chain and is not
  needed to select a backup destination.
