# Background Agent Parallel Work Guide (1-2 agents)

Purpose: enable safe parallel work without conflicts, CI failures, or duplicated effort.

Scope: 1-2 background agents working in parallel with the main agent on isolated tasks.

---

## Quick start (5 minutes)
1. Read `docs/AGENT_BOOTSTRAP.md` and `docs/AI_CONTEXT_PACK.md`.
2. Run: `.venv/bin/python scripts/start_session.py`.
3. Confirm the exact TASK ID and acceptance criteria with the main agent.
4. Read `docs/GIT_WORKFLOW_AI_AGENTS.md` (no manual git).
5. Confirm your file boundary (what you may edit, and what you must avoid).

---

## Task selection (parallel-safe)
Pick tasks with minimal overlap:
- Research docs in `docs/research/`
- Single-module changes with clear boundaries
- Tests that only touch one subsystem

Avoid:
- `docs/TASKS.md`, `docs/SESSION_LOG.md`, `docs/planning/next-session-brief.md` unless explicitly assigned
- Multi-module refactors that overlap other active work
- Edits to `Python/structural_lib/api.py` if another agent is already touching API surfaces

If unsure, ask the main agent before starting.

---

## Branching and isolation
Follow the workflow scripts only:

### Code/CI/deps changes (PR required)
```bash
./scripts/create_task_pr.sh TASK-XXX "short description"
# make changes
./scripts/ai_commit.sh "feat: describe change"
./scripts/finish_task_pr.sh TASK-XXX "short description"
```

### Docs/research-only changes
Use direct commits if allowed by the main agent, otherwise use a PR branch.
```bash
./scripts/ai_commit.sh "docs: add research notes"
```

Never run manual `git commit` or `git push`.

---

## Quality guardrails (avoid CI failures)
Before committing:
- Run Black and Ruff locally if you changed Python files:
  - `.venv/bin/python -m black Python/`
  - `.venv/bin/python -m ruff check --fix Python/`
- If you change API return types or dataclasses, update all call sites (CLI, tests).
- Let `./scripts/ai_commit.sh` run pre-commit hooks and fix any reported issues.

Common failure modes we saw:
- Formatting drift (Black/Ruff) after merging or rebasing.
- Mypy errors from updated result objects not propagated to CLI/tests.
- Unsorted imports or leftover `pass` statements in exception classes.

If CI fails, fix locally and re-run `./scripts/ai_commit.sh`.

---

## Communication + handoff
When done, send a handoff to the main agent (or include in PR description):

```markdown
## Handoff: BACKGROUND → MAIN
**Task:** TASK-XXX
**Summary:** 2-3 sentences on what changed and why.
**Files touched:** list paths
**Decisions:** key choices + rationale
**Open questions:** any unresolved items
**Action required:** next step for main agent
```

Only update `docs/HANDOFF.md` or session docs if explicitly requested.

---

## Parallel coordination rules (strict)
- One task per background agent (WIP=1).
- Do not edit shared high-churn files unless assigned.
- Do not merge your PR unless the main agent asks you to.
- Keep commits scoped and reversible.

If conflicts appear, stop and ask the main agent how to proceed.
