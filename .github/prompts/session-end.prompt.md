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

5. Update the task board:
   - Edit `docs/TASKS.md`
   - Mark completed items, add any new items discovered

6. Commit all doc updates:
   ```bash
   ./scripts/ai_commit.sh "docs: session end"
   ```
