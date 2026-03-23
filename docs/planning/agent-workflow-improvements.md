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

---

## Scripts Inventory & Consolidation Plan

### Current State: 81 Scripts (52 Python + 29 Shell)

**`_lib/` adoption:** 11 of 52 Python scripts use shared `_lib/` utilities. 41 still have standalone helpers.

### Tier Classification

#### Tier 0 — Daily Use (5 scripts, NEVER touch without tests)

| Script | Type | Size | Purpose |
|--------|------|------|---------|
| `ai_commit.sh` | Shell | 5KB | Every commit — stages, PR check, delegates to safe_push |
| `agent_start.sh` | Shell | 14KB | Every session — hooks, env, preflight, session.py start |
| `session.py` | Python | 39KB | Session lifecycle: start/end/handoff/check/summary/sync |
| `safe_push.sh` | Shell | 15KB | Conflict-minimized push (parallel fetch, amend, sync) |
| `should_use_pr.sh` | Shell | 16KB | Analyzes changes and recommends PR vs direct commit |

#### Tier 1 — Weekly Use (12 scripts)

| Script | Type | Size | Purpose |
|--------|------|------|---------|
| `sync_numbers.py` | Python | 14KB | Sync stale counts across docs (NEW) |
| `check_governance.py` | Python | 34KB | Folder structure + compliance validation |
| `check_streamlit.py` | Python | 95KB | All Streamlit validation (mega-script) |
| `check_links.py` | Python | 12KB | Broken internal link checker |
| `check_api.py` | Python | 15KB | API signature/docs validation |
| `check_architecture_boundaries.py` | Python | 15KB | 4-layer import enforcement |
| `discover_api_signatures.py` | Python | 11KB | Runtime function introspection |
| `find_automation.py` | Python | 5KB | Search automation-map.json |
| `generate_enhanced_index.py` | Python | 24KB | Generate index.json + index.md |
| `create_task_pr.sh` | Shell | 3KB | Create task branch + PR |
| `finish_task_pr.sh` | Shell | 9KB | Complete PR workflow |
| `recover_git_state.sh` | Shell | 5KB | Git incident recovery |

#### Tier 2 — Occasional Use (20 scripts)

| Script | Type | Size | Purpose |
|--------|------|------|---------|
| `validate_api_contracts.py` | Python | 21KB | API contract testing (CI) |
| `validate_imports.py` | Python | 9KB | Import validation after migration |
| `validate_schema_snapshots.py` | Python | 7KB | Schema snapshot validation |
| `validate_session_state.py` | Python | 14KB | Session docs consistency |
| `validate_git_state.sh` | Shell | 8KB | Git state pre-check |
| `check_circular_imports.py` | Python | 15KB | Circular import detector |
| `check_fastapi_issues.py` | Python | 15KB | FastAPI-specific validation |
| `check_type_annotations.py` | Python | 18KB | Type annotation coverage |
| `check_docs.py` | Python | 20KB | Doc index/link validation |
| `check_cost_optimizer_issues.py` | Python | 8KB | Cost optimizer bug checks |
| `check_ui_duplication.py` | Python | 20KB | UI code duplication scanner |
| `check_performance_issues.py` | Python | 19KB | Performance anti-pattern detector |
| `safe_file_move.py` | Python | 16KB | Move files + update 870+ links |
| `safe_file_delete.py` | Python | 11KB | Delete files with ref checking |
| `migrate_python_module.py` | Python | 17KB | Move Python module + imports |
| `migrate_react_component.py` | Python | 17KB | Move React component + imports |
| `batch_migrate_runner.py` | Python | 14KB | Batch migration with rollback |
| `release.py` | Python | 13KB | Release verification/management |
| `bump_version.py` | Python | 13KB | Version bumping (pyproject.toml) |
| `collect_diagnostics.py` | Python | 3KB | Debug bundle collector |

#### Tier 3 — Rarely Used / Supporting (22 scripts)

