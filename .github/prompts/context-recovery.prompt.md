---
description: "Recover context after LLM loses track — read priorities, recent changes, resume work"
---

# Context Recovery

Use this when starting a new chat after context overflow or session interruption.

## Step 1: Read What You Were Working On

```bash
cat docs/planning/next-session-brief.md
```

## Step 2: Check Active Tasks

```bash
head -60 docs/TASKS.md
```

## Step 3: See Recent Changes

```bash
git --no-pager log --oneline -20
```

## Step 4: Check for Uncommitted Work

```bash
git diff --stat
git status --short
```

## Step 5: Resume

Based on the above:
- If there's uncommitted work → review it, continue or commit
- If next-session-brief says something is in-progress → pick it up
- If everything is committed → start the next task from TASKS.md
