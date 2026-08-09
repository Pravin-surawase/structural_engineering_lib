---
name: innovation-research
description: "Research an explicitly requested innovation as an isolated, source-backed decision memo; do not prototype, change production code, or expand the task without approval."
argument-hint: "Research question or proposed capability"
---

# Innovation Research

This experimental skill is opt-in. Use it only when the user explicitly asks for innovation research or evaluation. Do not invoke it during maintenance, review, or delivery of an already-scoped feature.

## Research Contract

Define the decision to support, intended user, current main-process gap, constraints, timebox, and non-goals. Research should answer whether a separate implementation is justified, not create one by momentum.

## 1. Establish Current Capability

Use targeted indexes and searches:

```bash
./run.sh parity
rg -n "<capability>" Python/structural_lib fastapi_app react_app/src docs/TASKS.md
./run.sh find --api <candidate_function>
```

Do not infer a gap from an old backlog label or hardcoded feature list.

## 2. Gather Primary Evidence

Use current primary sources: governing standards available to the user, original research papers, official product/API documentation, and source repositories. Record publication/version dates, assumptions, licensing/data constraints, and what each source actually supports.

For structural engineering claims, distinguish exploratory evidence from code-compliance interpretation and qualified professional judgment.

## 3. Compare Bounded Options

For each viable option state:

- user outcome and integration point;
- data and dependency requirements;
- effect on Core, IS 456, Services, API, and UI boundaries;
- validation and benchmark availability;
- engineering, product, and maintenance risks;
- smallest useful vertical slice;
- explicit reasons to reject or defer it.

Prefer a simpler option only when it produces the requested outcome with credible validation.

## 4. Produce a Decision Memo

Return:

1. decision and confidence;
2. current-state evidence;
3. sources and their limitations;
4. recommended bounded slice and non-goals;
5. validation/qualified-review plan;
6. estimated affected paths and dependencies;
7. unanswered owner decisions.

Research stops at the memo. Do not create prototype files, endpoints, tasks, or handoff changes unless the user explicitly approves the next phase.

## Approved Prototype Phase

If the user separately approves a prototype, isolate it from production exports, define a disposal/promotion decision, and verify only the research hypothesis. Production integration requires a new implementation plan and the relevant architecture/IS 456 skills.
