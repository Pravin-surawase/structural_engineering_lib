---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# Unified CLI Upgrade Plan

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-03-24
**Last Updated:** 2026-04-04

---

## Problem

Agents face **85 active scripts** and waste time discovering, learning, and calling the right ones. Even experienced agents frequently:

- Call archived scripts (46 stale references found in Session 93)
- Duplicate functionality that already exists in hooks
- Run individual check scripts instead of the consolidated versions
- Skip validation because they don't know which scripts to run
- Can't tell which scripts are infrastructure (called by other scripts) vs standalone

The consolidation from 163 → 85 helped, but the **interface remained the same**: a flat directory of 85 scripts with no clear hierarchy.

---

## 1. Full Script Inventory (85 active)

### 1.1 Dependency Graph — Who Calls Whom

These are the verified call chains (subprocess, source, or direct invocation):

```
agent_start.sh ────→ install_git_hooks.sh
                   → session.py start

ai_commit.sh ──────→ should_use_pr.sh          (PR requirement check)
                   → safe_push.sh              (actual commit + push)
                   → sync_numbers.py           (post-commit stale-number warning)
                   → check_links.py            (post-commit broken-link warning)

finish_task_pr.sh ─→ gh CLI                    (create PR, poll CI)
                   → session.py handoff        (optional session handoff)

session.py ────────→ sync_numbers.py           (sync subcommand)
                   → check_links.py            (end checks)
                   → generate_enhanced_index.py (end checks)
                   → collect_diagnostics.py    (error hints, not direct)
                   → find_automation.py        (output hints)

release.py ────────→ bump_version.py           (version bump subprocess)

check_doc_versions.py → bump_version.py        (thin wrapper, --check-docs)
ci_local.sh ───────→ check_doc_versions.py     (version sync in CI)
check_version_consistency.sh → check_doc_versions.py

audit_readiness_report.py → check_api.py, check_governance.py, check_docs.py,
                            check_streamlit.py, check_circular_imports.py,
                            check_type_annotations.py, check_links.py,
                            should_use_pr.sh, ai_commit.sh

governance_health_score.py → check_links.py    (subprocess)

generate_all_indexes.sh → generate_enhanced_index.py
validate_api_contracts.py → generate_api_manifest.py (hints)

safe_file_move.py ─→ ai_commit.sh              (optional auto-commit)
safe_file_delete.py → ai_commit.sh             (optional auto-commit)
migrate_python_module.py → ai_commit.sh        (optional auto-commit)
migrate_react_component.py → ai_commit.sh      (optional auto-commit)
archive_old_files.sh → update_archive_index.py (if it exists)

create_task_pr.sh ─→ git commands only
should_use_pr.sh ──→ git commands only
safe_push.sh ──────→ git commands only
```

### 1.2 Script Layers

**Layer 1 — ENTRY POINTS (5 scripts agents call directly):**
| Script | Purpose | Frequency |
|--------|---------|-----------|
| `agent_start.sh` | Begin session | Every session start |
| `ai_commit.sh` | Commit + push | Every commit |
| `create_task_pr.sh` | Start PR branch | Per-task |
| `finish_task_pr.sh` | Ship PR | Per-task |
| `session.py` | End session / sync / summary | Every session end |

**Layer 2 — INFRASTRUCTURE (14 scripts called BY other scripts, rarely called directly):**
| Script | Called By | Purpose |
|--------|-----------|---------|
| `safe_push.sh` | ai_commit.sh | Conflict-proof push workflow |
| `should_use_pr.sh` | ai_commit.sh | PR requirement analysis |
| `sync_numbers.py` | ai_commit.sh, session.py | Doc number freshness |
| `check_links.py` | ai_commit.sh, session.py, governance_health_score.py | Broken link detection |
| `install_git_hooks.sh` | agent_start.sh | Git hook installation |
| `generate_enhanced_index.py` | session.py, generate_all_indexes.sh | Folder index generation |
| `bump_version.py` | release.py, check_doc_versions.py | Version management |
| `check_doc_versions.py` | ci_local.sh, check_version_consistency.sh | Version drift wrapper |
| `generate_api_manifest.py` | validate_api_contracts.py (hints) | API symbol manifest |
| `check_api.py` | audit_readiness_report.py | API validation |
| `check_governance.py` | audit_readiness_report.py | Governance validation |
| `check_docs.py` | audit_readiness_report.py | Doc validation |
| `check_circular_imports.py` | audit_readiness_report.py | Import cycle detection |
| `check_type_annotations.py` | audit_readiness_report.py | Type hint coverage |

