# Agent Repo Map Research

**Date:** 2026-01-10
**Status:** Draft research log (do not migrate yet)

---

## Scope

Document the current repo layout, agent workflow entry points, automation scripts, and high-risk gaps so we do not repeat discovery work later.

---

## Repo Structure Snapshot (Current State)

**Top-level:**
- `Python/` - primary library source and tests.
- `streamlit_app/` - Streamlit UI, pages, components, tests, and UI docs.
- `VBA/` - VBA modules, tests, examples.
- `Excel/` - Excel add-ins, templates, snapshots.
- `docs/` - documentation, planning, research, governance, and handoffs.
- `scripts/` - automation scripts (git, session, testing, validation, releases).
- `agents/` - agent role docs and agent-9 governance suite.
- `external_data/` - user-provided Excel files (external inputs).

**Notable external/integration areas:**
- `docs/specs/etabs-integration.md`
- `docs/research/xlwings-vba-strategy.md`
- `docs/_internal/copilot-tasks/xlwings-*`

---

## Agent Workflow Entry Points (Verified)

**Start session**
- `scripts/start_session.py`
- `docs/agent-bootstrap.md`
- `docs/AGENT_ONBOARDING.md`

**End session / handoff**
- `scripts/end_session.py`
- `scripts/check_handoff_ready.py`
- `scripts/update_handoff.py`
- `docs/handoff.md`
- `docs/contributing/end-of-session-workflow.md`

**Git workflow**
- `docs/git-workflow-ai-agents.md`
- `docs/AGENT_WORKFLOW_MASTER_GUIDE.md`
- `scripts/ai_commit.sh`
- `scripts/safe_push.sh`
- `scripts/should_use_pr.sh`
- `scripts/create_task_pr.sh`
- `scripts/finish_task_pr.sh`
- `scripts/recover_git_state.sh`
- `scripts/check_unfinished_merge.sh`
- `scripts/validate_git_state.sh`

**Release workflow**
- `scripts/release.py`
- `scripts/bump_version.py`
- `scripts/verify_release.py`
- `scripts/check_release_docs.py`
- `docs/releases.md`

---

## Streamlit UI (Testing and Validation)

- App root: `streamlit_app/app.py`
- Pages: `streamlit_app/pages/` (emoji + numeric prefix filenames)
- Tests: `streamlit_app/tests/`
- Docs: `streamlit_app/docs/`
- Validation tooling:
  - `scripts/check_streamlit_issues.py` (AST scanner)
  - `streamlit_app/SETUP_AND_MAINTENANCE_GUIDE.md`
  - `docs/streamlit-maintenance-guide.md`

---

## VBA / Excel / Xlwings / ETABS

- VBA code: `VBA/Modules/`, tests: `VBA/Tests/`.
- Excel deliverables: `Excel/` + `Excel/Templates/`.
- Xlwings research and plans in `docs/research/` and `docs/_internal/copilot-tasks/`.
- ETABS integration spec in `docs/specs/etabs-integration.md`.

---

## Automation Catalog vs Reality (Mismatch Risks)

- `docs/reference/automation-catalog.md` provides a script catalog.
- Some content diverges from actual script behavior:
  - `update_handoff.py` reads `docs/SESSION_LOG.md` (not git commits).
  - Link checker usage in some governance docs mismatches `scripts/check_links.py`.

---

## High-Risk Gaps and Conflicts

1. **Duplicate session logs (resolved):** canonical `docs/SESSION_LOG.md`; lowercase duplicate removed.
   - Scripts/docs updated to use `SESSION_LOG.md`.
   - Risk mitigated for case-sensitive systems.

2. **Naming governance vs Streamlit pages:** emoji + numeric prefixes in `streamlit_app/pages/` conflict with strict kebab-case governance.
   - Needs an explicit exception in governance/validator rules.

3. **Migration docs referencing missing scripts:** several migration docs reference scripts that do not exist in this repo.
   - Must reconcile before executing any migration plan.

---

## Next Research Steps (Planned)

1. Documentation deep-dive: verify doc index and required reading paths.
2. Automation alignment: reconcile docs vs actual scripts and update references.
3. Tests matrix: build one verified test map (Python + Streamlit + VBA + Excel).
4. Agent navigation model: draft a minimal, high-signal agent hub without moving files.

---

**Research Note:** No structural changes should be made until the documentation review is complete and user approval is recorded.

---

## Documentation Review (Current State)

**Primary index:**
- `docs/README.md` is the canonical entry map. It already lists:
  - Core agent onboarding and workflow docs
  - Canonical roots and legacy redirects
  - Release history and planning links

