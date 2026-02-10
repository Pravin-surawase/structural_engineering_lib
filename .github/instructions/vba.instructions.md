---
applyTo: "**/VBA/**,**/Excel/**"
---

# VBA / Excel Rules

- Python + VBA parity: same formulas, units, edge-case behavior
- Mac safety: wrap dimension multiplications in `CDbl()` to prevent overflow
- VBA import order matters: see docs/contributing/vba-guide.md
- Always requires PR: `./scripts/create_task_pr.sh TASK-XXX "desc"`