| Script | Type | Size | Purpose |
|--------|------|------|---------|
| `audit_error_handling.py` | Python | 10KB | Error handling audit |
| `audit_input_validation.py` | Python | 12KB | Input validation audit |
| `audit_readiness_report.py` | Python | 27KB | Full readiness assessment |
| `benchmark_api.py` | Python | 25KB | API performance benchmarks |
| `check_docker_config.py` | Python | 8KB | Docker configuration validation |
| `check_python_version.py` | Python | 6KB | Python version enforcement |
| `cleanup_stale_branches.py` | Python | 5KB | Branch cleanup |
| `create_doc.py` | Python | 8KB | Doc creation with metadata |
| `create_test_scaffold.py` | Python | 13KB | Test file generator |
| `external_cli_test.py` | Python | 11KB | External CLI smoke test |
| `generate_api_manifest.py` | Python | 4KB | API manifest generation |
| `generate_client_sdks.py` | Python | 14KB | Client SDK generation |
| `generate_docs_index.py` | Python | 7KB | Docs JSON index |
| `generate_streamlit_page.py` | Python | 12KB | Streamlit page generator |
| `governance_health_score.py` | Python | 17KB | Governance health metrics |
| `lint_vba.py` | Python | 7KB | VBA linting |
| `profile_streamlit_page.py` | Python | 18KB | Streamlit page profiler |
| `test_api_parity.py` | Python | 14KB | API parity testing |
| `test_import_3d_pipeline.py` | Python | 6KB | 3D import pipeline test |
| `test_vba_adapter.py` | Python | 6KB | VBA adapter testing |
| `update_test_stats.py` | Python | 6KB | Test statistics updater |
| `dxf_render.py` | Python | 3KB | DXF rendering (status unclear) |

#### Tier 4 — Small Utility / Pre-commit (22 scripts)

| Script | Type | Size | Purpose |
|--------|------|------|---------|
| `check_cli_reference.py` | Python | 1KB | CLI reference validation |
| `check_doc_versions.py` | Python | 2KB | Doc version drift (pre-commit) |
| `check_next_session_brief_length.py` | Python | 1KB | Brief length check |
| `check_repo_hygiene.py` | Python | 1KB | Repo hygiene (pre-commit) |
| `check_scripts_index.py` | Python | 2KB | Scripts index.json check |
| `check_tasks_format.py` | Python | 5KB | TASKS.md format validation |
| `check_not_main.sh` | Shell | 0.4KB | Branch check guard |
| `check_root_file_count.sh` | Shell | 2KB | Root file sprawl check |
| `check_unfinished_merge.sh` | Shell | 1KB | Merge state check (pre-commit) |
| `check_version_consistency.sh` | Shell | 3KB | Version string consistency |
| `check_wip_limits.sh` | Shell | 3KB | WIP limit enforcement |
| `ci_local.sh` | Shell | 1KB | Local CI runner |
| `pre_commit_check.sh` | Shell | 1KB | Pre-flight checks |
| `agent_mistakes_report.sh` | Shell | 4KB | Common mistakes reminder |
| `archive_old_files.sh` | Shell | 5KB | Auto-archive old docs |
| `collect_metrics.sh` | Shell | 9KB | Metrics collection |
| `generate_all_indexes.sh` | Shell | 1KB | Run generate_enhanced_index on all |
| `install_git_hooks.sh` | Shell | 4KB | Install git hooks |
| `launch_streamlit.sh` | Shell | 11KB | Streamlit launcher |
| `run_vba_smoke_tests.py` | Python | 4KB | VBA smoke tests |
| `repo_health_check.sh` | Shell | 1KB | Quick health check |
| `watch_tests.sh` | Shell | 3KB | Test watch mode |

### Issues Found

#### 1. Phantom Script References in `agent_start.sh`

7 scripts referenced but don't exist (consolidated into other scripts):

| Missing Reference | Was Merged Into |
|-------------------|----------------|
| `agent_preflight.sh` | `agent_start.sh` (inlined) |
| `agent_setup.sh` | `agent_start.sh` (inlined) |
| `copilot_setup.sh` | `agent_start.sh` (inlined) |
| `git_ops.sh` | `ai_commit.sh` + `recover_git_state.sh` |
| `worktree_manager.sh` | Removed (worktree support embedded) |
| `validate_folder_structure.py` | `check_governance.py --structure` |
| `check_governance_compliance.py` | `check_governance.py --compliance` |

