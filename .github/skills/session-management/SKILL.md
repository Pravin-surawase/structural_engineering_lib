---
name: session-management
description: "Automate AI agent session start and end workflows. Use when beginning a new work session or finishing one. Handles reading priorities, verifying environment, logging changes, updating handoff docs, and committing session artifacts."
---

# Session Management Skill

Automate the mandatory session start and end workflows for the structural_engineering_lib project.

## When to Use

- Starting a new coding session
- Ending a session (MANDATORY — never skip)
- Checking session state mid-work

## Session Start

Run these steps in order:

1. **Read priorities:**
   ```bash
   cat docs/planning/next-session-brief.md | head -50
   ```

2. **Read active tasks:**
   ```bash
   cat docs/TASKS.md | head -80
   ```

3. **Verify environment:**
   ```bash
   ./run.sh session start
   ```

4. **Quick orientation (optional):**
   ```bash
   ./run.sh session context
   ```

5. **Pre-flight check:**
   ```bash
   ./run.sh preflight
   ```

## Session End (REQUIRED — do NOT skip)

Every step must complete. Skipping has caused 10+ hours of wasted rework.

1. **Commit any uncommitted work:**
   ```bash
   ./scripts/ai_commit.sh "type: final changes description"
   ```

2. **Auto-generate SESSION_LOG entry:**
   ```bash
   .venv/bin/python scripts/session.py summary --write
   ```

3. **Sync stale doc numbers:**
   ```bash
   .venv/bin/python scripts/session.py sync --fix
   ```

4. **Update WORKLOG.md** — append one line per change:
   ```markdown
   | YYYY-MM-DD | TASK-XXX | Description of what changed | commit_hash |
   ```

5. **Update next-session-brief.md** — what the NEXT agent should do:
   - What was completed this session
   - What's still in progress
   - Any blockers or decisions needed

6. **Update TASKS.md:**
   - Mark completed items as ✅ Done
   - Add any new items discovered

7. **Commit all doc updates:**
   ```bash
   ./scripts/ai_commit.sh "docs: session end"
   ```

## Session Check (mid-session)

```bash
.venv/bin/python scripts/session.py check
```

Verifies:
- SESSION_LOG.md is not stale
- next-session-brief.md has recent updates
- TASKS.md has no abandoned "in progress" items

## Key Files

| File | Purpose |
|------|---------|
| `docs/SESSION_LOG.md` | Detailed session history (append-only) |
| `docs/WORKLOG.md` | Compact one-line-per-change log (append-only) |
| `docs/planning/next-session-brief.md` | Handoff to next session |
| `docs/TASKS.md` | Active task board |
| `scripts/session.py` | Session management CLI |

## Context Checkpoint (save before context overflow)

When a conversation is getting long, save a checkpoint so a new chat can resume:

```bash
# Ask the agent to write a checkpoint:
# "Save a checkpoint to next-session-brief.md with:
#  1. What we completed this session
#  2. What's currently in progress (with exact file paths and line numbers)
#  3. What's left to do
#  4. Any decisions made or blockers found"
```

The checkpoint goes into `docs/planning/next-session-brief.md`. A new chat can recover by reading it.

## Context Recovery (new chat after overflow)

Paste this into a new Copilot chat to recover:
```
Read these to recover context:
1. docs/planning/next-session-brief.md
2. docs/TASKS.md (first 60 lines)
3. .github/copilot-instructions.md
4. git log --oneline -20
Then continue from where I left off.
```

## Why This Matters

- **SESSION_LOG.md** is the project memory — gaps mean lost context
- **next-session-brief.md** is the handoff — without it, the next agent wastes time rediscovering state
- **WORKLOG.md** is the compact history — one line per change prevents rework
- **TASKS.md** tracks priorities — unupdated tasks get repeated or lost
- Empty sessions (no log, no handoff) have caused 10+ hours of wasted rework historically