**Layer 3 — STANDALONE TOOLS (66 scripts, agents run ad-hoc):**

Subdivided by purpose:

#### Validation (25 scripts)
| Script | Lines | Target | Pre-commit? |
|--------|-------|--------|-------------|
| `check_architecture_boundaries.py` | 522 | Layer violation detection | No |
| `check_bootstrap_freshness.py` | 261 | Bootstrap doc staleness | No |
| `check_cli_reference.py` | 45 | CLI docs sync | Yes |
| `check_cost_optimizer_issues.py` | 200 | Cost optimizer anti-patterns | Yes |
| `check_docker_config.py` | 200 | Docker config validation | No |
| `check_fastapi_issues.py` | 419 | FastAPI anti-patterns | No |
| `check_instruction_drift.py` | 211 | Platform instruction sync | No |
| `check_next_session_brief_length.py` | 28 | Brief length cap | Yes |
| `check_openapi_snapshot.py` | 206 | OpenAPI drift detection | No |
| `check_performance_issues.py` | 594 | **ARCHIVE** — Streamlit-specific | Yes |
| `check_python_version.py` | 200 | Python version consistency | Yes |
| `check_repo_hygiene.py` | 41 | .DS_Store/.coverage artifacts | Yes |
| `check_scripts_index.py` | 69 | scripts/index.json sync | Yes |
| `check_streamlit.py` | 2366 | Comprehensive Streamlit scanner | Yes |
| `check_tasks_format.py` | 157 | TASKS.md structure | Yes |
| `check_ui_duplication.py` | 616 | **ARCHIVE** — Streamlit-specific | No |
| `check_wip_limits.sh` | 76 | WIP limits | No |
| `validate_api_contracts.py` | 607 | FastAPI contract validation | No |
| `validate_imports.py` | 200 | Broken import detection | No |
| `validate_schema_snapshots.py` | 255 | Pydantic schema drift | No |
| `validate_script_refs.py` | 166 | Stale archive references | No |
| `validate_session_state.py` | 405 | **ARCHIVE** — Streamlit session | No |
| `check_not_main.sh` | 14 | Prevent main commits | Hook |
| `check_root_file_count.sh` | 50 | Root file limit | Hook |
| `check_unfinished_merge.sh` | 29 | Merge conflict guard | Hook |

#### Audit / Quality (6 scripts)
| Script | Lines | Purpose |
|--------|-------|---------|
| `audit_error_handling.py` | 370 | Error handling coverage audit |
| `audit_input_validation.py` | 360 | Input validation coverage audit |
| `audit_readiness_report.py` | 813 | Master audit orchestrator (6+ sub-scripts) |
| `governance_health_score.py` | 310 | Weighted governance score |
| `collect_diagnostics.py` | 121 | System diagnostics bundle |
| `repo_health_check.sh` | 30 | Repo size/file stats |

#### Testing (7 scripts)
| Script | Lines | Purpose |
|--------|-------|---------|
| `ci_local.sh` | 40 | Full local CI run |
| `external_cli_test.py` | 395 | CLI smoke test |
| `test_api_parity.py` | 441 | FastAPI ↔ library parity |
| `test_import_3d_pipeline.py` | 200 | Import→Design→3D integration |
| `test_vba_adapter.py` | 150 | VBA adapter tests |
| `update_test_stats.py` | 210 | Pytest stats → test_stats.json |
| `benchmark_api.py` | 455 | API endpoint benchmarks |

#### Generation (5 scripts)
| Script | Lines | Purpose |
|--------|-------|---------|
| `generate_all_indexes.sh` | 50 | Shell wrapper for all indexes |
| `generate_client_sdks.py` | 525 | TypeScript/Python SDK generation |
| `generate_docs_index.py` | 244 | docs-index.json from markdown scan |
| `generate_streamlit_page.py` | 474 | **ARCHIVE** — V3 is React |
| `create_test_scaffold.py` | 422 | Auto-generate pytest templates |

