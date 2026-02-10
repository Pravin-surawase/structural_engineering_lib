# Scripts

> **Purpose:** Automation scripts for development, CI/CD, and maintenance tasks
> **Owner:** All contributors
> **Last Updated:** 2026-01-24
> **Total Scripts:** 152

## 🤖 For AI Agents: Quick Discovery

**Use `index.json` for comprehensive script discovery:**

```python
# In your context, load this file for full script catalog:
# scripts/index.json - Contains all 152 scripts organized by category
```

**Key categories in index.json:**
- `tier0` - 5 essential scripts (use 95% of the time)
- `categories` - All scripts grouped by purpose (15 categories)
- `quick_reference` - Copy-paste commands
- `workflows` - Common workflow patterns
- `deprecated` - Scripts NOT to use

**Start here:**
```bash
./scripts/agent_start.sh --quick   # Start session
./scripts/ai_commit.sh "message"   # Commit changes
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
| `check_links.py` | Validate internal markdown links |
| `fix_broken_links.py` | Auto-fix broken links |
| `check_folder_structure.py` | Validate multi-code architecture |
| `check_streamlit.py` | Unified Streamlit validation (AST scanner + fragment checks) |
| `check_doc_versions.py` | Check version drift in docs |
| `generate_api_manifest.py` | Generate API manifest JSON |
| `check_scripts_index.py` | Ensure scripts index is in sync |

### File & Folder Management
| Script | Purpose |
|--------|---------|
| `safe_file_move.py` | Move files with link updates |
| `safe_file_delete.py` | Delete files with reference check |
| `check_folder_readmes.py` | Verify README presence |
| `find_orphan_files.py` | Find unreferenced docs |
| `archive_old_files.sh` | Archive old docs (90-day policy) |
| `archive_old_sessions.sh` | Archive old session docs |

### Documentation & Indexing
| Script | Purpose |
|--------|---------|
| `generate_docs_index.py` | Generate docs-index.json |
| `check_docs_index.py` | Validate docs index structure |
| `check_docs_index_links.py` | Validate docs index links |

### Session Management
| Script | Purpose |
|--------|---------|
| `session.py` | Unified session management (start, end, handoff, check) |
| `agent_setup.sh` | Agent environment setup |
| `agent_preflight.sh` | Pre-flight checks |
| `collect_diagnostics.py` | Bundle debug context (env, git, logs) |

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
./scripts/agent_setup.sh && ./scripts/agent_preflight.sh

# Safe file operations
python scripts/safe_file_move.py old.md new.md --dry-run
python scripts/safe_file_delete.py file.md --dry-run

# Validate before commit
python scripts/check_links.py
python scripts/check_folder_structure.py

# Commit changes
./scripts/ai_commit.sh "feat: description"
```
