# Scripts Improvement Research

**Type:** Research
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-02-10
**Last Updated:** 2026-02-10
**Related Tasks:** Post-migration cleanup (folder-structure-migration-v2)
**Abstract:** Deep analysis of 97 automation scripts — overlap detection, dead script identification, consolidation plan, and quality improvement roadmap. Targets a 42% reduction (97→55 active scripts).

---

## 1. Executive Summary

The `scripts/` directory contains **97 active scripts** (71 Python + 26 shell) totaling ~28,610 LOC in a flat folder structure. Deep analysis reveals:

- **7 scripts ready to archive immediately** (deprecated/superseded)
- **7 more candidates** for review/archival
- **4 high-overlap pairs** that should be merged
- **7 consolidation groups** that would reduce 97→55 scripts (42% reduction)
- **2 broken CI references** (archived scripts still called in workflows)
- **0 scripts using the shared `_lib/utils.py`** that already exists

---

## 2. Current Inventory

| Category | Python | Shell | Total | In CI |
|----------|--------|-------|-------|-------|
| Check/Validate | 26 | 5 | 31 | 18 |
| Generate | 6 | 1 | 7 | 2 |
| Audit | 3 | 0 | 3 | 1 |
| Test | 7 | 0 | 7 | 0 |
| Git/Commit | 1 | 8 | 9 | 5 |
| Session/Agent | 2 | 5 | 7 | 0 |
| Safe File Ops | 3 | 0 | 3 | 0 |
| Benchmark | 2 | 0 | 2 | 1 |
| Release | 3 | 0 | 3 | 1 |
| Migration | 2 | 0 | 2 | 0 |
| Governance/Metrics | 1 | 1 | 2 | 2 |
| Misc/Domain | 5 | 1 | 6 | 0 |
| Other | 10 | 5 | 15 | 3 |
| **Total** | **71** | **26** | **97** | **~30** |

### Quality Distribution

| Tier | Count | Definition |
|------|-------|------------|
| **A** (Mature CLI) | 25 | argparse, structured output, proper exit codes, CI-integrated |
| **B** (Solid Script) | 35 | argparse or clear CLI, good structure, may lack CI integration |
| **C** (Quick Hack) | 15 | No argparse, simple print-based, minimal error handling |
| **D** (Broken/Dead) | 1 | Non-functional or completely superseded |

---

## 3. High-Overlap Pairs (Merge Immediately)

### 3.1 `check_links.py` + `fix_broken_links.py` → Single `check_links.py`

Both ~320 lines, both scan markdown for broken links, both have `--fix` modes.

| Feature | check_links.py | fix_broken_links.py |
|---------|---------------|---------------------|
| Broken link scan | ✅ | ✅ |
| `--fix` mode | ✅ | ✅ |
| Migration map support | ✅ | ❌ |
| Fuzzy file-name matching | ❌ | ✅ |
| CI usage | ✅ (fast-checks, nightly) | ❌ |

**Action:** Absorb `fix_broken_links.py`'s fuzzy matching into `check_links.py --fix`. Archive `fix_broken_links.py`. Saves ~300 LOC.

### 3.2 `validate_folder_structure.py` + `check_governance_compliance.py` → Single `check_governance.py`

Both ~480 lines, both run in CI fast-checks, 60% overlap on checks.

| Feature | validate_folder_structure.py | check_governance_compliance.py |
|---------|------------------------------|-------------------------------|
| Root file count | ✅ | ✅ |
| Docs folder rules | ✅ | ✅ |
| Agent folder structure | ✅ | ✅ |
| Python lib structure | ✅ | ❌ |
| Doc metadata check | ❌ | ✅ |
| Category compliance | ❌ | ✅ |

**Action:** Merge into `check_governance.py` with flags `--structure`, `--compliance`, `--full`. Saves ~400 LOC.

### 3.3 `lint_vba.py` + `vba_validator.py` → Keep `lint_vba.py`

Both ~200 lines, both do VBA syntax checking. `lint_vba.py` has proper argparse CLI; `vba_validator.py` is a quick hack with no CLI.

**Action:** Archive `vba_validator.py`. No code changes needed.

### 3.4 `check_streamlit_issues.py` subsumes 2 scripts

The 2204-line mega-scanner has evolved through 7 phases and now covers what these do:
- `comprehensive_validator.py` (526 lines) — 4-level validation, no CI usage
- `validate_streamlit_page.py` (187 lines) — basic page validation, no CI usage

