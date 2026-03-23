# AI Agent Efficiency & Git Workflow Improvement Plan

**Type:** Planning
**Audience:** All Agents
**Status:** Implemented (Session 92)
**Importance:** High
**Created:** 2026-03-24
**Last Updated:** 2026-03-24

---

## Executive Summary

This repo already has **best-in-class** AI agent infrastructure — 83 mapped automation scripts, session continuity via `SESSION_LOG.md` + handoff docs, unified commit workflow (`ai_commit.sh`), 12 agent roles, and comprehensive per-filetype instructions. However, there are concrete opportunities to reduce context waste, eliminate duplication, adopt new Copilot features, and tighten the git workflow.

This document covers two areas:
1. **Making the repo more efficient for AI agents** (Part A)
2. **Making the git workflow better** (Part B)

---

## Part A: AI Agent Efficiency Improvements

### Current Strengths (What's Working)

| Area | Status | Notes |
|------|--------|-------|
| Unified commit (`ai_commit.sh`) | ✅ Excellent | Stages, hooks, PR check, safe push in one command |
| Session continuity | ✅ Excellent | `session.py` summary/sync/handoff auto-generates context |
| Automation discovery | ✅ Good | 83/83 scripts mapped, fuzzy search via `find_automation.py` |
| Per-filetype rules | ✅ Good | 5 domain rule files for Python, React, Streamlit, VBA, docs |
| Agent roles | ✅ Good | 12 roles defined, orchestration documented |
| Safety guardrails | ✅ Good | PR decision script, pre-commit hooks, git hooks |

### Problem 1: Instruction Duplication (Context Token Waste)

**Impact:** High — agents load 3 nearly-identical files, wasting ~40% of instruction tokens.

**Current state:**
- `CLAUDE.md` (149 lines) ≈ `.github/copilot-instructions.md` (149 lines) — **99% identical**
- `.claude/rules/*.md` (6 files) ≈ `.github/instructions/*.instructions.md` (5 files) — **same content, different format**
- `docs/getting-started/agent-bootstrap.md` — overlaps with both

**Recommendation:** Single Source of Truth (SSOT) strategy:

| File | Role | Content |
|------|------|---------|
| `.github/copilot-instructions.md` | **Canonical** for Copilot (VS Code, GitHub.com) | Full rules (repo-wide) |
| `CLAUDE.md` | **Canonical** for Claude Code | Full rules (identical content is fine — they serve different agents) |
| `.github/instructions/*.instructions.md` | **Canonical** per-file-type rules for Copilot | Domain-specific rules |
| `.claude/rules/*.md` | **Sync target** — auto-generated from `.github/instructions/` | Same content, `.claude` format |

**Action items:**
- [ ] Create `scripts/sync_agent_rules.sh` — copies `.github/instructions/*.instructions.md` → `.claude/rules/*.md` (addjusting frontmatter format)
- [ ] Add sync to `agent_start.sh` pre-flight (ensures rules never drift)
- [ ] Document in CLAUDE.md: "`.claude/rules/` is auto-synced from `.github/instructions/`"

### Problem 2: No AGENTS.md File (Missing Standard)

**Impact:** Medium — GitHub Copilot now supports `AGENTS.md` as a first-class instruction file (alongside `CLAUDE.md` and `GEMINI.md`). This is the emerging **cross-agent standard** (19k+ stars on GitHub).

**Recommendation:**
- [ ] Create `AGENTS.md` in repo root — a cross-platform instruction file that works with Copilot, Claude, Cursor, Windsurf, and other AI tools
- [ ] Keep it focused on the 20% of instructions that cover 80% of use cases
- [ ] Reference `CLAUDE.md` and `.github/copilot-instructions.md` for full details

### Problem 3: No Copilot Prompt Files

**Impact:** Medium — Copilot supports `.github/prompts/*.prompt.md` for reusable task templates. This could replace many manual workflow descriptions.

**Recommendation:** Create prompt files for common agent tasks:

| Prompt File | Purpose |
|-------------|---------|
| `.github/prompts/new-feature.prompt.md` | Template for adding a new feature (search → implement → test → commit) |
| `.github/prompts/bug-fix.prompt.md` | Template for fixing bugs (reproduce → diagnose → fix → test) |
| `.github/prompts/session-end.prompt.md` | Template for session end workflow (commit → summary → sync → handoff) |
| `.github/prompts/code-review.prompt.md` | Template for reviewing code changes |
| `.github/prompts/add-api-endpoint.prompt.md` | Template for adding a FastAPI endpoint |

### Problem 4: No Copilot Hooks

