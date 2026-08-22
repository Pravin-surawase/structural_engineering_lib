# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Modernize validation scheduling and reuse only exact PASS evidence.
- Git receipt: docs/verification/maint-012c-git-handoff-receipt.json | sha256:f4662fdc2b557aeb1c0011ce4f7aac795b09a4cb7cd704923e9dd4b0054da485 | HOLD
- Git identity: codex/maint-012c-evidence-scheduling@646660e323b65118a805b554c6cf4dbef46ef479 | upstream=origin/main@646660e323b65118a805b554c6cf4dbef46ef479 | base=origin/main@646660e323b65118a805b554c6cf4dbef46ef479 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `MAINT-012C` owns one strict local/hosted validation-domain map and exact content-addressed PASS reuse |
| **Next** | Complete the focused scheduler/cache/workflow contracts, freeze the candidate, run one quick and cumulative full gate plus ordinary hooks, then require every hosted check |
| **Why** | Local changed-check scheduling could silently no-op on unknown paths, hosted YAML duplicated ownership, and unchanged checks/jobs had no reusable command/runtime/input identity |
| **Held** | MAINT-012D scanner/script consolidation and physical compatibility deletion; product/structural/API/UI/Excel/ETABS behavior; dependencies; publication; settings; and professional approval |

## Exact MAINT-012C state

- Branch: `codex/maint-012c-evidence-scheduling`, created from exact merged
  `origin/main` commit `646660e323b65118a805b554c6cf4dbef46ef479`.
- Canonical scheduling: `scripts/verification-manifest.json`; read-only command:
  `./run.sh verification validate|plan|fingerprint|probe`.
- Seven domains: Python, FastAPI, React, Excel, control plane, docs, and
  repository. Every current path is owned; unknown paths/query failures select
  all seven. One rule set drives both job scheduling and fingerprint inputs.
- Local PASS receipts live in the Git common directory and bind current bytes,
  normalized command, declared domains, runtime/platform, and installed
  distributions. Git-state checks always run fresh; `--no-reuse` forces all
  selected checks fresh.
- Hosted jobs resolve runtime/dependencies before exact-key receipt lookup.
  There are no prefix restores, and the required PR Gate rejects missing or
  partially fail-closed applicability. The old repository catch-all is split so
  docs, architecture, and control checks run under their natural domains.
- MAINT-012B remains merged through PR #841. Compatibility generator files and
  scanner consolidation remain physically unchanged for MAINT-012D.

## Required Reading

1. [MAINT-012 modernization plan](maint-012-control-plane-modernization.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
