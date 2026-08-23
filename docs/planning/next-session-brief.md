# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Converge ETABS exported files into one deterministic snapshot and canonical beam requests
- Git receipt: docs/verification/lib-pro-007-p5-etabs-snapshot-git-handoff-receipt.json | sha256:aae36c259380c3aa2ed3a94c4af038bfbd87bbf5634b89ee3476d6178f899457 | HOLD
- Git identity: codex/lib-pro-007-p5-etabs-snapshot@426d401bb2afde417ff989bd7349c99b8f7cb438 | upstream=NONE | base=origin/main@426d401bb2afde417ff989bd7349c99b8f7cb438 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-007-P5` has one deterministic ETABS exported-file snapshot implementation from exact merged P4 base `426d401b` / tree `a5b01272` |
| **Next** | Freeze P5 content, run its focused batch, quick gate, normal staged hooks, hosted checks, and exact-tree merge |
| **Why** | P5 makes project/export/source identity, units, local axes, result selection, stable member IDs, exclusions, ambiguities, and every source row explicit before a canonical beam request exists |
| **Held** | P6-P7, M0 broad suites, live ETABS automation, EDB parsing, analysis control, model save/write-back, INDIA-3 engineering, release, branch/worktree deletion, and professional approval |

## P5 candidate outcome

- P4 merged through PR #856 at hosted `426d401b` / tree `a5b01272`; P5 starts
  from that exact tree and preserves the held INDIA-3 lane plus unrelated work.
- `build_etabs_canonical_snapshot_v1` reads only exported artifacts and delegates
  separate geometry and force CSVs to `parse_dual_csv_lossless`.
- EDB identity is recorded by name/hash without EDB intake. E2K and selected
  CSV/XML/Excel table archives are hash-bound; direct EDB parsing is rejected.
- Exact units, `M3 -> mu_knm` / `V2 -> vu_kn` mapping, and one case,
  combination, or source-envelope identity are required without implicit
  conversion or selection.
- ETABS `UniqueName` creates stable canonical member IDs. Every physical source
  row is `ACCEPTED`, `APPROVED_EXCLUSION`, or `BLOCKED`; any blocked row or
  ambiguity exposes no snapshot or request.
- The accepted synthetic fixture accounts 7 rows as 6 accepted, 1 approved
  non-beam exclusion, and 0 blocked, then emits two existing
  `ProjectBeamDesignInputV1` requests.
- Trial API access is optional. Manual ETABS table export remains the valid
  fallback and converges on the identical exported-file contract.

## P5 verification boundary

- Run snapshot/import/capability/project-beam/packaging focused tests together,
  then the consolidated quick gate once and normal staged hooks once.
- Verify the deterministic fixture and machine evidence, architecture/imports,
  docs, and unchanged REST/OpenAPI surface.
- Broad Python/FastAPI/React and full repository gates remain reserved for
  cumulative M0. P5 does not own P6, P7, live ETABS operation, release,
  professional approval, or INDIA-3 engineering.

## Required Reading

1. [Product-foundation convergence plan](lib-pro-007-product-foundation-convergence.md)
2. [P5 acquisition and snapshot guide](../guides/etabs-exported-snapshot-v1.md)
3. [P5 machine evidence](../verification/lib-pro-007-p5-etabs-snapshot-evidence.json)
4. [Current task board](../TASKS.md)
5. [Git workflow single source](../git-automation/git-workflow-single-source.md)