#### Git Operations (5 scripts)
| Script | Lines | Purpose |
|--------|-------|---------|
| `check_version_consistency.sh` | 65 | Version sync across files |
| `cleanup_stale_branches.py` | 150 | Delete merged feature branches |
| `pre_commit_check.sh` | 35 | Whitespace/conflict pre-flight |
| `recover_git_state.sh` | 200 | Git recovery automation |
| `validate_git_state.sh` | 100 | Git state validation |

#### Release (1 script — bump_version is infrastructure, release.py is entry)
| Script | Lines | Purpose |
|--------|-------|---------|
| `release.py` | 368 | Release CLI: bump/verify/checklist |

#### Utility (11 scripts)
| Script | Lines | Purpose |
|--------|-------|---------|
| `create_doc.py` | 260 | Create doc with metadata header |
| `discover_api_signatures.py` | 250 | API function param inspection |
| `dxf_render.py` | 300 | DXF file rendering |
| `find_automation.py` | 173 | Fuzzy script search |
| `safe_file_move.py` | 280 | Safe file move + link update |
| `safe_file_delete.py` | 210 | Safe file delete + link update |
| `migrate_python_module.py` | 410 | Python module migration |
| `migrate_react_component.py` | 387 | React component migration |
| `lint_vba.py` | 200 | VBA linter |
| `run_vba_smoke_tests.py` | 100 | VBA smoke tests (macOS only) |
| `collect_metrics.sh` | 50 | Sparse metrics collection |

#### Maintenance (2 scripts)
| Script | Lines | Purpose |
|--------|-------|---------|
| `archive_old_files.sh` | 150 | Auto-archive old docs/_active files |
| `agent_mistakes_report.sh` | 100 | Agent mistake tracking |

#### Streamlit-specific (2 scripts — beyond check_streamlit.py)
| Script | Lines | Purpose |
|--------|-------|---------|
| `launch_streamlit.sh` | 50 | **ARCHIVE** — V3 is React |
| `profile_streamlit_page.py` | 630 | **ARCHIVE** — Streamlit profiler |

#### Meta-validation (1 script)
| Script | Lines | Purpose |
|--------|-------|---------|
| `watch_tests.sh` | 50 | pytest file watcher |

---

## 2. Overlaps & Consolidation Opportunities

### 2.1 Confirmed Overlaps (fix now)

| Overlap | Scripts | Action |
|---------|---------|--------|
| **Doc number syncing** | `sync_numbers.py` vs `update_test_stats.py` | `update_test_stats.py` counts pytest stats; `sync_numbers.py` does the same PLUS 8 other metrics. **Absorb `update_test_stats.py` into `sync_numbers.py`** — add `--test-only` flag if needed |
| **OpenAPI drift** | `check_openapi_snapshot.py` vs `validate_api_contracts.py` | `validate_api_contracts.py` is a superset (does everything snapshot does + schema validation + manifest comparison). **Absorb `check_openapi_snapshot.py` into `validate_api_contracts.py`** |
| **Version checking** | `check_doc_versions.py` → `bump_version.py --check-docs` | `check_doc_versions.py` is a 69-line thin wrapper. **Keep as-is** — it's the pre-commit entry point that CI/hooks call. The indirection is intentional. |

### 2.2 Near-Overlaps (leave separate, acknowledge)

| Scripts | Why Keep Separate |
|---------|-------------------|
| `check_bootstrap_freshness.py` vs `sync_numbers.py` | Different angles: freshness checks for missing items, sync_numbers checks for stale counts. Complementary. |
| `validate_schema_snapshots.py` vs `validate_api_contracts.py` | Snapshots does Pydantic model comparison; contracts does OpenAPI/FastAPI. Different scopes. |
| `audit_readiness_report.py` vs `governance_health_score.py` | Audit generates evidence; score generates a weighted metric. Both legitimate. |

### 2.3 Archive Candidates (7 scripts → 85 → 78)

