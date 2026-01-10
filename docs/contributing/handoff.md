# Handoff Quick Start

Goal: enable the next agent to resume in under 2 minutes.

---

## Resume (next agent)
1. Run: `.venv/bin/python scripts/start_session.py`
2. Read:
   - `docs/planning/next-session-brief.md` (what changed + blockers)
   - `docs/TASKS.md` (active + up next)
   - `.github/copilot-instructions.md` (CRITICAL - git workflow, layers, rules)
3. Review recent work:
   - **Jan 6 2026**: TASK-143 (comparison), TASK-144 (SmartDesigner), workflow automation
   - Smart insights ecosystem now complete: dashboard, comparison, cost optimization, suggestions
   - New workflow tools: `create_task_pr.sh`, `finish_task_pr.sh`, `test_git_workflow.sh`
4. If releasing: `./scripts/ci_local.sh` then `.venv/bin/python scripts/verify_release.py --version X.Y.Z --source pypi`

### Quick output sample (start_session --quick)
```
$ .venv/bin/python scripts/start_session.py --quick
============================================================
🚀 SESSION START
============================================================
  Version:  v0.11.0
  Branch:   main
  Date:     2025-01-02
  Git:      Clean working tree

📝 Session Log:
  ✅ Entry exists for 2025-01-02

📋 Active Tasks:
  • S-007: External engineer CLI test (BLOCKER - requires human)

📖 Read first: docs/handoff.md → docs/agent-bootstrap.md → docs/ai-context-pack.md
============================================================
```

### Release verify (clean venv)
- Local wheel (pre-release): `.venv/bin/python scripts/verify_release.py --source wheel --wheel-dir Python/dist`
- PyPI (post-release): `.venv/bin/python scripts/verify_release.py --version X.Y.Z --source pypi`

## Handoff (ending)

> **📋 Full workflow:** See [contributing/end-of-session-workflow.md](end-of-session-workflow.md) for comprehensive checklist

**Quick steps (5 minutes):**
1. Run: `.venv/bin/python scripts/end_session.py --fix`
2. Update `docs/planning/next-session-brief.md` with summary + blockers.
3. Update `docs/TASKS.md` (move items to Done/Active).
4. Document issues in `docs/contributing/session-issues.md` (if encountered).
5. Ensure clean tree: `git status -sb`

## Common Traps (fast fixes)
- CI watch times out: re-run `gh pr checks <num> --watch`.
- PR behind base: `gh pr update-branch <num>` then re-check CI.
- PyPI verification: always use a clean venv.
