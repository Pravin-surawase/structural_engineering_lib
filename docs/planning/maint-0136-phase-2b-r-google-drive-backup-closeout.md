---
owner: Main Agent
status: archived
last_updated: 2026-08-27
doc_type: log
complexity: intermediate
tags: [maintenance, backup, recovery, google-drive, worktrees]
---

# MAINT-0136 Phase 2B-R Google Drive Backup Closeout

## Outcome

Phase 2B-R off-device recovery is complete. The exact archive was uploaded to a
new owner-only Google Drive folder for `structural_engineering_lib`, downloaded
through the authenticated account, matched byte-for-byte, and restored in full.

The machine-readable authority is the
[Google Drive backup evidence](../verification/maint-0136-phase-2b-r-google-drive-backup-evidence.json).
Its status is `OFF_DEVICE_BACKUP_VERIFIED_RESTORE_PASS_CLEANUP_HELD`.

## Verified recovery result

| Check | Result |
|---|---:|
| Frozen source files | 7,602 |
| Frozen source bytes | 123,164,574 |
| Compressed archive bytes | 92,256,339 |
| Archive SHA-256 | `bf18a66b339b2ad02f071346aed75cb27d3fceeae0e45464eb50dd11334167ac` |
| Remote metadata size | 92,256,339 |
| Authenticated download size | 92,256,339 |
| Download SHA-256 | Exact local match |
| Full downloaded restore | PASS, 7,602 files / 123,164,574 bytes |
| Drive visibility | Owner only; zero broad permissions |
| Drive encryption | AES-256 in transit and at rest |

The uploaded package contains the existing all-ref Git bundle, dirty-worktree
patch, 42 protected source files, and the exact preserved ignored state from 64
retirement-review worktrees. The tracked evidence records only aggregate
identities; remote locators and protected filenames remain in the private
receipt stored beside the archive.

## Destination boundary

The backup lives under a new `structural_engineering_lib Backups` root, not the
existing Sourcebook backup folder. Both the folder and archive were read back as
private, owner-only items. Google documents that Drive uploads are encrypted in
transit and at rest with AES-256; Workspace client-side encryption is not
claimed.

The connector does not expose remaining Drive quota. This does not weaken the
completed artifact proof: Drive accepted the exact 92,256,339-byte archive,
returned the same remote size, streamed it back through the authenticated
account, and the downloaded bytes restored exactly. Local restore workspace had
more than the preparation packet's required reserve.

## What remains held

The later [Phase 2B-W preparation](maint-0136-phase-2b-w-preparation-plan.md)
requeried 78 worktrees and froze 63 exact clean, backed, remotely recoverable or
integrated targets totaling 7,686,279,168 gross bytes. One backed lane lacks an
exact remote/integrated recovery path, and 14 live lanes are outside the backup
mapping; all 15 remain retained.

Worktree execution still requires confirmation bound to the exact target-set
SHA-256 `543a5f1b...129da`. Branch/ref/archive cleanup remains Phase 2C and is
not part of Phase 2B-W.