| Script | Lines | Reason |
|--------|-------|--------|
| `check_performance_issues.py` | 594 | Streamlit-specific, V3 is React |
| `check_ui_duplication.py` | 616 | Streamlit-specific, V3 is React |
| `validate_session_state.py` | 405 | Streamlit session state, V3 is React |
| `generate_streamlit_page.py` | 474 | Streamlit scaffolder, V3 is React |
| `profile_streamlit_page.py` | 630 | Streamlit profiler, V3 is React |
| `launch_streamlit.sh` | 50 | Streamlit launcher, V3 is React |
| `check_cost_optimizer_issues.py` | 200 | Streamlit-specific patterns, nearing obsolete |

After archive + 2 absorptions: **85 → 76 scripts**

---

## 3. Vision: Unified CLI

An AI agent should only need to know **6 commands** for 95% of their work:

```bash
./run.sh check              # "Is everything healthy?"
./run.sh commit "message"   # "Save my work"
./run.sh pr create|finish   # "Ship this for review"
./run.sh session start|end  # "Begin/wrap up work"
./run.sh find "topic"       # "Where is the right script?"
./run.sh release patch|minor # "Cut a release"
```

Each entry point orchestrates the right sub-scripts internally. Agents never need to know about `check_governance.py`, `check_api.py`, etc. — they just run `./run.sh check` and get a unified report.

---

## 4. Architecture

### 4.1 `./run.sh` — Single CLI Entry Point

```
./run.sh <command> [subcommand] [options]

Commands:
  check     Run validation checks (all, or by category)
  commit    Stage, commit, and push safely
  pr        Create/finish pull requests
  session   Start/end agent sessions
  find      Discover scripts and API signatures
  release   Version bumps and release management
  audit     Run readiness/governance audit
  test      Run test suites (pytest, parity, VBA, CLI)
  generate  Generate indexes, SDKs, manifests
```

Under the hood, `run.sh` dispatches to the existing scripts — no rewrite needed. It's a **thin orchestration layer** that calls the same proven scripts.

### 4.2 Command: `./run.sh check`

```bash
./run.sh check                    # Run ALL checks (30+ scripts, parallel by category)
./run.sh check --quick            # Fast subset: links, imports, types, hygiene (<30s)
./run.sh check --category api     # API checks only
./run.sh check --category docs    # Doc checks only
./run.sh check --category arch    # Architecture checks only
./run.sh check --fix              # Auto-fix what's fixable (sync_numbers, links)
./run.sh check --json             # Machine-readable output for CI
./run.sh check --pre-commit       # Only pre-commit-registered checks
```

**Category → Script mapping:**

| Category | Scripts (run in parallel within category) | Total |
|----------|------------------------------------------|-------|
| `api` | `check_api.py --all`, `validate_api_contracts.py`, `generate_api_manifest.py --check` | 3 |
| `docs` | `check_docs.py --all`, `check_links.py`, `check_doc_versions.py`, `check_cli_reference.py`, `check_tasks_format.py`, `check_next_session_brief_length.py`, `check_scripts_index.py` | 7 |
| `arch` | `check_architecture_boundaries.py`, `check_circular_imports.py`, `validate_imports.py` | 3 |
| `governance` | `check_governance.py --full`, `check_repo_hygiene.py`, `check_python_version.py`, `validate_schema_snapshots.py` | 4 |
| `fastapi` | `check_fastapi_issues.py`, `check_docker_config.py`, `validate_api_contracts.py` | 3 |
| `streamlit` | `check_streamlit.py --all-pages` | 1 |
| `git` | `validate_git_state.sh`, `check_unfinished_merge.sh`, `check_version_consistency.sh` | 3 |
| `stale` | `validate_script_refs.py`, `check_instruction_drift.py`, `check_bootstrap_freshness.py` | 3 |
| `code` | `check_type_annotations.py` | 1 |

**Unified output:**
```
━━━ Check Report ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  API:          ✅ 3/3 passed
  Docs:         ⚠️  6/7 passed (1 warning)
  Architecture: ✅ 3/3 passed
  Governance:   ✅ 4/4 passed
  FastAPI:      ✅ 3/3 passed
  Git:          ✅ 3/3 passed
  Stale:        ✅ 3/3 passed
  Code:         ✅ 1/1 passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total: 27/28 passed, 1 warning
  Auto-fixable: 1 (run with --fix)
```

