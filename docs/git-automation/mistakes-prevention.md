# Git Automation: Mistakes Prevention Guide

**Type:** Reference
**Audience:** All Agents
**Status:** Production Ready
**Importance:** Critical
**Version:** 0.16.5
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** Documentation consolidation

---

## Overview

Historical database of every git mistake made in this project. Learn from 100+ hours of debugging to prevent issues before they occur.

> **Philosophy:** Every mistake here led to real time lost. Read this to avoid repeating history.

---

## 🚨 Critical Mistakes Database

### 1. The Merge Commit Spike Disaster (2026-01-06)

**Impact:** CRITICAL
- 17 merge commits in a single day
- 40% of commits were merge commits
- 50% of pushes resulted in conflicts
- 3-5 minutes wasted per push

**Root Cause:**
```bash
# ❌ WRONG ORDER (caused 17 merge commits)
git commit -m "message"
[pre-commit hooks modify files]
git commit --amend --no-edit
git pull  # ← Too late! Original commit might be pushed
git push  # ← Creates conflict because hash changed
```

**The Problem:**
> "git commit --amend REWRITES HISTORY. Never amend after push."

**The Fix (Built Into safe_push.sh):**
```bash
# ✅ CORRECT ORDER (Agent 8 enforces this)
git pull --ff-only              # [1] Pull FIRST
git add .
git commit -m "message"         # [2] Commit
[pre-commit hooks modify files]
git add .
git commit --amend --no-edit    # [3] Amend BEFORE any push
git pull --ff-only              # [4] Pull AGAIN (catch race conditions)
git push                        # [5] Push
```

**Prevention:**
- ALWAYS use `./scripts/ai_commit.sh` - it enforces correct order
- NEVER manually run git commands

**Result:** 0 merge commits since fix (100% improvement)

---

### 2. Manual Git Fallback Under Stress

**Impact:** HIGH
- 67% of merge conflicts caused by manual git usage
- Agents reverted to `git add/commit/push` when scripts showed errors

**Pattern:**
```bash
# Agent tries:
./scripts/ai_commit.sh "feat: add feature"
# Error: "staged files found, commit first"
# Agent doesn't understand → uses manual git
git add .
git commit -m "feat: add feature"
git push
# → Creates conflict (no pull-first)
```

**The Problem:**
> Script errors with unclear messages cause agents to bypass automation.

**Prevention:**
```bash
# Agent 8 ONLY uses this command:
./scripts/ai_commit.sh "message"

# NEVER uses:
git add .            # ❌ FORBIDDEN
git commit           # ❌ FORBIDDEN
git pull             # ❌ FORBIDDEN (unless recovering)
git push             # ❌ FORBIDDEN
```

**If Script Fails:**
1. Run `./scripts/recover_git_state.sh`
2. Fix the issue
3. Try `ai_commit.sh` again
4. NEVER fall back to manual git

---

### 3. Terminal Stuck in Git Pager

**Impact:** HIGH
- Terminal enters alternate buffer mode
- Agent cannot send keystrokes to quit (`q`)
- All subsequent commands blocked
- Requires manual intervention

**Pattern:**
```bash
# ❌ WRONG - Triggers pager on long output
git status              # If > 24 lines, opens less
git log                 # Almost always opens less
git diff                # Opens less for file changes
```

**Prevention (Applied Automatically):**
```bash
# At session start, pager is disabled:
git config --global core.pager cat
git config --global pager.status false

# Or use --no-pager flag:
git --no-pager status
git --no-pager log --oneline -n 10
```

**Safe Alternatives:**
```bash
# Instead of:          Use:
git status          →  git status --short
git log             →  git log --oneline -n 10
git diff            →  git diff --stat
git branch -a       →  git --no-pager branch -a
```

**Recovery:**
1. User must press `q` in terminal
2. Or press `Ctrl+C` to force quit
3. Then apply pager prevention

---

### 4. CI Scope Mismatch

**Impact:** MEDIUM
- 25% of PRs had CI failures even though local checks passed
- Local: `ruff check structural_lib/`
- CI: `ruff check .` (includes examples/)

**Prevention:**
```bash
# Run EXACT CI commands locally:
cd Python
python -m black . --check     # Not structural_lib/, but .
python -m ruff check .        # Not structural_lib/, but .
python -m pytest tests/ -x    # CI runs all tests
cd ..
```

**Pre-commit hooks now match CI exactly.**

---

### 5. Streamlit Code Without Validation

**Impact:** MEDIUM
- Runtime crashes discovered in production
- 39 runtime bugs detected (2026-01-04)

**Pattern:**
```python
# ❌ Committed without validation
st.metric("Result", f"{result / total:.2f}")
# Runtime: ZeroDivisionError when total = 0
```

**Prevention:**
```bash
# Scanner runs automatically in pre-commit:
./scripts/ai_commit.sh "feat: add calculation"
# Scanner runs → detects unsafe division
# CRITICAL: ZeroDivisionError risk at line 42
# → Fix required before commit proceeds
```

**Never bypass:**
```bash
git commit --no-verify  # ❌ NEVER - skips all safety
```

**Result:** 0 new runtime bugs since scanner (2026-01-09)

---

### 6. Skipping Pre-Commit Hooks

**Impact:** MEDIUM
- Agents used `--no-verify` under time pressure
- CI failed 5 minutes later
- Wasted MORE time

**Prevention:**
- `ai_commit.sh` never uses `--no-verify`
- Hook failures trigger auto-fix, not bypass
- If hooks fail, fix the issue locally

---

## 🛡️ Prevention Checklist

### Before Every Session
- [ ] Run `./scripts/agent_start.sh --quick`
- [ ] Verify git state is clean
- [ ] Check for unfinished merges

### Before Every Commit
- [ ] Use ONLY `./scripts/ai_commit.sh "message"`
- [ ] Let pre-commit hooks run completely
- [ ] If hooks modify files, script handles it

### If Something Goes Wrong
- [ ] Run `./scripts/recover_git_state.sh`
- [ ] Check for unfinished merges: `./scripts/check_unfinished_merge.sh`
- [ ] NEVER fall back to manual git

### For Streamlit Code
- [ ] Let scanner run (automatic in pre-commit)
- [ ] Fix CRITICAL issues before committing
- [ ] HIGH issues are warnings only

---

## 🔧 Emergency Recovery Commands

| Situation | Command |
|-----------|---------|
| Git broken | `./scripts/recover_git_state.sh` |
| Unfinished merge | `git commit --no-edit && git push` |
| Merge conflict | `git checkout --ours <file> && git add <file> && git commit --no-edit` |
| Diverged branches | `git pull --ff-only` (if fails, see recover script) |
| Terminal stuck | User presses `q` or `Ctrl+C` |
| CI fails on format | `cd Python && python -m black . && cd .. && ./scripts/ai_commit.sh "style: format"` |

---

## 📊 Success Metrics (After Fixes)

| Metric | Before | After |
|--------|--------|-------|
| Merge commits per day | 17 | 0 |
| Conflicts from manual git | 67% | 0% |
| CI failures from scope mismatch | 25% | 0% |
| Streamlit runtime bugs | 39 | 0 new |
| Terminal stuck incidents | 100% | 0% |

---

## 🔗 Related Documentation

- [Workflow Guide](workflow-guide.md) - Core workflow and scripts
- [Automation Scripts](automation-scripts.md) - Script reference
- [Advanced Coordination](advanced-coordination.md) - Multi-agent patterns

---

**Remember:** Every mistake in this document cost real development time. Use the automation scripts to prevent repeating history.