**Action:** Clean up `agent_start.sh` to remove dead references.

#### 2. Low `_lib/` Adoption

Only 11/52 Python scripts import from `_lib/`. The remaining 41 duplicate patterns for:
- Subprocess execution (each re-implements `subprocess.run` wrappers)
- AST parsing (many re-implement `ast.parse` with try/except)
- JSON/table output (many re-implement formatting)
- Repository root resolution (each does `Path(__file__).parent.parent`)

**Action:** Prioritize migrating the 20 Tier 2-3 scripts that would benefit most.

#### 3. `check_streamlit.py` is 95KB

This is the largest script by far. It consolidates 4 former scripts but could benefit from
splitting subcommands into separate modules under `scripts/_streamlit/`.

**Action:** Not urgent — works fine as-is with subcommand flags.

#### 4. `validate_session_state.py` is a Streamlit Tool

Despite the name suggesting overlap with `session.py check`, this script validates
**Streamlit `st.session_state` usage** (uninitialized keys, missing defaults, type
inconsistencies). It is NOT related to session document management. No action needed.

### Consolidation Roadmap

#### Phase 4a — Quick Wins (do now)

- [x] Clean phantom references in `agent_start.sh` (7 dead refs → inlined)
- [ ] Clarify `dxf_render.py` status (active vs deprecated)
- [ ] Verify `sync_numbers.py` covers `agent-bootstrap.md` too

#### Phase 4b — `_lib/` Migration (v0.20)

Migrate 10 more scripts to use `_lib/utils.py` + `_lib/output.py`:

| Priority | Script | Pattern to Replace |
|----------|--------|--------------------|
| 1 | `check_circular_imports.py` | AST parsing, REPO_ROOT |
| 2 | `check_fastapi_issues.py` | AST parsing, JSON output |
| 3 | `check_type_annotations.py` | AST parsing, table output |
| 4 | `check_ui_duplication.py` | AST parsing, table output |
| 5 | `check_performance_issues.py` | AST parsing, REPO_ROOT |
| 6 | `check_cost_optimizer_issues.py` | REPO_ROOT, subprocess |
| 7 | `safe_file_move.py` | REPO_ROOT, subprocess |
| 8 | `safe_file_delete.py` | REPO_ROOT, subprocess |
| 9 | `validate_api_contracts.py` | AST, imports, output |
| 10 | `benchmark_api.py` | REPO_ROOT, JSON output |

#### Phase 4c — Targeted Merges (v0.21)

| Merge Target | Scripts to Absorb | Rationale |
|-------------|-------------------|-----------|
| `audit.py` | `audit_error_handling.py` + `audit_input_validation.py` + `audit_readiness_report.py` | All 3 are audit subcommands |
| `generate.py` | `generate_docs_index.py` + `generate_api_manifest.py` + `generate_all_indexes.sh` | All generation tools |
| `check_docker_config.py` → `check_governance.py --docker` | Absorb into governance | Docker check is a governance concern |

### Next Steps for "Simplify Agent Documentation Work"

#### Already Done (Session 91)
- [x] `sync_numbers.py` — auto-sync counts across 4 doc files
- [x] `session.py summary` — auto-generate session summary from git log
- [x] `session.py sync` — convenience wrapper for sync_numbers
- [x] Bootstrap docs updated with new session-end workflow

#### Next Up (Session 92)
- [ ] **Phantom cleanup** — remove 7 dead script references from `agent_start.sh`
- [ ] **`validate_session_state.py` deprecation** — redirect to `session.py check`
- [ ] **Inventory validation** — verify sync_numbers catches `agent-bootstrap.md` too
- [ ] **Session number auto-detect** — `summary --write` should pull session # from next-session-brief.md
- [ ] **Run `sync_numbers.py` at commit time** — add `--quick` mode to ai_commit.sh post-commit hook

#### Future Sessions
- [ ] Migrate 10 scripts to `_lib/` (Phase 4b)
- [ ] Merge 3 audit scripts into `audit.py` (Phase 4c)
- [ ] Add `sync_numbers` to GitHub Actions CI
- [ ] Auto-detect when bootstrap docs need refresh (new hooks/routes added but docs not updated)
