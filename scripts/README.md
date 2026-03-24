# Scripts

> **Purpose:** Automation scripts for development, CI/CD, and maintenance tasks
> **Owner:** All contributors
> **Last Updated:** 2026-03-24
> **Total Scripts:** 78 active (100 archived)

## 🚀 Unified CLI (`./run.sh`)

All scripts are accessible through `./run.sh` at the repo root — **use this instead of calling scripts directly:**

```bash
./run.sh session start              # Begin work
./run.sh commit "type: message"     # Commit safely
./run.sh check --quick              # Fast validation (8 checks, <30s)
./run.sh check                      # Full validation (28 checks, parallel)
./run.sh check --category api       # Run one category only
./run.sh check --json               # Machine-readable output
./run.sh test                       # Run pytest suite
./run.sh pr create TASK-XXX "desc"  # Start a PR
./run.sh find "topic"               # Discover scripts by task
./run.sh find --api func_name       # Get API param names
./run.sh audit                      # Full readiness audit
./run.sh generate indexes           # Regenerate folder indexes
./run.sh session end                # Wrap up
```

Run `./run.sh --help` or `./run.sh <command> --help` for full usage.

### Architecture

`run.sh` is a **thin bash dispatcher** — no logic, just routes to existing scripts:
- `./run.sh check` → `scripts/check_all.py` (parallel orchestrator, 28 checks across 9 categories)
- `./run.sh commit` → `scripts/ai_commit.sh`
- `./run.sh test` → `Python/.venv/bin/pytest` or specialized test scripts
- `./run.sh find` → `scripts/find_automation.py` / `scripts/discover_api_signatures.py`

Both paths work: `./run.sh check --category git` and `.venv/bin/python scripts/validate_git_state.sh` are equivalent.

## 🤖 For AI Agents: Quick Discovery

**Use `index.json` for comprehensive script discovery:**

```python
# In your context, load this file for full script catalog:
# scripts/index.json - Contains all scripts organized by category
```

**Key categories in index.json:**
- `tier0` - 5 essential scripts (use 95% of the time)
- `categories` - All scripts grouped by purpose (15 categories)
- `quick_reference` - Copy-paste commands
- `workflows` - Common workflow patterns
- `deprecated` - Scripts NOT to use

**Start here:**
```bash
./run.sh session start             # Start session
./run.sh commit "message"          # Commit changes
./scripts/recover_git_state.sh     # Fix git issues
```

---

## Contents

### Git & Workflow Automation
| Script | Purpose |
|--------|---------|
| `ai_commit.sh` | AI-agent commit workflow (primary method) |
| `safe_push.sh` | Safe push with conflict prevention |
| `create_task_pr.sh` | Create PR for task |
| `finish_task_pr.sh` | Finish and merge PR |
| `should_use_pr.sh` | Decision helper: PR vs direct commit |

### Code Quality & Validation
| Script | Purpose |
|--------|---------|
| `check_links.py` | Validate and fix broken internal markdown links |
| `check_governance.py` | Unified governance — folder structure + compliance (`--structure`, `--compliance`) |
| `check_docs.py` | Unified doc checker — metadata, frontmatter, index (`--metadata`, `--all`) |
| `check_api.py` | Unified API checker — signatures, docs sync (`--signatures`, `--sync`) |
| `check_streamlit.py` | Unified Streamlit validation (AST scanner + fragment checks) |
| `check_doc_versions.py` | Check version drift in docs |
| `generate_api_manifest.py` | Generate API manifest JSON |
| `check_scripts_index.py` | Ensure scripts index is in sync |

### File & Folder Management
| Script | Purpose |
|--------|---------|
| `safe_file_move.py` | Move files with link updates |
| `safe_file_delete.py` | Delete files with reference check |
| `archive_old_files.sh` | Archive old docs (90-day policy) |

### Documentation & Indexing
| Script | Purpose |
|--------|---------|
| `generate_docs_index.py` | Generate docs-index.json |
| `generate_enhanced_index.py` | Generate index.json + index.md for any folder |
| `generate_all_indexes.sh` | Regenerate all folder indexes |
| `check_docs.py --index` | Validate docs index structure |
| `check_docs.py --index-links` | Validate docs index links |

### Session Management
| Script | Purpose |
|--------|---------|
| `session.py` | Unified session management (start, end, handoff, check, summary, sync) |
| `agent_start.sh` | Agent environment setup + pre-flight checks |
| `collect_diagnostics.py` | Bundle debug context (env, git, logs) |

### Script Discovery
| Script | Purpose |
|--------|--------|
| `find_automation.py` | Find the right script for a task (fuzzy search) |
| `discover_api_signatures.py` | Look up exact API function parameters |
| `validate_script_refs.py` | Detect stale references to archived scripts |

### Release & Versioning
| Script | Purpose |
|--------|---------|
| `bump_version.py` | Version management |
| `release.py` | Unified release management (run, verify, check-docs, checklist) |

## Guidelines

1. **Shell scripts** (`.sh`) should be POSIX-compatible where possible
2. **Python scripts** should use `from __future__ import annotations` for 3.9 compatibility
3. All scripts should have `--help` option
4. Use `--dry-run` option for destructive operations
5. Exit codes: 0 = success, 1 = error, 2 = warning

## For AI Agents

When working with scripts:
- **ALWAYS use `ai_commit.sh` or `safe_push.sh`** for git operations
- Never run destructive scripts without `--dry-run` first
- Check script help before using: `python script.py --help`
- Scripts in this folder don't need README.md each - this folder README covers them

### Common Workflows

```bash
# Start session
./scripts/agent_start.sh --quick

# Find the right script
.venv/bin/python scripts/find_automation.py "your task"

# Safe file operations
.venv/bin/python scripts/safe_file_move.py old.md new.md --dry-run
.venv/bin/python scripts/safe_file_delete.py file.md --dry-run

# Validate before commit
.venv/bin/python scripts/check_links.py
.venv/bin/python scripts/check_governance.py

# Commit changes
./scripts/ai_commit.sh "feat: description"

# PR workflow
./scripts/create_task_pr.sh TASK-XXX "description"
# ... make changes and commit ...
./scripts/finish_task_pr.sh TASK-XXX "description"
```