### 4.3 Command: `./run.sh commit "message"`

Delegates to `ai_commit.sh` with all its existing safety:
- Stages all changes
- Checks PR requirement (via `should_use_pr.sh`)
- Pushes safely (via `safe_push.sh`)
- Post-commit sync warning (via `sync_numbers.py`)
- Post-commit link check (via `check_links.py`)

```bash
./run.sh commit "feat: add beam optimization"    # Standard commit
./run.sh commit "fix: stirrup spacing" --force   # Skip PR check
```

### 4.4 Command: `./run.sh pr`

```bash
./run.sh pr create TASK-XXX "description"    # → create_task_pr.sh
./run.sh pr finish                           # → finish_task_pr.sh (wait mode)
./run.sh pr status                           # → gh pr view --web
```

### 4.5 Command: `./run.sh session`

```bash
./run.sh session start          # → agent_start.sh --quick
./run.sh session end            # → session.py end --fix
./run.sh session summary        # → session.py summary --write
./run.sh session sync           # → session.py sync --fix
./run.sh session check          # → session.py check
```

### 4.6 Command: `./run.sh find`

```bash
./run.sh find "commit code"              # → find_automation.py "commit code"
./run.sh find --api design_beam_is456    # → discover_api_signatures.py design_beam_is456
./run.sh find --list                     # → find_automation.py --list
```

### 4.7 Command: `./run.sh release`

```bash
./run.sh release patch          # → release.py run patch
./run.sh release minor          # → release.py run minor
./run.sh release verify         # → release.py verify
./run.sh release check-docs     # → release.py check-docs
```

### 4.8 Command: `./run.sh audit`

```bash
./run.sh audit                  # → audit_readiness_report.py
./run.sh audit --score          # → governance_health_score.py
./run.sh audit --errors         # → audit_error_handling.py
./run.sh audit --inputs         # → audit_input_validation.py
./run.sh audit --diagnostics    # → collect_diagnostics.py
```

### 4.9 Command: `./run.sh test`

```bash
./run.sh test                   # → .venv/bin/pytest Python/tests/ -v
./run.sh test --parity          # → test_api_parity.py
./run.sh test --pipeline        # → test_import_3d_pipeline.py
./run.sh test --vba             # → run_vba_smoke_tests.py + test_vba_adapter.py
./run.sh test --cli             # → external_cli_test.py
./run.sh test --benchmark       # → benchmark_api.py
./run.sh test --ci              # → ci_local.sh (full CI)
./run.sh test --stats           # → update_test_stats.py (or sync_numbers.py after merge)
```

### 4.10 Command: `./run.sh generate`

```bash
./run.sh generate indexes       # → generate_all_indexes.sh
./run.sh generate sdk           # → generate_client_sdks.py
./run.sh generate manifest      # → generate_api_manifest.py
./run.sh generate docs-index    # → generate_docs_index.py
./run.sh generate scaffold <mod> # → create_test_scaffold.py <module>
```

---

## 5. `run.sh` Script Mapping (Complete)

Every active script mapped to exactly one `run.sh` subcommand:

