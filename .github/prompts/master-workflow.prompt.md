---
description: "Quality-gated pipeline for all code changes — ensures review, docs, and safe commit"
---

# Master Workflow — Quality-Gated Pipeline

Every code change in this project MUST follow this 5-step pipeline. No exceptions.

## The Pipeline

```
Step 1: @orchestrator  → Plan & scope the work
Step 2: @specialist    → Execute (frontend/backend/api-developer)
Step 3: @reviewer      → Verify (architecture, tests, IS 456)
Step 4: @doc-master    → Update WORKLOG, TASKS, next-session-brief
Step 5: @ops           → Commit via ai_commit.sh
```

## Step 1: Orchestrator Plans

- Read TASKS.md and next-session-brief.md
- Identify which files will be changed
- Choose the right specialist agent
- Provide a specific handoff with: task description, files to check, expected output

**Good handoff:**
> Task: Add `xu_max` limit check to flexure.py. Read `codes/is456/flexure.py` lines 80-120 first.
> After completing, hand off to @reviewer with files changed and how to test.

**Bad handoff:**
> Fix the beam calculation thing.

## Step 2: Specialist Executes

Before coding:
1. Read the files you'll modify
2. Check for existing code (hooks, routes, functions)
3. Understand current behavior

After coding — report to @reviewer:
```
Files Changed: [list]
What Changed: [summary]
How to Test: [steps]
```

## Step 3: Reviewer Verifies

Runs checks based on what changed:
- Python: `pytest`, architecture boundaries, import validation
- React: `npm run build`, hook duplication check
- FastAPI: route duplication, Pydantic model validation
- IS 456: formula verification, clause references

Reports verdict: **APPROVED** → @doc-master | **NEEDS CHANGES** → back to specialist

## Step 4: Doc-Master Updates

- WORKLOG.md: one line per change
- TASKS.md: mark done, add new items
- next-session-brief.md: if session is ending
- Hand off to @ops

## Step 5: Ops Commits

```bash
./scripts/ai_commit.sh "type(scope): description"
```

Reports: commit hash, branch, PR status, pipeline complete.

## Post-Task Review (Continuous Improvement)

After each completed task, the orchestrator should note:
1. Did the specialist need extra guidance? → Update their agent file
2. Did the reviewer catch something that should have been prevented? → Add a rule
3. Did anything get duplicated? → Add to "DO NOT recreate" lists
4. Was the handoff clear enough? → Improve the template

## Quick Reference

| Step | Agent | Key Output |
|------|-------|------------|
| 1. Plan | @orchestrator | Task scope + file list + specialist assignment |
| 2. Execute | @frontend/@backend/@api-developer | Code changes + work report |
| 3. Verify | @reviewer | APPROVED / NEEDS CHANGES + specific issues |
| 4. Document | @doc-master | WORKLOG + TASKS updated |
| 5. Commit | @ops | Commit hash + branch + PR status |