**Action:** Archive both. `check_streamlit_issues.py` is the canonical Streamlit validator.

---

## 4. Consolidation Groups (7 Merges)

### Group 1: `check_api_*.py` → `check_api.py`

Merge 3 thin scripts (56-249 lines) into one with subcommands:

```bash
check_api.py --signatures   # Streamlit→api.py call sites
check_api.py --docs          # api.__all__ → docs/reference/api.md
check_api.py --sync          # api.md ↔ api-stability.md
check_api.py --all           # Run all checks
```

### Group 2: Session Scripts → `session.py`

Merge 4 scripts into one CLI tool:

```bash
session.py start       # start_session.py
session.py end         # end_session.py
session.py handoff     # update_handoff.py
session.py check       # check_session_docs.py
```

### Group 3: Release Scripts → `release.py`

Consolidate into existing `release.py` with subcommands:

```bash
release.py bump            # bump_version.py
release.py verify          # verify_release.py
release.py check-docs      # check_release_docs.py
release.py checklist        # check_pre_release_checklist.py
```

### Group 4: VBA Tools → `vba_tools.py`

```bash
vba_tools.py lint     # lint_vba.py
vba_tools.py test     # run_vba_smoke_tests.py
```

### Group 5: Links → `check_links.py` (absorb fix_broken_links.py)

```bash
check_links.py                    # Scan only
check_links.py --fix              # Fix with fuzzy matching
check_links.py --map old new      # Migration map
```

### Group 6: Governance → `check_governance.py`

```bash
check_governance.py --structure    # Folder structure
check_governance.py --compliance   # Doc metadata + categories
check_governance.py --root-count   # Root file limit
check_governance.py --full         # All checks
```

### Group 7: Docs Checks → `check_docs.py` (already exists!)

`check_docs.py` (532L) was created to replace 4 archived scripts but **is never used in CI**. Fix CI to use it:

```bash
check_docs.py --metadata          # Doc metadata
check_docs.py --index             # Index file checks
check_docs.py --index-links       # Index link validation
check_docs.py --all               # All checks
```

### Impact Summary

| Action | Scripts Before | Scripts After | LOC Saved |
|--------|----------------|---------------|-----------|
| Merge check_api_* | 3 | 1 | ~175 |
| Merge session scripts | 4 | 1 | ~300 |
| Merge release scripts | 4 | 1 | ~200 |
| Merge VBA tools | 3 | 1 | ~200 |
| Merge links scripts | 2 | 1 | ~300 |
| Merge governance | 3 | 1 | ~400 |
| Fix CI for check_docs.py | 0 | 0 | - (fix only) |
| Archive 7 Tier-1 dead | 7 | 0 | ~1,380 |
| **Total** | **~26 merged/archived** | **-19** | **~2,955** |

**Net result:** 97 → ~55 active scripts (42% reduction)

---

## 5. Dead/Unused Scripts

### Tier 1: Archive Immediately (7 scripts)

| Script | Reason | Lines |
|--------|--------|-------|
| `test_setup.py` | 11-line one-off smoke test, no argparse, no CI | 11 |
| `vba_validator.py` | Duplicates `lint_vba.py`; no argparse, no CI | ~200 |
| `comprehensive_validator.py` | Subsumed by `check_streamlit_issues.py`; no CI | 526 |
| `validate_streamlit_page.py` | Subsumed by `check_streamlit_issues.py`; no CI | 187 |
| `copilot_setup.sh` | Subsumed by `agent_start.sh`; just sets git pager | 58 |
| `agent_setup.sh` | Deprecated in index.json — "Use agent_start.sh" | 200+ |
| `agent_preflight.sh` | Deprecated in index.json — "Use agent_start.sh" | 200+ |

### Tier 2: Review for Archival (7 scripts)

| Script | Reason | Lines |
|--------|--------|-------|
| `check_docs.py` | Created as consolidation but NEVER used anywhere | 532 |
| `test_import_3d_pipeline.py` | Feature-specific integration test, no CI | 200 |
| `test_vba_adapter.py` | Feature-specific test, no CI | 168 |
| `check_repo_hygiene.py` | 41 lines checking .DS_Store — too trivial | 41 |
| `check_python_version.py` | Not in CI, overlap with `bump_version.py` | 289 |
| `check_version_consistency.sh` | Shell version of what `bump_version.py` covers | 65 |
| `profile_streamlit_page.py` | Niche performance profiler, not in CI | 630 |

