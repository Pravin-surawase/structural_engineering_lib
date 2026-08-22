# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Implement MAINT-012A canonical operation registry and compatibility projection.
- Git receipt: docs/verification/maint-012a-git-handoff-receipt.json | sha256:6248eb1d1331a6629863e30d9edc868211aabdcaef71516332dbed7138635862 | HOLD
- Git identity: codex/maint-012a-control-registry@fc904511cc7b9683b2b464cdef71a45d2e9ee277 | upstream=NONE@UNKNOWN | base=origin/main@fc904511cc7b9683b2b464cdef71a45d2e9ee277 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `MAINT-012A` replaces duplicated/implicit operation metadata with one strict registry while preserving the generated automation-map compatibility surface |
| **Next** | Freeze docs/session/receipt, refresh affected indexes once, run consolidated local gates, create the immutable commit, then push and obtain required hosted evidence |
| **Why** | Repeated script discovery, inferred permissions, and independently edited registries consume time and can disagree; A gives later index/scanner/cache packets one validated foundation |
| **Held** | Index retirement, evidence caching, CI/scanner redesign, script deletion/moves, product/structural/API/UI/Excel/ETABS behavior, dependencies, publication, settings, and professional approval |

## Exact MAINT-012A state

- Canonical registry: `scripts/control-plane.json`; strict schema:
  `scripts/control-plane.schema.json`.
- Loader/CLI: `scripts/control_plane/`; compact verdict:
  `./run.sh control validate`.
- Frozen parity: 128 total operations, 125 active operations, 3 deprecated
  compatibility operations, 113/113 top-level scripts, and zero unspecified
  active default permissions.
- Migrated consumers: find automation, tool registry, prompt router, permission
  enforcement/audit, governance permission validation, script coverage, and
  session context guidance.
- `scripts/automation-map.json` is generated compatibility data; refresh it only
  with `./run.sh control export-legacy --write`.

## Required Reading

1. [MAINT-012 modernization plan](maint-012-control-plane-modernization.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
