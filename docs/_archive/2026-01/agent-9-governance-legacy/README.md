# Agent 9 Governance Hub

**Purpose:** Central home for governance, migration, and structure decisions.
**Owner:** Agent 9 (Governance & Sustainability)
**Navigation rule:** Use this README first, then jump to a single target doc.

---

## Quick Navigation (Start Here)

1. **Decision entry point**
   - `DECISION-SUMMARY.md` (final questions + readiness)
   - `AGENT-9-AND-MIGRATION-REVIEW.md` (review synthesis)

2. **Execution plan**
   - `FULL-MIGRATION-EXECUTION-PLAN.md` (ultra-safe plan)
   - `MIGRATION-TASKS.md` (step-by-step tasks + validations)
   - `MIGRATION-EXECUTION-PLAN.md` (execution order + stop conditions)
   - `MIGRATION-WALKTHROUGH.md` (operator runbook)
   - `MIGRATION_REVIEW_AND_RISKS.md` (known risks + mitigations)
   - `AGENT-9-GOVERNANCE-ROADMAP.md` (post-migration roadmap)

3. **Phase-by-phase docs**
   - `PHASE-0-PREPARATION.md`
   - `PHASE-1-STRUCTURE-CREATION.md`
   - `PHASE-2-AGENTS-MIGRATION.md`
   - `PHASE-4-DATED-FILES.md`
   - `PHASE-5-NAMING-CLEANUP.md`
   - `PHASE-6-LINK-FIXING.md`
   - `PHASE-7-SCRIPT-UPDATES.md`
   - `PHASE-8-FINAL-VALIDATION.md`

4. **Governance rules**
   - [FOLDER_STRUCTURE_GOVERNANCE.md](FOLDER_STRUCTURE_GOVERNANCE.md) (naming rules + exceptions)
   - [FOLDER_IMPLEMENTATION_GUIDE.md](_archive/FOLDER_IMPLEMENTATION_GUIDE.md) (practical setup)
   - [FOLDER_GOVERNANCE_RESEARCH_SUMMARY.md](_archive/FOLDER_GOVERNANCE_RESEARCH_SUMMARY.md) (research basis)
   - [RECURRING-ISSUES-ANALYSIS.md](RECURRING-ISSUES-ANALYSIS.md) (recurring issues & solutions)
   - [AUTOMATION-CATALOG.md](AUTOMATION-CATALOG.md) (available automation scripts)
   - [PHASE-B-TASK-TRACKER.md](PHASE-B-TASK-TRACKER.md) (Phase B task tracking)

5. **Execution support**
   - `ROLLBACK-PROCEDURES.md` (rollback levels)
   - `MIGRATION-SCRIPTS.md` (script references)
   - `LINK-MAP.md` (link tracking)
   - `MIGRATION-STATUS.md` (live status)
   - `METRICS_DASHBOARD.md` (auto-generated)

---

## Navigation Principles (Adopted)

- **Progressive disclosure:** start with this README, then go one level deeper.
- **Information scent:** use descriptive filenames and clear doc titles.
- **Two-level depth limit:** no deep nesting beyond this hub.
- **Diataxis separation:** keep reference, how-to, and explanation content separate.
- **Front matter metadata (optional):** add `Owner`, `Status`, `Last Updated` for fast scanning.

---

## Working Rules

- Keep governance docs inside `agents/agent-9/governance/`.
- Update references when file names or locations change.
- Use `scripts/generate_dashboard.sh` to refresh `METRICS_DASHBOARD.md`.
- Keep the migration plan phase-by-phase to reduce risk.
