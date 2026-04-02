# Governance & Maintenance Playbook

**Type:** Guide
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-04-02
**Last Updated:** 2026-04-02

---

This playbook defines recurring maintenance tasks, quality gates, and governance
limits for the **structural_engineering_lib** project. Every AI agent and human
contributor should follow these procedures to keep the project healthy.

---

## 1. Per-Session Checklist

### Session Start

```bash
# 1. Read priorities
cat docs/planning/next-session-brief.md

# 2. Check task board
head -60 docs/TASKS.md

# 3. Verify environment
./run.sh session start

# 4. Check git state
git status --short
git branch --show-current
```

### Session End (MANDATORY — do NOT skip)

```bash
# 1. Commit any remaining work
./scripts/ai_commit.sh "type(scope): message"

# 2. Log agent feedback
./run.sh feedback log --agent <name>

# 3. Auto-generate session summary
./run.sh session summary

# 4. Sync stale doc numbers
./run.sh session sync

# 5. Check evolution status (burn-in phase)
./run.sh evolve --status

# 6. Update handoff docs
# Edit: docs/planning/next-session-brief.md
# Edit: docs/TASKS.md

# 7. Commit doc updates
./scripts/ai_commit.sh "docs: session end"
```

> **Why this matters:** Skipping session-end steps has historically caused 10+
> hours of wasted rework. SESSION_LOG.md is the project memory;
> next-session-brief.md is the handoff. Without them, the next agent starts
> blind.

---

## 2. Weekly Maintenance (~1 hour)

```bash
# Quick validation (28 checks, <30s)
./run.sh check --quick

# Project health score (0-100)
./run.sh health

# Archive completed tasks (when >20 done items)
# Move from TASKS.md → docs/_archive/tasks-history.md

# Compact SESSION_LOG.md if >50KB
./run.sh session compact

# Run agent evolution (observe only during burn-in)
./run.sh evolve --status

# Clean stale git branches (dry-run first!)
.venv/bin/python scripts/cleanup_stale_branches.py --dry-run
```

---

## 3. Monthly Review (~2 hours)

```bash
# Full validation (all checks, parallel)
./run.sh check

# Full readiness audit
./run.sh audit

# IS 456 clause coverage dashboard
./run.sh parity

# Element completeness check
.venv/bin/python scripts/check_new_element_completeness.py

# Function quality scan
.venv/bin/python scripts/check_function_quality.py

# Feedback trends
./run.sh feedback summary

# Agent evolution review
./run.sh evolve --review weekly
```

---

## 4. Quality Gate Enforcement (Per PR)

Every new IS 456 function must pass the 9-step pipeline
(see `/function-quality-pipeline` skill):

1. **PLAN** → clause + formula + benchmark
2. **MATH REVIEW** → formula verified by @structural-engineer
3. **IMPLEMENT** → 12-point checklist (check with `check_function_quality.py`)
4. **TEST** → 6 test types (unit, edge, degenerate, SP:16, textbook, hypothesis)
5. **REVIEW** → dual pass: @structural-engineer (math) + @reviewer (code)
6. **API WIRE** → services/api.py
7. **ENDPOINT** → FastAPI router
8. **DOCUMENT** → docs updated
9. **COMMIT** → via ai_commit.sh

### Quality gates between steps

| Gate | Requirement |
|------|-------------|
| Step 2 → 3 | Formula approved by @structural-engineer |
| Step 4 → 5 | All tests pass (SP:16 benchmarks ±0.1%) |
| Step 5 → 6 | Both reviews (math + code) approved |

---

## 5. Quarterly Benchmarks (Structural Engineering)

| Task | Command | Purpose |
|------|---------|---------|
| Run all SP:16 benchmarks | `.venv/bin/pytest Python/tests/ -v -k "sp16 or benchmark"` | Catch regression from refactoring |
| Verify IS 456 table values | Manual check against standard | Tables are typed constants — typos propagate |
| Check BIS website for amendments | `fetch_webpage` for BIS portal | IS 456:2000 periodically revised |
| Clause coverage report | `.venv/bin/python scripts/check_clause_coverage.py` | Track implementation progress |

---

## 6. Error Handling Standards

All `DesignError` codes require:

| Field | Description |
|-------|-------------|
| `code` | Unique identifier (e.g. `E_FLEXURE_001`, `E_COLUMN_003`) |
| `severity` | `error` / `warning` / `info` |
| `message` | Human-readable description |
| `field` | Input field that caused the error |
| `hint` | Quick actionable tip (~1 line) |
| `clause` | IS 456 clause reference |
| `recovery` | Step-by-step fix instructions |

Error codes are defined in `Python/structural_lib/core/errors.py`.

---

## 7. Governance Limits

Enforced by `check_governance.py`:

| Rule | Limit | Check Command |
|------|-------|---------------|
| Root folder files | ≤ 17 | `./run.sh check --quick` |
| docs/ root files | ≤ 5 | `./run.sh check --quick` |
| docs/ total files | < 400 | `.venv/bin/python scripts/check_docs.py --budget` |
| WIP tasks | ≤ 2 | Review TASKS.md |
| Draft docs age | ≤ 7 days | Archive or promote |

---

## 8. Documentation Sync

After structural changes (file moves, renames, new modules):

```bash
# Regenerate folder indexes
.venv/bin/python scripts/generate_enhanced_index.py --all

# Sync numbers in docs
.venv/bin/python scripts/sync_numbers.py --fix

# Check internal links (870+)
.venv/bin/python scripts/check_links.py

# Safe file operations (NEVER use mv/rm directly)
.venv/bin/python scripts/safe_file_move.py old.md new.md --dry-run
.venv/bin/python scripts/safe_file_delete.py file.md
```

---

## 9. Release Checklist

```bash
# Pre-release validation
./run.sh release preflight <version>

# Docker-based preflight (2GB memory limit)
./run.sh release preflight --docker

# Version bump + release
./run.sh release run <version>
```

---

## 10. Incident Response

| Scenario | Diagnosis | Fix |
|----------|-----------|-----|
| Test failure | `.venv/bin/pytest Python/tests/ -v -k "test_name" --tb=short` | Use `/fix-test-failure` prompt |
| Import error | `.venv/bin/python scripts/validate_imports.py --scope structural_lib` | Fix import chain |
| Architecture breach | `.venv/bin/python scripts/check_architecture_boundaries.py` | Move code to correct layer |
| Broken links | `.venv/bin/python scripts/check_links.py` | Update paths or use `safe_file_move` |
| Calculation error reported | 1. Identify IS 456 clause 2. Hand-verify vs SP:16 3. Add regression test | Fix formula, trace @clause |

---

## 11. Agent System Maintenance

```bash
# Agent performance scoring
.venv/bin/python scripts/agent_scorer.py --agent backend

# Drift detection
.venv/bin/python scripts/agent_drift_detector.py --latest

# Compliance check
.venv/bin/python scripts/agent_compliance_checker.py --latest

# Route a task to best agent
./run.sh route "task description"

# Check agent registry
cat agents/agent_registry.json | python -m json.tool | head -50
```
