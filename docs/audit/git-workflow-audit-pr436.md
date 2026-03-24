# Git Workflow Audit — PR #436 Merge

**Type:** Audit
**Audience:** All Agents
**Status:** Approved
**Importance:** High
**Created:** 2026-03-25
**Last Updated:** 2026-03-25

---

## Purpose

Document all git workflow issues and improvements found while merging PR #436 (TASK-500: Unified CLI + onboarding audit). This PR was deliberately used as a full workflow test covering branch creation, CI checks, review comments, fixes, and squash merge.

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
**Status:** Fixed in this PR

Root file count limits were defined in **three different places** with **three different values**:

| Source | Value Before Fix | Purpose |
|--------|-----------------|---------|
| `docs/guidelines/governance-limits.json` | 16 | JSON config (canonical?) |
| `scripts/check_root_file_count.sh` | 15 | CI bash check |
| `scripts/check_governance.py` | 15 (hardcoded default) | Python validator |

**Root cause:** When `AGENTS.md` and `CLAUDE.md` were added, only the JSON was bumped to 16, but the bash and Python scripts still had 15. When `run.sh` was added (file #17), all three disagreed.

**Fix applied:** Set all three to 17. Added `run.sh`, `AGENTS.md`, `CLAUDE.md` to the `allowed_files` whitelist in `check_governance.py`.

**Recommendation:** Make `governance-limits.json` the single source of truth. Both `check_root_file_count.sh` and `check_governance.py` should read from it instead of using hardcoded defaults. This prevents drift when new root files are added.

### ISSUE-2: Index Format Mismatch Between Generator and Checker

**Severity:** High
**Status:** Fixed in this PR

The `generate_enhanced_index.py` script generates `index.json` with a `files` array format:
```json
{"files": [{"name": "script.py", ...}]}
```

But `check_scripts_index.py` expected the old `categories → scripts` format:
```json
{"categories": [{"scripts": [{"filename": "script.py"}]}]}
```

This caused the Scripts Validation CI check to fail even when `index.json` was freshly regenerated.

**Fix applied:** Updated `_load_indexed_scripts()` in `check_scripts_index.py` to support both formats — tries `categories` first, falls back to `files` array.

**Recommendation:** Standardize on the `files` array format since that's what the active generator produces. Consider deprecating the old `categories` format.

### ISSUE-3: Phantom Scripts in automation-map.json

**Severity:** Medium
**Status:** Fixed in this PR

Seven scripts that were archived (moved to `scripts/_archive/`) were still listed in `automation-map.json`:
- `check_ui_duplication.py`
- `check_performance_issues.py`
- `check_cost_optimizer_issues.py`
- `validate_session_state.py`
- `generate_streamlit_page.py`
- `launch_streamlit.sh`
- `profile_streamlit_page.py`

**Root cause:** The archive script (`archive_old_files.sh`) moves files but doesn't update `automation-map.json`. There's no automated sync between the filesystem and the map.

**Recommendation:** Add a check to `check_scripts_index.py` that verifies every script referenced in `automation-map.json` actually exists on disk. Or have `archive_old_files.sh` automatically remove entries from the map.

### ISSUE-4: `gh pr merge` Multi-Line Body Breaks zsh

**Severity:** Low
**Status:** Workaround applied

Running `gh pr merge` with a multi-line `--body` argument containing line breaks caused the terminal to get stuck in a `dquote>` prompt. The zsh shell interpreted the embedded newlines as incomplete string delimiters.

**Workaround:** Use a single-line body with single quotes:
```bash
gh pr merge 436 --squash --subject 'feat: ...' --body 'Single line summary'
```

**Recommendation:** Update `finish_task_pr.sh` to handle the merge step and ensure body text is properly escaped. Agents should not need to call `gh pr merge` directly.

### ISSUE-5: `finish_task_pr.sh` Not Used for Merge

**Severity:** Medium
**Status:** Observation

The intended workflow is `create_task_pr.sh` → work → `finish_task_pr.sh`. However, `finish_task_pr.sh` was not actually used for the merge. Instead, `gh pr merge` was called directly because:
1. The PR had CI failures that needed manual investigation
2. The finish script's behavior with already-fixed CIs wasn't clear
3. Direct merge gave more control over the squash commit message

**Recommendation:** Audit `finish_task_pr.sh` to ensure it:
- Waits for CI to pass (with timeout)
- Shows clear status of each check before merging
- Allows custom squash commit messages
- Falls back gracefully if a check is pre-existing failure (not introduced by PR)

### ISSUE-6: Pre-Existing CI Failures Not Distinguished from PR Failures

**Severity:** Medium
**Status:** Observation

The `check_all.py` run showed 9 failures, but ALL were pre-existing issues on main:
- `check_api.py --sync` (3 missing API symbols)
- `generate_api_manifest.py` (pydantic import error)
- `check_links.py` (9 broken doc links)
- `check_tasks_format.py` (missing heading)
- `check_architecture_boundaries.py` (2 violations)
- `validate_imports.py` (293 Streamlit stub imports)
- `check_openapi_snapshot.py` (stale snapshot)
- `check_type_annotations.py` (missing annotations)

It's hard for an agent (or developer) to know which failures are their fault vs pre-existing.

**Recommendation:** Add a `--baseline` mode to `check_all.py` that compares results against a stored baseline. Show only **new** failures introduced by the current branch. This is the single biggest workflow improvement that would save agent time.

---

## What Worked Well

1. **`ai_commit.sh`** — Reliable for staging, committing, and pushing. No issues in 6 commits.
2. **CI pipeline structure** — Three parallel jobs (Docs, Scripts, Python+FastAPI) give fast feedback (~2 min).
3. **Copilot code review** — Caught real issues (unused parameter, missing error handling, misleading description).
4. **`check_all.py --serial`** — Great for local debugging. Clear category grouping and pass/fail summary.
5. **`check_governance.py`** — Comprehensive (11 checks) with actionable error messages.
6. **`check_scripts_index.py`** — Catches drift between scripts folder and documentation indexes.
7. **Squash merge** — Collapses 6 development commits into one clean merge commit.

---

## Improvement Priorities

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| P1 | Single source of truth for governance limits (ISSUE-1) | Small | Prevents recurring config drift |
| P1 | Baseline mode for `check_all.py` (ISSUE-6) | Medium | Saves 30+ min per PR for agents |
| P2 | Auto-sync `automation-map.json` on archive (ISSUE-3) | Small | Prevents phantom entries |
| P2 | Audit `finish_task_pr.sh` merge flow (ISSUE-5) | Medium | End-to-end PR script coverage |
| P3 | Standardize index.json format (ISSUE-2) | Small | Already fixed, needs cleanup |
| P3 | Fix `gh pr merge` escaping (ISSUE-4) | Small | Edge case, workaround exists |

---

## Summary

The git workflow is **functional and mostly robust**. The main pain points are:
1. **Config drift** — multiple files defining the same setting (governance limits)
2. **No baseline comparison** — can't tell PR failures from pre-existing failures
3. **Incomplete automation** — `finish_task_pr.sh` not covering the merge step well enough

The `run.sh` + `check_all.py` additions (from this same PR) significantly improved the developer/agent experience by providing a single entry point for all validation.
