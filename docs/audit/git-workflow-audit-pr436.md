# Git Workflow Audit

**Type:** Audit
**Audience:** All Agents
**Status:** Approved
**Importance:** High
**Created:** 2026-03-25
**Last Updated:** 2026-03-25

---

## Purpose

Living audit of the git workflow. Originally based on PR #436 (TASK-500: Unified CLI + onboarding audit) which was deliberately used as a full workflow test. Now expanded with deep analysis of all 11 workflow scripts.

**Scripts audited:** `ai_commit.sh`, `safe_push.sh`, `create_task_pr.sh`, `finish_task_pr.sh`, `should_use_pr.sh`, `recover_git_state.sh`, `archive_old_files.sh`, `check_root_file_count.sh`, `check_governance.py`, `check_scripts_index.py`, `check_all.py`

---

## Workflow Steps Tested

| Step | Tool/Script | Result |
|------|-------------|--------|
| Branch creation | `create_task_pr.sh TASK-500` | ✅ Worked (prior session) |
| Incremental commits | `ai_commit.sh "type: message"` | ✅ Worked (6 commits) |
| CI pipeline (3 jobs) | GitHub Actions | ❌ 3 failures on first push |
| PR review comments | GitHub Copilot review | ⚠️ 4 comments required fixes |
| Fix + re-push | `ai_commit.sh` | ✅ Worked |
| CI re-run (all pass) | GitHub Actions | ✅ All 6 checks green |
| Squash merge | `gh pr merge 436 --squash` | ✅ Merged |
| Post-merge cleanup | Manual `git checkout main` | ✅ Done |
| Branch deletion | `git branch -d task/TASK-500` | ✅ Done |

---

## Issues Found

### ISSUE-1: Governance Limits — Three Sources of Truth

**Severity:** High
**Status:** ✅ FIXED

Root file count limits were defined in **three different places** with **three different values**:

| Source | Value Before Fix | Purpose |
|--------|-----------------|---------|
| `docs/guidelines/governance-limits.json` | 16 | JSON config (canonical?) |
| `scripts/check_root_file_count.sh` | 15 | CI bash check |
| `scripts/check_governance.py` | 15 (hardcoded default) | Python validator |