### Directly exposed via `./run.sh` subcommands (50)
| Script | `./run.sh` Command |
|--------|--------------------|
| `agent_start.sh` | `session start` |
| `session.py` | `session end/summary/sync/check` |
| `ai_commit.sh` | `commit` |
| `create_task_pr.sh` | `pr create` |
| `finish_task_pr.sh` | `pr finish` |
| `find_automation.py` | `find` |
| `discover_api_signatures.py` | `find --api` |
| `release.py` | `release` |
| `check_api.py` | `check --category api` |
| `check_architecture_boundaries.py` | `check --category arch` |
| `check_bootstrap_freshness.py` | `check --category stale` |
| `check_circular_imports.py` | `check --category arch` |
| `check_cli_reference.py` | `check --category docs` |
| `check_doc_versions.py` | `check --category docs` |
| `check_docker_config.py` | `check --category fastapi` |
| `check_docs.py` | `check --category docs` |
| `check_fastapi_issues.py` | `check --category fastapi` |
| `check_governance.py` | `check --category governance` |
| `check_instruction_drift.py` | `check --category stale` |
| `check_links.py` | `check --category docs` |
| `check_next_session_brief_length.py` | `check --category docs` |
| `check_openapi_snapshot.py` | `check --category api` (absorb into validate_api_contracts) |
| `check_python_version.py` | `check --category governance` |
| `check_repo_hygiene.py` | `check --category governance` |
| `check_scripts_index.py` | `check --category docs` |
| `check_streamlit.py` | `check --category streamlit` |
| `check_tasks_format.py` | `check --category docs` |
| `check_type_annotations.py` | `check --category code` |
| `check_unfinished_merge.sh` | `check --category git` |
| `check_version_consistency.sh` | `check --category git` |
| `check_wip_limits.sh` | `check --category git` |
| `validate_api_contracts.py` | `check --category api` |
| `validate_imports.py` | `check --category arch` |
| `validate_schema_snapshots.py` | `check --category governance` |
| `validate_script_refs.py` | `check --category stale` |
| `validate_git_state.sh` | `check --category git` |
| `audit_readiness_report.py` | `audit` |
| `audit_error_handling.py` | `audit --errors` |
| `audit_input_validation.py` | `audit --inputs` |
| `governance_health_score.py` | `audit --score` |
| `collect_diagnostics.py` | `audit --diagnostics` |
| `test_api_parity.py` | `test --parity` |
| `test_import_3d_pipeline.py` | `test --pipeline` |
| `test_vba_adapter.py` | `test --vba` |
| `benchmark_api.py` | `test --benchmark` |
| `external_cli_test.py` | `test --cli` |
| `ci_local.sh` | `test --ci` |
| `generate_all_indexes.sh` | `generate indexes` |
| `generate_client_sdks.py` | `generate sdk` |
| `generate_docs_index.py` | `generate docs-index` |

### Infrastructure scripts (called by other scripts, NOT directly by agents) (14)
| Script | Called By |
|--------|-----------|
| `safe_push.sh` | ai_commit.sh |
| `should_use_pr.sh` | ai_commit.sh |
| `sync_numbers.py` | ai_commit.sh, session.py |
| `install_git_hooks.sh` | agent_start.sh |
| `generate_enhanced_index.py` | session.py, generate_all_indexes.sh |
| `generate_api_manifest.py` | validate_api_contracts.py |
| `bump_version.py` | release.py, check_doc_versions.py |
| `check_not_main.sh` | git hook |
| `check_root_file_count.sh` | git hook |
| `pre_commit_check.sh` | git hook / manual |
| `update_test_stats.py` | standalone (merge into sync_numbers) |
| `check_doc_versions.py` | ci_local.sh (also exposed via check) |
| `check_links.py` | ai_commit.sh, session.py (also exposed via check) |
| `check_circular_imports.py` | audit_readiness_report.py (also exposed via check) |

### Ad-hoc utilities (not in run.sh — agents call directly when needed) (14)
| Script | When to use |
|--------|-------------|
| `safe_file_move.py` | Moving files (preserves 870+ links) |
| `safe_file_delete.py` | Deleting files safely |
| `migrate_python_module.py` | Moving Python modules + import updates |
| `migrate_react_component.py` | Moving React components + import updates |
| `create_doc.py` | Creating docs with proper metadata |
| `create_test_scaffold.py` | Generating pytest templates |
| `dxf_render.py` | Rendering DXF files |
| `lint_vba.py` | VBA linting |
| `run_vba_smoke_tests.py` | VBA smoke tests (macOS only) |
| `cleanup_stale_branches.py` | Branch cleanup |
| `recover_git_state.sh` | Git recovery |
| `archive_old_files.sh` | Monthly doc archiving |
| `agent_mistakes_report.sh` | Mistake tracking |
| `watch_tests.sh` | Continuous test watching |

