---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# Agent Onboarding Audit — Session 93

**Type:** Audit
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-03-24
**Last Updated:** 2026-03-24

---

## Purpose

Fresh-agent onboarding test: followed all documented steps exactly as a new AI agent would, and logged every friction point, error, and inconsistency encountered. Then conducted a deep audit of archived scripts to uncover systemic issues.

---

## Root Cause

**Script consolidation (Sessions 81-92) archived 90+ scripts but didn't update all callers.** Active scripts still reference archived ones, causing silent failures, misleading output, and crashes — with no validation step to catch this.

---

## Issues Found

### CRITICAL — Broken Script Runtime References

Scripts that fail or silently skip important checks because they call archived scripts:

| # | Active Script | Archived Script | Impact |
|---|---------------|-----------------|--------|
| 1 | `session.py` L262 | `check_handoff_ready.py` | "Doc Freshness" and "Handoff Checks" ALWAYS say "Some checks failed" — perpetual warning with zero actionable info |
| 2 | `session.py` L462 | `generate_folder_index.py` | `session.py end --fix` silently skips README index updates |
| 3 | `finish_task_pr.sh` L279-292 | `ci_monitor_daemon.sh` | Default "Async" mode crashes after PR is created. Agent left on task branch |
| 4 | `generate_all_indexes.sh` L36-38 | `generate_folder_index.py` | Index regeneration completely broken |
| 5 | `watch_tests.sh` L45 | `quick_check.sh` | Initial validation on watch mode broken (+ called with python3 on a .sh file) |
| 6 | `audit_readiness_report.py` L333-417 | 6 scripts | Audit silently skips: API signatures, folder structure, governance, doc metadata, link check, API docs sync |

### HIGH — Stale Doc Paths in Script Output

| # | Script | Stale Path | Correct Path |
|---|--------|-----------|--------------|
| 7 | `session.py` L338 | `docs/handoff.md` | `docs/planning/next-session-brief.md` |
| 8 | `session.py` L338 | `docs/agent-bootstrap.md` | `docs/getting-started/agent-bootstrap.md` |
| 9 | `session.py` L338 | `docs/ai-context-pack.md` | Does not exist (removed) |
| 10 | `bump_version.py` L69 | `docs/ai-context-pack.md` | Removed stale entry |
| 11 | `agent_start.sh` L257 | `agent-essentials.md` (first doc) | Merged redirect → `agent-bootstrap.md` is the canonical one |

### MEDIUM — Misleading Output (Echoes of Archived Scripts)

| # | Script | References | Impact |
|---|--------|------------|--------|
| 12 | `agent_mistakes_report.sh` L133 | `git_ops.sh` | Tells agents to use non-existent script |
| 13 | `finish_task_pr.sh` L303-304 | `pr_async_merge.sh`, `ci_monitor_daemon.sh` | Shows non-existent commands |

### MEDIUM — Number Inconsistencies

| # | Where | Says | Actual |
|---|-------|------|--------|
| 14 | `agent_start.sh` L279 | "43 public functions" | 23 public + 6 private = 29 total |

### LOW — UX/Clarity Issues

| # | Issue |
|---|-------|
| 15 | `session.py check` fails with "missing Focus: line" but no template or auto-fix |
| 16 | `session.py summary` has no `--dry-run` preview option |
| 17 | Script discovery (`find_automation.py`) not shown in start script output |
| 18 | No validation step exists to prevent archiving scripts still referenced by active code |
| 19 | 1 pre-existing test failure: `test_valid_inputs_return_valid_geometry` |

---

## Bootstrap Experience Assessment

### What Works Well (Preserve These)

1. **`agent_start.sh --quick`** — Fast (6s), installs hooks, shows clear overview
2. **`discover_api_signatures.py`** — Excellent, exact params with units and types
3. **`find_automation.py`** — Good natural-language script discovery
4. **`ai_commit.sh`** — Reliable commit workflow with hooks + push
5. **`create_task_pr.sh`** — Clean branch creation with auto-stash
6. **`session.py sync`** — Correctly counts all metrics across docs
7. **4-layer architecture** — Well-documented and enforced
8. **Folder `index.json` + `index.md`** — Excellent for fast context loading
9. **`next-session-brief.md`** — Detailed handoff with clear priorities
10. **`agent-bootstrap.md`** — Comprehensive 350-line bootstrap doc

### What Didn't Work (Fixed in This PR)

1. **Perpetual "Some checks failed"** — Agents learn to ignore warnings because handoff check always fails
2. **PR workflow crash** — Default mode requires archived daemon, crashes mid-workflow
3. **Ghost doc paths** — Start script points to 3 non-existent files
4. **Wrong function counts** — 43 ≠ 23 — erodes trust in other numbers
5. **Script discovery buried** — `find_automation.py` not in start output; agents resort to `find` and `grep`
6. **No stale-ref prevention** — Scripts get archived, callers break silently, nobody notices for sessions

---

## Fixes Applied in This PR

### Pass 1 — Initial Onboarding Fixes
1. ✅ `session.py` — Inlined handoff check (replaces archived `check_handoff_ready.py`)
2. ✅ `session.py` — Fixed stale doc paths (handoff.md → next-session-brief.md, etc.)
3. ✅ `agent_start.sh` — Fixed API function count (43 → 23 public + 6 private)
4. ✅ `bump_version.py` — Removed stale `ai-context-pack.md` entry
5. ✅ `finish_task_pr.sh` — Graceful fallback when `ci_monitor_daemon.sh` missing

### Pass 2 — Deep Archived Script Audit
6. ✅ `finish_task_pr.sh` — Changed default from broken "Async" to working "Wait" (polls CI, auto-merges)
7. ✅ `finish_task_pr.sh` — Fixed `local` keyword used outside function (bash bug)
8. ✅ `generate_all_indexes.sh` — Updated `generate_folder_index.py` → `generate_enhanced_index.py`
9. ✅ `session.py` — Updated `generate_folder_index.py` → `generate_enhanced_index.py`
10. ✅ `watch_tests.sh` — Replaced broken `python3 scripts/quick_check.sh` with pytest
11. ✅ `agent_mistakes_report.sh` — Fixed stale `git_ops.sh` reference
12. ✅ `agent_start.sh` — Replaced `agent-essentials.md` (redirect) with correct docs
13. ✅ `agent_start.sh` — Added "Script Discovery" section (find_automation.py, discover_api_signatures.py)
14. ✅ `agent-bootstrap.md` — Fixed `--async` flag and `git_ops.sh` references
15. ✅ Created `validate_script_refs.py` — Detects stale references to prevent future regressions

---

## Remaining Issues (Not Fixed — Separate PRs)

| Issue | Why Not Fixed | Suggested Fix |
|-------|---------------|---------------|
| `audit_readiness_report.py` references 6 archived scripts | All use `.exists()` guard — functional but skip checks | Rewrite to use consolidated equivalents (`check_api.py`, `check_governance.py`, `check_docs.py`) |
| `session.py summary` no `--dry-run` | Feature addition, not a bug fix | Add `--dry-run` flag |
| 3 instruction files drift apart | Structural issue, needs dedicated effort | Single source-of-truth + auto-generation |
| `create_doc.py` references archived `check_doc_similarity.py` | Uses `.exists()` guard — graceful degradation | Re-implement similarity check inline |

---

## Systemic Recommendation

**Add `validate_script_refs.py` to CI or pre-commit.** This is the validation gap that caused all 18 issues. Every time a script is archived, the validator should be run to catch broken callers before merge.
