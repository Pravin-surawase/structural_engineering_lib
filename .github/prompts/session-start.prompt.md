---
description: "Session start workflow — read priorities, check environment, plan work"
---

# Session Start Workflow

## 1. Read Priorities

Check what the previous session left for you:
```bash
cat docs/planning/next-session-brief.md
```

## 2. Check Active Tasks

```bash
cat docs/TASKS.md | head -60
```

Look for items marked "In Progress" or "Priority: P0/P1".

## 3. Verify Environment

```bash
./run.sh session start
```

This checks:
- Python venv is active
- Dependencies installed
- Git state is clean
- No stale locks

## 4. Orient Yourself

```bash
# Recent changes
git --no-pager log --oneline -10

# Current branch
git branch --show-current

# Any uncommitted work?
git status --short
```

## 5. Plan Your Session

Based on priorities from step 1-2:
- Pick 1-3 tasks to focus on
- Note any blockers or dependencies
- If a task spans multiple agents, start with @orchestrator

## Quick Start

If you just want to jump into coding:
```bash
./run.sh session start && cat docs/planning/next-session-brief.md | head -30
```
