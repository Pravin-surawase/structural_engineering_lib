---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: GIT-001
---

# GIT-001 Eight-Branch Retirement Authorization Proposal

## Decision

All eight exact targets remain held. The integrated classifier returned
`HOLD_UNKNOWN_OWNER` with reason code `RETENTION_EVIDENCE_UNKNOWN` for every
target. Owner identity is known; the disposition label is the classifier's
generic fail-closed outcome for unknown supplied evidence. No authoritative
record says that any exact historical branch tip is unneeded.

This packet is inspection-only for target disposition. It does not authorize
or perform local branch deletion, remote ref deletion, worktree removal,
pruning, cleanup, issue/PR closure, settings changes, or release work. The
normal documentation branch, commit, push, and PR lifecycle is separate from
the target-disposition mutation boundary.

## Fresh evidence boundary

- Remote and GitHub observation completed at `2026-08-15T08:49:01Z`.
- Refreshed default: `origin/main = 670ea4beeb2a8765fff59e05bb130ff54752369e`.
- Live local heads, live remote heads, and refreshed `origin/*` tracking heads
  match for all eight targets.
- Each target is unattached, has no dirty or operation-bearing worktree, is an
  exact ancestor of `origin/main`, and has zero branch-only commits or patches.
- PRs #724-#729, #732, and #734 are live-confirmed merged at the exact listed
  heads. They have no submitted reviews or comments. No open PR uses a target
  as head or base, and the open-PR reference scan found no target dependency.
- Branch trees differ from current `main` because later integrated commits
  changed the repository. Tree inequality is recorded, not treated as unique
  unpublished work.
- Age is metadata only and contributed no authority.

The caller evidence is
[GIT-001-eight-branch-retirement-classifier-evidence.json](GIT-001-eight-branch-retirement-classifier-evidence.json).
The compact machine-readable outcome is
[GIT-001-eight-branch-retirement-authorization-proposal.json](GIT-001-eight-branch-retirement-authorization-proposal.json).

## Exact disposition table

| Target | Exact head | PR / merge | Default relation | Classifier result | Local branch surface | Remote ref surface | Worktree surface |
|---|---|---|---|---|---|---|---|
| `codex/alpha-0231-candidate-evidence` | `adb161b85489f530b42e78abd7039e59160c83d6` | #732 / `95bed562` | 0 ahead, 23 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/ci-fastapi-load-lane-fix` | `21b9df1fd0d655d5976f73b8672502da4a6fbc60` | #729 / `06d14b7f` | 0 ahead, 65 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/column-rectangular-e2e` | `007dfa0c012404515907779f396ed94cf7a6694d` | #725 / `bcb181fa` | 0 ahead, 58 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/footing-isolated-v1` | `886871aef93d9a955a3cc2fa613fe49bad589ce7` | #727 / `dedebaae` | 0 ahead, 63 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/gpt-5-3-spark-work-program` | `6cd22dcbd073b599e4a2faef80352b294295f32e` | #734 / `6bc356c3` | 0 ahead, 16 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/is456-beam-primary-route` | `aa4fe606ee685240648c88db75e0d1052350fcb4` | #726 / `421790bb` | 0 ahead, 62 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/is456-slabs-closeout` | `d79a1558a0cfa5078f6ddea91c4166100bdc4d04` | #724 / `a4721836` | 0 ahead, 51 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |
| `codex/is456-slabs-plan` | `7e623984e027141fff62e5129c23fdc16264f8e0` | #728 / `be148d39` | 0 ahead, 62 behind, reachable | `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN` | Hold exact ref at exact SHA | Hold exact ref at exact SHA | Unattached; no action surface |

## Classifier command and outcome

The integrated classifier was invoked once with eight repeated exact `--branch`
selectors, `--default-ref origin/main`, `--remote origin`, and the supplied
evidence JSON. It inspected each target independently. The repository receipt
reported:

```text
mutation_policy = INSPECTION_ONLY
authorization = SEPARATE_EXACT_TARGET_APPROVAL_REQUIRED
status = UNKNOWN
query_failures = []
all target dispositions = HOLD_UNKNOWN_OWNER
all target reason codes = [RETENTION_EVIDENCE_UNKNOWN]
```

The output correctly did not reach `RETIREMENT_READY_PENDING_APPROVAL`.
An earlier draft inference that proposal authority implied `NO_RETENTION` was
caught and removed before publication. Autonomous orchestration and normal PR
integration authority do not establish that historical branch evidence is
unneeded.

## Protected holds preserved

This proposal excludes and preserves without modification:

- detached dirty `e54a` at
  `0fdb48edbb73114288feb8a246d6f30b80ac4d95`, with only
  `docs/SESSION_LOG.md` modified and stable patch ID
  `be157118f0267af328051ffbacc18d79c49ffd8c`;
- `codex/git-governance-research` at `657037364bbb49f2ef834c70f3a3c704bac83c7b`;
- `codex/excel-product-planning` at `a0e115e17009cc14b3d883e3c291d47c32f7ca4e`;
- `codex/release-preflight-alpha-policy` at
  `5da9c66a0f962fc08a6431fe95e39ec664a353f6`;
- attached GIT and Alpha lanes, all other refs, all worktrees, shared Git
  configuration, the stale primary `main`, and every unrelated filesystem.

The pre-write common Git configuration hash was
`bfdc47e4096d756d71f4077c9581bc146160602a719ff6afe3aa5853f8d0e228`.
The packet must reproduce these identities after document writes and before PR
publication.

## Next explicit authorization boundary

The next step is not deletion approval. First, an authoritative repository-owner
record must state `NO_RETENTION` or `RETAIN` for each named exact SHA. Any
`NO_RETENTION` target must then be refreshed and rerun through the classifier.
Only an unchanged exact target returning
`RETIREMENT_READY_PENDING_APPROVAL` may advance to a later approval request.

That later request must offer independent SHA-bound decisions for:

1. local branch ref deletion;
2. remote branch ref deletion; and
3. worktree removal only if a worktree exists at reinspection time.

Each approved action requires same-session reinspection and a post-action
receipt. This proposal itself authorizes none of them. GIT-7E remains explicitly
not started and is outside this packet.
