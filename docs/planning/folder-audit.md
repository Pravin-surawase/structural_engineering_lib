# Folder Audit — Repository Health & Documentation

**Type:** Planning
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-03-23
**Last Updated:** 2026-03-23 (Session 91)

---

## Purpose

Systematic audit of every folder and subfolder in the repository to:
- Document what each folder contains and its purpose
- Identify stale, duplicate, or misplaced content
- Find cleanup opportunities (archive, delete, consolidate)
- Verify README/index coverage
- Plan improvements per area

## Scope

**Total:** ~369 directories, ~3,719 files (excluding caches/build artifacts)

### Top-Level Folder Inventory

| # | Folder | Files | Has README | Has index.json | Status |
|---|--------|------:|:----------:|:--------------:|--------|
| 1 | `Python/` | 279 | Yes | Yes | — |
| 2 | `react_app/` | 79 | Yes | Partial (3) | — |
| 3 | `fastapi_app/` | 35 | No | No | — |
| 4 | `streamlit_app/` | 249 | Yes | No | — |
| 5 | `scripts/` | 191 | Yes | Yes | — |
| 6 | `docs/` | 2504 | Yes | Yes | — |
| 7 | `Excel/` | 12 | Yes | No | — |
| 8 | `VBA/` | 85 | Yes | No | — |
| 9 | `agents/` | 39 | Yes | Yes | — |
| 10 | `clients/` | 5 | No | No | — |
| 11 | `tests/` | 26 | No | No | — |
| 12 | `logs/` | 204 | Yes | No | — |
| 13 | `metrics/` | 2 | No | No | — |
| 14 | `git_operations_log/` | 3 | No | No | — |
| 15 | `tmp/` | 6 | No | No | — |
| 16 | `.github/` | ~15 | Partial | No | — |
| 17 | `.claude/` | ~5 | No | No | — |

### docs/ Subfolder Breakdown (largest area — 2504 files)

| Subfolder | Files | Notes |
|-----------|------:|-------|
| `reference/` | 1788 | 1760 are vendor/ETABS CHM files (30MB) |
| `_archive/` | 253 | Old sessions, planning, research |
| `research/` | 186 | 73 in navigation_study alone |
| `_internal/` | 47 | copilot-tasks, quality assessments |
| `planning/` | 40 | Active planning docs |
| `contributing/` | 33 | Contribution guides |
| `getting-started/` | 21 | Bootstrap, onboarding |
| `agents/` | 21 | Agent guides, session logs |
| `guidelines/` | 18 | Coding guidelines |
| `architecture/` | 13 | Architecture docs |
| `publications/` | 10 | Blog posts, findings |
| `learning/` | 9 | Learning materials |
| `verification/` | 8 | Verification docs |
| `guides/` | 7 | User guides |
| `git-automation/` | 7 | Git workflow docs |
| `_active/` | 5 | Active work items |
| `blog-drafts/` | 5 | Draft blog posts |
| `developers/` | 5 | Developer docs |
| `cookbook/` | 4 | Code recipes |
| `adr/` | 4 | Architecture Decision Records |
| `audit/` | 4 | Audit reports |
| `specs/` | 3 | Specifications |
| `legal/` | 3 | License, legal |
| `vba/` | 2 | VBA docs |
| `images/` | 1 | Images |
| `_references/` | 1 | External references |

---

## Audit Batches

Realistic plan — one batch per session, prioritized by impact.

### Batch 1: Quick Wins — Small Folders (this session)
**Scope:** `clients/`, `metrics/`, `git_operations_log/`, `tmp/`, `logs/`, `.github/`, `.claude/`
**Goal:** Document purpose, flag cleanup, ~30 min

| Folder | Purpose | Files | Findings | Action |
|--------|---------|------:|----------|--------|
| `clients/` | Auto-generated SDK clients | 5 | No README, likely stale vs API | Add README, regenerate |
| `metrics/` | Historical project metrics | 2 | No README, only 2 snapshots ever | Add README, low priority |
| `git_operations_log/` | Manual git logs (Jan 2026) | 3 | Obsolete — superseded by `logs/` | Archive or delete |
| `tmp/` | Temporary files | 6 | Completed task artifacts, not gitignored | Clean + add to `.gitignore` |
| `logs/` | Hook output + CI logs | 204 | 181 hook logs, no rotation, tracked in git | Add rotation, consider `.gitignore` |
| `.github/` | GH config, CI, templates | ~30 | Stub claims "900+ lines" (actual: 95) | Fix stale claim |
| `.claude/` | Claude AI per-filetype rules | 6 | Duplicates `.github/instructions/` | Document or consolidate |

### Batch 2: Code Folders — Python Core
**Scope:** `Python/structural_lib/` deep dive (codes, core, services, insights, reports, visualization)
**Goal:** Verify architecture layers, check for dead code, document module purposes