### Pending archive (7 — Streamlit-era, V3 is React)
| Script | Reason |
|--------|--------|
| `check_performance_issues.py` | Streamlit perf patterns |
| `check_ui_duplication.py` | Streamlit code duplication |
| `validate_session_state.py` | Streamlit session state |
| `generate_streamlit_page.py` | Streamlit scaffolder |
| `profile_streamlit_page.py` | Streamlit profiler |
| `launch_streamlit.sh` | Streamlit launcher |
| `check_cost_optimizer_issues.py` | Streamlit-specific patterns |

### ~~Pending absorption (2 merges)~~ — SKIPPED (stability decision)
| Source | Status | Reason for keeping separate |
|--------|--------|---------------------------|
| `check_openapi_snapshot.py` | **Kept** | Uses raw JSON baseline, different format from `validate_api_contracts.py` (extracted signatures) |
| `update_test_stats.py` | **Kept** | Runs full pytest (2min) vs `sync_numbers.py` count-only (5s) — genuinely different purposes |

**Total after cleanup: 85 → 78 scripts** (7 archived, 0 absorbed)

---

## 6. Implementation Plan

### Phase 0: Immediate Cleanup (no new code) ✅ DONE
**Impact:** 85 → 78 scripts (7 archived)

1. **Archive 7 Streamlit-era scripts** using `safe_file_move.py`: ✅
   - `check_performance_issues.py`, `check_ui_duplication.py`, `validate_session_state.py`
   - `generate_streamlit_page.py`, `profile_streamlit_page.py`, `launch_streamlit.sh`
   - `check_cost_optimizer_issues.py`

2. **Absorb `check_openapi_snapshot.py` into `validate_api_contracts.py`:**
   - Add `--snapshot-only` flag to `validate_api_contracts.py`
   - Archive `check_openapi_snapshot.py`

3. **Absorb `update_test_stats.py` into `sync_numbers.py`:**
   - Add `--test-only` flag that runs pytest + updates test_stats.json
   - Archive `update_test_stats.py`

### Phase 1: Create `./run.sh` (thin dispatcher) ✅ DONE
**Effort:** ~600 lines of shell (commit `669c8d1`)
**Impact:** Agents go from remembering 78 scripts to 9 subcommands

1. Create `run.sh` at repo root
2. Dispatch table: each subcommand calls existing scripts via functions
3. `--help` for each subcommand shows what it does
4. Error messages suggest the right subcommand for common mistakes
5. `./run.sh` with no args prints command overview

```bash
#!/usr/bin/env bash
# run.sh — Unified CLI for structural_engineering_lib
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$REPO_ROOT/.venv/bin/python"

case "${1:-}" in
  check)    shift; "$VENV" "$REPO_ROOT/scripts/check_all.py" "$@" ;;
  commit)   shift; "$REPO_ROOT/scripts/ai_commit.sh" "$@" ;;
  pr)       shift; _handle_pr "$@" ;;
  session)  shift; _handle_session "$@" ;;
  find)     shift; _handle_find "$@" ;;
  release)  shift; "$VENV" "$REPO_ROOT/scripts/release.py" "$@" ;;
  audit)    shift; _handle_audit "$@" ;;
  test)     shift; _handle_test "$@" ;;
  generate) shift; _handle_generate "$@" ;;
  *)        _print_usage ;;
esac
```

### Phase 2: Create `scripts/check_all.py` (smart orchestrator) ✅ DONE
**Effort:** ~340 lines of Python (commit `669c8d1`)
**Impact:** `./run.sh check` runs 28 checks in parallel with unified report

1. Define category → script mapping in a Python dict
2. Use `concurrent.futures.ProcessPoolExecutor` for parallel check execution
3. Capture stdout/stderr per check, extract pass/fail/warn
4. Render unified table output (like the mockup above)
5. `--json` flag for CI output
6. `--fix` propagated to scripts that support it
7. `--category X` filters to one category
8. `--quick` runs a curated fast subset (~10 checks, <30s)

### Phase 3: Update Documentation ✅ DONE
1. ✅ Update `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` — add `./run.sh` as primary interface
2. ✅ Update `scripts/README.md` — document run.sh architecture
3. Update `automation-map.json` — map tasks → `./run.sh` subcommands (deferred)
4. ✅ Update `docs/agents/guides/agent-quick-reference.md`
5. Regenerate `scripts/index.json` and `scripts/index.md` (deferred to Phase 4)