**Impact:** Medium — Copilot hooks (`.github/hooks/*.json`) allow deterministic actions at agent lifecycle points. This could auto-format code after every file edit and validate tests before committing.

**Recommendation:**
- [ ] Create `.github/hooks/format-on-edit.json` — Run Black + Ruff after every Python file edit
- [ ] Create `.github/hooks/validate-imports.json` — Check architecture boundaries after structural_lib edits
- [ ] Monitor Copilot hooks feature availability (currently preview in VS Code)

### Problem 5: No Copilot Custom Agents

**Impact:** Medium-Low — Copilot now supports `.github/agents/AGENT-NAME.md` for custom agent personas. The repo already has `agents/roles/*.md` (12 roles) but they aren't in Copilot's recognized format.

**Recommendation:**
- [ ] Create `.github/agents/governance.md` — Specialist for weekly maintenance checks
- [ ] Create `.github/agents/reviewer.md` — Code review agent with IS 456 domain knowledge
- [ ] Keep existing `agents/roles/*.md` as the detailed specification; `.github/agents/` as the Copilot-native entry points

### Problem 6: SESSION_LOG.md is 400KB+ (Context Overload)

**Impact:** Medium — agents that try to read session history waste context tokens on 400KB of historical data.

**Recommendation:**
- [ ] Create `docs/SESSION_LOG_RECENT.md` — auto-generated, last 10 sessions only (~20KB)
- [ ] Add to `session.py end` — auto-truncate recent view
- [ ] Update CLAUDE.md to point agents to the recent file instead

### Problem 7: `automation-map.json` Lacks Tags

**Impact:** Low — fuzzy matching works but misses cases where agents use different terminology.

**Recommendation:**
- [ ] Add `"tags"` field to each automation entry (e.g., `["git", "commit", "safe", "push"]`)
- [ ] Update `find_automation.py` to search tags as well as descriptions
- [ ] Low effort, high discoverability gain

### Problem 8: `index.json` Files Are Stale

**Impact:** Low — `Python/index.json` shows `file_count: 0`, `last_updated: 2026-01-21`. Stale indexes mislead agents.

**Recommendation:**
- [ ] Run `.venv/bin/python scripts/generate_enhanced_index.py --all` to refresh
- [ ] Add index regeneration to `session.py end` workflow
- [ ] Or add to monthly governance (Agent 9) checklist

---

## Part B: Git Workflow Improvements

### Current Strengths

| Area | Status | Notes |
|------|--------|-------|
| `ai_commit.sh` | ✅ Excellent | 7-step safe workflow (stash → fetch → stage → commit → hooks → sync → push) |
| `safe_push.sh` | ✅ Excellent | Prevents force-push, handles conflicts |
| `should_use_pr.sh` | ✅ Good | Automated PR vs direct decision |
| `create_task_pr.sh` / `finish_task_pr.sh` | ✅ Good | Full PR lifecycle scripted |
| Pre-commit hooks | ✅ Good | Black, Ruff, mypy, bandit, isort, whitespace |
| Git hooks (custom) | ✅ Good | pre-commit, pre-push, commit-msg via `core.hooksPath` |
| `recover_git_state.sh` | ✅ Good | Automated recovery from common failures |

### Improvement 1: Conventional Commits Enforcement

**Current state:** `ai_commit.sh` accepts any message. Some messages follow `type: description` but not enforced.

**Recommendation:**
- [ ] Add `commit-msg` hook validation for conventional commits format: `^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .{1,72}$`
- [ ] The hook already exists in `scripts/git-hooks/commit-msg` — verify it validates format
- [ ] Add scopes matching folder areas: `(react)`, `(fastapi)`, `(python)`, `(vba)`, `(docs)`, `(scripts)`, `(ci)`, `(export)`

**Why:** Enables auto-generated changelogs, searchable git history, and better session summaries.

### Improvement 2: Branch Protection & Merge Strategy

**Current state:** `should_use_pr.sh` recommends PRs for production code, but enforcement is advisory.

**Recommendation:**
- [ ] Enable GitHub branch protection on `main`: require CI pass, require PR for `Python/structural_lib/`, `VBA/`, `fastapi_app/`
- [ ] Set merge strategy to squash-merge for PRs (cleaner history)
- [ ] Allow direct push for `docs/`, `scripts/`, `tests/` (matches current decision matrix)

### Improvement 3: Automated PR Templates

**Current state:** `create_task_pr.sh` creates branches but no standardized PR body.

**Recommendation:**
- [ ] Create `.github/PULL_REQUEST_TEMPLATE.md` with sections:
  - **What:** Summary of changes
  - **Why:** Task reference or motivation
  - **Testing:** What was tested, what to verify
  - **Checklist:** Architecture boundaries respected, units explicit, tests pass