### Batch 3: Code Folders — UI Layers
**Scope:** `fastapi_app/`, `react_app/`, `streamlit_app/`
**Goal:** Component inventory, dead route detection, hook/component coverage

### Batch 4: Excel & VBA
**Scope:** `Excel/`, `VBA/` (all subfolders)
**Goal:** Document workbook/module inventory, check Python parity

### Batch 5: Scripts Deep Dive
**Scope:** `scripts/` (tiers, _lib, _archive, git-hooks)
**Goal:** Verify tier classification, find unused scripts, check _archive relevance

### Batch 6: Tests
**Scope:** `Python/tests/`, `tests/`, `fastapi_app/tests/`, `streamlit_app/tests/`
**Goal:** Test coverage map, find gaps, dead fixtures

### Batch 7: Docs — Active Content
**Scope:** `docs/planning/`, `docs/getting-started/`, `docs/architecture/`, `docs/contributing/`, `docs/agents/`, `docs/guidelines/`
**Goal:** Find stale docs, overlapping content, update outdated material

### Batch 8: Docs — Research & Publications
**Scope:** `docs/research/`, `docs/publications/`, `docs/blog-drafts/`, `docs/learning/`
**Goal:** Archive completed research, consolidate findings

### Batch 9: Docs — Archive & Internal
**Scope:** `docs/_archive/`, `docs/_internal/`, `docs/_active/`, `docs/_references/`
**Goal:** Verify archive is organized, internal docs still relevant

### Batch 10: Docs — Reference (Largest)
**Scope:** `docs/reference/` (1788 files, 30MB)
**Goal:** Assess vendor/ CHM files, check reference docs freshness

### Batch 11: Agents & Misc
**Scope:** `agents/`, `agents/agent-9/`, `agents/roles/`
**Goal:** Document agent configuration, check for stale agent data

---

## Audit Template (per folder)

For each folder audited, record:

```
### folder/path/

- **Purpose:** What is this folder for?
- **Files:** N files, M subfolders
- **README:** Yes/No/Stale
- **index.json:** Yes/No/Stale
- **Owner:** Who maintains this?
- **Freshness:** Last meaningful change date
- **Issues Found:**
  - [ ] Issue description
- **Actions:**
  - [ ] Action description
```

---

## Completed Audits

### Batch 1 — Quick Wins (Session 91)

#### `clients/`

- **Purpose:** Auto-generated SDK clients for the FastAPI backend
- **Files:** 5 files, 2 subfolders (python/, typescript/)
- **README:** No
- **index.json:** No
- **Owner:** Generated by `scripts/generate_client_sdks.py`
- **Freshness:** Initial scaffolds, never updated since creation
- **Content:** Python client (173 lines), TypeScript client (120 lines)
- **Issues Found:**
  - [ ] No README.md — agents won't know what this is
  - [ ] No `.gitignore` for generated output
  - [ ] Likely stale — clients may not match current API (35 endpoints, 75 schemas)
- **Actions:**
  - [ ] Add README explaining these are generated SDKs
  - [ ] Regenerate clients from current OpenAPI spec
  - [ ] Consider if these should be in `.gitignore` (generated artifacts)

#### `metrics/`

- **Purpose:** Historical project metrics snapshots
- **Files:** 2 JSON files
- **README:** No
- **index.json:** No
- **Owner:** `scripts/collect_metrics.sh`
- **Freshness:** Last updated 2026-01-23 (2 months stale)
- **Content:** `doc_consolidation_metrics.json` (consolidation baseline from Jan 13), `metrics_2026-01-10.json` (velocity, tech debt, coverage snapshot)
- **Issues Found:**
  - [ ] No README — purpose unclear to new agents
  - [ ] Only 2 snapshots ever taken — metrics collection not habitual
  - [ ] No automation to refresh periodically
- **Actions:**
  - [ ] Add README explaining metrics purpose and how to collect
  - [ ] Consider adding `collect_metrics.sh` to session end workflow
  - [ ] Low priority — functional but underused

#### `git_operations_log/`

- **Purpose:** Manual git operation logs from early sessions (Jan 2026)
- **Files:** 3 files (2 logs, 1 markdown narrative)
- **README:** No
- **index.json:** No
- **Owner:** None (manual, discontinued)
- **Freshness:** Last entry 2026-01-08 (11 weeks stale). Superseded by `logs/` hook output
- **Issues Found:**
  - [ ] Obsolete — `logs/` + `git_workflow.log` + hook output logs now serve this purpose
  - [ ] Only 1 day of logs ever captured
- **Actions:**
  - [ ] Archive to `docs/_archive/` or delete entirely
  - [ ] Low priority — 3 small files, no harm keeping

#### `tmp/`

