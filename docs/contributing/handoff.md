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
4. If releasing: `./scripts/ci_local.sh` then `.venv/bin/python scripts/release.py verify --version X.Y.Z --source pypi`

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
- Local wheel (pre-release): `.venv/bin/python scripts/release.py verify --source wheel --wheel-dir Python/dist`
- PyPI (post-release): `.venv/bin/python scripts/release.py verify --version X.Y.Z --source pypi`

## Handoff (ending)

> **📋 Full workflow:** See [contributing/end-of-session-workflow.md](end-of-session-workflow.md) for comprehensive checklist

**Quick steps (5 minutes):**
1. Run: `.venv/bin/python scripts/session.py end --fix`
2. Update `docs/planning/next-session-brief.md` with summary + blockers.
3. Update `docs/TASKS.md` (move items to Done/Active).
4. Document issues in `docs/contributing/session-issues.md` (if encountered).
5. Ensure clean tree: `git status -sb`

## Debug Snapshot Checklist

When encountering persistent errors, collect this information for handoff:

1. **Collect diagnostics bundle:**
   ```bash
   .venv/bin/python scripts/collect_diagnostics.py > diagnostics.txt
   ```

2. **Enable debug mode** (Streamlit):
   ```bash
   DEBUG=1 streamlit run streamlit_app/app.py
   ```

3. **Check log files:**
   - `logs/git_workflow.log` (git operations)
   - `logs/ci_monitor.log` (CI status)

4. **Run validators:**
   ```bash
   .venv/bin/python scripts/generate_api_manifest.py --check
   .venv/bin/python scripts/check_scripts_index.py
   .venv/bin/python scripts/check_links.py
   ```

5. **Include in handoff:**
   - Diagnostics output
   - Relevant log excerpts
   - Error screenshots/messages
   - Steps to reproduce

## Common Traps (fast fixes)
- CI watch times out: re-run `gh pr checks <num> --watch`.
- PR behind base: `gh pr update-branch <num>` then re-check CI.
- PyPI verification: always use a clean venv.
