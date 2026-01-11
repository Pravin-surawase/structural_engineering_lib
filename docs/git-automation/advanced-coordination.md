# Git Automation: Multi-Agent Coordination

**Type:** Guide
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Version:** 0.16.5
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** Documentation consolidation

---

## Overview

The git automation system supports **concurrent multi-agent operations** through automatic worktree detection and branch-aware behavior.

---

## 🏗️ Architecture

```
Main Workspace (main branch)
├─ Main Agent → ai_commit.sh → safe_push.sh → Push to remote
│
└─ Worktrees (feature branches)
   ├─ worktree-AGENT_5/ → Agent 5 → Local commits only
   ├─ worktree-AGENT_6/ → Agent 6 → Local commits only
   └─ worktree-AGENT_N/ → Agent N → Local commits only
```

**Key Principle:** Main agent pushes to remote. Background agents commit locally and submit via PR when ready.

---

## 🔄 Behavior Differences

| Aspect | Main Agent (main branch) | Background Agent (worktree) |
|--------|--------------------------|------------------------------|
| **Branch** | `main` | `worktree-AGENT_N-timestamp` |
| **Sync** | Pull from origin/main | Merge from origin/main |
| **Push** | ✅ Pushes to remote | ❌ Local commits only |
| **Display** | "Main agent workflow" | "Background agent workflow (🌿 Worktree)" |

---

## 📋 Usage Patterns

### Pattern 1: Main Agent (Standard)

Works on main branch, pushes directly:

```bash
# On main branch
./scripts/ai_commit.sh "feat: add new feature"

# Output:
# === Safe Push Workflow (Conflict-Minimized) ===
# 📍 Branch: main
#    (Main agent workflow - commits and pushes)
#
# ✅ Successfully pushed!
```

### Pattern 2: Background Agent (Worktree)

Works on feature branch, commits locally:

```bash
# Step 1: Create worktree
./scripts/worktree_manager.sh create AGENT_5

# Step 2: Work in worktree
cd worktree-AGENT_5-*

# Step 3: Commit (local only)
../scripts/ai_commit.sh "feat: research complete"

# Output:
# === Safe Push Workflow (Conflict-Minimized) ===
# 🌿 Worktree Mode: AGENT_5
# 📍 Branch: worktree-AGENT_5-2026-01-09-12-30-45
#    (Background agent workflow - commits locally)
#
# ✅ Committed locally (not pushed)
```

### Pattern 3: Submit Background Work

When background agent work is ready:

```bash
# Return to main workspace
cd $PROJECT_ROOT

# Submit via PR
./scripts/worktree_manager.sh submit AGENT_5 "Research complete"

# This creates PR for review and merge
```

---

## 🛡️ Safety Guarantees

### 1. No Conflicting Pushes
- **Main agent** pushes to `origin/main`
- **Background agents** commit locally to feature branches
- No two agents push to the same branch simultaneously

### 2. Branch Isolation
- Each worktree has its own branch: `worktree-AGENT_N-timestamp`
- Branches are independent and don't interfere
- Main workspace stays clean on `main` branch

### 3. Automatic Detection
The system automatically detects if it's running in a worktree:

```bash
# Detection logic (in safe_push.sh)
if [[ "$GIT_COMMON_DIR" != "$GIT_DIR" ]]; then
  IS_WORKTREE="true"
  # Extracts agent name from .agent_marker or branch name
fi
```

---

## 📋 Worktree Manager Commands

```bash
# Create worktree for background agent
./scripts/worktree_manager.sh create AGENT_5

# Submit completed work via PR
./scripts/worktree_manager.sh submit AGENT_5 "Work description"

# List all worktrees
./scripts/worktree_manager.sh list

# Cleanup after merge
./scripts/worktree_manager.sh cleanup AGENT_5
```

---

## 🔧 Configuration

### Worktree Naming Convention

Standard format: `worktree-{AGENT_NAME}-{TIMESTAMP}`

Examples:
- `worktree-AGENT_5-2026-01-09-12-30-45`
- `worktree-EDUCATOR-2026-01-09-14-15-30`
- `worktree-RESEARCHER-2026-01-09-16-45-20`

### Agent Marker File

`.agent_marker` (created automatically by `worktree_manager.sh create`):
```
AGENT_5
Created: 2026-01-09 12:30:45
Branch: worktree-AGENT_5-2026-01-09-12-30-45
```

---

## 🧩 Example: Multiple Concurrent Agents

### Scenario: 3 Agents Working in Parallel

**Main Agent (You):** Documentation on main
```bash
./scripts/ai_commit.sh "docs: update guide"
# ✅ Committed and pushed to origin/main
```

**Agent 5:** UI work in worktree
```bash
cd worktree-AGENT_5/
../scripts/ai_commit.sh "feat(ui): dark mode"
# ✅ Committed locally to worktree branch
```

**Agent 6:** Testing in worktree
```bash
cd worktree-AGENT_6/
../scripts/ai_commit.sh "test: add benchmarks"
# ✅ Committed locally to worktree branch
```

**Result:** ✅ All 3 agents working safely in parallel, no conflicts

---

## 🐛 Troubleshooting

### Issue: "Not sure if worktree"

**Cause:** `.agent_marker` file missing

**Fix:**
```bash
cd worktree-AGENT_N/
echo "AGENT_N" > .agent_marker
echo "Created: $(date)" >> .agent_marker
```

### Issue: "Branch name not recognized"

**Cause:** Non-standard branch name

**Fix:** Use standard format:
```bash
git checkout -b worktree-AGENT_5-$(date +%Y-%m-%d-%H-%M-%S)
```

### Issue: "Trying to push from worktree"

**Expected behavior:** Push is automatically skipped in worktree mode. No action needed.

---

## 📚 Best Practices

1. **Main agent** handles all PR creation and merging
2. **Background agents** commit locally, notify when ready
3. Use `worktree_manager.sh` for all worktree operations
4. Keep worktrees short-lived (hours, not days)
5. Clean up worktrees after merging

---

## 🔗 Related Documentation

- [Workflow Guide](workflow-guide.md) - Core workflow and decision trees
- [Automation Scripts](automation-scripts.md) - Script reference
- [Mistakes Prevention](mistakes-prevention.md) - Historical lessons learned

---

**Summary:** The git automation system seamlessly handles both main agent (push workflow) and background agents (local commit workflow) through automatic worktree detection. No configuration needed - it just works!
