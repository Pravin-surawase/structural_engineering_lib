# Agent 9 Governance Roadmap

**Date:** 2026-01-10
**Owner:** Agent 9 (Governance)
**Status:** Active (post-migration)

---

## Purpose

Single, stable plan for governance, sustainability, and AI-agent efficiency.
Use this doc as the one place to track goals, links, safety rules, tests, and success metrics.

---

## Goals (What "Done" Looks Like)

1. **Governance stability:** zero validation errors/warnings and no root/doc drift.
2. **Sustainable maintenance:** weekly checks + monthly deep validation without hero effort.
3. **AI agent efficiency:** predictable entry points, shallow navigation, clear information scent.
4. **Auditability:** every structure change logged with validation results.

---

## Current Baseline (Post-Migration)

- Validation errors: 0
- Validation warnings: 0
- Broken links: 0
- Root files: 10 (target met)
- docs/ root files: 3 (target met)

---

## Next Tasks (Execute in Order)

### 1) Merge the doc-fix branch
**Why:** keep the migration audit trail accurate.
**Action:** merge `chore/agent-8-consolidation-doc-fixes` into main.

### 2) Add Agent 9 entry points under docs/agents/
**Why:** research shows entry hubs reduce search time and context waste.
**Action:**
- Create `docs/agents/guides/agent-9-quick-start.md`.
- Create `docs/agents/guides/agent-9-governance-hub.md` linking to `agents/agent-9/governance/README.md`.
- Update `docs/agents/README.md` to link Agent 9 entry points.

### 3) Re-run navigation study after entry points exist
**Why:** prior study ran on a messy structure; re-test on clean structure.
**Action:** run `scripts/measure_agent_navigation.sh` + `scripts/analyze_navigation_data.py`.

### 4) Archive Phase A0-A6 planning docs
**Why:** keep active folders clean and reduce noise.
**Action:** move obsolete planning docs to `docs/_archive/YYYY-MM/` and update index.

---

## Ongoing Maintenance Cadence

### Weekly (15-30 min)
- `python3 scripts/validate_folder_structure.py`
- `python3 scripts/check_links.py`
- `./scripts/check_root_file_count.sh`
- Update `agents/agent-9/governance/MIGRATION-STATUS.md` if anything changed.

### Monthly (60-90 min)
- `./scripts/generate_dashboard.sh` + review metrics
- Re-run navigation study (baseline + hierarchical)
- Archive old session docs (`./scripts/archive_old_sessions.sh` DRY_RUN=1 first)

---

## Tests and Safety Checks (Run After Every Batch)

- `python3 scripts/validate_folder_structure.py`
- `python3 scripts/check_links.py`
- `./scripts/check_docs_index.py`
- `./scripts/check_docs_index_links.py`
- `./scripts/check_root_file_count.sh`

**Stop condition:** Any failure pauses the batch until fixed and logged.

---

## Success Metrics (Track in MIGRATION-STATUS.md)

| Metric | Target | Why |
| --- | --- | --- |
| Root files | ≤ 10 | Prevent root drift |
| docs/ root files | ≤ 5 | Keep docs hub small |
| Validation errors/warnings | 0 | Governance compliance |
| Broken links | 0 | Reliability for agents |
| Navigation error rate | ↓ | Measured by study |
| Files opened per task | ↓ | Efficiency |
| Tokens per task | ↓ | Context efficiency |

---

## Known Pitfalls (Avoid These)

- **Case-only renames on macOS** (pre-commit stash conflicts). Use temp names.
- **Moving scripts out of `scripts/`** (breaks automation and CI).
- **Untracked link updates** (always run link checks after moves).
- **Duplicate authority** (one canonical hub + links; no parallel docs).
- **Skipping validation** (drift reappears quickly).

---

## Key Links (Single Source of Truth)

- Governance rules: `agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md`
- Migration status: `agents/agent-9/governance/MIGRATION-STATUS.md`
- Task plan: `agents/agent-9/governance/MIGRATION-TASKS.md`
- Walkthrough: `agents/agent-9/governance/MIGRATION-WALKTHROUGH.md`
- Automation catalog: `agents/agent-9/governance/AUTOMATION-CATALOG.md`
- Recurring issues: `agents/agent-9/governance/RECURRING-ISSUES-ANALYSIS.md`
- Validation scripts: `scripts/validate_folder_structure.py`, `scripts/check_links.py`
- Agent hubs: `docs/agents/README.md`

---

## Ownership Rules

- Agent 9 owns governance docs under `agents/agent-9/governance/`.
- All agent entry points live in `docs/agents/`.
- No changes to validation scripts without updating governance rules + tests.
