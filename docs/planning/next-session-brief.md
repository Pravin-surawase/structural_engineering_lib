# Next Session Briefing

**Type:** Handoff
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2025-01-01
**Last Updated:** 2026-03-28

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-03-28
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Previous** | v0.20.0 | ✅ Done (React migration complete) |
| **Current** | v0.19.1 | 🔄 React UX Overhaul + Library Expansion |
| **Next** | v0.22.0 | 📋 Planned |

**Last Session:** Session 106 (Ops: CI Fixes + GitHub Maintenance)

---

## Session 106 Summary

- Fixed 3 CI blockers on PR #441 (black, ruff F401, circular import false positives)
- Merged PR #441 + Dependabot PR #434
- Closed 5 stale nightly QA issues, deleted 20 stale branches
- Created `scripts/github_maintenance.sh` + `.github/workflows/stale-cleanup.yml`
- Added auto-close to `nightly.yml` (closes old QA issues when nightly passes)

**Known Issues:**
- `gh pr checks --watch` hangs terminals → use `--json` instead
- Agent terminal PATH issue NOT fixed (agents try wrong venv location)
- Security Scan: cyclonedx-py CLI syntax changed
- Windows-only: `test_smart_designer_metadata` timing failure
- OpenSSF Scorecard: intermittent artifact upload failures

---

## Next Priorities

### Do First — Fix CI on Main

1. **Fix Security Scan** — cyclonedx-py CLI syntax changed
2. **Fix Windows test** — `test_smart_designer_metadata`: use `time.perf_counter()`
3. **Monitor OpenSSF Scorecard** — re-run before fixing

### Then — Agent Terminal Fixes + UX

1. **FIX AGENT TERMINAL PATHS** ← URGENT
2. **TASK-525: Smart HubPage**
3. **Phase 6: Archive stale planning docs** (43 → <10)
4. **TASK-517: Project BOQ**

### Design Principles
- Editor is the workstation → manual form only in `/design`
- Data-first → import → 3D → click beam → reinforcement
- IS 456 accuracy → top bars match 3D/2D, utilization = Mu/Mu_cap

### Recently Completed
- GitHub maintenance automation (github_maintenance.sh + stale-cleanup.yml)
- TASK-505: API integration tests (86 tests, 12 routers)
- TASK-510: Batch design, TASK-514: PDF export, TASK-515: Load calc, TASK-518: Torsion API

### Technical Debt
- 2 architecture violations: rebar_optimizer/multi_objective_optimizer bypass api facade
- ~13 backward-compat stub imports in streamlit_app/

---

## GitHub Maintenance

```bash
./run.sh github health              # Full health report
./run.sh github full-cleanup        # Preview all cleanup
./run.sh github clean-branches --execute  # Delete stale branches
```

Automated: `stale-cleanup.yml` runs weekly (Sundays 6 AM UTC).

---

## Required Reading

- [TASKS.md](../TASKS.md) — Current task tracking
- [AGENTS.md](../../AGENTS.md) — Cross-agent instructions

---

## Quick Commands

```bash
./run.sh session start              # Begin work
./run.sh commit "type: message"     # Safe commit
./run.sh check --quick              # Fast validation
./run.sh github health              # GitHub health
./run.sh test                       # Run pytest
docker compose up --build           # FastAPI at :8000/docs
cd react_app && npm run dev         # React at :5173
```
