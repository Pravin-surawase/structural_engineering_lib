# Agent Workflow Improvements — Roadmap

**Type:** Planning
**Audience:** All Agents
**Status:** Approved
**Importance:** High
**Created:** 2026-03-23
**Last Updated:** 2026-03-23

---

## Problem Statement

AI agents spend significant time on repetitive documentation tasks every session:
- **3–5 docs** need manual updates at session end (SESSION_LOG, TASKS, next-session-brief, bootstrap files)
- **Numbers go stale** across files (test count, script count, endpoint count, hook count)
- **Phantom references** appear when docs mention hooks/components that don't exist
- **No auto-detection** of new hooks, routes, or components added during a session
- **SESSION_LOG entries** are often left as skeleton templates

## Implemented Solutions

### 1. `sync_numbers.py` — Automated Codebase-to-Doc Sync

**Location:** `scripts/sync_numbers.py`
**Purpose:** Scan actual codebase and update stale counts across all doc files in one command.

**What it scans:**

| Metric | Source | Method |
|--------|--------|--------|
| Test count | `Python/tests/` | pytest `--co` collection |
| Script count | `scripts/*.py + *.sh` | File count |
| Hook count | `react_app/src/hooks/` | Grep for `export function` |
| Endpoint count | `fastapi_app/routers/` | Grep for `@router.<method>` |
| Router count | `fastapi_app/routers/*.py` | File count (minus `__init__`) |
| API public functions | `services/api.py` | Grep for `^def ` (non-underscore) |
| API private functions | `services/api.py` | Grep for `^def _` |
| Component count | `react_app/src/components/` | Find `*.tsx` |
| Hook files | `react_app/src/hooks/` | File count |

**Files it updates:**
- `README.md`
- `llms.txt`
- `CLAUDE.md`
- `.github/copilot-instructions.md`

**Usage:**
```bash
.venv/bin/python scripts/sync_numbers.py           # Scan + report (dry run)
.venv/bin/python scripts/sync_numbers.py --fix      # Scan + update files
.venv/bin/python scripts/sync_numbers.py --json     # Machine-readable output
```

### 2. `session.py summary` — Auto-Generate Session Summary

**Location:** Integrated into `scripts/session.py` as `summary` subcommand.
**Purpose:** Generate a session summary from git history, detect new code artifacts.

**What it detects from git log:**
- Commits since last session (grouped by type: feat, fix, docs, refactor, etc.)
- Files changed count and categories
- New hooks (new `export function use*` in hooks/)
- New endpoints (new `@router.*` in routers/)
- New components (new `.tsx` files in components/)
- New test files

**What it generates:**
- Summary paragraph for SESSION_LOG.md entry
- Commit-type breakdown
- List of new artifacts detected
- Updated handoff block for next-session-brief.md

**Usage:**
```bash
.venv/bin/python scripts/session.py summary           # Show summary (dry run)
.venv/bin/python scripts/session.py summary --write    # Write to SESSION_LOG + handoff
```

### 3. `session.py sync` — Run sync_numbers as Part of Session Workflow

**Location:** Integrated into `scripts/session.py` as `sync` subcommand.
**Purpose:** Convenience wrapper — runs sync_numbers.py from session workflow.

**Usage:**
```bash
.venv/bin/python scripts/session.py sync              # Scan + report
.venv/bin/python scripts/session.py sync --fix        # Scan + update files
```

---

## Recommended Agent Workflow (Updated)

### Session Start (unchanged)
```bash
./scripts/agent_start.sh --quick
```

### During Session (unchanged)
```bash
./scripts/ai_commit.sh "type: message"      # Commit work
```

### Session End (NEW — simplified)
```bash
# Step 1: Auto-generate session summary
.venv/bin/python scripts/session.py summary --write

# Step 2: Sync all numbers across docs
.venv/bin/python scripts/session.py sync --fix

# Step 3: Run end-of-session checks
.venv/bin/python scripts/session.py end --fix

# Step 4: Commit doc updates
./scripts/ai_commit.sh "docs: session end — auto-summary + sync"
```

**Before (manual):** Agent reads git log → manually writes SESSION_LOG → manually updates next-session-brief → manually checks numbers → 15–30 min.

**After (automated):** 3 commands → review output → commit → 2–5 min.

---

## Future Improvement Ideas

### Near-Term (v0.20 timeframe)

| # | Idea | Impact | Effort |
|---|------|--------|--------|
| 1 | **Hook into `ai_commit.sh`** — run sync_numbers after each commit | Numbers always fresh | Low |
| 2 | **Pre-commit hook validation** — warn if numbers are stale | Catch drift early | Low |
| 3 | **Session number auto-increment** — detect last session # from SESSION_LOG | Less manual tracking | Low |
| 4 | **Docker health in `agent_start.sh`** — check if FastAPI container is running | Fewer "can't connect" issues | Low |

### Medium-Term (v0.21+)

| # | Idea | Impact | Effort |
|---|------|--------|--------|
| 5 | **GitHub Actions CI check** — run sync_numbers in PR validation | Catch stale docs in PRs | Medium |
| 6 | **TypeScript SDK generation** — auto-generate from OpenAPI spec | Keep TS types in sync | Medium |
| 7 | **Interactive API playground** — Swagger UI with example payloads | Faster API exploration | Medium |
| 8 | **PyPI release automation** — `scripts/release.py publish` | One-command releases | Medium |

### Long-Term (v0.22+)

| # | Idea | Impact | Effort |
|---|------|--------|--------|
| 9 | **Multi-code support** — IS 13920, ACI 318 beyond IS 456 | Major feature expansion | High |
| 10 | **VS Code extension** — sidebar for beam design | IDE integration | High |
| 11 | **CLI web mode** — `structlib serve` for local web UI | Desktop users | High |
| 12 | **Auto-bootstrap refresh** — detect when bootstrap docs need update | Zero-maintenance docs | Medium |
| 13 | **Agent performance dashboard** — track session productivity metrics | Process improvement | Medium |

---

## Design Principles

1. **Scan, don't guess** — Always read actual code, never hardcode counts
2. **Dry-run by default** — Show what would change before changing it
3. **Extend `_lib/`** — Reuse shared utilities, don't duplicate
4. **Future-proof patterns** — Use regex patterns that survive when new hooks/routes are added
5. **Fail gracefully** — Missing files or failed scans produce warnings, not crashes
