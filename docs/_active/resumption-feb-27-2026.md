# Project Resumption Brief — Feb 27, 2026

**Type:** Guide
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-02-27
**Last Updated:** 2026-02-27

---

## 1. Where We Left Off

**Last active:** Session 90–91 on **Feb 11, 2026** (~16 days ago).

**Current branch:** `codex/4layer-lock-hardening` (1 commit ahead of `main`)
- Adds 4-layer governance locking + migration integration tests
- No open PR for this branch yet

**Working tree:** Clean — nothing uncommitted.

---

## 2. What Was Done Recently (Sessions 86–91, Feb 10–11)

### Major Refactoring: Library + Scripts (Sessions 87–91)

A massive multi-phase refactoring effort was completed:

| Phase | Description | PR | Status |
|-------|-------------|----|--------|
| Phase 0 | Migration scripts + folder structure plan | — | Done |
| Phase 1 | Move 10 core modules to `structural_lib/core/` | #424 | Merged |
| Phase 2 | Move 17 service modules to `structural_lib/services/` | #424 | Merged |
| Phase 3 | Move 9 root modules to `services/` | #425 | Merged |
| Phase 4-5 | React component feature grouping + root cleanup | #426 | Merged |
| Post-migration | CSS→Tailwind, governance v3, archive plan | #427 | Merged |

### Scripts Consolidation (Sessions 89–91)

Reduced automation scripts from **163 → ~79 active** through 3 phases:

| Phase | Description | PR | Status |
|-------|-------------|----|--------|
| Phase 1 | Archive 53 deprecated, consolidate 4 groups | #428 | Merged |
| Phase 2 | Consolidate session/release/streamlit scripts | #429 | Merged |
| Phase 3 | Create `_lib/output.py`, `_lib/ast_helpers.py`, migrate 10 scripts | #430 | Merged |

### Bug Fixes (Session 88)

| Fix | Description | PR |
|-----|-------------|----|
| Blank screen on beam click | Added null guards for beam dimensions | #422 |
| Beam off-center in design view | Centered beam at origin, dynamic camera | #422 |
| Camera locked after transition | Removed continuous lerping | #422 |
| Cell edits not saving | Use fresh Zustand state instead of stale closure | #422 |

---

## 3. Current State of the Stack

### Versions & Releases

| Version | Status | Notes |
|---------|--------|-------|
| **v0.19.0** | Released | DXF polish, AI model fix, Streamlit API index |
| **v0.19.1** | In Progress | DXF/report export fixes, manual export buttons |
| **v0.20** | Next | V3 Foundation — library API additions, V3 automation |
| **v0.21+** | Planned | V3 React — full React + R3F + FastAPI (6-week migration) |

### Architecture Health

```
React 19 + R3F + Tailwind ──HTTP/WS──> FastAPI ──Python──> structural_lib
   react_app/                            fastapi_app/          Python/structural_lib/
```

- **Python core:** Reorganized into `core/` and `services/` subpackages — clean separation
- **FastAPI:** 20+ routes working, WebSocket live design operational, 31 tests passing
- **React:** Component feature grouping done, hooks wired to real API, Viewport3D functional
- **Scripts:** Down from 163 to ~79, shared `_lib/` utilities created, 280+ stale refs fixed
- **CI:** All checks passing on `main`

### Current Branch: `codex/4layer-lock-hardening`

This branch adds governance enforcement:
- 4-layer migration gates in `check_governance.py`
- `governance-limits.json` config file
- Migration integration tests (247 lines)
- Batch migrate runner improvements

**Decision needed:** Merge this to `main` or continue development?

---

## 4. Open Work Items (What's Next)

### Immediate (Short-term)

| Priority | Task | Context |
|----------|------|---------|
| **P0** | Merge/close `codex/4layer-lock-hardening` branch | 1 commit ahead, clean |
| **P1** | Wire dashboard insights into React Dashboard component | Hooks exist (`useInsights.ts`), needs UI wiring |
| **P1** | Add live code check badges to DesignView | `useCodeChecks` hook ready |
| **P2** | Add rebar suggestion "Apply" buttons | `useRebarSuggestions` hook ready |
| **P2** | Create export panel (BBS/DXF/CSV) | Export functions exist in library |

### Medium-term (V3 Foundation — v0.20)

| Task | Status |
|------|--------|
| Scripts Phase 3 continued: make more scripts use `_lib/utils.py` | Research doc updated |
| Add SSE batch progress UI for batch design | Not started |
| Add REST fallback when WebSocket unavailable (DesignView) | Not started |
| OpenAPI schema generation (FastAPI) | Not started |
| Scripts consolidation: 79 → 55 target | Partially done |

### Long-term (V3 React — v0.21+)

| Task | Status |
|------|--------|
| Dockview layout system | Not started |
| AG Grid for beam tables (replace basic table) | Not started |
| API client with React Query | Not started |
| Full 3D building visualization | Hooks exist, UI partial |

---

## 5. Key Files to Review

| File | Purpose |
|------|---------|
| [TASKS.md](../TASKS.md) | Full task board with history |
| [next-session-brief.md](../planning/next-session-brief.md) | Session-to-session handoff |
| [scripts-improvement-research.md](../research/scripts-improvement-research.md) | Scripts consolidation roadmap |
| [folder-structure-governance.md](../guidelines/folder-structure-governance.md) | New 4-layer governance rules |
| [governance-limits.json](../guidelines/governance-limits.json) | Governance enforcement config |

---

## 6. Stale Branches (Cleanup Candidates)

| Branch | Purpose | Likely Status |
|--------|---------|---------------|
| `task/TASK-073` | Unknown legacy task | Stale — check if merged |
| `task/TASK-090` | Unknown legacy task | Stale — check if merged |
| `task/TASK-AGENT-EFFICIENCY` | Agent efficiency improvements | Likely superseded by Session 65+ |
| `task/TASK-CI-AUDIT` | CI audit | Likely completed |
| `task/TASK-DUALCSV` | Dual CSV import | Done in Session 81 |
| `task/TASK-V3-PHASE2` | V3 Phase 2 | Done in PRs #424-427 |
| `task/TASK-V3-PHASE4` | V3 Phase 4 | Done in PR #426 |
| `task/TASK-V3PARITY` | V3 parity work | Done in Session 82 |
| `task/TASK-WS-001` | WebSocket implementation | Done in Session 73 |

**Recommendation:** Clean up merged/stale branches to reduce clutter.

---

## 7. Suggested Session Plan

1. **Decide on `codex/4layer-lock-hardening`** — merge PR or abandon
2. **Clean stale branches** — delete ~8 that are already merged
3. **Wire React UI** — Connect dashboard insights, code check badges, rebar suggestions
4. **Continue scripts cleanup** — Target the 79 → 55 reduction
5. **Update TASKS.md** — Refresh with current priorities

---

*Auto-generated resumption brief. Move to `docs/_archive/` when no longer needed.*
