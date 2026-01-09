# Agent 8 Multi-Agent Coordination

**Version:** 1.0.0
**Last Updated:** 2026-01-09
**Status:** Active

---

## Overview

Agent 8 workflow (`ai_commit.sh` + `safe_push.sh`) now supports **concurrent multi-agent operations** with automatic worktree detection and branch-aware behavior.

### Architecture

```
Main Workspace (main branch)
├─ Main Agent → ai_commit.sh → safe_push.sh → Push to remote
│
└─ Worktrees (feature branches)
   ├─ worktree-AGENT_5/ → Agent 5 → ai_commit.sh → safe_push.sh → Local commits only
   ├─ worktree-AGENT_6/ → Agent 6 → ai_commit.sh → safe_push.sh → Local commits only
   └─ worktree-AGENT_N/ → Agent N → ai_commit.sh → safe_push.sh → Local commits only
```

---

## How It Works

### Automatic Detection

`safe_push.sh` automatically detects if it's running in:
1. **Main workspace** (on `main` branch) → Full push workflow
2. **Worktree** (feature branch) → Local commit workflow

Detection method:
```bash
# Checks git-common-dir vs git-dir
if [[ "$GIT_COMMON_DIR" != "$GIT_DIR" ]]; then
  IS_WORKTREE="true"
  # Extracts agent name from .agent_marker or branch name
fi
```

### Behavior Differences

| Aspect | Main Agent (main branch) | Background Agent (worktree) |
|--------|--------------------------|------------------------------|
| **Branch** | `main` | `worktree-AGENT_N-timestamp` |
| **Sync** | Pull from origin/main | Merge from origin/main |
| **Push** | ✅ Pushes to remote | ❌ Local commits only |
| **Display** | "Main agent workflow" | "Background agent workflow (🌿 Worktree)" |
| **Logging** | Standard workflow log | Includes worktree + agent info |

---

## Usage Patterns

### Main Agent (You)

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

### Background Agent (Worktree)

Works on feature branch, local commits:

```bash
# In worktree (e.g., worktree-AGENT_5/)
../scripts/ai_commit.sh "feat: research complete"

# Output:
# === Safe Push Workflow (Conflict-Minimized) ===
# 🌿 Worktree Mode: AGENT_5
# 📍 Branch: worktree-AGENT_5-2026-01-09-12-30-45
#    (Background agent workflow - commits locally)
#
# ✅ Committed locally (not pushed)
```

---

## Safety Guarantees

### 1. No Conflicting Pushes

- **Main agent** pushes to `origin/main`
- **Background agents** commit locally to feature branches
- No two agents push to the same branch simultaneously

### 2. Branch Isolation

- Each worktree has its own branch: `worktree-AGENT_N-timestamp`
- Branches are independent and don't interfere
- Main workspace stays clean on `main` branch

### 3. Merge Coordination

When background agent work is ready:

```bash
# Main agent reviews and merges
cd $PROJECT_ROOT
./scripts/worktree_manager.sh submit AGENT_5 "Research complete"

# This creates PR for review and merge
```

---

## Workflow Examples

### Scenario 1: Main Agent + 1 Background Agent

**Main Agent (You):**
```bash
# Working on main
git checkout main
./scripts/ai_commit.sh "docs: update README"
# ✅ Committed and pushed to origin/main
```

**Background Agent 5 (Parallel):**
```bash
# Working in worktree
cd worktree-AGENT_5-2026-01-09
../scripts/ai_commit.sh "research: API patterns"
# ✅ Committed locally to worktree-AGENT_5-2026-01-09
```

**Result:** ✅ No conflicts, both working independently

---

### Scenario 2: Multiple Background Agents

**Agent 5:** UI work in `worktree-AGENT_5/`
```bash
cd worktree-AGENT_5/
../scripts/ai_commit.sh "feat(ui): dark mode"
```

