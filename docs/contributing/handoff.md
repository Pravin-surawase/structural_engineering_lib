# Handoff Quick Start

Goal: enable the next agent to resume in under 2 minutes.

---

## Resume (next agent)
1. Run: `./scripts/agent_start.sh --quick` (or with `--agent 9` for governance work)
2. Read:
   - `docs/planning/next-session-brief.md` (what changed + blockers)
   - `docs/TASKS.md` (active + up next)
   - `.github/copilot-instructions.md` (CRITICAL - git workflow, layers, rules)
3. Review recent work:
   - **Jan 11 2026**: Session 13 - Folder Governance + Agent Onboarding
   - Created unified `agent_start.sh` (replaces 4 commands with 1)
   - Archived 4 redundant docs, consolidated agent-automation-system.md v1.1.0
4. If releasing: `./scripts/ci_local.sh` then `.venv/bin/python scripts/verify_release.py --version X.Y.Z --source pypi`

### Quick output sample (agent_start.sh --quick)
```
$ ./scripts/agent_start.sh --quick
============================================================
🚀 AGENT SESSION START
============================================================
  Version:  v0.16.0
  Branch:   main
  Date:     2026-01-11
  Git:      Clean working tree

📋 Active Tasks:
  • v0.17.0 implementation (TASK-272, 273, 274, 275)

📖 Read first: docs/handoff.md → docs/TASKS.md
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