### Tier 3: Broken CI References (2 issues)

| Archived Script | Still Called By | Fix |
|-----------------|---------------|-----|
| `check_docs_index.py` | `python-tests.yml` | Replace with `check_docs.py --index` |
| `check_docs_index_links.py` | `python-tests.yml` | Replace with `check_docs.py --index-links` |

---

## 6. Quality Improvement Plan

### 6.1 Shared Library (`_lib/`) — Fix Zero Usage

`_lib/utils.py` exists with `REPO_ROOT`, `run_command`, `find_python_files` but **no script imports it**. Every script independently does:

```python
REPO_ROOT = Path(__file__).parent.parent  # 97 copies of this
```

**Action:** Create a migration checklist to gradually adopt `_lib/utils.py` in all scripts. Start with the 25 Tier-A scripts since they're already well-structured.

### 6.2 New Shared Utilities to Create

| Utility | Purpose | Scripts That Would Use It |
|---------|---------|--------------------------|
| `_lib/output.py` | Unified JSON/table/markdown output | ~15 scripts with `--json` |
| `_lib/ast_helpers.py` | Common AST parsing boilerplate | 8 scripts that walk Python ASTs |
| `_lib/markdown.py` | Markdown link/heading parsing | 4+ doc-checking scripts |

### 6.3 Logging Adoption

Only 1/97 scripts uses Python `logging` — all others use `print()`. This makes verbosity control impossible.

**Proposal:** For new scripts and consolidation merges, use `logging` with:
- `--verbose` / `--quiet` flags mapped to log levels
- Structured log format for CI consumption
- JSON output mode for automation

### 6.4 `--dry-run` Coverage

Only 11/97 scripts support `--dry-run`. All file-modifying scripts have it ✅, but validation scripts don't preview what they'd flag.

**Proposal:** For check/validate scripts, add `--fix --dry-run` patterns where applicable (e.g., `check_links.py --fix --dry-run`).

---

## 7. Missing Automation Gaps

| Gap | Description | Priority |
|-----|-------------|----------|
| **FastAPI→React contract testing** | No script validates React TS types match FastAPI Pydantic models | High |
| **React component pattern checks** | ESLint exists but no custom checks for hook/component patterns | Medium |
| **Dependency audit** | No `pip audit` / `npm audit` automation | Medium |
| **Bundle size monitoring** | No React bundle size tracking across commits | Medium |
| **E2E test runner** | No Playwright/Cypress automation | Medium |
| **Auto-changelog** | No changelog generation from conventional commits | Low |
| **API doc generation** | `generate_api_manifest.py` does JSON but no human-readable auto-docs | Low |

---

## 8. Proposed `scripts/` Structure

If folder reorganization is pursued (currently all 97 in flat root):

```
scripts/
├── _lib/                           # Shared utilities
│   ├── utils.py                    # Repo root, subprocess, file finders
│   ├── output.py                   # JSON/table/markdown output
│   ├── ast_helpers.py              # AST parsing helpers
│   └── markdown.py                 # Markdown parsing helpers
│
├── core/                           # Core workflow (daily use)
│   ├── ai_commit.sh               # Commit + push
│   ├── agent_start.sh             # Session start
│   ├── should_use_pr.sh           # PR decision
│   ├── recover_git_state.sh       # Emergency recovery
│   ├── session.py                  # start/end/handoff/check
│   ├── create_task_pr.sh          # PR creation
│   └── finish_task_pr.sh          # PR completion
│
├── validate/                       # Validation & checks
│   ├── check_api.py               # API signatures/docs/sync
│   ├── check_links.py             # Link scan + fix
│   ├── check_governance.py        # Structure/compliance/root-count
│   ├── check_streamlit_issues.py  # Streamlit mega-scanner
│   ├── check_docs.py              # Doc metadata/index/links
│   ├── check_architecture_boundaries.py
│   ├── check_circular_imports.py
│   ├── check_type_annotations.py
│   ├── check_performance_issues.py
│   ├── check_fragment_violations.py
│   ├── validate_api_contracts.py
│   ├── validate_imports.py
│   └── validate_session_state.py
│
├── generate/                       # Code/doc generation
│   ├── generate_enhanced_index.py
│   ├── generate_docs_index.py
│   ├── generate_client_sdks.py
│   └── generate_streamlit_page.py
│
├── migrate/                        # File migration tools
│   ├── migrate_python_module.py
│   ├── migrate_react_component.py
│   ├── safe_file_move.py
│   ├── safe_file_delete.py
│   └── create_doc.py
│
├── release/                        # Release management
│   └── release.py                  # bump/verify/check/checklist
│
├── audit/                          # Audit & governance
│   ├── audit_readiness_report.py
│   ├── governance_health_score.py
│   └── collect_metrics.sh
│
├── domain/                         # Domain-specific tools
│   ├── benchmark_api.py
│   ├── discover_api_signatures.py
│   ├── dxf_render.py
│   ├── vba_tools.py               # lint + test
│   └── find_automation.py
│
├── git-hooks/                      # Git hook scripts
│   ├── check_not_main.sh
│   ├── check_unfinished_merge.sh
│   ├── install_git_hooks.sh
│   └── pre_commit_check.sh
│
├── ci/                             # CI-only scripts
│   ├── ci_local.sh
│   └── collect_diagnostics.py
│
├── test/                           # Test utilities
│   ├── create_test_scaffold.py
│   ├── update_test_stats.py
│   ├── external_cli_test.py
│   └── test_api_parity.py
│
├── _archive/                       # Archived scripts
│   └── (14+ scripts moved here)
│
├── automation-map.json
└── index.json
```