**Agent 6:** Testing in `worktree-AGENT_6/`
```bash
cd worktree-AGENT_6/
../scripts/ai_commit.sh "test: add benchmarks"
```

**Main Agent:** Docs on main
```bash
./scripts/ai_commit.sh "docs: update guide"
```

**Result:** ✅ All 3 agents working safely in parallel

---

## Integration with Week 1 Optimizations

When Week 1 optimizations are implemented:

### Parallel Fetch (Optimization #1)

- **Main agent:** Fetches from `origin/main`, merges/pushes
- **Worktree agents:** Fetches from `origin/main`, merges locally

### CI Monitor Daemon (Optimization #3)

- Monitors PRs from worktree branches
- Main agent creates PRs via `worktree_manager.sh submit`
- Daemon auto-merges when CI passes
- Zero blocking for background agents

### Merge Conflict Tests (Optimization #4)

- Tests cover both main and worktree scenarios
- Validates worktree → main merge patterns
- Ensures no cross-agent conflicts

---

## Troubleshooting

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

**Cause:** Background agent shouldn't push

**Fix:** This is actually **prevented automatically** - worktree mode skips push step

---

## Configuration

### Worktree Naming Convention

Standard format: `worktree-{AGENT_NAME}-{TIMESTAMP}`

Examples:
- `worktree-AGENT_5-2026-01-09-12-30-45`
- `worktree-EDUCATOR-2026-01-09-14-15-30`
- `worktree-RESEARCHER-2026-01-09-16-45-20`

### Agent Marker File

`.agent_marker` (created by `worktree_manager.sh create`):
```
AGENT_5
Created: 2026-01-09 12:30:45
Branch: worktree-AGENT_5-2026-01-09-12-30-45
```

---

## Implementation Status

✅ **Complete:**
- Worktree detection in `safe_push.sh`
- Agent name extraction
- Branch-aware messaging
- Logging with agent context

⏳ **Pending (Week 1):**
- Parallel fetch optimization
- CI monitor daemon integration
- Merge conflict test coverage

---

## Testing

### Test Worktree Detection

```bash
# Create test worktree
./scripts/worktree_manager.sh create TEST_AGENT

# Go to worktree
cd worktree-TEST_AGENT-*

# Test commit
echo "test" > test.txt
git add test.txt
../scripts/ai_commit.sh "test: worktree detection"

# Expected output:
# 🌿 Worktree Mode: TEST_AGENT
# 📍 Branch: worktree-TEST_AGENT-...
#    (Background agent workflow - commits locally)
```

### Verify No Push

```bash
# After commit in worktree
git log origin/main..HEAD
# Should show 1 unpushed commit

git push origin HEAD
# Should push successfully (manual confirmation that auto-push was skipped)
```

---

## Best Practices

1. **Main agent** handles all PR creation and merging
2. **Background agents** commit locally, notify when ready
3. Use `worktree_manager.sh` for all worktree operations
4. Keep worktrees short-lived (hours, not days)
5. Clean up worktrees after merging: `./scripts/worktree_manager.sh cleanup AGENT_NAME`

---

## Future Enhancements

### Week 2+ Optimizations
- Smart conflict prediction across worktrees
- Cross-agent file locking
- Dependency graph for agent tasks
- Automated worktree cleanup after merge

### Advanced Features
- Worktree-aware pre-commit hooks
- Agent activity dashboard
- Cross-worktree test running
- Shared cache between worktrees

---

## References

- [Background Agent Guide](../contributing/background-agent-guide.md)
- [Worktree Manager](../../scripts/worktree_manager.sh)
- [Agent 8 Week 1 Handoff](AGENT8-WEEK1-HANDOFF.md)
- [Git Workflow for AI Agents](../git-workflow-ai-agents.md)

---

**Summary:** Agent 8 workflow now seamlessly handles both main agent (push workflow) and background agents (local commit workflow) through automatic worktree detection. No configuration needed - it just works!
