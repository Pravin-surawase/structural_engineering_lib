# Task Board

> Single source of truth for work. Keep it short and current.

---

## Rules (read first)
- WIP = 1. Move tasks between sections; do not duplicate.
- Definition of Done: tests pass, docs updated, CHANGELOG/RELEASES updated when needed.
- Keep "Recently Done" to the last 10-20 items; older history lives in the archive.
- Use agent roles from `agents/` and the workflow in `docs/_internal/AGENT_WORKFLOW.md`.

---

## Current Release

- Target: v0.12.1 (maintenance)
- Focus: test hardening + DXF/BBS regression fixtures
- Blockers: none (update when set)

---

## Active

No active tasks. Move one item from "Up Next" when starting.

---

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-129** | Reduce property-invariant skips by tightening generators (d > d_min, paired fy inputs) | TESTER | 2 hrs | 🟡 Medium | Ready |
| **TASK-130** | Add contract tests for units conversion boundaries at API/CLI entrypoints | TESTER | 2 hrs | 🟡 Medium | Ready |
| **TASK-131** | Add regression fixtures for BBS/DXF mark-diff (missing marks, mismatched counts) | TESTER | 2 hrs | 🟡 Medium | Ready |

---

## Backlog

### v1.0 Readiness (carryover)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-077** | External user CLI test | CLIENT | 1 hr | 🔴 Critical |
| **TASK-078** | Seismic detailing validation | TESTER | 45 min | 🟡 Medium |
| **TASK-079** | VBA parity spot-check | TESTER | 1 hr | 🟡 Medium |

### Post-v1.0 (beam scope)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-081** | Level C Serviceability (creep + shrinkage) | DEV | 1-2 days | 🟡 Medium |
| **TASK-082** | VBA parity automation harness | DEVOPS | 1-2 days | 🟡 Medium |
| **TASK-085** | Torsion design + detailing (Cl. 41) | DEV | 2-3 days | 🟡 Medium |
| **TASK-086** | Side-face reinforcement check (Cl. 26.5.1.3) | DEV | 4 hrs | 🟡 Medium |
| **TASK-087** | Anchorage space check (Cl. 26.2) | DEV | 1 day | 🟡 Medium |
| **TASK-088** | Slenderness/stability check (Cl. 23.1.2) | DEV | 4 hrs | 🟡 Medium |
| **TASK-089** | Flanged effective width helper | INTEGRATION | 1 day | 🟡 Medium |

---

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-126** | Warn on Table 19 fck out-of-range in shear design | DEV | ✅ Done |
| **TASK-127** | Document Table 19 range warning in known-pitfalls + error schema | DOCS | ✅ Done |
| **TASK-128** | Add tests for Table 19 range warning | TESTER | ✅ Done |
| **TASK-122** | v0.12 release notes (CHANGELOG + RELEASES) | DOCS | ✅ Done |
| **TASK-123** | v0.12 version bump (Python/VBA) | DEVOPS | ✅ Done |
| **TASK-124** | v0.12 session log + next-session brief | DOCS | ✅ Done |
| **TASK-125** | v0.12 release tag + publish | DEVOPS | ✅ Done |
| **TASK-104** | Define stable API surface + doc updates | DOCS | ✅ Done |
| **TASK-105** | Validation APIs + `validate` CLI subcommand | DEV | ✅ Done |
| **TASK-106** | Detailing + BBS APIs + `detail` CLI subcommand | DEV | ✅ Done |
| **TASK-107** | DXF/report/critical API wrappers (no behavior change) | DEV | ✅ Done |
| **TASK-108** | API/CLI tests + stability labels | TESTER | ✅ Done |

---

## Archive

- Full history: `docs/_archive/TASKS_HISTORY.md`
