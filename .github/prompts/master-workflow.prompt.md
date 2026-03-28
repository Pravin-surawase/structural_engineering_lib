---
description: "Quality-gated pipeline for all code changes — ensures review, docs, and safe commit"
---

# Master Workflow — Quality-Gated Pipeline

Every code change in this project MUST follow this 6-step pipeline. No exceptions.

## The Pipeline

```
Step 1: @orchestrator  → Plan & scope the work
Step 2: @specialist    → Gather context (read existing code BEFORE changing anything)
Step 3: @specialist    → Execute the change
Step 4: @reviewer      → Verify (architecture, tests, IS 456, git hygiene)
Step 5: @doc-master    → Update WORKLOG, TASKS, next-session-brief
Step 6: @ops           → Commit via ai_commit.sh
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

## Feedback Loop (Continuous Improvement)

Every completed task feeds back into the system. This is how agents get smarter over time.

### After Each Task
The orchestrator reviews:
1. **Did the specialist need extra guidance?** → Update their `.agent.md` with specific instructions
2. **Did the reviewer catch preventable issues?** → Add a rule to the specialist's checklist
3. **Did anything get duplicated?** → Add to "DO NOT recreate" lists in the relevant agent
4. **Did @ops report any git issues?** → Add to Historical Mistakes in ops.agent.md
5. **Was the handoff clear enough?** → Improve the delegation template

### After Each Session
The orchestrator updates:
- `docs/TASKS.md` — mark completed, add discovered items
- `docs/planning/next-session-brief.md` — specific handoff for next agent
- Agent files — incorporate lessons learned during the session

### Feedback Data Flow

```
@specialist reports → @reviewer catches → @orchestrator logs
       ↓                    ↓                    ↓
  Work quality          Issue patterns       Agent updates
       ↓                    ↓                    ↓
  Updated agent.md     New checklist items   Governance log
```

### Escalation Rules
- Same mistake 2x → Add warning to agent file
- Same mistake 3x → Add enforcement check (script or pre-commit hook)
- Same mistake 5x → Redesign the workflow to prevent it structurally

## Quick Reference

| Step | Agent | Key Output |
|------|-------|------------|
| 1. Plan | @orchestrator | Task scope + file list + specialist assignment |
| 2. Gather | @frontend/@backend/@api-developer | Context acquired (existing patterns, functions, hooks) |
| 3. Execute | @frontend/@backend/@api-developer | Code changes + work report |
| 4. Verify | @reviewer | APPROVED / NEEDS CHANGES + specific issues |
| 5. Document | @doc-master | WORKLOG + TASKS updated |
| 6. Commit | @ops | Commit hash + branch + PR status |
