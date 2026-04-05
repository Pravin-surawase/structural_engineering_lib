---
description: "End-of-session workflow — commit, log, sync, handoff"
---

# Session End Workflow

Complete all end-of-session steps. Do NOT skip any.

## Steps

1. Commit any uncommitted work:
   ```bash
   ./scripts/ai_commit.sh "type: final changes description"
   ```

2. Auto-generate SESSION_LOG entry from git history:
   ```bash
   ./run.sh session summary
   ```
   Direct script: `.venv/bin/python scripts/session.py summary --write`

3. Sync stale doc numbers across reference files:
   ```bash
   ./run.sh session sync
   ```
   Direct script: `.venv/bin/python scripts/sync_numbers.py --fix`

4. Update the handoff document for the next agent:
   - Edit `docs/planning/next-session-brief.md`
   - Add: what was completed, what's next, any blockers

### Step 5: Agent Evolution Check (MANDATORY — not optional)

Run the agent evolution cycle to capture feedback and track quality:

```bash
# Collect session artifacts
.venv/bin/python scripts/agent_session_collector.py

# Quick score for agents active this session
./run.sh evolve --status

# Log any findings
./run.sh feedback log --agent agent-evolver
```

**Report one of:**
- "No issues detected this session"
- "Issues found: [list agent names and what they struggled with]"
- "Recurring pattern detected: [describe pattern — if 3+ occurrences, propose .agent.md update]"

This step feeds the continuous improvement loop. Skipping it means agent mistakes will keep repeating.

6. Update the task board:
   - Edit `docs/TASKS.md`
   - Mark completed items, add any new items discovered

7. Log agent feedback (stale docs, missing info, issues found):
   ```bash
   ./run.sh feedback log --agent <name>
   ```
   Direct script: `.venv/bin/python scripts/agent_feedback.py log --agent <name> --stale-doc "..." --missing-info "..." --issue "..."`

### Step 8: Quality Verification

Before final commit, verify all docs were actually updated:

```bash
# Verify WORKLOG has today's entry
grep "$(date +%Y-%m-%d)" docs/WORKLOG.md || echo "❌ MISSING"

# Verify TASKS was modified
git diff --name-only docs/TASKS.md | head -1 || echo "⚠️ Not modified"

# Verify next-session-brief was modified
git diff --name-only docs/planning/next-session-brief.md | head -1 || echo "❌ MISSING"
```

**If any verification fails, go back and fix it before the final commit.**

9. Commit all doc updates:
   ```bash
   ./scripts/ai_commit.sh "docs: session end"
   ```
