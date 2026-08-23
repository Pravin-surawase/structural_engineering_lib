---
description: "Compact task workflow — root cause, essential review, proportional verification, safe commit"
---

# Master Workflow — Compact Quality Loop

The active parent normally owns this loop end to end. Agent names describe
expertise, not mandatory handoffs.

## The Pipeline

```
Step 1: SCOPE      → main-process outcome, non-goals, exact files
Step 2: TRACE      → inspect the existing process and confirm the root cause
Step 3: EXECUTE    → make the smallest complete correction
Step 4: VERIFY     → narrow checks plus essential-only review
Step 5: RECORD     → update only task-owned state and handoff records
Step 6: CLOSEOUT   → quick gate once, then Codex-managed Git/GitHub work
```

## Step 1: Scope

- Start once with `./run.sh session begin --task-id <task> --agent <role>`
- Identify which files will be changed
- Delegate only independent bounded work that materially benefits from it
- For any delegation, provide objective, non-goals, exact files, pitfalls,
  acceptance, narrow commands, and return format

**Good handoff:**
> Task: Add `xu_max` limit check to flexure.py. Read `codes/is456/flexure.py` lines 80-120 first.
> Return the files changed, root cause corrected, and narrow verification result.

**Bad handoff:**
> Fix the beam calculation thing.

## Steps 2-3: Trace and Execute

Before coding:
1. Read the files you'll modify
2. Check for existing code (hooks, routes, functions)
3. Understand current behavior

After coding, retain this compact implementation record:
```
Files Changed: [list]
What Changed: [summary]
How to Test: [steps]
```

## Step 4: Verify

Run existing checks based on what changed:
- Python: `pytest`, architecture boundaries, import validation
- React: `npm run build`, hook duplication check
- FastAPI: route duplication, Pydantic model validation
- IS 456: formula verification, clause references

For each review finding ask whether fixing it changes the main-process outcome.
Ignore comments, edge cases, test-coverage gaps, generic hardening, and adjacent
improvements. Do not add tests during review.

## Step 5: Record State

- Update TASKS only when task state changed.
- Update the brief only for a durable continuation or ownership handoff.
- Do not create global log churn or a second docs commit by default.

## Step 6: Closeout

```bash
./run.sh check --quick
# Codex reviews, stages intended paths, commits, pushes, and creates/updates the PR.
```

Reports: commit hash, branch, PR status, pipeline complete.

## Feedback Loop (Continuous Improvement)

Feed concrete repeated failures back into the system on the governance cadence.

### On Concrete Evidence
The orchestrator asks:
1. **Did the same failure recur with evidence?** → Correct the shared root instruction or automation
2. **Would the change alter future main-process outcomes?** → If not, do not encode new policy
3. **Did duplication cause a repeated wrong outcome?** → Correct its canonical source
4. **Did Git workflow fail repeatedly?** → Preserve the proven recovery rule
5. **Did ambiguous handoffs recur?** → Improve the canonical delegation template

### Feedback Data Flow

```
@specialist reports → @reviewer catches → @orchestrator logs
       ↓                    ↓                    ↓
  Work quality          Issue patterns       Agent updates
       ↓                    ↓                    ↓
  Updated agent.md     New checklist items   Governance log
```

### Escalation Rules
- One occurrence → fix the scoped root cause; do not create permanent policy
- Three or more evidenced occurrences → propose one canonical instruction change
- Persistent failure after instruction repair → consider focused automation

## Quick Reference

| Step | Agent | Key Output |
|------|-------|------------|
| 1. Scope | Active parent | Outcome, non-goals, file list |
| 2. Trace | Active parent or bounded specialist | Existing path and root cause |
| 3. Execute | Active parent or bounded specialist | Complete scoped change |
| 4. Verify | Active parent or independent reviewer when justified | Essential outcome verdict |
| 5. Record | Active parent | Only changed task/handoff state |
| 6. Commit | Active parent or ops when justified | Commit hash + branch + PR status |