- **Purpose:** Temporary working files
- **Files:** 6 files (1 script, 4 backup files, 1 PR body)
- **README:** No
- **index.json:** No
- **Owner:** None (ad-hoc)
- **Content:** `add_when_to_use.py` (completed task helper), `deleted_backups/` (4 safe_file_delete backups from Jan), `pr-body.md` (leftover PR template)
- **Issues Found:**
  - [ ] `add_when_to_use.py` — task completed, script no longer needed
  - [ ] `deleted_backups/` — SECURITY.md backups from Jan 23, safe to clean
  - [ ] `pr-body.md` — leftover from a PR workflow
  - [ ] No `.gitignore` rule for `tmp/` — these get tracked
- **Actions:**
  - [ ] Clean all files (they're historical artifacts)
  - [ ] Add `tmp/` to `.gitignore` to prevent future tracking
  - [ ] Low effort, minor cleanup

#### `logs/`

- **Purpose:** Git hook output logs and CI monitor
- **Files:** 204 files (181 hook_output logs, git_workflow.log, ci_monitor.log, README, migration-rollbacks/)
- **README:** Yes
- **index.json:** No
- **Owner:** `scripts/install_git_hooks.sh` (auto-generated by hooks)
- **Freshness:** Active — latest log is from today (2026-03-23)
- **Content:** Hook output logs span Jan 23 – Mar 23 (139 from Jan, 27 from Feb, 12 from Mar). Also `migration-rollbacks/` with 9 rollback folders from Feb 11-27.
- **Issues Found:**
  - [ ] 181 hook log files is excessive — no rotation policy
  - [ ] Jan alone accounts for 139 logs (77%)
  - [ ] Migration rollbacks from Feb — can these be archived?
  - [ ] `logs/` is tracked in git — these bloat the repo
- **Actions:**
  - [ ] Add log rotation: keep last 30 days, archive older
  - [ ] Consider adding `logs/hook_output_*.log` to `.gitignore`
  - [ ] Archive migration-rollbacks older than 60 days
  - [ ] Medium priority — actively growing, will become a problem

#### `.github/`

- **Purpose:** GitHub configuration — workflows, templates, instructions
- **Files:** ~30 files across 4 subfolders
- **README:** Partial (workflows/ has one)
- **index.json:** No
- **Owner:** Maintainers
- **Freshness:** Active — instructions updated regularly
- **Structure:**
  - `workflows/` — 16 CI/CD workflows (tests, security, governance, docker, etc.)
  - `instructions/` — 5 per-filetype instruction files (docs, python-core, react, streamlit, vba)
  - `copilot/` — Redirect stub → `copilot-instructions.md`
  - `ISSUE_TEMPLATE/` — 3 templates (bug, feature, support) + config
- **Issues Found:**
  - [ ] `copilot/instructions.md` is a redirect stub (30 lines) → `copilot-instructions.md` (95 lines). The stub says "900+ lines" but actual canonical file is 95 lines
  - [ ] `.claude/rules/` and `.github/instructions/` serve similar purposes (per-filetype rules). Some duplication between the two
  - [ ] `DEVELOPMENT_TIMELINE.md` in `.github/` — odd location, may belong in `docs/`
- **Actions:**
  - [ ] Fix "900+ lines" claim in copilot stub — actual is 95 lines
  - [ ] Audit overlap between `.claude/rules/` and `.github/instructions/`
  - [ ] Consider moving `DEVELOPMENT_TIMELINE.md` to `docs/`
  - [ ] Low priority — functional, minor inaccuracies

#### `.claude/`

- **Purpose:** Claude Code (claude.ai) per-filetype rules
- **Files:** 6 files in `rules/` subfolder
- **README:** No
- **index.json:** No
- **Owner:** Maintainers
- **Freshness:** Active — rules are current
- **Content:** 6 rule files matching `.github/instructions/` topics: docs, fastapi, python-core, react, streamlit, vba
- **Issues Found:**
  - [ ] Duplicates `.github/instructions/` — both define per-filetype rules for AI agents
  - [ ] Claude rules use `globs:` frontmatter; GitHub instructions use `applyTo:` — different formats, same intent
  - [ ] Content is largely identical between the two sets
- **Actions:**
  - [ ] Document the intentional dual-format setup (Claude vs Copilot)
  - [ ] Or consolidate into one canonical source with a sync script
  - [ ] Low priority — both work, just duplicated maintenance

---

## Workflow Status (for context)

All workflow tooling is green as of Session 91:
- `check_scripts_index.py` — 83/83 scripts indexed, 60/60 docstrings
- `sync_numbers.py` — All doc numbers match codebase
- `check_openapi_snapshot.py` — Baseline matches (35 endpoints, 75 schemas)
- `session.py end` — 9-step end check including TASKS archival
- `ai_commit.sh` — Post-commit hooks: stale numbers + broken link detection
- `generate_enhanced_index.py` — Content hash watermarks + `--check` staleness

### Remaining Workflow Items
- [ ] `--dry-run` as universal default for mutating scripts
- [ ] Consistent `--json` output across remaining `check_*` scripts
- [ ] Migrate 38 more scripts to `_lib/` (Phase 4b)
- [ ] Add `sync_numbers` to GitHub Actions CI
