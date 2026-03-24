# Agent Onboarding Audit — Session 93

**Type:** Audit
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-03-24
**Last Updated:** 2026-03-24

---

## Purpose

Fresh-agent onboarding test: followed all documented steps exactly as a new AI agent would, and logged every friction point, error, and inconsistency encountered.

---

## Issues Found

### CRITICAL — Broken Script References (Silent Failures)

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | `session.py` calls `check_handoff_ready.py` but it was archived to `scripts/_archive/` | [session.py](../../scripts/session.py) L262 | "Doc Freshness" and "Handoff Checks" ALWAYS report "Some checks failed" — both in `agent_start.sh --quick` and `session.py end`. New agents see perpetual warnings with no actionable fix. |
| 2 | `audit_readiness_report.py` references `scripts/check_doc_metadata.py` which is also archived | [audit_readiness_report.py](../../scripts/audit_readiness_report.py) L385 | Audit report silently skips doc metadata check |
| 3 | `finish_task_pr.sh` defaults to "Async" mode which calls `ci_monitor_daemon.sh` — also archived | [finish_task_pr.sh](../../scripts/finish_task_pr.sh) L279-281 | PR finalization crashes with "No such file or directory" error after PR is created. Agent left on task branch instead of returning to main. |

### HIGH — Stale/Non-Existent Doc Paths in Scripts

| # | Issue | File | Line | Correct Path |
|---|-------|------|------|-------------|
| 3 | `session.py` prints "Read first: docs/handoff.md" — file does not exist | [session.py](../../scripts/session.py) L338 | `docs/planning/next-session-brief.md` |
| 4 | `session.py` prints "docs/agent-bootstrap.md" — file does not exist at that path | [session.py](../../scripts/session.py) L338 | `docs/getting-started/agent-bootstrap.md` |
| 5 | `session.py` prints "docs/ai-context-pack.md" — file does not exist | [session.py](../../scripts/session.py) L338 | Remove (no replacement exists) |
| 6 | `bump_version.py` references `docs/ai-context-pack.md` in version bump targets | [bump_version.py](../../scripts/bump_version.py) L69 | Remove stale entry |

### MEDIUM — Inconsistent Numbers Across Docs

| # | Issue | Where | Says | Actual |
|---|-------|-------|------|--------|
| 7 | `agent_start.sh` output says "api.py → 43 public functions" | [agent_start.sh](../../scripts/agent_start.sh) L279 | 43 | 23 public + 6 private = 29 total |

### LOW — UX/Clarity Issues

| # | Issue | Details |
|---|-------|---------|
| 8 | `session.py check` fails with "SESSION_LOG.md entry missing 'Focus:' line" but doesn't tell you how to fix it | No template or auto-fix offered |
| 9 | `session.py end` handoff check says "Some checks failed" with no specifics | Because the underlying script is archived, it always returns "Script not found" which becomes a generic error |
| 10 | `session.py summary` has no `--dry-run` option | Would be useful to preview before writing to SESSION_LOG |
| 11 | `check_docs.py` references `check_doc_metadata.py` in comments (L15) | Script archived, comment is stale |
| 12 | 1 property test failing: `test_valid_inputs_return_valid_geometry` in `test_ductile_hypothesis.py` | Pre-existing — not from this session |

---

## What Works Well

The onboarding workflow has many strong points worth preserving:

1. **`agent_start.sh --quick`** — Fast (6s), installs hooks, shows clear overview
2. **`discover_api_signatures.py`** — Excellent tool, exact params with units and types
3. **`find_automation.py`** — Good natural-language script discovery
4. **`ai_commit.sh`** — Reliable, handles staging + hooks + push
5. **`create_task_pr.sh`** — Clean branch creation with auto-stash
6. **`session.py sync`** — Correctly counts all metrics across docs
7. **4-layer architecture** is well-documented and enforced
8. **CLAUDE.md / AGENTS.md / copilot-instructions.md** — Comprehensive, mostly accurate
9. **Folder `index.json` + `index.md`** — Excellent for fast context loading
10. **next-session-brief.md** — Detailed handoff with clear priorities

---

## Fixes Applied in This PR

1. ✅ Fix `session.py` stale doc references (L338)
2. ✅ Fix `session.py` archived script reference — inlined basic handoff check
3. ✅ Fix `agent_start.sh` API function count (43 → 23 public + 6 private)
4. ✅ Fix `bump_version.py` stale `ai-context-pack.md` reference
5. ✅ Fix `finish_task_pr.sh` crash when `ci_monitor_daemon.sh` is archived — graceful fallback

---

## Recommendations for Future Improvement

### P1 — Quick Wins
- Add `--dry-run` to `session.py summary` for preview without writing
- Add specific error messages when `check_handoff_ready.py` can't be found
- Add a "Focus:" line auto-insertion to session log skeleton

### P2 — Workflow Improvements
- Create a `validate_script_refs.py` that checks all scripts referenced by other scripts actually exist
- Add periodic stale-reference detection to CI
- Add a "doc freshness" metric to `session.py sync` that verifies all paths printed in output exist

### P3 — Documentation
- Consolidate the 3 instruction files (CLAUDE.md, AGENTS.md, copilot-instructions.md) — they overlap heavily and drift apart
- Consider a single source-of-truth for agent numbers (functions, endpoints, hooks) that all docs and scripts pull from
