# Copilot Instructions — structural_engineering_lib

> **FOR AI AGENTS:** Read this FIRST. Following these rules prevents 99% of errors and maximizes session value.
> **Cost Model:** Per-request pricing → LONG sessions = better ROI. Target 5-10+ commits per session.

---

## 🎯 Mission

**Maximize value per session through automation-first workflows:**
- 90-95% faster commits
- 97.5% fewer errors
- 100% conflict elimination
- 5-10+ commits per session (don't stop early!)

---

## 🚀 Quick Start (30 Seconds)

```bash
# 1. Start session
./scripts/agent_start.sh --quick

# 2. Work → Commit (repeat many times)
./scripts/ai_commit.sh "feat: your description"

# 3. End session (AFTER substantial work)
.venv/bin/python scripts/end_session.py
```

**Essential Resources:**
1. [copilot-instructions-v2.md](/.github/copilot-instructions-v2.md) ← **YOU ARE HERE**
2. [agent-workflow-master-guide.md](docs/agents/guides/agent-workflow-master-guide.md) - Complete workflows
3. [TASKS.md](docs/TASKS.md) - Current work
4. [git-automation/README.md](docs/git-automation/README.md) - Git automation hub
5. [folder-structure-governance.md](docs/guidelines/folder-structure-governance.md) - Project structure

---

## ⚠️ THE ONE RULE: Git Automation

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ NEVER use manual git commands!                    ┃
┃ ALWAYS: ./scripts/ai_commit.sh "message"          ┃
┃                                                    ┃
┃ Manual git → 10-30min conflicts → wasted time     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Why automation wins:**
- **Speed:** 5 seconds vs 45-60 seconds (90% faster)
- **Safety:** Pre-commit hooks handled automatically
- **Reliability:** Pull-before-push prevents conflicts
- **Enforcement:** Git hooks block manual commands

**Key scripts (see scripts/index.json):**
```bash
ai_commit.sh              # PRIMARY - Commit + push
should_use_pr.sh          # PR vs direct decision
create_task_pr.sh         # Start PR branch
finish_task_pr.sh         # Submit PR + async merge
recover_git_state.sh      # Emergency recovery
```

---

## 📋 Essential Workflows

### A. Git & Commits

**Primary workflow:**
```bash
# Check if PR needed
./scripts/should_use_pr.sh --explain

# Direct commit (docs/tests/scripts)
./scripts/ai_commit.sh "docs: fix typo"

# PR workflow (production code/VBA/CI)
./scripts/create_task_pr.sh TASK-XXX "description"
./scripts/ai_commit.sh "feat: implement X"  # Repeat as needed
./scripts/finish_task_pr.sh TASK-XXX "description" --async
```

**Decision matrix (authoritative: `./scripts/should_use_pr.sh --explain`):**
| Change Type | Strategy |
|-------------|----------|
| Production code (`Python/structural_lib/`) | **PR required** |
| VBA code (`VBA/`, `Excel/`) | **PR required** |
| CI workflows (`.github/workflows/`) | **PR required** |
| Dependencies (`pyproject.toml`) | **PR required** |
| Docs/tests/scripts (<=150 lines, <=2 files) | Direct commit OK |

**Session docs rule:**
- Update `SESSION_LOG.md` + `next-session-brief.md` in same PR
- Log **PR number** (not merge hash)
- One commit at end: `./scripts/ai_commit.sh "docs: update session 31 progress"`

**Emergency recovery:**
```bash
./scripts/git_ops.sh --status      # Analyze state
./scripts/recover_git_state.sh     # Fix issues
./scripts/git_automation_health.sh # Health check
```

### B. Testing & Validation

**Before ANY commit:**
```bash
# Python code:
cd Python && .venv/bin/python -m pytest tests/ -v

# Streamlit code:
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
.venv/bin/python scripts/check_fragment_violations.py

# Formatting (auto-fix):
cd Python && .venv/bin/python -m black .
.venv/bin/python -m ruff check --fix .
```

**Validation scripts:**
```bash
check_streamlit_issues.py         # AST scanner for runtime errors
check_fragment_violations.py      # Streamlit fragment API validator
check_links.py                    # Validate internal markdown links
check_doc_metadata.py             # Validate document headers
check_folder_structure.py         # Validate project structure
```

**Test patterns:**
```python
# Unit test example
def test_calculate_ast_required_nominal_case():
    """Test steel calculation for nominal beam."""
    result = calculate_ast_required(
        moment=100,  # kN·m
        width=300,   # mm
        depth=450,   # mm
        fck=25.0,    # N/mm²
        fy=500.0,    # N/mm²
    )
    assert result.ast_required > 0
    assert result.ast_min <= result.ast_required <= result.ast_max
```

**Coverage gate:** CI requires 85% branch coverage minimum.

### C. File Operations

**NEVER use manual file operations! They break internal links (870+ validated links in docs).**

```bash
# Move file (updates all links automatically)
.venv/bin/python scripts/safe_file_move.py old.md new.md

# Delete file (checks references first)
.venv/bin/python scripts/safe_file_delete.py obsolete.md

# Find unreferenced files
.venv/bin/python scripts/find_orphan_files.py

# ❌ FORBIDDEN:
rm docs/old.md
mv docs/a.md docs/b.md
git rm docs/file.md
```

**File operation workflow:**
```bash
# 1. ALWAYS dry-run first
.venv/bin/python scripts/safe_file_move.py old.md new.md --dry-run

# 2. Execute if safe
.venv/bin/python scripts/safe_file_move.py old.md new.md

# 3. Verify links
.venv/bin/python scripts/check_links.py

# 4. Commit
./scripts/ai_commit.sh "refactor: move old.md to new location"
```

### D. Documentation

**Creating docs:**
```bash
# Use create_doc.py for proper metadata
.venv/bin/python scripts/create_doc.py docs/research/my-topic.md "My Topic Research"

# Options: --type, --status, --importance, --tasks
.venv/bin/python scripts/create_doc.py docs/planning/my-plan.md "My Plan" \
  --type=Plan --status=Draft --importance=High --tasks=TASK-XXX
```

**Maintaining docs:**
```bash
check_links.py                    # Validate all internal links
fix_broken_links.py --fix         # Auto-fix broken links
check_doc_metadata.py             # Validate metadata headers
check_duplicate_docs.py           # Find duplicate content
consolidate_docs.py archive       # Archive completed research
```

**Document metadata (REQUIRED for new files):**
```markdown
**Type:** [Guide|Research|Reference|Architecture|Decision]
**Audience:** [All Agents|Developers|Users]
**Status:** [Draft|Approved|Deprecated|Production Ready]
**Importance:** [Critical|High|Medium|Low]
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Related Tasks:** TASK-XXX
```

---

## 🏗️ Project Architecture

### 3-Layer System (NEVER Mix!)

| Layer | Location | Rules |
|-------|----------|-------|
| **Core** | `Python/structural_lib/codes/is456/*.py` | Pure functions, NO I/O, explicit units |
| **Application** | `api.py`, `job_runner.py` | Orchestrates core, NO formatting |
| **UI/I-O** | `streamlit_app/`, `excel_integration.py`, `dxf_export.py` | External interfaces only |

**Critical rules:**
- Core modules CANNOT import from Application or UI layers
- Units ALWAYS explicit: mm, N/mm², kN, kN·m
- No hidden conversions or assumptions

**Key files:**
- `Python/structural_lib/codes/is456/flexure.py` - Moment design (Mu, Ast)
- `Python/structural_lib/codes/is456/shear.py` - Shear design (Vu, stirrups)
- `Python/structural_lib/codes/is456/detailing.py` - Rebar layout, development lengths
- `Python/structural_lib/api.py` - Main entry point for users
- `streamlit_app/pages/01_beam_design.py` - Primary UI (4 visible pages, 8 hidden)

---

## 🎯 Streamlit-Specific Rules (CRITICAL)

### Fragment API (Session 30 Crisis Lesson)

**Problem:** Agents added `@st.fragment` but called `st.sidebar` inside fragments → runtime crashes.
**Solution:** Specialized validator + clear rules.

```python
# ❌ FORBIDDEN in @st.fragment functions:
@st.fragment
def bad_fragment():
    st.sidebar.button("Click")  # StreamlitAPIException!
    st.tabs(["A", "B"])         # Not allowed
    # Any function that uses st.sidebar internally!

# ✅ CORRECT patterns:
@st.fragment
def good_fragment():
    st.button("Click")          # OK - regular widgets
    st.write("Text")            # OK
    st.number_input("Value")    # OK

# OR wrap fragment call in sidebar context:
with st.sidebar:
    my_fragment()  # Now sidebar widgets OK inside
```

**Validation (automatic in pre-commit + CI):**
```bash
.venv/bin/python scripts/check_fragment_violations.py
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
```

### Safe Patterns (Scanner-Enforced)

```python
# ✅ REQUIRED patterns:
value = data.get('key', default)              # Not data['key']
first = items[0] if len(items) > 0 else None  # Not items[0]
result = a / b if b != 0 else 0               # Not a / b
value = st.session_state.get('key', default)  # Not st.session_state.key

# ❌ FORBIDDEN (causes runtime crashes):
value = data['key']              # KeyError
first = items[0]                 # IndexError
result = a / b                   # ZeroDivisionError
value = st.session_state.key     # AttributeError
```

### Import Rules

```python
# ✅ ALWAYS: Module level
import pandas as pd

def my_function():
    df = pd.DataFrame(data)

# ❌ NEVER: Inside functions
def my_function():
    import pandas as pd  # Wrong!
```

---

## 📁 Governance & Hygiene

### Folder Structure (Enforced by CI)

**Root limit:** 10 files max (current: 10 ✅)
```
README.md, LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md,
CHANGELOG.md, LICENSE_ENGINEERING.md, llms.txt, CITATION.cff,
SECURITY.md, AUTHORS.md
```

**Docs structure:**
- **Root:** 3-5 hub files (README.md, TASKS.md, SESSION_LOG.md)
- **Categories:** 15-20 folders with specific limits
- **Archive:** Old/completed files in `docs/_archive/`

**Check compliance:**
```bash
./scripts/check_folder_structure.py
./scripts/check_root_file_count.sh
./scripts/check_folder_readmes.py
```

### File Hygiene Rules

**Archive rule:** Move to `docs/_archive/` when:
- Research Status: Complete
- Sessions older than 90 days
- Deprecated documentation
- Superseded by newer files

**Prevent duplicates:**
```bash
# Before creating file, check if exists:
find docs/ -name "*similar-name*"
./scripts/check_duplicate_docs.py

# Check for orphan files:
./scripts/find_orphan_files.py
```

**README/Index maintenance:**
- Update README when adding/removing folders
- Update `index.json` when adding scripts
- Run after structural changes:
  ```bash
  ./scripts/generate_all_indexes.sh
  ./scripts/check_scripts_index.py
  ```

### Archival Scripts

```bash
archive_old_files.sh              # Files older than 90 days
archive_old_sessions.sh           # Old session docs
consolidate_docs.py archive       # Completed research
batch_archive.py                  # Batch operations
```

---

## 💰 Efficiency & Value Maximization

### Session Economics

**Cost model:** Per-request pricing → **Longer sessions = Better ROI**

| Session Type | Commits | Duration | Value Score |
|--------------|---------|----------|-------------|
| ❌ Poor | 1-2 | <15 min | Low (expensive per commit) |
| ⚠️ Acceptable | 3-4 | 15-30 min | Medium |
| ✅ Good | 5-7 | 30-60 min | High |
| 🌟 Excellent | 8-10+ | 60-90 min | Very High (optimal ROI) |

**Session guidelines:**
- **Minimum:** 5+ commits or 30+ minutes
- **Target:** Complete full task before stopping
- **If blocked:** Move to next task (don't end session early!)
- **Document:** Update TASKS.md + SESSION_LOG.md before ending

### Automation-First Mindset

**Core principle:** See 10+ similar issues → Build automation script FIRST

**Examples:**
- 396 broken links? → Build `fix_broken_links.py` (fixed 213 links in 5 seconds)
- Fragment API violations? → Build `check_fragment_violations.py` (prevents all future violations)
- Import errors? → Build `check_streamlit_imports.py` (catches before commit)

**Automation checklist:**
1. **Recognize pattern:** 10+ similar issues
2. **Research:** Check `scripts/` for existing tools
3. **Build:** Create specialized script
4. **Integrate:** Add to pre-commit hooks + CI
5. **Document:** Add to `scripts/index.json` + README

**Available automation (see scripts/index.json):**
```bash
# See all automation:
cat scripts/index.json

# Quick reference:
./scripts/agent_start.sh --quick      # Session start
./scripts/ai_commit.sh "message"      # Git workflow
./scripts/should_use_pr.sh --explain  # Decision automation
./scripts/check_*                     # Validation suite (25+ scripts)
./scripts/safe_file_*                 # File operations
./scripts/*_automation_*              # Workflow automation
```

### Value Indicators

| Metric | Target | Check |
|--------|--------|-------|
| Commits per session | 5-10+ | `git log --oneline --since="1 hour ago"` |
| Automation scripts created | When 10+ patterns found | Review `scripts/` directory |
| Documentation updated | Every significant change | Check git diff on docs/ |
| Tests added | With every behavior change | Check `Python/tests/` |
| Links validated | Before commit | `check_links.py` |
| Folder structure compliant | Always | `check_folder_structure.py` |

---

## 🚨 Common Mistakes (AVOID)

| Mistake | Impact | Correct Approach | Script |
|---------|--------|------------------|--------|
| **Manual git commands** | 10-30min conflicts | `ai_commit.sh` | - |
| **Creating duplicate docs** | Doc sprawl, wasted time | Check if exists first | `check_duplicate_docs.py` |
| **Not archiving old files** | Folder bloat, slow navigation | Use archive scripts | `archive_old_files.sh` |
| **Mixing architecture layers** | Broken imports, coupling | Respect 3-layer system | Check imports manually |
| **Manual file operations** | Broken links (870+) | Use safe_file_* scripts | `safe_file_move.py` |
| **Stopping session early** | Low value/cost ratio | Continue to next task | Check TASKS.md |
| **Not updating indexes** | Out-of-sync navigation | Run after changes | `generate_all_indexes.sh` |
| **Skipping validation** | Runtime errors in prod | Run before commit | `check_*` scripts |
| **Creating files without metadata** | Poor discoverability | Use `create_doc.py` | - |
| **Not checking PR need** | Wrong workflow | Use decision script | `should_use_pr.sh` |

---

## 📚 Essential Resources

### Daily Commands

```bash
# Session lifecycle
./scripts/agent_start.sh --quick              # Start (6s)
./scripts/ai_commit.sh "message"              # Commit (5s)
.venv/bin/python scripts/end_session.py       # End (3s)

# Decision support
./scripts/should_use_pr.sh --explain          # PR check (1s)
./scripts/git_ops.sh --status                 # State analysis (2s)

# Validation
.venv/bin/python scripts/check_links.py       # Links
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
cd Python && pytest tests/ -v                 # Tests

# File operations
.venv/bin/python scripts/safe_file_move.py old.md new.md
.venv/bin/python scripts/safe_file_delete.py obsolete.md
.venv/bin/python scripts/create_doc.py path/file.md "Title"
```

### Key Documentation

**Workflows:**
- [agent-workflow-master-guide.md](docs/agents/guides/agent-workflow-master-guide.md) - Complete workflows (717 lines)
- [agent-quick-reference.md](docs/agents/guides/agent-quick-reference.md) - Command cheat sheet
- [git-automation/README.md](docs/git-automation/README.md) - Git automation hub

**Project Structure:**
- [TASKS.md](docs/TASKS.md) - Current work items
- [folder-structure-governance.md](docs/guidelines/folder-structure-governance.md) - Structure rules
- [project-overview.md](docs/architecture/project-overview.md) - Architecture overview

**Domain Knowledge:**
- [streamlit-fragment-best-practices.md](docs/guidelines/streamlit-fragment-best-practices.md) - Fragment rules
- [testing-strategy.md](docs/contributing/testing-strategy.md) - Test patterns
- [api.md](docs/reference/api.md) - API reference

**Automation:**
- `scripts/index.json` - All scripts catalog
- `scripts/README.md` - Scripts overview

### Emergency Procedures

```bash
# Git issues
./scripts/recover_git_state.sh                # Auto-fix common issues
./scripts/git_automation_health.sh            # System health check
./scripts/check_unfinished_merge.sh           # Detect merge state

# Validation failures
.venv/bin/python scripts/comprehensive_validator.py  # Full validation
./scripts/repo_health_check.sh                # Overall health

# Documentation issues
.venv/bin/python scripts/fix_broken_links.py --fix   # Auto-fix links
./scripts/consolidate_docs.py analyze         # Find redundancy
```

---

## 🎓 First-Time Agent Checklist

### Before First Commit
- [ ] Read this file completely
- [ ] Run `./scripts/agent_start.sh --quick`
- [ ] Review [TASKS.md](docs/TASKS.md) for active work
- [ ] Understand 3-layer architecture
- [ ] Know the ONE RULE: Use `ai_commit.sh`

### Your First Commit
- [ ] Make a small change (e.g., fix typo)
- [ ] Run `./scripts/ai_commit.sh "docs: fix typo"`
- [ ] Verify commit appears in `git log`
- [ ] Observe what the script did (staged, pre-commit, pushed)

### After First Commit
- [ ] Read [agent-workflow-master-guide.md](docs/agents/guides/agent-workflow-master-guide.md)
- [ ] Bookmark [agent-quick-reference.md](docs/agents/guides/agent-quick-reference.md)
- [ ] Understand PR vs direct commit decision (use `should_use_pr.sh`)
- [ ] Ready for production work!

---

## 📞 When In Doubt

```bash
# 1. Analyze git state
./scripts/git_ops.sh --status

# 2. Check PR requirement
./scripts/should_use_pr.sh --explain

# 3. Review workflow guide
cat docs/agents/guides/agent-workflow-master-guide.md | less

# 4. Check current tasks
cat docs/TASKS.md

# 5. Emergency recovery
./scripts/recover_git_state.sh
```

**Decision tree:**
```
Problem?
├─ Git issues → ./scripts/git_ops.sh --status
├─ Workflow unclear → ./scripts/should_use_pr.sh --explain
├─ Links broken → .venv/bin/python scripts/fix_broken_links.py --fix
├─ Tests failing → cd Python && pytest tests/ -v
├─ Streamlit errors → .venv/bin/python scripts/check_streamlit_issues.py
└─ Unknown → Read agent-workflow-master-guide.md
```

---

**Remember:** This project optimizes for LONG, VALUABLE sessions. Don't stop early—find another task and keep delivering value!
