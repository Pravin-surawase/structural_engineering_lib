---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: guide
complexity: intermediate
tags: []
---

# Handoff Quick Start

> Current Git/session boundary: start with `./run.sh session brief --agent
> <role>`, `./run.sh session start`, `scripts/python_runtime.sh --diagnose`, and
> `scripts/git_state.py --json --worktrees`. The state authority is local-only;
> remote freshness remains `NOT_CHECKED` unless separately established.

Every durable task handoff uses a tracked machine-readable receipt built and
validated by `scripts/git_handoff_receipt.py`. It records the
`local_state_receipt_hash`, exact branch/head/upstream/base/worktree/tree/
operation identity, hosted PR/review/check facts or explicit `UNKNOWN`,
retention evidence, authorization, prohibited actions, and next permitted
action. `NOT_APPLICABLE` requires a reason and is never a substitute for
unknown. Task or transcript archive state is not Git retention evidence.

Reference the receipt in the newest session entry as `**Git handoff receipt:**
<tracked-path>`, then run `scripts/session.py handoff --git-receipt
<tracked-path>`. Session end validates schema, hash, exact-head contradictions,
and the round trip; missing or invalid evidence is a hold.

Goal: enable the next agent to resume in under 2 minutes.

---

## Resume (next agent)
1. Run: `./scripts/agent_start.sh --quick` (or with `--agent governance` for governance work)
2. Read:
   - `docs/planning/next-session-brief.md` (what changed + blockers)
   - `docs/TASKS.md` (active + up next)
   - `.github/copilot-instructions.md` (CRITICAL - git workflow, layers, rules)
3. Review recent work:
   - **Jan 11 2026**: Session 13 - Folder Governance + Agent Onboarding
   - Created unified `agent_start.sh` (replaces 4 commands with 1)
   - Archived 4 redundant docs, consolidated agent-automation-system.md v1.1.0
4. Release work remains separately authorized; use the maintained release-preflight workflow when in scope.

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
- Local wheel (pre-release): `./scripts/python_runtime.sh scripts/release.py verify --source wheel --wheel-dir Python/dist`
- PyPI (post-release): `./scripts/python_runtime.sh scripts/release.py verify --version X.Y.Z --source pypi`

## Handoff (ending)

> **📋 Full workflow:** See [contributing/end-of-session-workflow.md](end-of-session-workflow.md) for comprehensive checklist

**Quick steps (5 minutes):**
1. Validate the tracked Git receipt and run `./run.sh session end --agent <role>`.
2. Update `docs/planning/next-session-brief.md` with summary + blockers.
3. Update `docs/TASKS.md` (move items to Done/Active).
4. Document issues in `docs/contributing/session-issues.md` (if encountered).
5. Inspect the exact local tree with `./scripts/python_runtime.sh scripts/git_state.py --json`.

## Debug Snapshot Checklist

When encountering persistent errors, collect this information for handoff:

1. **Collect diagnostics bundle:**
   ```bash
   ./scripts/python_runtime.sh scripts/collect_diagnostics.py > diagnostics.txt
   ```

2. **Enable debug mode** (Streamlit):
   ```bash
   DEBUG=1 streamlit run streamlit_app/app.py
   ```

3. **Check log files:**
   - the versioned task-to-Git receipt (Git identity and holds)
   - `logs/ci_monitor.log` (CI status)

4. **Run validators:**
   ```bash
   ./scripts/python_runtime.sh scripts/generate_api_manifest.py --check
   ./scripts/python_runtime.sh scripts/check_scripts_index.py
   ./scripts/python_runtime.sh scripts/check_links.py
   ```

5. **Include in handoff:**
   - Diagnostics output
   - Relevant log excerpts
   - Error screenshots/messages
   - Steps to reproduce

## Common Traps (fast fixes)
- CI query times out: record `UNKNOWN`/hold and have Codex re-query the exact head.
- PR behind base: inspect exact base/head and let Codex choose a normal, non-rewriting update path.
- PyPI verification: always use a clean venv.