**Trade-offs:**
- **Pro:** Clear discoverability, logical grouping, easier for new agents
- **Con:** Breaks ALL existing references to `scripts/foo.py` (docs, CI, CLAUDE.md, bootstrap)
- **Risk:** Medium — requires updating ~50+ references across docs and CI
- **Recommendation:** Do this AFTER consolidation merges, as a separate phase

---

## 9. Prioritized Action Plan

### Phase 1: Quick Wins (1 session, low risk) — ✅ DONE (Session 89, PR #428)

1. ✅ **Archive 7 Tier-1 dead scripts** → Moved to `scripts/_archive/`
2. ✅ **Fix 2 broken CI references** → `check_docs_index.py` → `check_docs.py --index`
3. ✅ **Archive `vba_validator.py`** → `lint_vba.py` is the canonical VBA linter

### Phase 2: Consolidation Merges (2-3 sessions, medium risk) — 🟡 3 of 5 done

4. ✅ **Merge `check_links.py` + `fix_broken_links.py`** → Single script with `--fix` + fuzzy matching
5. ✅ **Merge `validate_folder_structure.py` + `check_governance_compliance.py`** → `check_governance.py`
6. ✅ **Merge 3 `check_api_*.py`** → `check_api.py` with `--signatures`, `--docs`, `--sync`
7. **Merge session scripts** → `session.py` CLI (next session)
8. **Merge release scripts** → Expand existing `release.py` (next session)

### Phase 3: Infrastructure (1-2 sessions, medium risk)

9. **Make scripts import `_lib/utils.py`** → Start with 10 most-used scripts
10. **Create `_lib/output.py`** → Unified JSON/table output
11. **Create `_lib/ast_helpers.py`** → Shared AST parsing

### Phase 4: Folder Reorganization (1 session, high risk)

12. **Move scripts into categorized subdirs** → Update all references
13. **Regenerate indexes** → `automation-map.json`, `index.json`

### Phase 5: New Automation (ongoing)

14. **FastAPI→React contract validator** → Pydantic ↔ TypeScript type sync
15. **Bundle size monitor** → Track React build output per commit
16. **Dependency audit automation** → `pip audit` + `npm audit` in CI

---

## 10. Metrics & Success Criteria

| Metric | Before | Current | Target |
|--------|--------|---------|--------|
| Active scripts | 97 | ~85 | ~55 |
| In CI | ~30 (31%) | ~30 (35%) | ~35 (64%) |
| Using `_lib/` | 0 (0%) | 0 (0%) | 30+ (55%) |
| With argparse | 55 (77% of Python) | 55 | 50+ (90%+) |
| With logging | 1 (1%) | 1 | 20+ (36%) |
| Broken CI refs | 2 | 0 ✅ | 0 |
| High-overlap pairs | 4 | 1 | 0 |
| Dead scripts | 7-14 | 0 ✅ | 0 |

---

*This document follows the metadata standard defined in copilot-instructions.md.*
