# Background Agent Parallel Work Research (2026-01-07)

## Purpose
Document the current state, known pitfalls, and concrete guardrails for running
1-2 background agents in parallel with the MAIN agent. This consolidates
existing research and recent workflow incidents into a single, actionable guide.

## Sources Reviewed
- `docs/research/documentation-handoff-analysis.md`
- `docs/research/git-workflow-production-stage.md`
- `docs/research/git-workflow-recurring-issues.md`
- `docs/contributing/agent-collaboration-framework.md`
- `docs/contributing/github-workflow.md`
- `docs/contributing/git-workflow-quick-reference.md`
- `docs/contributing/end-of-session-workflow.md`
- `docs/contributing/repo-professionalism.md`
- `docs/_internal/AGENT_WORKFLOW.md`
- `docs/contributing/session-issues.md`

## Summary of Existing Research
- The git workflow is strong but depends on strict script usage (`safe_push.sh`,
  `ai_commit.sh`, `should_use_pr.sh`). Manual git commands cause regressions.
- Handoff quality is a major lever for multi-agent speed. Automated handoffs
  (end_session/update_handoff) prevent drift.
- Documentation and role guidance are extensive, but parallel execution requires
  clear file boundaries and WIP enforcement.
- Workflow friction is typically enforcement, not missing tools.

## Observed Issues (Recent Parallel Work)
- Formatting and lint drift after merges caused CI failures (Black/Ruff).
- Type changes to result objects were not propagated to CLI/tests, causing mypy
  failures.
- High-churn files (TASKS/session docs) generated conflicts during parallel
  merges.
- CI checks were sometimes delayed or reported late; merging before checks
  completed caused extra cycles.

## Pitfalls and Mitigations
1. Manual git push
   - Risk: bypasses `safe_push.sh` sync and checks.
   - Fix: only use `ai_commit.sh` or PR scripts.
2. High-churn file edits
   - Risk: merge conflicts and lost updates.
   - Fix: MAIN-only ownership for TASKS, session logs, brief.
3. Uncoordinated API changes
   - Risk: tests/CLI out of sync, mypy failures.
   - Fix: update all call sites in the same branch; run mypy locally.
4. Skipping format/lint steps
   - Risk: CI failures on Black/Ruff/isort.
   - Fix: run local formatters or rely on pre-commit and fix before push.
5. Merging before checks finish
   - Risk: failed required checks on main.
   - Fix: wait for `gh pr checks --watch` to complete.

## Recommended Guardrails (Concrete)
- Use `./scripts/should_use_pr.sh --explain` before work begins.
- Enforce file boundaries (no edits to TASKS/session docs unless assigned).
- Require WIP=1 per background agent; allow WIP=3 only with MAIN approval.
- Always run `start_session.py` at session start.
- Use the handoff template from `docs/_internal/AGENT_WORKFLOW.md`.
- For Python edits, run:
  - `.venv/bin/python -m black Python/`
  - `.venv/bin/python -m ruff check --fix Python/`
  - `.venv/bin/python -m mypy Python/structural_lib`
  - `.venv/bin/python -m pytest Python/tests/unit/test_your_module.py -v`

## Improvements to System (Proposed)
- Add a short "background agent checklist" to onboarding message.
- Add a lightweight decision checklist for PR vs direct commit (one page).
- Add a CI wait reminder to the PR template or handoff template.
- Maintain a small "pitfalls" list in `docs/reference/known-pitfalls.md`
  specific to parallel agent work.

## Metrics to Track (Optional)
- CI failure rate per background agent task.
- Average time from task assignment to merge.
- Number of merge conflicts per week.
- Rework count due to missing call-site updates.

## Open Questions
- Should WIP=3 be allowed by default, or require explicit approval each time?
- Should background agents be restricted to docs/research-only unless assigned?
