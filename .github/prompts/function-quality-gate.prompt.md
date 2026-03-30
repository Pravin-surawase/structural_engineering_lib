---
description: "Run the full quality pipeline for a new IS 456 function — plan, math review, implement, test, review, API, docs, commit"
mode: "orchestrator"
---

# Function Quality Gate

Run this before adding any new IS 456 function to the library.

## Context

You are adding a new function to `Python/structural_lib/codes/is456/`. This prompt ensures the function goes through the full quality pipeline.

## Steps

1. **Read the quality skill first:**
   Use `/function-quality-pipeline` to understand the 9-step pipeline.

2. **Identify the function:**
   - What IS 456 clause does it implement?
   - What are the input parameters (with units)?
   - What is the return type?
   - What benchmark values exist (SP:16, textbooks)?

3. **Run the pipeline:**
   Follow all 9 steps in order. No step may be skipped.
   Track progress using the pipeline status template.

4. **Delegate to specialists:**
   - @structural-engineer → clause research + math verification
   - @structural-math → implementation (12-point checklist)
   - @tester → comprehensive tests (unit + benchmark + property + degenerate)
   - @reviewer → two-pass review (math + code)
   - @backend → API wiring
   - @api-developer → FastAPI endpoint
   - @doc-master → documentation
   - @ops → safe commit

5. **Quality gates (MUST pass before moving to next step):**
   - Step 3 → Step 4: Function runs without errors
   - Step 4 → Step 5: All tests pass (including benchmarks)
   - Step 5 → Step 6: Both math and code reviews approved
   - Step 9: Full test suite passes, `./run.sh check --quick` passes

## Incremental Complexity Rule

For new structural elements, implement the simplest case first:
- Column: axial only → uniaxial → biaxial → slender
- Footing: square isolated → rectangular → edge/corner
- Slab: one-way → two-way elastic → yield line

Each level must pass all benchmarks before proceeding to the next.

## Error Recovery

If a step fails:
1. Document what failed and why
2. Go back to the previous step
3. Fix the issue
4. Re-run the failed step
5. Continue the pipeline

Never skip a failed step. Never force-merge without all steps passing.
