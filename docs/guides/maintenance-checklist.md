# Maintenance Checklist

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** High
**Created:** 2026-03-29
**Last Updated:** 2026-03-29

---

## Quick Reference

| Frequency | Command | What It Does | Time |
|-----------|---------|-------------|------|
| **Daily** | `./run.sh health --quick` | Fast health scan (numbers, links) | ~10s |
| **Daily** | `./run.sh check --quick` | 8 core validation checks | ~30s |
| **Weekly** | `./run.sh evolve --review weekly` | Numbers sync + links + feedback | ~1min |
| **Weekly** | `./run.sh health` | Full 5-category health scan (0-100) | ~3min |
| **Weekly** | `./run.sh check` | All 28 validation checks | ~2min |
| **Monthly** | `./run.sh evolve --review monthly` | Full review + archive stale docs | ~5min |
| **Monthly** | `./run.sh audit` | 25-check readiness report | ~3min |
| **On Demand** | `./run.sh evolve --fix` | Auto-fix all fixable issues + commit | ~3min |
| **On Demand** | `./run.sh health --fix` | Auto-fix health issues | ~2min |

---

## Daily Maintenance (2 minutes)

Run these at the start or end of each session:

```bash
# 1. Quick health check
./run.sh health --quick

# 2. Quick validation
./run.sh check --quick

# 3. Check for uncommitted work
git status --short
```

**If issues found:** Run `./run.sh health --fix` to auto-fix, or note for weekly review.

---

## Weekly Maintenance (15-30 minutes)

Run every 5th session or weekly:

```bash
# 1. Full evolution review
./run.sh evolve --review weekly

# 2. Full health scan
./run.sh health

# 3. Full validation (28 checks)
./run.sh check

# 4. Run test suite
./run.sh test

# 5. Check feedback backlog
./run.sh feedback summary

# 6. Regenerate indexes (if files changed)
./run.sh generate indexes
```

### Weekly Manual Checks

| Check | How | Target |
|-------|-----|--------|
| Stale TASKS.md items | Read first 20 lines of `docs/TASKS.md` | No items >2 weeks old |
| next-session-brief freshness | Check `docs/planning/next-session-brief.md` date | Updated within last session |
| Open PRs | `gh pr list` | No stale PRs (>7 days old) |
| CI status | `gh run list --limit 5` | All recent runs green |
| Doc version numbers | `./run.sh session sync` | No drift detected |

---

## Monthly Maintenance (1-2 hours)

### Agent: governance (delegated by orchestrator)

```bash
# 1. Full monthly evolution
./run.sh evolve --review monthly

# 2. Full audit
./run.sh audit

# 3. Architecture check
.venv/bin/python scripts/check_architecture_boundaries.py

# 4. Import validation
.venv/bin/python scripts/validate_imports.py --scope structural_lib

# 5. Check for circular imports
.venv/bin/python scripts/check_circular_imports.py

# 6. Bootstrap freshness
.venv/bin/python scripts/check_bootstrap_freshness.py

# 7. Stale branch cleanup (dry-run first)
.venv/bin/python scripts/cleanup_stale_branches.py --dry-run

# 8. Instruction drift check
# Compare .github/instructions/*.instructions.md with .claude/rules/*.md
```

### Monthly Manual Checks

| Check | Tool | Action If Failed |
|-------|------|-----------------|
| Architecture violations | `check_architecture_boundaries.py` | Delegate to @backend |
| Circular imports | `check_circular_imports.py` | Delegate to @backend |
| Broken imports | `validate_imports.py` | Delegate to @backend |
| Stale GitHub issues | `gh issue list --state open` | Close with user approval |
| Merged branches still remote | `cleanup_stale_branches.py` | Delete with user approval |
| Agent instruction drift | Compare instruction files | Delegate to @doc-master |
| Test coverage | `./run.sh test` | Delegate to @tester |
| React build | `cd react_app && npm run build` | Delegate to @frontend |

---

## Health Score Categories

| Category | Weight | What It Checks |
|----------|--------|----------------|
| docs | 30% | Staleness, broken links, version drift, number sync |
| code | 25% | Linting, import cycles, architecture boundaries |
| agents | 20% | Agent instructions, skill manifests |
| infra | 15% | Docker config, CI checks, git state |
| feedback | 10% | Unresolved feedback items |

**Target:** 80+ overall score (Grade B or better)

---

## Common Fix Patterns

| Issue | Fix Command | Agent |
|-------|-------------|-------|
| Stale doc numbers | `./run.sh evolve --fix` | governance |
| Broken links | Manual fix or `safe_file_move.py` | doc-master |
| Architecture violations | Fix imports in violating file | backend |
| Missing git hooks | `bash scripts/install_git_hooks.sh` | ops |
| Stale branches | `cleanup_stale_branches.py --execute` | ops (needs approval) |
| Import cycle | Refactor module dependencies | backend |
| Agent instruction drift | Sync instruction files | doc-master |

---

## Maintenance Pipeline (Who Does What)

```
orchestrator  → diagnose (./run.sh health, ./run.sh check)
  → governance  → auto-fixes (evolve --fix, indexes, sync)
  → backend     → code fixes (architecture, imports, cycles)
  → tester      → verify no regressions
  → doc-master  → doc fixes (dates, drift, references)
  → reviewer    → verify health score improved
  → ops         → commit safely (ai_commit.sh)
```

---

## Tracking

After each maintenance session, log results:

```bash
# Log to WORKLOG
# Date | MAINT | description | commit

# Update health score in next-session-brief
# "Last health score: XX/100 (date)"
```
