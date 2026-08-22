# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Replace high-churn generic indexes with a small validated context
- Git receipt: docs/verification/maint-012b-git-handoff-receipt.json | sha256:81293b2bfc69f568134ec2a311a352867649d56fed109228d0f446becc42ac3e | HOLD
- Git identity: codex/maint-012b-index-architecture@efd219178c4293ab106f43e37b903c5c268283aa | upstream=origin/main@efd219178c4293ab106f43e37b903c5c268283aa | base=origin/main@efd219178c4293ab106f43e37b903c5c268283aa | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `MAINT-012B` retires generic committed indexes and replaces them with one small validated routing manifest plus bounded read-only live summaries |
| **Next** | Freeze the local candidate, run one quick and one full gate plus ordinary hooks, publish the unchanged PR, and require hosted checks before merge |
| **Why** | The retired projections consumed 1.39 MB/43,141 lines, covered only part of their own topology, churned frequently, and made agents repeat refresh/check cycles instead of reading current files directly |
| **Held** | MAINT-012C evidence reuse/change-domain scheduling; MAINT-012D scanner/script consolidation and physical compatibility deletion; product/structural/API/UI/Excel/ETABS behavior; dependencies; publication; settings; and professional approval |

## Exact MAINT-012B state

- Canonical routing: `scripts/context-manifest.json`; strict read-only command:
  `./run.sh context validate|list|show|summary`.
- Retired baseline: 140 files removed or replaced, including all generic folder
  JSON indexes, 69 generic Markdown indexes, and `docs/docs-index.json`.
- Retained index-named surfaces: authored `docs/index.md`, the required API
  route page, and the specialized validated live-Git guidance manifest.
- Compatibility generator entry points remain temporarily discoverable but
  cannot write. Their physical disposition belongs to MAINT-012D.
- The manifest is event-driven: update it only when an area root, read-first
  authority, retained surface, or canonical operation changes. It needs no
  periodic regeneration; a bounded quarterly usefulness review is sufficient.

## Required Reading

1. [MAINT-012 modernization plan](maint-012-control-plane-modernization.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
