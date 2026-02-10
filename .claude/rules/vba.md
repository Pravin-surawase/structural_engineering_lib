---
description: Rules for editing VBA/Excel files
globs: VBA/**,Excel/**
---

# VBA / Excel Rules

## Python + VBA parity

Same formulas, same units, same edge-case behavior between Python and VBA implementations.
When changing a formula in one, update the other.

## Mac safety

Wrap dimension multiplications in `CDbl()` to prevent overflow on Mac VBA.

## Import order matters

VBA modules must be imported in the correct order. See docs/contributing/vba-guide.md.

## Always requires PR

VBA/Excel changes NEVER go as direct commits:
```bash
./scripts/create_task_pr.sh TASK-XXX "description"
```