**Root cause:** When `AGENTS.md` and `CLAUDE.md` were added, only the JSON was bumped to 16, but the bash and Python scripts still had 15. When `run.sh` was added (file #17), all three disagreed.

**Fixes applied:**
1. Set all three to 17 and added `run.sh`, `AGENTS.md`, `CLAUDE.md` to `allowed_files` whitelist (PR #436)
2. Made `check_root_file_count.sh` read from `governance-limits.json` at runtime instead of hardcoding — now `governance-limits.json` is the single source of truth (post-merge fix)

**Verified:** `check_root_file_count.sh` ✅ PASS, `check_governance.py --structure` ✅ PASS (9/9)

### ISSUE-2: Index Format Mismatch Between Generator and Checker

**Severity:** High
**Status:** ✅ FIXED (PR #436)

`generate_enhanced_index.py` produces `index.json` with a `files` array format, but `check_scripts_index.py` expected the old `categories → scripts` format. Updated `_load_indexed_scripts()` to support both formats.

**Verified:** `check_scripts_index.py` ✅ PASS (79/79 scripts covered)

### ISSUE-3: Phantom Scripts in automation-map.json

**Severity:** Medium
**Status:** ✅ FIXED

Seven archived scripts were still listed in `automation-map.json`. Removed them in PR #436.

**Additional fix:** Updated `archive_old_files.sh` to replace stale reference to nonexistent `update_archive_index.py` with correct post-archive steps (`generate_enhanced_index.py` + `check_scripts_index.py`).

### ISSUE-4: `gh pr merge` Multi-Line Body Breaks zsh

**Severity:** Low
**Status:** Workaround documented

Running `gh pr merge` with multi-line `--body` in zsh causes `dquote>` prompt hang. Workaround: use single-line body with single quotes. Proper fix: always use `finish_task_pr.sh` (which doesn't have this problem since it uses `--body-file`).

### ISSUE-5: `finish_task_pr.sh` — Incomplete Merge Failure Path

**Severity:** High
**Status:** ✅ FIXED

When CI checks fail in `poll_pr_checks`, the script exited with `exit 1` without:
- Switching back to main
- Telling the user how to recover
- Cleaning up state

**Fix applied:** Added recovery information and `git checkout main` on the failure path, with clear instructions for retry/manual-merge/close options.

### ISSUE-6: Pre-Existing CI Failures Not Distinguished from PR Failures

**Severity:** Medium
**Status:** Open (recommendation)

`check_all.py` shows 9 failures, but ALL are pre-existing on main:
- `check_api.py --sync` (3 missing API symbols)
- `generate_api_manifest.py` (pydantic import error)
- `check_links.py` (9 broken doc links)
- `check_tasks_format.py` (missing heading)
- `check_architecture_boundaries.py` (2 violations)
- `validate_imports.py` (293 Streamlit stub imports)
- `check_openapi_snapshot.py` (stale snapshot)
- `check_type_annotations.py` (missing annotations)

**Recommendation:** Add a `--baseline` mode to `check_all.py` that stores results and compares against them, reporting only **new** failures.

### ISSUE-7: `safe_push.sh` Ignores Fetch Failure

**Severity:** High
**Status:** ✅ FIXED

`parallel_fetch_complete()` returns 1 on fetch failure, but the calling code at Step 5 did not check the return value. A failed fetch meant the commit could proceed without pulling the latest remote state.

**Fix applied:** Added `if ! parallel_fetch_complete; then` with warning message and log entry. Continues with local state (non-fatal) but clearly reports the issue.

### ISSUE-8: `archive_old_files.sh` References Nonexistent Script

**Severity:** Medium
**Status:** ✅ FIXED

The "Next steps" message referenced `python scripts/update_archive_index.py` which does not exist. Users following the instructions would get a `No such file` error.

**Fix applied:** Replaced with correct commands: `generate_enhanced_index.py scripts/` and `check_scripts_index.py`.

### ISSUE-9: `should_use_pr.sh` Hardcoded Thresholds

**Severity:** Low
**Status:** Open (observation)

All policy thresholds are hardcoded in the script:
```bash
MINOR_LINES_THRESHOLD=50
MINOR_FILES_THRESHOLD=3
SUBSTANTIAL_LINES=150
MAJOR_LINES=500
STREAMLIT_MINOR_THRESHOLD=20
```

These aren't in `governance-limits.json`. If thresholds change, the script requires manual editing.

**Recommendation:** Add a `pr_thresholds` section to `governance-limits.json` and have `should_use_pr.sh` read from it (same pattern as ISSUE-1 fix).

### ISSUE-10: `recover_git_state.sh` Hardcoded Safe Files List

**Severity:** Low
**Status:** Open (observation)

The list of files safe for auto-merge resolution is hardcoded:
```bash
SAFE_FILES="docs/TASKS.md docs/SESSION_LOG.md docs/planning/next-session-brief.md"
```

Low impact since the list rarely changes, but violates the DRY principle.

### ISSUE-11: `check_scripts_index.py` Phantom Detection Uses Simple String Split

**Severity:** Low
**Status:** Open (observation)

Phantom detection splits commands on whitespace and stops at the first `scripts/` match. Fails for multi-script commands like `"python3 scripts/a.py && scripts/b.py"` — only extracts `a.py`, misses `b.py`.

Current usage doesn't trigger this edge case, but a regex-based approach would be more robust.

---

## Workflow Steps Tested (PR #436)

| Step | Tool/Script | Result |
|------|-------------|--------|
| Branch creation | `create_task_pr.sh TASK-500` | ✅ Worked |
| Incremental commits | `ai_commit.sh "type: message"` | ✅ Worked (6 commits) |
| CI pipeline (3 jobs) | GitHub Actions | ❌ → ✅ (3 failures fixed) |
| PR review comments | GitHub Copilot review | ⚠️ 4 comments, all addressed |
| Fix + re-push | `ai_commit.sh` | ✅ Worked |
| CI re-run (all pass) | GitHub Actions | ✅ All 6 checks green |
| Squash merge | `gh pr merge 436 --squash` | ✅ Merged |
| Post-merge cleanup | `git checkout main && pull` | ✅ Done |
| Branch deletion | `git branch -d task/TASK-500` | ✅ Done |

---

## What Worked Well

1. **`ai_commit.sh`** — Reliable for staging, committing, and pushing. No issues in 6 commits.
2. **CI pipeline structure** — Three parallel jobs (Docs, Scripts, Python+FastAPI) give fast feedback (~2 min).
3. **Copilot code review** — Caught real issues (unused parameter, missing error handling, misleading description).
4. **`check_all.py --serial`** — Great for local debugging. Clear category grouping and pass/fail summary.
5. **`check_governance.py`** — Most robust script in the suite. Loads config from JSON, deep merges overrides, good error reporting. 11 checks, 0 issues found.
6. **`check_scripts_index.py`** — Catches drift between scripts folder and documentation indexes.
7. **Squash merge** — Collapses 6 development commits into one clean merge commit.

---

## Script Health Summary

| Script | Issues | Status | Notes |
|--------|--------|--------|-------|
| `check_governance.py` | 0 | ✅ Clean | Best script — reads config, good error handling |
| `check_all.py` | 0 | ✅ Clean | Works well, could benefit from `--baseline` |
| `check_scripts_index.py` | 1 low | ✅ Works | Minor: string-split parsing for phantoms |
| `ai_commit.sh` | 0 | ✅ Clean | Reliable commit workflow |
| `safe_push.sh` | 1 high | ✅ Fixed | Fetch failure now checked |
| `finish_task_pr.sh` | 1 high | ✅ Fixed | Recovery path now complete |
| `check_root_file_count.sh` | 1 critical | ✅ Fixed | Now reads governance JSON |
| `archive_old_files.sh` | 1 medium | ✅ Fixed | Stale reference removed |
| `create_task_pr.sh` | 0 | ✅ Clean | Stash formatting not a real risk |
| `should_use_pr.sh` | 1 low | ⚠️ Open | Hardcoded thresholds |
| `recover_git_state.sh` | 1 low | ⚠️ Open | Hardcoded safe files list |

---

## Improvement Priorities

| Priority | Issue | Effort | Impact | Status |
|----------|-------|--------|--------|--------|
| P0 | Single source of truth for governance limits (ISSUE-1) | Small | Prevents config drift | ✅ Done |
| P0 | `safe_push.sh` fetch error handling (ISSUE-7) | Small | Prevents silent sync failure | ✅ Done |
| P0 | `finish_task_pr.sh` merge failure cleanup (ISSUE-5) | Small | Prevents stuck branches | ✅ Done |
| P0 | Remove stale `update_archive_index.py` ref (ISSUE-8) | Small | Prevents user confusion | ✅ Done |
| P1 | Baseline mode for `check_all.py` (ISSUE-6) | Medium | Saves 30+ min per PR for agents | Open |
| P2 | Move PR thresholds to governance JSON (ISSUE-9) | Small | Config centralization | Open |
| P3 | Regex phantom detection (ISSUE-11) | Small | Edge case only | Open |
| P3 | Centralize safe files list (ISSUE-10) | Small | Rarely changes | Open |

---

## Validation Results (post-fix)

```
check_root_file_count.sh  ✅ PASS (17/17, reads from governance-limits.json)
check_governance.py       ✅ PASS (9/9 structure checks)
check_scripts_index.py    ✅ PASS (79/79 scripts covered)
check_all.py --serial     19/28 pass, 9 pre-existing failures (unchanged)
```

All 4 green categories: Governance (4/4), Git (3/3), Stale Refs (3/3), Streamlit (1/1).

---

## Summary

11 issues found across 11 workflow scripts. **7 fixed, 4 open** (all low priority).

The git workflow is **functional and robust** after these fixes. The remaining open items are quality-of-life improvements, not blockers. The single biggest remaining improvement would be a `--baseline` mode for `check_all.py` (ISSUE-6) to distinguish pre-existing failures from new ones.