**Handoff & session workflow:**
- `docs/agent-bootstrap.md` → `scripts/start_session.py` (first 30 seconds).
- `docs/AGENT_ONBOARDING.md` → `scripts/agent_setup.sh`, `scripts/agent_preflight.sh`.
- `docs/handoff.md` + `docs/contributing/end-of-session-workflow.md` → `scripts/end_session.py`.
- `scripts/update_handoff.py` writes to `docs/planning/next-session-brief.md` (handoff block).

**Git workflow:**
- Canonical rule set in `docs/git-workflow-ai-agents.md`.
- Operational detail in `docs/AGENT_WORKFLOW_MASTER_GUIDE.md`.

**Release workflow:**
- `scripts/release.py` (bump + checklist).
- `docs/releases.md` (immutable ledger + process).

---

## Documentation Audit Findings

**From `docs/research/documentation-handoff-analysis.md`:**
- Confirms strong onboarding, handoff, and git automation coverage.
- Notes automation discoverability gap and recommends a catalog.
- Lists 41 scripts and recommends creating `docs/reference/automation-catalog.md`.

**Reality check vs repo:**
- `docs/reference/automation-catalog.md` already exists and lists 43 scripts.
- Current `scripts/` count is **71 files** (catalog is outdated by 27 scripts).
- `docs/README.md` canonical roots list `SESSION_LOG.md`.

---

## Risks Identified (Updated)

1. **Session log casing split (resolved)**
   - Canonical `docs/SESSION_LOG.md`; lowercase duplicate removed.
   - Scripts/docs align on uppercase naming.

2. **Automation catalog drift**
   - Catalog exists but undercounts scripts (43 vs 71).
   - Missing 27 scripts from the catalog (see list below).

3. **Streamlit page naming conflict**
   - `streamlit_app/pages/` uses emoji + numeric prefixes.
   - Governance naming rules require kebab-case; needs explicit exception.

---

## Next Documentation Research (In Progress)

1. Cross-check `docs/reference/automation-catalog.md` against actual scripts.
2. Verify `docs/README.md` canonical roots and fix mismatched references (no edits yet).
3. Build a minimal agent hub outline using existing docs only.

---

## Automation Catalog Gap (Concrete List)

**Scripts present in `scripts/` but missing from the catalog (27):**

```
agent_preflight.sh
agent_setup.sh
archive_old_files.sh
archive_old_sessions.sh
auto_fix_page.py
autonomous_fixer.py
check_cost_optimizer_issues.py
check_root_file_count.sh
check_streamlit_issues.py
ci_monitor_daemon.sh
collect_metrics.sh
comprehensive_validator.py
create_test_scaffold.py
generate_dashboard.sh
governance_session.sh
pylint_streamlit.sh
repo_health_check.sh
risk_cache.sh
should_use_pr_old.sh
test_agent_automation.sh
test_branch_operations.sh
test_merge_conflicts.sh
test_page.sh
validate_folder_structure.py
validate_streamlit_page.py
watch_tests.sh
worktree_manager.sh
```

**Observation:** Catalog has no stale entries (everything listed exists), but it is incomplete.

---

## Test Matrix (Current)

**Python library (primary):**
- Tests: `Python/tests/`
- Runner: `pytest` (see `docs/contributing/testing-strategy.md`)
- CI: `.github/workflows/python-tests.yml` (3.9–3.12, coverage gate 85%)

**Streamlit app:**
- Tests: `streamlit_app/tests/`
- Validation: `scripts/check_streamlit_issues.py` (AST scanner)
- Guides: `streamlit_app/SETUP_AND_MAINTENANCE_GUIDE.md`, `docs/streamlit-maintenance-guide.md`

**VBA:**
- Code: `VBA/Modules/`
- Tests: `VBA/Tests/` (manual/human verification noted in docs)

**Excel templates/add-ins:**
- Files in `Excel/` and `Excel/Templates/`
- Validation is mostly manual today (refer to Excel docs and guides)

---

## Workflow Entry Point Summary (Verified)

**Session start:** `scripts/start_session.py` (via `docs/agent-bootstrap.md`)

**Session end/handoff:** `scripts/end_session.py` → `scripts/update_handoff.py` → `docs/planning/next-session-brief.md`

**Git ops:** `scripts/ai_commit.sh`, `scripts/safe_push.sh`, `scripts/should_use_pr.sh`

**Release:** `scripts/release.py`, `docs/releases.md`, `scripts/verify_release.py`

---

## Consolidation Note

This file is now the **single source of research findings** for the current audit. All future updates should append here so we do not split context across multiple docs.