### Phase 4: Polish & Extend ✅ DONE
1. ~~Add `./run.sh check --pre-commit`~~ ✅ Runs pre-commit hooks
2. ~~Add `./run.sh check --changed`~~ ✅ Auto-detects categories from git diff
3. ~~Add shell completion for run.sh~~ ✅ `eval "$(./run.sh --completions)"` for zsh
4. ~~Add timing output~~ ✅ Already in check_all.py (per-check + per-category + total)
5. Consider Python entry point alternative: `./eng check` via pyproject.toml scripts (deferred)

---

## 7. Migration Path

Existing scripts remain unchanged — `run.sh` is purely additive. Both interfaces work:

```bash
# Old way (still works, forever)
.venv/bin/python scripts/check_governance.py --structure

# New way (preferred for agents)
./run.sh check --category governance
```

No breaking changes. Gradual migration through documentation updates. The old scripts are the implementation — `run.sh` is just the user-friendly shell.

---

## 8. Agent Instruction Update (What CLAUDE.md Should Say)

After Phase 1, the commands section of all instruction files becomes:

```markdown
## Commands

```bash
./run.sh session start              # Begin work (verify env, read priorities)
./run.sh commit "type: message"     # Commit safely (THE ONE RULE)
./run.sh check                      # Validate everything
./run.sh check --quick              # Fast validation (<30s)
./run.sh pr create TASK-XXX "desc"  # Start a PR
./run.sh pr finish                  # Ship the PR
./run.sh session end                # Wrap up (logs, sync, handoff)
./run.sh find "topic"               # Find the right script
./run.sh find --api func_name       # Get API signatures
./run.sh release patch              # Cut a release
./run.sh test                       # Run test suite
./run.sh audit                      # Full readiness audit
```

## Direct Scripts (when run.sh doesn't cover it)

```bash
.venv/bin/python scripts/safe_file_move.py a b       # Move files safely
.venv/bin/python scripts/safe_file_delete.py file     # Delete files safely
.venv/bin/python scripts/migrate_python_module.py ... # Move Python modules
.venv/bin/python scripts/create_doc.py path           # Create doc with metadata
.venv/bin/python scripts/create_test_scaffold.py mod  # Generate test templates
```
```

---

## 9. Success Metrics

| Metric | Before | After Phase 1 | After Phase 2 |
|--------|--------|---------------|---------------|
| Commands agents need to know | 85 scripts | 9 subcommands + 5 direct | 9 subcommands + 5 direct |
| Scripts in scripts/ | 85 | 76 | 76 |
| Time to find the right script | 30-60s | 0s (subcommand) | 0s |
| Validation coverage per session | Partial | Full (one command) | Full, parallel |
| Stale reference risk | High | Low (stable entry points) | Low |
| Check execution time | Serial, ~5min | Serial, ~5min | Parallel, ~90s |
| New agent onboarding | Read 85 scripts | Read run.sh --help | Read run.sh --help |

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| run.sh becomes another thing to maintain | Medium | It's a pure dispatcher — no logic, just calls existing scripts |
| Agents still call scripts directly | Low | Both paths work; documentation guides to run.sh |
| check_all.py parallel execution hides failures | Medium | Always show full output for failures; --verbose flag |
| Shell vs Python for run.sh | Low | Start shell (simpler); migrate to Python click/typer if complexity grows |
| Pre-commit hooks need individual scripts | None | Hooks still call scripts directly; run.sh is agent-facing only |

---

## 11. Relationship to Existing Plans

This plan **supersedes** `docs/_archive/2026-03/scripts-consolidation-plan.md` (2026-02-10) for the "what's next" portion. The consolidation plan's Phase 1 (archive ~40 scripts) is **mostly done** — 93 scripts already archived. This plan picks up where consolidation left off:

- Consolidation Plan handled **reducing 163 → 85** (archiving dead scripts)
- This plan handles **making 76 scripts usable** (unified CLI + smart orchestration)
- The two plans are complementary, not competing