### Improvement 4: Pre-push Validation

**Current state:** Pre-push hook exists but scope unclear.

**Recommendation:**
- [ ] Pre-push should run: `pytest tests/ -x --timeout=60` (quick fail)
- [ ] Pre-push should check: no `TODO(urgent)` or `FIXME(critical)` in staged files
- [ ] Pre-push should verify: `session.py` can find matching SESSION_LOG entry (prevent orphan pushes)

### Improvement 5: Git Log Rotation

**Current state:** 181 hook log files in `logs/` tracked in git. Growing ~60/month.

**Recommendation:**
- [ ] Add `logs/hook_output_*.log` to `.gitignore`
- [ ] Add log rotation script: keep last 30 days, archive older to `logs/_archive/`
- [ ] Run rotation in `agent_start.sh` or monthly governance

### Improvement 6: Stale Branch Cleanup

**Current state:** No documented branch cleanup process.

**Recommendation:**
- [ ] Add `scripts/clean_stale_branches.sh` — lists branches merged to main, deletes after confirmation
- [ ] Run weekly via Agent 9 governance or monthly manual check
- [ ] Prune remote tracking branches: `git fetch --prune`

### Improvement 7: Commit Signing

**Current state:** No commit signing configured.

**Recommendation (future):**
- [ ] Configure GPG or SSH commit signing for verified commits
- [ ] Add to `agent_start.sh` setup if signing key available
- [ ] Low priority — cosmetic but adds trust

---

## Implementation Priority Matrix

| # | Item | Impact | Effort | Priority |
|---|------|--------|--------|----------|
| A1 | Rule sync script (dedup `.claude/rules/`) | High | Low | **P1** |
| A2 | Create `AGENTS.md` | Medium | Low | **P1** |
| A3 | Copilot prompt files (5 templates) | Medium | Medium | **P2** |
| B1 | Conventional commits enforcement | High | Low | **P1** |
| B3 | PR template | Medium | Low | **P1** |
| A6 | SESSION_LOG recent view | Medium | Low | **P2** |
| B5 | Git log rotation + `.gitignore` | Medium | Low | **P2** |
| A7 | Automation map tags | Low | Low | **P2** |
| A8 | Refresh stale `index.json` | Low | Low | **P2** |
| B2 | Branch protection rules (GitHub settings) | Medium | Low | **P2** |
| B4 | Pre-push validation improvements | Medium | Medium | **P3** |
| A4 | Copilot hooks (format on edit) | Medium | Medium | **P3** |
| A5 | Copilot custom agents | Medium-Low | Medium | **P3** |
| B6 | Stale branch cleanup script | Low | Low | **P3** |
| B7 | Commit signing | Low | Low | **P4** |

---

## Quick Wins (Can Do Now) — IMPLEMENTED

These items were completed in Session 92:

1. **Created `AGENTS.md`** ✅ — Cross-platform agent instruction file (Copilot, Claude, Cursor, Windsurf)
2. **Improved `.github/pull_request_template.md`** ✅ — Added architecture/units checklist, multi-stack testing
3. **Created `.github/prompts/` (5 templates)** ✅ — session-end, new-feature, bug-fix, add-api-endpoint, code-review
4. **Created `.github/instructions/fastapi.instructions.md`** ✅ — Missing Copilot per-file rules for FastAPI
5. **Merged divergent instruction content** ✅ — `.github/instructions/` and `.claude/rules/` now both have comprehensive content

### Items that already existed (no action needed):
- ~~Conventional commits~~ → Already enforced by `scripts/git-hooks/commit-msg` hook
- ~~PR template~~ → Already at `.github/pull_request_template.md` (improved)
- ~~`.gitignore` for logs/tmp~~ → `logs/*` and `tmp/` already excluded
- ~~Git log rotation~~ → `logs/*` already in `.gitignore` (hook logs not tracked in git)

---

## Metrics to Track

After implementing, track:
- **Context waste:** Average tokens spent on instructions per session (should decrease)
- **Rule drift:** Days since last `.claude/rules/` vs `.github/instructions/` mismatch
- **Commit quality:** % of commits following conventional format
- **Session compliance:** % of sessions with proper start/end logging
- **PR turnaround:** Time from PR creation to merge

---

## References

- [GitHub Copilot Customization Cheat Sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)
- [AGENTS.md Standard](https://github.com/agentsmd/agents.md) — 19k+ stars
- [Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [About Customizing Copilot Responses](https://docs.github.com/en/copilot/concepts/prompting/response-customization)
